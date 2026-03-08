# Quickstart: SMS Workflow System (002-sms-workflow)

**Branch**: `002-sms-workflow` | **Date**: 2026-03-10

---

## Prerequisites

- Docker + Docker Compose (for PostgreSQL + Redis in development)
- Python 3.14 + `uv` package manager
- Node 20 LTS + `npm`
- A configured `.env` file (see below)

---

## Environment Setup

Copy and fill in environment variables:

```bash
cp .env.example .env
```

Required variables:

```env
# Database (production / docker-compose)
DATABASE_URL=postgresql+asyncpg://sms:sms@localhost:5432/sms

# Database (test — auto-uses SQLite)
# TEST_DATABASE_URL=sqlite+aiosqlite:///./test.db  ← set automatically by pytest fixtures

# Redis (ARQ job queue)
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
ACCESS_TOKEN_EXPIRE_MINUTES=480

# LLM backend (LiteLLM compatible)
LLM_API_KEY=<openai-key or ollama endpoint>
LLM_MODEL=gpt-4o  # or ollama/llama3.2 for local

# researcher-mcp (SSE endpoint)
RESEARCHER_MCP_URL=http://localhost:8002/sse
SCIHUB_ENABLED=false  # opt-in only; ensure legal compliance
```

---

## Start Infrastructure

```bash
docker compose up -d   # starts PostgreSQL 16 + Redis
```

---

## Install Dependencies

```bash
# Python workspace (all packages)
uv sync --all-packages

# Frontend
cd frontend && npm install && cd ..
```

---

## Run Database Migrations

```bash
cd db
uv run alembic upgrade head
cd ..
```

---

## Start Development Servers

In separate terminals:

```bash
# 1. API backend (FastAPI, port 8000)
cd backend && uv run uvicorn backend.main:app --reload --port 8000

# 2. ARQ background worker
cd backend && uv run python -m backend.jobs.worker

# 3. researcher-mcp tool server (port 8002)
cd researcher-mcp && uv run researcher-mcp

# 4. Frontend dev server (port 5173)
cd frontend && npm run dev
```

Open: http://localhost:5173

---

## Run Tests

```bash
# All Python packages (uses SQLite automatically)
uv run pytest

# Specific package
cd backend && uv run pytest
cd agents && uv run pytest

# Frontend
cd frontend && npm test

# Agent evals (all pipelines — stub mode, no LLM credentials required)
cd agent-eval && uv run agent-eval eval-all

# Agent evals (live mode — requires LLM credentials)
cd agent-eval && uv run agent-eval eval-all --run-agent
```

---

## Key Workflows

### Create a Study
1. Open http://localhost:5173 → log in
2. Select or create a Research Group
3. Click **New Study** → complete the wizard (name, type, PICO/C, reviewers)
4. Study appears in the group's studies list at Phase 1

### Run a Search
1. Open a study → Phase 2 tab
2. Generate or manually enter a search string
3. Run **Test Search** → compare against seed papers, iterate
4. Click **Run Full Search** → monitor progress in the live progress dashboard

### View Results
1. Open a study → Results tab (unlocks after extraction is complete)
2. View charts, domain model
3. Click **Export** → choose format (SVG Only, JSON Only, CSV+JSON, Full Archive)

---

## Docker Compose (Remote Ollama variant)

For running with a local Ollama LLM instead of an OpenAI-compatible API:

```bash
docker compose -f docker-compose_2.yml up -d
```

Set in `.env`:
```env
LLM_MODEL=ollama/llama3.2
LLM_API_KEY=ollama  # placeholder
OLLAMA_BASE_URL=http://host.docker.internal:11434
```
