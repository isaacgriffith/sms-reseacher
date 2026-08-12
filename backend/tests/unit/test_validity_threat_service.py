"""Unit tests for backend.services.validity_threat_service (TFIX11).

The service derives Ampatzoglou threats from study configuration for SLR, SMS
and Tertiary studies. Rapid Reviews are excluded on purpose: per
``docs/methodology/09-threats-to-validity.md`` they use Cartaxo's disclosure
regime, already implemented by ``rr_protocol_service.set_single_reviewer_mode``.

Two properties carry most of the weight here:

- **Derivation is idempotent.** It runs on every read of the threat list, so a
  non-idempotent implementation would accumulate duplicates invisibly.
- **Nothing is ever blocked for being single-reviewer.** The corpus permits a
  lone researcher and requires only that the bias be recorded. Every test that
  touches the report gate checks it can be satisfied by acknowledgement alone.
"""

from __future__ import annotations

# Register all ORM models
import db.models  # noqa: F401
import db.models.candidate  # noqa: F401
import db.models.study  # noqa: F401
import db.models.users  # noqa: F401
import db.models.validity  # noqa: F401
import pytest
import pytest_asyncio
from db.base import Base
from db.models import Study, StudyType
from db.models.study import Reviewer, ReviewerType
from db.models.validity import StudyValidityThreat, ValidityCategory, ValidityThreatId
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.services.validity_threat_service import (
    address_threat,
    build_threats_section,
    list_threats,
    sync_derived_threats,
    unaddressed_applicable_threats,
)


