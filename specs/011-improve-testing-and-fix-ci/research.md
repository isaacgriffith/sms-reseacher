# Research: Improve Testing and Fix CI

## 1. Python Coverage 0% — Root Cause

**Decision**: Add explicit `--cov=src/<pkg>` flags to the CI pytest command for each matrix entry.

**Rationale**: The root `pyproject.toml` defines `[tool.pytest.ini_options]` with `addopts = "--import-mode=importlib"`. When `pytest` is invoked from the repo root (as CI does), it uses the **root** config, not the subproject's `pyproject.toml`. Each subproject has its own `addopts` with `--cov=src/<pkg>`, but these are never read. The CI command only passes `--cov-report=xml:...` and `--cov-fail-under=85` — without `--cov=src/<pkg>`, pytest-cov has no source to measure and reports 0%.

**Fix**: Add a `covsrc` field to each CI matrix entry and pass `--cov=${{ matrix.covsrc }}` in the test command. Matrix values:

- backend: `src/backend`
- agents: `src/agents`
- db: `src/db`
- agent-eval: `src/agent_eval`
- researcher-mcp: `src/researcher_mcp`

**Alternatives considered**:

- Remove root `[tool.pytest.ini_options]`: Would break the `asyncio_mode = "auto"` and `--import-mode=importlib` settings needed globally.
- Merge all configs into root: Not feasible since each package has different `--cov` targets.

## 2. Frontend Docker Build Failure — Root Cause

**Decision**: Make the `prepare` script in `package.json` conditional so it doesn't fail in Docker.

**Rationale**: `frontend/package.json` has `"prepare": "husky"`. During `npm ci`, npm runs the `prepare` lifecycle script. In the Docker build context, there is no `.git` directory, so `husky` fails with exit code 127. This crashes the entire Docker build.

**Fix**: Change the prepare script to: `"prepare": "husky || true"` (tolerates missing git). Alternatively, remove husky entirely since the project uses `pre-commit` (Python) for git hooks. The constitution mentions both "Husky + lint-staged" in VII.TypeScript and "pre-commit" in VII.Python. Since we're consolidating all hooks into `.pre-commit-config.yaml`, removing husky is cleaner.

**Alternatives considered**:

- `npm ci --ignore-scripts` in Dockerfile: Works but suppresses ALL lifecycle scripts which may break other packages.
- `.dockerignore` approach: Won't help since the issue is the lifecycle script, not file copying.

## 3. Python Formatting — 12 Files

**Decision**: Run `uv run ruff format` to auto-fix all formatting issues.

**Rationale**: These are mechanical formatting changes (whitespace, line length, import ordering). The 12 files were likely modified in recent features without running the formatter across the full project.

## 4. Frontend Formatting — 158 Files

**Decision**: Run `npx prettier --write src/` in the frontend directory to auto-fix all formatting issues.

**Rationale**: Same root cause as Python — formatting wasn't applied project-wide after features. The Prettier config is already correct (`singleQuote: true`, `trailingComma: "all"`, `printWidth: 100`).

## 5. Frontend Coverage Thresholds

**Decision**: Add `statements` and `functions` thresholds (85%) to `vite.config.ts`.

**Rationale**: The current config only enforces `lines: 85` and `branches: 85`. The spec requires all four metrics (lines, branches, statements, functions) at 85%. Current coverage is lines: 81.28%, branches: 84.88% — both need improvement through additional tests.

## 6. Pre-Commit Hook Strategy

**Decision**: Consolidate all git hooks into `.pre-commit-config.yaml`. Remove husky/lint-staged from frontend. Add the following hooks:

- Existing: ruff check, ruff format, mypy, pytest (unit), hadolint (3 Dockerfiles)
- New: eslint (frontend), prettier (frontend), pytest with coverage (all 5 packages), vitest with coverage (frontend)

**Rationale**: The project currently has two hook systems (pre-commit for Python, husky for frontend). This creates confusion and maintenance burden. Consolidating into one system (pre-commit) is cleaner. The constitution requires pre-commit hooks (VII.Python) and husky+lint-staged (VII.TypeScript), but these requirements conflict — the constitution update in this feature will harmonize them to use pre-commit for everything.

