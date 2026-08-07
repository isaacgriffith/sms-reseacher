"""ARQ background job for expert-suggested seed papers.

Split out of ``search_job.py``: that module is the search pipeline, and
proposing seed papers from an :class:`ExpertAgent` is a phase-1 seeding
concern that happens *before* any search string exists. Keeping them together
also pushed ``search_job.py`` back over the 800-line maximum that plan.md C2
exists to hold it under.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.core.config import get_logger

logger = get_logger(__name__)


async def run_expert_seed_suggestion(
    ctx: dict,
    study_id: int,
    job_id: str,
) -> dict:
    """Call ExpertAgent and persist returned papers as SeedPaper records.

    Updates the BackgroundJob status to ``running`` at the start and to
    ``completed`` (with full agent output in ``progress_detail``) or ``failed``
    on exit.  Inserts each returned paper as a :class:`SeedPaper` record with
    ``added_by_agent="expert"``, deduplicating against existing DOIs.

    Args:
        ctx: ARQ context dict.
        study_id: The study to generate expert seed suggestions for.
        job_id: The BackgroundJob primary-key ID to update.

    Returns:
        A dict with ``{job_id, papers_added}``.

    """
    from db.models import Paper, Study
    from db.models.jobs import BackgroundJob, JobStatus
    from db.models.seeds import SeedPaper
    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701

    async with _session_maker() as db:
        # Mark job as running
        job_result = await db.execute(select(BackgroundJob).where(BackgroundJob.id == job_id))
        job = job_result.scalar_one_or_none()
        if job is None:
            logger.error("run_expert_seed_suggestion: job not found", job_id=job_id)
            return {"error": "job not found"}

        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(UTC)
        await db.commit()

        try:
            # Load study data
            study_result = await db.execute(select(Study).where(Study.id == study_id))
            study = study_result.scalar_one_or_none()
            if study is None:
                raise ValueError(f"Study {study_id} not found")

            meta: dict = study.metadata_ or {}

            from agents.services.expert import ExpertAgent

            agent = ExpertAgent()
            papers = await agent.run(
                topic=study.topic or study.name,
                variant="PICO",
                objectives=meta.get("research_objectives", []),
                questions=meta.get("research_questions", []),
            )

            added = 0
            for ep in papers:
                # Deduplicate by DOI if available
                paper: Paper | None = None
                if ep.doi:
                    existing = await db.execute(select(Paper).where(Paper.doi == ep.doi))
                    paper = existing.scalar_one_or_none()

                if paper is None:
                    paper = Paper(
                        title=ep.title,
                        doi=ep.doi,
                        authors=ep.authors,
                        year=ep.year,
                        venue=ep.venue,
                    )
                    db.add(paper)
                    await db.flush()

                # Skip if already a seed for this study
                existing_seed = await db.execute(
                    select(SeedPaper).where(
                        SeedPaper.study_id == study_id,
                        SeedPaper.paper_id == paper.id,
                    )
                )
                if existing_seed.scalar_one_or_none() is None:
                    db.add(
                        SeedPaper(
                            study_id=study_id,
                            paper_id=paper.id,
                            added_by_agent="expert",
                        )
                    )
                    added += 1

            progress_detail = {
                "papers": [p.model_dump() for p in papers],
                "papers_added": added,
            }
            job.status = JobStatus.COMPLETED
            job.progress_pct = 100
            job.progress_detail = progress_detail
            job.completed_at = datetime.now(UTC)
            await db.commit()

            logger.info(
                "run_expert_seed_suggestion: completed",
                study_id=study_id,
                papers_added=added,
            )
            return {"job_id": job_id, "papers_added": added}

        except Exception as exc:
            logger.error("run_expert_seed_suggestion: failed", study_id=study_id, error=str(exc))
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            job.completed_at = datetime.now(UTC)
            await db.commit()
            return {"error": str(exc)}
