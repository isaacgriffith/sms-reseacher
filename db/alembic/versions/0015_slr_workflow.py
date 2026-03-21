"""slr_workflow

Revision ID: 0015
Revises: 0014
Create Date: 2026-03-20 00:00:00.000000

Feature 007 schema additions:

1. New PostgreSQL enum types:
   - ``review_protocol_status_enum`` — protocol lifecycle states.
   - ``synthesis_approach_enum`` — synthesis method choices.
   - ``checklist_scoring_method_enum`` — item scoring types.
   - ``agreement_round_type_enum`` — screening round labels.
   - ``synthesis_status_enum`` — synthesis job states.
   - ``grey_literature_type_enum`` — non-database source types.

2. New tables:
   - ``review_protocol`` — one protocol per SLR study.
   - ``quality_assessment_checklist`` — study-scoped QA checklist.
   - ``quality_checklist_item`` — individual scored checklist items.
   - ``quality_assessment_score`` — one score per (reviewer, paper, item).
   - ``inter_rater_agreement_record`` — Cohen's Kappa calculation records.
   - ``synthesis_result`` — synthesis run results.
   - ``grey_literature_source`` — non-database literature entries.

Downgrade restores the pre-007 state by dropping all new tables and enum types
in reverse dependency order.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "0015"
down_revision: str = "0014"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

# Enum type definitions — created/dropped explicitly so they survive table drops.
_review_protocol_status_enum = postgresql.ENUM(
    "draft",
    "under_review",
    "validated",
    name="review_protocol_status_enum",
    create_type=False,
)
_synthesis_approach_enum = postgresql.ENUM(
    "meta_analysis",
    "descriptive",
    "qualitative",
    name="synthesis_approach_enum",
    create_type=False,
)
_checklist_scoring_method_enum = postgresql.ENUM(
    "binary",
    "scale_1_3",
    "scale_1_5",
    name="checklist_scoring_method_enum",
    create_type=False,
)
_agreement_round_type_enum = postgresql.ENUM(
    "title_abstract",
    "intro_conclusions",
    "full_text",
    "quality_assessment",
    name="agreement_round_type_enum",
    create_type=False,
)
_synthesis_status_enum = postgresql.ENUM(
    "pending",
    "running",
    "completed",
    "failed",
    name="synthesis_status_enum",
    create_type=False,
)
_grey_literature_type_enum = postgresql.ENUM(
    "technical_report",
    "dissertation",
    "rejected_publication",
    "work_in_progress",
    name="grey_literature_type_enum",
    create_type=False,
)


def upgrade() -> None:
    """Apply feature 007 SLR workflow schema additions.

    Creates all six enum types first, then creates all seven tables in
    dependency order (checklists before items, etc.).
    """
    # 1. Create enum types
    _review_protocol_status_enum.create(op.get_bind(), checkfirst=True)
    _synthesis_approach_enum.create(op.get_bind(), checkfirst=True)
    _checklist_scoring_method_enum.create(op.get_bind(), checkfirst=True)
    _agreement_round_type_enum.create(op.get_bind(), checkfirst=True)
    _synthesis_status_enum.create(op.get_bind(), checkfirst=True)
    _grey_literature_type_enum.create(op.get_bind(), checkfirst=True)

    # 2. review_protocol
    op.create_table(
        "review_protocol",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            _review_protocol_status_enum,
            nullable=False,
            server_default="draft",
        ),
        sa.Column("background", sa.Text(), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("research_questions", sa.JSON(), nullable=True),
        sa.Column("pico_population", sa.Text(), nullable=True),
        sa.Column("pico_intervention", sa.Text(), nullable=True),
        sa.Column("pico_comparison", sa.Text(), nullable=True),
        sa.Column("pico_outcome", sa.Text(), nullable=True),
        sa.Column("pico_context", sa.Text(), nullable=True),
        sa.Column("search_strategy", sa.Text(), nullable=True),
        sa.Column("inclusion_criteria", sa.JSON(), nullable=True),
        sa.Column("exclusion_criteria", sa.JSON(), nullable=True),
        sa.Column("data_extraction_strategy", sa.Text(), nullable=True),
        sa.Column("synthesis_approach", _synthesis_approach_enum, nullable=True),
        sa.Column("dissemination_strategy", sa.Text(), nullable=True),
        sa.Column("timetable", sa.Text(), nullable=True),
        sa.Column("review_report", sa.JSON(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["study_id"], ["study.id"], ondelete="CASCADE", name="fk_review_protocol_study"
        ),
        sa.UniqueConstraint("study_id", name="uq_review_protocol_study"),
    )
    op.create_index("ix_review_protocol_study_id", "review_protocol", ["study_id"])

    # 3. quality_assessment_checklist
    op.create_table(
        "quality_assessment_checklist",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
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
            name="fk_quality_assessment_checklist_study",
        ),
        sa.UniqueConstraint("study_id", name="uq_quality_assessment_checklist_study"),
    )
    op.create_index(
        "ix_quality_assessment_checklist_study_id",
        "quality_assessment_checklist",
        ["study_id"],
    )

    # 4. quality_checklist_item
    op.create_table(
        "quality_checklist_item",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("checklist_id", sa.Integer(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("scoring_method", _checklist_scoring_method_enum, nullable=False),
        sa.Column(
            "weight", sa.Float(), nullable=False, server_default=sa.text("1.0")
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
            ["checklist_id"],
            ["quality_assessment_checklist.id"],
            ondelete="CASCADE",
            name="fk_quality_checklist_item_checklist",
        ),
    )
    op.create_index(
        "ix_quality_checklist_item_checklist_id",
        "quality_checklist_item",
        ["checklist_id"],
    )

    # 5. quality_assessment_score
    op.create_table(
        "quality_assessment_score",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("candidate_paper_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=False),
        sa.Column("checklist_item_id", sa.Integer(), nullable=False),
        sa.Column("score_value", sa.Float(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["candidate_paper_id"],
            ["candidate_paper.id"],
            ondelete="CASCADE",
            name="fk_quality_assessment_score_candidate_paper",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["reviewer.id"],
            ondelete="CASCADE",
            name="fk_quality_assessment_score_reviewer",
        ),
        sa.ForeignKeyConstraint(
            ["checklist_item_id"],
            ["quality_checklist_item.id"],
            ondelete="CASCADE",
            name="fk_quality_assessment_score_checklist_item",
        ),
        sa.UniqueConstraint(
            "candidate_paper_id",
            "reviewer_id",
            "checklist_item_id",
            name="uq_quality_assessment_score",
        ),
    )
    op.create_index(
        "ix_quality_assessment_score_candidate_paper_id",
        "quality_assessment_score",
        ["candidate_paper_id"],
    )
    op.create_index(
        "ix_quality_assessment_score_reviewer_id",
        "quality_assessment_score",
        ["reviewer_id"],
    )
    op.create_index(
        "ix_quality_assessment_score_checklist_item_id",
        "quality_assessment_score",
        ["checklist_item_id"],
    )

    # 6. inter_rater_agreement_record
    op.create_table(
        "inter_rater_agreement_record",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_a_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_b_id", sa.Integer(), nullable=False),
        sa.Column("round_type", _agreement_round_type_enum, nullable=False),
        sa.Column("phase", sa.String(20), nullable=False),
        sa.Column("kappa_value", sa.Float(), nullable=True),
        sa.Column("kappa_undefined_reason", sa.String(255), nullable=True),
        sa.Column("n_papers", sa.Integer(), nullable=False),
        sa.Column("threshold_met", sa.Boolean(), nullable=False),
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
            name="fk_inter_rater_agreement_record_study",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_a_id"],
            ["reviewer.id"],
            ondelete="CASCADE",
            name="fk_inter_rater_agreement_record_reviewer_a",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_b_id"],
            ["reviewer.id"],
            ondelete="CASCADE",
            name="fk_inter_rater_agreement_record_reviewer_b",
        ),
    )
    op.create_index(
        "ix_inter_rater_agreement_record_study_id",
        "inter_rater_agreement_record",
        ["study_id"],
    )

    # 7. synthesis_result
    op.create_table(
        "synthesis_result",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("approach", _synthesis_approach_enum, nullable=False),
        sa.Column(
            "status",
            _synthesis_status_enum,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("model_type", sa.String(20), nullable=True),
        sa.Column("parameters", sa.JSON(), nullable=True),
        sa.Column("computed_statistics", sa.JSON(), nullable=True),
        sa.Column("forest_plot_svg", sa.Text(), nullable=True),
        sa.Column("funnel_plot_svg", sa.Text(), nullable=True),
        sa.Column("qualitative_themes", sa.JSON(), nullable=True),
        sa.Column("sensitivity_analysis", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["study_id"], ["study.id"], ondelete="CASCADE", name="fk_synthesis_result_study"
        ),
    )
    op.create_index("ix_synthesis_result_study_id", "synthesis_result", ["study_id"])

    # 8. grey_literature_source
    op.create_table(
        "grey_literature_source",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("source_type", _grey_literature_type_enum, nullable=False),
        sa.Column("title", sa.String(1024), nullable=False),
        sa.Column("authors", sa.String(1024), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("url", sa.String(2048), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
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
            name="fk_grey_literature_source_study",
        ),
    )
    op.create_index(
        "ix_grey_literature_source_study_id", "grey_literature_source", ["study_id"]
    )


def downgrade() -> None:
    """Revert feature 007 SLR workflow schema additions.

    Drops all seven tables in reverse dependency order, then drops all
    six enum types.
    """
    # 1. Drop tables in reverse dependency order
    op.drop_index("ix_grey_literature_source_study_id", table_name="grey_literature_source")
    op.drop_table("grey_literature_source")

    op.drop_index("ix_synthesis_result_study_id", table_name="synthesis_result")
    op.drop_table("synthesis_result")

    op.drop_index(
        "ix_inter_rater_agreement_record_study_id",
        table_name="inter_rater_agreement_record",
    )
    op.drop_table("inter_rater_agreement_record")

    op.drop_index(
        "ix_quality_assessment_score_checklist_item_id",
        table_name="quality_assessment_score",
    )
    op.drop_index(
        "ix_quality_assessment_score_reviewer_id", table_name="quality_assessment_score"
    )
    op.drop_index(
        "ix_quality_assessment_score_candidate_paper_id",
        table_name="quality_assessment_score",
    )
    op.drop_table("quality_assessment_score")

    op.drop_index(
        "ix_quality_checklist_item_checklist_id", table_name="quality_checklist_item"
    )
    op.drop_table("quality_checklist_item")

    op.drop_index(
        "ix_quality_assessment_checklist_study_id",
        table_name="quality_assessment_checklist",
    )
    op.drop_table("quality_assessment_checklist")

    op.drop_index("ix_review_protocol_study_id", table_name="review_protocol")
    op.drop_table("review_protocol")

    # 2. Drop enum types
    _grey_literature_type_enum.drop(op.get_bind(), checkfirst=True)
    _synthesis_status_enum.drop(op.get_bind(), checkfirst=True)
    _agreement_round_type_enum.drop(op.get_bind(), checkfirst=True)
    _checklist_scoring_method_enum.drop(op.get_bind(), checkfirst=True)
    _synthesis_approach_enum.drop(op.get_bind(), checkfirst=True)
    _review_protocol_status_enum.drop(op.get_bind(), checkfirst=True)
