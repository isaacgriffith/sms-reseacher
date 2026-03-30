"""rapid_review_workflow

Revision ID: 0016
Revises: 0015
Create Date: 2026-03-29 00:00:00.000000

Feature 008 schema additions:

1. New PostgreSQL enum types:
   - ``rr_protocol_status_enum`` — Rapid Review protocol lifecycle states.
   - ``rr_quality_appraisal_mode_enum`` — quality appraisal approach choices.
   - ``rr_involvement_type_enum`` — practitioner stakeholder role types.
   - ``rr_threat_type_enum`` — threat-to-validity categories.
   - ``briefing_status_enum`` — Evidence Briefing version lifecycle states.

2. Extension to existing enum:
   - Adds ``protocol_invalidated`` value to ``inclusion_status_enum``
     (used when a validated Rapid Review protocol is edited — all collected
     papers are marked invalidated and must be re-screened).
     NOTE: ``ALTER TYPE ... ADD VALUE`` is non-reversible in PostgreSQL
     without dropping and recreating the type.  The downgrade() leaves the
     value in place but stops using it.

3. New tables (in dependency order):
   - ``rapid_review_protocol`` — one protocol per Rapid Review study.
   - ``practitioner_stakeholder`` — named practitioner contacts.
   - ``rr_threat_to_validity`` — auto-created validity threat records.
   - ``rr_narrative_synthesis_section`` — one section per research question.
   - ``evidence_briefing`` — versioned output document.
   - ``evidence_briefing_share_token`` — public share tokens.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "0016"
down_revision: str = "0015"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

# ---------------------------------------------------------------------------
# Enum type definitions — created/dropped explicitly so they survive table drops.
# ---------------------------------------------------------------------------

_rr_protocol_status_enum = postgresql.ENUM(
    "draft",
    "validated",
    name="rr_protocol_status_enum",
    create_type=False,
)
_rr_quality_appraisal_mode_enum = postgresql.ENUM(
    "full",
    "peer_reviewed_only",
    "skipped",
    name="rr_quality_appraisal_mode_enum",
    create_type=False,
)
_rr_involvement_type_enum = postgresql.ENUM(
    "problem_definer",
    "advisor",
    "recipient",
    name="rr_involvement_type_enum",
    create_type=False,
)
_rr_threat_type_enum = postgresql.ENUM(
    "single_source",
    "year_range",
    "language",
    "geography",
    "study_design",
    "single_reviewer",
    "qa_skipped",
    "qa_simplified",
    "context_restriction",
    name="rr_threat_type_enum",
    create_type=False,
)
_briefing_status_enum = postgresql.ENUM(
    "draft",
    "published",
    name="briefing_status_enum",
    create_type=False,
)


def upgrade() -> None:
    """Apply feature 008 Rapid Review workflow schema additions.

    Creates all five enum types, extends inclusion_status_enum, then
    creates all six tables in dependency order.
    """
    # 1. Create new enum types
    _rr_protocol_status_enum.create(op.get_bind(), checkfirst=True)
    _rr_quality_appraisal_mode_enum.create(op.get_bind(), checkfirst=True)
    _rr_involvement_type_enum.create(op.get_bind(), checkfirst=True)
    _rr_threat_type_enum.create(op.get_bind(), checkfirst=True)
    _briefing_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Extend existing inclusion_status_enum with protocol_invalidated.
    #    ALTER TYPE ... ADD VALUE cannot run inside a transaction in PostgreSQL
    #    < 12.  We use IF NOT EXISTS for idempotency.
    op.execute(
        "ALTER TYPE inclusion_status_enum ADD VALUE IF NOT EXISTS 'protocol_invalidated'"
    )

    # 3. rapid_review_protocol
    op.create_table(
        "rapid_review_protocol",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            _rr_protocol_status_enum,
            nullable=False,
            server_default="draft",
        ),
        sa.Column("practical_problem", sa.Text(), nullable=True),
        sa.Column("research_questions", sa.JSON(), nullable=True),
        sa.Column("time_budget_days", sa.Integer(), nullable=True),
        sa.Column("effort_budget_hours", sa.Integer(), nullable=True),
        sa.Column("context_restrictions", sa.JSON(), nullable=True),
        sa.Column("dissemination_medium", sa.String(255), nullable=True),
        sa.Column("problem_scoping_notes", sa.Text(), nullable=True),
        sa.Column("search_strategy_notes", sa.Text(), nullable=True),
        sa.Column("inclusion_criteria", sa.JSON(), nullable=True),
        sa.Column("exclusion_criteria", sa.JSON(), nullable=True),
        sa.Column(
            "single_reviewer_mode",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "single_source_acknowledged",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "quality_appraisal_mode",
            _rr_quality_appraisal_mode_enum,
            nullable=False,
            server_default="full",
        ),
        sa.Column(
            "version_id",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
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
            ["study_id"],
            ["study.id"],
            ondelete="CASCADE",
            name="fk_rr_protocol_study",
        ),
        sa.UniqueConstraint("study_id", name="uq_rr_protocol_study"),
    )
    op.create_index(
        "ix_rapid_review_protocol_study_id", "rapid_review_protocol", ["study_id"]
    )

    # 4. practitioner_stakeholder
    op.create_table(
        "practitioner_stakeholder",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role_title", sa.String(255), nullable=False),
        sa.Column("organisation", sa.String(255), nullable=False),
        sa.Column(
            "involvement_type",
            _rr_involvement_type_enum,
            nullable=False,
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
            ["study_id"],
            ["study.id"],
            ondelete="CASCADE",
            name="fk_practitioner_stakeholder_study",
        ),
    )
    op.create_index(
        "ix_practitioner_stakeholder_study_id",
        "practitioner_stakeholder",
        ["study_id"],
    )

    # 5. rr_threat_to_validity
    op.create_table(
        "rr_threat_to_validity",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("threat_type", _rr_threat_type_enum, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_detail", sa.String(500), nullable=True),
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
            name="fk_rr_threat_study",
        ),
    )
    op.create_index(
        "ix_rr_threat_to_validity_study_id", "rr_threat_to_validity", ["study_id"]
    )

    # 6. rr_narrative_synthesis_section
    op.create_table(
        "rr_narrative_synthesis_section",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("rq_index", sa.Integer(), nullable=False),
        sa.Column("narrative_text", sa.Text(), nullable=True),
        sa.Column("ai_draft_text", sa.Text(), nullable=True),
        sa.Column(
            "is_complete",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
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
            ["study_id"],
            ["study.id"],
            ondelete="CASCADE",
            name="fk_rr_synthesis_section_study",
        ),
        sa.UniqueConstraint(
            "study_id",
            "rq_index",
            name="uq_rr_synthesis_study_rq",
        ),
    )
    op.create_index(
        "ix_rr_narrative_synthesis_section_study_id",
        "rr_narrative_synthesis_section",
        ["study_id"],
    )

    # 7. evidence_briefing
    op.create_table(
        "evidence_briefing",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            _briefing_status_enum,
            nullable=False,
            server_default="draft",
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("findings", sa.JSON(), nullable=False),
        sa.Column("target_audience", sa.Text(), nullable=False),
        sa.Column("reference_complementary", sa.Text(), nullable=True),
        sa.Column("institution_logos", sa.JSON(), nullable=True),
        sa.Column("pdf_path", sa.String(1000), nullable=True),
        sa.Column("html_path", sa.String(1000), nullable=True),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
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
            ["study_id"],
            ["study.id"],
            ondelete="CASCADE",
            name="fk_evidence_briefing_study",
        ),
        sa.UniqueConstraint(
            "study_id",
            "version_number",
            name="uq_briefing_study_version",
        ),
    )
    op.create_index(
        "ix_evidence_briefing_study_id", "evidence_briefing", ["study_id"]
    )

    # 8. evidence_briefing_share_token
    op.create_table(
        "evidence_briefing_share_token",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("briefing_id", sa.Integer(), nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(64), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
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
            ["briefing_id"],
            ["evidence_briefing.id"],
            ondelete="CASCADE",
            name="fk_share_token_briefing",
        ),
        sa.ForeignKeyConstraint(
            ["study_id"],
            ["study.id"],
            ondelete="CASCADE",
            name="fk_share_token_study",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["user.id"],
            ondelete="SET NULL",
            name="fk_share_token_user",
        ),
        sa.UniqueConstraint("token", name="uq_share_token"),
    )
    op.create_index(
        "ix_evidence_briefing_share_token_briefing_id",
        "evidence_briefing_share_token",
        ["briefing_id"],
    )
    op.create_index(
        "ix_evidence_briefing_share_token_study_id",
        "evidence_briefing_share_token",
        ["study_id"],
    )
    op.create_index(
        "ix_evidence_briefing_share_token_token",
        "evidence_briefing_share_token",
        ["token"],
        unique=True,
    )


def downgrade() -> None:
    """Reverse feature 008 schema additions.

    NOTE: The ``protocol_invalidated`` value added to ``inclusion_status_enum``
    cannot be removed without dropping and recreating the enum type (PostgreSQL
    limitation).  The downgrade removes all new tables and enum types but
    leaves the extended ``inclusion_status_enum`` in place.
    """
    # Drop tables in reverse dependency order
    op.drop_table("evidence_briefing_share_token")
    op.drop_table("evidence_briefing")
    op.drop_table("rr_narrative_synthesis_section")
    op.drop_table("rr_threat_to_validity")
    op.drop_table("practitioner_stakeholder")
    op.drop_table("rapid_review_protocol")

    # Drop new enum types
    _briefing_status_enum.drop(op.get_bind(), checkfirst=True)
    _rr_threat_type_enum.drop(op.get_bind(), checkfirst=True)
    _rr_involvement_type_enum.drop(op.get_bind(), checkfirst=True)
    _rr_quality_appraisal_mode_enum.drop(op.get_bind(), checkfirst=True)
    _rr_protocol_status_enum.drop(op.get_bind(), checkfirst=True)

    # inclusion_status_enum: protocol_invalidated value is intentionally left
    # in place — ALTER TYPE DROP VALUE is not supported by PostgreSQL.
