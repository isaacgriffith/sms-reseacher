"""Search metrics aggregation endpoint."""

from db.models.search_exec import SearchExecution, SearchMetrics
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db

router = APIRouter(tags=["metrics"])
logger = get_logger(__name__)


class PhaseMetrics(BaseModel):
    """Metrics for one search phase."""

    phase_tag: str
    search_execution_id: int
    total_identified: int
    accepted: int
    rejected: int
    duplicates: int


class StudyMetricsResponse(BaseModel):
    """Aggregated metrics for a study."""

    study_id: int
    phases: list[PhaseMetrics]
    totals: PhaseMetrics


@router.get(
    "/studies/{study_id}/metrics",
    response_model=StudyMetricsResponse,
    summary="Get search metrics for a study",
)
async def get_study_metrics(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StudyMetricsResponse:
    """Return per-phase and total search metrics for a study."""
    await require_study_member(study_id, current_user, db)

    executions_result = await db.execute(
        select(SearchExecution)
        .where(SearchExecution.study_id == study_id)
        .order_by(SearchExecution.id)
    )
    executions = executions_result.scalars().all()

    phases: list[PhaseMetrics] = []
    total_identified = 0
    total_accepted = 0
    total_rejected = 0
    total_duplicates = 0

    for se in executions:
        metrics_result = await db.execute(
            select(SearchMetrics).where(SearchMetrics.search_execution_id == se.id)
        )
        m = metrics_result.scalar_one_or_none()
        if m is None:
            continue

        phases.append(
            PhaseMetrics(
                phase_tag=se.phase_tag,
                search_execution_id=se.id,
                total_identified=m.total_identified,
                accepted=m.accepted,
                rejected=m.rejected,
                duplicates=m.duplicates,
            )
        )
        total_identified += m.total_identified
        total_accepted += m.accepted
        total_rejected += m.rejected
        total_duplicates += m.duplicates

    return StudyMetricsResponse(
        study_id=study_id,
        phases=phases,
        totals=PhaseMetrics(
            phase_tag="all",
            search_execution_id=0,
            total_identified=total_identified,
            accepted=total_accepted,
            rejected=total_rejected,
            duplicates=total_duplicates,
        ),
    )
