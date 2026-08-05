# Tasks: Improve Testing and Fix CI

**Input**: Design documents from `/specs/011-improve-testing-and-fix-ci/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new project structure needed. This feature modifies existing config files only.

- [x] T001 Verify current CI failure state by reviewing latest GitHub Actions run output to confirm all 9 jobs fail as described in spec

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Fix the Docker build blocker and remove husky — these unblock both US1 (Docker CI job) and US2 (pre-commit consolidation).

**CRITICAL**: No user story work can begin until this phase is complete.

- [x] T002 Remove `husky` from `devDependencies` and remove `"prepare": "husky"` script from `frontend/package.json`; remove `lint-staged` config block from `frontend/package.json`; delete `frontend/.husky/` directory if it exists
- [x] T003 Run `cd frontend && npm install` to regenerate `frontend/package-lock.json` after husky removal; verify `npm ci` succeeds without errors

**Checkpoint**: Docker build blocker resolved; husky removed. User story implementation can begin.

---

## Phase 3: User Story 1 — All CI Pipelines Pass (Priority: P1) MVP

**Goal**: Fix all 9 failing GitHub Actions CI jobs so the project has a green baseline.

**Independent Test**: Push branch and verify all CI jobs pass: Python lint, 5 Python test/coverage jobs, frontend lint, frontend tests, Docker build + Hadolint + Trivy.

### 3a. Python Formatting Fix

- [x] T004 [P] [US1] Run `uv run ruff format backend/src agents/src db/src agent-eval/src researcher-mcp/src` to auto-fix all 12 Python formatting violations
- [x] T005 [P] [US1] Run `uv run ruff check --fix backend/src agents/src db/src agent-eval/src researcher-mcp/src` to auto-fix any fixable lint issues; then run `uv run ruff check backend/src agents/src db/src agent-eval/src researcher-mcp/src` to verify zero remaining violations
- [x] T006 [US1] Run `uv run ruff format --check backend/src agents/src db/src agent-eval/src researcher-mcp/src` to confirm zero formatting issues remain

### 3b. Python Lint Fix (mypy)

- [x] T007 [US1] Run `uv run mypy backend/src agents/src db/src agent-eval/src researcher-mcp/src` and fix any type errors that are reported; repeat until zero errors

### 3c. Frontend Formatting Fix

- [x] T008 [P] [US1] Run `cd frontend && npx prettier --write src/` to auto-fix all 158 frontend formatting violations
- [x] T009 [P] [US1] Run `cd frontend && npx eslint --fix src/` to auto-fix any fixable ESLint issues; then run `cd frontend && npm run lint` to verify zero remaining violations
- [x] T010 [US1] Run `cd frontend && npm run format:check` to confirm zero Prettier issues remain

### 3d. Python Coverage CI Fix

- [x] T011 [US1] Add `covsrc` field to each matrix entry in `.github/workflows/ci.yml` python-test job: `backend` → `src/backend`, `agents` → `src/agents`, `db` → `src/db`, `agent-eval` → `src/agent_eval`, `researcher-mcp` → `src/researcher_mcp`; update the pytest command to include `--cov=${{ matrix.covsrc }}`

### 3e. Python Coverage Gap Fix

- [x] T012 [US1] Run `uv run --package backend pytest backend/tests/ --cov=src/backend --cov-report=term-missing --cov-fail-under=85` locally; if coverage is below 85%, write additional tests in `backend/tests/` to reach the threshold
- [x] T013 [P] [US1] Run `uv run --package agents pytest agents/tests/ --cov=src/agents --cov-report=term-missing --cov-fail-under=85` locally; if coverage is below 85%, write additional tests in `agents/tests/` to reach the threshold
- [x] T014 [P] [US1] Run `uv run --package db pytest db/tests/ --cov=src/db --cov-report=term-missing --cov-fail-under=85` locally; if coverage is below 85%, write additional tests in `db/tests/` to reach the threshold
- [x] T015 [P] [US1] Run `uv run --package agent-eval pytest agent-eval/tests/ --cov=src/agent_eval --cov-report=term-missing --cov-fail-under=85` locally; if coverage is below 85%, write additional tests in `agent-eval/tests/` to reach the threshold
- [x] T016 [P] [US1] Run `uv run --package researcher-mcp pytest researcher-mcp/tests/ --cov=src/researcher_mcp --cov-report=term-missing --cov-fail-under=85` locally; if coverage is below 85%, write additional tests in `researcher-mcp/tests/` to reach the threshold

### 3f. Frontend Coverage Fix

- [x] T017 [US1] Add `statements: 85` and `functions: 85` to the `thresholds` object in `frontend/vite.config.ts` alongside existing `lines: 85` and `branches: 85`
- [x] T018 [US1] Run `cd frontend && npm run test:coverage` locally; if any metric (lines, branches, statements, functions) is below 85%, write additional tests in `frontend/src/` to reach the threshold on all four metrics

### 3g. Docker Build Verification

- [ ] T019 [US1] Verify Docker build succeeds for all three images: run `docker build -f backend/Dockerfile -t backend:ci .`, `docker build -f researcher-mcp/Dockerfile -t researcher-mcp:ci .`, and `docker build -f frontend/Dockerfile -t frontend:ci .`; fix any remaining build issues

### 3h. Validation

- [ ] T020 [US1] Run the full validation sequence from `specs/011-improve-testing-and-fix-ci/quickstart.md` "Verify CI Fixes" section to confirm all lint, test, coverage, and Docker checks pass locally

**Checkpoint**: All 9 CI jobs should now pass. US1 is complete and independently verifiable.

---

## Phase 4: User Story 2 — Pre-Commit Hooks Enforce Quality Gates (Priority: P2)

**Goal**: Consolidate all quality gate hooks into `.pre-commit-config.yaml` with full coverage enforcement.

**Independent Test**: Run `uv run pre-commit run --all-files` and verify all hooks pass.

### 4a. Add Frontend Lint Hooks

- [ ] T021 [P] [US2] Add ESLint pre-commit hook to `.pre-commit-config.yaml`: `id: eslint`, `language: system`, `entry: npx eslint`, `args: ["frontend/src/"]`, `pass_filenames: false`, `files: ^frontend/src/.*\\.tsx?$`
- [ ] T022 [P] [US2] Add Prettier pre-commit hook to `.pre-commit-config.yaml`: `id: prettier-check`, `language: system`, `entry: npx prettier --check`, `args: ["frontend/src/"]`, `pass_filenames: false`, `files: ^frontend/src/.*\\.tsx?$`

### 4b. Add Python Coverage Hooks

- [ ] T023 [P] [US2] Add pytest-coverage hook for backend to `.pre-commit-config.yaml`: `id: pytest-cov-backend`, `language: system`, `entry: uv run --package backend pytest`, `args: ["backend/tests/", "--cov=src/backend", "--cov-fail-under=85"]`, `pass_filenames: false`, `always_run: true`, `types: [python]`
- [ ] T024 [P] [US2] Add pytest-coverage hook for agents to `.pre-commit-config.yaml`: `id: pytest-cov-agents`, `language: system`, `entry: uv run --package agents pytest`, `args: ["agents/tests/", "--cov=src/agents", "--cov-fail-under=85"]`, `pass_filenames: false`, `always_run: true`, `types: [python]`
- [ ] T025 [P] [US2] Add pytest-coverage hook for db to `.pre-commit-config.yaml`: `id: pytest-cov-db`, `language: system`, `entry: uv run --package db pytest`, `args: ["db/tests/", "--cov=src/db", "--cov-fail-under=85"]`, `pass_filenames: false`, `always_run: true`, `types: [python]`
- [ ] T026 [P] [US2] Add pytest-coverage hook for agent-eval to `.pre-commit-config.yaml`: `id: pytest-cov-agent-eval`, `language: system`, `entry: uv run --package agent-eval pytest`, `args: ["agent-eval/tests/", "--cov=src/agent_eval", "--cov-fail-under=85"]`, `pass_filenames: false`, `always_run: true`, `types: [python]`
- [ ] T027 [P] [US2] Add pytest-coverage hook for researcher-mcp to `.pre-commit-config.yaml`: `id: pytest-cov-researcher-mcp`, `language: system`, `entry: uv run --package researcher-mcp pytest`, `args: ["researcher-mcp/tests/", "--cov=src/researcher_mcp", "--cov-fail-under=85"]`, `pass_filenames: false`, `always_run: true`, `types: [python]`

### 4c. Add Frontend Coverage Hook

- [ ] T028 [US2] Add vitest-coverage hook to `.pre-commit-config.yaml`: `id: vitest-coverage`, `language: system`, `entry: npm run test:coverage`, `args: ["--prefix", "frontend"]`, `pass_filenames: false`, `always_run: true`, `files: ^frontend/src/`

### 4d. Update Existing pytest Hook

- [ ] T029 [US2] Update the existing `pytest` hook in `.pre-commit-config.yaml` to remove it (its role is now covered by the per-package coverage hooks T023–T027); or keep it as a fast unit-test-only hook if desired for quick feedback

### 4e. Validation

- [ ] T030 [US2] Run `uv run pre-commit run --all-files` and verify ALL hooks pass: ruff-check, ruff-format, mypy, eslint, prettier-check, pytest-cov-backend, pytest-cov-agents, pytest-cov-db, pytest-cov-agent-eval, pytest-cov-researcher-mcp, vitest-coverage, hadolint-backend, hadolint-researcher-mcp, hadolint-frontend

**Checkpoint**: Pre-commit hooks provide full local quality gate enforcement. US2 is complete.

---

## Phase 5: User Story 3 — Project Renamed from SMS to Researcher (Priority: P3)

**Goal**: Drop `sms-` prefix from all package names; rename project to "Researcher" in all documentation.

**Independent Test**: Run `grep -r "sms-backend\|sms-agent-eval\|sms-researcher-mcp\|sms-frontend" --include="*.toml" --include="*.yml" --include="*.yaml" --include="*.json" --include="*.md" --include="Dockerfile" --exclude-dir=.venv --exclude-dir=specs --exclude-dir=node_modules .` and verify zero matches. Then run `uv sync --all-packages` and `cd frontend && npm install` to verify workspace resolves.

### 5a. Rename Python Packages

- [ ] T031 [P] [US3] Change `name = "sms-backend"` to `name = "backend"` in `backend/pyproject.toml`
- [ ] T032 [P] [US3] Change `name = "sms-agent-eval"` to `name = "agent-eval"` in `agent-eval/pyproject.toml`
- [ ] T033 [P] [US3] Change `name = "sms-researcher-mcp"` to `name = "researcher-mcp"` in `researcher-mcp/pyproject.toml`
- [ ] T034 [US3] Run `uv sync --all-packages` to regenerate `uv.lock` with new package names; verify no resolution errors

### 5b. Rename Frontend Package

- [ ] T035 [US3] Change `"name": "sms-frontend"` to `"name": "frontend"` in `frontend/package.json`; run `cd frontend && npm install` to regenerate `frontend/package-lock.json`

### 5c. Update CI Workflow References

- [ ] T036 [US3] Update `.github/workflows/ci.yml` python-test matrix: change `sms-backend` → `backend`, `sms-agent-eval` → `agent-eval`, `sms-researcher-mcp` → `researcher-mcp` in all `package` fields
- [ ] T037 [US3] Update `.github/workflows/ci.yml` Docker build tags: change `sms-backend:ci` → `backend:ci`, `sms-researcher-mcp:ci` → `researcher-mcp:ci`, `sms-frontend:ci` → `frontend:ci`
- [ ] T038 [US3] Update `.github/workflows/ci.yml` Trivy scan image-ref values: change `sms-backend:ci` → `backend:ci`, `sms-researcher-mcp:ci` → `researcher-mcp:ci`, `sms-frontend:ci` → `frontend:ci`
- [ ] T039 [US3] Update `.github/workflows/ci.yml` GHCR push tags: replace all `sms-backend` → `backend`, `sms-researcher-mcp` → `researcher-mcp`, `sms-frontend` → `frontend` in image tag lines
- [ ] T040 [US3] Update `.github/workflows/ci.yml` E2E test service: change `POSTGRES_USER: sms` → `POSTGRES_USER: researcher`, `POSTGRES_DB: sms_test` → `POSTGRES_DB: researcher_test`, and `DATABASE_URL` to use `researcher:researcher@localhost:5432/researcher_test`
- [ ] T041 [US3] Update `.github/workflows/mutation-python.yml` matrix: change `sms-backend` → `backend`, `sms-agent-eval` → `agent-eval`, `sms-researcher-mcp` → `researcher-mcp`

### 5d. Update Docker and Cosmic-Ray References

- [ ] T042 [P] [US3] Update `backend/Dockerfile` line 18: change `--package sms-backend` → `--package backend`
- [ ] T043 [P] [US3] Update `researcher-mcp/Dockerfile` line 16: change `--package sms-researcher-mcp` → `--package researcher-mcp`
- [ ] T044 [P] [US3] Update `backend/cosmic-ray.toml` line 5: change `--package sms-backend` → `--package backend`
- [ ] T045 [P] [US3] Update `agent-eval/cosmic-ray.toml` line 5: change `--package sms-agent-eval` → `--package agent-eval`
- [ ] T046 [P] [US3] Update `researcher-mcp/cosmic-ray.toml` line 5: change `--package sms-researcher-mcp` → `--package researcher-mcp`

### 5e. Update docker-compose.yml

- [ ] T047 [US3] Update `docker-compose.yml`: change `POSTGRES_USER` default from `sms` → `researcher`, `POSTGRES_DB` default from `sms_researcher` → `researcher`, and all `DATABASE_URL` defaults to use `researcher:...@db:5432/researcher`

### 5f. Update Pre-Commit Hooks

- [ ] T048 [US3] Update all `--package` references in `.pre-commit-config.yaml` coverage hooks (T023–T027) if they were written with old names; verify hook entries use `backend`, `agent-eval`, `researcher-mcp` (not `sms-` prefixed)

### 5g. Validation

- [ ] T049 [US3] Run `grep -r "sms-backend\|sms-agent-eval\|sms-researcher-mcp\|sms-frontend" --include="*.toml" --include="*.yml" --include="*.yaml" --include="*.json" --include="*.md" --include="Dockerfile" --exclude-dir=.venv --exclude-dir=specs --exclude-dir=node_modules .` and verify zero matches
- [ ] T050 [US3] Run `uv sync --all-packages` and all 5 Python test suites to verify workspace resolves and tests pass with new names
- [ ] T051 [US3] Run `docker build -f backend/Dockerfile -t backend:ci .`, `docker build -f researcher-mcp/Dockerfile -t researcher-mcp:ci .`, `docker build -f frontend/Dockerfile -t frontend:ci .` to verify all Docker builds succeed with new names

**Checkpoint**: All `sms-` prefixes removed. US3 is complete.

---

## Phase 6: User Story 4 — Governance Documents Enforce Whole-Project Quality (Priority: P4)

**Goal**: Update CLAUDE.md, constitution, and templates to mandate whole-project quality validation at feature completion.

**Independent Test**: Review updated documents and verify they contain explicit whole-project validation language.

### 6a. Update CLAUDE.md

- [ ] T052 [US4] Add a "Feature Completion Quality Gates" section to `CLAUDE.md` requiring: (1) `uv run ruff check` + `ruff format --check` + `mypy` across ALL subproject source directories, (2) `pytest --cov-fail-under=85` for ALL 5 Python packages, (3) `cd frontend && npm run test:coverage` passing, (4) `uv run pre-commit run --all-files` passing — emphasize "all subprojects, not just changed files"

### 6b. Update Constitution

- [ ] T053 [US4] Rename title from "SMS Researcher Constitution" to "Researcher Constitution" in `.specify/memory/constitution.md`; update any "SMS Researcher" or "SMS research platform" references to "Researcher" throughout the document
- [ ] T054 [US4] Update Development Workflow step 6 in `.specify/memory/constitution.md` to explicitly state that lint, type-check, and coverage gates apply to "all subprojects in the workspace" not just "touched files" or "modified subprojects"
- [ ] T055 [US4] Update section VII.TypeScript Toolchain in `.specify/memory/constitution.md`: replace "Husky + `lint-staged` MUST run..." with "Pre-commit hooks MUST run `eslint` and `prettier --check` on staged `.ts`/`.tsx` files before commit" to harmonize with the pre-commit approach
- [ ] T056 [US4] Add a Sync Impact Report HTML comment block at the top of `.specify/memory/constitution.md` documenting the version bump (MINOR), rationale, modified sections, and template impacts; increment version from 1.7.0 to 1.8.0

### 6c. Update Templates

- [ ] T057 [P] [US4] Add a gate row "Whole-project lint/type/coverage — all subprojects pass ruff, mypy, pytest --cov-fail-under=85, and npm run test:coverage" to the Constitution Check table in `.specify/templates/plan-template.md`
- [ ] T058 [P] [US4] Add a mandatory final validation task to `.specify/templates/tasks-template.md` in the Notes section: "Before feature completion, run full-project validation: `uv run ruff check/format --check` + `mypy` across all src dirs, `pytest --cov-fail-under=85` for all 5 packages, `npm run test:coverage` in frontend, `pre-commit run --all-files`"

### 6d. Validation

- [ ] T059 [US4] Review `CLAUDE.md`, `.specify/memory/constitution.md`, `.specify/templates/plan-template.md`, and `.specify/templates/tasks-template.md` to confirm whole-project quality gate language is present and unambiguous

**Checkpoint**: Governance documents updated. US4 is complete.

---

## Phase 7: Feature Completion Documentation _(mandatory — Constitution Principle X)_

**Purpose**: Update all required documentation before the feature branch is merged.

> **These tasks MUST be completed before the feature is marked done.**

- [ ] T060 [P] Update `CLAUDE.md` at repository root: update all `--package sms-*` references to use new names; update project description to "Researcher"; add quality gate section per T052; update "Active Technologies" and "Recent Changes" sections
- [ ] T061 [P] Update `README.md` at repository root: change title from "SMS Researcher" to "Researcher"; update sub-project table; update all `--package` command examples
- [ ] T062 [P] Update `CHANGELOG.md` at repository root with a new entry for `011-improve-testing-and-fix-ci`: describe CI fixes, pre-commit consolidation, project rename, and governance updates
- [ ] T063 [P] Update `backend/README.md` title from "sms-backend" to "backend"; update all `--package` references
- [ ] T064 [P] Update `backend/CHANGELOG.md` title from "Changelog — sms-backend" to "Changelog — backend"; add entry for package rename
- [ ] T065 [P] Update `agent-eval/README.md` title from "sms-agent-eval" to "agent-eval"; update all `--package` references
- [ ] T066 [P] Update `agent-eval/CHANGELOG.md` title from "Changelog — sms-agent-eval" to "Changelog — agent-eval"; add entry for package rename
- [ ] T067 [P] Update `researcher-mcp/README.md` title from "sms-researcher-mcp" to "researcher-mcp"; update all `--package` references
- [ ] T068 [P] Update `researcher-mcp/CHANGELOG.md` title from "Changelog — sms-researcher-mcp" to "Changelog — researcher-mcp"; add entry for package rename
- [ ] T069 [P] Update `frontend/README.md` title from "sms-frontend" to "frontend"; add entry noting husky removal
- [ ] T070 [P] Update `frontend/CHANGELOG.md` title from "Changelog — sms-frontend" to "Changelog — frontend"; add entry for package rename and husky removal

---

## Phase 8: Final Validation

**Purpose**: End-to-end verification that all success criteria are met.

- [ ] T071 Run `uv run ruff check backend/src agents/src db/src agent-eval/src researcher-mcp/src` and `uv run ruff format --check backend/src agents/src db/src agent-eval/src researcher-mcp/src` — verify zero violations
- [ ] T072 Run `uv run mypy backend/src agents/src db/src agent-eval/src researcher-mcp/src` — verify zero errors
- [ ] T073 Run all 5 Python test suites with coverage: `uv run --package backend pytest backend/tests/ --cov=src/backend --cov-fail-under=85`, same for agents, db, agent-eval, researcher-mcp — all must pass with >= 85% coverage
- [ ] T074 Run `cd frontend && npm run lint && npm run format:check && npm run test:coverage` — verify all pass with >= 85% on all four metrics
- [ ] T075 Run `uv run pre-commit run --all-files` — verify ALL hooks pass
- [ ] T076 Run `docker build -f backend/Dockerfile -t backend:ci . && docker build -f researcher-mcp/Dockerfile -t researcher-mcp:ci . && docker build -f frontend/Dockerfile -t frontend:ci .` — all three builds succeed
- [ ] T077 Run `grep -r "sms-backend\|sms-agent-eval\|sms-researcher-mcp\|sms-frontend" --include="*.toml" --include="*.yml" --include="*.yaml" --include="*.json" --include="*.md" --include="Dockerfile" --exclude-dir=.venv --exclude-dir=specs --exclude-dir=node_modules .` — verify zero matches
- [ ] T078 Push branch and verify all GitHub Actions CI jobs pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: No dependencies — can start immediately (removes husky blocker)
- **US1 (Phase 3)**: Depends on Phase 2 (husky removal unblocks Docker build)
- **US2 (Phase 4)**: Depends on Phase 3 (pre-commit hooks rely on all lint/tests passing first)
- **US3 (Phase 5)**: Depends on Phase 3 (rename should happen after CI is green to verify nothing breaks)
- **US4 (Phase 6)**: Depends on Phase 5 (governance docs reference new package names)
- **Docs (Phase 7)**: Depends on Phase 5 and Phase 6 (docs reflect final names and governance)
- **Final Validation (Phase 8)**: Depends on all prior phases

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational (Phase 2). No dependencies on other stories.
- **US2 (P2)**: Depends on US1 — pre-commit hooks need all lint/tests to already pass.
- **US3 (P3)**: Depends on US1 — rename should happen on a green CI baseline.
- **US4 (P4)**: Depends on US3 — governance docs reference renamed packages.

### Within Each User Story

- Auto-format tasks (T004/T005, T008/T009) can run in parallel
- Coverage gap fixes (T012–T016) can run in parallel across packages
- CI config changes should be verified together (T020)
- Rename tasks (T031–T046) can run in parallel per file
- Governance updates (T057/T058) can run in parallel

### Parallel Opportunities

- T004 + T005 (Python ruff format + check fix) can run in parallel
- T008 + T009 (Frontend prettier + eslint fix) can run in parallel
- T012–T016 (Python coverage fixes per package) can all run in parallel
- T021–T028 (Pre-commit hook additions) can all run in parallel
- T031–T033 (Python package renames) can all run in parallel
- T042–T046 (Docker/cosmic-ray renames) can all run in parallel
- T060–T070 (Documentation updates) can all run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch Python formatting fixes together:
Task: "T004 Run ruff format across all Python source directories"
Task: "T005 Run ruff check --fix across all Python source directories"

# Launch frontend formatting fixes together:
Task: "T008 Run prettier --write in frontend"
Task: "T009 Run eslint --fix in frontend"

# Launch all Python coverage gap fixes together:
Task: "T012 Fix backend coverage gaps"
Task: "T013 Fix agents coverage gaps"
Task: "T014 Fix db coverage gaps"
Task: "T015 Fix agent-eval coverage gaps"
Task: "T016 Fix researcher-mcp coverage gaps"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (remove husky)
2. Complete Phase 3: US1 — Fix all CI pipelines
3. **STOP and VALIDATE**: Push branch, verify all 9 CI jobs pass
4. This alone delivers the primary value — green CI

### Incremental Delivery

1. Phase 2 (Foundational) → Husky removed, Docker unblocked
2. Phase 3 (US1) → All CI green (MVP!)
3. Phase 4 (US2) → Pre-commit hooks enforced locally
4. Phase 5 (US3) → Project renamed to Researcher
5. Phase 6 (US4) → Governance hardened for future features
6. Phase 7–8 → Docs + final validation
