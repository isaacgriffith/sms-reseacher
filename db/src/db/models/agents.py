"""ORM models: Provider, AvailableModel, Agent — LLM provider and agent abstractions.

Feature 005 additions:
- :class:`ProviderType` — supported LLM provider types.
- :class:`AgentTaskType` — task roles agents can fulfil in the research workflow.
- :class:`Provider` — a configured LLM service (Anthropic, OpenAI, or Ollama).
- :class:`AvailableModel` — an individual model offered by a provider.
- :class:`Agent` — a fully configured AI participant combining a role, persona, and model.
"""

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
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class ProviderType(str, enum.Enum):
    """Supported LLM provider backends.

    Values:
        ANTHROPIC: Anthropic Messages API (api_key required).
        OPENAI: OpenAI Chat Completions API (api_key required).
        OLLAMA: Self-hosted Ollama server (base_url required; no api_key).
    """

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"


class AgentTaskType(str, enum.Enum):
    """Research workflow task roles that an agent can fulfil.

    Each value maps to a distinct step in the SMS/SLR research pipeline.
    New task types require a code change — this is intentional to keep the
    set of valid roles bounded and auditable.
    """

    SCREENER = "screener"
    EXTRACTOR = "extractor"
    LIBRARIAN = "librarian"
    EXPERT = "expert"
    QUALITY_JUDGE = "quality_judge"
    AGENT_GENERATOR = "agent_generator"
    DOMAIN_MODELER = "domain_modeler"
    SYNTHESISER = "synthesiser"
    VALIDITY_ASSESSOR = "validity_assessor"


class Provider(Base):
    """A configured LLM service that supplies models for agent inference.

    Stores provider credentials (encrypted) and metadata. Disabling a
    provider makes all its models unavailable for new agent assignments.
    Uses optimistic locking (``version_id``) to detect concurrent edits.
    """

    __tablename__ = "provider"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_type: Mapped[ProviderType] = mapped_column(
        Enum(ProviderType, name="providertype"), nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    api_key_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
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

    available_models: Mapped[list[AvailableModel]] = relationship(
        "AvailableModel", back_populates="provider", cascade="all, delete-orphan"
    )
    agents: Mapped[list[Agent]] = relationship("Agent", back_populates="provider")

    __mapper_args__ = {"version_id_col": version_id}

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<Provider id={self.id} type={self.provider_type} name={self.display_name!r}>"


class AvailableModel(Base):
    """An individual model offered by a Provider, discovered via its catalog API.

    Model identifiers are provider-native (e.g. ``claude-sonnet-4-6`` for
    Anthropic). The ``(provider_id, model_identifier)`` pair is unique.
    Disabling a model prevents it from being selected for new agents.
    Uses optimistic locking (``version_id``) to detect concurrent edits.
    """

    __tablename__ = "available_model"
    __table_args__ = (
        UniqueConstraint("provider_id", "model_identifier", name="uq_available_model"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("provider.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_identifier: Mapped[str] = mapped_column(String(200), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
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

    provider: Mapped[Provider] = relationship("Provider", back_populates="available_models")
    agents: Mapped[list[Agent]] = relationship("Agent", back_populates="model")

    __mapper_args__ = {"version_id_col": version_id}

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<AvailableModel id={self.id} identifier={self.model_identifier!r}"
            f" enabled={self.is_enabled}>"
        )


class Agent(Base):
    """A fully configured AI participant in the research workflow.

    Combines a task role, a persona, a Jinja2 system-message template, and a
    reference to the :class:`AvailableModel` that drives inference.  The
    ``system_message_undo_buffer`` preserves the previous template for a
    single-level undo when the template is regenerated.
    Uses optimistic locking (``version_id``) to detect concurrent edits.
    """

    __tablename__ = "agent"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type: Mapped[AgentTaskType] = mapped_column(
        Enum(AgentTaskType, name="agenttasktype"), nullable=False
    )
    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role_description: Mapped[str] = mapped_column(Text, nullable=False)
    persona_name: Mapped[str] = mapped_column(String(100), nullable=False)
    persona_description: Mapped[str] = mapped_column(Text, nullable=False)
    persona_svg: Mapped[str | None] = mapped_column(Text, nullable=True)
    system_message_template: Mapped[str] = mapped_column(Text, nullable=False)
    system_message_undo_buffer: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("available_model.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("provider.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
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

    model: Mapped[AvailableModel] = relationship("AvailableModel", back_populates="agents")
    provider: Mapped[Provider] = relationship("Provider", back_populates="agents")

    __mapper_args__ = {"version_id_col": version_id}

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<Agent id={self.id} task={self.task_type}"
            f" role={self.role_name!r} persona={self.persona_name!r}>"
        )
