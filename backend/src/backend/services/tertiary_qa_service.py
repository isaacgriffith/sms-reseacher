"""Tertiary Study quality assessment service (feature 009).

Provides a default secondary-study QA checklist pre-seeded with the six
mandatory dimensions for evaluating secondary literature (SLRs, SMSs,
Rapid Reviews).
"""

from __future__ import annotations

import structlog
from db.models.slr import ChecklistScoringMethod, QualityAssessmentChecklist, QualityChecklistItem
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Default checklist definition
# ---------------------------------------------------------------------------

_DEFAULT_CHECKLIST_NAME = "Secondary Study Quality Assessment"
_DEFAULT_CHECKLIST_DESCRIPTION = (
    "Six mandatory dimensions for appraising secondary literature "
    "(SLRs, SMSs, and Rapid Reviews) included in a Tertiary Study."
)

_DEFAULT_ITEMS: list[dict] = [
    {
        "order": 1,
        "question": (
            "Protocol documentation completeness: Is the study protocol (or "
            "research plan) explicitly documented and sufficiently detailed?"
        ),
        "scoring_method": ChecklistScoringMethod.SCALE_1_3,
        "weight": 1.0,
    },
    {
        "order": 2,
        "question": (
            "Search strategy adequacy: Is the search strategy clearly reported "
            "with sufficient detail to be reproduced (databases, keywords, date range)?"
        ),
        "scoring_method": ChecklistScoringMethod.SCALE_1_3,
        "weight": 1.0,
    },
    {
        "order": 3,
        "question": (
            "Inclusion/exclusion criteria clarity: Are the inclusion and exclusion "
            "criteria explicitly stated and unambiguous?"
        ),
        "scoring_method": ChecklistScoringMethod.SCALE_1_3,
        "weight": 1.0,
    },
    {
        "order": 4,
        "question": (
            "Quality assessment approach: Did the study apply a quality assessment "
            "to its primary studies using explicit, reported criteria?"
        ),
        "scoring_method": ChecklistScoringMethod.SCALE_1_3,
        "weight": 1.0,
    },
    {
        "order": 5,
        "question": (
            "Synthesis method appropriateness: Is the chosen synthesis method "
            "(meta-analysis, narrative, thematic, etc.) justified and appropriate "
            "for the data and research questions?"
        ),
        "scoring_method": ChecklistScoringMethod.SCALE_1_3,
        "weight": 1.0,
    },
    {
        "order": 6,
        "question": (
            "Validity threats discussion: Does the study identify and discuss "
            "threats to internal and external validity?"
        ),
        "scoring_method": ChecklistScoringMethod.SCALE_1_3,
        "weight": 1.0,
    },
]


# ---------------------------------------------------------------------------
# Service function
# ---------------------------------------------------------------------------


async def get_or_create_default_secondary_study_checklist(
    study_id: int,
    db: AsyncSession,
) -> QualityAssessmentChecklist:
    """Return the QA checklist for *study_id*, creating the default if absent.

    If no :class:`QualityAssessmentChecklist` exists for the study, one is
    auto-created with the six mandatory secondary-study QA dimensions.  If a
    checklist already exists (e.g. a custom one configured by the researcher),
    it is returned unchanged.

    This function flushes but does **not** commit; the caller is responsible
    for committing the session after calling this.

    Args:
        study_id: The Tertiary Study whose QA checklist to retrieve or create.
        db: Active async database session.

    Returns:
        The existing or newly-created :class:`QualityAssessmentChecklist` with
        all items eagerly loaded.

    """
    result = await db.execute(
        select(QualityAssessmentChecklist).where(QualityAssessmentChecklist.study_id == study_id)
    )
    checklist = result.scalar_one_or_none()

    if checklist is not None:
        await db.refresh(checklist, attribute_names=["items"])
        return checklist

    # Create the default checklist.
    checklist = QualityAssessmentChecklist(
        study_id=study_id,
        name=_DEFAULT_CHECKLIST_NAME,
        description=_DEFAULT_CHECKLIST_DESCRIPTION,
    )
    db.add(checklist)
    await db.flush()

    for item_data in _DEFAULT_ITEMS:
        item = QualityChecklistItem(
            checklist_id=checklist.id,
            order=item_data["order"],
            question=item_data["question"],
            scoring_method=item_data["scoring_method"],
            weight=item_data["weight"],
        )
        db.add(item)

    await db.flush()
    await db.refresh(checklist, attribute_names=["items"])

    logger.info(
        "tertiary_qa_service: default checklist created",
        study_id=study_id,
        checklist_id=checklist.id,
        n_items=len(_DEFAULT_ITEMS),
    )
    return checklist
