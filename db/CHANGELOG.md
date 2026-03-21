# Changelog — sms-db

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.7.0] — 2026-03-21 — feature/007-slr-workflow

### Added
- **`ReviewProtocol`** ORM model (`db/src/db/models/slr.py`): PICO/S fields, synthesis approach
  enum, status lifecycle (`draft` → `validated`); FK to `study`
- **`ProtocolReviewReport`** ORM: per-section strengths/weaknesses/recommendations from AI review
- **`QualityChecklist`** + **`QualityChecklistItem`** ORM: configurable checklists with binary/
  numeric scoring methods and weights
- **`QualityScore`** ORM: per-reviewer scores for individual checklist items
- **`SynthesisResult`** ORM: stores approach, status, computed statistics, Forest/Funnel plot SVG,
  qualitative themes, and sensitivity analysis output
- **`GreyLiteratureSource`** ORM: tracks dissertation/report/preprint/conference/website sources
- **Alembic migration `0015_slr_workflow`**: creates all 7 new tables with FK constraints and
  full `downgrade()` path

## [0.6.0] — 2026-03-18 — feature/006-database-search-and-retrieval

### Added
- **`DatabaseIndex` StrEnum**: `ieee_xplore`, `acm_dl`, `scopus`, `web_of_science`, `inspec`,
  `science_direct`, `springer_link`, `google_scholar`, `semantic_scholar`
- **`IntegrationType` StrEnum**: maps to credential types for each source
  (`IEEE_XPLORE`, `ELSEVIER`, `WOS`, `SPRINGER_NATURE`, `SEMANTIC_SCHOLAR`)
- **`TestStatus` StrEnum**: `success`, `auth_failed`, `rate_limited`, `unreachable`, `untested`
- **`FullTextSource` StrEnum**: `unpaywall`, `scihub`, `manual`
- **`StudyDatabaseSelection` ORM model**: `study_id` FK (CASCADE), `selected_indices` JSON array,
  `created_at`/`updated_at` audit timestamps; unique on `study_id`
- **`SearchIntegrationCredential` ORM model**: `integration_type` (unique PK-like), `api_key_encrypted`
  (LargeBinary, nullable), `base_url`, `inst_token`, `version_id` (optimistic locking),
  `last_tested_at`, `test_status`, `test_message`, `created_at`/`updated_at`
- **`Paper` model additions**: `full_text_markdown` (Text, nullable), `full_text_source`
  (`FullTextSource` enum, nullable), `full_text_converted_at` (DateTime tz-aware, nullable)
- **Alembic migration `0014_database_search_and_retrieval`**: creates both new tables; adds three
  columns to `paper` table; full `downgrade()` path

---

## [0.5.0] — 2026-03-17 — feature/005-models-and-agents

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

## [0.3.0] — 2026-03-16 — feature/003-project-setup-improvements

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