@pytest_asyncio.fixture
async def db_session():
    """Provide a fresh in-memory SQLite session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        yield session
    await engine.dispose()


async def _make_study(db_session, study_type: StudyType = StudyType.SLR) -> int:
    """Create a study of *study_type* and return its id."""
    study = Study(name="A review", study_type=study_type)
    db_session.add(study)
    await db_session.flush()
    return study.id


async def _add_human_reviewers(db_session, study_id: int, count: int) -> None:
    """Attach *count* human reviewer rows to *study_id*."""
    for _ in range(count):
        db_session.add(Reviewer(study_id=study_id, reviewer_type=ReviewerType.HUMAN))
    await db_session.flush()


# ---------------------------------------------------------------------------
# Derivation
# ---------------------------------------------------------------------------


class TestSingleReviewerDerivation:
    """One human reviewer derives the three threats that bias implies."""

    @pytest.mark.asyncio
    async def test_one_reviewer_derives_three_threats(self, db_session) -> None:
        """Single-reviewer bias is not one threat but three, at three steps.

        TV7 is selection, TV13.4 is unverified extraction, TV16 is researcher
        bias in synthesis — which ch.09 defines as "including only one author
        doing the synthesis".
        """
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)

        await sync_derived_threats(study_id, db_session)

        threats = await list_threats(study_id, db_session)
        assert {t.threat_id for t in threats} == {
            ValidityThreatId.TV7,
            ValidityThreatId.TV13_4,
            ValidityThreatId.TV16,
        }

    @pytest.mark.asyncio
    async def test_threats_are_filed_under_reporting_categories(self, db_session) -> None:
        """Each threat carries the Petersen & Gencel heading it reports under."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)

        await sync_derived_threats(study_id, db_session)

        by_id = {t.threat_id: t for t in await list_threats(study_id, db_session)}

        # TV13.4 is the only one of the three ch.09 files for us: 222 states
        # "TV13 (extraction bias) is filed under **descriptive validity**".
        assert by_id[ValidityThreatId.TV13_4].validity_category == ValidityCategory.DESCRIPTIVE

        # TFIX15. TV7 and TV16 used to carry theoretical and interpretive. The
        # chapter states neither pairing — TV7's was an extension of the pairing
        # ch.09 220-221 makes for TV1.2 alone, and TV16's was flagged as an
        # inference in the code that set it. ch.09 206-210 says the rest of the
        # cross-mapping "must be verified against the PDF before being quoted",
        # so the researcher files these rather than the platform guessing.
        assert by_id[ValidityThreatId.TV7].validity_category is None
        assert by_id[ValidityThreatId.TV16].validity_category is None

    @pytest.mark.asyncio
    async def test_two_reviewers_derive_nothing(self, db_session) -> None:
        """The bias does not exist when two people screen independently."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 2)

        await sync_derived_threats(study_id, db_session)

        assert await list_threats(study_id, db_session) == []

    @pytest.mark.asyncio
    async def test_zero_reviewers_derives_nothing(self, db_session) -> None:
        """A study nobody has screened yet is not a single-reviewer study.

        Reviewer rows are created lazily on first decision, so a brand-new
        study has none. Treating zero as one would fire the disclosure before
        there is anything to disclose.
        """
        study_id = await _make_study(db_session)

        await sync_derived_threats(study_id, db_session)

        assert await list_threats(study_id, db_session) == []

    @pytest.mark.asyncio
    async def test_ai_reviewers_do_not_count_as_a_second_reviewer(self, db_session) -> None:
        """An AI reviewer does not discharge the need for a human cross-check.

        The mitigation the corpus prescribes is supervisor cross-check or
        test-retest by a *person*; counting an agent here would let the
        platform silently declare the bias resolved by adding automation.
        """
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        db_session.add(Reviewer(study_id=study_id, reviewer_type=ReviewerType.AI_AGENT))
        await db_session.flush()

        await sync_derived_threats(study_id, db_session)

        assert len(await list_threats(study_id, db_session)) == 3

    @pytest.mark.asyncio
    async def test_rapid_studies_are_excluded(self, db_session) -> None:
        """Rapid Reviews keep Cartaxo's regime; they must not get both.

        ``rr_protocol_service.set_single_reviewer_mode`` already records this
        bias as an ``RRThreatToValidity``. Deriving here too would show a
        Rapid researcher the same threat twice under two vocabularies.
        """
        study_id = await _make_study(db_session, StudyType.RAPID)
        await _add_human_reviewers(db_session, study_id, 1)

        await sync_derived_threats(study_id, db_session)

        assert await list_threats(study_id, db_session) == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize("study_type", [StudyType.SLR, StudyType.SMS, StudyType.TERTIARY])
    async def test_all_three_ampatzoglou_study_types_covered(self, db_session, study_type) -> None:
        """The defect TFIX11 names is that only Rapid discloses this."""
        study_id = await _make_study(db_session, study_type)
        await _add_human_reviewers(db_session, study_id, 1)

        await sync_derived_threats(study_id, db_session)

        applicable = {t.threat_id for t in await list_threats(study_id, db_session)}

        # The three single-reviewer threats apply on every Ampatzoglou study
        # type. TFIX15 added a fourth derivation that fires on SMS alone —
        # ch.09 110 calls TV13.5 "mostly a mapping-study threat" — so assert the
        # single-reviewer set is present rather than pinning a total that means
        # something different per study type.
        assert {
            ValidityThreatId.TV7,
            ValidityThreatId.TV13_4,
            ValidityThreatId.TV16,
        } <= applicable
        assert (ValidityThreatId.TV13_5 in applicable) is (study_type is StudyType.SMS)

    @pytest.mark.asyncio
    async def test_threats_scope_to_their_own_study(self, db_session) -> None:
        """A lone reviewer on one study must not raise threats on another."""
        lone_study = await _make_study(db_session)
        await _add_human_reviewers(db_session, lone_study, 1)
        paired_study = await _make_study(db_session)
        await _add_human_reviewers(db_session, paired_study, 2)

        await sync_derived_threats(lone_study, db_session)
        await sync_derived_threats(paired_study, db_session)

        assert len(await list_threats(lone_study, db_session)) == 3
        assert await list_threats(paired_study, db_session) == []


class TestDerivationIsIdempotent:
    """Re-derivation must converge, because it runs on every read."""

    @pytest.mark.asyncio
    async def test_repeated_derivation_does_not_duplicate(self, db_session) -> None:
        """Three calls produce three rows, not nine."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)

        for _ in range(3):
            await sync_derived_threats(study_id, db_session)

        assert len(await list_threats(study_id, db_session)) == 3

    @pytest.mark.asyncio
    async def test_gaining_a_reviewer_withdraws_the_threats(self, db_session) -> None:
        """Adding a second screener retires the disclosure."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)

        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)

        assert await list_threats(study_id, db_session) == []

    @pytest.mark.asyncio
    async def test_withdrawn_threats_keep_their_recorded_text(self, db_session) -> None:
        """A second reviewer must not delete what the first one wrote.

        The row is flagged inapplicable rather than deleted, so if the study
        drops back to one reviewer the acknowledgement is still there.
        """
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)
        await address_threat(
            study_id, ValidityThreatId.TV7, db_session, acknowledgement="Accepted deliberately."
        )

        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)

        stored = (
            await db_session.execute(
                select(StudyValidityThreat).where(
                    StudyValidityThreat.study_id == study_id,
                    StudyValidityThreat.threat_id == ValidityThreatId.TV7,
                )
            )
        ).scalar_one()
        assert stored.is_applicable is False
        assert stored.acknowledgement == "Accepted deliberately."

    @pytest.mark.asyncio
    async def test_losing_a_reviewer_restores_the_threat(self, db_session) -> None:
        """Applicability follows the configuration in both directions."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 2)
        await sync_derived_threats(study_id, db_session)

        reviewer = (
            (await db_session.execute(select(Reviewer).where(Reviewer.study_id == study_id)))
            .scalars()
            .first()
        )
        await db_session.delete(reviewer)
        await db_session.flush()
        await sync_derived_threats(study_id, db_session)

        assert len(await list_threats(study_id, db_session)) == 3


