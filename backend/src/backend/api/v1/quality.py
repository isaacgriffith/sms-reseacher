"""Quality evaluation endpoints: list, detail, and enqueue quality judge job (US7)."""

from datetime import UTC, datetime

import arq.connections
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db

router = APIRouter(tags=["quality"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Response / request schemas
# ---------------------------------------------------------------------------


class QualityReportSummary(BaseModel):
    """Lightweight quality report for list endpoints."""

    id: int
    study_id: int
    version: int
    total_score: int
    generated_at: datetime


class QualityReportDetail(BaseModel):
    """Full quality report including per-rubric details and recommendations."""

    id: int
    study_id: int
    version: int
    score_need_for_review: int
    score_search_strategy: int
    score_search_evaluation: int
    score_extraction_classification: int
    score_study_validity: int
    total_score: int
    rubric_details: dict | None
    recommendations: list | None
    generated_at: datetime


class QualityJobResponse(BaseModel):
    """Response for POST /quality-reports — 202 Accepted."""

    job_id: str
    study_id: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _load_report(study_id: int, report_id: int, db: AsyncSession):
    """Load a QualityReport belonging to the given study, or raise 404.

    Args:
        study_id: Owning study.
        report_id: QualityReport primary key.
        db: Active async session.

    Returns:
        The :class:`QualityReport` instance.

    Raises:
        HTTPException: 404 if the report does not exist or belongs to a
            different study.

    """
    from db.models.results import QualityReport

    result = await db.execute(
        select(QualityReport).where(
            QualityReport.id == report_id,
            QualityReport.study_id == study_id,
        )
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quality report not found"
        )
    return report


def _to_summary(report) -> QualityReportSummary:
    """Build a :class:`QualityReportSummary` from a QualityReport ORM row.

    Args:
        report: :class:`QualityReport` ORM instance.

    Returns:
        A populated :class:`QualityReportSummary`.

    """
    return QualityReportSummary(
        id=report.id,
        study_id=report.study_id,
        version=report.version,
        total_score=report.total_score,
        generated_at=report.generated_at,
    )


def _to_detail(report) -> QualityReportDetail:
    """Build a :class:`QualityReportDetail` from a QualityReport ORM row.

    Args:
        report: :class:`QualityReport` ORM instance.

    Returns:
        A populated :class:`QualityReportDetail`.

    """
    return QualityReportDetail(
        id=report.id,
        study_id=report.study_id,
        version=report.version,
        score_need_for_review=report.score_need_for_review,
        score_search_strategy=report.score_search_strategy,
        score_search_evaluation=report.score_search_evaluation,
        score_extraction_classification=report.score_extraction_classification,
        score_study_validity=report.score_study_validity,
        total_score=report.total_score,
        rubric_details=report.rubric_details,
        recommendations=report.recommendations,
        generated_at=report.generated_at,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/quality-reports",
    response_model=list[QualityReportSummary],
    summary="List quality reports for a study",
)
async def list_quality_reports(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[QualityReportSummary]:
    """Return all quality reports for the study, newest first."""
    await require_study_member(study_id, current_user, db)

    from db.models.results import QualityReport

    result = await db.execute(
        select(QualityReport)
        .where(QualityReport.study_id == study_id)
        .order_by(QualityReport.version.desc())
    )
    return [_to_summary(r) for r in result.scalars().all()]


@router.get(
    "/studies/{study_id}/quality-reports/{report_id}",
    response_model=QualityReportDetail,
    summary="Get a quality report with rubric details",
)
async def get_quality_report(
    study_id: int,
    report_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QualityReportDetail:
    """Return one quality report with full rubric details and recommendations."""
    await require_study_member(study_id, current_user, db)
    report = await _load_report(study_id, report_id, db)
    return _to_detail(report)


@router.post(
    "/studies/{study_id}/quality-reports",
    response_model=QualityJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enqueue a quality evaluation job",
)
async def create_quality_report(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QualityJobResponse:
    """Enqueue a background quality evaluation job for the study."""
    from datetime import datetime

    from db.models.jobs import BackgroundJob, JobStatus, JobType

    from backend.core.config import get_settings

    await require_study_member(study_id, current_user, db)

    settings = get_settings()
    redis = await arq.connections.create_pool(
        arq.connections.RedisSettings.from_dsn(settings.redis_url)
    )
    job = await redis.enqueue_job("run_quality_eval", study_id)
    await redis.close()

    job_id = job.job_id if job else f"quality_eval_{study_id}_{int(datetime.now(UTC).timestamp())}"

    bg_job = BackgroundJob(
        id=job_id,
        study_id=study_id,
        job_type=JobType.QUALITY_EVAL,
        status=JobStatus.QUEUED,
    )
    db.add(bg_job)
    await db.commit()

    logger.info("create_quality_report: enqueued", study_id=study_id, job_id=job_id)
    return QualityJobResponse(job_id=job_id, study_id=study_id)
