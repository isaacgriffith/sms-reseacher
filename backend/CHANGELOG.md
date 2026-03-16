# Changelog — sms-backend

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
