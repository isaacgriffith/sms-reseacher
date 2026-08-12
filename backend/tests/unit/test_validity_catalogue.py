"""Unit tests for the Ampatzoglou catalogue (TFIX15 part 1).

These tests exist to stop the catalogue drifting away from
`09-threats-to-validity.md`. They assert **fidelity to the chapter**, not
internal consistency — a catalogue can be perfectly self-consistent and still
describe a taxonomy nobody published, which is the failure TFIX13 deleted a
component for.

The count assertions matter more than they look. ch.09 40 quotes the source as
"34 distinct named threats", while the chapter's own tables yield 33 assessable
entries. ch.09 43-46 explains why — the source duplicates the labels "TV1.3"
and "TV15", and the chapter follows its checklist instead "which is internally
consistent". A future reader who spots 33-vs-34 must not reconcile it by
inventing a ``TV22_1``.
"""

from __future__ import annotations

import pytest
from db.models.validity import ValidityCategory, ValidityThreatId

from backend.services.validity_catalogue import (
    ASSESSABLE,
    BY_ID,
    CATALOGUE,
    Derivation,
    ThreatPhase,
)

_GROUPS = {
    ValidityThreatId.TV1,
    ValidityThreatId.TV8,
    ValidityThreatId.TV13,
    ValidityThreatId.TV15,
    ValidityThreatId.TV18,
    ValidityThreatId.TV22,
}


def test_every_enum_member_is_in_the_catalogue():
    """A member with no definition would be a threat nothing can describe."""
    assert {d.threat_id for d in CATALOGUE} == set(ValidityThreatId)


def test_catalogue_has_no_duplicate_entries():
    """The source duplicates two labels (ch.09 43-46); the catalogue must not."""
    ids = [d.threat_id for d in CATALOGUE]

    assert len(ids) == len(set(ids))


def test_catalogue_carries_all_thirty_nine_table_rows():
    """The chapter's three tables list 39 rows in total."""
    assert len(CATALOGUE) == 39


def test_thirty_three_entries_are_assessable():
    """39 rows minus the six group umbrellas.

    ch.09 40 says "34 distinct named threats" — that figure comes from the
    source, whose labelling ch.09 43-46 records as internally inconsistent. The
    chapter's tables are the reconciled version and give 33. Do not add a
    ``TV22_1`` to make this 34.
    """
    assert len(ASSESSABLE) == 33


def test_the_six_group_umbrellas_are_marked_as_groups():
    """Groups organise their children; they are not separately assessable."""
    groups = {d.threat_id for d in CATALOGUE if d.derivation is Derivation.GROUP}

    assert groups == _GROUPS


def test_every_sub_threat_points_at_a_real_group():
    """A parent that is not itself a group would make the tree incoherent."""
    for definition in CATALOGUE:
        if definition.parent is not None:
            assert definition.parent in _GROUPS


def test_group_entries_have_no_parent():
    """No group is nested inside another in the chapter's tables."""
    for definition in CATALOGUE:
        if definition.derivation is Derivation.GROUP:
            assert definition.parent is None


def test_the_three_phases_match_the_chapter_ranges():
    """TV1–TV7 selection, TV8–TV16 data, TV17–TV22 research."""
    assert BY_ID[ValidityThreatId.TV7].phase is ThreatPhase.STUDY_SELECTION
    assert BY_ID[ValidityThreatId.TV8].phase is ThreatPhase.DATA
    assert BY_ID[ValidityThreatId.TV16].phase is ThreatPhase.DATA
    assert BY_ID[ValidityThreatId.TV17].phase is ThreatPhase.RESEARCH


# ---------------------------------------------------------------------------
# Reporting categories — the part most at risk of being invented
# ---------------------------------------------------------------------------


def test_tv1_2_is_theoretical():
    """ch.09 220-221 states this pairing outright."""
    assert BY_ID[ValidityThreatId.TV1_2].reporting_category is ValidityCategory.THEORETICAL


