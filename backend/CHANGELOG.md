# Changelog — sms-backend

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.8.0] — 2026-03-29 — feature/008-rapid-review-workflow

### Added
- **RR API routers** (`api/v1/rapid/`): `protocol.py`, `search_config.py`, `qa_config.py`,
  `stakeholders.py`, `narrative.py`, `briefing.py` — full CRUD + job-trigger endpoints for
  every Rapid Review phase
- **Public Briefing router** (`api/v1/public/briefings.py`):
  `GET /public/briefings/{token}` and `GET /public/briefings/{token}/export` — unauthenticated
  endpoints that validate share token expiry/revocation and return published briefing data or
  binary PDF; registered under `/api/v1` alongside authenticated routes
- **`RRProtocolService`** (`services/rr_protocol_service.py`): create/read/update Rapid Review
  protocol with status transition validation (`draft` ↔ `validated`); seeds
  `RRThreatToValidity` records on validation based on QA mode
- **`RRPhaseGate`** (`services/rr_phase_gate.py`): `get_rr_unlocked_phases()` returns
  progressively unlocked phases based on protocol status, stakeholder count, and narrative
  synthesis completion; wired into `GET /api/v1/studies/{id}/phases` dispatch dict
- **`NarrativeSynthesisService`** (`services/narrative_synthesis_service.py`): load/update
  sections, mark complete, finalize synthesis (validates all sections complete; HTTP 422 with
  `incomplete_sections` list when not)
- **`EvidenceBriefingService`** (`services/evidence_briefing_service.py`):
  `get_briefings_for_study`, `create_new_version` (auto-incremented version_number),
  `publish_version` (atomic demote-then-promote), `generate_html` (Jinja2 → `/tmp/briefings/{id}/`),
  `generate_pdf` (WeasyPrint), `create_share_token` (`secrets.token_urlsafe(32)`),
  `revoke_token`, `resolve_token` (validates revoked_at/expires_at, returns PUBLISHED briefing)
- **ARQ background jobs**: `evidence_briefing_job.py` (Jinja2→HTML→WeasyPrint PDF; marks job
  COMPLETED or FAILED); `narrative_synthesis_job.py` (per-section AI draft via
  `NarrativeSynthesiserAgent`)
- **Jinja2 A4 HTML template** (`templates/rapid/evidence_briefing.html.j2`): 6 sections with
  print CSS `@page { size: A4; margin: 1.5cm; }`; A4 page size enforced in WeasyPrint call
- **New dependency**: `weasyprint` added to `backend/pyproject.toml`
- Unit + integration tests: `test_rr_protocol_service.py`, `test_narrative_synthesis_service.py`,
  `test_evidence_briefing_service.py`, `test_evidence_briefing_job.py`, `test_narrative_synthesis_job.py`,
  `test_protocol_quality_routes.py`; ≥85% coverage

## [0.7.0] — 2026-03-21 — feature/007-slr-workflow

### Added
- **SLR API routers** (`api/v1/slr/`): protocol, inter-rater reliability, quality assessment,
  synthesis, grey literature, and report endpoints
- **`SLRProtocolService`** (`services/slr_protocol_service.py`): create/read/update protocol with
  status transition validation
- **`SLRPhaseGate`** (`services/slr_phase_gate.py`): `get_slr_unlocked_phases()` returns
  progressively unlocked phases based on protocol status, Kappa threshold, and included paper count;
  wired into `GET /api/v1/studies/{id}/phases` via `StudyType` dispatch dict
- **`InterRaterService`** (`services/inter_rater_service.py`): Cohen's κ computation via
  `sklearn.metrics.cohen_kappa_score`; `safe_cohen_kappa` handles edge cases
- **`QualityAssessmentService`** (`services/quality_assessment_service.py`): checklist CRUD and
  per-reviewer score submission
- **`SynthesisService`** + strategies (`services/synthesis_service.py`,
  `services/synthesis_strategies.py`): `MetaAnalysisStrategy` (pooled effect size + Forest/Funnel
  SVG via `scipy`/`matplotlib`), `DescriptiveSynthesisStrategy`, `QualitativeSynthesisStrategy`
- **`SLRReportService`** (`services/slr_report_service.py`): structured Markdown report generation
- **`statistics.py`** (`services/statistics.py`): `pooled_effect_size`, `weighted_mean`,
  `between_study_variance`, `confidence_interval` for meta-analysis
- **`synthesis_job.py`** + **`protocol_review_job.py`** (`jobs/`): ARQ background jobs
- **`SLR_KAPPA_THRESHOLD`** and **`SLR_MIN_SYNTHESIS_PAPERS`** config settings

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
