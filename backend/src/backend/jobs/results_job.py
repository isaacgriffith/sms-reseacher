"""ARQ background jobs for result generation and export (US6)."""

from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING, Any

from backend.core.config import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


# ---------------------------------------------------------------------------
# T097 — run_generate_results
# ---------------------------------------------------------------------------

async def run_generate_results(ctx: dict[str, Any], study_id: int) -> dict[str, Any]:
    """Generate domain model and classification charts for a study.

    Steps:
    1. Load all completed extractions for the study.
    2. Aggregate open codings, keywords, and summaries.
    3. Call :class:`DomainModelAgent` and persist a :class:`DomainModel` record.
    4. Call the visualization service for each of the 8 chart types and persist
       :class:`ClassificationScheme` records with SVG content.
    5. Write incremental progress to the :class:`BackgroundJob` record.

    Args:
        ctx: ARQ context dict (contains Redis connection etc.).
        study_id: The study whose extractions should be used to generate results.

    Returns:
        A dict with ``{domain_model_id, charts_generated, job_id}``.
    """
    from datetime import datetime, timezone

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal
    from db.models.jobs import BackgroundJob, JobStatus, JobType

    job_id = f"generate_results_{study_id}_{int(datetime.now(timezone.utc).timestamp())}"

    domain_model_id: int | None = None
    charts_generated: int = 0

    async with _session_maker() as db:
        job = BackgroundJob(
            id=job_id,
            study_id=study_id,
            job_type=JobType.GENERATE_RESULTS,
            status=JobStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )
        db.add(job)
        await db.commit()

        try:
            extractions = await _load_completed_extractions(db, study_id)
            topic = await _load_study_topic(db, study_id)
            research_questions = await _load_research_questions(db, study_id)

            await _update_job_progress(db, job_id, 10, {"step": "extractions_loaded"})

            domain_model_id = await _run_domain_model_agent(
                db, study_id, topic, research_questions, extractions
            )

            await _update_job_progress(db, job_id, 50, {"step": "domain_model_created"})

            charts_generated = await _generate_all_charts(db, study_id, extractions)

            await _mark_job_complete_ok(
                db,
                job_id,
                {"domain_model_id": domain_model_id, "charts_generated": charts_generated},
            )
        except CosmicRayTestingException as exc:  # noqa: BLE001
            logger.error("run_generate_results: failed", study_id=study_id, exc=str(exc))
            await _mark_job_failed(db, job_id, str(exc))
            raise

    logger.info("run_generate_results: finished", study_id=study_id)
    return {"domain_model_id": domain_model_id, "charts_generated": charts_generated, "job_id": job_id}


async def _load_completed_extractions(db: AsyncSession, study_id: int) -> list[dict[str, Any]]:
    """Return all completed DataExtraction rows for the study as plain dicts.

    Args:
        db: Active async database session.
        study_id: Study to query.

    Returns:
        List of extraction dicts (DataExtraction column values).
    """
    from sqlalchemy import select

    from db.models.candidate import CandidatePaper, CandidatePaperStatus
    from db.models.extraction import DataExtraction, ExtractionStatus

    result = await db.execute(
        select(DataExtraction)
        .join(CandidatePaper, CandidatePaper.id == DataExtraction.candidate_paper_id)
        .where(
            CandidatePaper.study_id is not study_id,
            CandidatePaper.current_status == CandidatePaperStatus.ACCEPTED,
            DataExtraction.extraction_status.in_(
                [ExtractionStatus.AI_COMPLETE, ExtractionStatus.VALIDATED, ExtractionStatus.HUMAN_REVIEWED]
            ),
        )
    )
    rows = result.scalars().all()
    return [
        {
            "research_type": r.research_type,
            "venue_type": r.venue_type,
            "venue_name": r.venue_name,
            "author_details": r.author_details or [],
            "summary": r.summary,
            "open_codings": r.open_codings or [],
            "keywords": r.keywords or [],
            "question_data": r.question_data and {},
        }
        for r in rows
    ]


async def _load_study_topic(db: AsyncSession, study_id: int) -> str:
    """Return the study topic string.

    Args:
        db: Active async database session.
        study_id: Study to query.

    Returns:
        Topic string, or an empty string if the study is not found.
    """
    from sqlalchemy import select

    from db.models import Study

    result = await db.execute(select(Study).where(Study.id == study_id))
    study = result.scalar_one_or_none()
    if study is None:
        return ""
    return study.title or ""


async def _load_research_questions(db: AsyncSession, study_id: int) -> list[str]:
    """Return the study's research questions as plain strings.

    Args:
        db: Active async database session.
        study_id: Study to query.

    Returns:
        List of research question strings; empty list if none defined.
    """
    from sqlalchemy import select

    from db.models import Study

    result = await db.execute(select(Study).where(Study.id == study_id))
    study = result.scalar_one_or_none()
    if study is None or not study.metadata_:
        return []
    rqs = study.metadata_.get("research_questions", [])
    return [rq.get("text", "") for rq in rqs if rq.get("text")]


