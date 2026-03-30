"""ARQ background job for AI-assisted tertiary data extraction (feature 009).

Processes all ``pending`` :class:`TertiaryDataExtraction` records for a
Tertiary Study, calls an LLM to suggest values for the nine secondary-study
extraction fields, and sets ``extraction_status`` to ``ai_complete``.
"""

from __future__ import annotations

import json
from typing import Any

import structlog

from backend.core.config import get_logger

logger = get_logger(__name__)
_structlog = structlog.get_logger(__name__)

# System prompt for the LLM used to suggest secondary-study extraction fields.
_EXTRACTION_SYSTEM_PROMPT = (
    "You are a systematic review expert. Given the title and abstract of a secondary "
    "study (SLR, SMS, or Rapid Review), extract structured metadata and return a JSON "
    "object with these exact keys: "
    '"secondary_study_type" (one of SLR|SMS|RAPID_REVIEW|UNKNOWN), '
    '"research_questions_addressed" (list of strings), '
    '"databases_searched" (list of strings), '
    '"study_period_start" (int year or null), '
    '"study_period_end" (int year or null), '
    '"primary_study_count" (int or null), '
    '"synthesis_approach_used" (short string or null), '
    '"key_findings" (paragraph or null), '
    '"research_gaps" (paragraph or null). '
    "Return only valid JSON — no prose, no markdown fences."
)


async def run_tertiary_extraction(
    ctx: dict[str, Any],
    *,
    study_id: int,
) -> dict[str, Any]:
    """AI-pre-fill pending TertiaryDataExtraction records for *study_id*.

    For each ``pending`` extraction record linked to the study:
    1. Load the associated paper title and abstract.
    2. Call the configured LLM to suggest the nine extraction fields.
    3. Update the record with suggested values and set status to ``ai_complete``.

    Args:
        ctx: ARQ worker context dict.
        study_id: The Tertiary Study to process.

    Returns:
        A dict with ``{"status": "completed", "study_id": ..., "papers_processed": N}``.

    """
    bound = _structlog.bind(study_id=study_id)

    from db.models import Paper
    from db.models.candidate import CandidatePaper
    from db.models.tertiary import TertiaryDataExtraction
    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal

    async with _session_maker() as db:
        # Load pending extractions for this study.
        pending_result = await db.execute(
            select(TertiaryDataExtraction)
            .join(CandidatePaper, TertiaryDataExtraction.candidate_paper_id == CandidatePaper.id)
            .where(
                CandidatePaper.study_id == study_id,
                TertiaryDataExtraction.extraction_status == "pending",
            )
        )
        pending = list(pending_result.scalars().all())

        if not pending:
            bound.info("run_tertiary_extraction: no pending records")
            return {"status": "completed", "study_id": study_id, "papers_processed": 0}

        papers_processed = 0
        for extraction in pending:
            # Fetch paper title + abstract.
            paper_result = await db.execute(
                select(Paper)
                .join(CandidatePaper, CandidatePaper.paper_id == Paper.id)
                .where(CandidatePaper.id == extraction.candidate_paper_id)
            )
            paper = paper_result.scalar_one_or_none()
            if paper is None:
                bound.warning(
                    "run_tertiary_extraction: paper not found",
                    candidate_paper_id=extraction.candidate_paper_id,
                )
                continue

            try:
                suggestions = await _suggest_extraction_fields(paper.title, paper.abstract or "")
                _apply_suggestions(extraction, suggestions)
                papers_processed += 1
            except Exception as exc:  # noqa: BLE001
                bound.warning(
                    "run_tertiary_extraction: LLM call failed",
                    candidate_paper_id=extraction.candidate_paper_id,
                    exc=str(exc),
                )

        await db.commit()

    bound.info(
        "run_tertiary_extraction: completed",
        papers_processed=papers_processed,
        total_pending=len(pending),
    )
    return {"status": "completed", "study_id": study_id, "papers_processed": papers_processed}


async def _suggest_extraction_fields(title: str, abstract: str) -> dict[str, Any]:
    """Call the LLM to suggest secondary-study extraction fields.

    Args:
        title: The paper's title.
        abstract: The paper's abstract (may be empty).

    Returns:
        Dict of suggested field values (may have ``None`` for unknown fields).

    Raises:
        ValueError: If the LLM response cannot be parsed as JSON.

    """
    from agents.core.llm_client import LLMClient

    client = LLMClient()
    user_content = f"Title: {title}\n\nAbstract: {abstract}"
    messages = [
        {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
    raw_text: str = await client.complete(messages)

    # Strip optional markdown fences.
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    return json.loads(raw_text)  # type: ignore[no-any-return]


def _apply_suggestions(extraction: Any, suggestions: dict[str, Any]) -> None:
    """Write LLM-suggested values onto an extraction record.

    Sets ``extraction_status`` to ``ai_complete`` and records the agent name.
    Only known fields are applied; unknown keys are silently ignored.

    Args:
        extraction: The :class:`TertiaryDataExtraction` ORM instance.
        suggestions: Dict of suggested field values from the LLM.

    """
    _ALLOWED_FIELDS = {
        "secondary_study_type",
        "research_questions_addressed",
        "databases_searched",
        "study_period_start",
        "study_period_end",
        "primary_study_count",
        "synthesis_approach_used",
        "key_findings",
        "research_gaps",
    }
    for field, value in suggestions.items():
        if field in _ALLOWED_FIELDS and value is not None:
            setattr(extraction, field, value)

    extraction.extraction_status = "ai_complete"
    extraction.extracted_by_agent = "TertiaryExtractionAgent"
