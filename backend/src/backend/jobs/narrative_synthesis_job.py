"""ARQ background job for AI-assisted narrative synthesis drafting (feature 008).

This module provides the ``run_narrative_draft`` job function registered with
the ARQ worker.  The job fetches the target
:class:`~db.models.rapid_review.RRNarrativeSynthesisSection`, calls the
:class:`~agents.narrative_synthesiser_agent.NarrativeSynthesiserAgent` to
produce a practitioner-friendly draft, and writes the result to
``ai_draft_text``.
"""

from __future__ import annotations

from typing import Any

from backend.core.config import get_logger

logger = get_logger(__name__)


async def run_narrative_draft(
    ctx: dict[str, Any],
    *,
    section_id: int,
) -> dict[str, Any]:
    """Generate an AI narrative draft for a synthesis section.

    Fetches the :class:`~db.models.rapid_review.RRNarrativeSynthesisSection`
    identified by *section_id*, loads the corresponding protocol research
    question, collects included papers for the study, invokes the
    ``NarrativeSynthesiserAgent``, and stores the resulting text in
    ``ai_draft_text``.

    Job status is tracked via a :class:`~db.models.jobs.BackgroundJob` record
    whose ID follows the pattern ``rr_narrative_draft_{section_id}_{ts}``.
    The route handler creates the record before enqueueing; this job updates
    the status to ``RUNNING`` then ``COMPLETED`` or ``FAILED``.

    Args:
        ctx: ARQ worker context dict (contains Redis connection, etc.).
        section_id: Primary key of the synthesis section to draft.

    Returns:
        A dict with ``status``, ``section_id``, and ``study_id``.

    """
    from agents.narrative_synthesiser_agent import NarrativeSynthesiserAgent, PaperSummary
    from db.models import InclusionStatus, Paper, StudyPaper
    from db.models.jobs import BackgroundJob, JobStatus
    from db.models.rapid_review import RRNarrativeSynthesisSection
    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal

    job_id: str | None = None
    study_id: int | None = None

    async with _session_maker() as db:
        # ---- Fetch section ---------------------------------------------------
        section_result = await db.execute(
            select(RRNarrativeSynthesisSection).where(RRNarrativeSynthesisSection.id == section_id)
        )
        section = section_result.scalar_one_or_none()
        if section is None:
            logger.error("run_narrative_draft: section not found", section_id=section_id)
            return {"status": "failed", "section_id": section_id, "study_id": None}

        study_id = section.study_id

        # ---- Find the BackgroundJob record created by the route handler ------
        job_prefix = f"rr_narrative_draft_{section_id}_"
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

        bound = logger.bind(section_id=section_id, study_id=study_id, job_id=job_id)
        bound.info("run_narrative_draft: starting")

        try:
            # ---- Fetch protocol for the research question --------------------
            from backend.services import rr_protocol_service

            protocol = await rr_protocol_service.get_or_create_protocol(study_id, db)
            rqs: list[str] = protocol.research_questions or []
            rq_text = rqs[section.rq_index] if section.rq_index < len(rqs) else ""

            # ---- Collect included papers -------------------------------------
            papers_result = await db.execute(
                select(Paper)
                .join(StudyPaper, StudyPaper.paper_id == Paper.id)
                .where(
                    StudyPaper.study_id == study_id,
                    StudyPaper.inclusion_status == InclusionStatus.INCLUDED,
                )
                .limit(50)  # cap to avoid excessive token usage
            )
            paper_rows = papers_result.scalars().all()
            papers = [PaperSummary(title=p.title or "", abstract=p.abstract) for p in paper_rows]

            # ---- Call agent --------------------------------------------------
            agent = NarrativeSynthesiserAgent()
            draft_text = await agent.draft_section(
                study_id=study_id,
                rq_index=section.rq_index,
                rq_text=rq_text,
                papers=papers,
            )

            # ---- Persist result ---------------------------------------------
            section.ai_draft_text = draft_text
            if bg_job is not None:
                bg_job.status = JobStatus.COMPLETED
            await db.commit()
            bound.info("run_narrative_draft: completed")
            return {"status": "completed", "section_id": section_id, "study_id": study_id}

        except Exception as exc:  # noqa: BLE001
            bound.error("run_narrative_draft: failed", exc=str(exc))
            if bg_job is not None:
                bg_job.status = JobStatus.FAILED
                bg_job.error_message = str(exc)
                await db.commit()
            return {"status": "failed", "section_id": section_id, "study_id": study_id}