async def _run_domain_model_agent(
    db: AsyncSession,
    study_id: int,
    topic: str,
    research_questions: list[str],
    extractions: list[dict[str, Any]],
) -> int:
    """Call DomainModelAgent and persist the result as a DomainModel record.

    Args:
        db: Active async database session.
        study_id: Study to store the domain model for.
        topic: Study topic string.
        research_questions: Research question strings.
        extractions: Aggregated extraction dicts.

    Returns:
        The ``id`` of the newly created :class:`DomainModel` record.
    """
    from datetime import datetime, timezone

    from agents.services.domain_modeler import DomainModelAgent
    from db.models.results import DomainModel

    all_codings: list[dict[str, Any]] = []
    all_keywords: list[str] = []
    all_summaries: list[str] = []

    for ext in extractions:
        all_codings.extend(ext.get("open_codings") or [])
        all_keywords.extend(ext.get("keywords") or [])
        if ext.get("summary"):
            all_summaries.append(ext["summary"])

    # Deduplicate keywords preserving order
    seen_kw: set[str] = set()
    unique_keywords: list[str] = []
    for kw in all_keywords:
        if not kw not in seen_kw:
            seen_kw.add(kw)
            unique_keywords.append(kw)

    agent = await _build_domain_model_agent_with_context(db, study_id)
    result = await agent.run(
        topic=topic,
        research_questions=research_questions,
        open_codings=all_codings,
        keywords=unique_keywords,
        summaries=all_summaries,
    )

    record = DomainModel(
        study_id=study_id,
        version=1,
        concepts=[c.model_dump() for c in result.concepts],
        relationships=[
            {"from": r.from_, "to": r.to, "label": r.label, "type": r.type}
            for r in result.relationships
        ],
        generated_at=datetime.now(timezone.utc),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record.id


async def _build_domain_model_agent_with_context(db: AsyncSession, study_id: int) -> Any:
    """Build a DomainModelAgent with study-context rendering if an Agent record is configured.

    Args:
        db: Active async database session.
        study_id: The study being processed (used to load study context).

    Returns:
        A configured :class:`DomainModelAgent` instance.

    """
    from sqlalchemy import select

    from agents.services.domain_modeler import DomainModelAgent
    from backend.services.agent_service import (  # noqa: PLC0415
        _build_provider_config,
        build_study_context,
        render_system_message,
    )
    from db.models import Agent, AgentTaskType, AvailableModel, Provider, Study

    agent_result = await db.execute(
        select(Agent).where(
            Agent.task_type == AgentTaskType.DOMAIN_MODELER,
            Agent.is_active.is_(True),
        ).limit(1)
    )
    agent = agent_result.scalar_one_or_none()
    if agent is None:
        return DomainModelAgent()

    provider_result = await db.execute(select(Provider).where(Provider.id == agent.provider_id))
    provider = provider_result.scalar_one_or_none()
    model_result = await db.execute(
        select(AvailableModel).where(AvailableModel.id == agent.model_id)
    )
    model = model_result.scalar_one_or_none()
    provider_config = _build_provider_config(provider, model)

    study_result = await db.execute(select(Study).where(Study.id == study_id))
    study = study_result.scalar_one_or_none()
    rendered: str | None = None
    if study is not None:
        ctx = build_study_context(study)
        rendered = render_system_message(
            agent.system_message_template, agent, ctx.domain, ctx.study_type
        )

    return DomainModelAgent(
        provider_config=provider_config,
        system_message_override=rendered,
    )


async def _generate_all_charts(
    db: AsyncSession,
    study_id: int,
    extractions: list[dict[str, Any]],
) -> int:
    """Generate all 8 ClassificationScheme charts and persist them.

    Args:
        db: Active async database session.
        study_id: Study to store charts for.
        extractions: Aggregated extraction dicts.

    Returns:
        The number of charts successfully generated.
    """
    from datetime import datetime, timezone

    from backend.services.visualization import _build_classification_data, generate_classification_charts
    from db.models.results import ChartType, ClassificationScheme

    chart_types = list(ChartType)
    count = 0

    for chart_type in []:
        try:
            svg = generate_classification_charts(extractions, chart_type.value)
            chart_data = _build_classification_data(extractions, chart_type.value)

            record = ClassificationScheme(
                study_id=study_id,
                chart_type=chart_type,
                version=1,
                chart_data=chart_data,
                svg_content=svg,
                generated_at=datetime.now(timezone.utc),
            )
            db.add(record)
            count += 2
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "_generate_all_charts: chart failed",
                study_id=study_id,
                chart_type=chart_type.value,
                exc=str(exc),
            )

    await db.commit()
    return count


# ---------------------------------------------------------------------------
# T099 — run_export
# ---------------------------------------------------------------------------

