"""database_search_and_retrieval

Revision ID: 0014
Revises: 0013
Create Date: 2026-03-17 00:00:00.000000

Feature 006 schema additions:

1. New PostgreSQL enum types:
   - ``databaseindex`` — academic database index identifiers.
   - ``integrationtype`` — service types for credential storage.
   - ``teststatus`` — connectivity test result states.
   - ``fulltextsource`` — provenance of retrieved full-text content.

2. New tables:
   - ``study_database_selection`` — per-study toggle for each database index.
   - ``search_integration_credential`` — encrypted API key storage per integration.

3. New columns on ``paper``:
   - ``full_text_markdown`` (TEXT, nullable) — MarkItDown-converted paper content.
   - ``full_text_source`` (VARCHAR(20), nullable) — FullTextSource enum value.
   - ``full_text_converted_at`` (TIMESTAMPTZ, nullable) — conversion timestamp.

Downgrade restores the pre-006 state by dropping the new tables, removing the
new columns from ``paper``, and dropping the new enum types.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "0014"
down_revision: str = "0013"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

# Enum type definitions — created explicitly so they survive table drops.
_databaseindex_enum = postgresql.ENUM(
    "ieee_xplore",
    "acm_dl",
    "scopus",
    "web_of_science",
    "inspec",
    "science_direct",
    "springer_link",
    "google_scholar",
    "semantic_scholar",
    name="databaseindex",
    create_type=False,
)
_integrationtype_enum = postgresql.ENUM(
    "ieee_xplore",
    "elsevier",
    "web_of_science",
    "springer_nature",
    "semantic_scholar",
    "unpaywall",
    "google_scholar",
    name="integrationtype",
    create_type=False,
)
_teststatus_enum = postgresql.ENUM(
    "success",
    "rate_limited",
    "auth_failed",
    "unreachable",
    "untested",
    name="teststatus",
    create_type=False,
)


def upgrade() -> None:
    """Apply feature 006 schema additions.

    Creates enum types first so column definitions can reference them, then
    creates the two new tables, then adds the new columns to ``paper``.
    """
    # 1. Create enum types
    _databaseindex_enum.create(op.get_bind(), checkfirst=True)
    _integrationtype_enum.create(op.get_bind(), checkfirst=True)
    _teststatus_enum.create(op.get_bind(), checkfirst=True)

    # 2. study_database_selection
    op.create_table(
        "study_database_selection",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("database_index", _databaseindex_enum, nullable=False),
        sa.Column(
            "is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")
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
            ["study_id"], ["study.id"], ondelete="CASCADE", name="fk_study_database_selection_study"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "study_id", "database_index", name="uq_study_database_selection"
        ),
    )
    op.create_index(
        "ix_study_database_selection_study_id",
        "study_database_selection",
        ["study_id"],
    )

    # 3. search_integration_credential
    op.create_table(
        "search_integration_credential",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("integration_type", _integrationtype_enum, nullable=False),
        sa.Column("api_key_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column("auxiliary_token_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column("config_json_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_test_status", _teststatus_enum, nullable=True),
        sa.Column("version_id", sa.Integer(), nullable=False, server_default=sa.text("0")),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("integration_type", name="uq_search_integration_credential_type"),
    )

    # 4. New columns on paper
    with op.batch_alter_table("paper", schema=None) as batch_op:
        batch_op.add_column(sa.Column("full_text_markdown", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "full_text_source",
                sa.String(length=20),
                nullable=True,
                comment="FullTextSource enum value: unpaywall|direct|scihub|unavailable|pending",
            )
        )
        batch_op.add_column(
            sa.Column("full_text_converted_at", sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    """Revert feature 006 schema additions.

    Removes the new columns from ``paper``, drops both new tables, then drops
    the new enum types.
    """
    # 1. Remove new columns from paper
    with op.batch_alter_table("paper", schema=None) as batch_op:
        batch_op.drop_column("full_text_converted_at")
        batch_op.drop_column("full_text_source")
        batch_op.drop_column("full_text_markdown")

    # 2. Drop tables (index dropped automatically with the table)
    op.drop_table("search_integration_credential")
    op.drop_index(
        "ix_study_database_selection_study_id", table_name="study_database_selection"
    )
    op.drop_table("study_database_selection")

    # 3. Drop enum types
    _teststatus_enum.drop(op.get_bind(), checkfirst=True)
    _integrationtype_enum.drop(op.get_bind(), checkfirst=True)
    _databaseindex_enum.drop(op.get_bind(), checkfirst=True)
