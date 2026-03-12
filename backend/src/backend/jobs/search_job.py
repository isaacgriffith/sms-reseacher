"""ARQ background jobs for test-search execution."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def run_test_search(
    ctx: dict[str, Any],
    study_id: int,
    search_string_id: int,
    databases: list[str],
) -> dict[str, Any]:
    """Run a test search and compute recall against the seed paper test set.

    Calls researcher-mcp ``search_papers`` with the search string against the
    requested databases, counts how many seed papers are in the result set,
    computes recall, and creates a :class:`SearchStringIteration` record.

    Args:
        ctx: ARQ context dict (contains Redis connection etc.).
        study_id: The study whose seeds are used as the test set.
        search_string_id: The search string to evaluate.
        databases: Database identifiers to query (e.g. ``["acm", "ieee"]``).

    Returns:
        A dict with ``{iteration_id, result_set_count, test_set_recall}``.
    """
    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal
    from db.models.search import SearchString, SearchStringIteration
    from db.models.seeds import SeedPaper

    async with _session_maker() as db:
        # Load the search string
        ss_result = await db.execute(
            select(SearchString).where(SearchString.id == search_string_id)
        )
        ss = ss_result.scalar_one_or_none()
        if ss is None:
            logger.error("run_test_search: search_string %d not found", search_string_id)
            return {"error": "search_string not found"}

        # Load seed paper DOIs for recall computation
        seeds_result = await db.execute(
            select(SeedPaper).where(SeedPaper.study_id == study_id)
        )
        seed_papers = seeds_result.scalars().all()

        # Attempt to call researcher-mcp; fall back gracefully if unavailable
        result_dois: set[str] = set()
        result_count = 0
        try:
            import httpx

            from backend.core.config import get_settings

            settings = get_settings()
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{settings.researcher_mcp_url.rstrip('/sse').rstrip('/')}/tools/search_papers",
                    json={
                        "query": ss.string_text,
                        "databases": databases or ["acm", "ieee", "scopus"],
                        "max_results": 100,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    papers = data.get("papers", [])
                    result_count = len(papers)
                    result_dois = {
                        p.get("doi", "").lower().strip()
                        for p in papers
                        if p.get("doi")
                    }
        except Exception as exc:
            logger.warning("run_test_search: researcher-mcp unavailable: %s", exc)
            # Continue with 0 results — iteration is still recorded

        # Compute recall: fraction of seed papers found in results
        from db.models import Paper

        seed_dois: set[str] = set()
        for sp in seed_papers:
            paper_result = await db.execute(select(Paper).where(Paper.id == sp.paper_id))
            paper = paper_result.scalar_one_or_none()
            if paper and paper.doi:
                seed_dois.add(paper.doi.lower().strip())

        if seed_dois:
            matched = len(seed_dois & result_dois)
            recall = matched / len(seed_dois)
        else:
            recall = 0.0

        # Determine next iteration number
        existing_iters = await db.execute(
            select(SearchStringIteration)
            .where(SearchStringIteration.search_string_id == search_string_id)
            .order_by(SearchStringIteration.iteration_number.desc())
        )
        latest_iter = existing_iters.scalars().first()
        next_iter_num = (latest_iter.iteration_number + 1) if latest_iter else 1

        iteration = SearchStringIteration(
            search_string_id=search_string_id,
            iteration_number=next_iter_num,
            result_set_count=result_count,
            test_set_recall=recall,
        )
        db.add(iteration)
        await db.commit()

        logger.info(
            "run_test_search: completed",
            study_id=study_id,
            search_string_id=search_string_id,
            result_count=result_count,
            recall=recall,
            iteration_id=iteration.id,
        )
        return {
            "iteration_id": iteration.id,
            "result_set_count": result_count,
            "test_set_recall": recall,
        }


async def run_full_search(
    ctx: dict,
    study_id: int,
    search_execution_id: int,
) -> dict:
    """Execute the full search pipeline for a study.

    Steps:
    1. Query each database via researcher-mcp ``search_papers``.
    2. Deduplicate each result against existing CandidatePapers.
    3. Create CandidatePaper records.
    4. Call ScreenerAgent for each candidate.
    5. Create PaperDecision records.
    6. Update SearchMetrics.
    7. Write progress to BackgroundJob.

    Args:
        ctx: ARQ context.
        study_id: The study being searched.
        search_execution_id: The SearchExecution to run.

    Returns:
        Summary dict with candidate counts.
    """
    from datetime import datetime, timezone

    from sqlalchemy import select

    from backend.core.config import get_settings
    from backend.core.database import _session_maker  # noqa: PLC2701
    from backend.services.dedup import check_duplicate
    from db.models import Paper, Study
    from db.models.candidate import CandidatePaper, CandidatePaperStatus, PaperDecision, PaperDecisionType
    from db.models.criteria import ExclusionCriterion, InclusionCriterion
    from db.models.jobs import BackgroundJob, JobStatus
    from db.models.search import SearchString
    from db.models.search_exec import SearchExecution, SearchExecutionStatus, SearchMetrics
    from db.models.study import Reviewer

    async with _session_maker() as db:
        # Load search execution
        exec_result = await db.execute(
            select(SearchExecution).where(SearchExecution.id == search_execution_id)
        )
        search_exec = exec_result.scalar_one_or_none()
        if search_exec is None:
            logger.error("run_full_search: SearchExecution %d not found", search_execution_id)
            return {"error": "search_execution not found"}

        # Mark running
        search_exec.status = SearchExecutionStatus.RUNNING
        search_exec.started_at = datetime.now(timezone.utc)

        # Update BackgroundJob to running
        job_result = await db.execute(
            select(BackgroundJob).where(
                BackgroundJob.study_id == study_id,
                BackgroundJob.status == JobStatus.QUEUED,
            )
        )
        bg_job = job_result.scalars().first()
        if bg_job:
            bg_job.status = JobStatus.RUNNING
            bg_job.started_at = datetime.now(timezone.utc)
        await db.commit()

        # Load search string
        ss_result = await db.execute(
            select(SearchString).where(SearchString.id == search_exec.search_string_id)
        )
        ss = ss_result.scalar_one_or_none()
        if ss is None:
            logger.error("run_full_search: SearchString not found")
            return {"error": "search_string not found"}

        # Load criteria
        inc_result = await db.execute(
            select(InclusionCriterion)
            .where(InclusionCriterion.study_id == study_id)
            .order_by(InclusionCriterion.order_index)
        )
        exc_result = await db.execute(
            select(ExclusionCriterion)
            .where(ExclusionCriterion.study_id == study_id)
            .order_by(ExclusionCriterion.order_index)
        )
        inclusion_criteria = [
            {"id": c.id, "description": c.description}
            for c in inc_result.scalars().all()
        ]
        exclusion_criteria = [
            {"id": c.id, "description": c.description}
            for c in exc_result.scalars().all()
        ]

        # Load or create an AI reviewer for this study
        reviewer_result = await db.execute(
            select(Reviewer).where(
                Reviewer.study_id == study_id,
                Reviewer.reviewer_type == "ai_agent",
            )
        )
        ai_reviewer = reviewer_result.scalars().first()
        if ai_reviewer is None:
            ai_reviewer = Reviewer(
                study_id=study_id,
                reviewer_type="ai_agent",
                agent_name="screener",
            )
            db.add(ai_reviewer)
            await db.flush()

        settings = get_settings()
        databases = search_exec.databases_queried or ["acm", "ieee", "scopus"]
        phase_tag = search_exec.phase_tag

        total_identified = 0
        accepted_count = 0
        rejected_count = 0
        duplicate_count = 0

        # Initialize metrics record
        metrics_result = await db.execute(
            select(SearchMetrics).where(
                SearchMetrics.search_execution_id == search_execution_id
            )
        )
        metrics = metrics_result.scalar_one_or_none()
        if metrics is None:
            metrics = SearchMetrics(search_execution_id=search_execution_id)
            db.add(metrics)
            await db.flush()

        from agents.services.screener import ScreenerAgent

        screener = ScreenerAgent()

        for db_name in databases:
            # Update progress
            if bg_job:
                pct = int(
                    (databases.index(db_name) / len(databases)) * 80
                )
                bg_job.progress_pct = pct
                bg_job.progress_detail = {
                    "phase": "searching",
                    "current_database": db_name,
                    "papers_found": total_identified,
                }
                await db.commit()

            # Query researcher-mcp
            papers_from_db: list[dict] = []
            try:
                import httpx

                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(
                        f"{settings.researcher_mcp_url.rstrip('/sse').rstrip('/')}/tools/search_papers",
                        json={
                            "query": ss.string_text,
                            "databases": [db_name],
                            "max_results": 200,
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        papers_from_db = data.get("results", data.get("papers", []))
            except Exception as exc:
                logger.warning("run_full_search: researcher-mcp error for %s: %s", db_name, exc)
                continue

            for paper_data in papers_from_db:
                total_identified += 1

                # Upsert Paper record
                paper_doi = paper_data.get("doi")
                paper_title = paper_data.get("title", "Untitled")

                if paper_doi:
                    existing_paper = await db.execute(
                        select(Paper).where(Paper.doi == paper_doi)
                    )
                    paper = existing_paper.scalar_one_or_none()
                else:
                    paper = None

                if paper is None:
                    paper = Paper(
                        title=paper_title,
                        abstract=paper_data.get("abstract"),
                        doi=paper_doi,
                        authors=paper_data.get("authors", []),
                        year=paper_data.get("year"),
                        venue=paper_data.get("venue"),
                        source_url=paper_data.get("source_url"),
                    )
                    db.add(paper)
                    await db.flush()

                # Deduplication check
                dedup = await check_duplicate(
                    study_id=study_id,
                    doi=paper_doi,
                    title=paper_title,
                    authors=paper_data.get("authors"),
                    db=db,
                )

                if dedup.is_duplicate:
                    duplicate_count += 1
                    # Still record as duplicate candidate if no existing candidate
                    existing_cp = await db.execute(
                        select(CandidatePaper).where(
                            CandidatePaper.study_id == study_id,
                            CandidatePaper.paper_id == paper.id,
                        )
                    )
                    if existing_cp.scalar_one_or_none() is not None:
                        continue
                    cp = CandidatePaper(
                        study_id=study_id,
                        paper_id=paper.id,
                        search_execution_id=search_execution_id,
                        phase_tag=phase_tag,
                        current_status=CandidatePaperStatus.DUPLICATE,
                        duplicate_of_id=dedup.candidate_id,
                    )
                    db.add(cp)
                    await db.flush()
                    continue

                # Check for existing candidate (idempotent)
                existing_cp_result = await db.execute(
                    select(CandidatePaper).where(
                        CandidatePaper.study_id == study_id,
                        CandidatePaper.paper_id == paper.id,
                    )
                )
                if existing_cp_result.scalar_one_or_none() is not None:
                    duplicate_count += 1
                    continue

                # Create CandidatePaper
                cp = CandidatePaper(
                    study_id=study_id,
                    paper_id=paper.id,
                    search_execution_id=search_execution_id,
                    phase_tag=phase_tag,
                    current_status=CandidatePaperStatus.PENDING,
                )
                db.add(cp)
                await db.flush()

                # AI screening
                try:
                    screening = await screener.run(
                        inclusion_criteria=inclusion_criteria,
                        exclusion_criteria=exclusion_criteria,
                        abstract=paper.abstract or "",
                        title=paper.title,
                    )

                    from agents.services.screener import ScreeningResult

                    if isinstance(screening, ScreeningResult):
                        decision_str = screening.decision
                        reasons = [r.model_dump() for r in screening.reasons]
                    else:
                        lower = str(screening).lower()
                        decision_str = "accepted" if "accept" in lower else "rejected"
                        reasons = []

                    decision_enum = PaperDecisionType(decision_str)
                    cp.current_status = CandidatePaperStatus(decision_str)

                    pd = PaperDecision(
                        candidate_paper_id=cp.id,
                        reviewer_id=ai_reviewer.id,
                        decision=decision_enum,
                        reasons=reasons,
                        is_override=False,
                    )
                    db.add(pd)

                    if decision_str == "accepted":
                        accepted_count += 1
                    else:
                        rejected_count += 1

                except Exception as exc:
                    logger.warning("run_full_search: screening error: %s", exc)
                    rejected_count += 1

                await db.flush()

        # Update metrics
        metrics.total_identified = total_identified
        metrics.accepted = accepted_count
        metrics.rejected = rejected_count
        metrics.duplicates = duplicate_count
        metrics.computed_at = datetime.now(timezone.utc)

        # Mark search execution complete
        search_exec.status = SearchExecutionStatus.COMPLETED
        search_exec.completed_at = datetime.now(timezone.utc)

        if bg_job:
            bg_job.status = JobStatus.COMPLETED
            bg_job.progress_pct = 100
            bg_job.completed_at = datetime.now(timezone.utc)
            bg_job.progress_detail = {
                "phase": "complete",
                "total_identified": total_identified,
                "accepted": accepted_count,
                "rejected": rejected_count,
                "duplicates": duplicate_count,
            }

        await db.commit()

        logger.info(
            "run_full_search: completed study_id=%d total=%d accepted=%d",
            study_id,
            total_identified,
            accepted_count,
        )
        return {
            "search_execution_id": search_execution_id,
            "total_identified": total_identified,
            "accepted": accepted_count,
            "rejected": rejected_count,
            "duplicates": duplicate_count,
        }


async def run_snowball(
    ctx: dict,
    study_id: int,
    phase_tag: str,
    paper_dois: list[str],
    direction: str,
    search_execution_id: int,
) -> dict:
    """Execute iterative snowball sampling from a set of papers.

    Calls ``get_references`` (backward) or ``get_citations`` (forward) via
    the researcher-mcp, deduplicates, screens new papers, updates
    SearchMetrics, and stops if new non-duplicate count < snowball_threshold.

    Args:
        ctx: ARQ context.
        study_id: The study to snowball for.
        phase_tag: Phase label (e.g. ``"backward-search-1"``).
        paper_dois: List of DOIs of seed papers for snowball.
        direction: ``"backward"`` (references) or ``"forward"`` (citations).
        search_execution_id: The SearchExecution to record results against.

    Returns:
        Summary dict with counts.
    """
    from datetime import datetime, timezone

    from sqlalchemy import select

    from backend.core.config import get_settings
    from backend.core.database import _session_maker  # noqa: PLC2701
    from backend.services.dedup import check_duplicate
    from db.models import Paper, Study
    from db.models.candidate import CandidatePaper, CandidatePaperStatus, PaperDecision, PaperDecisionType
    from db.models.criteria import ExclusionCriterion, InclusionCriterion
    from db.models.jobs import BackgroundJob, JobStatus
    from db.models.search_exec import SearchExecution, SearchExecutionStatus, SearchMetrics
    from db.models.study import Reviewer

    async with _session_maker() as db:
        # Load study for snowball_threshold
        study_result = await db.execute(select(Study).where(Study.id == study_id))
        study = study_result.scalar_one_or_none()
        if study is None:
            return {"error": "study not found"}

        snowball_threshold = study.snowball_threshold or 5

        # Load or create AI reviewer
        reviewer_result = await db.execute(
            select(Reviewer).where(
                Reviewer.study_id == study_id,
                Reviewer.reviewer_type == "ai_agent",
            )
        )
        ai_reviewer = reviewer_result.scalars().first()
        if ai_reviewer is None:
            ai_reviewer = Reviewer(
                study_id=study_id,
                reviewer_type="ai_agent",
                agent_name="screener",
            )
            db.add(ai_reviewer)
            await db.flush()

        # Load criteria
        inc_result = await db.execute(
            select(InclusionCriterion)
            .where(InclusionCriterion.study_id == study_id)
            .order_by(InclusionCriterion.order_index)
        )
        exc_result = await db.execute(
            select(ExclusionCriterion)
            .where(ExclusionCriterion.study_id == study_id)
            .order_by(ExclusionCriterion.order_index)
        )
        inclusion_criteria = [
            {"id": c.id, "description": c.description}
            for c in inc_result.scalars().all()
        ]
        exclusion_criteria = [
            {"id": c.id, "description": c.description}
            for c in exc_result.scalars().all()
        ]

        settings = get_settings()
        tool = "get_references" if direction == "backward" else "get_citations"

        new_non_duplicate_count = 0
        accepted_count = 0
        rejected_count = 0
        duplicate_count = 0

        from agents.services.screener import ScreenerAgent, ScreeningResult

        screener = ScreenerAgent()

        for doi in paper_dois:
            try:
                import httpx

                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(
                        f"{settings.researcher_mcp_url.rstrip('/sse').rstrip('/')}/tools/{tool}",
                        json={"doi": doi, "max_results": 50},
                    )
                    if resp.status_code != 200:
                        continue
                    data = resp.json()
                    papers_list = data.get("references" if direction == "backward" else "citations", [])

            except Exception as exc:
                logger.warning("run_snowball: mcp error for doi %s: %s", doi, exc)
                continue

            for paper_data in papers_list:
                paper_doi = paper_data.get("doi")
                paper_title = paper_data.get("title", "Untitled")

                if paper_doi:
                    existing_paper_result = await db.execute(
                        select(Paper).where(Paper.doi == paper_doi)
                    )
                    paper = existing_paper_result.scalar_one_or_none()
                else:
                    paper = None

                if paper is None:
                    paper = Paper(
                        title=paper_title,
                        doi=paper_doi,
                        authors=paper_data.get("authors", []),
                        year=paper_data.get("year"),
                        venue=paper_data.get("venue"),
                        source_url=paper_data.get("source_url"),
                    )
                    db.add(paper)
                    await db.flush()

                dedup = await check_duplicate(
                    study_id=study_id,
                    doi=paper_doi,
                    title=paper_title,
                    authors=paper_data.get("authors"),
                    db=db,
                )

                if dedup.is_duplicate:
                    duplicate_count += 1
                    continue

                existing_cp_result = await db.execute(
                    select(CandidatePaper).where(
                        CandidatePaper.study_id == study_id,
                        CandidatePaper.paper_id == paper.id,
                    )
                )
                if existing_cp_result.scalar_one_or_none() is not None:
                    duplicate_count += 1
                    continue

                new_non_duplicate_count += 1
                cp = CandidatePaper(
                    study_id=study_id,
                    paper_id=paper.id,
                    search_execution_id=search_execution_id,
                    phase_tag=phase_tag,
                    current_status=CandidatePaperStatus.PENDING,
                )
                db.add(cp)
                await db.flush()

                try:
                    screening = await screener.run(
                        inclusion_criteria=inclusion_criteria,
                        exclusion_criteria=exclusion_criteria,
                        abstract="",
                        title=paper.title,
                    )
                    if isinstance(screening, ScreeningResult):
                        decision_str = screening.decision
                        reasons = [r.model_dump() for r in screening.reasons]
                    else:
                        lower = str(screening).lower()
                        decision_str = "accepted" if "accept" in lower else "rejected"
                        reasons = []

                    cp.current_status = CandidatePaperStatus(decision_str)
                    pd = PaperDecision(
                        candidate_paper_id=cp.id,
                        reviewer_id=ai_reviewer.id,
                        decision=PaperDecisionType(decision_str),
                        reasons=reasons,
                    )
                    db.add(pd)
                    if decision_str == "accepted":
                        accepted_count += 1
                    else:
                        rejected_count += 1
                except Exception as exc:
                    logger.warning("run_snowball: screening error: %s", exc)
                    rejected_count += 1

                await db.flush()

        # Update metrics
        metrics_result = await db.execute(
            select(SearchMetrics).where(
                SearchMetrics.search_execution_id == search_execution_id
            )
        )
        metrics = metrics_result.scalar_one_or_none()
        if metrics is None:
            metrics = SearchMetrics(search_execution_id=search_execution_id)
            db.add(metrics)
            await db.flush()

        metrics.total_identified += new_non_duplicate_count + duplicate_count
        metrics.accepted += accepted_count
        metrics.rejected += rejected_count
        metrics.duplicates += duplicate_count
        metrics.computed_at = datetime.now(timezone.utc)

        await db.commit()

        stopped_early = new_non_duplicate_count < snowball_threshold
        logger.info(
            "run_snowball: study=%d direction=%s new=%d accepted=%d stopped_early=%s",
            study_id,
            direction,
            new_non_duplicate_count,
            accepted_count,
            stopped_early,
        )
        return {
            "study_id": study_id,
            "direction": direction,
            "new_non_duplicate_count": new_non_duplicate_count,
            "accepted": accepted_count,
            "rejected": rejected_count,
            "duplicates": duplicate_count,
            "stopped_early": stopped_early,
        }
