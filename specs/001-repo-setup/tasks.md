# Tasks: Mono-Repo Project Setup

**Branch**: `001-repo-setup` | **Input**: `specs/001-repo-setup/`  
**Prerequisites**: plan.md ✓ | spec.md ✓ | data-model.md ✓ | contracts/ ✓ | research.md ✓ | quickstart.md ✓

**Format**: `[ID] [P?] [Story?] Description — file path`  
- **[P]**: Parallelizable (independent files, no incomplete dependencies)  
- **[USn]**: Maps to User Story n from spec.md

**Total tasks**: 81 | **Phases**: 10

---

## Phase 1: Setup (Repo Root Scaffold)

**Purpose**: Initialize the UV workspace root and shared configuration files that every sub-project depends on.

- [x] T001 Initialize root `pyproject.toml` with UV workspace declaration (`members = ["backend","agents","db","agent-eval","researcher-mcp"]`) and dev-dep `pre-commit>=3.7` — `pyproject.toml`
- [x] T002 [P] Create `.env.example` with all documented env vars (`DATABASE_URL`, `SECRET_KEY`, `LLM_PROVIDER`, `LLM_MODEL`, `OLLAMA_BASE_URL`, `ANTHROPIC_API_KEY`, `RESEARCHER_MCP_URL`, `SEMANTIC_SCHOLAR_RPM`, `OPEN_ALEX_RPM`, `SCIHUB_ENABLED`) — `.env.example`
- [x] T003 [P] Create `.trivyignore` with header comment explaining review process (empty CVE list to start) — `.trivyignore`
- [x] T004 [P] Update `.gitignore` to exclude `.venv/`, `__pycache__/`, `*.pyc`, `.env`, `dist/`, `node_modules/`, `agents/prompts/*/candidates/` — `.gitignore`

---

## Phase 2: Foundational (db sub-project + shared schema)

**Purpose**: The `db` package is imported by `backend`; it MUST exist before backend or agents can be implemented.

**⚠️ CRITICAL**: Phase 3 (US1) cannot begin until this phase is complete.

- [x] T005 Create `db/pyproject.toml` for package `sms-db` (`requires-python = ">=3.14"`, deps: `sqlalchemy[asyncio]>=2`, `alembic`, `asyncpg`, `aiosqlite`; full Ruff + MyPy strict + pytest config) — `db/pyproject.toml`
- [x] T006 [P] Create `db/src/db/__init__.py` and `db/src/db/base.py` with `DeclarativeBase` and async engine factory (`create_async_engine`) — `db/src/db/base.py`
- [x] T007 Create `db/src/db/models.py` with `Study` (id, name, study_type, status, created_at, updated_at), `Paper` (id, title, abstract, doi unique, metadata JSON, created_at), and `StudyPaper` join table (study_id FK, paper_id FK, inclusion_status; composite PK) — `db/src/db/models.py`
- [x] T008 Initialize Alembic in `db/`: create `alembic.ini`, `db/alembic/env.py` (async-compatible), and first migration `0001_initial_schema.py` covering all three tables — `db/alembic/`
- [x] T009 [P] Create placeholder unit test asserting `Study`, `Paper`, `StudyPaper` models instantiate without error — `db/tests/unit/test_models.py`

**Checkpoint**: `uv sync` succeeds; `uv run --package sms-db pytest db/tests/` passes.

---

## Phase 3: User Story 1 — Developer bootstraps Python sub-projects (Priority: P1) 🎯 MVP

**Goal**: `backend/` and `agents/` sub-projects install, lint, type-check, and pass tests on a clean clone.

**Independent Test**: `uv sync && uv run --package sms-backend pytest backend/tests/` passes; `uv run ruff check backend/` and `uv run mypy backend/src` report zero violations.

### backend sub-project

