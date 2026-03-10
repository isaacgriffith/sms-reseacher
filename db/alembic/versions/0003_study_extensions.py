"""Study extensions: new columns, StudyMember, Reviewer tables.

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add new columns to study and paper; create study_member and reviewer tables."""
    # Extend study table
    with op.batch_alter_table("study") as batch_op:
        batch_op.add_column(sa.Column("topic", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("motivation", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column("current_phase", sa.SmallInteger(), nullable=False, server_default="1")
        )
        batch_op.add_column(
            sa.Column("research_group_id", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("snowball_threshold", sa.SmallInteger(), nullable=False, server_default="5")
        )
        batch_op.create_foreign_key(
            "fk_study_research_group",
            "research_group",
            ["research_group_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index("ix_study_research_group_id", ["research_group_id"])

    # Extend paper table
    with op.batch_alter_table("paper") as batch_op:
        batch_op.add_column(sa.Column("authors", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("year", sa.SmallInteger(), nullable=True))
        batch_op.add_column(sa.Column("venue", sa.String(length=512), nullable=True))
        batch_op.add_column(sa.Column("source_url", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column("full_text_available", sa.Boolean(), nullable=False, server_default="0")
        )

    # Create study_member table
    op.create_table(
        "study_member",
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("lead", "member", name="study_member_role_enum"),
            nullable=False,
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("study_id", "user_id"),
        sa.UniqueConstraint("study_id", "user_id", name="uq_study_member"),
    )

    # Create reviewer table
    op.create_table(
        "reviewer",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column(
            "reviewer_type",
            sa.Enum("human", "ai_agent", name="reviewer_type_enum"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("agent_name", sa.String(length=255), nullable=True),
        sa.Column("agent_config", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reviewer_study_id", "reviewer", ["study_id"])


def downgrade() -> None:
    """Reverse study extensions."""
    op.drop_index("ix_reviewer_study_id", table_name="reviewer")
    op.drop_table("reviewer")
    op.drop_table("study_member")

    with op.batch_alter_table("paper") as batch_op:
        batch_op.drop_column("full_text_available")
        batch_op.drop_column("source_url")
        batch_op.drop_column("venue")
        batch_op.drop_column("year")
        batch_op.drop_column("authors")

    with op.batch_alter_table("study") as batch_op:
        batch_op.drop_index("ix_study_research_group_id")
        batch_op.drop_constraint("fk_study_research_group", type_="foreignkey")
        batch_op.drop_column("snowball_threshold")
        batch_op.drop_column("research_group_id")
        batch_op.drop_column("current_phase")
        batch_op.drop_column("motivation")
        batch_op.drop_column("topic")

    op.execute("DROP TYPE IF EXISTS reviewer_type_enum")
    op.execute("DROP TYPE IF EXISTS study_member_role_enum")
