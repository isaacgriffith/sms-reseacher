# Tasks: Wire Up Unreachable Workflows

**Feature**: `012-wire-up-unreachable-workflows`
**Input**: Design documents from `/specs/012-wire-up-unreachable-workflows/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Format: `[ID] [P?] [Story] Description`

- **[P]** — parallelisable: different file, no dependency on an incomplete task
- **[US1]…[US4]** — the user story the task serves
- Every task names the exact file it touches

## Path Conventions

`uv` workspace plus a Vite/React SPA. Backend at `backend/src/backend/`, models and migrations at
`db/src/db/`, frontend at `frontend/src/`, e2e at `frontend/e2e/`.

**Tests are required for this feature** — Constitution Principle VI (≥85% coverage, mutation
≥85%) and FR-021 (every capability driven through the UI against a live backend). Every phase
below is test-first: the test task precedes its implementation task and must fail before the
implementation is written.

---

## Refactoring Tasks (Pre-feature, required by Constitution Principle IV)

> These come **first** and land as separate `refactor:` / `fix:` commits carrying no feature
> change. Each was found during the pre-implementation review and is recorded in plan.md
> Complexity Tracking as C1–C3. Skipping them means building on top of the exact defects that
> produced this feature.

- [X] TREF1 [P] Write characterisation tests for `StudyPage`'s current per-study-type rendering in `frontend/src/pages/__tests__/StudyPage.dispatch.test.tsx` — assert SLR, Rapid, and SMS each render their existing phase bodies, so the C1 refactor is provably behaviour-preserving
- [X] TREF2 Replace the eleven `isSLR` / `isRapid` boolean dispatch points in `frontend/src/pages/StudyPage.tsx` with a study-type → renderer map in `frontend/src/components/studies/studyTypeDispatch.tsx` (C1; mirrors the backend's `_PHASE_GATE_DISPATCH`)
- [X] TREF3 [P] Write unit tests for `_load_criteria`, `_process_single_candidate`, and `_record_paper_decision` in `backend/tests/unit/test_screening_pipeline.py` before extracting them
- [X] TREF4 Extract the screening helpers from `backend/src/backend/jobs/search_job.py` (941 lines) into `backend/src/backend/jobs/screening_pipeline.py`, leaving `search_job.py` importing them (C2 — brings the file under the 800-line maximum and gives the re-screen job a shared home rather than a copy)
- [X] TREF5 [P] Write a failing test in `backend/tests/unit/test_screening_pipeline.py` asserting that a provider error during screening raises rather than returning `("rejected", [])` (C3 — must be RED before TREF6)
- [X] TREF6 Change `_run_screening_pass` in `backend/src/backend/jobs/screening_pipeline.py` to propagate provider errors instead of swallowing them into a rejection (C3 — FR-024 is unsatisfiable while a fault is persisted as a legitimate reject)
- [X] TREF7 Give `CandidatePaper` a `paper` relationship and delegate `title` / `abstract` to it in `db/src/db/models/candidate.py`; construct candidates with `paper=` rather than `paper_id=` in `screening_pipeline.py` (**C6**, found while doing TREF6 — both callers pass a `CandidatePaper` to `_run_screening_pass`, which reads `.abstract` off it. `CandidatePaper` carried neither field, so every call raised `AttributeError` into the bare `except` and returned a rejection: the screener was never invoked for any paper in any search. TREF6 is not landable without this, since propagating the error would turn a silent wrong answer into a crash on every search)

- [X] TREF8 Fail the run rather than stranding it: `run_full_search` now wraps its sweep and calls `_fail_search_run`, which rolls back the partial sweep and marks the `SearchExecution` and `BackgroundJob` failed (**C7** — with TREF6 propagating, a provider outage escaped `run_full_search`, which had no handler, leaving the job row at `running` for ever; the UI cannot tell a crashed search from a slow one). The sweep moves to `_execute_search_sweep`, and `run_expert_seed_suggestion` moves to `backend/src/backend/jobs/seed_suggestion_job.py` — it is a phase-1 seeding job, not a search, and keeping it here put `search_job.py` back over the 800-line maximum

- [X] TREF9 Give `run_snowball` the same failure handling, and record the policy that T044 must **not** copy. Snowball moves to `backend/src/backend/jobs/snowball_job.py` (it walks citation edges rather than querying an index, and keeping it in `search_job.py` breached the 800-line maximum again); it now marks its `SearchExecution` running → completed → failed, where it previously left it `pending` whatever happened, and shares `_fail_search_run`. The opposite policy required of the re-screen job is recorded as **R9** in `research.md`, on T044 itself, in `_fail_search_run`'s docstring, and in `MEMORY.md`

**Checkpoint**: `uv run pytest backend/tests/` and `cd frontend && npm test` both green. Behaviour
does change for a user, and deliberately: the AI screener now actually runs during a search
(TREF7), and a failed search reports itself as failed (TREF8). Covered end-to-end against a live
database by `backend/tests/integration/test_search_pipeline_screening.py`.

---

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Record the baseline in `specs/012-wire-up-unreachable-workflows/quickstart.md` by running `python3 scripts/audit_unreachable_frontend.py` (expect 23 unreachable), `grep -rn "future sprint" frontend/src` (expect 2), and `grep -c "test.fixme" frontend/e2e/screen-paper.spec.ts` (expect 3) — if any already passes, the plan needs revisiting before work starts
- [ ] T002 [P] Verify the baseline is clean by running every hook in `.pre-commit-config.yaml` via `uv run pre-commit run --all-files`, so later gate failures are attributable to this feature rather than pre-existing

---

## Phase 2: Foundational (Blocking Prerequisites)

> Test fixtures every story's e2e depends on. Without these the four journeys cannot be driven
> against a live backend, which FR-021 requires.

- [ ] T003 Extend `scripts/seed_e2e_user.py` with a Tertiary study owned by the seeded research group, so US2 has something to open
- [ ] T004 [P] Extend `scripts/seed_e2e_user.py` with a study holding accepted papers and at least one extraction record, so US3 has data to display
- [ ] T005 [P] Extend `scripts/seed_e2e_user.py` with a candidate paper carrying two disagreeing reviewer decisions, so US1 can exercise the conflict path
- [ ] T006 [P] Extend `scripts/seed_e2e_user.py` with a second research-group study, so Tertiary seed import has a source to offer

**Checkpoint**: `uv run python scripts/seed_e2e_user.py` is idempotent and creates every fixture the four journeys need.

---

## Phase 3: User Story 1 — Record a screening decision (Priority: P1) 🎯 MVP

**Goal**: A reviewer can select a paper, see prior decisions and disagreement, and record accept / reject / duplicate with reasons and an annotation.

**Independent test**: Open a study with candidate papers, select one, submit an accept decision with a reason, and confirm the queue reflects the new status — with nothing else in this feature present.

### Tests for User Story 1 ⚠️ write first, must fail

- [ ] T007 [P] [US1] Integration test in `backend/tests/integration/test_papers_decisions.py`: a submission whose `observed_status` differs from the stored status returns 409 carrying both statuses (FR-025, FR-027)
- [ ] T008 [P] [US1] Integration test in `backend/tests/integration/test_papers_decisions.py`: a second decision by the same reviewer without `overrides_decision_id` returns 409 carrying their earlier decision (FR-022)
- [ ] T009 [P] [US1] Integration test in `backend/tests/integration/test_papers_decisions.py`: resubmitting with `overrides_decision_id` succeeds, sets `is_override`, retains the original, and does **not** raise the paper's conflict flag (FR-022)
- [ ] T010 [US1] Migrate the ~10 existing `POST …/decisions` calls in `backend/tests/integration/test_papers_decisions.py` to supply `observed_status` (C5 — required field, so existing callers stop working; migrating them is part of this task, not follow-up)
- [ ] T011 [P] [US1] Component test in `frontend/src/components/studies/__tests__/ScreeningView.test.tsx`: selecting a queue row opens the reviewer panel for that candidate
- [ ] T012 [P] [US1] Component test in `frontend/src/components/studies/__tests__/ScreeningView.test.tsx`: reasons and annotation already entered survive a re-confirmation prompt (FR-025)

### Implementation for User Story 1

- [ ] T013 [US1] Add required `observed_status` and the stale-state 409 to `DecisionRequest` and `submit_decision` in `backend/src/backend/api/v1/papers.py` (FR-025, FR-027)
- [ ] T014 [US1] Add the unacknowledged-prior-decision 409 to `submit_decision` in `backend/src/backend/api/v1/papers.py`, returning the reviewer's earlier decision in the payload (FR-022)
- [ ] T015 [US1] Create `frontend/src/components/studies/ScreeningView.tsx` composing `PaperQueue`, selection state, `ReviewerPanel`, `PaperCard`, and `MetricsDashboard` (≤100 JSX lines — decompose if it grows)
- [ ] T016 [US1] Mount `ScreeningView` at phase 3 for the SMS branch and inside `SLRScreeningView` in `frontend/src/pages/StudyPage.tsx`, so both paths gain decisions from one change (FR-006)
- [ ] T017 [US1] Send `observed_status` and `overrides_decision_id` from the reviewer panel in `frontend/src/components/phase2/ReviewerPanel.tsx`, preserving entered input across a re-confirmation
- [ ] T018 [US1] Remove `test.fixme` from the three cases in `frontend/e2e/screen-paper.spec.ts` and make them assert real behaviour (no `isVisible()` guards, no conditional skips — Principle VI)
- [ ] T019 [US1] Extend `frontend/e2e/screen-paper.spec.ts` to record a decision end-to-end on an SMS study and on an SLR study against a live backend (FR-021)

**Checkpoint**: A reviewer can screen papers on SMS and SLR studies. Agreement measurement becomes exercisable. Tertiary is covered in Phase 4, which is where that study type becomes reachable.

---

## Phase 4: User Story 2 — Conduct a Tertiary Study (Priority: P2)

**Goal**: A Tertiary study opens its own workspace and its five phases, and a seed study can be imported from the owning research group.

**Independent test**: Create a Tertiary study, open it, confirm the tertiary workspace appears, then import a seed study from the group.

### Tests for User Story 2 ⚠️ write first, must fail

- [ ] T020 [P] [US2] Integration test in `backend/tests/integration/test_studies.py`: `GET /studies/{id}` returns `research_group_id` matching the owning group, for **every** study type (FR-010)
- [ ] T021 [P] [US2] Component test in `frontend/src/pages/__tests__/StudyPage.dispatch.test.tsx`: a study whose type is Tertiary renders the tertiary workspace, not the SMS phase panels (FR-007)

### Implementation for User Story 2

- [ ] T022 [US2] Add `research_group_id: int` to `StudyDetail` and populate it in `backend/src/backend/api/v1/studies/__init__.py` (FR-009, FR-010 — seed import cannot function without it)
- [ ] T023 [P] [US2] Add `research_group_id: number` to the `StudyDetail` interface in `frontend/src/pages/StudyPage.tsx`, mirroring the backend model
- [ ] T024 [US2] Register Tertiary in `frontend/src/components/studies/studyTypeDispatch.tsx` so `StudyPage` renders its header then delegates wholesale to `TertiaryStudyPage`, passing `studyId`, `unlockedPhases`, and `groupId` (R7 — takeover, not per-phase dispatch)
- [ ] T025 [US2] Create `frontend/e2e/tertiary-workflow.spec.ts` covering protocol → seed import → screening → extraction → report against a live backend (FR-021 — this workflow has no e2e coverage today because it could not be reached)
- [ ] T026 [US2] Extend `frontend/e2e/screen-paper.spec.ts` to record a decision on a Tertiary study, completing FR-006 across all three screening study types

**Checkpoint**: Thirteen previously unreachable modules are reachable from one dispatch entry. Feature 009 delivers value to a user for the first time.

---

## Phase 5: User Story 3 — Extraction, validity, and quality reporting (Priority: P3)

**Goal**: Phases 4 and 5 present real functionality instead of a placeholder.

**Independent test**: Open a mapping study with accepted papers, record extraction data for one, then open the reporting phase and view the quality report.

### Tests for User Story 3 ⚠️ write first, must fail

- [ ] T027 [P] [US3] Component test in `frontend/src/pages/__tests__/ExtractionPage.test.tsx`: an explicit `studyId` prop takes precedence over the route parameter (R8 — do not rely on the route coincidence)
- [ ] T028 [P] [US3] Component test in `frontend/src/pages/__tests__/StudyPage.dispatch.test.tsx`: phases 4 and 5 of an SMS study render extraction and quality reporting, and the string "future sprint" appears nowhere (FR-016)

### Implementation for User Story 3

- [ ] T029 [US3] Add an optional `studyId` prop taking precedence over `useParams` in `frontend/src/pages/ExtractionPage.tsx` (R8)
- [ ] T030 [US3] Mount `ExtractionPage` and `ValidityForm` at phase 4 for the non-SLR/non-Rapid branch in `frontend/src/components/studies/studyTypeDispatch.tsx`, validity below extraction rather than in nested tabs (spec Assumption 6)
- [ ] T031 [US3] Mount `QualityReport` at phase 5 for the non-SLR/non-Rapid branch in `frontend/src/components/studies/studyTypeDispatch.tsx`
- [ ] T032 [US3] Delete both "will be available in a future sprint" placeholders from `frontend/src/pages/StudyPage.tsx` (FR-016)
- [ ] T033 [US3] Create `frontend/e2e/extraction-phases.spec.ts` covering extraction entry, the concurrent-edit conflict path, validity recording, and the quality report (FR-021)

**Checkpoint**: Six more unreachable modules are reachable. No placeholder outlives its implementation.

---

## Phase 6: User Story 4 — Re-screen after revising criteria (Priority: P4)

**Goal**: Re-assess existing candidates against current criteria without repeating the database search, preserving earlier rounds.

**Independent test**: Revise criteria, start a re-screen, watch it report progress to completion, and confirm the earlier round is still retrievable.

### Tests for User Story 4 ⚠️ write first, must fail

- [ ] T034 [P] [US4] Unit test in `backend/tests/unit/test_rescreen_job.py`: outstanding candidates are derived as study candidates minus those judged by the round's reviewer, including after a partial run (R5 — no stored cursor)
- [ ] T035 [P] [US4] Unit test in `backend/tests/unit/test_rescreen_job.py`: the in-flight guard matches `full_search`, `snowball_search`, and `rescreen` in non-terminal states and ignores terminal ones (FR-026)
- [ ] T036 [P] [US4] Integration test in `backend/tests/integration/test_screening_runs.py`: `202` enqueues a job and creates exactly one new reviewer carrying the round in `agent_config` (FR-019, R2)
- [ ] T037 [P] [US4] Integration test in `backend/tests/integration/test_screening_runs.py`: `409` while a full search runs, with `blocking_job_id` and `blocking_job_type` in the payload (FR-026)
- [ ] T038 [P] [US4] Integration test in `backend/tests/integration/test_screening_runs.py`: `422` when the study has no candidate papers
- [ ] T039 [P] [US4] Integration test in `backend/tests/integration/test_screening_runs.py`: a run failing part-way retains its assessments, reports coverage, is not marked complete, and a restart covers only the remainder (FR-024)
- [ ] T040 [P] [US4] Integration test in `backend/tests/integration/test_screening_runs.py`: decisions recorded by a human survive a run untouched (FR-019)
- [ ] T041 [P] [US4] Migration test in `db/tests/integration/test_migrations.py`: `0019` upgrades and downgrades cleanly

### Implementation for User Story 4

- [ ] T042 [US4] Add `RESCREEN = "rescreen"` to `JobType` in `db/src/db/models/jobs.py` (R1)
- [ ] T043 [US4] Create Alembic migration `db/alembic/versions/0019_rescreen_job_type.py` adding the value to `background_job_type_enum`, with a working `downgrade()` (R1 — the PRD's "no migration" claim is wrong on this point)
- [ ] T044 [US4] Create `backend/src/backend/jobs/rescreen_job.py` composing the extracted screening pipeline, creating one reviewer per round and deriving outstanding candidates from decision rows (R2, R5). **On failure it must commit the assessments it completed and record its coverage — it must NOT call `_fail_search_run`, which rolls back** (R9). The search jobs restart because re-running a query is cheap; a re-screen resumes because each assessment is a paid provider call and R5's cursor-free resume reads the very rows a rollback would destroy
- [ ] T045 [US4] Register the re-screen job in `backend/src/backend/jobs/worker.py`
- [ ] T046 [US4] Create `backend/src/backend/api/v1/screening_runs.py` implementing `POST /studies/{id}/screening-runs` with the 202/409/422 responses per `contracts/screening-runs.md`, gated on `require_study_member` (FR-023)
- [ ] T047 [US4] Register the new router in `backend/src/backend/api/v1/router.py` (Principle X — an unregistered router is dead code)
- [ ] T048 [P] [US4] Create `frontend/src/services/screeningRunsApi.ts` to start a run and read its progress, with role-namespaced query keys (`['screening-runs','detail',id]` — never distinguish by argument absence)
- [ ] T049 [US4] Add a re-screen control feeding the returned `job_id` to the existing `JobProgressPanel` in `frontend/src/components/studies/ScreeningView.tsx`
- [ ] T050 [US4] Create `frontend/e2e/rescreen.spec.ts` covering start, progress, completion, and preservation of the prior round (FR-021)

**Checkpoint**: All four journeys complete. Every capability in the feature is reachable and driven by an e2e test.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T051 Add `python3 scripts/audit_unreachable_frontend.py` as a required step in `.github/workflows/ci.yml` (Principle X — turns the acceptance oracle into a regression gate)
- [ ] T052 [P] Replace the 5 conditional `test.skip()` calls in `frontend/e2e/results-dashboard.spec.ts` with real assertions or `test.fixme` plus a gap citation (C4 — forbidden by Principle VI; recorded as a known outstanding violation in the constitution)
- [ ] T053 [P] Verify coverage ≥85% for `backend`, `db`, and `frontend` via the commands in `quickstart.md`
- [ ] T054 [P] Run mutation testing on every modified subproject — `./scripts/run-mutation-safe.sh backend`, `./scripts/run-mutation-safe.sh db`, and `cd frontend && npx stryker run` — and record the scores in the PR (≥85% killed)
- [ ] T055 Confirm the definition of done in `quickstart.md`: audit exits 0, no "future sprint" string remains, no `isVisible()` guards or conditional skips introduced

### Feature Completion Documentation (Constitution Development Workflow step 9)

- [ ] TDOC1 [P] Update `CLAUDE.md` with the re-screen command surface and the reachability audit's new CI role
- [ ] TDOC2 [P] Update root `README.md` — remove the route-table note saying the Tertiary workflow is unreachable, which this feature makes false
- [ ] TDOC3 [P] Update root `CHANGELOG.md` with what this feature added, changed, and fixed
- [ ] TDOC4 [P] Update `backend/README.md`, `db/README.md`, and `frontend/README.md` for the modified subprojects
- [ ] TDOC5 [P] Update `backend/CHANGELOG.md`, `db/CHANGELOG.md`, and `frontend/CHANGELOG.md`
- [ ] TDOC6 Mark **G18, G19, G20** closed in `docs/feature-gaps.md` and update the built-but-never-wired audit count from 23 to the two remaining G21 modules
- [ ] TDOC7 [P] Add a `MEMORY.md` entry if implementation surfaces a further non-obvious trap, per that file's own guidance

---

## Dependencies

```text
TREF1 → TREF2 ────────────────┐
TREF3 → TREF4 → TREF5 → TREF6 │
                              ▼
        Phase 1 (T001–T002) → Phase 2 (T003–T006)
                              │
        ┌─────────────────────┼─────────────────────┬──────────────────┐
        ▼                     ▼                     ▼                  ▼
   US1 (T007–T019)      US2 (T020–T026)      US3 (T027–T033)    US4 (T034–T050)
        │                     │                     │                  │
        └──────── T026 needs US2's T024 ────────────┘                  │
                              │                                        │
                        T049 needs US1's T015 ────────────────────────┘
                              ▼
                       Phase 7 (T051–T055, TDOC1–TDOC7)
