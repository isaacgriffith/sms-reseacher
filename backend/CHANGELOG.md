# Changelog — sms-backend

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — feature/004-frontend-improvements

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

## [Unreleased] — feature/003-project-setup-improvements

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
