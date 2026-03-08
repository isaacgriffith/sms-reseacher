# Feature Specification: Mono-Repo Project Setup

**Feature Branch**: `001-repo-setup`
**Created**: 2026-03-08
**Status**: Draft
**Input**: `docs/repo-setup.md` — mono-repo structure and harness requirements

## Clarifications

### Session 2026-03-08

- Q: Should the TypeScript test runner be Jest (as originally specified) or Vitest? → A: Vitest
- Q: Should pre-commit hooks run the full test suite or a subset? → A: Hybrid — static analysis + unit tests only; integration tests deferred to CI
- Q: Should a CI/CD pipeline be configured as part of this feature? → A: Yes — GitHub Actions; minimal workflow running full test suite on push/PR
- Q: Should the `agents` sub-project communicate with `backend` via HTTP or direct Python import? → A: Direct library import via UV workspace dependency
- Q: Should the backend skeleton include authentication scaffolding? → A: Yes — placeholder JWT/OAuth2 middleware stubs, wired up in a later feature

### Session 2026-03-08 (amendment)

- Q: Should CI push built Docker images to a container registry? → A: Yes — GitHub Container Registry (GHCR); push on merge to `main` only, tagged with commit SHA and `latest`
- Q: How should unfixable upstream CVEs in base images be handled in trivy scans? → A: `.trivyignore` file at repo root; exceptions are explicit, documented, and reviewed via PR
- Q: Should the backend skeleton include structured logging? → A: Yes — `structlog` configured in `backend/core/config.py`; JSON output; all routes and services inherit it

### Session 2026-03-08 (researcher-mcp clarifications)

- Q: Should `researcher-mcp` have a Dockerfile? → A: Yes — multi-stage Dockerfile (`python:3.14-slim` builder + runtime), build context = repo root, same pattern as backend; hadolint + trivy apply; image pushed to GHCR on `main` merge.
- Q: When an external paper search API is unavailable, what should `researcher-mcp` do? → A: Cascade — try Semantic Scholar → OpenAlex in order; return first successful result set; include a `source` field and optional `warnings` list in the response to surface fallback usage.
- Q: Should `researcher-mcp` implement built-in retry / rate-limit handling for external APIs? → A: Yes — exponential backoff (max 3 attempts, jitter) via `tenacity` + per-source configurable rate limiting; rate limit params exposed as env vars (`SEMANTIC_SCHOLAR_RPM`, `OPEN_ALEX_RPM`).
- Q: Should full MyPy + Ruff + pytest tooling apply to all Python sub-projects? → A: Yes — all five (`backend`, `agents`, `db`, `agent-eval`, `researcher-mcp`) must have full tooling; FR-002 updated to reflect this.
- Q: Should `researcher-mcp` Docker image be pushed to GHCR on `main` merges? → A: Yes — push `ghcr.io/<org>/sms-researcher-mcp` tagged with commit SHA and `latest` alongside backend and frontend; SC-016 updated.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer bootstraps Python sub-project (Priority: P1)

A developer clones the repository and is able to initialise, build, and run tests for either the `backend` or `agents` Python sub-project using a single `uv` command sequence. Static analysis (MyPy, Ruff, PyDoc) and tests (pytest) all pass out of the box.

**Why this priority**: The Python sub-projects contain the core application logic. Without a correctly configured Python harness, no meaningful development can begin.

**Independent Test**: Run `uv sync && uv run pytest` inside `backend/` on a freshly cloned repository; all checks pass and at least one placeholder test is green.

**Acceptance Scenarios**:

1. **Given** a fresh clone, **When** `uv sync` is run inside `backend/`, **Then** all dependencies are installed into an isolated virtual environment with no errors.
2. **Given** dependencies installed, **When** `uv run ruff check .` is run, **Then** zero lint violations are reported.
3. **Given** dependencies installed, **When** `uv run mypy .` is run, **Then** zero type errors are reported.
4. **Given** dependencies installed, **When** `uv run pytest` is run, **Then** at least one placeholder test passes.

---

### User Story 2 - Developer bootstraps TypeScript/React frontend (Priority: P2)

A developer can install and validate the `frontend` sub-project with `npm install && npm test`, with ESLint, Prettier, and Vitest all passing.

**Why this priority**: The frontend is the primary user-facing component, but depends on the backend being established first.

**Independent Test**: Run `npm install && npm test` inside `frontend/` on a freshly cloned repository; all checks pass.

**Acceptance Scenarios**:

1. **Given** a fresh clone, **When** `npm install` is run inside `frontend/`, **Then** all dependencies install without errors.
2. **Given** dependencies installed, **When** `npm run lint` is run, **Then** ESLint reports zero violations.
3. **Given** dependencies installed, **When** `npm run format:check` is run, **Then** Prettier reports no formatting issues.
4. **Given** dependencies installed, **When** `npm test` is run, **Then** at least one placeholder Vitest test passes.