def test_tv1_2_pairing_is_not_extended_to_its_siblings():
    """The chapter pairs TV1.2, not the TV1 group.

    Extending it to TV1.1/TV1.3/TV1.4/TV1.5 would assert four mappings ch.09
    does not make, under a caveat (206-210) saying the cross-mapping must be
    checked against the PDF first.
    """
    for sibling in (
        ValidityThreatId.TV1_1,
        ValidityThreatId.TV1_3,
        ValidityThreatId.TV1_4,
        ValidityThreatId.TV1_5,
    ):
        assert BY_ID[sibling].reporting_category is None


def test_tv13_family_is_descriptive():
    """ch.09 222 files TV13 under descriptive validity; sub-threats are TV13."""
    for member in (
        ValidityThreatId.TV13,
        ValidityThreatId.TV13_1,
        ValidityThreatId.TV13_2,
        ValidityThreatId.TV13_3,
        ValidityThreatId.TV13_4,
        ValidityThreatId.TV13_5,
    ):
        assert BY_ID[member].reporting_category is ValidityCategory.DESCRIPTIVE


def test_tv22_2_is_external_generalizability():
    """ch.09 223 says "generalizability"; TV22.2's own wording picks external."""
    assert (
        BY_ID[ValidityThreatId.TV22_2].reporting_category
        is ValidityCategory.GENERALIZABILITY_EXTERNAL
    )


def test_no_category_is_asserted_without_a_recorded_source():
    """Every category must name the chapter text that licenses it.

    This is the test that stops the catalogue growing a mapping by inference.
    """
    for definition in CATALOGUE:
        if definition.reporting_category is not None:
            assert definition.category_source, definition.threat_id


def test_most_entries_have_no_reporting_category():
    """ch.09 supplies three pairings, not thirty-three.

    If this ever fails because categories were filled in, the fix is to check
    Ampatzoglou's Tables IV and V against the PDF (ch.09 206-210) and cite it —
    not to relax the test.
    """
    uncategorised = [d for d in CATALOGUE if d.reporting_category is None]

    assert len(uncategorised) > len(CATALOGUE) / 2


# ---------------------------------------------------------------------------
# Derivation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "threat_id",
    [
        ValidityThreatId.TV1_2,
        ValidityThreatId.TV1_3,
        ValidityThreatId.TV7,
        ValidityThreatId.TV13_2,
        ValidityThreatId.TV13_4,
        ValidityThreatId.TV13_5,
        ValidityThreatId.TV16,
    ],
)
def test_entries_with_a_chapter_conditional_are_derived(threat_id: ValidityThreatId):
    """Each of these has an explicit rule in ch.09 that decides applicability.

    TV1.2/TV1.3 by the mutual-exclusivity rule (85-88); TV13.2 "only relevant
    where primary-study quality is evaluated" (107); TV13.5 "mostly a
    mapping-study threat" (110); TV7/TV13.4/TV16 by reviewer count, per TFIX11.
    """
    assert BY_ID[threat_id].derivation is Derivation.DERIVED


def test_threats_needing_domain_knowledge_are_asked_not_derived():
    """TV3 depends on whether another-language communities are active.

    ch.09 62 makes it conditional on something no configuration holds, so
    deriving it would be guessing.
    """
    assert BY_ID[ValidityThreatId.TV3].derivation is Derivation.ASK


def test_most_of_the_catalogue_is_asked():
    """Step 3 covers every threat; the platform can only compute a few.

    A catalogue that claimed to derive most of 33 would be overclaiming.
    """
    asked = [d for d in ASSESSABLE if d.derivation is Derivation.ASK]

    assert len(asked) > len(ASSESSABLE) / 2


def test_no_group_is_marked_derived_or_ask():
    """Applicability is a property of the named threat, not its umbrella."""
    for definition in CATALOGUE:
        if definition.threat_id in _GROUPS:
            assert definition.derivation is Derivation.GROUP


def test_every_entry_describes_what_goes_wrong():
    """A catalogue row with no description cannot be checked by a human."""
    for definition in CATALOGUE:
        assert definition.label.strip(), definition.threat_id
        assert definition.what_goes_wrong.strip(), definition.threat_id
