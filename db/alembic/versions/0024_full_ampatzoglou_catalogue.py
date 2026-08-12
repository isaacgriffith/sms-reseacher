"""Encode the full Ampatzoglou TV1–TV22 catalogue (TFIX15 part 1).

``study_validity_threat`` held three catalogue entries, which made
Ampatzoglou's **step 3** — "check every threat for whether it pertains to the
study" (`09-threats-to-validity.md` 169) — impossible to perform: 30 threats
were never presented, so they were never checked. This migration widens the
catalogue enum to the chapter's full tables and adds the two columns step 3
needs to be answerable.

**Why ``is_applicable`` becomes nullable.**  Step 3 is a *check*, and a check
needs three outcomes, not two: applicable, checked-and-ruled-out, and not yet
looked at.  The previous ``NOT NULL DEFAULT true`` column could not tell an
unexamined threat from one a researcher had deliberately dismissed, so a study
could not report how much of step 3 it had actually done.

**Why ``applicability_is_derived`` is added.**  The chapter wants threats
"derived from the protocol configuration rather than presented as a flat
checklist" (90-92), but only some entries have a rule behind them.  This column
records which answers the platform computed and which a human gave, so
re-derivation cannot silently overwrite a researcher's judgement.

**Why ``validity_category`` becomes nullable.**  ch.09 220-223 supplies exactly
three worked Ampatzoglou→Petersen pairings, and 206-210 warns that the rest of
the cross-mapping "must be verified against the PDF before being quoted"
because the source's Tables IV and V "were displaced by one row in text
extraction".  Filing the other threats from inference would manufacture a
mapping the corpus does not contain, so the column is left empty until a
researcher files it — consistent with ch.09 217-218, which describes Petersen &
Gencel as the *reporting* taxonomy.

That reasoning applies retroactively to two rows already written.  ``tv7`` was
filed under theoretical validity and ``tv16`` under interpretive; neither
pairing appears in the chapter, and the ``tv16`` one was already flagged in
code as an inference when it was written.  Both are set to NULL here.
``tv13_4`` keeps ``descriptive``, which ch.09 222 does state.

Revision ID: 0024
Revises: 0023
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0024"
down_revision: str = "0023"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: Catalogue members added by this migration.  ``tv7``, ``tv13_4`` and ``tv16``
#: already exist and are deliberately absent.
_ADDED_THREAT_IDS: tuple[str, ...] = (
    "tv1",
    "tv1_1",
    "tv1_2",
    "tv1_3",
    "tv1_4",
    "tv1_5",
    "tv2",
    "tv3",
    "tv4",
    "tv5",
    "tv6",
    "tv8",
    "tv8_1",
    "tv8_2",
    "tv9",
    "tv10",
    "tv11",
    "tv12",
    "tv13",
    "tv13_1",
    "tv13_2",
    "tv13_3",
    "tv13_5",
    "tv14",
    "tv15",
    "tv15_1",
    "tv15_2",
    "tv17",
    "tv18",
    "tv18_1",
    "tv18_2",
    "tv19",
    "tv20",
    "tv21",
    "tv22",
    "tv22_2",
)

#: The three members that existed before this migration.
_ORIGINAL_THREAT_IDS: tuple[str, ...] = ("tv7", "tv13_4", "tv16")

#: Categories the chapter does *not* source, cleared from existing rows.
_UNSOURCED_CATEGORY_ROWS: tuple[str, ...] = ("tv7", "tv16")


def upgrade() -> None:
    """Widen the catalogue enum and make step 3 answerable."""
    for member in _ADDED_THREAT_IDS:
        op.execute(f"ALTER TYPE validity_threat_id_enum ADD VALUE IF NOT EXISTS '{member}'")

    # PostgreSQL forbids using an enum value added in the same transaction.
    op.execute("COMMIT")

    op.alter_column("study_validity_threat", "validity_category", nullable=True)
    op.alter_column("study_validity_threat", "is_applicable", nullable=True)
    op.alter_column("study_validity_threat", "is_applicable", server_default=None)

    op.add_column(
        "study_validity_threat",
        sa.Column(
            "applicability_is_derived",
            sa.Boolean(),
            nullable=False,
            server_default="0",
        ),
    )

    # Every row written before this migration came from a derivation rule.
    op.execute("UPDATE study_validity_threat SET applicability_is_derived = true")

    unsourced = ", ".join(f"'{t}'" for t in _UNSOURCED_CATEGORY_ROWS)
    op.execute(
        "UPDATE study_validity_threat SET validity_category = NULL "
        f"WHERE threat_id IN ({unsourced})"
    )


def downgrade() -> None:
    """Restore the three-entry catalogue and the two-valued applicability flag.

    Rows outside the original three are removed first: PostgreSQL will not cast
    the column to a type lacking a value still in use.  The ``validity_category``
    values cleared by :func:`upgrade` are not restored — they were never
    sourced, and rewriting them would re-assert a mapping the chapter does not
    make.
    """
    original = ", ".join(f"'{t}'" for t in _ORIGINAL_THREAT_IDS)
    op.execute(f"DELETE FROM study_validity_threat WHERE threat_id NOT IN ({original})")

    op.drop_column("study_validity_threat", "applicability_is_derived")

    # NOT NULL cannot be restored while rows hold the "not yet checked" state
    # this migration introduced; treat unchecked as applicable, which is what
    # the old default meant.
    op.execute("UPDATE study_validity_threat SET is_applicable = true WHERE is_applicable IS NULL")
    op.alter_column("study_validity_threat", "is_applicable", server_default="1")
    op.alter_column("study_validity_threat", "is_applicable", nullable=False)

    op.execute(
        "UPDATE study_validity_threat SET validity_category = 'descriptive' "
        "WHERE validity_category IS NULL"
    )
    op.alter_column("study_validity_threat", "validity_category", nullable=False)

    threat_ids = ", ".join(f"'{t}'" for t in _ORIGINAL_THREAT_IDS)
    op.execute("ALTER TYPE validity_threat_id_enum RENAME TO validity_threat_id_enum_old")
    op.execute(f"CREATE TYPE validity_threat_id_enum AS ENUM ({threat_ids})")
    op.execute(
        "ALTER TABLE study_validity_threat "
        "ALTER COLUMN threat_id TYPE validity_threat_id_enum "
        "USING threat_id::text::validity_threat_id_enum"
    )
    op.execute("DROP TYPE validity_threat_id_enum_old")
