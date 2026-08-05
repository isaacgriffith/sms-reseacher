# Implementation Plan: Improve Testing and Fix CI

**Branch**: `011-improve-testing-and-fix-ci` | **Date**: 2026-03-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-improve-testing-and-fix-ci/spec.md`

## Summary

Fix all 9 failing CI jobs (Python lint, 5 Python test/coverage, frontend lint, frontend test/coverage, Docker build), consolidate git hooks into pre-commit with full coverage enforcement, rename project from "SMS" to "Researcher" (dropping `sms-` prefix from 3 Python packages + frontend), and update governance documents to mandate whole-project quality validation.

## Technical Context

**Language/Version**: Python 3.14 (backend, agents, db, agent-eval, researcher-mcp); TypeScript 5.4 / Node 20 LTS (frontend)
**Primary Dependencies**: ruff, mypy, pytest-cov (Python lint/test); ESLint, Prettier, Vitest (frontend lint/test); pre-commit (hooks); Docker, Hadolint, Trivy (containers)
**Storage**: N/A (no schema changes)
**Testing**: pytest with pytest-cov (Python); Vitest with v8 coverage (frontend); Playwright (e2e)
**Target Platform**: GitHub Actions CI; Linux/macOS developer machines
**Project Type**: UV workspace mono-repo (web service + CLI + MCP server + frontend SPA)
**Performance Goals**: Pre-commit hooks complete within reasonable time (~2-5 minutes with full test suites)
**Constraints**: All coverage metrics (line, branch, statement, function) >= 85% across all subprojects
**Scale/Scope**: 5 Python subprojects + 1 frontend; ~20 config files to modify; ~170 files to auto-format

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

| Gate                                                                                                                                          | Status | Notes                                                             |
| --------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ----------------------------------------------------------------- |
| SOLID — no SRP violations in target modules                                                                                                   | PASS   | Config changes only; no new modules                               |
| SOLID — extension points exist (OCP) where variation expected                                                                                 | PASS   | N/A — no new abstractions                                         |
| Structural — no DRY violations (duplication)                                                                                                  | PASS   | CI matrix pattern avoids duplication                              |
| Structural — no YAGNI violations (speculative generality)                                                                                     | PASS   | Only implementing what's needed                                   |
| Code clarity — no long methods (>20 lines) in touched code                                                                                    | PASS   | N/A — config/docs changes                                         |
| Code clarity — no switch/if-chain smells in touched code                                                                                      | PASS   | N/A                                                               |
| Code clarity — no common code smells identified                                                                                               | PASS   | N/A                                                               |
| Refactoring — pre-implementation review completed                                                                                             | PASS   | Research phase identified all root causes                         |
| Refactoring — any found refactors added to task list with tests                                                                               | PASS   | Husky removal is a cleanup task                                   |
| GRASP/patterns — responsibility assignments reviewed                                                                                          | PASS   | N/A                                                               |
| Test coverage — existing tests pass; refactor tests written first                                                                             | PASS   | Coverage fixes restore existing tests                             |
| Toolchain (VII) — no unapproved deps or tool substitutions introduced                                                                         | PASS   | All tools already approved; removing husky in favor of pre-commit |
| Toolchain (VII) — FastAPI/SQLAlchemy 2.x/ARQ/LiteLLM patterns followed                                                                        | PASS   | N/A — no application code changes                                 |
| Observability (VIII) — new models have audit fields + structlog used                                                                          | PASS   | N/A — no new models                                               |
| Observability (VIII) — config via Pydantic BaseSettings + lru_cache                                                                           | PASS   | N/A                                                               |
| Infrastructure (VIII) — Docker services have healthchecks if added                                                                            | PASS   | No new Docker services                                            |
| Language (IX) — React components functional, props typed, ≤100 JSX lines                                                                      | PASS   | N/A — formatting only                                             |
| Language (IX) — Hooks called at top level only (Rules of Hooks); no inline refs in deps                                                       | PASS   | N/A                                                               |
| Language (IX) — No React state mutation; no array-index keys in lists                                                                         | PASS   | N/A                                                               |
| Language (IX) — >3 related useState → useReducer; useCallback only when justified                                                             | PASS   | N/A                                                               |
| Language (IX) — useEffect returns cleanup for all resource-acquiring effects                                                                  | PASS   | N/A                                                               |
| Language (IX) — React.memo applied deliberately; useImperativeHandle used for imperative APIs                                                 | PASS   | N/A                                                               |
| Language (IX) — useWatch used (not watch) for reactive form field subscriptions                                                               | PASS   | N/A                                                               |
| Language (IX) — Vite env vars use VITE\_ prefix + import.meta.env                                                                             | PASS   | N/A                                                               |
| Language (IX) — Python: no plain dict for domain data; pathlib used                                                                           | PASS   | N/A                                                               |
| Language (IX) — Python: no mutable defaults; specific exception handling                                                                      | PASS   | N/A                                                               |
| Language (IX) — TypeScript: no any/enum/non-null(!) without justification                                                                     | PASS   | N/A                                                               |
| Language (IX) — TypeScript: unknown + Zod at all external boundaries                                                                          | PASS   | N/A                                                               |
| Code clarity — all source files have a module-level doc comment                                                                               | PASS   | N/A — no new source files                                         |
| Code clarity — all functions/methods/classes have doc comments                                                                                | PASS   | N/A                                                               |
| Pre-existing issues — all pre-existing test failures, linting errors, and type errors in touched files are resolved before feature completion | PASS   | This IS the feature that resolves them                            |
| Feature completion docs — CLAUDE.md, READMEs, CHANGELOGs updated                                                                              | PASS   | Included as explicit tasks                                        |
| Whole-project lint/type/coverage validation                                                                                                   | PASS   | This is the core deliverable                                      |

## Project Structure

### Documentation (this feature)

```text
specs/011-improve-testing-and-fix-ci/
├── plan.md              # This file
├── research.md          # Root cause analysis for all CI failures
├── data-model.md        # Configuration entities (no DB changes)
├── quickstart.md        # Verification commands
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
# Configuration files touched by this feature
.github/workflows/
├── ci.yml                        # Fix coverage flags, rename packages, fix Docker
└── mutation-python.yml           # Rename packages