- [x] T010 [US1] Create `backend/pyproject.toml` for package `sms-backend` (`requires-python = ">=3.14"`, deps: `fastapi>=0.111`, `uvicorn[standard]`, `pydantic>=2`, `pydantic-settings`, `structlog`, `python-jose[cryptography]`, `litellm`; workspace deps: `agents`, `db`; full Ruff + MyPy strict + pytest-asyncio config) — `backend/pyproject.toml`
- [x] T011 [US1] Implement `Settings` class (pydantic-settings) and configure `structlog` for JSON output with `stdlib` integration; expose `get_logger()` helper — `backend/src/backend/core/config.py`
- [x] T012 [P] [US1] Implement stub JWT bearer-token middleware (`oauth2_scheme = OAuth2PasswordBearer`; `get_current_user` stub returning a placeholder user; all routes depend on it via `Depends(get_current_user)`) — `backend/src/backend/core/auth.py`
- [x] T013 [P] [US1] Implement FastAPI middleware that binds a request-scoped `structlog` logger (including `method`, `path`); logs response with `status_code` and `duration_ms` after route completes — `backend/src/backend/core/logging.py`
- [x] T014 [US1] Create FastAPI application factory in `main.py`: register `logging.py` middleware, include `api/v1/router`, configure lifespan — `backend/src/backend/main.py`
- [x] T015 [P] [US1] Implement `GET /api/v1/health` returning `{"status": "ok", "version": "0.1.0"}`; protect via `Depends(get_current_user)` stub — `backend/src/backend/api/v1/health.py`
- [x] T016 [P] [US1] Create `APIRouter` including health router; mount at `/api/v1` in `main.py` — `backend/src/backend/api/v1/router.py`
- [x] T017 [US1] Create placeholder test: `GET /api/v1/health` returns 200 using `httpx.AsyncClient` with ASGI transport — `backend/tests/unit/test_health.py`

### agents sub-project

- [x] T018 [US1] Create `agents/pyproject.toml` for package `sms-agents` (`requires-python = ">=3.14"`, deps: `litellm`, `jinja2`, `mcp`, `httpx`; full Ruff + MyPy strict + pytest-asyncio config) — `agents/pyproject.toml`
- [x] T019 [P] [US1] Implement `AgentSettings` (pydantic-settings) reading `LLM_PROVIDER`, `LLM_MODEL`, `OLLAMA_BASE_URL`, `RESEARCHER_MCP_URL` with documented defaults — `agents/src/agents/core/config.py`
- [x] T020 [P] [US1] Implement `LLMClient` wrapping `litellm.acompletion`; model string constructed as `ollama/{LLM_MODEL}` or `anthropic/{LLM_MODEL}` based on `LLM_PROVIDER`; Ollama base URL injected via `api_base` kwarg — `agents/src/agents/core/llm_client.py`
- [x] T021 [US1] Implement `MCPClient` in `mcp_client.py`: connect to `RESEARCHER_MCP_URL` via HTTP/SSE; discover available tools; `to_litellm_tools()` method converting MCP tool schemas to LiteLLM `{"type":"function","function":{...}}` format — `agents/src/agents/core/mcp_client.py`
- [x] T022 [P] [US1] Implement stub `ScreenerAgent` with `run(inclusion_criteria, exclusion_criteria, abstract) -> str`; loads prompts via `PromptLoader`; calls `LLMClient.complete()` — `agents/src/agents/services/screener.py`
- [x] T023 [P] [US1] Implement stub `ExtractorAgent` with `run(data_fields, paper_text) -> str` — `agents/src/agents/services/extractor.py`
- [x] T024 [P] [US1] Implement stub `SynthesiserAgent` with `run(papers_summary, research_question) -> str` — `agents/src/agents/services/synthesiser.py`
- [x] T025 [P] [US1] Create `screener` prompt directory: `system.md` (role definition), `user.md.j2` (Jinja2 template with `{{ inclusion_criteria }}`, `{{ exclusion_criteria }}`, `{{ abstract }}`), empty `candidates/.gitkeep` — `agents/src/agents/prompts/screener/`
- [x] T026 [P] [US1] Create `extractor` prompt directory: `system.md`, `user.md.j2` (`{{ data_fields }}`, `{{ paper_text }}`), `candidates/.gitkeep` — `agents/src/agents/prompts/extractor/`
- [x] T027 [P] [US1] Create `synthesiser` prompt directory: `system.md`, `user.md.j2` (`{{ papers_summary }}`, `{{ research_question }}`), `candidates/.gitkeep` — `agents/src/agents/prompts/synthesiser/`
- [x] T028 [US1] Implement `PromptLoader` helper that reads `system.md` and renders `user.md.j2` via Jinja2 given a context dict; unit test renders each template with sample context and asserts no `UndefinedError` — `agents/src/agents/core/prompt_loader.py`, `agents/tests/unit/test_prompt_loader.py`
- [x] T029 [P] [US1] Implement unit test verifying `LLMClient` constructs correct model string for both `anthropic` and `ollama` providers (mock `litellm.acompletion`) — `agents/tests/unit/test_llm_client.py`

