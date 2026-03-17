"""models_and_agents

Revision ID: 0012
Revises: 2f51665cbb6d
Create Date: 2026-03-16 00:00:00.000000

Adds three new tables for Feature 005 (Models & Agents Management):
- ``provider``       — configured LLM services (Anthropic, OpenAI, Ollama)
- ``available_model`` — individual models fetched from each provider's catalog
- ``agent``          — fully configured AI agents with role, persona, and model

Also adds a nullable ``agent_id`` FK column to the existing ``reviewer`` table
to link AI reviewers to the new Agent abstraction (transitional — agent_name
is retained until all rows are migrated).

Seed data (upgrade only):
- Inserts a default Anthropic provider when ANTHROPIC_API_KEY is set.
- Inserts bootstrap AgentGenerator, Screener, and Extractor agent records.
- Backfills reviewer.agent_id for known ai_agent rows.
"""

import base64
import os
import uuid as _uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

# ---------------------------------------------------------------------------
# Fixed seed UUIDs — deterministic across environments and re-runs
# ---------------------------------------------------------------------------

_PROVIDER_ID = _uuid.UUID("00000000-0000-0000-0001-000000000001")
_MODEL_ID = _uuid.UUID("00000000-0000-0000-0001-000000000002")
_AGENT_GENERATOR_ID = _uuid.UUID("00000000-0000-0000-0002-000000000001")
_SCREENER_AGENT_ID = _uuid.UUID("00000000-0000-0000-0002-000000000002")
_EXTRACTOR_AGENT_ID = _uuid.UUID("00000000-0000-0000-0002-000000000003")

# Default model identifier for the seeded Anthropic provider
_DEFAULT_MODEL_IDENTIFIER = "claude-haiku-4-5-20251001"
_DEFAULT_MODEL_DISPLAY_NAME = "Claude Haiku 4.5"

# ---------------------------------------------------------------------------
# Default system message templates — derived from existing prompt content
# ---------------------------------------------------------------------------

_AGENT_GENERATOR_TEMPLATE = (
    "You are {{ persona_name }}, an expert AI agent designer for {{ domain }} research.\n\n"
    "{{ persona_description }}\n\n"
    "Your role is {{ role_name }}: {{ role_description }}\n\n"
    "You specialise in {{ study_type }} workflows. "
    "Produce Jinja2 system message templates that incorporate the six standard "
    "placeholder variables: role_name, role_description, persona_name, "
    "persona_description, domain, and study_type.\n\n"
    "Output only the raw template string — no code fences, no markdown headings."
)

_SCREENER_TEMPLATE = (
    "You are {{ persona_name }}, a {{ role_name }} for {{ domain }} research.\n\n"
    "{{ persona_description }}\n\n"
    "{{ role_description }}\n\n"
    "Your task is to evaluate whether a paper's abstract meets the inclusion criteria "
    "for a {{ study_type }}.\n\n"
    "## Role\n\n"
    "- Analyse the abstract objectively and impartially.\n"
    "- Apply the inclusion and exclusion criteria strictly.\n"
    "- Provide a clear decision: **include** or **exclude**.\n"
    "- Briefly justify your decision in one or two sentences.\n\n"
    "## Output Format\n\n"
    "Respond in the following format only:\n\n"
    "Decision: include | exclude\n"
    "Reason: <one or two sentence justification>\n\n"
    "Do not include any additional text outside this format."
)

_EXTRACTOR_TEMPLATE = (
    "You are {{ persona_name }}, a {{ role_name }} for {{ domain }} research.\n\n"
    "{{ persona_description }}\n\n"
    "{{ role_description }}\n\n"
    "Your task is to extract structured data fields from a paper processed as part of "
    "a {{ study_type }}, then classify the paper's research type.\n\n"
    "Extract only what is explicitly stated in the paper text or metadata. "
    "Do not infer or hallucinate values not present in the source material. "
    "If a field cannot be determined, use null.\n\n"
    "Return a single valid JSON object matching the extraction schema."
)


# ---------------------------------------------------------------------------
# Internal: minimal Fernet encryption (mirrors backend/utils/encryption.py)
# ---------------------------------------------------------------------------

def _encrypt_api_key(plaintext: str, secret_key: str) -> bytes:
    """Fernet-encrypt an API key using the same algorithm as the backend utility.

    Args:
        plaintext: The raw API key string.
        secret_key: Application SECRET_KEY from environment.

    Returns:
        Fernet ciphertext bytes for storage in ``api_key_encrypted``.
    """
    from cryptography.fernet import Fernet  # noqa: PLC0415
    from cryptography.hazmat.primitives import hashes  # noqa: PLC0415
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # noqa: PLC0415

    _SALT = b"sms-researcher-v1"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_SALT,
        iterations=390_000,
    )
    raw = kdf.derive(secret_key.encode("utf-8"))
    key = base64.urlsafe_b64encode(raw)
    return Fernet(key).encrypt(plaintext.encode("utf-8"))

