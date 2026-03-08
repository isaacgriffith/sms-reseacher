"""Criteria and search string tables.

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-10

Creates:
- inclusion_criterion
- exclusion_criterion
- search_string
- search_string_iteration
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # inclusion_criterion
    op.create_table(
        "inclusion_criterion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("order_index", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # exclusion_criterion
    op.create_table(
        "exclusion_criterion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("order_index", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # search_string
    op.create_table(
        "search_string",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("string_text", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_by_agent", sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # search_string_iteration
    op.create_table(
        "search_string_iteration",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("search_string_id", sa.Integer(), nullable=False),
        sa.Column("iteration_number", sa.SmallInteger(), nullable=False),
        sa.Column("result_set_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("test_set_recall", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("ai_adequacy_judgment", sa.Text(), nullable=True),
        sa.Column("human_approved", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["search_string_id"], ["search_string.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("search_string_iteration")
    op.drop_table("search_string")
    op.drop_table("exclusion_criterion")
    op.drop_table("inclusion_criterion")
