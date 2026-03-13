"""Add DataExtraction and ExtractionFieldAudit tables (US5).

Revision ID: 0009
Revises: 0008
Create Date: 2026-03-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # data_extraction table
    # ------------------------------------------------------------------
    op.create_table(
        "data_extraction",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("candidate_paper_id", sa.Integer(), nullable=False),
        sa.Column(
            "research_type",
            sa.Enum(
                "evaluation",
                "solution_proposal",
                "validation",
                "philosophical",
                "opinion",
                "personal_experience",
                "unknown",
                name="research_type_enum",
            ),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column("venue_type", sa.String(128), nullable=False, server_default=""),
        sa.Column("venue_name", sa.String(512), nullable=True),
        sa.Column("author_details", sa.JSON(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("open_codings", sa.JSON(), nullable=True),
        sa.Column("keywords", sa.JSON(), nullable=True),
        sa.Column("question_data", sa.JSON(), nullable=True),
        sa.Column(
            "extraction_status",
            sa.Enum(
                "pending",
                "ai_complete",
                "validated",
                "human_reviewed",
                name="extraction_status_enum",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("version_id", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("extracted_by_agent", sa.String(255), nullable=True),
        sa.Column("validated_by_reviewer_id", sa.Integer(), nullable=True),
        sa.Column("conflict_flag", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["candidate_paper_id"], ["candidate_paper.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["validated_by_reviewer_id"], ["reviewer.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_paper_id", name="uq_data_extraction_candidate_paper"),
    )
    op.create_index(
        "ix_data_extraction_candidate_paper_id",
        "data_extraction",
        ["candidate_paper_id"],
    )

    # ------------------------------------------------------------------
    # extraction_field_audit table
    # ------------------------------------------------------------------
    op.create_table(
        "extraction_field_audit",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("extraction_id", sa.Integer(), nullable=False),
        sa.Column("field_name", sa.String(128), nullable=False),
        sa.Column("original_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("changed_by_user_id", sa.Integer(), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["extraction_id"], ["data_extraction.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["changed_by_user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_extraction_field_audit_extraction_id",
        "extraction_field_audit",
        ["extraction_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_extraction_field_audit_extraction_id", table_name="extraction_field_audit")
    op.drop_table("extraction_field_audit")
    op.drop_index("ix_data_extraction_candidate_paper_id", table_name="data_extraction")
    op.drop_table("data_extraction")
    op.execute("DROP TYPE IF EXISTS extraction_status_enum")
    op.execute("DROP TYPE IF EXISTS research_type_enum")
