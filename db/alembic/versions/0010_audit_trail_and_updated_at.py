"""Add AuditRecord table and missing updated_at/created_at columns (NFR-001, FR-044).

Revision ID: 0010
Revises: 0009
Create Date: 2026-03-12

Covers:
- T120: updated_at → search_string; created_at → pico_component
- T121: updated_at → inclusion_criterion, exclusion_criterion,
        search_execution (+ created_at), search_metrics, background_job
- T122: AuditRecord table with composite indexes
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: str | None = "0009_r"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # T120: search_string — add updated_at
    # ------------------------------------------------------------------
    op.add_column(
        "search_string",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # T120: pico_component — add created_at
    # ------------------------------------------------------------------
    op.add_column(
        "pico_component",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # T121: inclusion_criterion — add updated_at
    # ------------------------------------------------------------------
    op.add_column(
        "inclusion_criterion",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # T121: exclusion_criterion — add updated_at
    # ------------------------------------------------------------------
    op.add_column(
        "exclusion_criterion",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # T121: search_execution — add created_at and updated_at
    # ------------------------------------------------------------------
    op.add_column(
        "search_execution",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.add_column(
        "search_execution",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # T121: search_metrics — add updated_at
    # ------------------------------------------------------------------
    op.add_column(
        "search_metrics",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # T121: background_job — add updated_at
    # ------------------------------------------------------------------
    op.add_column(
        "background_job",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # T122: audit_record table
    # ------------------------------------------------------------------
    op.create_table(
        "audit_record",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("actor_agent", sa.String(255), nullable=True),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column(
            "action",
            sa.Enum("create", "update", "delete", name="audit_action_enum"),
            nullable=False,
        ),
        sa.Column("field_name", sa.String(128), nullable=True),
        sa.Column("before_value", sa.JSON(), nullable=True),
        sa.Column("after_value", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_user_id"], ["user.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_audit_record_study_created",
        "audit_record",
        ["study_id", "created_at"],
    )
    op.create_index(
        "ix_audit_record_entity",
        "audit_record",
        ["entity_type", "entity_id"],
    )


def downgrade() -> None:
    # Drop audit_record indexes and table
    op.drop_index("ix_audit_record_entity", table_name="audit_record")
    op.drop_index("ix_audit_record_study_created", table_name="audit_record")
    op.drop_table("audit_record")

    # Drop added columns in reverse order
    op.drop_column("background_job", "updated_at")
    op.drop_column("search_metrics", "updated_at")
    op.drop_column("search_execution", "updated_at")
    op.drop_column("search_execution", "created_at")
    op.drop_column("exclusion_criterion", "updated_at")
    op.drop_column("inclusion_criterion", "updated_at")
    op.drop_column("pico_component", "created_at")
    op.drop_column("search_string", "updated_at")
