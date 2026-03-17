# Changelog — sms-db

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — feature/005-models-and-agents

### Added
- **`ProviderType` StrEnum**: `anthropic`, `openai`, `ollama`
- **`AgentTaskType` StrEnum**: `screener`, `extractor`, `librarian`, `expert`, `quality_judge`,
  `agent_generator`, `domain_modeler`, `synthesiser`, `validity_assessor`
- **`Provider` model**: UUID PK; `provider_type`, `display_name`, `api_key_encrypted`
  (LargeBinary, nullable), `base_url` (nullable), `is_enabled`, `version_id` (optimistic
  locking), `created_at`, `updated_at`
- **`AvailableModel` model**: UUID PK; `provider_id` FK (CASCADE delete), `model_identifier`,
  `display_name`, `is_enabled`, `version_id`, `created_at`, `updated_at`; unique constraint
  on `(provider_id, model_identifier)`
- **`Agent` model**: UUID PK; `task_type`, role/persona fields, `system_message_template`,
  `system_message_undo_buffer`, `model_id` FK (SET NULL), `provider_id` FK (SET NULL),
  `is_active`, `version_id`, `created_at`, `updated_at`; SQLAlchemy optimistic locking via
  `__mapper_args__ = {"version_id_col": version_id}`
- **Migration `0012_models_and_agents`**: creates PostgreSQL enums for `ProviderType` and
  `AgentTaskType`; creates `provider`, `available_model`, and `agent` tables; adds nullable
  `agent_id` UUID FK to `reviewer`; seeds a default Anthropic provider (when
  `ANTHROPIC_API_KEY` is set), bootstrap `AgentGenerator` agent, `Screener` agent, and
  `Extractor` agent; backfills `reviewer.agent_id` for rows matching known agent names;
  `downgrade()` reverses all steps in order
- **Stub migration `0013_remove_reviewer_agent_name`**: `upgrade()` is a no-op comment
  signalling cleanup debt; `downgrade()` is a no-op
- Integration test `test_migration_0012.py`: verifies table creation, seed records, and clean
  downgrade
- Exports in `db/src/db/models/__init__.py`: `ProviderType`, `AgentTaskType`, `Provider`,
  `AvailableModel`, `Agent`

### Changed
- `Reviewer` model: added nullable `agent_id` UUID FK → `agent.id` (SET NULL on delete);
  existing `agent_name` column retained

---

## [Unreleased] — feature/003-project-setup-improvements

### Changed
- Coverage command documented in `CLAUDE.md`: `uv run pytest db/tests/ --cov=db`
- Mutation testing tool updated to `cosmic-ray` (was `mutmut`); run via manual GitHub
  Actions `workflow_dispatch` workflow
- `pytest` build gate enforced: skip/xfail markers without `reason=` cause the run to fail

---

## [0.2.0] — 2026-03-12 — feature/002-sms-workflow

### Added
- `Study` model: `id`, `name`, `study_type` (SMS/SLR/Tertiary/Rapid), `status`
  (draft/active/completed/archived), `created_at`, `updated_at`
- `Paper` model: `id`, `title`, `abstract`, `doi` (unique), `metadata` (JSON),
  `created_at`
- `StudyPaper` join table: composite PK (`study_id`, `paper_id`),
  `inclusion_status` (pending/included/excluded), CASCADE deletes
- Alembic migration `0001_initial_schema.py` creating all three tables
- `engine_factory()` — async SQLAlchemy engine factory supporting PostgreSQL and SQLite
- `get_session()` — async context manager for session lifecycle management
- Async-compatible `alembic/env.py` for programmatic migration application
- Integration tests using `aiosqlite` (SQLite in-memory)

---

## [0.1.0] — 2026-03-11 — feature/001-repo-setup

### Added
- Initial `pyproject.toml` (`sms-db`) as UV workspace member
- SQLAlchemy 2.x async + Alembic dependency baseline
- Ruff, MyPy strict, pytest + pytest-asyncio configuration
