"""Add the study-generic threats-to-validity table (TFIX11).

``docs/methodology/09-threats-to-validity.md`` assigns different frameworks to
different study types: Rapid Reviews use Cartaxo's disclosure regime, already
stored in ``rr_threat_to_validity``, while SLR, SMS and Tertiary use
Ampatzoglou's catalogue.  This table is the second of those two — it does not
replace or migrate the first, and the two coexist deliberately.

**Why a new table rather than widening ``rr_threat_to_validity``.**  Its
``rr_threat_type_enum`` members (``year_range``, ``language``, ``qa_skipped``)
are *methodological concessions* in Cartaxo's sense.  Ampatzoglou's TV-numbered
catalogue entries are a different vocabulary answering a different question, and
folding both into one enum would erase a distinction the chapter is explicit
about.

**``mitigation`` and ``acknowledgement`` are the point of the table.**
Ampatzoglou's step 4 requires that every identified threat carry one or the
other, and the chapter calls a threat with neither "an incomplete study".
``rr_threat_to_validity`` has no such column, so a report gate could not be
built over it.  Either column satisfies the requirement; neither outranks the
other, because a lone researcher who cannot mitigate must still be able to
finish by acknowledging.

**``is_applicable`` rather than deleting rows.**  Applicability is derived from
configuration and genuinely changes mid-study — human ``reviewer`` rows are
created lazily the first time a member records a decision, so a study can cross
from one reviewer to two long after screening starts.  Deleting on that
transition would discard whatever the researcher had already written; if they
later drop back to one reviewer, the text would be gone for good.

Revision ID: 0022
Revises: 0021
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0022"
down_revision: str = "0021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the study_validity_threat table and its two enums."""
    threat_id_enum = sa.Enum(
        "tv7",
        "tv13_4",
        "tv16",
        name="validity_threat_id_enum",
    )
    validity_category_enum = sa.Enum(
        "descriptive",
        "theoretical",
        "generalizability_internal",
        "generalizability_external",
        "interpretive",
        "repeatability",
        name="validity_category_enum",
    )

    bind = op.get_bind()
    threat_id_enum.create(bind, checkfirst=True)
    validity_category_enum.create(bind, checkfirst=True)

    op.create_table(
        "study_validity_threat",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("threat_id", threat_id_enum, nullable=False),
        sa.Column("validity_category", validity_category_enum, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "source_detail",
            sa.String(length=500),
            nullable=True,
            comment="What in the configuration produced this threat, e.g. '1 human reviewer'",
        ),
        sa.Column(
            "mitigation",
            sa.Text(),
            nullable=True,
            comment="Step 4, first outcome: an action taken to reduce the threat",
        ),
        sa.Column(
            "acknowledgement",
            sa.Text(),
            nullable=True,
            comment="Step 4, second outcome: the threat is accepted and not (fully) mitigated",
        ),
        sa.Column(
            "is_applicable",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
            comment="False once the configuration that derived this threat no longer holds",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        # Re-derivation runs whenever the threat list is read, so without this
        # a single-reviewer study would gain a duplicate TV7 on every page load.
        sa.UniqueConstraint("study_id", "threat_id", name="uq_study_validity_threat"),
    )
    op.create_index(
        op.f("ix_study_validity_threat_study_id"),
        "study_validity_threat",
        ["study_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the table, its index, and both enums."""
    op.drop_index(op.f("ix_study_validity_threat_study_id"), table_name="study_validity_threat")
    op.drop_table("study_validity_threat")

    bind = op.get_bind()
    sa.Enum(name="validity_category_enum").drop(bind, checkfirst=True)
    sa.Enum(name="validity_threat_id_enum").drop(bind, checkfirst=True)
