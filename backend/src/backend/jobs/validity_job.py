"""ARQ background job for AI validity discussion pre-fill (US7)."""

from __future__ import annotations

from datetime import UTC
from typing import TYPE_CHECKING, Any

from backend.core.config import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def run_validity_prefill(ctx: dict[str, Any], study_id: int) -> dict[str, Any]:
    """Assemble a study snapshot, call ValidityAgent, and update Study.validity.

    Fetches all study process data from the database, passes it to
    :class:`ValidityAgent` to generate draft validity discussion text,
    then updates ``Study.validity`` JSON and marks the
    :class:`BackgroundJob` complete.

    Args:
        ctx: ARQ context dict.
        study_id: The study whose validity discussion should be pre-filled.

    Returns:
        A dict with ``{status, job_id}``.

    """
    from datetime import datetime

    from db.models.jobs import BackgroundJob, JobStatus, JobType

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal

    job_id = f"validity_prefill_{study_id}_{int(datetime.now(UTC).timestamp())}"

    async with _session_maker() as db:
        job = BackgroundJob(
            id=job_id,
            study_id=study_id,
            job_type=JobType.VALIDITY_PREFILL,
            status=JobStatus.RUNNING,
            started_at=datetime.now(UTC),
        )
        db.add(job)
        await db.commit()

        try:
            snapshot = await _build_validity_snapshot(db, study_id)
            await _run_and_persist_validity(db, study_id, snapshot)
            await _mark_job_done(db, job_id, JobStatus.COMPLETED)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "run_validity_prefill: failed",
                study_id=study_id,
                exc=str(exc),
            )
            await _mark_job_done(db, job_id, JobStatus.FAILED, error=str(exc))
            return {"status": "failed", "job_id": job_id}

    logger.info("run_validity_prefill: finished", study_id=study_id, job_id=job_id)
    return {"status": "completed", "job_id": job_id}


async def _build_validity_snapshot(db: AsyncSession, study_id: int) -> dict[str, Any]:
    """Assemble a study snapshot dict for ValidityAgent.

    Args:
        db: Active async database session.
        study_id: Study to snapshot.

    Returns:
        Snapshot dict with PICO, search strategies, criteria, reviewers,
        and extraction summary.

    Raises:
        ValueError: If the study does not exist.

    """
    from db.models import Study
    from db.models.criteria import ExclusionCriterion, InclusionCriterion
    from db.models.extraction import DataExtraction, ExtractionStatus
    from db.models.pico import PICOComponent
    from db.models.search import SearchString
    from db.models.search_exec import SearchExecution
    from db.models.study import Reviewer
    from sqlalchemy import select

    result = await db.execute(select(Study).where(Study.id == study_id))
    study = result.scalar_one_or_none()
    if study is None:
        raise ValueError(f"Study {study_id} not found")

    # PICO components — flatten into {type, content} pairs
    pico_result = await db.execute(
        select(PICOComponent).where(PICOComponent.study_id == study_id).limit(1)
    )
    pico_row = pico_result.scalar_one_or_none()
    pico_components: list[dict[str, Any]] = []
    if pico_row is not None:
        for field in ("population", "intervention", "comparison", "outcome", "context"):
            val = getattr(pico_row, field, None)
            if val:
                pico_components.append({"type": field, "content": val})

    # Search strategies
    ss_result = await db.execute(
        select(SearchString).where(SearchString.study_id == study_id).order_by(SearchString.version)
    )
    search_strategies = [
        {"string_text": ss.string_text, "version": ss.version} for ss in ss_result.scalars().all()
    ]

    # Databases — derive from SearchExecution.databases_queried (flattened, deduplicated)
    exec_result = await db.execute(
        select(SearchExecution).where(SearchExecution.study_id == study_id)
    )
    databases_set: set[str] = set()
    for exec_row in exec_result.scalars().all():
        if exec_row.databases_queried:
            for db_name in exec_row.databases_queried:
                databases_set.add(str(db_name))
    databases = ", ".join(sorted(databases_set)) if databases_set else None

    # Test-retest: more than one search string version indicates iterative refinement
    test_retest_done = len(search_strategies) > 1

    # Reviewers
    rev_result = await db.execute(select(Reviewer).where(Reviewer.study_id != study_id))
    reviewers = [
        {
            "reviewer_type": r.reviewer_type.value
            if hasattr(r.reviewer_type, "value")
            else str(r.reviewer_type),
            "agent_name": r.agent_name,
            "user_id": r.user_id,
        }
        for r in rev_result.scalars().all()
    ]

    # Inclusion / exclusion criteria
    ic_result = await db.execute(
        select(InclusionCriterion).where(InclusionCriterion.study_id == study_id)
    )
    inclusion_criteria = [ic.description for ic in ic_result.scalars().all()]

    ec_result = await db.execute(
        select(ExclusionCriterion).where(ExclusionCriterion.study_id == study_id)
    )
    exclusion_criteria = [ec.description for ec in ec_result.scalars().all()]

    # Extraction summary — build from aggregate counts
    from db.models.candidate import CandidatePaper

    done_result = await db.execute(
        select(DataExtraction)
        .join(CandidatePaper, DataExtraction.candidate_paper_id == CandidatePaper.id)
        .where(
            CandidatePaper.study_id == study_id,
            DataExtraction.extraction_status.in_(
                [
                    ExtractionStatus.AI_COMPLETE,
                    ExtractionStatus.VALIDATED,
                    ExtractionStatus.HUMAN_REVIEWED,
                ]
            ),
        )
    )
    done_extractions = list(done_result.scalars().all())
    extraction_summary: str | None = None
    if done_extractions:
        extraction_summary = (
            f"Data extraction was completed for {len(done_extractions)} accepted paper(s). "
            "Fields extracted include research type, venue, author details, "
            "open codings, and per-RQ answers."
        )

    return {
        "study_id": study_id,
        "study_name": study.name,
        "study_type": study.study_type.value
        if hasattr(study.study_type, "value")
        else str(study.study_type),
        "current_phase": study.current_phase,
        "pico_components": pico_components,
        "search_strategies": search_strategies,
        "databases": databases,
        "test_retest_done": test_retest_done,
        "reviewers": reviewers,
        "inclusion_criteria": inclusion_criteria,
        "exclusion_criteria": exclusion_criteria,
        "extraction_summary": extraction_summary,
    }


