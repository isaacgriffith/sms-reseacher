"""The DARE quality instrument for tertiary studies (TFIX7 part 3).

``07-quality-assessment.md`` assigns DARE to tertiary studies, "because their
primary studies are secondary studies", and ``04-tertiary.md`` 2.3 supplies the
full anchors.  Four questions, scored **Y = 1, P = 0.5, N = 0**, total out of 4.

Why this module exists rather than a single quality float
---------------------------------------------------------
``TertiaryDataExtraction.reviewer_quality_rating`` is one ``float`` covering all
of methodological quality.  ``07-quality-assessment.md`` rejects that shape
directly — "where you score both, keep them as **separate metrics** … combining
them into a single number is bad practice" — and a single number also cannot
carry the per-answer justification the tertiary protocol makes mandatory.  That
column is **deprecated**; see :mod:`backend.services.tertiary_report_service`.

Storage reuses the existing study-scoped checklist machinery
(``QualityAssessmentChecklist`` -> ``QualityChecklistItem`` ->
``QualityAssessmentScore``) rather than introducing a parallel one.  DARE *is* a
four-item anchored checklist, the tables already model exactly that, and the
reuse means DARE inherits per-item notes and the Cohen's kappa pipeline for
free — which matters here, because ``07-quality-assessment.md`` records that
agreement on quality scoring is poor even among experts (0.54 on the average
quality score), so measuring it is part of using the instrument honestly.

Anchor provenance
-----------------
Q1-Q4 and their anchors are quoted from ``04-tertiary.md`` 2.3.  The optional
fifth question is CRD's criterion 3, which the SE community dropped and which
``10-reporting-and-evaluation.md`` says is "worth restoring as an optional fifth
question" — but **the corpus supplies no Y/P/N anchors for it**, because CRD
scored it as a binary.  Its anchors below are therefore *platform-authored* and
are marked as such.  They must not be cited as Kitchenham's or CRD's.
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog
from db.models.slr import (
    ChecklistScoringMethod,
    QualityAssessmentChecklist,
    QualityChecklistItem,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

#: Name given to a seeded DARE checklist.
DARE_CHECKLIST_NAME = "DARE"

#: The only admissible score values for a ``yes_partial_no`` item.
YES_PARTIAL_NO_SCORES: tuple[float, ...] = (0.0, 0.5, 1.0)


@dataclass(frozen=True)
class DareQuestion:
    """One anchored DARE question.

    Attributes:
        order: 1-based position within the instrument.
        question: The question as put to the reviewer.
        anchors: What each score value means, keyed by the value as a string.

    """

    order: int
    question: str
    anchors: dict[str, str]


# ---------------------------------------------------------------------------
# The instrument — quoted from 04-tertiary.md 2.3
# ---------------------------------------------------------------------------

DARE_QUESTIONS: tuple[DareQuestion, ...] = (
    DareQuestion(
        order=1,
        question="Are the review's inclusion and exclusion criteria described and appropriate?",
        anchors={
            "1.0": "Inclusion criteria explicitly defined in the paper",
            "0.5": "Inclusion criteria implicit",
            "0.0": "Not defined and not readily inferable",
        },
    ),
    DareQuestion(
        order=2,
        question="Is the literature search likely to have covered all relevant studies?",
        anchors={
            "1.0": (
                "Searched four or more digital libraries and used additional search "
                "strategies, or identified and referenced all journals addressing the topic"
            ),
            "0.5": (
                "Searched 3 or 4 libraries with no extra strategies, or a defined but "
                "restricted set of journals and proceedings"
            ),
            "0.0": "Searched up to 2 libraries, or an extremely restricted set of journals",
        },
    ),
    DareQuestion(
        order=3,
        question="Did the reviewers assess the quality/validity of the included studies?",
        anchors={
            "1.0": "Explicitly defined quality criteria, extracted from each primary study",
            "0.5": "The research question itself involves quality issues addressed by the study",
            # The "or quality data extracted but not used" clause is a 2010
            # tightening. It is what makes collecting scores and ignoring them
            # score worse than never collecting them, and it is the single
            # clause most often lost when this rubric is paraphrased.
            "0.0": (
                "No explicit quality assessment attempted — or quality data extracted but not used"
            ),
        },
    ),
    DareQuestion(
        order=4,
        question="Were the basic data/studies adequately described?",
        anchors={
            "1.0": (
                "Information presented per paper such that data summaries can be traced "
                "to relevant papers"
            ),
            "0.5": (
                "Only summary information — papers grouped into categories, but individual "
                "studies cannot be linked to a category"
            ),
            "0.0": "Results of individual studies not specified; primary studies not cited",
        },
    ),
)

#: CRD's criterion 3, mandatory in the original DARE and dropped by SE.
#:
#: ``10-reporting-and-evaluation.md`` records the omission as "a concrete
#: instance of SE weakening an inherited standard", notes it is the same
#: criterion Cruzes & Dyba found missing from half the reviews they audited,
#: and recommends restoring it as an optional fifth question — which is what
#: this is.  Opt-in rather than default, because scores including it are not
#: comparable with the four-question DARE totals every SE tertiary study
#: reports.
#:
#: **The anchors here are platform-authored.** CRD scored this criterion as a
#: binary and the corpus supplies no Y/P/N wording for it.
DARE_SYNTHESIS_QUESTION = DareQuestion(
    order=5,
    question="Were the included studies synthesized?",
    anchors={
        "1.0": (
            "Findings from the included studies are combined into an explicit synthesis, "
            "with the method stated (platform-authored anchor — not from CRD)"
        ),
        "0.5": (
            "Findings are grouped or tabulated but not synthesised into an answer to the "
            "review question (platform-authored anchor — not from CRD)"
        ),
        "0.0": (
            "Studies are listed or described individually with no attempt at synthesis "
            "(platform-authored anchor — not from CRD)"
        ),
    },
)


def dare_item_payloads(include_synthesis: bool = False) -> list[dict]:
    """Return DARE questions shaped for ``quality_assessment_service.upsert_checklist``.

    Args:
        include_synthesis: Include the optional fifth (synthesis) question.
            Off by default, so a study's total is the out-of-4 figure the SE
            tertiary studies report.

    Returns:
        A list of item dicts with ``order``, ``question``, ``scoring_method``,
        ``weight`` and ``anchors``.

    """
    questions = list(DARE_QUESTIONS)
    if include_synthesis:
        questions.append(DARE_SYNTHESIS_QUESTION)
    return [
        {
            "order": question.order,
            "question": question.question,
            "scoring_method": ChecklistScoringMethod.YES_PARTIAL_NO.value,
            # Equal weights are load-bearing: DARE totals out of the number of
            # questions, so any other weighting silently rescales the result
            # into a figure that is no longer a DARE score.
            "weight": 1.0,
            "anchors": dict(question.anchors),
        }
        for question in questions
    ]


def validate_yes_partial_no(score_value: float, notes: str | None) -> None:
    """Validate one ``yes_partial_no`` answer, raising on anything inadmissible.

    Two rules, both methodological rather than merely defensive:

    1. The value must be one of :data:`YES_PARTIAL_NO_SCORES`. An off-scale
       value is not a finer-grained judgement, it is a score that cannot be
       read back as Y, P or N.
    2. A justification is **mandatory**. ``04-tertiary.md`` specifies that
       reviewers answer "providing a justification for each answer" and its
       implementation note calls this out as "not optional metadata". Without
       it a disagreement between two reviewers cannot be adjudicated, which is
       the entire point of recording per-reviewer scores.

    Args:
        score_value: The submitted score.
        notes: The submitted justification.

    Raises:
        ValueError: If the value is off-scale or the justification is absent
            or blank.

    """
    if score_value not in YES_PARTIAL_NO_SCORES:
        raise ValueError(
            f"Score {score_value} is not valid for a yes/partial/no item: must be 0.0, 0.5 or 1.0."
        )
    if notes is None or not notes.strip():
        raise ValueError(
            "A justification is required for every yes/partial/no answer "
            "(04-tertiary.md: justification per answer is mandatory)."
        )


def dare_total(average_score: float, item_count: int) -> float:
    """Convert a weighted average back to a DARE total out of ``item_count``.

    ``quality_assessment_service.compute_aggregate_score`` returns a weighted
    *mean*, which for equally weighted 0-1 items lies in 0-1. DARE is reported
    as a total out of 4 (or 5 with the synthesis question), so presenting the
    mean unchanged would show "0.75" where the instrument says "3 out of 4".

    Args:
        average_score: Weighted mean across the checklist's items.
        item_count: Number of items in the instrument.

    Returns:
        The total on DARE's own scale.

    """
    return average_score * item_count


async def seed_dare_checklist(
    study_id: int,
    db: AsyncSession,
    include_synthesis: bool = False,
) -> QualityAssessmentChecklist:
    """Give *study_id* a DARE checklist, unless it already has a checklist.

    Idempotent, and deliberately non-destructive: if the study already has any
    checklist — DARE or one the team defined themselves — it is returned
    untouched. Replacing it would delete its items, and
    ``quality_assessment_score.checklist_item_id`` cascades on delete, so every
    score already recorded against those items would go with them.

    Args:
        study_id: The study to seed.
        db: Active async database session.
        include_synthesis: Seed the optional fifth question as well.

    Returns:
        The study's checklist — freshly seeded, or the pre-existing one.

    """
    bound = logger.bind(study_id=study_id)

    result = await db.execute(
        select(QualityAssessmentChecklist).where(QualityAssessmentChecklist.study_id == study_id)
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        await db.refresh(existing, attribute_names=["items"])
        bound.info("seed_dare_checklist: checklist already present", name=existing.name)
        return existing

    checklist = QualityAssessmentChecklist(
        study_id=study_id,
        name=DARE_CHECKLIST_NAME,
        description=(
            "Database of Abstracts of Reviews of Effects (CRD, University of York), as "
            "applied to secondary studies in software engineering. Scored Y = 1, "
            "P = 0.5, N = 0."
        ),
    )
    db.add(checklist)
    await db.flush()

    for payload in dare_item_payloads(include_synthesis=include_synthesis):
        db.add(
            QualityChecklistItem(
                checklist_id=checklist.id,
                order=payload["order"],
                question=payload["question"],
                scoring_method=payload["scoring_method"],
                weight=payload["weight"],
                anchors=payload["anchors"],
            )
        )

    await db.commit()
    await db.refresh(checklist, attribute_names=["items"])
    bound.info("seed_dare_checklist: seeded", item_count=len(checklist.items))
    return checklist