.pre-commit-config.yaml           # Add frontend hooks, coverage hooks

backend/
├── pyproject.toml                # Rename sms-backend → backend
├── Dockerfile                    # Update --package flag
├── cosmic-ray.toml               # Update --package flag
├── README.md                     # Rename title
└── CHANGELOG.md                  # Rename title

agent-eval/
├── pyproject.toml                # Rename sms-agent-eval → agent-eval
├── cosmic-ray.toml               # Update --package flag
├── README.md                     # Rename title
└── CHANGELOG.md                  # Rename title

researcher-mcp/
├── pyproject.toml                # Rename sms-researcher-mcp → researcher-mcp
├── Dockerfile                    # Update --package flag
├── cosmic-ray.toml               # Update --package flag
├── README.md                     # Rename title
└── CHANGELOG.md                  # Rename title

frontend/
├── package.json                  # Rename sms-frontend → frontend; remove husky
├── package-lock.json             # Regenerate
├── vite.config.ts                # Add statements + functions thresholds
├── README.md                     # Rename title
├── CHANGELOG.md                  # Rename title
└── src/**                        # Auto-format with prettier (158 files)

backend/src/**                    # Auto-format with ruff (12 files across all Python)
agents/src/**
db/src/**
agent-eval/src/**
researcher-mcp/src/**

README.md                         # Rename to "Researcher"
CLAUDE.md                         # Rename refs + add quality gate section
.specify/memory/constitution.md   # Rename + add whole-project validation
.specify/templates/plan-template.md   # Add whole-project gate row
.specify/templates/tasks-template.md  # Add whole-project validation task
```

**Structure Decision**: Existing web application layout. No new directories or packages created. All changes are to configuration, documentation, and auto-formatting of existing source files.

## Implementation Phases

### Phase 1: CI Pipeline Fixes (P1)

**Goal**: Get all 9 CI jobs passing.

#### 1a. Python Formatting Fix

- Run `uv run ruff format` across all Python source directories
- Run `uv run ruff check --fix` for auto-fixable lint issues
- Verify `uv run ruff check` and `uv run ruff format --check` pass clean

#### 1b. Frontend Formatting Fix

- Run `npx prettier --write src/` in frontend directory
- Run `npx eslint --fix src/` for auto-fixable lint issues
- Verify `npm run lint` and `npm run format:check` pass clean

#### 1c. Python Coverage CI Fix

- Add `covsrc` field to each CI matrix entry in `ci.yml`
- Update test command to include `--cov=${{ matrix.covsrc }}`
- Matrix values: backend→`src/backend`, agents→`src/agents`, db→`src/db`, agent-eval→`src/agent_eval`, researcher-mcp→`src/researcher_mcp`

#### 1d. Frontend Coverage Thresholds

- Add `statements: 85` and `functions: 85` to `vite.config.ts` coverage thresholds
- Write additional frontend tests to bring all 4 metrics above 85%

#### 1e. Frontend Docker Build Fix

- Remove husky from `frontend/package.json` devDependencies
- Remove the `"prepare": "husky"` script
- Remove husky config files (`.husky/` directory if present)
- Verify `docker build -f frontend/Dockerfile -t frontend:ci .` succeeds

### Phase 2: Pre-Commit Consolidation (P2)

**Goal**: All quality gates enforced locally via pre-commit.

#### 2a. Add Frontend Lint Hooks

- Add ESLint hook (language: `system`, entry: `npx eslint`, files: `frontend/src/**/*.{ts,tsx}`)
- Add Prettier hook (language: `system`, entry: `npx prettier --check`, files: `frontend/src/**/*.{ts,tsx}`)

#### 2b. Add Coverage Hooks

- Add per-subproject pytest coverage hooks (5 hooks, one per Python package)
- Add frontend vitest coverage hook
- Each hook uses `pass_filenames: false` and `always_run: true` (or appropriate `types`/`files` filters)

#### 2c. Remove Husky/lint-staged

- Remove husky devDependency and prepare script (done in 1e)
- Remove any lint-staged configuration from package.json
- Remove `.husky/` directory if present

#### 2d. Verify Pre-Commit

- Run `uv run pre-commit run --all-files` and verify all hooks pass

### Phase 3: Project Rename (P3)

**Goal**: Drop `sms-` prefix from all package names; rename project to "Researcher".

#### 3a. Rename Python Packages

- Update `name` field in `backend/pyproject.toml`, `agent-eval/pyproject.toml`, `researcher-mcp/pyproject.toml`
- Run `uv sync --all-packages` to regenerate `uv.lock`
- Verify all Python tests still pass

#### 3b. Rename Frontend Package

- Update `name` in `frontend/package.json`
- Run `npm install` to regenerate `package-lock.json`

#### 3c. Update CI References

- Update all matrix `package` values in `ci.yml` and `mutation-python.yml`
- Update Docker image tags (build, Trivy scan, GHCR push)
- Update E2E postgres service (user: `researcher`, db: `researcher_test`, DATABASE_URL)
- Update `docker-compose.yml` postgres defaults (`POSTGRES_USER`, `POSTGRES_DB`, `DATABASE_URL`)

#### 3d. Update Docker and Cosmic-Ray References

- Update `--package` flags in `backend/Dockerfile`, `researcher-mcp/Dockerfile`
- Update `--package` flags in all 3 `cosmic-ray.toml` files

#### 3e. Update Documentation

- `README.md`: Title → "Researcher", all `--package` references
- `CLAUDE.md`: All `--package` references
- Subproject `README.md` files: Titles
- Subproject `CHANGELOG.md` files: Title lines

### Phase 4: Governance Updates (P4)

**Goal**: Ensure future features maintain whole-project quality.

#### 4a. Update CLAUDE.md

- Add "Feature Completion Quality Gates" section requiring:
  - Full-project ruff check + format + mypy
  - All 5 Python packages pass pytest with `--cov-fail-under=85`
  - Frontend passes `npm run test:coverage`
  - `pre-commit run --all-files` passes

#### 4b. Update Constitution

- Rename "SMS Researcher Constitution" → "Researcher Constitution"
- Update Development Workflow step 6 to explicitly require "all subprojects" validation
- Add language clarifying that lint/type/coverage gates apply to the ENTIRE project
- Update VII.TypeScript to reference pre-commit instead of husky+lint-staged
- Bump version (MINOR — new mandatory requirement)

#### 4c. Update Templates

- `plan-template.md`: Add gate row "Whole-project lint/type/coverage validation"
- `tasks-template.md`: Add mandatory final task for whole-project validation

### Phase 5: Feature Completion Documentation

- Update `CLAUDE.md` with new package names and quality gate requirements
- Update root `README.md` with "Researcher" identity
- Update all subproject `README.md` and `CHANGELOG.md` files
- Update root `CHANGELOG.md` with feature entry

## Complexity Tracking

| Item                                 | Type             | Why Accepted / Resolution                                                                                                                                                          |
| ------------------------------------ | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Husky removal                        | Toolchain change | Constitution VII.TypeScript specifies husky+lint-staged, but this conflicts with VII.Python pre-commit. Constitution amendment in Phase 4b harmonizes to pre-commit for all hooks. |
| 158 frontend files reformatted       | Scope            | Mechanical auto-format change; large diff but zero logic changes. Committed as a single `style:` commit.                                                                           |
| 12 Python files reformatted          | Scope            | Same as above — single `style:` commit.                                                                                                                                            |
| Pre-commit with full coverage (slow) | Tradeoff         | User explicitly chose Option A (full coverage in pre-commit). Commits will take 2-5 minutes but provide full local guarantee.                                                      |