### Metamorphic tests (agents — FR-016)

- [x] T030 [P] [US1] Create metamorphic test conftest with `hypothesis` strategies generating paper abstracts and criteria; define MR fixture base class — `agents/tests/metamorphic/conftest.py`
- [x] T031 [P] [US1] Implement screener MR test: label-preserving transformation (e.g., synonym substitution in abstract) → decision must be identical; document GeMTest as alternative in module docstring — `agents/tests/metamorphic/test_screener_mr.py`
- [x] T032 [P] [US1] Implement extractor MR test: field-order permutation in prompt → extracted values must be identical regardless of order — `agents/tests/metamorphic/test_extractor_mr.py`
- [x] T033 [P] [US1] Implement synthesiser MR test: paper-order permutation in input → synthesised answer must be semantically equivalent (checked via string overlap heuristic in unit form) — `agents/tests/metamorphic/test_synthesiser_mr.py`

---

## Phase 4: User Story 4 — Database schema sub-project verified (Priority: P4)

**Goal**: `db/` is importable by `backend/` with no errors; alembic migration runs cleanly against SQLite.

**Independent Test**: `python -c "from db.models import Study, Paper, StudyPaper"` exits 0 from within the workspace.

*Note*: `db/` implementation tasks are in Phase 2 (Foundational). This phase validates the import contract from `backend`'s perspective.

- [x] T034 [US4] Add integration test in `backend/` verifying `from db.models import Study, Paper, StudyPaper` and `from db.base import engine_factory` complete without `ImportError` — `backend/tests/integration/test_db_import.py`
- [x] T035 [P] [US4] Update `db/README.md` describing schema entities, Alembic usage (`uv run alembic upgrade head`), and how `backend` imports models — `db/README.md`

---

## Phase 5: User Story 2 — Developer bootstraps TypeScript/React frontend (Priority: P2)

**Goal**: `frontend/` installs, lints, formats, and passes Vitest on a clean clone.

**Independent Test**: `npm install && npm test` in `frontend/` exits 0 with at least one passing test.

