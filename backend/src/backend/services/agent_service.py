"""AgentService — CRUD and system-message generation for agents (Feature 005).

Handles creation, retrieval, update, and deactivation of Agent records,
as well as Jinja2 template validation, system-message generation via the
AgentGeneratorAgent, and the undo-buffer swap for system message changes.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

import jinja2
import sqlalchemy.exc
from db.models.agents import Agent, AgentTaskType, AvailableModel, Provider, ProviderType
from db.models.study import Reviewer
from db.models import Study, StudyType
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_logger, get_settings
from backend.utils.encryption import decrypt_secret

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Known Jinja2 variable allowlist
# ---------------------------------------------------------------------------

_KNOWN_TEMPLATE_VARS: dict[str, str] = {
    "role_name": "",
    "role_description": "",
    "persona_name": "",
    "persona_description": "",
    "domain": "",
    "study_type": "",
}

# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------


class TemplateRenderError(Exception):
    """Raised when Jinja2 template rendering fails due to an unknown variable.

    Attributes:
        variable_name: The unknown variable name that caused the error, if
            the failure was an UndefinedError.  ``None`` for other errors.

    """

    def __init__(self, message: str, variable_name: str | None = None) -> None:
        """Initialise the error.

        Args:
            message: Human-readable error description.
            variable_name: Optional unknown variable that caused the failure.

        """
        super().__init__(message)
        self.variable_name = variable_name


class TemplateValidationError(Exception):
    """Raised when a system message template fails Jinja2 validation.

    Attributes:
        variable_name: The unknown variable name that caused the error, if
            the failure was an UndefinedError.  ``None`` for syntax errors.

    """

    def __init__(self, message: str, variable_name: str | None = None) -> None:
        """Initialise the error.

        Args:
            message: Human-readable error description.
            variable_name: Optional unknown variable that caused the failure.

        """
        super().__init__(message)
        self.variable_name = variable_name


class AgentNotFoundError(Exception):
    """Raised when an agent record cannot be located by its ID."""


class AgentGeneratorNotConfiguredError(Exception):
    """Raised when no active AgentGenerator agent record exists in the database."""


class AgentHasDependentsError(Exception):
    """Raised when deactivating an agent that is still referenced by Reviewers.

    Attributes:
        reviewer_ids: List of dependent Reviewer primary keys.

    """

    def __init__(self, reviewer_ids: list[int]) -> None:
        """Initialise the error.

        Args:
            reviewer_ids: Primary keys of Reviewer rows that reference the agent.

        """
        super().__init__(
            f"Agent has {len(reviewer_ids)} dependent reviewer(s): {reviewer_ids}"
        )
        self.reviewer_ids = reviewer_ids


class PersonaSvgGenerationError(Exception):
    """Raised when the LLM returns an invalid SVG string during persona generation."""


class NoUndoBufferError(Exception):
    """Raised when restore_system_message is called but the undo buffer is NULL."""


class StaleVersionError(Exception):
    """Raised when an optimistic-lock version_id check fails during update."""


# ---------------------------------------------------------------------------
# Helper dataclasses
# ---------------------------------------------------------------------------


@dataclass
class AgentUpdate:
    """Input schema for partially updating an existing Agent record.

    All fields are optional — only non-``None`` values are applied.

    Attributes:
        version_id: Optimistic-locking counter.  Must match the current DB
            value; raises :class:`sqlalchemy.exc.StaleDataError` if stale.
        task_type: New AgentTaskType string value, or ``None`` to keep.
        role_name: New role label, or ``None`` to keep.
        role_description: New role description, or ``None`` to keep.
        persona_name: New persona name, or ``None`` to keep.
        persona_description: New persona description, or ``None`` to keep.
        persona_svg: New SVG markup (may be ``None`` to clear).
        system_message_template: New Jinja2 template, or ``None`` to keep.
        model_id: New model UUID, or ``None`` to keep.
        provider_id: New provider UUID, or ``None`` to keep.
        is_active: New activation status, or ``None`` to keep.

    """

    version_id: int = 0
    task_type: str | None = None
    role_name: str | None = None
    role_description: str | None = None
    persona_name: str | None = None
    persona_description: str | None = None
    persona_svg: str | None = field(default=None, metadata={"sentinel": True})
    system_message_template: str | None = None
    model_id: uuid.UUID | None = None
    provider_id: uuid.UUID | None = None
    is_active: bool | None = None


@dataclass
class AgentCreate:
    """Input schema for creating a new Agent record.

    Attributes:
        task_type: One of the :class:`AgentTaskType` enum values.
        role_name: Short functional role label.
        role_description: Plain-text description of what the role does.
        persona_name: Human-readable persona name.
        persona_description: Narrative persona background.
        system_message_template: Jinja2 template string.
        model_id: UUID of the :class:`AvailableModel` to assign.
        provider_id: UUID of the :class:`Provider` (must match model's provider).
        persona_svg: Optional raw SVG markup.

    """

    task_type: str
    role_name: str
    role_description: str
    persona_name: str
    persona_description: str
    system_message_template: str
    model_id: uuid.UUID
    provider_id: uuid.UUID
    persona_svg: str | None = None


@dataclass
class StudyContext:
    """Context values derived from a Study for template rendering.

    Attributes:
        domain: Human-readable domain label (e.g. the study topic).
        study_type: Human-readable study type label (e.g. "Systematic Mapping Study").

    """

    domain: str
    study_type: str


@dataclass
class _DbProviderConfig:
    """Concrete :class:`ProviderConfig` built from database records.

    Attributes:
        model_string: Fully-qualified LiteLLM model string.
        api_base: Optional base URL override for Ollama.
        api_key: Decrypted plaintext API key, or ``None`` for Ollama.

    """

    model_string: str
    api_base: str | None
    api_key: str | None


# ---------------------------------------------------------------------------
# Jinja2 template validation
# ---------------------------------------------------------------------------


def _validate_template(template_str: str) -> None:
    """Validate a Jinja2 template string against the known-variable allowlist.

    First checks that the template parses without syntax errors, then attempts
    to render it with all known variables bound to empty-string placeholder
    values.  Any ``UndefinedError`` means an unknown variable is referenced.

    Args:
        template_str: The raw Jinja2 template string to validate.

    Raises:
        TemplateValidationError: If the template has a syntax error or
            references a variable not in the allowlist.

    """
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)  # noqa: B008
    try:
        template = env.from_string(template_str)
    except jinja2.TemplateSyntaxError as exc:
        raise TemplateValidationError(
            f"Jinja2 syntax error in system message template: {exc}"
        ) from exc

    try:
        template.render(**_KNOWN_TEMPLATE_VARS)
    except jinja2.UndefinedError as exc:
        # Extract the variable name from the error message when possible
        var_name = str(exc).split("'")[1] if "'" in str(exc) else None
        raise TemplateValidationError(
            f"Template references unknown variable: {exc}",
            variable_name=var_name,
        ) from exc


# ---------------------------------------------------------------------------
# Study-context helpers (T058-T059)
# ---------------------------------------------------------------------------

# Map StudyType enum values to human-readable labels
_STUDY_TYPE_LABELS: dict[str, str] = {
    StudyType.SMS.value: "Systematic Mapping Study",
    StudyType.SLR.value: "Systematic Literature Review",
    StudyType.TERTIARY.value: "Tertiary Study",
    StudyType.RAPID.value: "Rapid Review",
}

_DEFAULT_DOMAIN = "Software Engineering and Artificial Intelligence"


def build_study_context(study: Study) -> StudyContext:
    """Build a :class:`StudyContext` from a Study ORM record.

    Maps the ``study_type`` enum to a human-readable label and uses the
    study ``topic`` as the domain (falling back to the default when absent).

    Args:
        study: The :class:`Study` ORM instance to derive context from.

    Returns:
        :class:`StudyContext` with ``domain`` and ``study_type`` strings.

    """
    study_type_str = (
        study.study_type.value
        if hasattr(study.study_type, "value")
        else str(study.study_type)
    )
    study_type_label = _STUDY_TYPE_LABELS.get(study_type_str, study_type_str)
    domain = study.topic if study.topic else _DEFAULT_DOMAIN
    return StudyContext(domain=domain, study_type=study_type_label)


def render_system_message(
    template: str,
    agent: Agent,
    domain: str,
    study_type: str,
) -> str:
    """Render a Jinja2 system message template with agent and study context.

    Binds all six known template variables (role_name, role_description,
    persona_name, persona_description, domain, study_type) and renders
    using :class:`jinja2.StrictUndefined` so any unknown variable raises
    a :class:`TemplateRenderError`.

    Args:
        template: Jinja2 template string to render.
        agent: :class:`Agent` ORM record supplying role/persona values.
        domain: Human-readable domain label (e.g. study topic).
        study_type: Human-readable study type label.

    Returns:
        Rendered system message string.

    Raises:
        TemplateRenderError: If the template references an unknown variable.

    """
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)  # noqa: B008
    tmpl = env.from_string(template)
    context = {
        "role_name": agent.role_name,
        "role_description": agent.role_description,
        "persona_name": agent.persona_name,
        "persona_description": agent.persona_description,
        "domain": domain,
        "study_type": study_type,
    }
    try:
        return tmpl.render(**context)
    except jinja2.UndefinedError as exc:
        var_name = str(exc).split("'")[1] if "'" in str(exc) else None
        raise TemplateRenderError(
            f"Template references unknown variable: {exc}",
            variable_name=var_name,
        ) from exc


# ---------------------------------------------------------------------------
# AgentService
# ---------------------------------------------------------------------------


class AgentService:
    """CRUD and generation operations for Agent records.

    All methods accept an :class:`AsyncSession` as their last argument and
    do not manage transactions themselves — the caller is responsible for
    ``session.commit()`` / ``session.rollback()``.
    """

    # ------------------------------------------------------------------
    # Task-type enumeration
    # ------------------------------------------------------------------

    @staticmethod
    def get_agent_task_types() -> list[str]:
        """Return all valid agent task type values as strings.

        Returns:
            Sorted list of :class:`AgentTaskType` enum string values.

        """
        return sorted(t.value for t in AgentTaskType)

    # ------------------------------------------------------------------
    # CRUD — create
    # ------------------------------------------------------------------

    async def create_agent(
        self,
        data: AgentCreate,
        session: AsyncSession,
    ) -> Agent:
        """Persist a new Agent record after validating all constraints.

        Validation steps:

        1. ``model_id`` must reference an *enabled* :class:`AvailableModel`.
        2. The model's ``provider_id`` must equal ``data.provider_id``.
        3. ``system_message_template`` must pass Jinja2 syntax and unknown-
           variable checks (see :func:`_validate_template`).

        Args:
            data: :class:`AgentCreate` with all required fields.
            session: Active async database session.

        Returns:
            The newly created :class:`Agent` ORM instance (not yet committed).

        Raises:
            ValueError: If the model is not found, is disabled, or the
                provider_id does not match the model's provider.
            TemplateValidationError: If the template fails Jinja2 validation.

        """
        # 1. Load and validate model
        model_result = await session.execute(
            select(AvailableModel).where(AvailableModel.id == data.model_id)
        )
        model = model_result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"AvailableModel {data.model_id} not found")
        if not model.is_enabled:
            raise ValueError(f"AvailableModel {data.model_id} is disabled")
        if model.provider_id != data.provider_id:
            raise ValueError(
                f"Model provider_id {model.provider_id} does not match "
                f"supplied provider_id {data.provider_id}"
            )

        # 2. Validate Jinja2 template (syntax + known-variable allowlist)
        _validate_template(data.system_message_template)

        # 2b. Validate template renders with dummy context values (T060)
        _dummy_agent = Agent(
            task_type=AgentTaskType(data.task_type),
            role_name=data.role_name,
            role_description=data.role_description,
            persona_name=data.persona_name,
            persona_description=data.persona_description,
            system_message_template=data.system_message_template,
            model_id=data.model_id,
            provider_id=data.provider_id,
        )
        render_system_message(
            data.system_message_template,
            _dummy_agent,
            domain="[domain]",
            study_type="[study_type]",
        )

        # 3. Persist
        agent = Agent(
            task_type=AgentTaskType(data.task_type),
            role_name=data.role_name,
            role_description=data.role_description,
            persona_name=data.persona_name,
            persona_description=data.persona_description,
            persona_svg=data.persona_svg,
            system_message_template=data.system_message_template,
            model_id=data.model_id,
            provider_id=data.provider_id,
        )
        session.add(agent)
        await session.flush()
        logger.info("agent_created", agent_id=str(agent.id), task_type=data.task_type)
        return agent

    # ------------------------------------------------------------------
    # CRUD — list
    # ------------------------------------------------------------------

    async def list_agents(
        self,
        session: AsyncSession,
        *,
        task_type: str | None = None,
        is_active: bool | None = None,
    ) -> list[Agent]:
        """Return a list of Agent records with optional filters.

        Args:
            session: Active async database session.
            task_type: Optional filter by :class:`AgentTaskType` value string.
            is_active: Optional filter by activation status.

        Returns:
            List of :class:`Agent` instances ordered by role_name.

        """
        query = select(Agent)
        if task_type is not None:
            query = query.where(Agent.task_type == AgentTaskType(task_type))
        if is_active is not None:
            query = query.where(Agent.is_active == is_active)
        query = query.order_by(Agent.role_name)
        result = await session.execute(query)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # CRUD — get
    # ------------------------------------------------------------------

    async def get_agent(
        self,
        agent_id: uuid.UUID,
        session: AsyncSession,
    ) -> Agent:
        """Return a single Agent by its primary key.

        Args:
            agent_id: UUID of the agent to load.
            session: Active async database session.

        Returns:
            The :class:`Agent` ORM instance.

        Raises:
            AgentNotFoundError: If no agent with ``agent_id`` exists.

        """
        result = await session.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found")
        return agent

    # ------------------------------------------------------------------
    # CRUD — update
    # ------------------------------------------------------------------

    async def update_agent(
        self,
        agent_id: uuid.UUID,
        data: AgentUpdate,
        session: AsyncSession,
    ) -> Agent:
        """Apply a partial update to an Agent record.

        Only non-``None`` fields in *data* are applied.  The
        ``system_message_template`` field is validated with
        :func:`_validate_template` before being written.

        Optimistic locking is enforced via ``version_id``: if
        ``data.version_id`` does not match the current DB value, a
        :class:`sqlalchemy.exc.StaleDataError` is raised.

        Args:
            agent_id: UUID of the agent to update.
            data: :class:`AgentUpdate` with the fields to change.
            session: Active async database session.

        Returns:
            The updated :class:`Agent` ORM instance (not yet committed).

        Raises:
            AgentNotFoundError: If no agent with ``agent_id`` exists.
            sqlalchemy.exc.StaleDataError: If ``data.version_id`` is stale.
            ValueError: If the model/provider constraint is violated.
            TemplateValidationError: If ``system_message_template`` is invalid.

        """
        agent = await self.get_agent(agent_id, session)

        # Optimistic locking check
        if agent.version_id != data.version_id:
            raise StaleVersionError(
                f"Agent {agent_id} has been modified by another request "
                f"(expected version_id={data.version_id}, got {agent.version_id})"
            )

        if data.task_type is not None:
            agent.task_type = AgentTaskType(data.task_type)
        if data.role_name is not None:
            agent.role_name = data.role_name
        if data.role_description is not None:
            agent.role_description = data.role_description
        if data.persona_name is not None:
            agent.persona_name = data.persona_name
        if data.persona_description is not None:
            agent.persona_description = data.persona_description
        if data.persona_svg is not None:
            agent.persona_svg = data.persona_svg
        if data.is_active is not None:
            agent.is_active = data.is_active

        # Model / provider update with consistency check
        new_model_id = data.model_id or agent.model_id
        new_provider_id = data.provider_id or agent.provider_id
        if data.model_id is not None or data.provider_id is not None:
            model_result = await session.execute(
                select(AvailableModel).where(AvailableModel.id == new_model_id)
            )
            model = model_result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"AvailableModel {new_model_id} not found")
            if not model.is_enabled:
                raise ValueError(f"AvailableModel {new_model_id} is disabled")
            if model.provider_id != new_provider_id:
                raise ValueError(
                    f"Model provider_id {model.provider_id} does not match "
                    f"supplied provider_id {new_provider_id}"
                )
            agent.model_id = new_model_id
            agent.provider_id = new_provider_id

        if data.system_message_template is not None:
            _validate_template(data.system_message_template)
            # Validate renders with dummy context (T060)
            render_system_message(
                data.system_message_template,
                agent,
                domain="[domain]",
                study_type="[study_type]",
            )
            agent.system_message_template = data.system_message_template

        await session.flush()
        logger.info("agent_updated", agent_id=str(agent_id))
        return agent

    # ------------------------------------------------------------------
    # CRUD — deactivate
    # ------------------------------------------------------------------

    async def deactivate_agent(
        self,
        agent_id: uuid.UUID,
        session: AsyncSession,
    ) -> Agent:
        """Soft-delete an agent by setting ``is_active = False``.

        Raises :class:`AgentHasDependentsError` when any ``Reviewer`` row
        still references this agent via ``agent_id``.

        Args:
            agent_id: UUID of the agent to deactivate.
            session: Active async database session.

        Returns:
            The updated :class:`Agent` ORM instance (not yet committed).

        Raises:
            AgentNotFoundError: If no agent with ``agent_id`` exists.
            AgentHasDependentsError: If active Reviewer rows reference the agent.

        """
        reviewer_result = await session.execute(
            select(Reviewer).where(Reviewer.agent_id == agent_id)
        )
        reviewers = reviewer_result.scalars().all()
        if reviewers:
            raise AgentHasDependentsError([r.id for r in reviewers])

        agent = await self.get_agent(agent_id, session)
        agent.is_active = False
        await session.flush()
        logger.info("agent_deactivated", agent_id=str(agent_id))
        return agent

    # ------------------------------------------------------------------
    # Undo system message
    # ------------------------------------------------------------------

    async def restore_system_message(
        self,
        agent_id: uuid.UUID,
        session: AsyncSession,
    ) -> Agent:
        """Swap ``system_message_template`` with ``system_message_undo_buffer``.

        After the swap the undo buffer holds the previous template, so an
        immediate second call to this method will restore the original.

        Args:
            agent_id: UUID of the agent.
            session: Active async database session.

        Returns:
            The updated :class:`Agent` ORM instance (not yet committed).

        Raises:
            AgentNotFoundError: If no agent with ``agent_id`` exists.
            NoUndoBufferError: If ``system_message_undo_buffer`` is ``NULL``.

        """
        agent = await self.get_agent(agent_id, session)
        if not agent.system_message_undo_buffer:
            raise NoUndoBufferError(
                f"Agent {agent_id} has no previous system message to restore"
            )
        current = agent.system_message_template
        agent.system_message_template = agent.system_message_undo_buffer
        agent.system_message_undo_buffer = current
        await session.flush()
        logger.info("system_message_restored", agent_id=str(agent_id))
        return agent

    # ------------------------------------------------------------------
    # System-message generation
    # ------------------------------------------------------------------

    async def generate_system_message(
        self,
        agent_id: uuid.UUID,
        session: AsyncSession,
    ) -> str:
        """Generate (or regenerate) the system message template for an Agent.

        Locates the bootstrap ``agent_generator`` Agent in the database, builds
        a :class:`_DbProviderConfig` from its provider record (decrypting the
        API key), instantiates :class:`AgentGeneratorAgent`, and calls
        ``generate_system_message``.

        If the target agent already has a ``system_message_template``, the
        existing value is moved to ``system_message_undo_buffer`` before the
        new template is written.  The session is flushed but **not committed**.

        Args:
            agent_id: UUID of the :class:`Agent` whose system message to
                regenerate.
            session: Active async database session.

        Returns:
            The newly generated Jinja2 template string.

        Raises:
            AgentNotFoundError: If no Agent with ``agent_id`` exists.
            AgentGeneratorNotConfiguredError: If no active ``agent_generator``
                agent record exists in the database.

        """
        # 1. Load target agent
        agent_result = await session.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = agent_result.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found")

        # 2. Load model display name
        model_result = await session.execute(
            select(AvailableModel).where(AvailableModel.id == agent.model_id)
        )
        model = model_result.scalar_one_or_none()
        model_display_name = model.display_name if model else agent.role_name

        # 3. Locate bootstrap AgentGenerator agent
        gen_result = await session.execute(
            select(Agent).where(
                Agent.task_type == AgentTaskType.AGENT_GENERATOR,
                Agent.is_active.is_(True),
            ).limit(1)
        )
        generator_agent = gen_result.scalar_one_or_none()
        if generator_agent is None:
            raise AgentGeneratorNotConfiguredError(
                "No active agent_generator agent is configured. "
                "Create one via POST /api/v1/admin/agents before generating system messages."
            )

        # 4. Build ProviderConfig from the generator agent's provider
        provider_result = await session.execute(
            select(Provider).where(Provider.id == generator_agent.provider_id)
        )
        provider = provider_result.scalar_one_or_none()
        gen_model_result = await session.execute(
            select(AvailableModel).where(AvailableModel.id == generator_agent.model_id)
        )
        gen_model = gen_model_result.scalar_one_or_none()

        provider_config = _build_provider_config(provider, gen_model)

        # 5. Instantiate AgentGeneratorAgent and generate
        from agents.agent_generator import AgentGeneratorAgent  # noqa: PLC0415

        generator = AgentGeneratorAgent()
        new_template = await generator.generate_system_message(
            task_type=agent.task_type.value,
            role_name=agent.role_name,
            role_description=agent.role_description,
            persona_name=agent.persona_name,
            persona_description=agent.persona_description,
            model_display_name=model_display_name,
            provider_config=provider_config,
        )

        # 6. Update undo buffer and set new template
        if agent.system_message_template:
            agent.system_message_undo_buffer = agent.system_message_template
        agent.system_message_template = new_template
        await session.flush()

        logger.info(
            "system_message_generated",
            agent_id=str(agent_id),
            generator_agent_id=str(generator_agent.id),
        )
        return new_template

    # ------------------------------------------------------------------
    # Persona SVG generation
    # ------------------------------------------------------------------

    async def generate_persona_svg(
        self,
        *,
        persona_name: str,
        persona_description: str,
        provider_config: _DbProviderConfig | None = None,
    ) -> str:
        """Generate SVG markup for a persona using an LLM.

        Calls the LLM with a concise prompt requesting ONLY valid SVG markup
        for a simple avatar representing the persona.  Validates that the
        response begins with ``<svg``.

        Args:
            persona_name: Human-readable persona name.
            persona_description: Narrative description of the persona.
            provider_config: Optional database-resolved provider config for
                routing the LLM call.  Falls back to environment settings
                when ``None``.

        Returns:
            Raw SVG markup string starting with ``<svg``.

        Raises:
            PersonaSvgGenerationError: If the LLM response does not start
                with ``<svg`` or if the LLM call fails.

        """
        from agents.core.llm_client import LLMClient  # noqa: PLC0415

        client = LLMClient()
        prompt = (
            f"Generate a simple SVG avatar for a research persona named '{persona_name}'. "
            f"Persona description: {persona_description}\n\n"
            "Requirements:\n"
            "- Output ONLY the raw SVG markup, nothing else\n"
            "- Start with <svg and end with </svg>\n"
            "- Use a viewBox of '0 0 100 100'\n"
            "- Keep it simple: a circle for the head, basic facial features, "
            "and a color scheme that reflects the persona\n"
            "- No comments, no XML declaration, no markdown"
        )
        messages = [
            {"role": "system", "content": "You are an SVG artist. Output only valid SVG markup."},
            {"role": "user", "content": prompt},
        ]
        try:
            raw = await client.complete(messages, provider_config=provider_config, max_tokens=512)
        except Exception as exc:
            raise PersonaSvgGenerationError(f"LLM call failed: {exc}") from exc

        svg = raw.strip()
        if not svg.lower().startswith("<svg"):
            raise PersonaSvgGenerationError(
                f"LLM did not return valid SVG (response: {svg[:80]!r})"
            )
        return svg


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_provider_config(
    provider: Provider | None,
    model: AvailableModel | None,
) -> _DbProviderConfig | None:
    """Construct a :class:`_DbProviderConfig` from DB records.

    Returns ``None`` when either *provider* or *model* is ``None``, signalling
    that the caller should fall back to environment-based settings.

    Args:
        provider: The :class:`Provider` record (may be ``None``).
        model: The :class:`AvailableModel` record (may be ``None``).

    Returns:
        A :class:`_DbProviderConfig` ready for :class:`LLMClient`, or
        ``None`` if the records are unavailable.

    """
    if provider is None or model is None:
        return None

    settings = get_settings()

    # Decrypt API key when present
    api_key: str | None = None
    if provider.api_key_encrypted:
        try:
            api_key = decrypt_secret(provider.api_key_encrypted, settings.secret_key)
        except Exception:  # noqa: BLE001
            logger.warning(
                "api_key_decrypt_failed", provider_id=str(provider.id)
            )

    # Build LiteLLM model string by provider type
    prefix_map = {
        ProviderType.ANTHROPIC: "anthropic",
        ProviderType.OPENAI: "openai",
        ProviderType.OLLAMA: "ollama",
    }
    prefix = prefix_map.get(provider.provider_type, "anthropic")
    model_string = f"{prefix}/{model.model_identifier}"

    return _DbProviderConfig(
        model_string=model_string,
        api_base=provider.base_url,
        api_key=api_key,
    )
