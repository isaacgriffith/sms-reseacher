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

# Run tests with coverage (minimum 85% line coverage required)
uv run --package sms-backend pytest backend/tests/ --cov=backend --cov-report=term-missing

# Mutation testing (run via GitHub Actions workflow_dispatch, or locally)
uv run cosmic-ray run backend/cosmic-ray.toml

# Lint and type-check
uv run ruff check backend/src
uv run ruff format --check backend/src
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
| `GET` | `/api/v1/health` | Health check |
| Various | `/api/v1/studies/*` | Study CRUD and status transitions |
| Various | `/api/v1/papers/*` | Paper management and search |
| Various | `/api/v1/criteria/*` | Inclusion/exclusion criteria |
| Various | `/api/v1/pico/*` | PICO element management |
| Various | `/api/v1/search-strings/*` | Search string generation and versioning |
| Various | `/api/v1/quality/*` | Quality assessment criteria and scoring |
| Various | `/api/v1/results/*` | Result aggregation and export |
| Various | `/api/v1/jobs/*` | Background job status |

### Admin Endpoints (`/api/v1/admin/`)

| Method | Path | Description |
|--------|------|-------------|
| `GET/POST` | `/admin/providers` | List / create LLM providers |
| `GET/PATCH/DELETE` | `/admin/providers/{id}` | Get / update / delete a provider |
| `POST` | `/admin/providers/{id}/refresh-models` | Fetch models from provider API and upsert |
| `GET` | `/admin/providers/{id}/models` | List models for a provider |
| `PATCH` | `/admin/providers/{id}/models/{model_id}` | Enable or disable a model |
| `GET/POST` | `/admin/agents` | List / create agents |
| `GET/PATCH/DELETE` | `/admin/agents/{id}` | Get / update / deactivate an agent |
| `POST` | `/admin/agents/{id}/generate-system-message` | Generate system message via AgentGeneratorAgent |
| `POST` | `/admin/agents/{id}/undo-system-message` | Restore previous system message from undo buffer |
| `POST` | `/admin/agents/generate-persona-svg` | Generate persona SVG illustration via LLM |
| `GET` | `/admin/agent-task-types` | List all supported AgentTaskType values |

Full interactive API documentation is available at `http://localhost:8000/docs` when the server is running.

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
│   ├── api/v1/
│   │   ├── router.py       # APIRouter mounted at /api/v1
│   │   ├── health.py       # GET /api/v1/health
│   │   ├── admin/          # Admin sub-routers (providers, models, agents)
│   │   └── [domain].py     # studies, papers, criteria, pico, search_strings, quality, results, jobs
│   ├── services/
│   │   ├── provider_service.py   # Provider CRUD + model-list fetch (Anthropic/OpenAI/Ollama)
│   │   ├── agent_service.py      # Agent CRUD + system-message generation + study-context rendering
│   │   └── ...                   # Other business logic services
│   ├── utils/
│   │   └── encryption.py         # Fernet encrypt_secret / decrypt_secret
│   └── jobs/               # ARQ background job definitions
└── tests/
    ├── unit/
    └── integration/
```

See [quickstart.md](../specs/001-repo-setup/quickstart.md) for full onboarding instructions.
