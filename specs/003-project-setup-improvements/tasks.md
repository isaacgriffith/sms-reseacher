# Tasks: Project Setup & Quality Improvements

**Input**: Design documents from `/specs/003-project-setup-improvements/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and
testing of each story. Implementation order diverges from spec priority order because US1
verification (FR-005: commands must actually work) can only be validated after US2/US3 tools
are fully configured.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking dependency)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Exact file paths included in all descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Baseline tooling changes and coverage audit that all phases depend on.

- [x] T001 Audit current test coverage for all 5 Python packages: run `uv run pytest --cov=src/<pkg> <pkg>/tests/` per package and record baseline line-coverage percentages to guide gap-closing in Phase 3
- [x] T002 [P] Remove `mutmut` from root `pyproject.toml` `dev-dependencies`; add `cosmic-ray` as dev-dependency in root `pyproject.toml`
- [x] T003 [P] Create root `conftest.py` with `pytest_collection_finish` hook that fails the session if any collected test has `@pytest.mark.skip` or `@pytest.mark.xfail` without a non-empty `reason=` argument, per research.md §4
- [x] T004 [P] Add `@vitest/coverage-v8` to `frontend/package.json` `devDependencies`; run `npm install` to update `package-lock.json`
- [x] T005 [P] Update `frontend/vite.config.ts` `test.coverage` block: set `provider: 'v8'`, add `'json-summary'` to reporters list, add `thresholds: { lines: 85, branches: 85 }`, set `include: ['src/**/*.{ts,tsx}']`, per research.md §3

---

## Phase 2: Foundational (CI Pipeline — Blocking Prerequisites)

**Purpose**: GitHub Actions updates that activate coverage PR comments, move mutation jobs to
`workflow_dispatch`, and add the Playwright e2e job. All story CI validation depends on this.

**⚠️ CRITICAL**: No story can be validated in CI until this phase is complete.

- [x] T006a Remove all mutation testing job blocks (cosmic-ray and Stryker jobs) from `.github/workflows/ci.yml`; commit with `ci: remove per-PR mutation jobs`
- [x] T006b [P] Add `--cov-report=xml:<pkg>/coverage.xml` to each Python package's pytest step in `.github/workflows/ci.yml`; add `MishaKav/pytest-coverage-comment@main` step (guarded by `github.event_name == 'pull_request'`) per Python package, per research.md §2
- [x] T006c [P] Add `davelosert/vitest-coverage-report-action@v2` step to the `frontend-test` job in `.github/workflows/ci.yml`, per research.md §3
- [x] T006d Add `e2e-tests` job to `.github/workflows/ci.yml`: PostgreSQL 16 service container, `uv sync`, `npm ci`, `npx playwright install --with-deps chromium`, `uv run alembic upgrade head`, `npx playwright test`; upload `playwright-report/` artifact on failure; per research.md §5
- [x] T006e Verify the full updated `.github/workflows/ci.yml` passes `actionlint` (if available) or equivalent dry-run lint; confirm no job references a removed mutation job
- [x] T007 [P] Create `.github/workflows/mutation-python.yml` with `on: [workflow_dispatch, workflow_call]` triggers (inputs: `packages`, default `"all"`), matrix strategy over all 5 packages running `uv run cosmic-ray run <pkg>/cosmic-ray.toml`, and a kill-rate check step that fails if score < 85%, per research.md §6; after creating the file, confirm with `.specify/scripts/bash/` or the end-of-feature hook that this workflow is invoked via `workflow_call` at feature completion — document the invocation mechanism in a comment at the top of the file (satisfies FR-013 speckit trigger)
- [x] T008 [P] Create `.github/workflows/mutation-frontend.yml` with `on: [workflow_dispatch, workflow_call]` triggers, Node 20 setup, `npm ci`, `npx stryker run` in `frontend/`, and fail-on-kill-rate-below-85%, per research.md §6; same speckit trigger verification as T007 — document the invocation mechanism at the top of the file

> **Note**: T006a must complete before T006b–T006d to avoid merge conflicts on `ci.yml`.
> T006b and T006c can run in parallel (different job blocks in the same file — edit carefully).
> T006d depends on T006a.

**Checkpoint**: CI pipeline updated — coverage comments active on PRs; mutation workflows available for manual dispatch

---

## Phase 3: User Story 2 — Confident Code Change Verification (Priority: P2)

**Goal**: All existing tests pass; line coverage ≥ 85% for every Python package and the frontend; no unexplained test failures or skips.

**Independent Test**: Run `uv run pytest --cov=src/<pkg> --cov-fail-under=85 <pkg>/tests/` for each of the 5 Python packages and `cd frontend && npm run test:coverage` — all must pass.

### Implementation for User Story 2

- [x] T009 [P] [US2] Replace `[tool.mutmut]` section with `[tool.cosmic-ray]` in `backend/pyproject.toml`; remove `mutmut` from `dev-dependencies`; add `cosmic-ray` to `dev-dependencies`
- [x] T010 [P] [US2] Replace `[tool.mutmut]` section with `[tool.cosmic-ray]` in `agents/pyproject.toml`; update `dev-dependencies` accordingly
- [x] T011 [P] [US2] Replace `[tool.mutmut]` section with `[tool.cosmic-ray]` in `db/pyproject.toml`; update `dev-dependencies` accordingly
- [x] T012 [P] [US2] Replace `[tool.mutmut]` section with `[tool.cosmic-ray]` in `agent-eval/pyproject.toml`; update `dev-dependencies` accordingly
- [x] T013 [P] [US2] Replace `[tool.mutmut]` section with `[tool.cosmic-ray]` in `researcher-mcp/pyproject.toml`; update `dev-dependencies` accordingly
- [x] T014 [US2] Add unit and/or integration tests to `backend/tests/` to bring `backend/src/` line coverage to ≥ 85% (use T001 audit baseline to identify gaps); annotate any legitimately untestable lines (e.g. `if __name__ == "__main__"` guards, abstract stubs) with `# pragma: no cover` per constitution VI; run `uv run --package sms-backend pytest backend/tests/ --cov=src/backend --cov-fail-under=85` to confirm
- [x] T015 [US2] Before writing any new tests, check whether `agents/tests/metamorphic/` exists and contains metamorphic tests for each agent's core transformation behavior (required by Constitution VI). If absent or incomplete: create them first in `agents/tests/metamorphic/` defining at least one metamorphic relation per agent. Then add any remaining unit/integration tests to `agents/tests/` to bring `agents/src/` line coverage to ≥ 85%; annotate legitimately untestable lines with `# pragma: no cover`; confirm with `uv run --package sms-agents pytest agents/tests/ --cov=src/agents --cov-fail-under=85`
- [x] T016 [US2] Add unit and/or integration tests to `db/tests/` to bring `db/src/` line coverage to ≥ 85%; annotate legitimately untestable lines with `# pragma: no cover` per constitution VI; confirm with `uv run --package sms-db pytest db/tests/ --cov=src/db --cov-fail-under=85`
- [x] T017 [US2] Add unit and/or integration tests to `agent-eval/tests/` to bring `agent-eval/src/` line coverage to ≥ 85%; annotate legitimately untestable lines with `# pragma: no cover` per constitution VI; confirm with `uv run --package sms-agent-eval pytest agent-eval/tests/ --cov=src/agent_eval --cov-fail-under=85`
- [x] T018 [US2] Add unit and/or integration tests to `researcher-mcp/tests/` to bring `researcher-mcp/src/` line coverage to ≥ 85%; annotate legitimately untestable lines with `# pragma: no cover` per constitution VI; confirm with `uv run --package sms-researcher-mcp pytest researcher-mcp/tests/ --cov=src/researcher_mcp --cov-fail-under=85`
- [x] T019 [US2] Add frontend component and unit tests to `frontend/src/` to bring TypeScript line coverage to ≥ 85%; annotate legitimately untestable lines with `/* istanbul ignore */` per constitution VI; run `cd frontend && npm run test:coverage` to confirm thresholds pass

