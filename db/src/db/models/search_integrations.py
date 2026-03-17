"""ORM models for feature 006: database search integrations and full-text retrieval.

Feature 006 additions:
- :class:`DatabaseIndex` — enum of supported academic database indices.
- :class:`IntegrationType` — enum of credential-carrying service integrations.
- :class:`TestStatus` — connectivity test result states.
- :class:`FullTextSource` — provenance enum for retrieved full-text content.
- :class:`StudyDatabaseSelection` — per-study toggle for each database index.
- :class:`SearchIntegrationCredential` — encrypted API key storage per integration.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class DatabaseIndex(str, enum.Enum):
    """Supported academic database indices that a study can search.

    Values map directly to source identifiers used by the SourceRegistry in
    researcher-mcp and to the toggle labels shown in the study settings UI.
    """

    IEEE_XPLORE = "ieee_xplore"
    ACM_DL = "acm_dl"
    SCOPUS = "scopus"
    WEB_OF_SCIENCE = "web_of_science"
    INSPEC = "inspec"
    SCIENCE_DIRECT = "science_direct"
    SPRINGER_LINK = "springer_link"
    GOOGLE_SCHOLAR = "google_scholar"
    SEMANTIC_SCHOLAR = "semantic_scholar"


class IntegrationType(str, enum.Enum):
    """Service types for which API credentials can be stored.

    Note that ``ELSEVIER`` covers Scopus, ScienceDirect, and Inspec — all
    three share the same ``ELSEVIER_API_KEY`` / ``ELSEVIER_INST_TOKEN`` pair.
    ``UNPAYWALL`` stores an email address rather than an API key.
    ``GOOGLE_SCHOLAR`` stores a proxy URL in ``config_json_encrypted``.
    """

    IEEE_XPLORE = "ieee_xplore"
    ELSEVIER = "elsevier"
    WEB_OF_SCIENCE = "web_of_science"
    SPRINGER_NATURE = "springer_nature"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    UNPAYWALL = "unpaywall"
    GOOGLE_SCHOLAR = "google_scholar"


class TestStatus(str, enum.Enum):
    """Result states for an on-demand connectivity test of a search integration.

    Values:
        SUCCESS: Test query succeeded; integration is reachable and authenticated.
        RATE_LIMITED: Request was accepted but the API signalled rate limiting.
        AUTH_FAILED: Credentials were rejected by the remote service.
        UNREACHABLE: Network or DNS failure; service could not be contacted.
        UNTESTED: No test has been run yet.
    """

    SUCCESS = "success"
    RATE_LIMITED = "rate_limited"
    AUTH_FAILED = "auth_failed"
    UNREACHABLE = "unreachable"
    UNTESTED = "untested"


class FullTextSource(str, enum.Enum):
    """Provenance of a paper's retrieved full-text content.

    Values:
        UNPAYWALL: Retrieved via Unpaywall open-access API.
        DIRECT: Retrieved from the paper's direct URL.
        SCIHUB: Retrieved via SciHub (opt-in, operator-enabled only).
        UNAVAILABLE: All retrieval attempts failed; no full text stored.
        PENDING: Retrieval has been queued but not yet attempted.
    """

    UNPAYWALL = "unpaywall"
    DIRECT = "direct"
    SCIHUB = "scihub"
    UNAVAILABLE = "unavailable"
    PENDING = "pending"


class StudyDatabaseSelection(Base):
    """Records which academic database indices a study has enabled for search.

    One row per (study, database_index) pair.  Missing rows are treated as
    disabled — the application only inserts rows that have been explicitly
    toggled.  Deleting a study cascades to delete all its selection rows.
    """

    __tablename__ = "study_database_selection"
    __table_args__ = (
        UniqueConstraint("study_id", "database_index", name="uq_study_database_selection"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    database_index: Mapped[DatabaseIndex] = mapped_column(
        Enum(DatabaseIndex, name="databaseindex"),
        nullable=False,
    )
    is_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
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

    study: Mapped["Study"] = relationship("Study")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<StudyDatabaseSelection study_id={self.study_id}"
            f" index={self.database_index} enabled={self.is_enabled}>"
        )


class SearchIntegrationCredential(Base):
    """Encrypted API credentials for a subscription-gated database integration.

    One row per :class:`IntegrationType`.  API keys are stored Fernet-encrypted
    and are never returned in plaintext via any API response.  If no row exists
    for an integration type the application falls back to the corresponding
    environment variable.

    Uses optimistic locking (``version_id``) to detect concurrent edits.
    """

    __tablename__ = "search_integration_credential"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    integration_type: Mapped[IntegrationType] = mapped_column(
        Enum(IntegrationType, name="integrationtype"),
        nullable=False,
        unique=True,
    )
    api_key_encrypted: Mapped[bytes | None] = mapped_column(
        LargeBinary,
        nullable=True,
        comment="Fernet-encrypted primary API key; NULL when using env-var fallback",
    )
    auxiliary_token_encrypted: Mapped[bytes | None] = mapped_column(
        LargeBinary,
        nullable=True,
        comment="Fernet-encrypted secondary credential (e.g. Elsevier inst token)",
    )
    config_json_encrypted: Mapped[bytes | None] = mapped_column(
        LargeBinary,
        nullable=True,
        comment="Fernet-encrypted JSON blob for additional config (e.g. proxy URL)",
    )
    last_tested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_test_status: Mapped[TestStatus | None] = mapped_column(
        Enum(TestStatus, name="teststatus"),
        nullable=True,
        default=TestStatus.UNTESTED,
    )
    version_id: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
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

    __mapper_args__ = {"version_id_col": version_id}

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<SearchIntegrationCredential type={self.integration_type}"
            f" tested={self.last_test_status}>"
        )