- [x] T036 [US2] Create `frontend/package.json` with scripts `dev`, `build`, `lint`, `format:check`, `test`, `prepare`; deps: `react@18`, `react-dom@18`; devDeps: `typescript@5`, `vite@5`, `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `eslint@9`, `typescript-eslint`, `eslint-plugin-react-hooks`, `eslint-config-prettier`, `prettier@3`, `husky@9`, `lint-staged` — `frontend/package.json`
- [x] T037 [P] [US2] Create `frontend/tsconfig.json` with `"strict": true`, `"module": "ESNext"`, `"target": "ES2020"`, `"jsx": "react-jsx"` — `frontend/tsconfig.json`
- [x] T038 [P] [US2] Create `frontend/vite.config.ts` configuring Vite 5 build and embedding Vitest config (`globals: true`, `environment: "jsdom"`, `setupFiles`) — `frontend/vite.config.ts`
- [x] T039 [P] [US2] Create `frontend/eslint.config.js` (ESLint 9 flat config) including `typescript-eslint` recommended rules and `eslint-plugin-react-hooks` — `frontend/eslint.config.js`
- [x] T040 [P] [US2] Create `frontend/.prettierrc` with project formatting rules (single quotes, trailing commas, 100 char print width) and `frontend/.prettierignore` — `frontend/.prettierrc`
- [x] T041 [US2] Create `frontend/src/main.tsx` (React 18 `createRoot`) and `frontend/src/App.tsx` (minimal functional component returning placeholder UI) — `frontend/src/main.tsx`, `frontend/src/App.tsx`
- [x] T042 [P] [US2] Create placeholder Vitest test: renders `<App />` without crashing using `@testing-library/react` `render()` — `frontend/src/App.test.tsx`
- [x] T043 [P] [US2] Create `frontend/index.html` as Vite entry point referencing `src/main.tsx` — `frontend/index.html`

---

## Phase 6: User Story 3 — Pre-commit hooks prevent broken commits (Priority: P3)

**Goal**: `git commit` is blocked by hooks on lint/type/test failure in any sub-project.

**Independent Test**: Introduce a deliberate Ruff violation in `backend/`; `git commit` rejects with the violation message.

- [x] T044 [US3] Create root `.pre-commit-config.yaml` with four local hooks (`ruff-check`, `ruff-format`, `mypy`, `pytest`) all using `language: system` and `uv run` as entry; `pass_filenames: false` on all; scoped to Python sub-project paths — `.pre-commit-config.yaml`
- [x] T045 [P] [US3] Install Husky in `frontend/`: create `frontend/.husky/pre-commit` script (`cd frontend && npx lint-staged`) — `frontend/.husky/pre-commit`
- [x] T046 [P] [US3] Create `frontend/.lintstagedrc` targeting `*.{ts,tsx}` with `["eslint --fix", "prettier --write"]` — `frontend/.lintstagedrc`

---

## Phase 7: agent-eval sub-project

**Goal**: `uv run agent-eval --help` shows four commands; `evaluate --help` shows all options (SC-009, SC-010).

**Independent Test**: `uv run --package sms-agent-eval agent-eval --help` exits 0 and lists `evaluate`, `report`, `compare`, `improve`.

- [x] T047 Create `agent-eval/pyproject.toml` for package `sms-agent-eval` (`requires-python = ">=3.14"`, deps: `typer[all]`, `rich`, `deepeval`, `litellm`, `jinja2`; workspace dep: `agents`; entry point: `agent-eval = "agent_eval.cli:app"`; full Ruff + MyPy strict + pytest config) — `agent-eval/pyproject.toml`
- [x] T048 [P] Implement `EvalReport` and `TestCaseResult` Pydantic models (`run_id` UUID, `agent_type`, `prompt_version`, `test_cases`, `overall_score`, `timestamp`; `case_id`, `input`, `output`, `scores`, `passed`) — `agent-eval/src/agent_eval/models.py`
- [x] T049 [P] Implement `LiteLLMJudge` class extending `DeepEvalBaseLLM`; wraps `litellm.completion`; `generate()` and `a_generate()` methods; provider/model/url from env vars — `agent-eval/src/agent_eval/judge/litellm_judge.py`
- [x] T050 Implement `evaluate` command: `--agent`, `--suite` (JSONL path), `--model`, `--provider`, `--ollama-url`, `--threshold`, `--output`; reads JSONL, runs agent, scores with `deepeval` metrics, writes `EvalReport` JSON; Rich table output; exit codes 0/1/2 — `agent-eval/src/agent_eval/commands/evaluate.py`
- [x] T051 [P] Implement `report` command: `--format` (table/json/markdown), `--output`; reads `EvalReport` JSON and renders with Rich — `agent-eval/src/agent_eval/commands/report.py`
- [x] T052 [P] Implement `compare` command: `BASELINE` and `CANDIDATE` positional args; loads both reports; Rich table showing metric deltas with ↑/↓ indicators — `agent-eval/src/agent_eval/commands/compare.py`
- [x] T053 [P] Implement `improve` command: `--report`, `--agent`, `--model`, `--provider`, `--ollama-url`, `--threshold`, `--output-dir`; identifies cases below threshold; calls LLM to suggest revised prompts; writes `system_candidate_{ts}.md` and `user_candidate_{ts}.md.j2` to `candidates/` — `agent-eval/src/agent_eval/commands/improve.py`
- [x] T054 Wire all four commands into Typer `app` with `--version` option and help text `"SMS Researcher — Agent Evaluation CLI"` — `agent-eval/src/agent_eval/cli.py`
- [x] T055 [P] Create unit test: invoke `agent-eval --help` via Typer test runner; assert exit 0; assert output contains `evaluate`, `report`, `compare`, `improve` — `agent-eval/tests/unit/test_cli_help.py`
- [x] T056 [P] Create unit test for `EvalReport` and `TestCaseResult` instantiation and JSON round-trip — `agent-eval/tests/unit/test_models.py`

---

## Phase 8: researcher-mcp sub-project

**Goal**: `uv run researcher-mcp` starts FastMCP server; SSE endpoint responds; all 5 MCP tools are registered (SC-018, SC-019, SC-020).

**Independent Test**: `uv run --package sms-researcher-mcp researcher-mcp` starts; `curl http://localhost:8002/sse` returns valid SSE; `search_papers(query="software engineering", limit=5)` returns ≥1 result with `title` and `doi`.

