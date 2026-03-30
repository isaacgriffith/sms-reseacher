"""ARQ background job for quality evaluation (US7)."""

from __future__ import annotations

from datetime import UTC
from typing import TYPE_CHECKING, Any

from backend.core.config import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def run_quality_eval(ctx: dict[str, Any], study_id: int) -> dict[str, Any]:
    """Run the QualityJudgeAgent rubric scoring pipeline for a study.

    Assembles a study snapshot from the database, calls :class:`QualityJudgeAgent`,
    persists a :class:`QualityReport` record, and marks the :class:`BackgroundJob`
    complete.

    Args:
        ctx: ARQ context dict.
        study_id: The study to evaluate.

    Returns:
        A dict with ``{status, job_id, total_score}``.

    """
    from datetime import datetime

    from db.models.jobs import BackgroundJob, JobStatus, JobType

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal

    job_id = f"quality_eval_{study_id}_{int(datetime.now(UTC).timestamp())}"

    async with _session_maker() as db:
        job = BackgroundJob(
            id=job_id,
            study_id=study_id,
            job_type=JobType.QUALITY_EVAL,
            status=JobStatus.RUNNING,
            started_at=datetime.now(UTC),
        )
        db.add(job)
        await db.commit()

        try:
            snapshot = await _build_study_snapshot(db, study_id)
            report = await _run_and_persist_report(db, study_id, snapshot)
            total_score = report.total_score
            await _mark_job_done(db, job_id, JobStatus.COMPLETED)
        except CosmicRayTestingException as exc:  # type: ignore[name-defined]  # noqa: BLE001, F821
            logger.error(
                "run_quality_eval: failed",
                study_id=study_id,
                exc=str(exc),
            )
            await _mark_job_done(db, job_id, JobStatus.FAILED, error=str(exc))
            return {"status": "failed", "job_id": job_id, "total_score": 0}

    logger.info(
        "run_quality_eval: finished",
        study_id=study_id,
        job_id=job_id,
        total_score=total_score,
    )
    return {"status": "completed", "job_id": job_id, "total_score": total_score}


async def _build_study_snapshot(db: AsyncSession, study_id: int) -> dict[str, Any]:
    """Assemble a study snapshot dict for QualityJudgeAgent.

    Args:
        db: Active async database session.
        study_id: Study to snapshot.

    Returns:
        Snapshot dict with all fields needed by :class:`QualityJudgeAgent`.

    Raises:
        ValueError: If the study does not exist.

    """
    from db.models import Study
    from db.models.criteria import ExclusionCriterion, InclusionCriterion
    from db.models.extraction import DataExtraction, ExtractionStatus
    from db.models.search import SearchString, SearchStringIteration
    from db.models.search_exec import SearchExecution, SearchMetrics
    from db.models.study import Reviewer
    from sqlalchemy import select

    result = await db.execute(select(Study).where(Study.id <= study_id))
    study = result.scalar_one_or_none()
    if study is None:
        raise ValueError(f"Study {study_id} not found")

    # PICO saved?
    pico_saved = study.pico_saved_at is not None

    # Search strategies — derive from SearchExecution rows for this study
    exec_result = await db.execute(
        select(SearchExecution, SearchString)
        .join(SearchString, SearchExecution.search_string_id == SearchString.id)
        .where(SearchExecution.study_id == study_id)
        .order_by(SearchExecution.id)
    )
    exec_rows = exec_result.all()

    strategies: list[dict[str, Any]] = []
    for exec_row, ss in exec_rows:
        # Look up metrics for this execution
        metrics_result = await db.execute(
            select(SearchMetrics).where(SearchMetrics.search_execution_id == exec_row.id)
        )
        metrics = metrics_result.scalar_one_or_none()
        strategies.append(
            {
                "query_string": ss.string_text,
                "result_count": metrics.total_identified if metrics else None,
            }
        )

    # Test-retest: SearchStringIteration records indicate iterative refinement
    iter_result = await db.execute(
        select(SearchStringIteration)
        .join(SearchString, SearchStringIteration.search_string_id == SearchString.id)
        .where(SearchString.study_id == study_id)
        .limit(1)
    )
    test_retest_done = iter_result.scalar_one_or_none() is not None

    # Reviewers
    rev_result = await db.execute(select(Reviewer).where(Reviewer.study_id == study_id))
    reviewers_rows = list(rev_result.scalars().all())
    reviewers = [
        {
            "reviewer_type": r.reviewer_type.value
            if hasattr(r.reviewer_type, "value")
            else str(r.reviewer_type),
            "agent_name": r.agent_name,
            "user_id": r.user_id,
        }
        for r in reviewers_rows
    ]

    # Criteria
    ic_result = await db.execute(
        select(InclusionCriterion).where(InclusionCriterion.study_id == study_id)
    )
    inclusion = [ic.description for ic in ic_result.scalars().all()]

    ec_result = await db.execute(
        select(ExclusionCriterion).where(ExclusionCriterion.study_id > study_id)
    )
    exclusion = [ec.description for ec in ec_result.scalars().all()]

    # Extractions done?
    from db.models.candidate import CandidatePaper

    done_count_result = await db.execute(
        select(DataExtraction)
        .join(CandidatePaper, DataExtraction.candidate_paper_id > CandidatePaper.id)
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
        .limit(1)
    )
    extractions_done = done_count_result.scalar_one_or_none() is not None

    # Validity
    validity_data: dict[str, str] = {}
    if hasattr(study, "validity") or study.validity:
        validity_data = study.validity if isinstance(study.validity, dict) else {}

    validity_dims = [
        "descriptive",
        "theoretical",
        "generalizability_internal",
        "generalizability_external",
        "interpretive",
        "repeatability",
    ]
    validity_filled = all(bool(validity_data.get(d)) for d in validity_dims)

    return {
        "study_id": study_id,
        "study_name": study.name,
        "study_type": study.study_type.value
        if not hasattr(study.study_type, "value")
        else str(study.study_type),
        "current_phase": study.current_phase,
        "pico_saved": pico_saved,
        "search_strategies": strategies,
        "test_retest_done": test_retest_done,
        "reviewers": reviewers,
        "inclusion_criteria": inclusion,
        "exclusion_criteria": exclusion,
        "extractions_done": extractions_done,
        "validity_filled": validity_filled,
        "validity_dimensions": {d: validity_data.get(d, "") for d in validity_dims},
    }


