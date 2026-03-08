# Implementation Plan: Mono-Repo Project Setup

**Branch**: `001-repo-setup` | **Date**: 2026-03-08 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/001-repo-setup/spec.md`

---

## Summary

Scaffold a six-sub-project UV workspace mono-repo for SMS Researcher: `frontend` (React/Vite), `backend` (FastAPI), `agents` (LiteLLM AI agents), `db` (SQLAlchemy/Alembic schemas), `agent-eval` (Typer CLI for agent evaluation), and `researcher-mcp` (FastMCP paper-search server). Every sub-project ships with a complete static-analysis harness, ≥85% test coverage enforced in CI, ≥85% mutation score, Docker images (backend, frontend, researcher-mcp), and a GitHub Actions workflow that builds, scans, and pushes to GHCR on every `main` merge.

---

## Technical Context

**Language/Version**: Python 3.14 (backend, agents, db, agent-eval, researcher-mcp); TypeScript 5.4 / Node 20 LTS (frontend)  
**Primary Dependencies**:
- Backend: `fastapi>=0.111`, `uvicorn[standard]`, `pydantic>=2`, `structlog`, `sqlalchemy[asyncio]>=2`, `alembic`, `python-jose[cryptography]`, `litellm`
- Agents: `litellm`, `jinja2`, `mcp` (MCP client SDK), `httpx`
- DB: `sqlalchemy[asyncio]>=2`, `alembic`, `aiosqlite`, `asyncpg`
- Agent-eval: `typer[all]`, `rich`, `deepeval`, `litellm`, `jinja2`
- Researcher-MCP: `fastmcp`, `httpx`, `tenacity`, `pydantic>=2`
- Frontend: `react@18`, `vite@5`, `typescript@5`, `vitest`, `@testing-library/react`, `eslint@9`, `prettier@3`, `typescript-eslint`

**Storage**: PostgreSQL 16 (production / Docker Compose); SQLite + `aiosqlite` (unit/integration tests)  
**Testing**: pytest + pytest-asyncio + pytest-cov + mutmut (Python); Vitest + Stryker (TypeScript)  
**Target Platform**: Linux server (Docker containers); developer workstation (uv + npm)  
**Performance Goals**: Not defined for harness setup; researcher-mcp API calls covered by tenacity retry with ≤3 attempts  
**Constraints**: Python `requires-python = ">=3.14"`; `uv sync` single-lockfile workspace; hadolint zero-error Dockerfiles; trivy CRITICAL/HIGH CVE block in CI  
**Scale/Scope**: Mono-repo scaffold; 6 sub-projects; CI matrix across all sub-projects

---

## Constitution Check

*No project-specific constitution has been ratified. The following principles from FR-011 govern:*

| Principle | Status | Notes |
|-----------|--------|-------|
| DRY | ✓ Pass | Shared UV lockfile; shared `db` package; single `.pre-commit-config.yaml` at root |
| SOLID | ✓ Pass | Each sub-project has single responsibility; agents imported as library not HTTP service |
| GRASP | ✓ Pass | `researcher-mcp` owns paper-search concerns; `agent-eval` owns evaluation concerns |
| Test-first (≥85% coverage + mutation) | ✓ Pass | FR-014, FR-015 enforce CI gates |
| Simplicity / YAGNI | ✓ Pass | Auth wired up in later feature; SciHub opt-in; Ollama behind Compose profile |

*No gate violations. Complexity tracking not required.*

---

## Project Structure

### Documentation (this feature)

```text
specs/001-repo-setup/
├── plan.md                       # This file
├── research.md                   # Phase 0 — 25 research decisions
├── data-model.md                 # Phase 1 — entities + service registry
├── quickstart.md                 # Phase 1 — developer onboarding guide
├── contracts/
│   ├── backend-api.md            # FastAPI REST skeleton contract
│   ├── agents-api.md             # Python agent library contract
│   ├── agent-eval-cli.md         # Typer CLI contract (evaluate/report/compare/improve)
│   └── researcher-mcp-tools.md  # FastMCP tool contract (5 MCP tools)
└── tasks.md                      # Phase 2 — task list (/speckit.tasks)
```

### Source Code (repository root)

```text
sms-reseacher/                          # Repo root — UV workspace root
├── pyproject.toml                       # [tool.uv.workspace] members list + dev deps
├── uv.lock                              # Shared lockfile (committed)
├── .pre-commit-config.yaml              # Root pre-commit: ruff, mypy, pytest (Python sub-projects)
├── .env.example                         # Template for local env vars
├── .trivyignore                         # Accepted CVE exceptions (documented + reviewed)
├── docker-compose.yml                   # Orchestrates frontend, backend, db, researcher-mcp (+ ollama profile)
├── .github/
│   └── workflows/
│       └── ci.yml                       # Full CI: lint → test → coverage → mutation → docker build → trivy → GHCR push
│
├── backend/
│   ├── pyproject.toml                   # sms-backend; deps: fastapi, uvicorn, structlog, litellm, agents, db
│   ├── Dockerfile                       # Multi-stage; build context = repo root; python:3.14-slim
│   ├── src/
│   │   └── backend/
│   │       ├── __init__.py
│   │       ├── main.py                  # FastAPI app factory; lifespan; middleware wiring
│   │       ├── core/
│   │       │   ├── config.py            # Settings (pydantic-settings); structlog config; env vars
│   │       │   ├── auth.py              # Stub JWT bearer-token middleware; Depends() stub
│   │       │   └── logging.py           # Request-scoped logger middleware
│   │       └── api/
│   │           └── v1/
│   │               ├── router.py
│   │               └── health.py        # GET /api/v1/health → {status, version}
│   └── tests/
│       ├── unit/
│       │   └── test_health.py           # Placeholder: health endpoint returns 200
│       └── integration/
│           └── test_app_startup.py
│
├── agents/
│   ├── pyproject.toml                   # sms-agents; deps: litellm, jinja2, mcp, httpx
│   ├── src/
│   │   └── agents/
│   │       ├── __init__.py
│   │       ├── core/
│   │       │   ├── config.py            # LLM_PROVIDER, LLM_MODEL, OLLAMA_BASE_URL, RESEARCHER_MCP_URL
│   │       │   ├── llm_client.py        # LiteLLM wrapper (Anthropic + Ollama, config-driven)
│   │       │   └── mcp_client.py        # FastMCP HTTP/SSE client; tool discovery + LiteLLM conversion
│   │       ├── services/
│   │       │   ├── screener.py          # Stub screener agent
│   │       │   ├── extractor.py         # Stub extractor agent
│   │       │   └── synthesiser.py       # Stub synthesiser agent
│   │       └── prompts/
│   │           ├── screener/
│   │           │   ├── system.md
│   │           │   ├── user.md.j2       # Jinja2: {inclusion_criteria}, {exclusion_criteria}
│   │           │   └── candidates/      # Human-reviewed prompt revisions (gitignored on main)
│   │           ├── extractor/
│   │           │   ├── system.md
│   │           │   └── user.md.j2       # Jinja2: {data_fields}, {paper_text}
│   │           └── synthesiser/
│   │               ├── system.md
│   │               └── user.md.j2       # Jinja2: {papers_summary}, {research_question}
│   └── tests/
│       ├── unit/
│       │   ├── test_llm_client.py
│       │   └── test_prompt_loader.py    # Renders each .md.j2 with sample context; asserts no error
│       ├── metamorphic/
│       │   ├── conftest.py              # MR fixtures (hypothesis strategies)
│       │   ├── test_screener_mr.py      # MR: label-preserving → same decision
│       │   ├── test_extractor_mr.py
│       │   └── test_synthesiser_mr.py
│       └── integration/
│           └── test_mcp_client.py
│
├── db/
│   ├── pyproject.toml                   # sms-db; deps: sqlalchemy[asyncio], alembic, asyncpg, aiosqlite
│   ├── src/
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── models.py                # Study, Paper, StudyPaper SQLAlchemy models
│   │       └── base.py                  # DeclarativeBase; async engine factory
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 0001_initial_schema.py   # Study + Paper + StudyPaper tables
│   ├── alembic.ini
│   └── tests/
│       └── unit/
│           └── test_models.py           # Placeholder: Study model instantiation
│
├── agent-eval/
│   ├── pyproject.toml                   # sms-agent-eval; entry: agent-eval = "agent_eval.cli:app"
│   ├── src/
│   │   └── agent_eval/
│   │       ├── __init__.py
│   │       ├── cli.py                   # Typer app; commands: evaluate, report, compare, improve
│   │       ├── commands/
│   │       │   ├── evaluate.py
│   │       │   ├── report.py
│   │       │   ├── compare.py
│   │       │   └── improve.py
│   │       ├── judge/
│   │       │   └── litellm_judge.py     # DeepEvalBaseLLM wrapper over LiteLLM
│   │       └── models.py                # EvalReport, TestCaseResult pydantic models
│   └── tests/
│       ├── unit/
│       │   ├── test_cli_help.py         # agent-eval --help exits 0; shows 4 commands
│       │   └── test_models.py
│       └── integration/
│
├── researcher-mcp/
│   ├── pyproject.toml                   # sms-researcher-mcp; entry: researcher-mcp = "researcher_mcp.server:main"
│   ├── Dockerfile                       # Multi-stage; build context = repo root; python:3.14-slim
│   ├── src/
│   │   └── researcher_mcp/
│   │       ├── __init__.py
│   │       ├── server.py                # FastMCP app; registers all tools; main() entrypoint
│   │       ├── core/
│   │       │   ├── config.py            # SEMANTIC_SCHOLAR_RPM, OPEN_ALEX_RPM, SCIHUB_ENABLED, SCIHUB_URL
│   │       │   └── http_client.py       # httpx AsyncClient + tenacity retry decorator factory
│   │       ├── sources/
│   │       │   ├── semantic_scholar.py  # search_papers, get_paper, search_authors, get_author
│   │       │   ├── open_alex.py         # cascade fallback implementation
│   │       │   ├── crossref.py          # DOI resolution
│   │       │   ├── unpaywall.py         # PDF fetch (legal open access)
│   │       │   ├── arxiv.py             # PDF fetch (preprints)
│   │       │   └── scihub.py            # PDF fetch (opt-in; SCIHUB_ENABLED=false default)
│   │       └── tools/
│   │           ├── search.py            # @mcp.tool() search_papers, get_paper (cascade)
│   │           ├── authors.py           # @mcp.tool() search_authors, get_author
│   │           └── pdf.py               # @mcp.tool() fetch_paper_pdf (Unpaywall→arXiv→SciHub)
│   └── tests/
│       ├── unit/
│       │   ├── test_cascade.py          # Cascade fallback: primary fails → secondary used
│       │   ├── test_retry.py            # tenacity retry on 5xx
│       │   └── test_scihub_disabled.py  # SCIHUB_ENABLED=false → no SciHub contact
│       └── integration/
│           └── test_mcp_tools.py
│
└── frontend/
    ├── package.json                     # scripts: dev, build, lint, format:check, test, prepare
    ├── tsconfig.json                    # strict: true
    ├── vite.config.ts                   # Vite 5 + Vitest config
    ├── eslint.config.js                 # ESLint 9 flat config; typescript-eslint; react-hooks
    ├── .prettierrc                       # Prettier 3 rules
    ├── .husky/
    │   └── pre-commit                   # cd frontend && npx lint-staged
    ├── .lintstagedrc                    # {"*.{ts,tsx}": ["eslint --fix", "prettier --write"]}
    ├── Dockerfile                       # Multi-stage: node:20-alpine build + nginx:alpine serve
    ├── nginx.conf                       # SPA fallback: try_files $uri $uri/ /index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        └── App.test.tsx                 # Placeholder: renders without crashing
