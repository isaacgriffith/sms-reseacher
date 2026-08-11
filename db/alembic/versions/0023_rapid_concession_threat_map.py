"""Correct the Rapid Review concession-to-threat map (TFIX15 part 2).

``docs/methodology/03-rapid-review.md`` gives Cartaxo's disclosure regime: there
is no threat taxonomy, and instead "**every methodological concession is itself
a threat that must be recorded**" (287-288).  Its map has eight rows.  Two
defects against that map are corrected here.

**One row was inverted.**  The last row — narrowing criteria to the
practitioner's context — is marked "**Explicitly NOT a threat — good
practice**" (302), and the chapter's ⚙ IMPLEMENTATION note names that exception
as the thing the mapping must honour: it supplies "the full mapping, *and the
exception that must not generate a threat*".  ``_auto_create_threats`` did the
opposite, writing one ``context_restriction`` threat per entry in
``rapid_review_protocol.context_restrictions``.  A Rapid Review that scoped
itself to its practitioner's context therefore had the recommended practice
published against it under "Limitations & Threats to Validity" in the evidence
briefing (``evidence_briefing.html.j2`` 282).

**Three rows had no enum member at all.**  Title-only first screening pass →
false negatives; narrative synthesis → limited synthesis rigour; excluding
studies with missing data → missing-data exclusions.  Under a regime whose whole
content is that every concession must be recorded, a concession with nowhere to
be recorded is a hole in the regime.

**On deleting the rows.**  The information is not lost: the underlying
``rapid_review_protocol.context_restrictions`` JSON is untouched, so what the
researcher configured survives intact.  Only its miscategorisation as a threat
is removed.  Note also that no UI ever wrote ``context_restrictions`` — the
field is accepted by ``PUT /api/v1/rapid/studies/{id}/protocol`` and present in
the frontend schema, but no form populates it — so in practice the affected row
count is expected to be zero.

**Reversibility is asymmetric, deliberately.**  ``downgrade()`` restores the
enum to its previous member set exactly.  It cannot resurrect the deleted
``context_restriction`` rows, because a delete carries no undo — and
reconstructing them would mean re-asserting the very claim the chapter forbids.

Revision ID: 0023
Revises: 0022
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0023"
down_revision: str = "0022"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: Members of ``rr_threat_type_enum`` before this migration.
_PREVIOUS_MEMBERS: tuple[str, ...] = (
    "single_source",
    "year_range",
    "language",
    "geography",
    "study_design",
    "single_reviewer",
    "qa_skipped",
    "qa_simplified",
    "context_restriction",
)

#: Concessions named by ch.03's map that previously had no member.
_ADDED_MEMBERS: tuple[str, ...] = (
    "false_negatives",
    "limited_synthesis_rigour",
    "missing_data_exclusions",
)


def upgrade() -> None:
    """Add the three missing concession types and drop the inverted rows."""
    for member in _ADDED_MEMBERS:
        op.execute(f"ALTER TYPE rr_threat_type_enum ADD VALUE IF NOT EXISTS '{member}'")

    # Committed before the DELETE so the new values become usable afterwards.
    # PostgreSQL forbids using an enum value added in the same transaction.
    op.execute("COMMIT")

    op.execute("DELETE FROM rr_threat_to_validity WHERE threat_type = 'context_restriction'")


def downgrade() -> None:
    """Restore the previous enum member set.

    Rows carrying one of the three added types are removed first, because
    PostgreSQL will not cast a column to a type that lacks a value still in use.
    The ``context_restriction`` rows deleted by :func:`upgrade` are not restored
    — see the module docstring.
    """
    added = ", ".join(f"'{m}'" for m in _ADDED_MEMBERS)
    op.execute(f"DELETE FROM rr_threat_to_validity WHERE threat_type IN ({added})")

    previous = ", ".join(f"'{m}'" for m in _PREVIOUS_MEMBERS)
    op.execute("ALTER TYPE rr_threat_type_enum RENAME TO rr_threat_type_enum_old")
    op.execute(f"CREATE TYPE rr_threat_type_enum AS ENUM ({previous})")
    op.execute(
        "ALTER TABLE rr_threat_to_validity "
        "ALTER COLUMN threat_type TYPE rr_threat_type_enum "
        "USING threat_type::text::rr_threat_type_enum"
    )
    op.execute("DROP TYPE rr_threat_type_enum_old")