# revision identifiers, used by Alembic.
revision: str = "0012"
down_revision: str | None = "2f51665cbb6d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply migration: create provider, available_model, agent tables and reviewer FK."""
    # --- Enums -----------------------------------------------------------
    providertype = sa.Enum(
        "anthropic", "openai", "ollama", name="providertype", create_type=True
    )
    agenttasktype = sa.Enum(
        "screener",
        "extractor",
        "librarian",
        "expert",
        "quality_judge",
        "agent_generator",
        "domain_modeler",
        "synthesiser",
        "validity_assessor",
        name="agenttasktype",
        create_type=True,
    )
    providertype.create(op.get_bind(), checkfirst=True)
    agenttasktype.create(op.get_bind(), checkfirst=True)

    # --- provider table --------------------------------------------------
    op.create_table(
        "provider",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "provider_type",
            sa.Enum("anthropic", "openai", "ollama", name="providertype", create_type=False),
            nullable=False,
        ),
        sa.Column("display_name", sa.String(100), nullable=False, unique=True),
        sa.Column("api_key_encrypted", sa.LargeBinary, nullable=True),
        sa.Column("base_url", sa.String(500), nullable=True),
        sa.Column(
            "is_enabled",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "version_id",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # --- available_model table -------------------------------------------
    op.create_table(
        "available_model",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "provider_id",
            UUID(as_uuid=True),
            sa.ForeignKey("provider.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("model_identifier", sa.String(200), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column(
            "is_enabled",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "version_id",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("provider_id", "model_identifier", name="uq_available_model"),
    )

    # --- agent table -----------------------------------------------------
    op.create_table(
        "agent",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "task_type",
            sa.Enum(
                "screener",
                "extractor",
                "librarian",
                "expert",
                "quality_judge",
                "agent_generator",
                "domain_modeler",
                "synthesiser",
                "validity_assessor",
                name="agenttasktype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("role_name", sa.String(100), nullable=False),
        sa.Column("role_description", sa.Text, nullable=False),
        sa.Column("persona_name", sa.String(100), nullable=False),
        sa.Column("persona_description", sa.Text, nullable=False),
        sa.Column("persona_svg", sa.Text, nullable=True),
        sa.Column("system_message_template", sa.Text, nullable=False),
        sa.Column("system_message_undo_buffer", sa.Text, nullable=True),
        sa.Column(
            "model_id",
            UUID(as_uuid=True),
            sa.ForeignKey("available_model.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "provider_id",
            UUID(as_uuid=True),
            sa.ForeignKey("provider.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "version_id",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # --- reviewer.agent_id FK column ------------------------------------
    op.add_column(
        "reviewer",
        sa.Column(
            "agent_id",
            UUID(as_uuid=True),
            sa.ForeignKey("agent.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
    )

    # === T053: Seed block ================================================
    # All inserts are conditional (INSERT … WHERE NOT EXISTS) so the
    # migration is safe to re-run or apply to a partially seeded database.

    bind = op.get_bind()

    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    secret_key = os.environ.get("SECRET_KEY", "")

    now_expr = sa.text("CURRENT_TIMESTAMP")

    # --- Seed default Anthropic provider (when ANTHROPIC_API_KEY is set) ---
    if anthropic_api_key and secret_key:
        encrypted_key: bytes | None = _encrypt_api_key(anthropic_api_key, secret_key)
    elif anthropic_api_key:
        # Store as base64-encoded plaintext when SECRET_KEY not available
        # (development / CI environments); the backend will handle decryption
        # using whatever SECRET_KEY is configured at runtime.
        encrypted_key = base64.b64encode(anthropic_api_key.encode("utf-8"))
    else:
        encrypted_key = None

    provider_exists = bind.execute(
        sa.text("SELECT 1 FROM provider WHERE id = :id"),
        {"id": str(_PROVIDER_ID)},
    ).first()

    if not provider_exists:
        bind.execute(
            sa.text(
                "INSERT INTO provider "
                "(id, provider_type, display_name, api_key_encrypted, base_url, "
                "is_enabled, version_id, created_at, updated_at) "
                "VALUES (:id, 'anthropic', :display_name, :api_key, NULL, "
                "TRUE, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {
                "id": str(_PROVIDER_ID),
                "display_name": "Anthropic (Default)",
                "api_key": encrypted_key,
            },
        )

    # --- Seed default model ---
    model_exists = bind.execute(
        sa.text("SELECT 1 FROM available_model WHERE id = :id"),
        {"id": str(_MODEL_ID)},
    ).first()

    if not model_exists:
        bind.execute(
            sa.text(
                "INSERT INTO available_model "
                "(id, provider_id, model_identifier, display_name, is_enabled, "
                "version_id, created_at, updated_at) "
                "VALUES (:id, :provider_id, :model_id_str, :display_name, "
                "TRUE, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {
                "id": str(_MODEL_ID),
                "provider_id": str(_PROVIDER_ID),
                "model_id_str": _DEFAULT_MODEL_IDENTIFIER,
                "display_name": _DEFAULT_MODEL_DISPLAY_NAME,
            },
        )

    # --- Seed AgentGenerator bootstrap agent ---
    gen_exists = bind.execute(
        sa.text("SELECT 1 FROM agent WHERE id = :id"),
        {"id": str(_AGENT_GENERATOR_ID)},
    ).first()

    if not gen_exists:
        bind.execute(
            sa.text(
                "INSERT INTO agent "
                "(id, task_type, role_name, role_description, persona_name, "
                "persona_description, persona_svg, system_message_template, "
                "system_message_undo_buffer, model_id, provider_id, is_active, "
                "version_id, created_at, updated_at) "
                "VALUES (:id, 'agent_generator', 'Agent Generator', "
                ":role_desc, 'Dr. Genesis', "
                ":persona_desc, NULL, :template, NULL, :model_id, :provider_id, "
                "TRUE, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {
                "id": str(_AGENT_GENERATOR_ID),
                "role_desc": "Generates Jinja2 system message templates for research agents",
                "persona_desc": (
                    "An expert AI agent designer specialised in systematic literature "
                    "review and systematic mapping study research workflows"
                ),
                "template": _AGENT_GENERATOR_TEMPLATE,
                "model_id": str(_MODEL_ID),
                "provider_id": str(_PROVIDER_ID),
            },
        )

    # --- Seed Screener agent ---
    screener_exists = bind.execute(
        sa.text("SELECT 1 FROM agent WHERE id = :id"),
        {"id": str(_SCREENER_AGENT_ID)},
    ).first()

    if not screener_exists:
        bind.execute(
            sa.text(
                "INSERT INTO agent "
                "(id, task_type, role_name, role_description, persona_name, "
                "persona_description, persona_svg, system_message_template, "
                "system_message_undo_buffer, model_id, provider_id, is_active, "
                "version_id, created_at, updated_at) "
                "VALUES (:id, 'screener', 'Screener', "
                ":role_desc, 'Dr. Aria', "
                ":persona_desc, NULL, :template, NULL, :model_id, :provider_id, "
                "TRUE, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {
                "id": str(_SCREENER_AGENT_ID),
                "role_desc": (
                    "Determines whether a paper meets inclusion criteria for a "
                    "systematic study by analysing its abstract"
                ),
                "persona_desc": (
                    "A meticulous systematic reviewer with expertise in software "
                    "engineering and AI research, known for rigorous and impartial "
                    "paper screening"
                ),
                "template": _SCREENER_TEMPLATE,
                "model_id": str(_MODEL_ID),
                "provider_id": str(_PROVIDER_ID),
            },
        )

    # --- Seed Extractor agent ---
    extractor_exists = bind.execute(
        sa.text("SELECT 1 FROM agent WHERE id = :id"),
        {"id": str(_EXTRACTOR_AGENT_ID)},
    ).first()

    if not extractor_exists:
        bind.execute(
            sa.text(
                "INSERT INTO agent "
                "(id, task_type, role_name, role_description, persona_name, "
                "persona_description, persona_svg, system_message_template, "
                "system_message_undo_buffer, model_id, provider_id, is_active, "
                "version_id, created_at, updated_at) "
                "VALUES (:id, 'extractor', 'Extractor', "
                ":role_desc, 'Dr. Atlas', "
                ":persona_desc, NULL, :template, NULL, :model_id, :provider_id, "
                "TRUE, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {
                "id": str(_EXTRACTOR_AGENT_ID),
                "role_desc": (
                    "Extracts structured data fields from paper text and classifies "
                    "the paper's research type using R1-R6 decision rules"
                ),
                "persona_desc": (
                    "A systematic data extraction specialist with deep knowledge of "
                    "research classification frameworks and structured information "
                    "extraction from academic literature"
                ),
                "template": _EXTRACTOR_TEMPLATE,
                "model_id": str(_MODEL_ID),
                "provider_id": str(_PROVIDER_ID),
            },
        )

    # === T054: Backfill block =============================================
    # Update reviewer.agent_id for ai_agent rows whose agent_name matches
    # a known seeded agent.  Unknown agent_name values are skipped silently.

    _AGENT_NAME_TO_ID = {
        "screener": str(_SCREENER_AGENT_ID),
        "Screener": str(_SCREENER_AGENT_ID),
        "ScreenerAgent": str(_SCREENER_AGENT_ID),
        "extractor": str(_EXTRACTOR_AGENT_ID),
        "Extractor": str(_EXTRACTOR_AGENT_ID),
        "ExtractorAgent": str(_EXTRACTOR_AGENT_ID),
    }

    for agent_name, agent_id_str in _AGENT_NAME_TO_ID.items():
        bind.execute(
            sa.text(
                "UPDATE reviewer SET agent_id = :agent_id "
                "WHERE reviewer_type = 'ai_agent' "
                "AND agent_name = :agent_name "
                "AND agent_id IS NULL"
            ),
            {"agent_id": agent_id_str, "agent_name": agent_name},
        )


def downgrade() -> None:
    """Reverse migration: drop agent_id column and all three tables."""
    op.drop_column("reviewer", "agent_id")
    op.drop_table("agent")
    op.drop_table("available_model")
    op.drop_table("provider")

    # Drop enums last (after tables that reference them are gone).
    sa.Enum(name="agenttasktype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="providertype").drop(op.get_bind(), checkfirst=True)
