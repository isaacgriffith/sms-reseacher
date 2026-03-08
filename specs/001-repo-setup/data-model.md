# Data Model: Mono-Repo Setup

**Branch**: `001-repo-setup` | **Date**: 2026-03-08

> This feature is a repository scaffolding task, not an application feature. The "entities" here are the structural artefacts that must exist after setup rather than persistent database records.

---

## Sub-project Registry

Each sub-project is a self-contained unit with a well-defined manifest and toolchain.

| Sub-project | Language | Manifest | Role |
|-------------|----------|----------|------|
| `frontend`   | TypeScript / React | `package.json` | Researcher-facing SPA |
| `backend`    | Python 3.14 | `pyproject.toml` | FastAPI API gateway; orchestrates agents |
| `agents`     | Python 3.14 | `pyproject.toml` | AI research-task execution; owns prompt templates |
| `db`         | Python 3.14 | `pyproject.toml` | SQLAlchemy models + Alembic migrations |
| `agent-eval` | Python 3.14 | `pyproject.toml` | Typer CLI for agent evaluation and prompt improvement |
| `researcher-mcp` | Python 3.14 | `pyproject.toml` | FastMCP server providing paper search / fetch tools to agents |

**Relationships**:
```
frontend  ──HTTP──►  backend
                        │
               ┌────────┴────────┐
               │                 │
             agents             db
          (import)        (import)

agent-eval ──import──► agents        (reads prompts, invokes agent functions)
agent-eval ──API──►    LiteLLM       (LLM-as-a-Judge calls via deepeval)

agents     ──MCP/SSE──► researcher-mcp  (tool calls: search, fetch, metadata)
researcher-mcp ──HTTP──► Semantic Scholar / OpenAlex / CrossRef / Unpaywall / arXiv
```

---

## Harness Entity per Sub-project

### Python Sub-project Harness (`backend`, `agents`, `db`)

**Fields** (all present in `pyproject.toml`):

| Field | Value | Notes |
|-------|-------|-------|
| `[project].name` | `sms-backend` / `sms-agents` / `sms-db` | Unique package name |
| `[project].requires-python` | `>=3.14` | Minimum Python version |
| `[project].dependencies` | framework deps | Per sub-project |
| `[tool.ruff]` section | `select`, `ignore`, `line-length` | Linting + formatting |
| `[tool.mypy]` section | `strict = true`, `python_version` | Type checking |
| `[tool.pytest.ini_options]` | `testpaths`, `asyncio_mode` | Test discovery |
| `[build-system]` | `uv` via `hatchling` | Build backend |

**Validation rules**:
- `requires-python` MUST be `>=3.14`.
- `[tool.mypy] strict = true` MUST be set.
- `[tool.ruff] select` MUST include `["E","W","F","I","D","UP","B"]`.
- `tests/` directory MUST exist with at least one passing placeholder test.

### TypeScript Sub-project Harness (`frontend`)

**Files** (all present in `frontend/`):

| File | Purpose |
|------|---------|
| `package.json` | NPM manifest; scripts: `dev`, `build`, `lint`, `format:check`, `test` |
| `tsconfig.json` | TypeScript compiler options (`strict: true`) |
| `vite.config.ts` | Vite build config; Vitest config embedded |
| `eslint.config.js` | ESLint 9 flat config |
| `.prettierrc` | Prettier formatting rules |
| `.husky/pre-commit` | Git hook invoking lint-staged |
| `.lintstagedrc` | Staged-file lint/format rules |

**Validation rules**:
- `tsconfig.json` MUST have `"strict": true`.
- ESLint MUST include `typescript-eslint` and `eslint-plugin-react-hooks`.
- `npm test` MUST run Vitest and pass at least one test.

---

## Database Schema Entities (initial skeleton in `db/`)

These are the minimal tables required to validate the harness. Full schema evolves in later features.

### `Study`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `INTEGER` | PK, auto-increment |
| `name` | `VARCHAR(255)` | NOT NULL |
| `study_type` | `VARCHAR(50)` | NOT NULL; enum: `SMS`, `SLR`, `Tertiary`, `Rapid` |
| `status` | `VARCHAR(50)` | NOT NULL; default `draft` |
| `created_at` | `TIMESTAMP` | NOT NULL; server default now() |
| `updated_at` | `TIMESTAMP` | NOT NULL; server default now(), on-update |

