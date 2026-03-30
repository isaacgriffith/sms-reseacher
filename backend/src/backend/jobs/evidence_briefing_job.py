"""ARQ background job for Evidence Briefing generation (feature 008).

This module provides the ``run_generate_evidence_briefing`` job function
registered with the ARQ worker.  The job renders the Jinja2 HTML template,
converts it to PDF via ``weasyprint``, and stores the output file paths on the
:class:`~db.models.rapid_review.EvidenceBriefing` record.
"""

from __future__ import annotations

from typing import Any

from backend.core.config import get_logger

logger = get_logger(__name__)


async def run_generate_evidence_briefing(
    ctx: dict[str, Any],
    *,
    briefing_id: int,
) -> dict[str, Any]:
    """Generate HTML and PDF exports for an Evidence Briefing version.

    Renders the Jinja2 HTML template from
    ``backend/templates/rapid/evidence_briefing.html.j2`` and converts it to
    a one-page A4 PDF via ``weasyprint``.  Stores the output paths in
    :attr:`~db.models.rapid_review.EvidenceBriefing.html_path` and
    :attr:`~db.models.rapid_review.EvidenceBriefing.pdf_path`.

    Job status is tracked via a :class:`~db.models.jobs.BackgroundJob` record
    whose ID follows the pattern ``rr_briefing_{briefing_id}_{ts}``.
    The route handler creates the record before enqueueing; this job updates
    the status to ``RUNNING`` then ``COMPLETED`` or ``FAILED``.

    Args:
        ctx: ARQ worker context dict (contains Redis connection, etc.).
        briefing_id: Primary key of the Evidence Briefing record to process.

    Returns:
        A dict with ``status``, ``briefing_id``, and ``study_id``.

    """
    from db.models.jobs import BackgroundJob, JobStatus
    from db.models.rapid_review import EvidenceBriefing
    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal
    from backend.services import evidence_briefing_service

    job_id: str | None = None
    study_id: int | None = None

    async with _session_maker() as db:
        # ---- Fetch briefing --------------------------------------------------
        briefing_result = await db.execute(
            select(EvidenceBriefing).where(EvidenceBriefing.id == briefing_id)
        )
        briefing = briefing_result.scalar_one_or_none()
        if briefing is None:
            logger.error(
                "run_generate_evidence_briefing: briefing not found",
                briefing_id=briefing_id,
            )
            return {"status": "failed", "briefing_id": briefing_id, "study_id": None}

        study_id = briefing.study_id

        # ---- Find the BackgroundJob record created by the route handler ------
        job_prefix = f"rr_briefing_{briefing_id}_"
        job_result = await db.execute(
            select(BackgroundJob).where(
                BackgroundJob.id.like(f"{job_prefix}%"),
                BackgroundJob.study_id == study_id,
            )
        )
        bg_job = job_result.scalars().first()
        if bg_job is not None:
            job_id = bg_job.id
            bg_job.status = JobStatus.RUNNING
            await db.commit()

        bound = logger.bind(briefing_id=briefing_id, study_id=study_id, job_id=job_id)
        bound.info("run_generate_evidence_briefing: starting")

        try:
            # ---- Generate HTML -----------------------------------------------
            await evidence_briefing_service.generate_html(briefing_id, db)
            bound.info("run_generate_evidence_briefing: html generated")

            # ---- Convert to PDF ----------------------------------------------
            await evidence_briefing_service.generate_pdf(briefing_id, db)
            bound.info("run_generate_evidence_briefing: pdf generated")

            if bg_job is not None:
                bg_job.status = JobStatus.COMPLETED
                await db.commit()

            bound.info("run_generate_evidence_briefing: completed")
            return {"status": "completed", "briefing_id": briefing_id, "study_id": study_id}

        except Exception as exc:  # noqa: BLE001
            bound.error("run_generate_evidence_briefing: failed", exc=str(exc))
            if bg_job is not None:
                bg_job.status = JobStatus.FAILED
                bg_job.error_message = str(exc)
                await db.commit()
            return {"status": "failed", "briefing_id": briefing_id, "study_id": study_id}