**Coverage in pre-commit**: Per clarification, full test suites with coverage enforcement run in pre-commit hooks. Each Python subproject gets its own hook with `--cov=src/<pkg> --cov-fail-under=85`. Frontend gets `npm run test:coverage`. These are slow but provide the full local guarantee requested.

**Alternatives considered**:

- Keep both pre-commit and husky: Two hook systems is a maintenance burden and confusing for developers.
- Use only husky: pre-commit has better support for Python tooling.

## 7. Package Rename Scope

**Decision**: Rename three packages: `sms-backend` → `backend`, `sms-agent-eval` → `agent-eval`, `sms-researcher-mcp` → `researcher-mcp`. Also rename `sms-frontend` → `frontend` in package.json. Update all CI, Docker, documentation, and GHCR references.

**Full rename inventory** (excluding specs/ historical docs and uv.lock which auto-regenerates):

### Files requiring edits:

| File                                    | Change                                                                                                 |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `backend/pyproject.toml`                | `name = "sms-backend"` → `"backend"`                                                                   |
| `agent-eval/pyproject.toml`             | `name = "sms-agent-eval"` → `"agent-eval"`                                                             |
| `researcher-mcp/pyproject.toml`         | `name = "sms-researcher-mcp"` → `"researcher-mcp"`                                                     |
| `frontend/package.json`                 | `"name": "sms-frontend"` → `"frontend"`                                                                |
| `.github/workflows/ci.yml`              | Matrix packages, Docker tags, GHCR tags, Trivy refs, E2E db user/name                                  |
| `.github/workflows/mutation-python.yml` | Matrix packages                                                                                        |
| `backend/Dockerfile`                    | `--package sms-backend` → `--package backend`                                                          |
| `researcher-mcp/Dockerfile`             | `--package sms-researcher-mcp` → `--package researcher-mcp`                                            |
| `backend/cosmic-ray.toml`               | `--package sms-backend` → `--package backend`                                                          |
| `agent-eval/cosmic-ray.toml`            | `--package sms-agent-eval` → `--package agent-eval`                                                    |
| `researcher-mcp/cosmic-ray.toml`        | `--package sms-researcher-mcp` → `--package researcher-mcp`                                            |
| `README.md`                             | Title + all `--package` refs                                                                           |
| `CLAUDE.md`                             | All `--package` refs                                                                                   |
| `backend/README.md`                     | Title + `--package` refs                                                                               |
| `agent-eval/README.md`                  | Title + `--package` refs                                                                               |
| `researcher-mcp/README.md`              | Title + `--package` refs                                                                               |
| `frontend/README.md`                    | Title                                                                                                  |
| `backend/CHANGELOG.md`                  | Title line                                                                                             |
| `agent-eval/CHANGELOG.md`               | Title line                                                                                             |
| `researcher-mcp/CHANGELOG.md`           | Title line                                                                                             |
| `frontend/CHANGELOG.md`                 | Title line                                                                                             |
| `.specify/memory/constitution.md`       | Title + any "SMS Researcher" project name refs                                                         |
| `docker-compose.yml`                    | `POSTGRES_USER: sms` → `researcher`, `POSTGRES_DB: sms_researcher` → `researcher`, `DATABASE_URL` refs |
| `frontend/package-lock.json`            | Regenerate after package.json rename                                                                   |

### Files NOT modified (historical records):

- `specs/*/` — Historical specs, plans, tasks, quickstarts retain original references
- `uv.lock` — Auto-regenerated by `uv sync`

## 8. Governance Update Strategy

**Decision**: Update three governance documents to mandate whole-project validation.

### CLAUDE.md changes:

- Add a "Feature Completion Quality Gates" section requiring:
  - `uv run ruff check` + `ruff format --check` + `mypy` across ALL subprojects (not just changed files)
  - `pytest` with `--cov-fail-under=85` for ALL 5 Python packages
  - `cd frontend && npm run test:coverage` passing
  - `pre-commit run --all-files` passing

### Constitution changes:

- Update Development Workflow step 6 to explicitly state "all subprojects" not "touched files"
- Add language clarifying that coverage and lint gates apply to the entire project, not just modified subprojects
- Update project name from "SMS Researcher" to "Researcher"

### Template changes:

- Plan template: Add a gate row for "Whole-project lint/type/coverage validation"
- Tasks template: Add a mandatory final task for whole-project validation
