"""PICO/C and seed tables: PICOComponent, SeedPaper, SeedAuthor.

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create pico_component, seed_paper, and seed_author tables."""
    op.create_table(
        "pico_component",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column(
            "variant",
            sa.Enum("PICO", "PICOS", "PICOT", "SPIDER", "PCC", name="pico_variant_enum"),
            nullable=False,
        ),
        sa.Column("population", sa.Text(), nullable=True),
        sa.Column("intervention", sa.Text(), nullable=True),
        sa.Column("comparison", sa.Text(), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column("extra_fields", sa.JSON(), nullable=True, comment="Variant-specific fields"),
        sa.Column("ai_suggestions", sa.JSON(), nullable=True, comment="AI refinement suggestions"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("study_id"),
    )
    op.create_index("ix_pico_component_study_id", "pico_component", ["study_id"], unique=True)

    op.create_table(
        "seed_paper",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("paper_id", sa.Integer(), nullable=False),
        sa.Column("added_by_user_id", sa.Integer(), nullable=True),
        sa.Column("added_by_agent", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.ForeignKeyConstraint(["paper_id"], ["paper.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["added_by_user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_seed_paper_study_id", "seed_paper", ["study_id"])

    op.create_table(
        "seed_author",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("author_name", sa.String(length=255), nullable=False),
        sa.Column("institution", sa.String(length=255), nullable=True),
        sa.Column("profile_url", sa.Text(), nullable=True),
        sa.Column("added_by_user_id", sa.Integer(), nullable=True),
        sa.Column("added_by_agent", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["added_by_user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_seed_author_study_id", "seed_author", ["study_id"])


def downgrade() -> None:
    """Drop seed and PICO tables."""
    op.drop_index("ix_seed_author_study_id", table_name="seed_author")
    op.drop_table("seed_author")
    op.drop_index("ix_seed_paper_study_id", table_name="seed_paper")
    op.drop_table("seed_paper")
    op.drop_index("ix_pico_component_study_id", table_name="pico_component")
    op.drop_table("pico_component")
    op.execute("DROP TYPE IF EXISTS pico_variant_enum")
