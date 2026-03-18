# sms-db

SQLAlchemy 2.x async models and Alembic migrations for SMS Researcher.

## Schema Entities

### Study

Represents a systematic research study.

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | Auto-increment |
| `name` | String(255) | Required |
| `study_type` | Enum | `SMS`, `SLR`, `Tertiary`, `Rapid` |
| `status` | Enum | `draft` → `active` → `completed` / `archived` |
| `created_at` | DateTime(tz) | Server default `NOW()` |
| `updated_at` | DateTime(tz) | Server default `NOW()`, auto-updated |

### Paper

Represents a single academic paper.

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | Auto-increment |
| `title` | Text | Required |
| `abstract` | Text | Nullable |
| `doi` | String(255) | Unique, nullable |
| `metadata` | JSON | Flexible bibliographic fields |
| `created_at` | DateTime(tz) | Server default `NOW()` |

### StudyPaper (join table)

Links a `Study` to a `Paper` with an inclusion decision.

| Column | Type | Notes |
|--------|------|-------|
| `study_id` | Integer FK → study.id | Composite PK, CASCADE delete |
| `paper_id` | Integer FK → paper.id | Composite PK, CASCADE delete |
| `inclusion_status` | Enum | `pending`, `included`, `excluded` |

### Provider (added in migration 0012)

Stores LLM provider credentials.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `provider_type` | Enum | `anthropic`, `openai`, `ollama` |
| `display_name` | String | Required |
| `api_key_encrypted` | LargeBinary | Nullable; Fernet-encrypted |
| `base_url` | String | Nullable; used for Ollama |
| `is_enabled` | Boolean | Default `true` |
| `version_id` | Integer | Optimistic locking |
| `created_at` / `updated_at` | DateTime(tz) | Auto-managed |

### AvailableModel (added in migration 0012)

Individual models fetched from a provider's API.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `provider_id` | UUID FK → provider.id | CASCADE delete |
| `model_identifier` | String | API model ID (e.g. `claude-sonnet-4-6`) |
| `display_name` | String | Human-readable label |
| `is_enabled` | Boolean | Default `true` |
| `version_id` | Integer | Optimistic locking |
| `created_at` / `updated_at` | DateTime(tz) | Auto-managed |

Unique constraint: `(provider_id, model_identifier)`.

### Agent (added in migration 0012)

Defines an LLM agent with role, persona, and a Jinja2 system message template.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `task_type` | Enum | `AgentTaskType` values |
| `role_name` / `role_description` | String / Text | Role identity |
| `persona_name` / `persona_description` | String / Text | Persona identity |
| `persona_svg` | Text | Nullable; SVG illustration |
| `system_message_template` | Text | Jinja2 template |
| `system_message_undo_buffer` | Text | Nullable; previous template |
| `model_id` | UUID FK → available_model.id | Nullable, SET NULL on delete |
| `provider_id` | UUID FK → provider.id | Nullable, SET NULL on delete |
| `is_active` | Boolean | Default `true` |
| `version_id` | Integer | Optimistic locking |
| `created_at` / `updated_at` | DateTime(tz) | Auto-managed |

### Reviewer (updated in migration 0012)

`agent_id` UUID FK column added (nullable, SET NULL on delete → `agent` table).

### StudyDatabaseSelection (added in migration 0014)

Tracks which academic database indices are active for a study.

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `study_id` | Integer FK → study.id | Unique, CASCADE delete |
| `selected_indices` | JSON | List of `DatabaseIndex` string values |
| `created_at` / `updated_at` | DateTime(tz) | Auto-managed |

### SearchIntegrationCredential (added in migration 0014)

Stores encrypted API credentials for external academic databases.

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `integration_type` | Enum | `IntegrationType` value (unique) |
| `api_key_encrypted` | LargeBinary | Nullable; Fernet-encrypted |
| `base_url` | String | Nullable |
| `inst_token` | String | Nullable; institutional token |
| `version_id` | Integer | Optimistic locking |
| `last_tested_at` | DateTime(tz) | Nullable |
| `test_status` | Enum | `TestStatus` value |
| `test_message` | Text | Nullable; last test result message |
| `created_at` / `updated_at` | DateTime(tz) | Auto-managed |

### Paper (additions in migration 0014)

| Column | Type | Notes |
|--------|------|-------|
| `full_text_markdown` | Text | Nullable; converted full-text content |
| `full_text_source` | Enum | `FullTextSource`: `unpaywall`, `scihub`, `manual` |
| `full_text_converted_at` | DateTime(tz) | Nullable; when conversion occurred |

## Development

```bash
# From repo root
uv sync

# Run tests with coverage (minimum 85% line coverage required)
uv run --package sms-db pytest db/tests/ --cov=db --cov-report=term-missing

# Mutation testing (run via GitHub Actions workflow_dispatch, or locally)
uv run cosmic-ray run db/cosmic-ray.toml

# Lint and type-check
uv run ruff check db/src
uv run ruff format --check db/src
uv run mypy db/src
```

## Alembic Usage

```bash
# Apply all migrations to head
uv run alembic upgrade head

# Generate a new migration after model changes
uv run alembic revision --autogenerate -m "describe_change"

# Downgrade one step
uv run alembic downgrade -1
```

Migrations live in `db/alembic/versions/`.

| Migration | Description |
|-----------|-------------|
| `0001_initial_schema.py` | Creates `study`, `paper`, `study_paper` tables |
| `0012_models_and_agents.py` | Creates `provider`, `available_model`, `agent` tables; adds `reviewer.agent_id` FK; seeds default provider and agent records |
| `0013_remove_reviewer_agent_name.py` | Stub — signals cleanup debt for `reviewer.agent_name` column (no-op until backfill is complete) |

## Importing from backend

```python
from db.models import Study, Paper, StudyPaper
from db.base import engine_factory, get_session

engine = engine_factory("sqlite+aiosqlite:///./dev.db")

async with get_session(engine) as session:
    study = Study(name="My SMS", study_type="SMS")
    session.add(study)
    await session.commit()
```

The `db` package is a UV workspace member. Backend declares it as a workspace dependency in `backend/pyproject.toml`.
