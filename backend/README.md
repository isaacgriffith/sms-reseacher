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
| `IEEE_XPLORE_API_KEY` | — | IEEE Xplore API key for search integrations |
| `ELSEVIER_API_KEY` | — | Elsevier API key (Scopus, Inspec, ScienceDirect) |
| `ELSEVIER_INST_TOKEN` | — | Elsevier institutional token (optional) |
| `WOS_API_KEY` | — | Web of Science API key |
| `SPRINGER_API_KEY` | — | SpringerNature API key |
| `SLR_KAPPA_THRESHOLD` | `0.6` | Minimum Cohen's κ required to unlock QA phase for SLR studies |
| `SLR_MIN_SYNTHESIS_PAPERS` | `2` | Minimum included papers required to start synthesis |

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
| `GET/PUT` | `/admin/search-integrations` | List all integration types / upsert credential |
| `POST` | `/admin/search-integrations/{type}/test` | Trigger connectivity test for an integration |

### Study Endpoints (additions)

| Method | Path | Description |
|--------|------|-------------|
| `GET/PUT` | `/api/v1/studies/{id}/database-selection` | Read/write active database indices for a study |
| `GET` | `/api/v1/papers/{id}/markdown` | Retrieve stored full-text Markdown for a paper |

### Rapid Review Endpoints (`/api/v1/rapid/`)

| Method | Path | Description |
|--------|------|-------------|
| `GET/PUT` | `/rapid/studies/{id}/protocol` | Read / upsert Rapid Review protocol |
| `GET/PUT` | `/rapid/studies/{id}/search-config` | Read / upsert search restriction config |
| `GET/PUT` | `/rapid/studies/{id}/qa-config` | Read / upsert quality appraisal config |
| `GET/POST` | `/rapid/studies/{id}/stakeholders` | List / add practitioner stakeholders |
| `GET/PATCH/DELETE` | `/rapid/studies/{id}/stakeholders/{sid}` | Get / update / delete a stakeholder |
| `GET` | `/rapid/studies/{id}/narrative-synthesis` | List narrative synthesis sections |
| `PATCH` | `/rapid/studies/{id}/narrative-synthesis/{section_id}` | Update narrative text / is_complete flag |
| `POST` | `/rapid/studies/{id}/narrative-synthesis/{section_id}/ai-draft` | Trigger AI draft ARQ job |
| `POST` | `/rapid/studies/{id}/narrative-synthesis/complete` | Finalise synthesis (validates all sections complete) |
| `GET/POST` | `/rapid/studies/{id}/briefings` | List / create new Evidence Briefing version |
| `GET` | `/rapid/studies/{id}/briefings/{bid}` | Get specific briefing version |
| `POST` | `/rapid/studies/{id}/briefings/{bid}/publish` | Publish briefing version (demotes prior published) |
| `GET` | `/rapid/studies/{id}/briefings/{bid}/export` | Download PDF (FileResponse) |
| `POST` | `/rapid/studies/{id}/briefings/{bid}/share-token` | Create share token for unauthenticated access |
| `DELETE` | `/rapid/briefings/share-token/{token}` | Revoke a share token |

### Public Endpoints (`/api/v1/public/`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/public/briefings/{token}` | Retrieve published briefing via share token (no auth) |
| `GET` | `/public/briefings/{token}/export` | Download briefing PDF via share token (no auth) |

### Tertiary Endpoints (`/api/v1/tertiary/`)

| Method | Path | Description |
|--------|------|-------------|
| `GET/PUT` | `/tertiary/studies/{id}/protocol` | Read / upsert Tertiary Study protocol |
| `GET/POST` | `/tertiary/studies/{id}/seed-imports` | List / create seed imports from other platform studies |
| `GET/PUT` | `/tertiary/papers/{id}/extraction` | Read / upsert secondary-study data extraction |
| `POST` | `/tertiary/papers/{id}/extraction/ai-assist` | Trigger AI pre-fill ARQ job for extraction |
| `GET` | `/tertiary/studies/{id}/report` | Generate tertiary report (landscape + synthesis + recommendations) |

### SLR Endpoints (`/api/v1/slr/`)

| Method | Path | Description |
|--------|------|-------------|
| `GET/PUT` | `/slr/studies/{id}/protocol` | Read / upsert SLR review protocol |
| `POST` | `/slr/studies/{id}/protocol/review` | Trigger AI protocol review (ARQ job) |
| `GET` | `/slr/studies/{id}/inter-rater-reliability` | Compute Cohen's κ for screened papers |
| `GET/PUT` | `/slr/studies/{id}/quality-checklist` | Read / upsert quality assessment checklist |
| `GET/PUT` | `/slr/papers/{id}/quality-scores` | Read / submit quality scores for a paper |
| `GET/POST` | `/slr/studies/{id}/synthesis` | List synthesis results / start new synthesis job |
| `GET` | `/slr/synthesis/{id}` | Get individual synthesis result |
| `GET/POST` | `/slr/studies/{id}/grey-literature` | List / add grey literature sources |
| `DELETE` | `/slr/studies/{id}/grey-literature/{source_id}` | Delete a grey literature source |
| `GET` | `/slr/studies/{id}/report` | Generate and download structured SLR report |

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
