"""Candidate papers, search execution, background jobs, and search metrics.

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-11

Creates:
- search_execution
- candidate_paper
- paper_decision
- background_job
- search_metrics
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # search_execution
    op.create_table(
        "search_execution",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("search_string_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "running", "completed", "failed",
                name="search_execution_status_enum",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("phase_tag", sa.String(64), nullable=False, server_default="initial-search"),
        sa.Column("databases_queried", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("job_id", sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["search_string_id"], ["search_string.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_search_execution_study_id", "search_execution", ["study_id"])

    # candidate_paper
    op.create_table(
        "candidate_paper",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("paper_id", sa.Integer(), nullable=False),
        sa.Column("search_execution_id", sa.Integer(), nullable=False),
        sa.Column("phase_tag", sa.String(64), nullable=False),
        sa.Column(
            "current_status",
            sa.Enum(
                "pending", "accepted", "rejected", "duplicate",
                name="candidate_paper_status_enum",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("duplicate_of_id", sa.Integer(), nullable=True),
        sa.Column("version_id", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["paper_id"], ["paper.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["search_execution_id"], ["search_execution.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["duplicate_of_id"], ["candidate_paper.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("study_id", "paper_id", name="uq_candidate_paper_study_paper"),
    )
    op.create_index("ix_candidate_paper_study_id", "candidate_paper", ["study_id"])

    # paper_decision
    op.create_table(
        "paper_decision",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("candidate_paper_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=False),
        sa.Column(
            "decision",
            sa.Enum("accepted", "rejected", "duplicate", name="paper_decision_type_enum"),
            nullable=False,
        ),
        sa.Column("reasons", sa.JSON(), nullable=True),
        sa.Column("is_override", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overrides_decision_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["candidate_paper_id"], ["candidate_paper.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["reviewer.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["overrides_decision_id"], ["paper_decision.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_paper_decision_candidate_paper_id", "paper_decision", ["candidate_paper_id"])

    # background_job
    op.create_table(
        "background_job",
        sa.Column("id", sa.String(255), nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column(
            "job_type",
            sa.Enum(
                "full_search", "snowball_search", "batch_extraction", "quality_eval",
                name="background_job_type_enum",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("queued", "running", "completed", "failed", name="background_job_status_enum"),
            nullable=False,
            server_default="queued",
        ),
        sa.Column("progress_pct", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("progress_detail", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "queued_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_background_job_study_id", "background_job", ["study_id"])

    # search_metrics
    op.create_table(
        "search_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("search_execution_id", sa.Integer(), nullable=False),
        sa.Column("total_identified", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accepted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rejected", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicates", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["search_execution_id"], ["search_execution.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("search_execution_id", name="uq_search_metrics_execution"),
    )


def downgrade() -> None:
    op.drop_table("search_metrics")
    op.drop_index("ix_background_job_study_id", table_name="background_job")
    op.drop_table("background_job")
    op.drop_index("ix_paper_decision_candidate_paper_id", table_name="paper_decision")
    op.drop_table("paper_decision")
    op.drop_index("ix_candidate_paper_study_id", table_name="candidate_paper")
    op.drop_table("candidate_paper")
    op.drop_index("ix_search_execution_study_id", table_name="search_execution")
    op.drop_table("search_execution")
    op.drop_constraint(None, "search_execution_status_enum", type_="enum")
    op.drop_constraint(None, "candidate_paper_status_enum", type_="enum")
    op.drop_constraint(None, "paper_decision_type_enum", type_="enum")
    op.drop_constraint(None, "background_job_type_enum", type_="enum")
    op.drop_constraint(None, "background_job_status_enum", type_="enum")
