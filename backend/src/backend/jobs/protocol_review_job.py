"""ARQ background job for SLR protocol AI review (feature 007)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from backend.core.config import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    pass


async def run_protocol_review(
    ctx: dict[str, Any],
    *,
    study_id: int,
    protocol_id: int,
) -> dict[str, Any]:
    """Run the ProtocolReviewerAgent on a draft SLR protocol.

    Fetches the :class:`ReviewProtocol` record, calls
    :class:`ProtocolReviewerAgent`, stores the JSON review report in
    ``ReviewProtocol.review_report``, and sets ``status`` back to ``draft``
    so the researcher can iterate on the feedback.

    Args:
        ctx: ARQ worker context dict.
        study_id: The study the protocol belongs to.
        protocol_id: Primary key of the :class:`ReviewProtocol` to review.

    Returns:
        A dict with ``{status, study_id, protocol_id}``.

    """
    bound_log = logger.bind(study_id=study_id, protocol_id=protocol_id)

    from db.models.slr import ReviewProtocol, ReviewProtocolStatus
    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal

    async with _session_maker() as db:
        result = await db.execute(select(ReviewProtocol).where(ReviewProtocol.id == protocol_id))
        protocol = result.scalar_one_or_none()
        if protocol is None:
            bound_log.error("run_protocol_review: protocol not found")
            return {"status": "failed", "study_id": study_id, "protocol_id": protocol_id}

        protocol_data = _build_protocol_data(protocol)

        try:
            from agents.services.protocol_reviewer import ProtocolReviewerAgent

            agent = ProtocolReviewerAgent()
            review_result = await agent.review(protocol_data)

            protocol.review_report = review_result.model_dump()
            protocol.status = ReviewProtocolStatus.DRAFT
            await db.commit()
        except Exception as exc:  # noqa: BLE001
            bound_log.error(
                "run_protocol_review: agent call failed",
                exc=str(exc),
            )
            return {"status": "failed", "study_id": study_id, "protocol_id": protocol_id}

    bound_log.info(
        "run_protocol_review: finished",
        issue_count=len(review_result.issues),
    )
    return {"status": "completed", "study_id": study_id, "protocol_id": protocol_id}


def _build_protocol_data(protocol: Any) -> dict[str, Any]:
    """Assemble a protocol data dict suitable for :class:`ProtocolReviewerAgent`.

    Args:
        protocol: A :class:`ReviewProtocol` ORM instance.

    Returns:
        Dict with all protocol fields required by the agent's Jinja2 template.

    """
    synthesis = protocol.synthesis_approach
    synthesis_value: str | None = synthesis.value if synthesis is not None else None

    return {
        "background": protocol.background,
        "rationale": protocol.rationale,
        "research_questions": protocol.research_questions or [],
        "pico_population": protocol.pico_population,
        "pico_intervention": protocol.pico_intervention,
        "pico_comparison": protocol.pico_comparison,
        "pico_outcome": protocol.pico_outcome,
        "pico_context": protocol.pico_context,
        "search_strategy": protocol.search_strategy,
        "inclusion_criteria": protocol.inclusion_criteria or [],
        "exclusion_criteria": protocol.exclusion_criteria or [],
        "data_extraction_strategy": protocol.data_extraction_strategy,
        "synthesis_approach": synthesis_value,
        "dissemination_strategy": protocol.dissemination_strategy,
        "timetable": protocol.timetable,
    }