# ---------------------------------------------------------------------------
# Step 4 — addressing a threat
# ---------------------------------------------------------------------------


class TestAddressThreat:
    """Ampatzoglou step 4: a mitigation *or* an acknowledgement."""

    @pytest.mark.asyncio
    async def test_recording_a_mitigation_addresses_it(self, db_session) -> None:
        """Supervisor cross-check is the mitigation 01-slr.md names."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)

        threat = await address_threat(
            study_id,
            ValidityThreatId.TV7,
            db_session,
            mitigation="Supervisor cross-checked a random sample of 30 decisions.",
        )

        assert threat.is_addressed is True

    @pytest.mark.asyncio
    async def test_recording_an_acknowledgement_addresses_it(self, db_session) -> None:
        """A lone researcher with no supervisor must still be able to finish."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)

        threat = await address_threat(
            study_id,
            ValidityThreatId.TV16,
            db_session,
            acknowledgement="Sole author; the bias is accepted and reported.",
        )

        assert threat.is_addressed is True

    @pytest.mark.asyncio
    async def test_clearing_both_makes_it_unaddressed_again(self, db_session) -> None:
        """Retracting an acknowledgement must reopen the gate, not leave it ajar."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)
        await address_threat(study_id, ValidityThreatId.TV7, db_session, acknowledgement="Accepted")

        threat = await address_threat(
            study_id, ValidityThreatId.TV7, db_session, mitigation="", acknowledgement=""
        )

        assert threat.is_addressed is False

    @pytest.mark.asyncio
    async def test_unknown_threat_raises(self, db_session) -> None:
        """Addressing a threat that was never derived is a caller error."""
        study_id = await _make_study(db_session)

        with pytest.raises(LookupError):
            await address_threat(
                study_id, ValidityThreatId.TV7, db_session, acknowledgement="Accepted"
            )


# ---------------------------------------------------------------------------
# The report gate
# ---------------------------------------------------------------------------


class TestUnaddressedApplicableThreats:
    """What the report/export gate consults."""

    @pytest.mark.asyncio
    async def test_derived_but_unaddressed_threats_are_returned(self, db_session) -> None:
        """A fresh single-reviewer study has three unaddressed threats."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)

        assert len(await unaddressed_applicable_threats(study_id, db_session)) == 3

    @pytest.mark.asyncio
    async def test_acknowledging_all_three_clears_the_gate(self, db_session) -> None:
        """Acknowledgement alone must be enough to publish.

        This is the load-bearing case for TFIX11's "disclosure, not a gate":
        a lone researcher who cannot mitigate is never trapped.
        """
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)

        # TFIX15. This iterated every ValidityThreatId, which worked while the
        # enum held exactly the three derived threats. The catalogue is now the
        # full TV1–TV22 set including six group umbrellas, which are never
        # materialised — addressing one raises LookupError. Only threats that
        # actually apply can block the gate, so only those need addressing.
        for threat in await list_threats(study_id, db_session):
            await address_threat(
                study_id, threat.threat_id, db_session, acknowledgement="Accepted deliberately."
            )

        assert await unaddressed_applicable_threats(study_id, db_session) == []

    @pytest.mark.asyncio
    async def test_partially_addressed_still_blocks(self, db_session) -> None:
        """Addressing two of three leaves the third outstanding."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)
        await address_threat(study_id, ValidityThreatId.TV7, db_session, acknowledgement="Accepted")
        await address_threat(
            study_id, ValidityThreatId.TV16, db_session, acknowledgement="Accepted"
        )

        outstanding = await unaddressed_applicable_threats(study_id, db_session)
        assert [t.threat_id for t in outstanding] == [ValidityThreatId.TV13_4]

    @pytest.mark.asyncio
    async def test_inapplicable_threats_never_block(self, db_session) -> None:
        """A withdrawn threat must not hold the report hostage.

        Without this, a study that added a second reviewer would be blocked
        for ever by an unaddressed threat that no longer applies.
        """
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)

        assert await unaddressed_applicable_threats(study_id, db_session) == []

    @pytest.mark.asyncio
    async def test_a_study_with_no_threats_is_clear(self, db_session) -> None:
        """The gate is inert for studies the derivation does not touch."""
        study_id = await _make_study(db_session, StudyType.RAPID)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)

        assert await unaddressed_applicable_threats(study_id, db_session) == []


# ---------------------------------------------------------------------------
# The report section (Ampatzoglou step 1)
# ---------------------------------------------------------------------------


class TestBuildThreatsSection:
    """Step 1: a dedicated threats-to-validity section in the final report.

    The gate compels the researcher to address each threat; this is what makes
    that compulsion mean something. Without it the platform extracts a
    disclosure and then discards it — the acknowledgement never reaches a
    reader.
    """

    @pytest.mark.asyncio
    async def test_section_names_each_threat(self, db_session) -> None:
        """Every applicable threat appears, by catalogue id."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)

        section = await build_threats_section(study_id, db_session)

        assert "TV7" in section
        assert "TV13.4" in section
        assert "TV16" in section

    @pytest.mark.asyncio
    async def test_section_files_threats_under_reporting_categories(self, db_session) -> None:
        """Petersen & Gencel headings appear, per ch.09 Framework B."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)

        section = await build_threats_section(study_id, db_session)

        # ch.09 222 files TV13 under descriptive validity — the one heading of
        # the three that the chapter states for a threat derived here.
        assert "descriptive validity" in section.lower()

        # TFIX15. The section used to assert theoretical and interpretive too.
        # Neither pairing is in the chapter, and ch.09 206-210 warns the
        # cross-mapping "must be verified against the PDF before being quoted".
        # An unfiled threat is named as unfiled rather than given a heading the
        # corpus does not support.
        assert "not yet filed" in section.lower()

    @pytest.mark.asyncio
    async def test_acknowledgement_reaches_the_report(self, db_session) -> None:
        """The whole point: what the researcher wrote must be published.

        A lone researcher is compelled by the gate to write this. If it does
        not appear in the report, the platform has extracted a disclosure and
        thrown it away.
        """
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)
        await address_threat(
            study_id,
            ValidityThreatId.TV7,
            db_session,
            acknowledgement="No second reviewer was available; the bias is accepted.",
        )

        section = await build_threats_section(study_id, db_session)

        assert "No second reviewer was available; the bias is accepted." in section

    @pytest.mark.asyncio
    async def test_mitigation_reaches_the_report(self, db_session) -> None:
        """Both step-4 outcomes are published, not just one."""
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)
        await address_threat(
            study_id,
            ValidityThreatId.TV13_4,
            db_session,
            mitigation="A supervisor cross-checked a random sample of 30 extractions.",
        )

        section = await build_threats_section(study_id, db_session)

        assert "A supervisor cross-checked a random sample of 30 extractions." in section

    @pytest.mark.asyncio
    async def test_unmitigated_threats_are_labelled_as_such(self, db_session) -> None:
        """An acknowledgement must read as an acknowledgement, not a mitigation.

        Collapsing the two would let a reader take "accepted, not mitigated"
        for "handled" — which is the misreading ch.09's step 4 exists to stop.
        """
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)
        await address_threat(
            study_id, ValidityThreatId.TV7, db_session, acknowledgement="Accepted deliberately."
        )

        section = await build_threats_section(study_id, db_session)

        assert "not fully mitigated" in section.lower()

    @pytest.mark.asyncio
    async def test_section_does_not_claim_catalogue_completeness(self, db_session) -> None:
        """The platform derives 3 of ~22 entries, so it must not imply step 3.

        Ampatzoglou's step 3 is "check every threat for whether it pertains to
        the study". The platform does not do that, and a report that listed
        three threats without saying so would overstate what was checked.
        """
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 1)
        await sync_derived_threats(study_id, db_session)

        section = await build_threats_section(study_id, db_session)

        assert "automatically" in section.lower()

    @pytest.mark.asyncio
    async def test_no_threats_says_so_without_inventing_any(self, db_session) -> None:
        """A study with no derived threats must not get a canned threat list.

        The SLR report previously asserted "inter-rater variability during
        screening" for every study — false for a single-reviewer study, which
        has exactly one rater and no inter-rater variability at all.
        """
        study_id = await _make_study(db_session)
        await _add_human_reviewers(db_session, study_id, 2)
        await sync_derived_threats(study_id, db_session)

        section = await build_threats_section(study_id, db_session)

        assert "inter-rater variability" not in section.lower()
        assert "publication bias" not in section.lower()
        assert section.strip() != ""
