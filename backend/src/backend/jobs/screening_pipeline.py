"""The screening pipeline shared by every job that judges candidate papers.

These helpers were extracted from ``search_job.py`` (plan.md C2), which had
grown to 941 lines — over the 800-line maximum — while holding the only copy of
logic a second consumer now needs. The re-screen job composes exactly this
pipeline: load the study's criteria, build a screener carrying the study
context, turn a search result into a candidate, judge it, and record the
judgement.

Extracting rather than copying is what keeps DRY: the alternative was a
re-screen job with its own near-identical screening pass, and two places for
the next defect in it to be fixed only once.

The seam is deliberate. Nothing here knows about searches, snowballing, or
databases queried — those stay in ``search_job.py``, which imports from this
module. Anything that reaches for a ``SearchExecution`` belongs there, not
here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from backend.core.config import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class ScreeningUnavailableError(RuntimeError):
    """Raised when the screener could not judge a paper.

    A provider fault is not a rejection. FR-024 requires a run to distinguish
    the papers it assessed from the papers it never reached, and that
    distinction cannot exist while a timeout is persisted as a legitimate
    reject.

    Mirrors :class:`~backend.jobs.search_job.TestSearchUnavailableError`, which
    draws the same line for a search that failed versus a search that matched
    nothing.
    """


# ---------------------------------------------------------------------------
# Criteria
# ---------------------------------------------------------------------------


async def _load_criteria(db: AsyncSession, study_id: int) -> tuple[list[dict], list[dict]]:
    """Load inclusion and exclusion criteria for a study.

    Args:
        db: Active async database session.
        study_id: The study whose criteria are being screened against.

    Returns:
        An ``(inclusion, exclusion)`` pair of ``{id, description}`` dicts, each
        in the reviewer-authored ``order_index`` order.

    """
    from db.models.criteria import ExclusionCriterion, InclusionCriterion
    from sqlalchemy import select

    inc = await db.execute(
        select(InclusionCriterion)
        .where(InclusionCriterion.study_id == study_id)
        .order_by(InclusionCriterion.order_index)
    )
    exc = await db.execute(
        select(ExclusionCriterion)
        .where(ExclusionCriterion.study_id == study_id)
        .order_by(ExclusionCriterion.order_index)
    )
    inclusion = [{"id": c.id, "description": c.description} for c in inc.scalars().all()]
    exclusion = [{"id": c.id, "description": c.description} for c in exc.scalars().all()]
    return inclusion, exclusion


# ---------------------------------------------------------------------------
# Candidate creation
# ---------------------------------------------------------------------------


async def _upsert_paper(db: AsyncSession, paper_data: dict) -> Any:
    """Upsert a Paper record by DOI, or create new if DOI is absent."""
    from db.models import Paper
    from sqlalchemy import select

    doi = paper_data.get("doi")
    if doi:
        existing = await db.execute(select(Paper).where(Paper.doi == doi))
        paper = existing.scalar_one_or_none()
        if paper:
            return paper
    paper = Paper(
        title=paper_data.get("title", "Untitled"),
        abstract=paper_data.get("abstract"),
        doi=doi,
        authors=paper_data.get("authors", []),
        year=paper_data.get("year"),
        venue=paper_data.get("venue"),
        source_url=paper_data.get("source_url"),
    )
    db.add(paper)
    await db.flush()
    return paper


async def _process_single_candidate(
    db: AsyncSession,
    paper_data: dict,
    study_id: int,
    search_execution_id: int,
    phase_tag: str,
) -> tuple[Any, bool]:
    """Create a CandidatePaper for paper_data. Returns (cp_or_None, is_duplicate).

    A paper the study has already recorded returns ``(None, True)``. The True is
    load-bearing: it is what makes the caller count a duplicate and move on,
    rather than fall through and hand ``None`` to the screening pass.
    """
    from db.models.candidate import CandidatePaper, CandidatePaperStatus
    from sqlalchemy import select

    from backend.services.dedup import check_duplicate

    paper = await _upsert_paper(db, paper_data)
    dedup = await check_duplicate(
        study_id=study_id,
        doi=paper_data.get("doi"),
        title=paper_data.get("title", "Untitled"),
        authors=paper_data.get("authors"),
        db=db,
    )
    existing_cp = (
        await db.execute(
            select(CandidatePaper).where(
                CandidatePaper.study_id == study_id,
                CandidatePaper.paper_id == paper.id,
            )
        )
    ).scalar_one_or_none()
    if existing_cp is not None:
        return None, True
    status = CandidatePaperStatus.DUPLICATE if dedup.is_duplicate else CandidatePaperStatus.PENDING
    kwargs = {"duplicate_of_id": dedup.candidate_id} if dedup.is_duplicate else {}
    # Assign the relationship, not the FK: the screening pass reads
    # `candidate.title` / `.abstract`, which delegate to the composed paper.
    # Setting `paper_id` alone would leave that unloaded, and a lazy load on a
    # freshly flushed row raises MissingGreenlet under an async session.
    cp = CandidatePaper(
        study_id=study_id,
        paper=paper,
        search_execution_id=search_execution_id,
        phase_tag=phase_tag,
        current_status=status,
        **kwargs,
    )
    db.add(cp)
    await db.flush()
    return cp, dedup.is_duplicate


# ---------------------------------------------------------------------------
# Screening
# ---------------------------------------------------------------------------


async def _build_screener_with_context(db: Any, ai_reviewer: Any, study_id: int) -> Any:
    """Build a ScreenerAgent with study-context rendering if an Agent record is linked.

    Resolves the Agent record from the reviewer's ``agent_id``, loads the
    Provider, renders the system message with the study context, and builds
    a :class:`ScreenerAgent` with ``provider_config`` and
    ``system_message_override`` set.  Falls back to a plain
    :class:`ScreenerAgent` when no Agent is linked.

    Args:
        db: Active async database session.
        ai_reviewer: The :class:`Reviewer` ORM record for the AI screener.
        study_id: The study being screened (used to load study context).

    Returns:
        A configured :class:`ScreenerAgent` instance.

    """
    from agents.services.screener import ScreenerAgent
    from db.models import Agent, AvailableModel, Provider, Study
    from sqlalchemy import select

    from backend.services.agent_service import (  # noqa: PLC0415
        _build_provider_config,
        build_study_context,
        render_system_message,
    )

    if not ai_reviewer.agent_id:
        return ScreenerAgent()

    agent_result = await db.execute(select(Agent).where(Agent.id == ai_reviewer.agent_id))
    agent = agent_result.scalar_one_or_none()
    if agent is None or not agent.is_active:
        return ScreenerAgent()

    provider_result = await db.execute(select(Provider).where(Provider.id == agent.provider_id))
    provider = provider_result.scalar_one_or_none()
    model_result = await db.execute(
        select(AvailableModel).where(AvailableModel.id == agent.model_id)
    )
    model = model_result.scalar_one_or_none()
    provider_config = _build_provider_config(provider, model)

    study_result = await db.execute(select(Study).where(Study.id == study_id))
    study = study_result.scalar_one_or_none()
    if study is not None:
        ctx = build_study_context(study)
        rendered = render_system_message(
            agent.system_message_template, agent, ctx.domain, ctx.study_type
        )
    else:
        rendered = None

    return ScreenerAgent(
        provider_config=provider_config,
        system_message_override=rendered,
    )


async def _run_screening_pass(
    screener: Any,
    paper: Any,
    inclusion_criteria: list[dict],
    exclusion_criteria: list[dict],
) -> tuple[str, list]:
    """Screen a paper with the ScreenerAgent.

    Args:
        screener: The :class:`ScreenerAgent` to judge with.
        paper: Anything carrying ``title`` and ``abstract`` — a
            :class:`Paper`, or a :class:`CandidatePaper`, which delegates both
            to the paper it composes.
        inclusion_criteria: Inclusion criteria as ``{id, description}`` dicts.
        exclusion_criteria: Exclusion criteria as ``{id, description}`` dicts.

    Returns:
        A ``(decision, reasons)`` pair.

    Raises:
        ScreeningUnavailableError: If the screener could not reach a verdict.
            Deliberately not caught here: this used to return
            ``("rejected", [])``, which wrote provider faults to the database
            as judgements.

    """
    from agents.services.screener import ScreeningResult

    # Read the bibliography before the guarded call. A candidate that cannot
    # produce a title is a programming error, and wrapping it as an outage
    # would file the bug under a cause nobody investigates.
    title = paper.title
    abstract = paper.abstract or ""

    try:
        result = await screener.run(
            inclusion_criteria=inclusion_criteria,
            exclusion_criteria=exclusion_criteria,
            abstract=abstract,
            title=title,
        )
    except Exception as exc:
        logger.warning("_run_screening_pass: screener unavailable", title=title, exc=str(exc))
        raise ScreeningUnavailableError(f"screener could not judge {title!r}") from exc

    if isinstance(result, ScreeningResult):
        return result.decision, [r.model_dump() for r in result.reasons]
    lower = str(result).lower()
    return "accepted" if "accept" in lower else "rejected", []


# ---------------------------------------------------------------------------
# Recording the judgement
# ---------------------------------------------------------------------------


async def _record_paper_decision(
    db: AsyncSession, cp: Any, reviewer_id: int, decision: str, reasons: list
) -> None:
    """Create PaperDecision and update CandidatePaper status."""
    from db.models.candidate import CandidatePaperStatus, PaperDecision, PaperDecisionType

    cp.current_status = CandidatePaperStatus(decision)
    pd = PaperDecision(
        candidate_paper_id=cp.id,
        reviewer_id=reviewer_id,
        decision=PaperDecisionType(decision),
        reasons=reasons,
        is_override=False,
    )
    db.add(pd)
