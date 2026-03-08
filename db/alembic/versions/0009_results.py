"""Add DomainModel, ClassificationScheme, and QualityReport tables (US6).

Revision ID: 0009_r
Revises: 0009
Create Date: 2026-03-12

Inserted between the extraction migration (0009) and the audit-trail migration
(0010) to maintain the canonical ordering:
  0009 (extraction) → 0009_r (results) → 0010 (audit_trail)
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_r"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # domain_model table
    # ------------------------------------------------------------------
    op.create_table(
        "domain_model",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("concepts", sa.JSON(), nullable=True),
        sa.Column("relationships", sa.JSON(), nullable=True),
        sa.Column("svg_content", sa.Text(), nullable=True),
        sa.Column(
            "generated_at",
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
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_domain_model_study_id", "domain_model", ["study_id"])

    # ------------------------------------------------------------------
    # classification_scheme table
    # ------------------------------------------------------------------
    op.create_table(
        "classification_scheme",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column(
            "chart_type",
            sa.Enum(
                "venue",
                "author",
                "locale",
                "institution",
                "year",
                "subtopic",
                "research_type",
                "research_method",
                name="chart_type_enum",
            ),
            nullable=False,
        ),
        sa.Column("version", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("chart_data", sa.JSON(), nullable=True),
        sa.Column("svg_content", sa.Text(), nullable=True),
        sa.Column(
            "generated_at",
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
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_classification_scheme_study_id", "classification_scheme", ["study_id"]
    )

    # ------------------------------------------------------------------
    # quality_report table
    # ------------------------------------------------------------------
    op.create_table(
        "quality_report",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column(
            "score_need_for_review", sa.SmallInteger(), nullable=False, server_default="0"
        ),
        sa.Column(
            "score_search_strategy", sa.SmallInteger(), nullable=False, server_default="0"
        ),
        sa.Column(
            "score_search_evaluation", sa.SmallInteger(), nullable=False, server_default="0"
        ),
        sa.Column(
            "score_extraction_classification",
            sa.SmallInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "score_study_validity", sa.SmallInteger(), nullable=False, server_default="0"
        ),
        sa.Column("total_score", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("rubric_details", sa.JSON(), nullable=True),
        sa.Column("recommendations", sa.JSON(), nullable=True),
        sa.Column(
            "generated_at",
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
        sa.ForeignKeyConstraint(["study_id"], ["study.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quality_report_study_id", "quality_report", ["study_id"])


def downgrade() -> None:
    op.drop_index("ix_quality_report_study_id", table_name="quality_report")
    op.drop_table("quality_report")
    op.drop_index("ix_classification_scheme_study_id", table_name="classification_scheme")
    op.drop_table("classification_scheme")
    op.execute("DROP TYPE IF EXISTS chart_type_enum")
    op.drop_index("ix_domain_model_study_id", table_name="domain_model")
    op.drop_table("domain_model")
