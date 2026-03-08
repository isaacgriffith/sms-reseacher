"""Background job status and SSE progress stream endpoints."""

import asyncio
import json
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db
from db.models.jobs import BackgroundJob, JobStatus

router = APIRouter(tags=["jobs"])
logger = get_logger(__name__)


class BackgroundJobResponse(BaseModel):
    """Response for a background job."""

    id: str
    study_id: int
    job_type: str
    status: str
    progress_pct: int
    progress_detail: dict | None
    error_message: str | None


@router.get(
    "/jobs/{job_id}/progress",
    summary="SSE stream for background job progress",
)
async def job_progress_sse(
    job_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Stream real-time progress for a background job via Server-Sent Events.

    Polls the BackgroundJob table every 0.5 seconds and emits:
    - ``event: progress`` — while job is queued or running
    - ``event: complete`` — when job reaches ``completed`` status
    - ``event: error`` — when job reaches ``failed`` status

    The stream auto-closes on completion or error.
    """

    async def event_generator() -> AsyncIterator[str]:
        from backend.core.database import _session_maker  # noqa: PLC2701

        max_polls = 7200  # 1 hour at 0.5s intervals
        polls = 0
        while polls < max_polls:
            async with _session_maker() as poll_db:
                result = await poll_db.execute(
                    select(BackgroundJob).where(BackgroundJob.id == job_id)
                )
                job = result.scalar_one_or_none()

            if job is None:
                yield f"event: error\ndata: {json.dumps({'error': 'job not found'})}\n\n"
                return

            payload = {
                "job_id": job_id,
                "status": job.status.value,
                "progress_pct": job.progress_pct,
                "detail": job.progress_detail,
            }

            if job.status == JobStatus.COMPLETED:
                yield f"event: complete\ndata: {json.dumps(payload)}\n\n"
                return
            elif job.status == JobStatus.FAILED:
                payload["error"] = job.error_message
                yield f"event: error\ndata: {json.dumps(payload)}\n\n"
                return
            else:
                yield f"event: progress\ndata: {json.dumps(payload)}\n\n"

            await asyncio.sleep(0.5)
            polls += 1

        yield f"event: error\ndata: {json.dumps({'error': 'stream timeout'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/studies/{study_id}/jobs",
    response_model=list[BackgroundJobResponse],
    summary="List background jobs for a study",
)
async def list_study_jobs(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BackgroundJobResponse]:
    """Return the 20 most recent background jobs for a study."""
    await require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(BackgroundJob)
        .where(BackgroundJob.study_id == study_id)
        .order_by(BackgroundJob.queued_at.desc())
        .limit(20)
    )
    jobs = result.scalars().all()
    return [
        BackgroundJobResponse(
            id=j.id,
            study_id=j.study_id,
            job_type=j.job_type.value,
            status=j.status.value,
            progress_pct=j.progress_pct,
            progress_detail=j.progress_detail,
            error_message=j.error_message,
        )
        for j in jobs
    ]