- [x] T057 Create `researcher-mcp/pyproject.toml` for package `sms-researcher-mcp` (`requires-python = ">=3.14"`, deps: `fastmcp`, `httpx`, `tenacity`, `pydantic>=2`; entry point: `researcher-mcp = "researcher_mcp.server:main"`; full Ruff + MyPy strict + pytest config) — `researcher-mcp/pyproject.toml`
- [x] T058 [P] Implement `ResearcherSettings` (pydantic-settings): `SEMANTIC_SCHOLAR_RPM=100`, `OPEN_ALEX_RPM=300`, `SCIHUB_ENABLED=false`, `SCIHUB_URL`, `UNPAYWALL_EMAIL` — `researcher-mcp/src/researcher_mcp/core/config.py`
- [x] T059 [P] Implement `make_retry_client()` factory returning `httpx.AsyncClient` with `tenacity` retry decorator applied (max 3 attempts, exponential backoff + full jitter, retry on HTTP 5xx and `httpx.TimeoutException`); implement token-bucket rate limiter applied per source — `researcher-mcp/src/researcher_mcp/core/http_client.py`
- [x] T060 Implement `SemanticScholarSource`: `search_papers()`, `get_paper()`, `search_authors()`, `get_author()` methods calling `api.semanticscholar.org`; returns typed Pydantic response objects including `source="semantic_scholar"` — `researcher-mcp/src/researcher_mcp/sources/semantic_scholar.py`
- [x] T061 [P] Implement `OpenAlexSource`: `search_papers()`, `get_paper()` as cascade fallback; maps OpenAlex work schema to shared response types; sets `source="open_alex"` — `researcher-mcp/src/researcher_mcp/sources/open_alex.py`
- [x] T062 [P] Implement `CrossRefSource`: `resolve_doi(doi)` querying `api.crossref.org/works/{doi}`; returns enriched paper metadata; sets `source="crossref"` — `researcher-mcp/src/researcher_mcp/sources/crossref.py`
- [x] T063 [P] Implement `UnpaywallSource`: `fetch_pdf(doi, output_path)` querying `api.unpaywall.org/{doi}`; downloads open-access PDF if `best_oa_location.url_for_pdf` present — `researcher-mcp/src/researcher_mcp/sources/unpaywall.py`
- [x] T064 [P] Implement `ArxivSource`: `fetch_pdf(doi, output_path)` resolving DOI to arXiv ID via CrossRef; downloads `arxiv.org/pdf/{arxiv_id}` — `researcher-mcp/src/researcher_mcp/sources/arxiv.py`
- [x] T065 [P] Implement `SciHubSource`: `fetch_pdf(doi, output_path)` gated by `SCIHUB_ENABLED` check at call time; if disabled raises `MCPError("SCIHUB_DISABLED")`; includes prominent legal warning docstring — `researcher-mcp/src/researcher_mcp/sources/scihub.py`
- [x] T066 Implement `@mcp.tool() search_papers` and `@mcp.tool() get_paper` with Semantic Scholar → OpenAlex cascade; CrossRef enrichment for DOI-prefixed IDs; response includes `source` + `warnings` fields — `researcher-mcp/src/researcher_mcp/tools/search.py`
- [x] T067 [P] Implement `@mcp.tool() search_authors` and `@mcp.tool() get_author` using `SemanticScholarSource` — `researcher-mcp/src/researcher_mcp/tools/authors.py`
- [x] T068 [P] Implement `@mcp.tool() fetch_paper_pdf` with Unpaywall → arXiv → SciHub (opt-in) cascade; returns `FetchResult` with `success`, `output_path`, `source`, `url`, `warnings` — `researcher-mcp/src/researcher_mcp/tools/pdf.py`
- [x] T069 Create `FastMCP` app instance; register all tools from `search.py`, `authors.py`, `pdf.py`; implement `main()` entrypoint running server on `0.0.0.0:8002` — `researcher-mcp/src/researcher_mcp/server.py`
- [x] T070 [P] Unit test: mock primary source to raise `httpx.HTTPStatusError(status=500)`; assert cascade selects secondary source and response `source` field equals `"open_alex"` — `researcher-mcp/tests/unit/test_cascade.py`
- [x] T071 [P] Unit test: mock `httpx.AsyncClient.get` to raise `httpx.TimeoutException` twice then succeed; assert tenacity retried exactly 3 times total and final response returned — `researcher-mcp/tests/unit/test_retry.py`
- [x] T072 [P] Unit test: with `SCIHUB_ENABLED=false` (default), calling `fetch_paper_pdf` after Unpaywall + arXiv both fail returns `success=False` and warning containing `"SciHub disabled"`; assert no outbound request to any scihub URL — `researcher-mcp/tests/unit/test_scihub_disabled.py`

