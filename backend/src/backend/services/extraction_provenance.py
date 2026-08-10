"""Appraisal provenance for extraction-derived figures (TFIX14).

Every figure this platform derives from extractions — charts, the validity
snapshot, the export archive — was previously computed over ``ai_complete``,
``validated`` and ``human_reviewed`` rows alike, with nothing in the output
saying which was which. A study that AI-extracted 200 papers and had 12 checked
produced numbers indistinguishable from one that checked all 200.

The corpus does not answer this by exclusion:

- `01-slr.md` 266-270 — Kitchenham et al. distrust automatic extraction of
  results, but the caveat "does not forbid automation; it forbids extraction
  **decoupled from appraisal**". Making the appraisal state visible in the
  output is what re-couples them.
- `08-extraction-and-synthesis.md` 89-90 — unresolvable uncertainty is pushed
  into sensitivity analysis or the trustworthiness evaluation "**rather than
  silently resolved**". Dropping the unappraised rows would resolve it silently
  in the other direction, and lose the data besides.
- `08-extraction-and-synthesis.md` 461-463 — sensitivity analysis repeats over
  subsets, and names this exact one: "studies where extraction was
  unproblematic".

So this module carries the denominators rather than filtering on them. Actually
recomputing each figure over the appraised subset and reporting whether the
conclusion moves is the stronger treatment that chapter requires, and is tracked
separately as gap **G64**; the counts here are its precondition.

@module extraction_provenance
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sqlalchemy.ext.asyncio import AsyncSession


def _status_values(names: tuple[str, ...]) -> tuple[Any, ...]:
    """Resolve status names to ``ExtractionStatus`` members.

    Imported lazily so this module stays importable in contexts where the ``db``
    package is not installed, matching the pattern the jobs already use.

    Args:
        names: Enum member names to resolve.

    Returns:
        The resolved enum members.

    """
    from db.models.extraction import ExtractionStatus

    return tuple(getattr(ExtractionStatus, name) for name in names)


#: Statuses that may contribute to a reported figure at all.
REPORTABLE_STATUSES: tuple[Any, ...] = _status_values(
    ("AI_COMPLETE", "VALIDATED", "HUMAN_REVIEWED")
)

#: Statuses a human has actually stood behind.
#:
#: ``validated`` is included though nothing in ``backend/src`` assigns it — a
#: status ranked above ``human_reviewed`` must not count for *less* than the one
#: below it. Same reasoning as ``phase_gate.py`` 98-101.
APPRAISED_STATUSES: tuple[Any, ...] = _status_values(("VALIDATED", "HUMAN_REVIEWED"))

_REPORTABLE_VALUES: frozenset[str] = frozenset(s.value for s in REPORTABLE_STATUSES)
_APPRAISED_VALUES: frozenset[str] = frozenset(s.value for s in APPRAISED_STATUSES)


@dataclass(frozen=True)
class ExtractionProvenance:
    """How much of a study's reported extraction data a human has checked.

    Attributes:
        total: Reportable extractions on accepted papers.
        appraised: Of those, how many carry an appraised status.

    """

    total: int
    appraised: int

    @property
    def unappraised(self) -> int:
        """Reportable extractions no human has signed off.

        Clamped at zero so a malformed pair can never put a negative count in a
        report.
        """
        return max(self.total - self.appraised, 0)

    @property
    def is_fully_appraised(self) -> bool:
        """Whether every reported extraction was appraised.

        A study with no extractions is **not** fully appraised — vacuous truth
        would read to a user as "everything checked".
        """
        return self.total > 0 and self.appraised >= self.total

    def as_dict(self) -> dict[str, int | bool]:
        """Return the counts as a JSON-serialisable mapping.

        Returns:
            Both denominators plus the derived flags.

        """
        return {
            "total": self.total,
            "appraised": self.appraised,
            "unappraised": self.unappraised,
            "is_fully_appraised": self.is_fully_appraised,
        }

    def describe(self) -> str:
        """Return a sentence stating the counts, or ``""`` if nothing extracted.

        The wording deliberately avoids "complete" for unappraised rows. The
        sentence this replaces called every row "completed" regardless of
        whether a human had ever seen it.

        Returns:
            A prose summary suitable for a report section.

        """
        if self.total <= 0:
            return ""
        papers = "paper" if self.total == 1 else "papers"
        if self.is_fully_appraised:
            return (
                f"Data was extracted from {self.total} accepted {papers}, "
                "and every extraction was appraised by a reviewer."
            )
        return (
            f"Data was extracted from {self.total} accepted {papers}, of which "
            f"{self.appraised} were appraised by a reviewer and {self.unappraised} "
            "remain AI-extracted and unappraised. Figures derived from these "
            "extractions include the unappraised records."
        )


def _value_of(status: Any) -> str:
    """Return the string value of an enum member or a plain string.

    Args:
        status: An ``ExtractionStatus`` member or its raw column value.

    Returns:
        The status string.

    """
    return status.value if hasattr(status, "value") else str(status)


def from_statuses(statuses: Iterable[Any]) -> ExtractionProvenance:
    """Count appraised and total extractions from statuses already in memory.

    Callers that have already loaded their rows use this rather than issuing a
    second query — every downstream consumer this fixes was already holding the
    rows it needed.

    Args:
        statuses: ``ExtractionStatus`` members or raw status strings. Values
            outside :data:`REPORTABLE_STATUSES` are ignored.

    Returns:
        The provenance counts.

    """
    total = 0
    appraised = 0
    for status in statuses:
        value = _value_of(status)
        if value not in _REPORTABLE_VALUES:
            continue
        total += 1
        if value in _APPRAISED_VALUES:
            appraised += 1
    return ExtractionProvenance(total=total, appraised=appraised)


async def load_provenance(study_id: int, db: AsyncSession) -> ExtractionProvenance:
    """Count a study's reportable extractions without loading their payloads.

    For callers — the results API among them — that need the denominators but
    not the extraction bodies.

    Args:
        study_id: Study to count.
        db: Active async session.

    Returns:
        The provenance counts for accepted papers in that study.

    """
    from db.models.candidate import CandidatePaper, CandidatePaperStatus
    from db.models.extraction import DataExtraction
    from sqlalchemy import select

    result = await db.execute(
        select(DataExtraction.extraction_status)
        .join(CandidatePaper, CandidatePaper.id == DataExtraction.candidate_paper_id)
        .where(
            CandidatePaper.study_id == study_id,
            CandidatePaper.current_status == CandidatePaperStatus.ACCEPTED,
            DataExtraction.extraction_status.in_(REPORTABLE_STATUSES),
        )
    )
    return from_statuses(result.scalars().all())
