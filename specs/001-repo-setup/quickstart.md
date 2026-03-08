# Quickstart: SMS Researcher Mono-Repo

**Branch**: `001-repo-setup` | **Date**: 2026-03-08

This guide covers getting any sub-project running from a fresh clone.

---

## Prerequisites

| Tool | Minimum Version | Install |
|------|----------------|---------|
| `uv` | 0.4+ | `curl -Ls https://astral.sh/uv/install.sh \| sh` |
| `node` | 20 LTS | via `nvm` or package manager |
| `npm` | 10+ | bundled with Node 20 |
| `pre-commit` | 3.7+ | `pip install pre-commit` or `uv tool install pre-commit` |
| `git` | 2.40+ | package manager |
| `ollama` | 0.3+ | **Optional** (host install) — only needed if running outside Docker; `curl -fsSL https://ollama.com/install.sh \| sh` |
| `docker` | 24+ (with Compose v2) | Required for containerised deployment |
| `hadolint` | 2.12+ | Dockerfile linter — `brew install hadolint` or from GitHub releases |
| `trivy` | 0.50+ | **Optional** — container vulnerability scanner; `brew install trivy` |

---

## Clone & First-time Setup

```bash
git clone <repo-url>
cd sms-reseacher
```

---

## Python Sub-projects (backend, agents, db, agent-eval)

All Python sub-projects share a UV workspace rooted at the repo root.

### Install all Python dependencies

```bash
# From repo root — installs all workspace members into a shared .venv
uv sync
```

### Run a specific sub-project's tests

```bash
uv run --package sms-backend    pytest backend/tests/
uv run --package sms-agents     pytest agents/tests/
uv run --package sms-db         pytest db/tests/
uv run --package sms-agent-eval pytest agent-eval/tests/
```

### Run static analysis

```bash
# Lint (Ruff)
uv run ruff check backend/ agents/ db/

# Format check (Ruff)
uv run ruff format --check backend/ agents/ db/

# Type check (MyPy)
uv run mypy backend/src agents/src db/src
```

### Start the backend (development)

```bash
uv run --package sms-backend uvicorn backend.main:app --reload --port 8000
```

### Run database migrations

```bash
# From db/ directory
cd db
uv run alembic upgrade head
```

---

## Agent Evaluation CLI (`agent-eval/`)

By default uses `LLM_PROVIDER` / `LLM_MODEL` from `.env`. Override per-command with `--provider` and `--model`.

```bash
# Show all commands
uv run agent-eval --help

# Evaluate using Anthropic (cloud)
uv run agent-eval evaluate \
  --agent screener \
  --suite agent-eval/test-suites/screener.jsonl \
  --output /tmp/eval-report.json

# Evaluate using local Ollama (fully offline)
uv run agent-eval evaluate \
  --agent screener \
  --suite agent-eval/test-suites/screener.jsonl \
  --provider ollama \
  --model llama3.2:3b \
  --output /tmp/eval-report.json

# Display a saved report
uv run agent-eval report /tmp/eval-report.json

# Compare two evaluation runs
uv run agent-eval compare baseline.json candidate.json

# Generate candidate improved prompts for weak cases
uv run agent-eval improve \
  --report /tmp/eval-report.json \
  --agent screener
```

Candidate prompt files are written to `agents/prompts/screener/candidates/` for human review before merging.

---

## Researcher MCP Server (`researcher-mcp/`)

```bash
# Start the FastMCP server (development)
uv run --package sms-researcher-mcp researcher-mcp
# → Listening on http://localhost:8002/sse

# Verify SSE endpoint
curl http://localhost:8002/sse
# → valid SSE response

# Run tests
uv run --package sms-researcher-mcp pytest researcher-mcp/tests/

# Configure paper source rate limits (optional)
export SEMANTIC_SCHOLAR_RPM=100   # default; matches unauthenticated API limit
export OPEN_ALEX_RPM=300

# Enable SciHub (opt-in; read the legal warning first)
export SCIHUB_ENABLED=true
export SCIHUB_URL=https://sci-hub.se
```

> **Legal notice**: SciHub is disabled by default (`SCIHUB_ENABLED=false`). Enabling it is solely the user's responsibility. Check your jurisdiction's copyright law before enabling.

---

## Frontend (`frontend/`)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Run tests (Vitest)
npm test

# Lint
npm run lint

# Format check
npm run format:check

# Build for production
npm run build
```

---

## Docker: Local Deployment

### Run everything with Docker Compose

```bash
# Copy env file and configure
cp .env.example .env

# Start frontend + backend + database (uses Anthropic or remote Ollama)
docker compose up

# Start with local Ollama (downloads model on first run)
docker compose --profile ollama up

# Pull a model into the running Ollama container
docker compose exec ollama ollama pull llama3.2:3b

# Verify backend is healthy
curl http://localhost:8000/api/v1/health
# → {"status": "ok", "version": "0.1.0"}

# Frontend is at http://localhost:3000
```

### Build images individually

```bash
# Backend (build context = repo root)
docker build -f backend/Dockerfile -t sms-backend:dev .

# Frontend (build context = frontend/)
docker build -f frontend/Dockerfile -t sms-frontend:dev frontend/
```

### Validate Dockerfiles

```bash
# Lint (requires hadolint installed, or via pre-commit)
hadolint backend/Dockerfile
hadolint frontend/Dockerfile

# Validate compose file
docker compose config
```

### Scan images for vulnerabilities (requires trivy)

```bash
trivy image sms-backend:dev
trivy image sms-frontend:dev
```

---

## Pre-commit Hooks

Install hooks once after cloning:

```bash
# Python hooks (root)
pre-commit install

# Frontend hooks
cd frontend && npm run prepare  # installs Husky
```

After installation, every `git commit` automatically runs:
- **Python**: Ruff lint, Ruff format check, MyPy, pytest
- **Frontend**: ESLint, Prettier (via lint-staged on staged files)

---

## Environment Variables

Copy the example env file and edit as needed:

```bash
cp .env.example .env
```

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./dev.db` | Database connection string |
| `SECRET_KEY` | (required in prod) | JWT signing key |
| `LLM_PROVIDER` | `anthropic` | LLM provider: `anthropic` or `ollama` |
| `LLM_MODEL` | `claude-sonnet-4-6` | Model ID (e.g. `llama3.2:3b` for Ollama) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL (used when `LLM_PROVIDER=ollama`) |
| `ANTHROPIC_API_KEY` | (required when `LLM_PROVIDER=anthropic`) | Anthropic API key |
| `RESEARCHER_MCP_URL` | `http://localhost:8002/sse` | MCP server URL used by `agents` |
| `SEMANTIC_SCHOLAR_RPM` | `100` | Semantic Scholar requests-per-minute limit |
| `OPEN_ALEX_RPM` | `300` | OpenAlex requests-per-minute limit |
| `SCIHUB_ENABLED` | `false` | Enable SciHub PDF fetching (opt-in; see legal notice) |

---

## Common Issues

| Problem | Solution |
|---------|---------|
| `uv: command not found` | Install uv: `curl -Ls https://astral.sh/uv/install.sh \| sh` |
| `Python 3.14 not found` | `uv python install 3.12` |
| `npm: command not found` | Install Node 20 LTS via `nvm install 20` |
| MyPy errors on first run | Run `uv sync` first to install stubs |
| Pre-commit hooks not firing | Run `pre-commit install` from repo root |