---

## Phase 9: Docker + Docker Compose

**Goal**: `hadolint` passes on all Dockerfiles; `docker compose config` validates; `docker compose up` starts all services (SC-012, SC-013, SC-014).

- [x] T073 Create multi-stage `backend/Dockerfile`: stage 1 (`python:3.14-slim`) installs UV binary, copies workspace source, runs `uv sync --frozen --no-dev --package sms-backend`; stage 2 (`python:3.14-slim`) copies `.venv` + `src`, creates non-root `appuser`, sets `CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]` — `backend/Dockerfile`
- [x] T074 [P] Create multi-stage `researcher-mcp/Dockerfile`: stage 1 (`python:3.14-slim`) installs UV, syncs `sms-researcher-mcp` package; stage 2 (`python:3.14-slim`) copies `.venv` + `src`, creates `appuser`, sets `CMD ["researcher-mcp"]` — `researcher-mcp/Dockerfile`
- [x] T075 [P] Create multi-stage `frontend/Dockerfile`: stage 1 (`node:20-alpine`) runs `npm ci && npm run build`; stage 2 (`nginx:alpine`) copies `dist/` and custom `nginx.conf` — `frontend/Dockerfile`
- [x] T076 [P] Create `frontend/nginx.conf` with `try_files $uri $uri/ /index.html` for SPA routing — `frontend/nginx.conf`
- [x] T077 Create `docker-compose.yml` defining services: `db` (postgres:16-alpine, port 5432, healthcheck `pg_isready`), `backend` (backend/Dockerfile root context, port 8000, depends_on db healthy), `frontend` (frontend/Dockerfile, port 3000→80, depends_on backend), `researcher-mcp` (researcher-mcp/Dockerfile root context, port 8002, always-on), `ollama` (ollama/ollama, port 11434, profile `ollama`, healthcheck); all secrets via env vars with safe dev defaults — `docker-compose.yml`

---

## Phase 10: GitHub Actions CI

**Goal**: CI runs full test matrix, enforces 85% coverage + 85% mutation score, builds + scans + pushes all 3 images to GHCR on `main` merge (SC-008, SC-016, SC-021).

- [x] T078 Create `.github/workflows/ci.yml` with:
  - **Trigger**: `push` to any branch and `pull_request`
  - **Jobs (all parallelized)**:
    - `python-lint`: `uv run ruff check` + `uv run mypy` across all 5 Python sub-projects
    - `python-test`: pytest + coverage (fail < 85% line+branch) for each Python sub-project (matrix)
    - `python-mutation`: `mutmut run` for each Python sub-project; fail if score < 85% (matrix)
    - `frontend-lint`: `npm run lint` + `npm run format:check`
    - `frontend-test`: `npm test` + Vitest coverage (fail < 85%)
    - `frontend-mutation`: Stryker; fail if score < 85%
    - `docker-build-scan`: build backend, frontend, researcher-mcp images; `hadolint` each Dockerfile; `trivy image` each; fail on CRITICAL/HIGH not in `.trivyignore`
    - `ghcr-push` (only on `main` merge): login to GHCR; push `sms-backend`, `sms-frontend`, `sms-researcher-mcp` tagged `{sha}` + `latest`
  — `.github/workflows/ci.yml`