**Checkpoint**: All 5 Python packages and frontend pass their 85% coverage gates; zero unexplained failures or skips

---

## Phase 4: User Story 3 — Mutation Testing Confidence (Priority: P3)

**Goal**: `cosmic-ray` configured per Python package; Playwright e2e tests cover all four primary user journeys; mutation kill rate ≥ 85% for all Python packages (cosmic-ray) and frontend (Stryker).

**Independent Test**: Run `uv run cosmic-ray run backend/cosmic-ray.toml` then `uv run cosmic-ray results backend/cosmic-ray.toml` — kill rate ≥ 85%. Run `cd frontend && npx playwright test` against the running stack — all four journey specs pass.

### Implementation for User Story 3

- [x] T020 [P] [US3] Create `backend/cosmic-ray.toml` with `module-path = "src/backend"`, `timeout = 30.0`, and `test-command = "uv run --package sms-backend pytest backend/tests/unit -x -q"` per research.md §1
- [x] T021 [P] [US3] Create `agents/cosmic-ray.toml` with `module-path = "src/agents"`, `timeout = 30.0`, and `test-command = "uv run --package sms-agents pytest agents/tests/unit -x -q"`
- [x] T022 [P] [US3] Create `db/cosmic-ray.toml` with `module-path = "src/db"`, `timeout = 30.0`, and `test-command = "uv run --package sms-db pytest db/tests/unit -x -q"`
- [x] T023 [P] [US3] Create `agent-eval/cosmic-ray.toml` with `module-path = "src/agent_eval"`, `timeout = 30.0`, and `test-command = "uv run --package sms-agent-eval pytest agent-eval/tests/unit -x -q"`
- [x] T024 [P] [US3] Create `researcher-mcp/cosmic-ray.toml` with `module-path = "src/researcher_mcp"`, `timeout = 30.0`, and `test-command = "uv run --package sms-researcher-mcp pytest researcher-mcp/tests/unit -x -q"`
- [x] T025 [US3] Add `@playwright/test` to `frontend/package.json` `devDependencies`; run `npm install`; run `npx playwright install --with-deps chromium` to install Chromium browser binary
- [x] T026 [US3] Create `frontend/playwright.config.ts` with `testDir: './e2e'`, `fullyParallel: true`, `forbidOnly: !!process.env.CI`, `retries: process.env.CI ? 2 : 0`, `reporter: process.env.CI ? 'github' : 'html'`, `use: { baseURL: 'http://localhost:5173', trace: 'on-first-retry', screenshot: 'only-on-failure' }`, and dual `webServer` entries (Vite dev server + FastAPI backend) per research.md §5
- [x] T027 [US3] Create `frontend/e2e/create-study.spec.ts` — Playwright test covering the Create Study primary user journey end-to-end (frontend form → backend POST → db write → confirmation UI); use `LLM_PROVIDER=mock` fixture
- [x] T028 [P] [US3] Create `frontend/e2e/search-papers.spec.ts` — Playwright test covering the Search for Papers journey (frontend search → backend → researcher-mcp → mocked Semantic Scholar response → results displayed)
- [x] T029 [P] [US3] Create `frontend/e2e/screen-paper.spec.ts` — Playwright test covering the Screen a Paper journey (backend → agents → LLM stub via `LLM_PROVIDER=mock` → screening result stored and displayed)
- [x] T030 [P] [US3] Create `frontend/e2e/results-dashboard.spec.ts` — Playwright test covering the View Results Dashboard journey (frontend → backend API → populated results table rendered)