---

### User Story 3 - Pre-commit hooks prevent broken commits (Priority: P3)

A developer attempting to commit code that fails static analysis or tests is blocked by pre-commit hooks in whichever sub-project they are working in.

**Why this priority**: Quality gates are important but secondary to having a working baseline harness.

**Independent Test**: Introduce a deliberate lint error in `backend/` and attempt `git commit`; commit is rejected with a clear error message.

**Acceptance Scenarios**:

1. **Given** a staged change with a Ruff lint violation in `backend/`, **When** `git commit` is run, **Then** the commit is rejected and the violation is reported.
2. **Given** a staged change with a failing unit test in `backend/`, **When** `git commit` is run, **Then** the commit is rejected and the test failure is reported.
3. **Given** a staged change with a TypeScript ESLint violation in `frontend/`, **When** `git commit` is run, **Then** the commit is rejected and the violation is reported.
4. **Given** clean, passing code in any sub-project, **When** `git commit` is run, **Then** the commit succeeds.
5. **Given** a failing integration test (not a unit test), **When** `git commit` is run, **Then** the commit is NOT blocked (integration tests run in CI only).

---

### User Story 4 - Developer sets up database schema sub-project (Priority: P4)

A developer can navigate to `db/` and find schema definitions consumable by the backend.

**Why this priority**: The `db` sub-project is the lowest-complexity deliverable; it provides schemas but no standalone runtime.

**Independent Test**: The `db/` directory exists with at least one schema file and a README describing its usage.

**Acceptance Scenarios**:

1. **Given** the repo, **When** a developer opens `db/`, **Then** they find schema definition files (e.g., SQL migrations or SQLAlchemy models).
2. **Given** the `backend/` project, **When** it imports from `db/`, **Then** no import errors occur.

---

### Edge Cases

