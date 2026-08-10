"""Derive and record threats to validity for non-Rapid studies (TFIX11).

``docs/methodology/09-threats-to-validity.md`` combines two frameworks:
Ampatzoglou's catalogue says *which* things can go wrong, Petersen & Gencel's
taxonomy says which heading each one is *reported under*. This module applies
both to SLR, SMS and Tertiary studies.

**Rapid Reviews are deliberately excluded.** The chapter assigns them Cartaxo's
disclosure regime instead — "every methodological concession is itself a threat"
— which ``rr_protocol_service.set_single_reviewer_mode`` already implements.
Deriving here as well would show a Rapid researcher the same bias twice, in two
vocabularies, and leave them unsure whether it was one problem or two.

**What is derived, and why three threats rather than one.** A single human
reviewer biases three distinct steps, and the chapter catalogues them
separately: selection (TV7), extraction (TV13.4) and synthesis (TV16, which it
defines as covering "only one author doing the synthesis"). Recording one
generic "single reviewer" threat would collapse three mitigations — each named
at a different point in ``01-slr.md`` — into a single box.

**The platform never blocks a single-reviewer study.** ``04-tertiary.md``
records one person seeing every paper as "a known bias, **accepted
deliberately**", and asks only that the trade-off be recorded "rather than
pretending it does not exist". So derivation discloses; it does not gate. What
*is* gated — at report generation only — is Ampatzoglou's step 4: a threat
carrying neither a mitigation nor an acknowledgement. That is always
satisfiable by acknowledging, so it can never trap a lone researcher.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from db.models import Study, StudyType
from db.models.study import Reviewer, ReviewerType
from db.models.validity import StudyValidityThreat, ValidityCategory, ValidityThreatId
from sqlalchemy import func, select

from backend.core.config import get_logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

# Study types governed by Ampatzoglou's catalogue. Rapid is absent by design —
# see the module docstring.
_AMPATZOGLOU_STUDY_TYPES = frozenset({StudyType.SLR, StudyType.SMS, StudyType.TERTIARY})

# The three threats a lone human reviewer raises, with the reporting category
# each is filed under.
#
# Category assignment follows ch.09's worked pairings where it gives them:
# "TV13 (extraction bias) is filed under **descriptive validity**", and a
# study-selection threat is "discussed under **theoretical validity**, because
# it concerns whether the study captured what it intended to". TV16's mapping to
# interpretive validity is an inference from the category definitions rather
# than a pairing the chapter states outright — TV16 is bias "in interpreting or
# synthesising", and interpretive validity asks whether "the conclusions are
# reasonable given the data". Flagged here rather than presented as sourced.
_SINGLE_REVIEWER_THREATS: tuple[tuple[ValidityThreatId, ValidityCategory, str], ...] = (
    (
        ValidityThreatId.TV7,
        ValidityCategory.THEORETICAL,
        "Inclusion and exclusion decisions were made by a single human reviewer, so no "
        "independent second judgement was applied and no inter-rater agreement can be "
        "computed. Kitchenham & Charters require a lone researcher to use test-retest — "
        "re-evaluating a random sample of already-screened papers to check their own "
        "consistency (01-slr.md 2.2; 06-search-and-selection.md, Reliability).",
    ),
    (
        ValidityThreatId.TV13_4,
        ValidityCategory.DESCRIPTIVE,
        "Data extraction was carried out by a single human reviewer and was not validated "
        "by external or internal review. A lone researcher is required to use a supervisor "
        "cross-check on a sample, or test-retest (01-slr.md 2.4); Ampatzoglou also lists "
        "random paper screening to cross-check extraction among TV13's mitigations. "
        "Extraction bias is described in the corpus as one of the most common threats in "
        "software engineering secondary studies.",
    ),
    (
        ValidityThreatId.TV16,
        ValidityCategory.INTERPRETIVE,
        "A single researcher interpreted and synthesised the results. Ampatzoglou defines "
        "TV16 as bias in interpreting or synthesising, explicitly including the case of "
        "only one author doing the synthesis. Suggested mitigations include piloting the "
        "data analysis and interpretation, reliability checks such as post-review surveys "
        "with experts, using a formal synthesis method, and sensitivity analysis.",
    ),
)


async def count_human_reviewers(study_id: int, db: AsyncSession) -> int:
    """Return how many human reviewer slots *study_id* has.

    AI reviewers are excluded. The mitigations the corpus prescribes — a
    supervisor cross-check, or a second independent screener — are human acts,
    so counting an agent here would let the platform declare the bias resolved
    by adding automation to it.

    Args:
        study_id: The study to count reviewers for.
        db: Active async session.

    Returns:
        The number of ``Reviewer`` rows of type ``human``.

    """
    result = await db.execute(
        select(func.count())
        .select_from(Reviewer)
        .where(
            Reviewer.study_id == study_id,
            Reviewer.reviewer_type == ReviewerType.HUMAN,
        )
    )
    return int(result.scalar_one())


async def _applicable_threat_ids(study_id: int, db: AsyncSession) -> set[ValidityThreatId]:
    """Return the threat ids that currently apply to *study_id*.

    Args:
        study_id: The study whose configuration is evaluated.
        db: Active async session.

    Returns:
        The set of applicable :class:`ValidityThreatId` values — empty for
        Rapid studies, for studies that do not exist, and for studies with
        zero or two-or-more human reviewers.

    """
    study = (await db.execute(select(Study).where(Study.id == study_id))).scalar_one_or_none()
    if study is None or study.study_type not in _AMPATZOGLOU_STUDY_TYPES:
        return set()

    # Zero reviewers is not single-reviewer. Reviewer rows are created lazily,
    # the first time a member records a decision, so a study that nobody has
    # screened yet has none — firing the disclosure then would announce a bias
    # before anyone has had the chance to introduce it.
    if await count_human_reviewers(study_id, db) != 1:
        return set()

    return {threat_id for threat_id, _, _ in _SINGLE_REVIEWER_THREATS}


async def sync_derived_threats(study_id: int, db: AsyncSession) -> None:
    """Reconcile *study_id*'s derived threat rows with its current configuration.

    Idempotent, because it runs on every read of the threat list. Rows for
    threats that no longer apply are flagged ``is_applicable = False`` rather
    than deleted, so a study that gains a second reviewer does not lose the
    text its first reviewer wrote — and gets it back if it drops to one again.

    Args:
        study_id: The study to reconcile.
        db: Active async session. Committed by this function.

    """
    applicable = await _applicable_threat_ids(study_id, db)

    existing = {
        threat.threat_id: threat
        for threat in (
            await db.execute(
                select(StudyValidityThreat).where(StudyValidityThreat.study_id == study_id)
            )
        )
        .scalars()
        .all()
    }

    changed = False
    for threat_id, category, description in _SINGLE_REVIEWER_THREATS:
        should_apply = threat_id in applicable
        row = existing.get(threat_id)

        if row is None:
            if should_apply:
                db.add(
                    StudyValidityThreat(
                        study_id=study_id,
                        threat_id=threat_id,
                        validity_category=category,
                        description=description,
                        source_detail="1 human reviewer",
                        is_applicable=True,
                    )
                )
                changed = True
        elif row.is_applicable != should_apply:
            row.is_applicable = should_apply
            changed = True

    if changed:
        await db.commit()
        logger.info(
            "sync_derived_threats: reconciled",
            study_id=study_id,
            applicable=sorted(t.value for t in applicable),
        )


async def list_threats(study_id: int, db: AsyncSession) -> list[StudyValidityThreat]:
    """Return the currently applicable threats for *study_id*.

    Inapplicable rows are retained in the database but never listed — they are
    history, not part of the study's current threat profile.

    Args:
        study_id: The study to list threats for.
        db: Active async session.

    Returns:
        Applicable :class:`StudyValidityThreat` rows, ordered by id.

    """
    result = await db.execute(
        select(StudyValidityThreat)
        .where(
            StudyValidityThreat.study_id == study_id,
            StudyValidityThreat.is_applicable.is_(True),
        )
        .order_by(StudyValidityThreat.id)
    )
    return list(result.scalars().all())


async def address_threat(
    study_id: int,
    threat_id: ValidityThreatId,
    db: AsyncSession,
    *,
    mitigation: str | None = None,
    acknowledgement: str | None = None,
) -> StudyValidityThreat:
    """Record Ampatzoglou's step-4 outcome for one threat.

    Both outcomes are permitted and neither ranks above the other: reporting a
    mitigation and acknowledging that the threat is not (fully) mitigated are
    the two branches the chapter offers. Passing empty strings clears an
    outcome, which returns the threat to unaddressed — retracting an
    acknowledgement must reopen the report gate rather than leave it ajar.

    Args:
        study_id: The study the threat belongs to.
        threat_id: Which catalogue entry to address.
        db: Active async session. Committed by this function.
        mitigation: An action taken to reduce the threat, or ``None`` to leave
            the stored value unchanged.
        acknowledgement: An explicit statement that the threat is accepted, or
            ``None`` to leave the stored value unchanged.

    Returns:
        The updated :class:`StudyValidityThreat`.

    Raises:
        LookupError: If the study has no row for *threat_id*.

    """
    threat = (
        await db.execute(
            select(StudyValidityThreat).where(
                StudyValidityThreat.study_id == study_id,
                StudyValidityThreat.threat_id == threat_id,
            )
        )
    ).scalar_one_or_none()

    if threat is None:
        raise LookupError(f"Study {study_id} has no derived threat {threat_id.value}")

    if mitigation is not None:
        threat.mitigation = mitigation
    if acknowledgement is not None:
        threat.acknowledgement = acknowledgement

    await db.commit()
    await db.refresh(threat)
    logger.info(
        "address_threat: recorded",
        study_id=study_id,
        threat_id=threat_id.value,
        addressed=threat.is_addressed,
    )
    return threat


async def unaddressed_applicable_threats(
    study_id: int, db: AsyncSession
) -> list[StudyValidityThreat]:
    """Return applicable threats carrying neither a mitigation nor an acknowledgement.

    This is what the report and export endpoints consult. The chapter calls a
    threat in this state "an incomplete study", and singles the check out as
    "exactly the shape of check the platform's phase gates already perform".

    Filtering happens in Python rather than SQL so that
    :attr:`StudyValidityThreat.is_addressed` stays the single definition of
    what "addressed" means — including its rejection of whitespace, which a
    naive ``IS NOT NULL`` predicate would accept.

    Args:
        study_id: The study to check.
        db: Active async session.

    Returns:
        The outstanding threats, empty when the study is clear to report.

    """
    return [t for t in await list_threats(study_id, db) if not t.is_addressed]


_THREAT_LABELS: dict[ValidityThreatId, str] = {
    ValidityThreatId.TV7: "TV7 — Study inclusion/exclusion",
    ValidityThreatId.TV13_4: "TV13.4 — Unverified data extraction",
    ValidityThreatId.TV16: "TV16 — Researcher bias",
}

_CATEGORY_LABELS: dict[ValidityCategory, str] = {
    ValidityCategory.DESCRIPTIVE: "descriptive validity",
    ValidityCategory.THEORETICAL: "theoretical validity",
    ValidityCategory.GENERALIZABILITY_INTERNAL: "generalizability (internal)",
    ValidityCategory.GENERALIZABILITY_EXTERNAL: "generalizability (external)",
    ValidityCategory.INTERPRETIVE: "interpretive validity",
    ValidityCategory.REPEATABILITY: "repeatability",
}

# Stated in every generated section, whether or not any threat was derived.
#
# Ampatzoglou's step 3 is "check every threat for whether it pertains to the
# study", against the full TV1-TV22 catalogue. The platform derives three
# entries from configuration and checks nothing else, so a section that simply
# listed what it found would imply a completeness it has not earned. Saying so
# costs one sentence; leaving it out would make the report overstate its own
# rigour, which is the failure the chapter's closing caution is about.
_COVERAGE_CAVEAT = (
    "The threats below were derived automatically from this study's "
    "configuration. They are not a complete application of a threat catalogue, "
    "and do not replace the authors' own review of threats specific to this "
    "review."
)


async def build_threats_section(study_id: int, db: AsyncSession) -> str:
    """Render the study's threats-to-validity section for its report.

    This is Ampatzoglou's **step 1** — "create a dedicated threats-to-validity
    section in both the protocol and the final report" — and it is what makes
    the step-4 gate mean anything. Without it the platform compels a researcher
    to record a mitigation or an acknowledgement and then publishes neither.

    Each threat is rendered with its catalogue id, the Petersen & Gencel
    heading it reports under, its description, and its step-4 outcome. The two
    outcomes are labelled differently on purpose: collapsing them would let a
    reader take "accepted, not mitigated" for "handled".

    Args:
        study_id: The study whose report is being generated.
        db: Active async session.

    Returns:
        A human-readable section body. Never empty — a study with no derived
        threats gets a statement to that effect rather than silence, because a
        blank section is indistinguishable from a section that failed to build.

    """
    threats = await list_threats(study_id, db)

    if not threats:
        return (
            "No threats to validity were derived automatically from this "
            "study's configuration. " + _COVERAGE_CAVEAT
        )

    parts = [
        "Threats are catalogued following Ampatzoglou et al. and reported under "
        "the validity categories of Petersen & Gencel. " + _COVERAGE_CAVEAT,
        "",
    ]

    for threat in threats:
        label = _THREAT_LABELS.get(threat.threat_id, threat.threat_id.value)
        category = _CATEGORY_LABELS.get(threat.validity_category, threat.validity_category.value)
        parts.append(f"{label} (reported under {category}).")
        parts.append(threat.description)

        mitigation = (threat.mitigation or "").strip()
        acknowledgement = (threat.acknowledgement or "").strip()
        if mitigation:
            parts.append(f"Mitigation: {mitigation}")
        if acknowledgement:
            parts.append(f"Acknowledged as not fully mitigated: {acknowledgement}")
        if not mitigation and not acknowledgement:
            # Reachable only for a report built by a path that does not call
            # require_threats_addressed. Better to publish the omission than to
            # let the threat vanish from the section that exists to carry it.
            parts.append("No mitigation or acknowledgement has been recorded for this threat.")
        parts.append("")

    return "\n".join(parts).strip()


async def require_threats_addressed(study_id: int, db: AsyncSession) -> None:
    """Raise HTTP 409 if *study_id* has an unaddressed applicable threat.

    Called by the report and export endpoints, and **only** by them. The
    distinction is deliberate and is the whole shape of TFIX11: a
    single-reviewer study is never blocked from *proceeding* — the corpus
    permits it explicitly — but a study must not *publish* a report carrying a
    threat it has neither mitigated nor acknowledged, which the chapter calls
    "an incomplete study".

    Derivation runs first, so a study that became single-reviewer since its
    last page load is still caught.

    Args:
        study_id: The study about to generate a report or export.
        db: Active async session.

    Raises:
        HTTPException: 409 listing the outstanding threats, with the two ways
            to clear each one.

    """
    from fastapi import HTTPException, status

    await sync_derived_threats(study_id, db)
    outstanding = await unaddressed_applicable_threats(study_id, db)
    if not outstanding:
        return

    logger.info(
        "require_threats_addressed: blocked",
        study_id=study_id,
        outstanding=[t.threat_id.value for t in outstanding],
    )
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error": "unaddressed_validity_threats",
            "message": (
                "This study has identified threats to validity that carry neither a "
                "mitigation nor an acknowledgement. Record either one for each — "
                "acknowledging that a threat is not mitigated is a complete answer."
            ),
            "threats": [
                {
                    "threat_id": t.threat_id.value,
                    "validity_category": t.validity_category.value,
                    "description": t.description,
                }
                for t in outstanding
            ],
        },
    )