### `Paper`
| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `INTEGER` | PK, auto-increment |
| `title` | `TEXT` | NOT NULL |
| `abstract` | `TEXT` | nullable |
| `doi` | `VARCHAR(255)` | nullable, unique |
| `metadata` | `JSONB` / `JSON` | nullable; flexible bibliographic fields |
| `created_at` | `TIMESTAMP` | NOT NULL; server default now() |

### `StudyPaper` (join table)
| Column | Type | Constraints |
|--------|------|-------------|
| `study_id` | `INTEGER` | FK → `Study.id`, NOT NULL |
| `paper_id` | `INTEGER` | FK → `Paper.id`, NOT NULL |
| `inclusion_status` | `VARCHAR(50)` | nullable; `included`, `excluded`, `pending` |
| PK | composite | (`study_id`, `paper_id`) |

**State transitions for `Study.status`**:
```
draft → active → completed
              └→ archived
```

**State transitions for `StudyPaper.inclusion_status`**:
```
pending → included
        └→ excluded
```

---

## Pre-commit Configuration Entity

Both Python and TypeScript sub-projects declare a pre-commit configuration.

### Python (root `.pre-commit-config.yaml`)
```yaml
repos:
  - repo: local
    hooks:
      - {id: ruff-check,   entry: uv run ruff check .,       language: system, pass_filenames: false}
      - {id: ruff-format,  entry: uv run ruff format --check ., language: system, pass_filenames: false}
      - {id: mypy,         entry: uv run mypy .,              language: system, pass_filenames: false}
      - {id: pytest,       entry: uv run pytest,              language: system, pass_filenames: false}
```

### Frontend (`.husky/pre-commit` + `.lintstagedrc`)
```sh
#!/bin/sh
cd frontend && npx lint-staged
```
```json
{ "*.{ts,tsx}": ["eslint --fix", "prettier --write"] }
```

---

## Prompt Template Entity (`agents/prompts/`)

Each agent type owns a directory of Markdown prompt files. These are the canonical source of truth for agent behaviour and are versioned in git.

| File | Role | Format |
|------|------|--------|
| `{agent_type}/system.md` | System prompt (static) | Plain Markdown |
| `{agent_type}/user.md.j2` | User prompt template | Markdown + Jinja2 |
| `{agent_type}/candidates/` | Proposed revised prompts from `agent-eval improve` | Plain Markdown |

**Validation rules**:
- Every agent type stubbed in `agents/services/` MUST have a corresponding `prompts/{agent_type}/` directory.
- `user.md.j2` MUST render without error when given a sample context dict (verified by a unit test in `agents/tests/unit/test_prompt_loader.py`).
- `candidates/` directory MUST NOT be committed to `main` without human review.

**Initial agent types** (stubs):

| Agent Type | System prompt variable(s) |
|------------|--------------------------|
| `screener` | `{inclusion_criteria}`, `{exclusion_criteria}` |
| `extractor` | `{data_fields}`, `{paper_text}` |
| `synthesiser` | `{papers_summary}`, `{research_question}` |

---

## `agent-eval` Harness Entity

| Field | Value |
|-------|-------|
| `[project].name` | `sms-agent-eval` |
| `[project].requires-python` | `>=3.14` |
| Primary deps | `typer`, `rich`, `deepeval`, `litellm`, `jinja2` |
| Workspace deps | `agents` (via `[tool.uv.sources]`) |
| CLI entry point | `[project.scripts] agent-eval = "agent_eval.cli:app"` |
| Test runner | pytest + pytest-cov (≥85% coverage) |
| Mutation testing | mutmut |

**EvalReport entity** (in-memory / JSON file output):

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | `str` (UUID) | Unique evaluation run identifier |
| `agent_type` | `str` | e.g. `screener`, `extractor` |
| `prompt_version` | `str` | Git SHA of prompt files at eval time |
| `test_cases` | `list[TestCaseResult]` | Per-case scores and metadata |
| `overall_score` | `float` | Mean score across all metrics and cases |
| `timestamp` | `datetime` | When the evaluation ran |

