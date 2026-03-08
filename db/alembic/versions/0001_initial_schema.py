"""Initial schema: Study, Paper, StudyPaper.

Revision ID: 0001
Revises:
Create Date: 2026-03-08

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial tables."""
    op.create_table(
        "study",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "study_type",
            sa.Enum("SMS", "SLR", "Tertiary", "Rapid", name="study_type_enum"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("draft", "active", "completed", "archived", name="study_status_enum"),
            nullable=False,
            server_default="draft",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "paper",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("doi", sa.String(length=255), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True, comment="Flexible bibliographic fields"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("doi"),
    )

    op.create_table(
        "study_paper",
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("paper_id", sa.Integer(), nullable=False),
        sa.Column(
            "inclusion_status",
            sa.Enum("pending", "included", "excluded", name="inclusion_status_enum"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["paper_id"], ["paper.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("study_id", "paper_id"),
        sa.UniqueConstraint("study_id", "paper_id", name="uq_study_paper"),
    )


def downgrade() -> None:
    """Drop all initial tables."""
    op.drop_table("study_paper")
    op.drop_table("paper")
    op.drop_table("study")
    op.execute("DROP TYPE IF EXISTS inclusion_status_enum")
    op.execute("DROP TYPE IF EXISTS study_status_enum")
    op.execute("DROP TYPE IF EXISTS study_type_enum")