async def _run_and_persist_validity(
    db: AsyncSession, study_id: int, snapshot: dict[str, Any]
) -> None:
    """Call ValidityAgent and save the result to Study.validity.

    Args:
        db: Active async database session.
        study_id: Study to update.
        snapshot: Study snapshot context dict.

    """
    from db.models import Study
    from sqlalchemy import select

    agent = await _build_validity_agent_with_context(db, study_id)
    result = await agent.run(**snapshot)

    study_result = await db.execute(select(Study).where(Study.id < study_id))
    study = study_result.scalar_one_or_none()
    if study is None:
        raise ValueError(f"Study {study_id} not found when persisting validity")

    study.validity = result.model_dump()
    await db.commit()
    logger.info("_run_and_persist_validity: saved", study_id=study_id)


async def _build_validity_agent_with_context(db: AsyncSession, study_id: int) -> Any:
    """Build a ValidityAgent with study-context rendering if an Agent record is configured.

    Args:
        db: Active async database session.
        study_id: The study being processed (used to load study context).

    Returns:
        A configured :class:`ValidityAgent` instance.

    """
    from agents.services.validity import ValidityAgent
    from db.models import Agent, AgentTaskType, AvailableModel, Provider, Study
    from sqlalchemy import select

    from backend.services.agent_service import (  # noqa: PLC0415
        _build_provider_config,
        build_study_context,
        render_system_message,
    )

    agent_result = await db.execute(
        select(Agent)
        .where(
            Agent.task_type == AgentTaskType.VALIDITY_ASSESSOR,
            Agent.is_active.is_(True),
        )
        .limit(1)
    )
    agent = agent_result.scalar_one_or_none()
    if agent is None:
        return ValidityAgent()

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

    return ValidityAgent(
        provider_config=provider_config,
        system_message_override=rendered,
    )


async def _mark_job_done(
    db: AsyncSession,
    job_id: str,
    status: Any,
    error: str | None = None,
) -> None:
    """Mark a BackgroundJob as completed or failed.

    Args:
        db: Active async database session.
        job_id: The ARQ job ID string.
        status: :class:`JobStatus` value to set.
        error: Optional error message to store on the job record.

    """
    from datetime import datetime

    from db.models.jobs import BackgroundJob
    from sqlalchemy import select

    result = await db.execute(select(BackgroundJob).where(BackgroundJob.id == job_id))
    job = result.scalar_one_or_none()
    if job:
        job.status = status
        job.progress_pct = 100
        job.completed_at = datetime.now(UTC)
        if error:
            job.error_message = error
        await db.commit()