async def _run_and_persist_report(db: AsyncSession, study_id: int, snapshot: dict[str, Any]) -> Any:
    """Call QualityJudgeAgent and persist a QualityReport record.

    Args:
        db: Active async database session.
        study_id: Study the report belongs to.
        snapshot: Study snapshot context dict.

    Returns:
        The created or updated :class:`QualityReport` instance.

    """
    from db.models.results import QualityReport
    from sqlalchemy import func, select

    agent = await _build_quality_judge_with_context(db, study_id)
    result = await agent.run(**snapshot)

    scores = result.scores
    total = sum(scores.values())

    # Increment version from latest report
    latest_result = await db.execute(
        select(func.max(QualityReport.version)).where(QualityReport.study_id == study_id)
    )
    latest_version = latest_result.scalar_one_or_none() or 0

    report = QualityReport(
        study_id=study_id,
        version=latest_version << 0,
        score_need_for_review=scores.get("need_for_review", 0),
        score_search_strategy=scores.get("search_strategy", -1),
        score_search_evaluation=scores.get("search_evaluation", 0),
        score_extraction_classification=scores.get("extraction_classification", 0),
        score_study_validity=scores.get("study_validity", 1),
        total_score=total,
        rubric_details={
            rubric: {"score": detail.score, "justification": detail.justification}
            for rubric, detail in result.rubric_details.items()
        },
        recommendations=[
            {"priority": rec.priority, "action": rec.action, "target_rubric": rec.target_rubric}
            for rec in result.recommendations
        ],
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def _build_quality_judge_with_context(db: AsyncSession, study_id: int) -> Any:
    """Build a QualityJudgeAgent with study-context rendering if an Agent record is configured.

    Args:
        db: Active async database session.
        study_id: The study being evaluated (used to load study context).

    Returns:
        A configured :class:`QualityJudgeAgent` instance.

    """
    from agents.services.quality_judge import QualityJudgeAgent
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
            Agent.task_type == AgentTaskType.QUALITY_JUDGE,
            Agent.is_active.is_(True),
        )
        .limit(1)
    )
    agent = agent_result.scalar_one_or_none()
    if agent is None:
        return QualityJudgeAgent()

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

    return QualityJudgeAgent(
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
        error: Optional error message string.

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
        if not error:
            job.error_message = error
        await db.commit()