- What happens if a developer runs pre-commit in a sub-project that hasn't had `uv sync` / `npm install` run yet? → Hook should fail gracefully with an actionable message.
- How does the system handle a Python version mismatch (e.g., Python 3.10 when 3.11+ required)? → `pyproject.toml` should declare `requires-python` and `uv` should surface a clear error.
- What if a developer tries to test `agents` independently of `backend`? → It should work; `agents` is a self-contained Python package with its own test suite, even though backend imports it as a library.
- What if trivy reports a HIGH/CRITICAL CVE in a base image with no available fix? → Add the CVE ID to `.trivyignore` with a comment stating the rationale and a scheduled review date; the addition requires a PR review before merging.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST contain six sub-projects: `frontend`, `backend`, `agents`, `db`, `agent-eval`, and `researcher-mcp`.
- **FR-002**: Every Python sub-project (`backend`, `agents`, `db`, `agent-eval`, `researcher-mcp`) MUST be driven by a `pyproject.toml` that configures MyPy (strict), Ruff (lint + format), PyDoc, and pytest.
- **FR-003**: Each Python sub-project MUST be built and managed with UV (`uv sync`, `uv run`, `uv build`).
- **FR-004**: Each Python sub-project MUST use an isolated virtual environment (`.venv`) created by UV.
- **FR-005**: The `frontend` sub-project MUST be driven by `package.json` (NPM) configuring ESLint, Prettier, and Vitest (formerly Jest).
- **FR-006**: Each sub-project MUST include a pre-commit configuration that runs static-analysis tools and unit tests before every commit; integration tests are excluded from pre-commit and run in CI only.
- **FR-007**: The `backend` sub-project MUST expose a FastAPI application skeleton.
- **FR-008**: The `agents` sub-project MUST be a standalone Python package installed as a UV workspace dependency and imported directly by `backend` (no separate HTTP process for MVP).
- **FR-009**: The `db` sub-project MUST define at least a minimal database schema (tables/models) reusable by `backend`.
- **FR-010**: All sub-projects MUST pass their respective static-analysis and test suites on a clean install.
- **FR-011**: Code MUST follow DRY, SOLID, and GRASP principles; AI-generated implementations MUST be reviewed against these standards.
- **FR-012**: The repository MUST include a GitHub Actions CI workflow (`.github/workflows/ci.yml`) that runs the full test suite (unit + integration) for all sub-projects on every push and pull request.
- **FR-013**: The `backend` skeleton MUST include a placeholder authentication module (`backend/core/auth.py`) with stub JWT bearer-token middleware; all API routes MUST reference this stub via `Depends()` so auth can be fully wired up in a later feature without structural changes.
- **FR-013b**: The `backend` skeleton MUST configure `structlog` for structured JSON logging in `backend/core/config.py`; a FastAPI middleware MUST attach a request-scoped logger to every request; all route handlers and services MUST use this logger rather than `print` or stdlib `logging` directly.
- **FR-014**: Every sub-project MUST configure test coverage reporting with a minimum threshold of 85% (line and branch) enforced in CI; the build MUST fail if coverage falls below this threshold.
- **FR-015**: Every sub-project MUST include mutation testing configuration (`mutmut` for Python, Stryker for TypeScript); mutation testing runs in CI with a minimum mutation score of 85%.
- **FR-016**: The `agents` sub-project MUST include a `tests/metamorphic/` directory containing at least one metamorphic test that defines and validates a metamorphic relation (MR) for each agent task type.
- **FR-017**: The repository MUST contain a fifth sub-project `agent-eval` — a `typer`-based CLI tool (`uv run agent-eval`) for evaluating and improving AI agents.
- **FR-018**: `agent-eval` MUST provide at minimum four commands: `evaluate`, `report`, `compare`, and `improve`.
- **FR-019**: `agent-eval` MUST use `deepeval` as the primary LLM-as-a-Judge evaluation framework; all LLM judge calls (including domain-specific research criteria) MUST route through `litellm` consistent with FR-022.
- **FR-020**: The `agents` sub-project MUST store all system and user prompts as Markdown files under `agents/prompts/{agent_type}/`; user prompts MUST use Jinja2 templating (`.md.j2` extension) for variable substitution.
- **FR-021**: The `agent-eval improve` command MUST read current prompt files, identify low-scoring evaluation cases, and write candidate revised prompts to `agents/prompts/{agent_type}/candidates/` for human review.
- **FR-022**: Both `agents` and `agent-eval` MUST use `litellm` as the sole LLM client; the provider (Anthropic or Ollama), model name, and Ollama base URL MUST be fully configurable via environment variables (`LLM_PROVIDER`, `LLM_MODEL`, `OLLAMA_BASE_URL`) with no code changes required to switch providers.
- **FR-023**: When `LLM_PROVIDER=ollama`, both `agents` and `agent-eval` MUST route all LLM calls through Ollama at `OLLAMA_BASE_URL` (default: `http://localhost:11434`); when `LLM_PROVIDER=anthropic`, calls MUST use `ANTHROPIC_API_KEY`.
- **FR-024**: The LLM-as-a-Judge in `agent-eval` MUST work with any Ollama-served model as the judge, enabling fully offline evaluation runs.
- **FR-025**: The `backend` sub-project MUST include a multi-stage `Dockerfile` (build context: repo root) that produces a minimal production image using the UV workspace.
- **FR-026**: The `frontend` sub-project MUST include a multi-stage `Dockerfile` that builds the Vite bundle and serves it via `nginx:alpine`.
- **FR-027**: Both Dockerfiles MUST pass `hadolint` with zero errors; `hadolint` MUST be configured as a pre-commit hook and run in CI.
- **FR-028**: CI MUST build both images and scan them with `trivy`; builds with CRITICAL or HIGH CVEs not listed in `.trivyignore` MUST fail the pipeline; a repo-root `.trivyignore` file MAY list accepted CVE IDs for unfixable upstream vulnerabilities, each accompanied by a comment documenting the rationale and a review date.
- **FR-029**: The repository root MUST contain a `docker-compose.yml` that orchestrates `frontend`, `backend`, and `db` (PostgreSQL) services; an `ollama` service MUST be included but gated behind a Compose profile (`--profile ollama`) so it is opt-in.
- **FR-030**: The `docker-compose.yml` MUST use health checks on `db` (and `ollama` when profiled) so that `backend` only starts once its dependencies are ready.
- **FR-031**: All configurable values in `docker-compose.yml` (passwords, API keys, model names) MUST be sourced from environment variables with safe defaults for local development.
- **FR-032**: CI MUST push successfully built and scanned Docker images to GitHub Container Registry (GHCR) on every merge to `main`; images MUST be tagged with both the commit SHA and `latest`; pushes on PR branches MUST NOT occur.
- **FR-033**: The repository MUST contain a sixth sub-project `researcher-mcp` — a FastMCP server providing research tool capabilities (paper search, author lookup, PDF fetch) to the `agents` sub-project.
- **FR-034**: `researcher-mcp` MUST expose at minimum five MCP tools: `search_papers`, `get_paper`, `search_authors`, `get_author`, `fetch_paper_pdf`.
- **FR-035**: `researcher-mcp` MUST support at least two academic search sources: Semantic Scholar and OpenAlex; CrossRef MUST be supported for DOI resolution.
- **FR-036**: `researcher-mcp` MUST support PDF fetching via Unpaywall (legal open access) and arXiv; SciHub access MUST be opt-in only, disabled by default (`SCIHUB_ENABLED=false`), and accompanied by a documented legal/ethical warning.
- **FR-037**: The `agents` sub-project MUST configure an MCP client in `agents/core/mcp_client.py` that connects to `researcher-mcp` via HTTP/SSE; the server URL MUST be configurable via `RESEARCHER_MCP_URL` (default: `http://localhost:8002/sse`).
- **FR-038**: MCP tools discovered from `researcher-mcp` MUST be convertible to LiteLLM function-call format and passed to agent LLM calls as the `tools` parameter.
- **FR-039**: `researcher-mcp` MUST be added to `docker-compose.yml` as a service on port 8002, always-on (no profile needed).
- **FR-042**: `researcher-mcp` MUST use `tenacity` for all outbound HTTP calls to external paper APIs; retry policy: max 3 attempts, exponential backoff with jitter, retrying on 5xx responses and timeouts only; per-source requests-per-minute limits MUST be configurable via env vars (`SEMANTIC_SCHOLAR_RPM`, `OPEN_ALEX_RPM`) with documented safe defaults matching each API's public rate limit.
- **FR-041**: `researcher-mcp` MUST implement source-cascade fallback for `search_papers` and `get_paper`: Semantic Scholar is tried first, then OpenAlex; the first successful response is returned; all tool responses MUST include a `source` field (string) indicating which source served the result and an optional `warnings` list for degraded-mode notifications; if all sources fail, an MCP error is raised.
- **FR-040**: The `researcher-mcp` sub-project MUST include a multi-stage `Dockerfile` (build context: repo root) using `python:3.14-slim` for both builder and runtime stages, following the same pattern as the backend Dockerfile; it MUST pass `hadolint` with zero errors, run as a non-root user, and use `--frozen` UV install.