---

## Phase 11: Polish & Cross-Cutting Concerns

**Goal**: All sub-projects have READMEs; mutmut + Stryker configured; hadolint in pre-commit; edge case docs match implementation.

- [x] T079 [P] Add `mutmut` to dev dependencies and configure `[tool.mutmut]` in each Python `pyproject.toml` (5 files); set `paths_to_mutate` to `src/` — `backend/pyproject.toml`, `agents/pyproject.toml`, `db/pyproject.toml`, `agent-eval/pyproject.toml`, `researcher-mcp/pyproject.toml`
- [x] T080 [P] Add `stryker` configuration (`stryker.config.json`) to `frontend/`; set `mutationScore` threshold to 85 — `frontend/stryker.config.json`, `frontend/package.json`
- [x] T081 [P] Add `hadolint` pre-commit hook to root `.pre-commit-config.yaml` (runs `hadolint backend/Dockerfile`, `hadolint researcher-mcp/Dockerfile`, `hadolint frontend/Dockerfile`) — `.pre-commit-config.yaml`
- [x] T082 [P] Create `backend/README.md` with setup steps, env vars, and link to quickstart — `backend/README.md`
- [x] T083 [P] Create `agents/README.md` with setup steps, prompt template format, MCP client usage — `agents/README.md`
- [x] T084 [P] Create `db/README.md` (already started in T035; finalize with Alembic commands) — `db/README.md`
- [x] T085 [P] Create `agent-eval/README.md` with CLI usage examples from contracts/agent-eval-cli.md — `agent-eval/README.md`
- [x] T086 [P] Create `researcher-mcp/README.md` with server startup, env vars, legal SciHub warning, MCP tool summary — `researcher-mcp/README.md`
- [x] T087 [P] Create root `README.md` linking to all sub-project READMEs and quickstart.md — `README.md`

---

## Dependency Graph

```
Phase 1 (Setup)
    │
    └─► Phase 2 (db Foundational)
            │
            └─► Phase 3 (US1: backend + agents) ──────────────────► Phase 7 (agent-eval)
            │       │                                                        │
            │       └─► Phase 4 (US4 validation)                            │
            │                                                                │
            └─► Phase 5 (US2: frontend) [independent of Phase 3]            │
                                                                             │
Phase 3 + Phase 5 complete                                                   │
    │                                                                         │
    └─► Phase 6 (US3: pre-commit) [requires all sub-projects to exist]       │
            │                                                                 │
            └─► Phase 8 (researcher-mcp) [independent of agent-eval]         │
                    │                                                         │
                    └─► Phase 9 (Docker + Compose) [requires all src]  ◄─────┘
                            │
                            └─► Phase 10 (CI/CD) [requires Docker + all tests]
                                    │
                                    └─► Phase 11 (Polish)
```

**Parallel opportunities per phase**:
- Phase 3: T012–T016 (backend core files) ‖ T019–T027 (agents core + prompts) ‖ T030–T033 (metamorphic tests)
- Phase 5: T037–T040 (tsconfig, vite, eslint, prettier) all in parallel
- Phase 7: T048–T053 (agent-eval commands + judge) in parallel after T047
- Phase 8: T058–T065 (sources) in parallel after T057; T066–T068 (tools) in parallel after sources
- Phase 9: T073–T076 (Dockerfiles + nginx) in parallel after T057/T036

---

## Implementation Strategy

**MVP** (deliver first — unblocks all other work):
1. Phase 1 → Phase 2 → Phase 3 (US1)
2. Validates: `uv sync && uv run --package sms-backend pytest backend/tests/` green

**Increment 2**: Phase 4 (US4) + Phase 5 (US2) — parallel after Phase 2
**Increment 3**: Phase 6 (US3 pre-commit) — after Phases 3 + 5
**Increment 4**: Phase 7 (agent-eval) + Phase 8 (researcher-mcp) — parallel after Phase 3
**Increment 5**: Phase 9 (Docker) → Phase 10 (CI) → Phase 11 (Polish)
