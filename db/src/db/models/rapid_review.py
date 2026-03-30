"""ORM models for feature 008: Rapid Review workflow.

Feature 008 additions:
- :class:`RRProtocolStatus` — Rapid Review protocol lifecycle states.
- :class:`RRQualityAppraisalMode` — quality appraisal approach choices.
- :class:`RRInvolvementType` — practitioner stakeholder role types.
- :class:`RRThreatType` — categories of threat-to-validity entries.
- :class:`BriefingStatus` — Evidence Briefing version lifecycle states.
- :class:`RapidReviewProtocol` — one protocol per Rapid Review study.
- :class:`PractitionerStakeholder` — named practitioner contacts (no platform account).
- :class:`RRThreatToValidity` — auto-created validity threat records.
- :class:`RRNarrativeSynthesisSection` — one synthesis section per research question.
- :class:`EvidenceBriefing` — versioned Evidence Briefing output document.
- :class:`EvidenceBriefingShareToken` — opaque tokens for public practitioner access.
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from db.base import Base

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class RRProtocolStatus(str, enum.Enum):
    """Rapid Review protocol lifecycle states.

    Transitions::

        draft → validated
        validated → draft  (on any protocol edit)
    """

    DRAFT = "draft"
    VALIDATED = "validated"


class RRQualityAppraisalMode(str, enum.Enum):
    """Quality appraisal approach for a Rapid Review.

    Determines how phase 4 is gated and which threats are auto-created.
    """

    FULL = "full"
    PEER_REVIEWED_ONLY = "peer_reviewed_only"
    SKIPPED = "skipped"


class RRInvolvementType(str, enum.Enum):
    """Role of a practitioner stakeholder in a Rapid Review."""

    PROBLEM_DEFINER = "problem_definer"
    ADVISOR = "advisor"
    RECIPIENT = "recipient"


class RRThreatType(str, enum.Enum):
    """Category of a threat-to-validity entry in a Rapid Review."""

    SINGLE_SOURCE = "single_source"
    YEAR_RANGE = "year_range"
    LANGUAGE = "language"
    GEOGRAPHY = "geography"
    STUDY_DESIGN = "study_design"
    SINGLE_REVIEWER = "single_reviewer"
    QA_SKIPPED = "qa_skipped"
    QA_SIMPLIFIED = "qa_simplified"
    CONTEXT_RESTRICTION = "context_restriction"


class BriefingStatus(str, enum.Enum):
    """Evidence Briefing version lifecycle states.

    At most one version per study may be ``published`` at a time.
    Promoting a new version atomically demotes the previous one to ``draft``.
    """

    DRAFT = "draft"
    PUBLISHED = "published"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class RapidReviewProtocol(Base):
    """One Rapid Review protocol per study.

    A Rapid Review study cannot advance past phase 1 until ``status`` is
    ``validated``.  Any edit to a validated protocol resets it to ``draft``
    and marks all collected papers as ``protocol_invalidated``.

    Uses optimistic locking (``version_id``) to prevent lost-update conflicts
    during concurrent edits.
    """

    __tablename__ = "rapid_review_protocol"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    status: Mapped[RRProtocolStatus] = mapped_column(
        Enum(RRProtocolStatus, name="rr_protocol_status_enum"),
        nullable=False,
        default=RRProtocolStatus.DRAFT,
        server_default=RRProtocolStatus.DRAFT.value,
    )
    practical_problem: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_questions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    time_budget_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    effort_budget_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    context_restrictions: Mapped[list | None] = mapped_column(
        JSON, nullable=True, comment="list[{type: str, description: str}]"
    )
    dissemination_medium: Mapped[str | None] = mapped_column(String(255), nullable=True)
    problem_scoping_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    search_strategy_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    inclusion_criteria: Mapped[list | None] = mapped_column(JSON, nullable=True)
    exclusion_criteria: Mapped[list | None] = mapped_column(JSON, nullable=True)
    single_reviewer_mode: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    single_source_acknowledged: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="Set True when a SINGLE_SOURCE threat has been acknowledged",
    )
    quality_appraisal_mode: Mapped[RRQualityAppraisalMode] = mapped_column(
        Enum(RRQualityAppraisalMode, name="rr_quality_appraisal_mode_enum"),
        nullable=False,
        default=RRQualityAppraisalMode.FULL,
        server_default=RRQualityAppraisalMode.FULL.value,
    )
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    threats: Mapped[list[RRThreatToValidity]] = relationship(
        "RRThreatToValidity",
        back_populates="protocol",
        cascade="all, delete-orphan",
        primaryjoin="RapidReviewProtocol.study_id == RRThreatToValidity.study_id",
        foreign_keys="[RRThreatToValidity.study_id]",
    )

    __mapper_args__ = {"version_id_col": version_id}

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<RapidReviewProtocol id={self.id} study_id={self.study_id} status={self.status}>"


class PractitionerStakeholder(Base):
    """Named practitioner contact for a Rapid Review.

    Practitioners have no platform account and cannot log in.
    At least one stakeholder must exist before the protocol can be validated.
    """

    __tablename__ = "practitioner_stakeholder"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False)
    organisation: Mapped[str] = mapped_column(String(255), nullable=False)
    involvement_type: Mapped[RRInvolvementType] = mapped_column(
        Enum(RRInvolvementType, name="rr_involvement_type_enum"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<PractitionerStakeholder id={self.id} study_id={self.study_id} name={self.name!r}>"


class RRThreatToValidity(Base):
    """Auto-created validity threat record for a Rapid Review.

    Records are created automatically by the service layer when search
    restrictions, single-reviewer mode, or quality appraisal omissions are
    applied.  They are not created directly by the researcher.
    """

    __tablename__ = "rr_threat_to_validity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    threat_type: Mapped[RRThreatType] = mapped_column(
        Enum(RRThreatType, name="rr_threat_type_enum"),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_detail: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="e.g. '2015-2025', 'English only', 'RCT only'",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    protocol: Mapped[RapidReviewProtocol] = relationship(
        "RapidReviewProtocol",
        back_populates="threats",
        primaryjoin="RRThreatToValidity.study_id == RapidReviewProtocol.study_id",
        foreign_keys="[RRThreatToValidity.study_id]",
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<RRThreatToValidity id={self.id} study_id={self.study_id} type={self.threat_type}>"


class RRNarrativeSynthesisSection(Base):
    """One narrative synthesis section per research question.

    Sections are auto-created when the protocol is first validated, one per
    entry in :attr:`RapidReviewProtocol.research_questions`.  The researcher
    edits ``narrative_text``; the AI writes ``ai_draft_text`` which the
    researcher may accept, edit, or discard.
    """

    __tablename__ = "rr_narrative_synthesis_section"
    __table_args__ = (UniqueConstraint("study_id", "rq_index", name="uq_rr_synthesis_study_rq"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rq_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Zero-based index into RapidReviewProtocol.research_questions",
    )
    narrative_text: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Researcher-authored final content"
    )
    ai_draft_text: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="AI-generated draft, pre-acceptance"
    )
    is_complete: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<RRNarrativeSynthesisSection id={self.id} study_id={self.study_id}"
            f" rq_index={self.rq_index} complete={self.is_complete}>"
        )


class EvidenceBriefing(Base):
    """Versioned Evidence Briefing output document for a Rapid Review.

    Each generation creates a new numbered version (v1, v2, …) scoped per
    study.  At most one version may be ``published`` at any time; promoting a
    version atomically demotes the previous published version to ``draft``.
    The published version is accessible via :class:`EvidenceBriefingShareToken`.
    """

    __tablename__ = "evidence_briefing"
    __table_args__ = (
        UniqueConstraint("study_id", "version_number", name="uq_briefing_study_version"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Auto-incremented per study (1, 2, 3…)"
    )
    status: Mapped[BriefingStatus] = mapped_column(
        Enum(BriefingStatus, name="briefing_status_enum"),
        nullable=False,
        default=BriefingStatus.DRAFT,
        server_default=BriefingStatus.DRAFT.value,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    findings: Mapped[dict] = mapped_column(
        JSON, nullable=False, comment="{rq_index: str} — per-RQ findings text"
    )
    target_audience: Mapped[str] = mapped_column(Text, nullable=False)
    reference_complementary: Mapped[str | None] = mapped_column(Text, nullable=True)
    institution_logos: Mapped[list | None] = mapped_column(
        JSON, nullable=True, comment="list[str] — stored file paths"
    )
    pdf_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    html_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    share_tokens: Mapped[list[EvidenceBriefingShareToken]] = relationship(
        "EvidenceBriefingShareToken",
        back_populates="briefing",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<EvidenceBriefing id={self.id} study_id={self.study_id}"
            f" v{self.version_number} status={self.status}>"
        )


class EvidenceBriefingShareToken(Base):
    """Opaque share token granting unauthenticated access to a published briefing.

    Tokens are cryptographically random (``secrets.token_urlsafe(32)``) and
    revocable by any study team member via ``revoked_at``.  The token always
    resolves to the currently published briefing for the study, not a pinned
    version.
    """

    __tablename__ = "evidence_briefing_share_token"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    briefing_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("evidence_briefing.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Denormalised for access-check performance",
    )
    created_by_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=False,
    )
    token: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
        comment="secrets.token_urlsafe(32)",
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="NULL = active"
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="NULL = no expiry"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    briefing: Mapped[EvidenceBriefing] = relationship(
        "EvidenceBriefing", back_populates="share_tokens"
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<EvidenceBriefingShareToken id={self.id}"
            f" briefing_id={self.briefing_id}"
            f" revoked={self.revoked_at is not None}>"
        )