```

**Structure Decision**: Option 2 (web application) extended to a 6-sub-project UV workspace mono-repo. Each Python sub-project is a workspace member under the shared `uv.lock`; the frontend is managed independently via npm. Docker Compose at the repo root wires all services together.

---

## Complexity Tracking

*No constitution violations. Six sub-projects are mandated by FR-001 and each has a distinct, non-overlapping responsibility.*

| Sub-project | Responsibility | Simpler alternative rejected because |
|-------------|---------------|-------------------------------------|
| `backend` | API gateway; orchestrates agents | Cannot merge with `agents`; agents must be importable standalone (FR-008) |
| `agents` | LLM agent logic + prompts | Separate package enables `agent-eval` to import without pulling in HTTP server |
| `db` | Schema definitions + migrations | Separate package enables `backend` + tests to share models without circular deps |
| `agent-eval` | CLI evaluation tooling | Separate package avoids polluting production `agents` with evaluation/judge deps |
| `researcher-mcp` | Paper search + PDF fetch (MCP server) | Separate service enables independent scaling; MCP protocol requires a running server |
| `frontend` | Researcher-facing SPA | TypeScript/React cannot be a UV workspace member |

---

## Phase 0: Research Status

All 25 research decisions documented in [`research.md`](research.md). No NEEDS CLARIFICATION items remain.

Key decisions (summary):
| Topic | Decision |
|-------|----------|
| Python version | 3.14 (fallback: 3.13) |
| Python workspace | UV workspace, shared `uv.lock` |
| Lint/format | Ruff (replaces flake8, isort, black, pydocstyle) |
| Type check | MyPy strict |
| Testing | pytest + pytest-asyncio + pytest-cov; mutmut ≥85% |
| Frontend scaffold | Vite 5 + React 18 + TypeScript 5 + Vitest + Stryker |
| Backend | FastAPI 0.111+ + Pydantic v2 + structlog |
| Database | SQLAlchemy 2.x async + Alembic; PostgreSQL prod / SQLite dev |
| LLM abstraction | LiteLLM (Anthropic + Ollama, config-driven via env vars) |
| Agents integration | Direct Python import (UV workspace dep) |
| MCP server | FastMCP (researcher-mcp); HTTP/SSE port 8002 |
| MCP client | `agents/core/mcp_client.py`; RESEARCHER_MCP_URL configurable |
| Paper sources | Semantic Scholar → OpenAlex cascade; CrossRef for DOI |
| PDF sources | Unpaywall → arXiv → SciHub (opt-in, default off) |
| API failure | Cascade fallback; tenacity retry (max 3, exp backoff + jitter) |
| Rate limiting | Per-source env vars: SEMANTIC_SCHOLAR_RPM, OPEN_ALEX_RPM |
| Docker (backend) | Multi-stage python:3.14-slim; repo root build context |
| Docker (frontend) | Multi-stage node:20-alpine + nginx:alpine |
| Docker (researcher-mcp) | Multi-stage python:3.14-slim; repo root build context |
| Compose | frontend + backend + db + researcher-mcp always-on; ollama profile |
| CI | GitHub Actions; full matrix; GHCR push on main (all 3 images) |
| CVE handling | .trivyignore with documented rationale + review date |
| Agent evaluation | deepeval + LiteLLMJudge wrapper; Typer CLI |
| Prompt templates | Markdown + Jinja2 (.md.j2); per agent-type directory |
| Metamorphic testing | hypothesis + pytest MR fixtures; GeMTest as documented alt |

---

## Phase 1: Design Artifacts

All Phase 1 artifacts are complete:

| Artifact | Status | Notes |
|----------|--------|-------|
| [`data-model.md`](data-model.md) | Complete | 6 sub-projects; Study/Paper/StudyPaper schema; Docker Compose registry |
| [`quickstart.md`](quickstart.md) | Complete | All sub-projects including researcher-mcp; env vars table |
| [`contracts/backend-api.md`](contracts/backend-api.md) | Complete | FastAPI REST skeleton |
| [`contracts/agents-api.md`](contracts/agents-api.md) | Complete | Python agent library |
| [`contracts/agent-eval-cli.md`](contracts/agent-eval-cli.md) | Complete | Typer CLI (evaluate/report/compare/improve) |
| [`contracts/researcher-mcp-tools.md`](contracts/researcher-mcp-tools.md) | Complete | FastMCP 5-tool contract |

---

## Next Step

Run `/speckit.tasks` to generate the dependency-ordered task list (`tasks.md`).
