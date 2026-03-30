"""tertiary_studies_workflow

Revision ID: 0017
Revises: 0016
Create Date: 2026-03-29 00:00:00.000000

Feature 009 schema additions:

1. New PostgreSQL enum types:
   - ``tertiary_protocol_status_enum`` — Tertiary protocol lifecycle states.
   - ``secondary_study_type_enum`` — type labels for included secondary studies.

2. New tables (in dependency order):
   - ``tertiary_study_protocol`` — one protocol per Tertiary Study.
   - ``secondary_study_seed_import`` — seed import audit records.
   - ``tertiary_data_extraction`` — secondary-study-specific extraction fields.

3. Extension to existing table:
   - Adds nullable ``source_seed_import_id`` FK column to ``candidate_paper``,
     linking papers introduced via seed import to the import audit record.

Downgrade reverses all steps in reverse order.  The two new enum types are
dropped; the existing ``synthesis_approach_enum`` and
``extraction_status_enum`` are referenced but never created/dropped here.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision: str = "0017"
down_revision: str = "0016"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

# ---------------------------------------------------------------------------
# New enum type definitions.
# ---------------------------------------------------------------------------

_tertiary_protocol_status_enum = postgresql.ENUM(
    "draft",
    "validated",
    name="tertiary_protocol_status_enum",
    create_type=False,
)

_secondary_study_type_enum = postgresql.ENUM(
    "SLR",
    "SMS",
    "RAPID_REVIEW",
    "UNKNOWN",
    name="secondary_study_type_enum",
    create_type=False,
)

# Existing enum types referenced but NOT created/dropped in this migration.
_synthesis_approach_enum = postgresql.ENUM(
    "meta_analysis",
    "descriptive",
    "qualitative",
    name="synthesis_approach_enum",
    create_type=False,
)
_extraction_status_enum = postgresql.ENUM(
    "pending",
    "ai_complete",
    "validated",
    "human_reviewed",
    name="extraction_status_enum",
    create_type=False,
)


def upgrade() -> None:
    """Apply feature 009 Tertiary Studies Workflow schema additions.

    Creates two new enum types, three new tables in dependency order, and
    adds one nullable FK column to ``candidate_paper``.
    """
    # 1. Create new enum types.
    _tertiary_protocol_status_enum.create(op.get_bind(), checkfirst=True)
    _secondary_study_type_enum.create(op.get_bind(), checkfirst=True)

    # 2. tertiary_study_protocol
    op.create_table(
        "tertiary_study_protocol",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            _tertiary_protocol_status_enum,
            nullable=False,
            server_default="draft",
        ),
        sa.Column("background", sa.Text(), nullable=True),
        sa.Column("research_questions", sa.JSON(), nullable=True),
        sa.Column("secondary_study_types", sa.JSON(), nullable=True),
        sa.Column("inclusion_criteria", sa.JSON(), nullable=True),
        sa.Column("exclusion_criteria", sa.JSON(), nullable=True),
        sa.Column("recency_cutoff_year", sa.Integer(), nullable=True),
        sa.Column("search_strategy", sa.Text(), nullable=True),
        sa.Column("quality_threshold", sa.Float(), nullable=True),
        sa.Column("synthesis_approach", _synthesis_approach_enum, nullable=True),
        sa.Column("dissemination_strategy", sa.Text(), nullable=True),
        sa.Column(
            "version_id",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["study_id"],
            ["study.id"],
            ondelete="CASCADE",
            name="fk_tertiary_protocol_study",
        ),
        sa.UniqueConstraint("study_id", name="uq_tertiary_protocol_study"),
    )
    op.create_index(
        "ix_tertiary_study_protocol_study_id",
        "tertiary_study_protocol",
        ["study_id"],
    )

    # 3. secondary_study_seed_import
    op.create_table(
        "secondary_study_seed_import",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("target_study_id", sa.Integer(), nullable=False),
        sa.Column("source_study_id", sa.Integer(), nullable=False),
        sa.Column(
            "imported_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "records_added",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "records_skipped",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("imported_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["target_study_id"],
            ["study.id"],
            ondelete="CASCADE",
            name="fk_seed_import_target_study",
        ),
        sa.ForeignKeyConstraint(
            ["source_study_id"],
            ["study.id"],
            ondelete="RESTRICT",
            name="fk_seed_import_source_study",
        ),
        sa.ForeignKeyConstraint(
            ["imported_by_user_id"],
            ["user.id"],
            ondelete="SET NULL",
            name="fk_seed_import_user",
        ),
    )
    op.create_index(
        "ix_secondary_study_seed_import_target_study_id",
        "secondary_study_seed_import",
        ["target_study_id"],
    )
    op.create_index(
        "ix_secondary_study_seed_import_source_study_id",
        "secondary_study_seed_import",
        ["source_study_id"],
    )

    # 4. tertiary_data_extraction
    op.create_table(
        "tertiary_data_extraction",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("candidate_paper_id", sa.Integer(), nullable=False),
        sa.Column("secondary_study_type", _secondary_study_type_enum, nullable=True),
        sa.Column("research_questions_addressed", sa.JSON(), nullable=True),
        sa.Column("databases_searched", sa.JSON(), nullable=True),
        sa.Column("study_period_start", sa.Integer(), nullable=True),
        sa.Column("study_period_end", sa.Integer(), nullable=True),
        sa.Column("primary_study_count", sa.Integer(), nullable=True),
        sa.Column("synthesis_approach_used", sa.Text(), nullable=True),
        sa.Column("key_findings", sa.Text(), nullable=True),
        sa.Column("research_gaps", sa.Text(), nullable=True),
        sa.Column("reviewer_quality_rating", sa.Float(), nullable=True),
        sa.Column(
            "extraction_status",
            _extraction_status_enum,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("extracted_by_agent", sa.String(256), nullable=True),
        sa.Column("validated_by_reviewer_id", sa.Integer(), nullable=True),
        sa.Column(
            "version_id",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["candidate_paper_id"],
            ["candidate_paper.id"],
            ondelete="CASCADE",
            name="fk_tertiary_extraction_candidate_paper",
        ),
        sa.ForeignKeyConstraint(
            ["validated_by_reviewer_id"],
            ["user.id"],
            ondelete="SET NULL",
            name="fk_tertiary_extraction_reviewer",
        ),
        sa.UniqueConstraint(
            "candidate_paper_id",
            name="uq_tertiary_extraction_candidate_paper",
        ),
    )
    op.create_index(
        "ix_tertiary_data_extraction_candidate_paper_id",
        "tertiary_data_extraction",
        ["candidate_paper_id"],
    )

    # 5. Extend synthesis_approach_enum with tertiary synthesis approaches.
    #    ADD VALUE IF NOT EXISTS is safe to run even if the values already exist.
    op.execute("ALTER TYPE synthesis_approach_enum ADD VALUE IF NOT EXISTS 'narrative'")
    op.execute("ALTER TYPE synthesis_approach_enum ADD VALUE IF NOT EXISTS 'thematic'")

    # 6. Add source_seed_import_id column to candidate_paper.
    op.add_column(
        "candidate_paper",
        sa.Column(
            "source_seed_import_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_candidate_paper_seed_import",
        "candidate_paper",
        "secondary_study_seed_import",
        ["source_seed_import_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_candidate_paper_source_seed_import_id",
        "candidate_paper",
        ["source_seed_import_id"],
    )


def downgrade() -> None:
    """Reverse feature 009 Tertiary Studies Workflow schema additions.

    Drops the new column, tables, and enum types in reverse dependency order.

    Note: The ``narrative`` and ``thematic`` values added to
    ``synthesis_approach_enum`` cannot be removed from a PostgreSQL ENUM
    type via ``ALTER TYPE ... DROP VALUE`` (not supported). Those values
    remain in the type but are harmless since no rows reference them after
    downgrade.
    """
    # Remove the column added to candidate_paper.
    op.drop_index(
        "ix_candidate_paper_source_seed_import_id",
        table_name="candidate_paper",
    )
    op.drop_constraint(
        "fk_candidate_paper_seed_import",
        "candidate_paper",
        type_="foreignkey",
    )
    op.drop_column("candidate_paper", "source_seed_import_id")

    # Drop new tables in reverse dependency order.
    op.drop_index(
        "ix_tertiary_data_extraction_candidate_paper_id",
        table_name="tertiary_data_extraction",
    )
    op.drop_table("tertiary_data_extraction")

    op.drop_index(
        "ix_secondary_study_seed_import_source_study_id",
        table_name="secondary_study_seed_import",
    )
    op.drop_index(
        "ix_secondary_study_seed_import_target_study_id",
        table_name="secondary_study_seed_import",
    )
    op.drop_table("secondary_study_seed_import")

    op.drop_index(
        "ix_tertiary_study_protocol_study_id",
        table_name="tertiary_study_protocol",
    )
    op.drop_table("tertiary_study_protocol")

    # Drop the two new enum types.
    _secondary_study_type_enum.drop(op.get_bind(), checkfirst=True)
    _tertiary_protocol_status_enum.drop(op.get_bind(), checkfirst=True)