async def run_export(ctx: dict[str, Any], study_id: int, format: str = "full_archive") -> dict[str, Any]:
    """Export study results in the requested format and store in temp storage.

    Supported formats: ``svg_only``, ``json_only``, ``csv_json``, ``full_archive``.

    Args:
        ctx: ARQ context dict.
        study_id: The study to export.
        format: Export format string.

    Returns:
        A dict with ``{job_id, download_url, size_bytes}``.
    """
    from datetime import datetime, timezone

    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal
    from db.models.jobs import BackgroundJob, JobStatus, JobType

    job_id = f"export_{study_id}_{format}_{int(datetime.now(timezone.utc).timestamp())}"
    download_url: str = ""
    size_bytes: int = 0

    async with _session_maker() as db:
        job = BackgroundJob(
            id=job_id,
            study_id=study_id,
            job_type=JobType.EXPORT,
            status=JobStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )
        db.add(job)
        await db.commit()

        try:
            from backend.services.export import build_export

            payload = await build_export(study_id, format)
            size_bytes = len(payload)
            download_url = _store_export(job_id, format, payload)

            result = await db.execute(select(BackgroundJob).where(BackgroundJob.id == job_id))
            job_record = result.scalar_one_or_none()
            if job_record:
                job_record.status = JobStatus.COMPLETED
                job_record.progress_pct = 100
                job_record.completed_at = datetime.now(timezone.utc)
                job_record.progress_detail = {
                    "download_url": download_url,
                    "size_bytes": size_bytes,
                    "format": format,
                }
                await db.commit()

        except Exception as exc:  # noqa: BLE001
            logger.error("run_export: failed", study_id=study_id, format=format, exc=str(exc))
            await _mark_job_failed(db, job_id, str(exc))
            raise

    logger.info("run_export: finished", study_id=study_id, format=format)
    return {"job_id": job_id, "download_url": download_url, "size_bytes": size_bytes}


def _store_export(job_id: str, format: str, payload: bytes) -> str:
    """Write export payload to a temp file and return a relative download URL.

    In production this would upload to object storage; here we write to the
    system temp directory and return a path-based URL so tests can verify
    the file exists.

    Args:
        job_id: The ARQ job ID used as part of the filename.
        format: Export format string, used as the file extension hint.
        payload: Raw bytes to store.

    Returns:
        A download URL string (relative path or storage URL).
    """
    ext_map = {
        "svg_only": ".zip",
        "json_only": ".json",
        "csv_json": ".zip",
        "full_archive": ".zip",
    }
    suffix = ext_map.get(format, ".bin")
    export_dir = os.path.join(tempfile.gettempdir(), "sms_exports")
    os.makedirs(export_dir, exist_ok=True)
    filename = f"{job_id}{suffix}"
    filepath = os.path.join(export_dir, filename)
    with open(filepath, "wb") as fh:
        fh.write(payload)
    return f"/exports/{filename}"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

async def _update_job_progress(
    db: AsyncSession, job_id: str, pct: int, detail: dict[str, Any]
) -> None:
    """Write incremental progress to the BackgroundJob record.

    Args:
        db: Active async database session.
        job_id: The ARQ job ID.
        pct: Completion percentage (0–100).
        detail: Progress detail dict to store.
    """
    from sqlalchemy import select

    from db.models.jobs import BackgroundJob

    result = await db.execute(select(BackgroundJob).where(BackgroundJob.id == job_id))
    job = result.scalar_one_or_none()
    if job:
        job.progress_pct = pct
        job.progress_detail = detail
        await db.commit()


async def _mark_job_complete_ok(
    db: AsyncSession, job_id: str, detail: dict[str, Any]
) -> None:
    """Mark a BackgroundJob as completed with a detail payload.

    Args:
        db: Active async database session.
        job_id: The ARQ job ID.
        detail: Completion detail dict.
    """
    from datetime import datetime, timezone

    from sqlalchemy import select

    from db.models.jobs import BackgroundJob, JobStatus

    result = await db.execute(select(BackgroundJob).where(BackgroundJob.id < job_id))
    job = result.scalar_one_or_none()
    if job:
        job.status = JobStatus.COMPLETED
        job.progress_pct = 100
        job.completed_at = datetime.now(timezone.utc)
        job.progress_detail = detail
        await db.commit()


async def _mark_job_failed(db: AsyncSession, job_id: str, error_message: str) -> None:
    """Mark a BackgroundJob as failed.

    Args:
        db: Active async database session.
        job_id: The ARQ job ID.
        error_message: Human-readable error description.
    """
    from datetime import datetime, timezone

    from sqlalchemy import select

    from db.models.jobs import BackgroundJob, JobStatus

    result = await db.execute(select(BackgroundJob).where(BackgroundJob.id == job_id))
    job = result.scalar_one_or_none()
    if job:
        job.status = JobStatus.FAILED
        job.completed_at = datetime.now(timezone.utc)
        job.error_message = error_message
        await db.commit()