**TestCaseResult entity**:

| Field | Type | Description |
|-------|------|-------------|
| `case_id` | `str` | Identifier for the test input |
| `input` | `dict` | Rendered prompt inputs |
| `output` | `str` | Agent response |
| `scores` | `dict[str, float]` | Metric name → score (0.0–1.0) |
| `passed` | `bool` | All metrics ≥ threshold |

---

## Docker Image Entities

### Backend Image (`backend/Dockerfile`)

| Stage | Base | Purpose |
|-------|------|---------|
| `builder` | `python:3.14-slim` + UV binary | Install production deps from workspace |
| `runtime` | `python:3.14-slim` | Serve FastAPI app as non-root user |

**Validation rules**:
- MUST pass `hadolint` with zero errors.
- MUST run as non-root user (`USER appuser`).
- MUST use `--frozen` UV install (lockfile-pinned).
- Build context: **repo root** (to resolve workspace siblings `agents/`, `db/`).

### Frontend Image (`frontend/Dockerfile`)

| Stage | Base | Purpose |
|-------|------|---------|
| `builder` | `node:20-alpine` | `npm ci` + `npm run build` (Vite) |
| `runtime` | `nginx:alpine` | Serve `dist/` with SPA fallback config |

**Validation rules**:
- MUST pass `hadolint` with zero errors.
- `nginx.conf` MUST include `try_files $uri $uri/ /index.html` for React Router.
- MUST use `npm ci` (not `npm install`) for reproducible builds.

---

## Docker Compose Service Registry

Defined in `docker-compose.yml` at repo root.

| Service | Source | Ports | Profile | Depends On |
|---------|--------|-------|---------|------------|
| `db` | `postgres:16-alpine` | 5432 | always | — |
| `backend` | `backend/Dockerfile` (root ctx) | 8000 | always | `db` (healthy) |
| `frontend` | `frontend/Dockerfile` | 3000→80 | always | `backend` |
| `researcher-mcp` | `researcher-mcp/Dockerfile` (root ctx) | 8002 | always | — |
| `ollama` | `ollama/ollama` | 11434 | `ollama` | — |

**Environment variable sources** (all from `.env` / shell, safe dev defaults):

| Variable | Default | Used By |
|----------|---------|---------|
| `POSTGRES_PASSWORD` | `smsdev` | `db`, `backend` |
| `SECRET_KEY` | `dev-secret-key` | `backend` |
| `LLM_PROVIDER` | `ollama` | `backend`, `agents`, `agent-eval` |
| `LLM_MODEL` | `llama3.2:3b` | `backend`, `agents`, `agent-eval` |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | `agents`, `agent-eval` |
| `ANTHROPIC_API_KEY` | `` | `agents`, `agent-eval` (when provider=anthropic) |
| `RESEARCHER_MCP_URL` | `http://researcher-mcp:8002/sse` | `agents` |
| `SEMANTIC_SCHOLAR_RPM` | `100` | `researcher-mcp` |
| `OPEN_ALEX_RPM` | `300` | `researcher-mcp` |
| `SCIHUB_ENABLED` | `false` | `researcher-mcp` |

**Health check definitions**:
```yaml
db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U sms -d smsresearcher"]
    interval: 5s
    timeout: 5s
    retries: 5

ollama:  # (profile: ollama)
  healthcheck:
    test: ["CMD-SHELL", "ollama list || exit 1"]
    interval: 10s
    timeout: 5s
    retries: 6
```

---

## UV Workspace Entity

The root `pyproject.toml` owns the workspace declaration.

```toml
[tool.uv.workspace]
members = ["backend", "agents", "db", "agent-eval", "researcher-mcp"]

[tool.uv]
dev-dependencies = ["pre-commit>=3.7"]
```

Each member's `pyproject.toml` references siblings:
```toml
# backend/pyproject.toml
[tool.uv.sources]
agents = { workspace = true }
db     = { workspace = true }

# agent-eval/pyproject.toml
[tool.uv.sources]
agents = { workspace = true }
```
