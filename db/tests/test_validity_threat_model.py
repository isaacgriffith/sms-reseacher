"""Unit tests for the study-generic validity threat model (TFIX11).

The model encodes Ampatzoglou et al.'s threat catalogue for SLR, SMS and
Tertiary studies. Rapid Reviews are deliberately **not** covered — per
``docs/methodology/09-threats-to-validity.md`` they use Cartaxo's disclosure
regime instead, which the existing ``RRThreatToValidity`` already implements.

The property under test throughout is Ampatzoglou's **step 4**: every
identified threat carries either a mitigation action or an explicit
acknowledgement that it is not (fully) mitigated. A threat with neither is,
in the chapter's words, "an incomplete study".
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
from db.models.validity import (
    StudyValidityThreat,
    ValidityCategory,
    ValidityThreatId,
)


@pytest_asyncio.fixture
async def session():
    """Yield an in-memory SQLite async session with all tables created."""
    import db.models  # noqa: F401  — ensures all FK targets are registered
    import db.models.study  # noqa: F401
    import db.models.users  # noqa: F401
    import db.models.validity  # noqa: F401

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    await engine.dispose()


async def _make_study(session) -> int:
    """Create a minimal study and return its id."""
    from db.models import Study, StudyType

    study = Study(name="A one-person review", study_type=StudyType.SLR)
    session.add(study)
    await session.flush()
    return study.id


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_table_name_is_study_scoped_not_rapid_scoped():
    """The table is study-generic, not a second copy of the Rapid one."""
    assert StudyValidityThreat.__tablename__ == "study_validity_threat"


def test_threat_ids_are_ampatzoglou_catalogue_entries():
    """Only the catalogue entries the platform actually derives are encoded."""
    assert {t.value for t in ValidityThreatId} == {"tv7", "tv13_4", "tv16"}


def test_validity_categories_match_the_six_study_validity_keys():
    """Reporting categories are Petersen & Gencel's, matching ``Study.validity``."""
    assert {c.value for c in ValidityCategory} == {
        "descriptive",
        "theoretical",
        "generalizability_internal",
        "generalizability_external",
        "interpretive",
        "repeatability",
    }


def test_has_both_step_four_outcome_columns():
    """Step 4 permits *either* a mitigation *or* an acknowledgement.

    ``RRThreatToValidity`` has neither column, which is why TFIX11's
    instruction to copy it was not followed.
    """
    columns = {c.key for c in inspect(StudyValidityThreat).columns}
    assert "mitigation" in columns
    assert "acknowledgement" in columns


# ---------------------------------------------------------------------------
# Step 4 — addressed means mitigated *or* acknowledged
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_new_threat_is_not_addressed(session):
    """A freshly derived threat has neither outcome, so it is unaddressed."""
    study_id = await _make_study(session)
    threat = StudyValidityThreat(
        study_id=study_id,
        threat_id=ValidityThreatId.TV7,
        validity_category=ValidityCategory.THEORETICAL,
        description="Single reviewer screened every paper.",
    )
    session.add(threat)
    await session.flush()

    assert threat.is_addressed is False


@pytest.mark.asyncio
async def test_a_mitigation_addresses_the_threat(session):
    """Recording a mitigation action satisfies step 4."""
    study_id = await _make_study(session)
    threat = StudyValidityThreat(
        study_id=study_id,
        threat_id=ValidityThreatId.TV7,
        validity_category=ValidityCategory.THEORETICAL,
        description="Single reviewer screened every paper.",
        mitigation="A supervisor cross-checked a random sample of 30 decisions.",
    )
    session.add(threat)
    await session.flush()

    assert threat.is_addressed is True


@pytest.mark.asyncio
async def test_an_acknowledgement_addresses_the_threat(session):
    """Acknowledging an unmitigated threat is an equally valid step-4 outcome.

    This is the load-bearing case for a lone researcher: the corpus permits
    single-reviewer studies, so the platform must never make "I could not
    mitigate this" an unreachable state.
    """
    study_id = await _make_study(session)
    threat = StudyValidityThreat(
        study_id=study_id,
        threat_id=ValidityThreatId.TV7,
        validity_category=ValidityCategory.THEORETICAL,
        description="Single reviewer screened every paper.",
        acknowledgement="No second reviewer was available; the bias is accepted and reported.",
    )
    session.add(threat)
    await session.flush()

    assert threat.is_addressed is True


@pytest.mark.asyncio
async def test_whitespace_is_not_an_outcome(session):
    """Blank text must not count as addressing a threat.

    Without this, a user could satisfy the report gate by typing a space.
    """
    study_id = await _make_study(session)
    threat = StudyValidityThreat(
        study_id=study_id,
        threat_id=ValidityThreatId.TV16,
        validity_category=ValidityCategory.INTERPRETIVE,
        description="One author performed the synthesis.",
        mitigation="   ",
        acknowledgement="\n\t ",
    )
    session.add(threat)
    await session.flush()

    assert threat.is_addressed is False


# ---------------------------------------------------------------------------
# Derivation invariants
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_one_row_per_study_and_threat(session):
    """The unique constraint is what makes re-derivation idempotent.

    Derivation runs on every read of the threat list, so without this a
    single-reviewer study would accumulate a duplicate TV7 on every page load.
    """
    study_id = await _make_study(session)
    for _ in range(2):
        session.add(
            StudyValidityThreat(
                study_id=study_id,
                threat_id=ValidityThreatId.TV7,
                validity_category=ValidityCategory.THEORETICAL,
                description="Single reviewer screened every paper.",
            )
        )

    with pytest.raises(IntegrityError):
        await session.flush()


@pytest.mark.asyncio
async def test_threats_default_to_applicable(session):
    """A derived threat applies until the configuration says otherwise."""
    study_id = await _make_study(session)
    threat = StudyValidityThreat(
        study_id=study_id,
        threat_id=ValidityThreatId.TV13_4,
        validity_category=ValidityCategory.DESCRIPTIVE,
        description="Extractions were not independently verified.",
    )
    session.add(threat)
    await session.flush()

    assert threat.is_applicable is True


@pytest.mark.asyncio
async def test_recorded_text_survives_becoming_inapplicable(session):
    """Adding a second reviewer must not destroy what the first one wrote.

    ``is_applicable`` is a flag rather than a delete precisely so that a study
    that briefly had two reviewers, then dropped back to one, does not lose
    its acknowledgement text.
    """
    study_id = await _make_study(session)
    threat = StudyValidityThreat(
        study_id=study_id,
        threat_id=ValidityThreatId.TV7,
        validity_category=ValidityCategory.THEORETICAL,
        description="Single reviewer screened every paper.",
        acknowledgement="Accepted deliberately.",
    )
    session.add(threat)
    await session.flush()

    threat.is_applicable = False
    await session.flush()
    await session.refresh(threat)

    assert threat.acknowledgement == "Accepted deliberately."
