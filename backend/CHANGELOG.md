# Changelog — sms-backend

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.6.0] — 2026-03-18 — feature/006-database-search-and-retrieval

### Added
- **`CredentialService`** (`services/credential_service.py`): `upsert_credential` (Fernet-encrypted
  key, optimistic locking via `version_id`), `get_credential`, `get_effective_key` (DB key with
  env-var fallback), `configured_via` (database / environment / not_configured),
  `run_connectivity_test`, `_probe_ieee` (live HTTP probe); `VersionConflictError` on stale write
- **`DatabaseSelectionService`** (`services/database_selection.py`): read and write active
  `DatabaseIndex` list for a study
- **`PaperMarkdownService`** (`services/paper_markdown.py`): retrieve stored `full_text_markdown`
  for a paper
- **Admin Search Integrations router** (`api/v1/admin/search_integrations.py`):
  `GET /admin/search-integrations` — list all integration types with configuration and test status;
  `PUT /admin/search-integrations/{type}` — upsert credential (never echoes key back);
  `POST /admin/search-integrations/{type}/test` — connectivity test with `TestStatus` result
- **Study database-selection router** (`api/v1/studies/database_selection.py`):
  `GET/PUT /studies/{id}/database-selection` — read and write active indices
- **Paper Markdown router** (`api/v1/paper_markdown.py`):
  `GET /papers/{id}/markdown` — return stored full-text Markdown
- Unit tests: `test_credential_service.py`, `test_database_selection.py`, `test_paper_markdown.py`
- Integration tests: `admin/test_search_integrations.py`

---

## [0.5.0] — 2026-03-17 — feature/005-models-and-agents

### Added
- **`ProviderService`** (`services/provider_service.py`): CRUD for `Provider` records; Fernet
  encryption of API keys on create/update; `fetch_models_anthropic`, `fetch_models_openai`,
  `fetch_models_ollama` fetchers; `refresh_models` upserts `AvailableModel` rows preserving
  enable/disable state; raises `ProviderHasDependentsError` (HTTP 409) on blocked delete;
  raises `ProviderFetchError` (HTTP 502) on unreachable provider
- **`AgentService`** (`services/agent_service.py`): CRUD for `Agent` records with Jinja2
  template validation (strict `StrictUndefined` + known-variable allowlist);
  `generate_system_message` delegates to `AgentGeneratorAgent` and manages the undo buffer;
  `generate_persona_svg` with SVG validity check; `restore_system_message` swap;
  `render_system_message(template, agent, domain, study_type)` for study-context injection;
  `build_study_context(study)` maps enum values to human-readable labels
- **`backend/utils/encryption.py`**: `encrypt_secret(plaintext, secret_key) -> bytes` and
  `decrypt_secret(ciphertext, secret_key) -> str` via Fernet with PBKDF2HMAC key derivation
- **Admin API routers** (`api/v1/admin/`):
  - `providers.py`: `GET/POST /providers`, `GET/PATCH/DELETE /providers/{id}`,
    `POST /providers/{id}/refresh-models`
  - `models_router.py`: `GET /providers/{id}/models`, `PATCH /providers/{id}/models/{model_id}`
  - `agents.py`: `GET/POST /agents`, `GET/PATCH/DELETE /agents/{id}`,
    `POST /agents/{id}/generate-system-message`, `POST /agents/{id}/undo-system-message`,
    `POST /agents/generate-persona-svg`, `GET /agent-task-types`
- All agent invocation paths (screener, extractor, and others) updated to resolve `Reviewer.agent_id`,
  call `render_system_message` with study context, build `ProviderConfig` from Agent's provider
  record, and pass both as overrides to the agent class
- Unit tests: `test_provider_service.py`, `test_agent_service.py`, `test_encryption.py`
- Integration tests: `test_providers.py`, `test_agents.py`

---

## [0.4.0] — 2026-03-16 — feature/004-frontend-improvements

### Added
- `PUT /me/password` — password change with complexity validation and `token_version` session
  invalidation; audit event `PASSWORD_CHANGED`
- `POST /me/2fa/setup`, `/confirm`, `/disable`, `/backup-codes/regenerate` — full TOTP
  lifecycle with encrypted secret (Fernet/HKDF), QR code generation, bcrypt-hashed backup codes
- `POST /auth/login/totp` — second-step login consuming partial JWT (`stage: totp_required`)
- `GET /api/v1/openapi.json` — authenticated OpenAPI schema; default `/docs`/`/redoc` disabled
- `GET /me/preferences`, `PUT /me/preferences/theme` — user preference endpoints
- `SecurityAuditEvent` and `BackupCode` ORM models + Alembic migration
- `backend.core.totp` — `pyotp` wrapper for secret generation, URI, QR PNG, verification
- `backend.core.encryption` — Fernet + HKDF encryption for secrets at rest
- `backend.services.totp_service` — TOTP lifecycle with brute-force lockout logic
- `backend.services.password_service` — password change with complexity enforcement
- Integration tests: `test_me_password`, `test_me_preferences`, `test_me_totp`,
  `test_auth_totp`, `test_openapi_auth`

### Changed
- `get_current_user` now performs a DB lookup to validate `token_version`; missing users
  return 401 instead of propagating to the endpoint
- `POST /auth/login` checks `totp_enabled` and returns partial token when 2FA is required
- `GET /auth/me` response includes `theme_preference` and `totp_enabled`

---

## [0.3.0] — 2026-03-16 — feature/003-project-setup-improvements

### Changed
- Coverage command documented in `CLAUDE.md`: `uv run pytest backend/tests/ --cov=backend`
- Mutation testing tool updated to `cosmic-ray` (was `mutmut`); run via manual GitHub
  Actions `workflow_dispatch` workflow
- `pytest` build gate enforced: skip/xfail markers without `reason=` cause the run to fail

---

## [0.2.0] — 2026-03-12 — feature/002-sms-workflow

### Added
- FastAPI app factory (`src/backend/main.py`) with lifespan event handling
- REST API v1 router (`/api/v1`) with endpoints for:
  - Studies (CRUD, status transitions)
  - Papers (create, read, list, search)
  - Screening criteria (inclusion/exclusion management)
  - PICO elements (Population, Intervention, Comparison, Outcome)
  - Search strings (generate, save, version)
  - Quality assessment (criteria, scoring)
  - Results (aggregate, export)
  - Background jobs (status polling)
  - Health check (`GET /api/v1/health`)
- JWT bearer-token authentication middleware (`src/backend/core/auth.py`)
- structlog request-scoped logging middleware (`src/backend/core/logging.py`)
- Pydantic Settings configuration (`src/backend/core/config.py`) with `lru_cache`
- ARQ background job queue integration for long-running agent tasks
- LiteLLM abstraction for agent-triggered LLM calls
- Multi-stage `Dockerfile` (`python:3.14-slim`)
- Unit and integration test suite (`tests/unit/`, `tests/integration/`)

---

## [0.1.0] — 2026-03-11 — feature/001-repo-setup

### Added
- Initial `pyproject.toml` (`sms-backend`) as UV workspace member
- Minimal FastAPI skeleton (`GET /api/v1/health`)
- Ruff, MyPy strict, pytest + pytest-asyncio configuration