### Key Entities

- **Sub-project**: A self-contained unit of the mono-repo (`frontend`, `backend`, `agents`, `db`, `agent-eval`, `researcher-mcp`) with its own dependency manifest, toolchain, and test suite.
- **Harness**: The combination of static-analysis tools, test runner, and pre-commit hooks configured for a sub-project.
- **Schema**: A database definition (tables, relationships, constraints) living in `db/` and imported by `backend/`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All six sub-project directories exist with correctly populated configuration files (pyproject.toml / package.json / schema files).
- **SC-002**: `uv run pytest` passes in both `backend/` and `agents/` on a clean clone with zero failures.
- **SC-003**: `npm test` (Vitest) passes in `frontend/` on a clean clone with zero failures.
- **SC-004**: `uv run ruff check .` and `uv run mypy .` report zero violations in `backend/` and `agents/`.
- **SC-005**: `npm run lint` and `npm run format:check` report zero violations in `frontend/`.
- **SC-006**: A deliberate lint error causes `git commit` to be rejected in every sub-project.
- **SC-007**: All sub-projects can be set up independently by following a sub-project README in under 5 minutes.
- **SC-008**: The GitHub Actions CI workflow runs green on a clean push to `main` with no failures across all six sub-projects.
- **SC-009**: `uv run agent-eval --help` displays the four top-level commands (`evaluate`, `report`, `compare`, `improve`) without error.
- **SC-010**: `uv run agent-eval evaluate --help` succeeds and shows expected options.
- **SC-011**: At least one prompt template file exists under `agents/prompts/` for each stubbed agent type; the Jinja2 template renders without error given a sample context dict.
- **SC-012**: `hadolint backend/Dockerfile` and `hadolint frontend/Dockerfile` both exit 0.
- **SC-013**: `docker compose config` validates without errors.
- **SC-014**: `docker compose up` (without `--profile ollama`) starts frontend, backend, and db services successfully and backend `/api/v1/health` returns 200.
- **SC-015**: `docker compose --profile ollama up` additionally starts the `ollama` service; `docker compose exec ollama ollama list` exits 0.
- **SC-016**: On a merge to `main`, CI pushes `ghcr.io/<org>/sms-backend`, `ghcr.io/<org>/sms-frontend`, and `ghcr.io/<org>/sms-researcher-mcp` — each tagged with both the commit SHA and `latest`; all three images are visible in the repository's Packages page.
- **SC-017**: A request to any `backend` API endpoint produces a structured JSON log line containing at minimum `method`, `path`, `status_code`, and `duration_ms` fields.
- **SC-018**: `uv run researcher-mcp` starts the FastMCP server; `curl http://localhost:8002/sse` returns a valid SSE response.
- **SC-019**: `search_papers(query="software engineering", limit=5)` called via MCP client returns at least one result with `title` and `doi` fields.
- **SC-020**: `fetch_paper_pdf` with `SCIHUB_ENABLED=false` (default) MUST NOT attempt to contact SciHub.
- **SC-021**: `hadolint researcher-mcp/Dockerfile` exits 0; CI builds and trivy-scans the `sms-researcher-mcp` image and pushes it to GHCR (tagged commit SHA + `latest`) on every merge to `main`.
