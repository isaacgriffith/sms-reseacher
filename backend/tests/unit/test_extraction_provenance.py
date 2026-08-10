"""Unit tests for extraction appraisal provenance (TFIX14).

The defect these guard against is not that unappraised extractions are used —
`01-slr.md` 269-270 is explicit that the caveat "does not forbid automation; it
forbids extraction **decoupled from appraisal**". The defect is that the
appraisal state was invisible downstream, so a study with 200 AI extractions and
12 checked ones reported figures indistinguishable from 200 checked ones.

`08-extraction-and-synthesis.md` 461-463 names this exact subset — "studies
where extraction was unproblematic" — as a sensitivity-analysis dimension, and
89-90 requires uncertainty to be surfaced "rather than silently resolved".
Excluding the unappraised rows would also be a silent resolution, which is why
these tests assert the counts are *carried*, not filtered.
"""

from __future__ import annotations

import pytest

from backend.services.extraction_provenance import (
    APPRAISED_STATUSES,
    REPORTABLE_STATUSES,
    ExtractionProvenance,
    from_statuses,
)


class _Status:
    """Minimal stand-in carrying the ``.value`` an ExtractionStatus exposes."""

    def __init__(self, value: str) -> None:
        self.value = value


def test_reportable_statuses_include_ai_complete():
    """AI-extracted rows stay reportable — the corpus forbids silent exclusion.

    `08-extraction-and-synthesis.md` 89-90: uncertainty is pushed to sensitivity
    analysis "rather than silently resolved". Dropping the rows resolves it
    silently in the other direction.
    """
    values = {s.value for s in REPORTABLE_STATUSES}

    assert "ai_complete" in values
    assert "validated" in values
    assert "human_reviewed" in values


def test_appraised_statuses_exclude_ai_complete():
    """Only human-touched statuses count as appraised."""
    values = {s.value for s in APPRAISED_STATUSES}

    assert "ai_complete" not in values
    assert values == {"validated", "human_reviewed"}


def test_from_statuses_counts_appraised_and_total():
    """A mixed set reports both denominators."""
    statuses = [_Status("ai_complete")] * 188 + [_Status("human_reviewed")] * 12

    provenance = from_statuses(statuses)

    assert provenance.total == 200
    assert provenance.appraised == 12
    assert provenance.unappraised == 188


def test_from_statuses_treats_validated_as_appraised():
    """`validated` ranks above `human_reviewed` and must not count for less.

    Mirrors the reasoning already recorded in `phase_gate.py` 98-101.
    """
    provenance = from_statuses([_Status("validated"), _Status("ai_complete")])

    assert provenance.appraised == 1
    assert provenance.total == 2


def test_from_statuses_accepts_plain_strings():
    """Callers holding raw column values need not import the enum."""
    provenance = from_statuses(["ai_complete", "human_reviewed"])

    assert provenance.total == 2
    assert provenance.appraised == 1


def test_from_statuses_ignores_unreportable_statuses():
    """Pending and in-progress rows are not part of any reported figure."""
    provenance = from_statuses([_Status("pending"), _Status("ai_complete")])

    assert provenance.total == 1
    assert provenance.appraised == 0


def test_empty_provenance_is_not_fully_appraised():
    """Zero extractions must not read as "everything checked"."""
    provenance = from_statuses([])

    assert provenance.total == 0
    assert provenance.is_fully_appraised is False


def test_fully_appraised_when_every_row_is_checked():
    """A study that checked everything says so."""
    provenance = from_statuses([_Status("human_reviewed")] * 3)

    assert provenance.is_fully_appraised is True
    assert provenance.unappraised == 0


def test_unappraised_never_goes_negative():
    """A malformed pair must not produce a negative count in a report."""
    provenance = ExtractionProvenance(total=1, appraised=5)

    assert provenance.unappraised == 0


def test_as_dict_carries_both_denominators():
    """The export payload needs the numbers, not the prose."""
    payload = from_statuses([_Status("ai_complete"), _Status("human_reviewed")]).as_dict()

    assert payload["total"] == 2
    assert payload["appraised"] == 1
    assert payload["unappraised"] == 1
    assert payload["is_fully_appraised"] is False


def test_describe_is_empty_when_nothing_extracted():
    """No extraction means no sentence — not a sentence claiming zero."""
    assert from_statuses([]).describe() == ""


def test_describe_states_the_unappraised_remainder():
    """The prose must name the unverified remainder, not just the total.

    This is the sentence `validity_job` previously got wrong: it called every
    row "completed" regardless of whether a human had ever seen it.
    """
    text = from_statuses([_Status("ai_complete")] * 188 + [_Status("validated")] * 12).describe()

    assert "200" in text
    assert "12" in text
    assert "188" in text
    assert "unappraised" in text


def test_describe_does_not_claim_appraisal_when_none_happened():
    """A wholly AI-extracted study must not read as appraised at all."""
    text = from_statuses([_Status("ai_complete")] * 5).describe()

    assert "5" in text
    assert "unappraised" in text


def test_describe_says_so_when_everything_was_appraised():
    """The fully-checked case earns a plainly different sentence."""
    text = from_statuses([_Status("human_reviewed")] * 4).describe()

    assert "unappraised" not in text
    assert "4" in text


@pytest.mark.parametrize("total", [1, 7, 40])
def test_describe_always_names_the_total(total: int):
    """Whatever the mix, the denominator is always stated."""
    text = from_statuses([_Status("ai_complete")] * total).describe()

    assert str(total) in text
