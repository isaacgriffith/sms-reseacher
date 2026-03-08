# sms-backend

FastAPI API gateway for SMS Researcher. Orchestrates agents, exposes REST endpoints, and handles authentication.

## Setup

```bash
# From repo root — install all workspace members
uv sync

# Run the backend in development mode
uv run --package sms-backend uvicorn backend.main:app --reload --port 8000

# Run tests
uv run --package sms-backend pytest backend/tests/

# Lint and type-check
uv run ruff check backend/src
uv run mypy backend/src
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./dev.db` | Async database URL |
| `SECRET_KEY` | (required in production) | JWT signing key |
| `LLM_PROVIDER` | `anthropic` | LLM provider: `anthropic` or `ollama` |
| `LLM_MODEL` | `claude-sonnet-4-6` | Model identifier |
| `ANTHROPIC_API_KEY` | — | Required when `LLM_PROVIDER=anthropic` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `RESEARCHER_MCP_URL` | `http://localhost:8002/sse` | MCP server URL used by agents |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check — returns `{"status": "ok", "version": "0.1.0"}` |

## Project Structure

```
backend/
├── pyproject.toml          # sms-backend package config
├── Dockerfile              # Multi-stage python:3.14-slim image
├── src/backend/
│   ├── main.py             # FastAPI app factory
│   ├── core/
│   │   ├── config.py       # pydantic-settings Settings class
│   │   ├── auth.py         # JWT bearer-token middleware stub
│   │   └── logging.py      # structlog request-scoped middleware
│   └── api/v1/
│       ├── router.py       # APIRouter mounted at /api/v1
│       └── health.py       # GET /api/v1/health
└── tests/
    ├── unit/test_health.py
    └── integration/test_db_import.py
```

See [quickstart.md](../specs/001-repo-setup/quickstart.md) for full onboarding instructions.