> **agent-eval e2e scope note (FR-019)**: `agent-eval` is an offline evaluation framework with
> no frontend-facing user journey. Its primary journeys are exercised indirectly through the
> "Screen a paper" spec (T029), which drives the `agents/` package. No standalone `agent-eval`
> Playwright spec is required; this exclusion satisfies the FR-019 edge-case clause ("What if
> a service has no frontend-visible primary journey?").

- [X] T031 [US3] Run `uv run cosmic-ray run <pkg>/cosmic-ray.toml` for each of the 5 packages (sequentially — compute-intensive); review kill rate via `uv run cosmic-ray results`; add tests to kill surviving mutants; for any mutant representing genuinely equivalent code (same observable behaviour), document it in `<pkg>/cosmic-ray-survivors.md` with the mutant ID, affected line, and justification — this file is committed alongside the package and referenced in the PR description per constitution VI; continue until kill rate ≥ 85% or all survivors are individually justified (depends on T020–T024, T014–T018)
- [X] T032 [US3] Run `cd frontend && npx stryker run`; review Stryker HTML report; add tests or document justified survivors until kill rate ≥ 85% (depends on T019)

**Checkpoint**: All cosmic-ray configs functional; full Playwright e2e suite passing; mutation kill rates ≥ 85% for all 6 subprojects

---

## Phase 5: User Story 1 — First-Time Contributor Onboarding (Priority: P1)

**Goal**: `CLAUDE.md` contains accurate, runnable commands for every quality gate; all commands verified working on the current checkout without modification (FR-005).

**Independent Test**: Follow only `CLAUDE.md` from a clean environment — complete environment setup, run tests, coverage, lint, mutation, and e2e — every command succeeds with no errors.

> **Note**: T033–T038 (CLAUDE.md editing) can run in parallel; T039 (end-to-end verification)
> is the capstone gate and must run last, after all prior phases are complete.

### Implementation for User Story 1

- [x] T033 [US1] Update `CLAUDE.md` environment setup section: Python 3.14 + `uv python install 3.14` + `uv sync --all-packages`; Node 20 LTS + `cd frontend && npm install`; Playwright browser install (`cd frontend && npx playwright install --with-deps chromium`); optional pre-commit hook install
- [x] T034 [P] [US1] Update `CLAUDE.md` test commands section: per-package `uv run --package <pkg> pytest <pkg>/tests/` for all 5 Python packages; combined `uv run pytest backend/tests/ agents/tests/ db/tests/ agent-eval/tests/ researcher-mcp/tests/`; frontend `cd frontend && npm test` and `npm run test:watch`
- [x] T035 [P] [US1] Update `CLAUDE.md` coverage commands section: per-package `uv run --package <pkg> pytest <pkg>/tests/ --cov=src/<module> --cov-report=term-missing --cov-report=xml:<pkg>/coverage.xml` for all 5 packages; `cd frontend && npm run test:coverage`
- [x] T036 [P] [US1] Update `CLAUDE.md` lint and type-check section: `uv run ruff check <all src dirs>`; `uv run ruff format --check <all src dirs>`; `uv run mypy <all src dirs>`; `cd frontend && npm run lint`; `cd frontend && npm run format:check`
- [x] T037 [P] [US1] Update `CLAUDE.md` mutation testing section: `uv run cosmic-ray run <pkg>/cosmic-ray.toml` for each package; `uv run cosmic-ray results <pkg>/cosmic-ray.toml`; `uv run cosmic-ray html-report <pkg>/cosmic-ray.toml > /tmp/<pkg>-mutation-report.html`; `cd frontend && npx stryker run`
- [x] T038 [P] [US1] Update `CLAUDE.md` end-to-end section: Docker Compose path (`cp .env.example .env && docker compose up -d`; `cd frontend && PLAYWRIGHT_BASE_URL=http://localhost:5173 npx playwright test`; `npx playwright show-report`); and manual stack startup alternative per quickstart.md
- [x] T039 [US1] Execute every command block in `CLAUDE.md` sequentially on the current checkout; fix any command that fails or produces incorrect output; confirm SC-001 satisfied (depends on T033–T038 and all phases 1–4 complete)
- [x] T039a [US1] Verify `.specify/memory/constitution.md` Principles VI and VII still accurately reflect the finalized commands confirmed by T039 (cosmic-ray invocation, Stryker invocation, Playwright e2e, coverage thresholds, workflow_dispatch cadence); update wording if any command detail changed during implementation (satisfies FR-006)

**Checkpoint**: A contributor can follow `CLAUDE.md` from start to finish without errors; SC-001 and FR-006 satisfied

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final end-to-end validation across all stories before documentation and merge.

- [x] T040 Run the full combined test suite (`uv run pytest backend/tests/ agents/tests/ db/tests/ agent-eval/tests/ researcher-mcp/tests/ && cd frontend && npm test`) and confirm zero failures and zero unexplained skips
- [x] T041 Verify root `conftest.py` skip/xfail enforcement fires correctly: temporarily add a bare `@pytest.mark.skip` (no `reason=`) to any test, confirm pytest exits non-zero with the expected message, then remove the temporary marker
- [x] T042 Run the full Playwright e2e suite (`cd frontend && npx playwright test`) against the Docker Compose stack; confirm all four journey specs pass; view HTML report for any flaky results

---

## Phase 7: Feature Completion Documentation *(mandatory — Constitution Principle X)*

**Purpose**: Update all required documentation before the feature branch is merged.

> **These tasks MUST be completed before the feature is marked done. Omitting them is a
> blocking violation of Constitution Principle X (Feature Completion Documentation).**

- [x] TDOC1 [P] Final completeness review of `CLAUDE.md`: confirm every section added by T033–T038 is present, no command was accidentally reverted during T039 fixes, and the Quality Toolchain section accurately lists all tools introduced by this feature (cosmic-ray, `@vitest/coverage-v8`, Playwright, workflow_dispatch mutation CI)
- [x] TDOC2 [P] Update `README.md` at repository root to accurately reflect the full quality toolchain: cosmic-ray (replaces mutmut), Playwright e2e, coverage gates, workflow_dispatch mutation CI, and Principle X documentation requirement
- [x] TDOC3 [P] Update `CHANGELOG.md` at repository root Unreleased section with all changes introduced by this feature (follow Keep a Changelog format: Added / Changed / Removed)
- [x] TDOC4 [P] Update `README.md` in `backend/`, `agents/`, `db/`, `agent-eval/`, and `researcher-mcp/` to reflect cosmic-ray config, updated test/coverage commands, and any new tests added in Phase 3
- [x] TDOC5 [P] Update `CHANGELOG.md` in `backend/`, `agents/`, `db/`, `agent-eval/`, `researcher-mcp/`, and `frontend/` Unreleased sections with per-subproject detail matching the root changelog level of detail

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately; all tasks parallelizable
- **Foundational (Phase 2)**: Depends on Phase 1 — T006a first (removes mutation jobs), then T006b/T006c/T006d in parallel; T007/T008 can start after T002; BLOCKS CI validation for all stories
- **US2 (Phase 3)**: T009–T013 depend on Phase 1 (T002 first for consistency); T014–T019 depend on T001 (audit baseline)
- **US3 (Phase 4)**: T020–T024 can start after Phase 1; T025–T030 (Playwright) are independent; T031 depends on T020–T024 AND T014–T018 (coverage must be ≥ 85% for meaningful mutation scores); T032 depends on T019
- **US1 (Phase 5)**: T033–T038 can run in parallel with Phase 3 and 4; T039 depends on ALL prior phases complete; T039a depends on T039
- **Polish (Phase 6)**: Depends on Phase 5
- **Documentation (Phase 7)**: Depends on Phase 6

### User Story Dependencies

- **US2 (P2)**: Unblocked after Phase 1 — can start immediately
- **US3 (P3)**: cosmic-ray TOMLs (T020–T024) unblocked after Phase 1; Playwright (T025–T030) independent; T031/T032 blocked on US2 coverage work
- **US1 (P1)**: CLAUDE.md editing (T033–T038) can proceed in parallel; T039 verification is the final gate
- **US4 (P4) / TDOC tasks**: Fully unblocked only after Phase 6

### Parallel Opportunities

```bash
# Phase 1 — all can start together:
T002: root pyproject.toml mutmut→cosmic-ray
T003: root conftest.py skip/xfail enforcement
T004: frontend/package.json @vitest/coverage-v8
T005: frontend/vite.config.ts coverage config

# Phase 2 — T006a first, then in parallel:
T006b: ci.yml Python coverage steps
T006c: ci.yml frontend coverage step
T006d: ci.yml e2e job
# Also in parallel after T002:
T007: mutation-python.yml
T008: mutation-frontend.yml

# Phase 3 — pyproject.toml replacements together:
T009: backend/pyproject.toml
T010: agents/pyproject.toml
T011: db/pyproject.toml
T012: agent-eval/pyproject.toml
T013: researcher-mcp/pyproject.toml
# Then coverage gap-filling in parallel:
T014: backend tests   T015: agents tests
T016: db tests        T017: agent-eval tests
T018: researcher-mcp  T019: frontend tests

# Phase 4 — cosmic-ray TOMLs and Playwright specs together:
T020: backend/cosmic-ray.toml    T021: agents/cosmic-ray.toml
T022: db/cosmic-ray.toml         T023: agent-eval/cosmic-ray.toml
T024: researcher-mcp/cosmic-ray  T028: search-papers.spec.ts
T029: screen-paper.spec.ts       T030: results-dashboard.spec.ts

# Phase 5 — CLAUDE.md sections together:
T034: test commands   T035: coverage commands
T036: lint commands   T037: mutation commands
T038: e2e commands
```

---

## Implementation Strategy

### MVP First (Coverage Foundation)

1. Complete Phase 1: Setup
2. Complete Phase 2: CI pipeline (T006a first, then T006b–T006d — unblocks coverage comment validation)
3. Complete Phase 3: US2 — all tests green, all coverage gates pass
4. **STOP and VALIDATE**: `uv run pytest --cov-fail-under=85` per package; `npm run test:coverage` — must all pass

### Incremental Delivery

1. Phase 1 + 2 → CI infrastructure ready
2. Phase 3 → Coverage green for all 6 subprojects
3. Phase 4 → Mutation configured + Playwright e2e passing
4. Phase 5 → CLAUDE.md verified end-to-end (SC-001 satisfied)
5. Phase 6 + 7 → Polish + docs → ready to merge

---

## Notes

- **[P] tasks** = different files, no shared dependencies — safe to run in parallel
- **[Story] label** maps each task to its user story for traceability
- **T001** (coverage audit) must complete before T014–T019 to know the gap size
- **T031** (cosmic-ray run) must start after T014–T018 and T020–T024; mutation quality is only meaningful when coverage ≥ 85%
- **T039** (CLAUDE.md verification) is the capstone; all prior work must be complete
- **T039a** (constitution.md verification) follows T039 and satisfies FR-006
- Commit after each logical group; conventional prefix: `ci:`, `test:`, `chore:`, `docs:`
- `conftest.py` hook (T003): keep ≤ 15 lines per research.md §4; Google-style docstring required
- Playwright helpers: JSDoc required on all exported functions
- New Python test helpers: no mutable defaults, no bare `except`; use `pathlib.Path` for file refs
- TypeScript e2e specs: no `any`, no non-null `!`; use typed `Page` / `Locator` / `expect` APIs
- Constitution compliance: all tasks respect Principles I–X (SOLID, DRY, YAGNI, Code Clarity,
  Refactoring, GRASP, Testing, Toolchain, Observability, Language, Feature Completion Docs)