```

**Hard dependencies**

- **TREF2 blocks US2 and US3** — both mount into the dispatch map it creates. Adding them to the
  boolean chain first is the cheapest path and the one that recreates this feature's own defect.
- **TREF4 and TREF6 block US4** — the re-screen job composes the extracted pipeline, and FR-024
  is unsatisfiable while a provider fault is persisted as a rejection.
- **T042 → T043 → T044** — enum, then migration, then the job that inserts rows using it.
- **T026 depends on T024** — a Tertiary study must be reachable before a decision can be recorded
  on one. This is why US1's own e2e covers SMS and SLR only, keeping the story independently
  testable.
- **T049 depends on T015** — the re-screen control lives in the screening view US1 creates.

**Story independence**: US1, US2, and US3 are independently deliverable once the refactors land.
US4 depends only on the refactors plus one control placement.

---

## Parallel Execution Examples

**Within the refactoring phase** — two independent tracks:

```text
Track A (frontend): TREF1 → TREF2
Track B (backend):  TREF3 → TREF4 → TREF5 → TREF6
```

**Within US1** — the test tasks are different files or independent cases:

```text
T007, T008, T009 [P]  backend integration tests
T011, T012       [P]  frontend component tests
(T010 is sequential — it edits the same test file as T007–T009)
```

**Within US4** — eight test tasks run together:

```text
T034, T035                   [P]  unit
T036, T037, T038, T039, T040 [P]  integration
T041                         [P]  migration
```

**Across stories, after the refactors land**: US1, US2, and US3 proceed on three tracks; only
T026 and T049 need a join.

---

## Implementation Strategy

**MVP** — refactors plus Phase 1–3 (TREF1–TREF6, T001–T019). Delivers manual screening on SMS and
SLR studies, which unblocks inter-rater agreement and is the single most consequential gap.

**Incremental delivery**

| Increment | Adds                                    | User-visible outcome                                 |
| --------- | --------------------------------------- | ---------------------------------------------------- |
| MVP       | Screening decisions                     | Papers can be judged; agreement becomes measurable   |
| + US2     | Tertiary workspace, `research_group_id` | An entire study type becomes usable                  |
| + US3     | Phases 4 and 5                          | A study can be carried to a report                   |
| + US4     | Re-screening                            | Criteria can be revised without repeating the search |
| + Phase 7 | CI reachability gate, docs, mutation    | The defect class cannot silently recur               |

**Commit discipline** (Principle IV): TREF1–TREF6 are `refactor:` / `fix:` commits carrying no
feature change. Story tasks are `feat:`. T010's test migration belongs with T013's implementation
in one commit — a required field and its callers must move together.

---

## Task Summary

| Phase               | Tasks       | Count  |
| ------------------- | ----------- | ------ |
| Refactoring (C1–C3) | TREF1–TREF6 | 6      |
| Setup               | T001–T002   | 2      |
| Foundational        | T003–T006   | 4      |
| US1 (P1) 🎯 MVP     | T007–T019   | 13     |
| US2 (P2)            | T020–T026   | 7      |
| US3 (P3)            | T027–T033   | 7      |
| US4 (P4)            | T034–T050   | 17     |
| Polish              | T051–T055   | 5      |
| Documentation       | TDOC1–TDOC7 | 7      |
| **Total**           |             | **68** |
