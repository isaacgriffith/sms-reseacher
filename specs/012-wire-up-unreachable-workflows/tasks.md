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

- [x] TREF1 [P] Write characterisation tests for `StudyPage`'s current per-study-type rendering in `frontend/src/pages/__tests__/StudyPage.dispatch.test.tsx` — assert SLR, Rapid, and SMS each render their existing phase bodies, so the C1 refactor is provably behaviour-preserving
- [x] TREF2 Replace the eleven `isSLR` / `isRapid` boolean dispatch points in `frontend/src/pages/StudyPage.tsx` with a study-type → renderer map in `frontend/src/components/studies/studyTypeDispatch.tsx` (C1; mirrors the backend's `_PHASE_GATE_DISPATCH`)
- [x] TREF3 [P] Write unit tests for `_load_criteria`, `_process_single_candidate`, and `_record_paper_decision` in `backend/tests/unit/test_screening_pipeline.py` before extracting them
- [x] TREF4 Extract the screening helpers from `backend/src/backend/jobs/search_job.py` (941 lines) into `backend/src/backend/jobs/screening_pipeline.py`, leaving `search_job.py` importing them (C2 — brings the file under the 800-line maximum and gives the re-screen job a shared home rather than a copy)
- [x] TREF5 [P] Write a failing test in `backend/tests/unit/test_screening_pipeline.py` asserting that a provider error during screening raises rather than returning `("rejected", [])` (C3 — must be RED before TREF6)
- [x] TREF6 Change `_run_screening_pass` in `backend/src/backend/jobs/screening_pipeline.py` to propagate provider errors instead of swallowing them into a rejection (C3 — FR-024 is unsatisfiable while a fault is persisted as a legitimate reject)
- [x] TREF7 Give `CandidatePaper` a `paper` relationship and delegate `title` / `abstract` to it in `db/src/db/models/candidate.py`; construct candidates with `paper=` rather than `paper_id=` in `screening_pipeline.py` (**C6**, found while doing TREF6 — both callers pass a `CandidatePaper` to `_run_screening_pass`, which reads `.abstract` off it. `CandidatePaper` carried neither field, so every call raised `AttributeError` into the bare `except` and returned a rejection: the screener was never invoked for any paper in any search. TREF6 is not landable without this, since propagating the error would turn a silent wrong answer into a crash on every search)

- [x] TREF8 Fail the run rather than stranding it: `run_full_search` now wraps its sweep and calls `_fail_search_run`, which rolls back the partial sweep and marks the `SearchExecution` and `BackgroundJob` failed (**C7** — with TREF6 propagating, a provider outage escaped `run_full_search`, which had no handler, leaving the job row at `running` for ever; the UI cannot tell a crashed search from a slow one). The sweep moves to `_execute_search_sweep`, and `run_expert_seed_suggestion` moves to `backend/src/backend/jobs/seed_suggestion_job.py` — it is a phase-1 seeding job, not a search, and keeping it here put `search_job.py` back over the 800-line maximum

- [x] TREF9 Give `run_snowball` the same failure handling, and record the policy that T044 must **not** copy. Snowball moves to `backend/src/backend/jobs/snowball_job.py` (it walks citation edges rather than querying an index, and keeping it in `search_job.py` breached the 800-line maximum again); it now marks its `SearchExecution` running → completed → failed, where it previously left it `pending` whatever happened, and shares `_fail_search_run`. The opposite policy required of the re-screen job is recorded as **R9** in `research.md`, on T044 itself, in `_fail_search_run`'s docstring, and in `MEMORY.md`

**Checkpoint**: `uv run pytest backend/tests/` and `cd frontend && npm test` both green. Behaviour
does change for a user, and deliberately: the AI screener now actually runs during a search
(TREF7), and a failed search reports itself as failed (TREF8). Covered end-to-end against a live
database by `backend/tests/integration/test_search_pipeline_screening.py`.

---

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Record the baseline in `specs/012-wire-up-unreachable-workflows/quickstart.md` by running `python3 scripts/audit_unreachable_frontend.py` (expect 23 unreachable), `grep -rn "future sprint" frontend/src` (expect 2), and `grep -c "test.fixme" frontend/e2e/screen-paper.spec.ts` (expect 3) — if any already passes, the plan needs revisiting before work starts

  > Recorded 2026-08-08. Nothing has started passing, so the plan stands. Audit: 23, exit 1.
  > `test.fixme`: 3 in `screen-paper.spec.ts`, 8 suite-wide — both unchanged. The `"future sprint"`
  > grep returned **4**, not 2, and the discrepancy is TREF2's doing: two literal `<Typography>`
  > lines in `StudyPage.tsx` became one `futureSprintPlaceholder(phase)` factory in
  > `studyTypeDispatch.tsx`, which TREF1's characterisation test then names three times. One
  > production occurrence, three assertions about it. **T032 is therefore a replacement, not a
  > deletion** — see the note in `quickstart.md`.

- [x] T002 [P] Verify the baseline is clean by running every hook in `.pre-commit-config.yaml` via `uv run pre-commit run --all-files`, so later gate failures are attributable to this feature rather than pre-existing — 9/9 pass on 2026-08-08

---

## Phase 2: Foundational (Blocking Prerequisites)

> Test fixtures every story's e2e depends on. Without these the four journeys cannot be driven
> against a live backend, which FR-021 requires.

- [x] T003 Extend `scripts/seed_e2e_user.py` with a Tertiary study owned by the seeded research group, so US2 has something to open — `_seed_tertiary_study`. Deliberately carries **no** protocol row: phase 1 is always unlocked for a Tertiary study, and seeding a _validated_ protocol would skip past the first step of the journey T025 exists to exercise
- [x] T004 [P] Extend `scripts/seed_e2e_user.py` with a study holding accepted papers and at least one extraction record, so US3 has data to display — `_seed_extraction_fixture`. Two **additional** accepted papers on the main study rather than a re-status of `SEED_PAPERS`, which `screen-paper.spec.ts` needs to stay pending; one carries an extraction, one is left bare so the view has a populated row and an empty one
- [x] T005 [P] Extend `scripts/seed_e2e_user.py` with a candidate paper carrying two disagreeing reviewer decisions, so US1 can exercise the conflict path — `_seed_conflict_fixture`. Both reviewers are **human**: `papers.py` filters to `ReviewerType.HUMAN` before comparing outcomes, so a human-versus-AI pair would leave `conflict_flag` false however much they disagree
- [x] T006 [P] Extend `scripts/seed_e2e_user.py` with a second research-group study, so Tertiary seed import has a source to offer — `_seed_seed_import_source`. Typed SMS (the panel filters to SMS/SLR/Rapid) and carrying **accepted** papers (`import_seed_study` raises `ValueError` on a source with none), so it both lists and imports

**Checkpoint**: `uv run python scripts/seed_e2e_user.py` is idempotent and creates every fixture the four journeys need.

---

## Defects found during implementation

> Found while reading code this feature depends on, not by looking for them. Each lands as its own
> `fix:` commit carrying no feature change (Principle IV), placed at the point where the work that
> depends on it begins.

- [x] TFIX1 **The SMS phase 4/5 unlock query has no `study_id` filter.** `get_unlocked_phases` in `backend/src/backend/services/phase_gate.py` gates phases 4 and 5 on `select(DataExtraction).where(DataExtraction.extraction_status != ExtractionStatus.PENDING)` — a query over the whole table. One non-pending extraction _anywhere in the database_ unlocks phases 4 and 5 for _every_ SMS study, including studies with no papers, no search, and no extraction of their own. Fix by joining `CandidatePaper` and constraining `CandidatePaper.study_id == study_id`, which is what `tertiary_phase_gate.py` already does for its own phase 5. **Blocks US3**: T028 asserts phases 4 and 5 render extraction and quality reporting, and until this is fixed that test can pass for the wrong reason — T004's seeded extraction unlocks those phases globally, so T028 would be green even if the study under test had nothing of its own to show. Land it **before** T029

  > **Reproduced 2026-08-08** against the fixtures T003–T006 create. `E2E Source Mapping Study`
  > (study 3) holds two accepted papers and **zero** `DataExtraction` rows of its own. Given a PICO
  > so the gate reaches the phase 4/5 query rather than returning early at phase 2,
  > `get_unlocked_phases(3)` returns `[1, 2, 3, 4, 5]` — phases 4 and 5 unlocked solely because
  > study 1 has an extraction. A demonstrated defect, not an inference from reading.
  >
  > Add a regression test alongside the fix: two SMS studies both past phase 3, an extraction on
  > the first only, asserting the second does not reach phase 4. Without that assertion the defect
  > stays invisible to the suite, which is how it survived this long.

- [x] TFIX2 **`alembic upgrade head` does not work from the repository root.** `alembic.ini` lives in `db/`, there is no root `alembic.ini`, and the root `pyproject.toml` has no `[tool.alembic]` section — so `uv run alembic upgrade head` from the repo root fails with `FAILED: No 'script_location' key found in configuration.` It is documented in the root position in **two** places a newcomer follows first: `CLAUDE.md` ("Database Migrations", all three commands, plus the manual stack startup under e2e) and this feature's own `quickstart.md` (Setup). Fix the documented commands to `(cd db && uv run alembic upgrade head)` — the same treatment the coverage commands already got — or add a root `alembic.ini` pointing at `db/alembic`. **Blocks no code, blocks every fresh setup**, including the `quickstart.md` Setup block this feature tells a reader to run before anything else

  > Found while setting up a database to verify T003–T006. Related, and worth stating where a
  > reader will hit it: **the migrations do not run on SQLite at all.** `0014` calls `add_column`
  > with a foreign-key constraint outside batch mode, and the SQLite dialect raises
  > `NotImplementedError: No support for ALTER of constraints`. A local SQLite database therefore
  > has to be built with `Base.metadata.create_all`, which is what the `db` test suite does — the
  > documented `alembic upgrade head` path is PostgreSQL-only. Neither file says so, and
  > `CLAUDE.md`'s manual e2e startup explicitly pairs `alembic upgrade head` with
  > `DATABASE_URL=sqlite+aiosqlite:///./dev.db`, which cannot work.

- [x] TFIX3 **`PaperDecision` has no `annotation` column, and the annotation masquerades as a criterion.** `data-model.md` lists `annotation` among `PaperDecision`'s fields. There is no such column (`db/src/db/models/candidate.py`). `ReviewerPanel.tsx:82-83` instead appends the free text to the `reasons` JSON array as `{"criterion_type": "annotation", "text": "…"}`. The capability works, so nothing is broken for a user — but FR-002 says reasons are "drawn from the study's criteria", and an annotation carried as a pseudo-reason is counted by anything that counts reasons, including any future agreement or criteria-frequency analysis. Either add a real `annotation` column (a migration, which `data-model.md` says this feature does not have) or state the encoding explicitly in `data-model.md` and make every reader of `reasons` filter `criterion_type == "annotation"`. **Low severity, high staleness risk** — recorded because the documentation currently describes a field that does not exist

  > **Resolved 2026-08-08 — the user chose the column.** Migration `0020` adds a nullable
  > `paper_decision.annotation`; `annotation` becomes its own field on `DecisionRequest`,
  > `ResolveConflictRequest` and `DecisionResponse`; `ReviewerPanel` sends it top-level and no
  > longer appends a fake criterion to `reasons`. Empty input sends `null`, not `""` — those are
  > different claims about whether the reviewer wrote anything.
  >
  > One fact that reframed the severity while the options were being weighed: **nothing
  > analytical reads `reasons` today.** The only consumer is `PaperCard`'s display list, and the
  > AI screening pipeline writes reasons but never annotations. The pollution was prospective,
  > not active — it would have bitten criteria-frequency and criteria-based agreement analysis,
  > which the methodology corpus calls for and which is not built yet.
  >
  > **No data migration.** Existing rows keep their embedded pseudo-reason, and `PaperCard`
  > renders either encoding: it pulls `criterion_type == "annotation"` entries out of the
  > criteria list into the annotation slot, falling back to the new column when present. Old rows
  > display correctly, and a legacy annotation never appears in both places.
  >
  > This pushes the rescreen migration from `0020` to **`0021`** — corrected on T041, T043,
  > `plan.md`, `data-model.md`, `quickstart.md` and `CLAUDE.md`. A reserved gap was considered
  > and rejected: alembic chains on `down_revision`, so a placeholder number would depend on
  > whoever writes the next migration remembering to splice in before it.

- [x] TFIX4 **The screening UI asks the researcher to type their own database id.** `ReviewerPanel.tsx` renders a numeric "Reviewer ID" input, and `canSubmit` is false until it is filled. Its own comment concedes the point: _"simplified — in real use would be populated from auth context"_. FR-005 requires that any member of a study can record a decision; requiring them to know their internal `reviewer.id` is not that. There is **no endpoint that resolves the current user's reviewer row** — `grep` finds no `/reviewers` route anywhere under `backend/src/backend/api/v1/`, so this cannot be fixed in the frontend alone. Add `GET /api/v1/studies/{id}/reviewers` (or return the caller's `reviewer_id` on `StudyDetail`, alongside the existing `viewer_role`), then have `ReviewerPanel` resolve it and drop the input. **Blocks T018 and T019**

  > This is why US1's e2e is not written yet. An e2e could type `1` and pass — the seed fixtures
  > make reviewer ids deterministic — but it would be asserting that a screen no researcher can
  > use does work. Feature 012 exists because finished code was unreachable; shipping a green e2e
  > over an unusable control would be the same failure with a passing test on top.
  >
  > Note this also makes the _wrong reviewer_ trivially recordable today: nothing stops a user
  > typing another member's reviewer id, and the endpoint only checks that the reviewer belongs to
  > the study (`_require_reviewer_in_study`), not that it belongs to the caller. Whoever fixes
  > TFIX4 should decide whether the endpoint starts rejecting a `reviewer_id` that is not the
  > caller's own — which would be a second, deliberate tightening in the shape of FR-027.

  > **Resolved 2026-08-08.** The user's call, and it is better than any of the three options I
  > put up: _"have the reviewer ID be associated with the User ID and be held within the session
  > context. Thus, when the user records a decision on a paper, the reviewer id is pulled from
  > the current session."_ `reviewer_id` is **deleted** from `DecisionRequest` and
  > `ResolveConflictRequest`; `_resolve_session_reviewer(study_id, current_user, db)` resolves the
  > caller's `human` reviewer row from `(study_id, current_user.user_id)`, creating it on demand
  > so a member added after study creation can screen at all — which is what FR-005 actually
  > requires. `_require_reviewer_in_study` is gone; it validated an input that no longer exists.
  >
  > Removing the field closed the impersonation hole as a side effect rather than as a separate
  > tightening, so no FR-027-shaped decision was needed. It also fixed a third instance nobody had
  > catalogued: `PaperCard` resolved conflicts as `onResolve(lastTwo[0]?.reviewer_id ?? 0, …)`,
  > attributing the binding resolution to the first disagreeing reviewer, or to reviewer `0`.
  >
  > The integration tests improved as a consequence: the multi-reviewer cases now authenticate as
  > two real users (`alice`, `bob`) instead of inserting two synthetic reviewer rows, which is
  > what the feature actually models. `test_reviewer_not_in_study_returns_422` was replaced by
  > `test_non_member_returns_403` — the guarantee that now carries the weight.

- [x] TFIX5 **SLR quality scoring cannot be reached, and the identity trap is already laid behind it.** Two separate problems that look like one, because a hardcoded `reviewerId={0}` makes the second one visible while the first hides it.

  **1. `QualityScoreForm` is unreachable.** Nothing imports it but its own test; it is one of the 20 modules `scripts/audit_unreachable_frontend.py` reports. `QualityAssessmentPage`'s "Score Papers" tab renders the string `Select an accepted paper to score it.` and no form — the accepted-paper selector that sentence implies does not exist. So **no quality score can be submitted through the UI at all**. Wiring it is feature work (selector + mount), takes the audit 20 → 19, and overlaps US3's territory rather than being a one-line fix.

  **2. The endpoint takes a client-supplied `reviewer_id`.** `backend/src/backend/api/v1/slr/quality.py:269` passes `body.reviewer_id` straight to `quality_assessment_service.submit_scores` with no check that the reviewer belongs to the caller — the identical shape TFIX4 removed from screening. Latent while (1) holds, live the moment the form is wired. Fix it the same way: resolve from the session, delete the field from the request body.

  **3. The `reviewerId` prop is dead.** `studyTypeDispatch.tsx:304` passes `reviewerId={0}`, and `QualityAssessmentPage` immediately discards it — `reviewerId: _reviewerId`, unused. Delete the prop and the argument.

  > **This entry replaces an earlier version that was wrong, and the way it was wrong is the point.**
  > It claimed "every reviewer sees and writes the same phantom reviewer `0`", and therefore that
  > "Cohen's κ over quality scores is computed across reviewers who are all recorded as the same
  > person, so inter-rater agreement on quality assessment is meaningless." **None of that is
  > happening.** κ cannot be computed over UI-entered scores because there are none: the form is
  > unreachable and the tab renders a placeholder.
  >
  > The error came from reading `reviewerId={0}` at the call site and inferring the capability
  > behind it ran — without tracing where the value landed. It landed nowhere. That is precisely
  > the failure mode feature 012 exists to eliminate, committed while cataloguing it, which is
  > the strongest available argument that a call site is not evidence a capability works.
  >
  > Recorded rather than silently corrected because `docs/feature-gaps.md` already tracks
  > "present and wrong" as a defect class with **no automated instrument**, and this is a worked
  > example of a human (and an AI) producing one under exactly the conditions that class predicts.

  > **Resolved 2026-08-08 — and there were four parts, not three.** Audit **8 → 7**;
  > `QualityScoreForm` is mounted behind an accepted-paper selector on the Score Papers tab, which
  > replaces the `Select an accepted paper to score it.` placeholder. No new endpoint: the selector
  > reuses `GET /studies/{id}/papers?status=accepted`, already gated on `require_study_member` and
  > already called by `PaperQueue`.
  >
  > **Part 4, which this entry missed: none of the four routes in `slr/quality.py` checked study
  > membership at all.** The module imported only `get_current_user`, so any authenticated user
  > could read _and write_ quality scores for any paper in any study — while `rapid/quality.py`,
  > the direct analogue, has always had the check. Demonstrated, not inferred:
  > `assert 200 == 403` on all four routes with a non-member caller, and
  > `assert 1 not in {1}` showing a spoofed `reviewer_id` accepted verbatim.
  >
  > **All four parts share one cause, and it is the argument for Principle X being a gate rather
  > than a report.** Every one of them was unexploitable while the form was unreachable: a
  > client-supplied `reviewer_id` cannot be abused through a form nobody can open, a missing
  > authorization check cannot be exercised by a UI that never calls the endpoint, and
  > `reviewerId={0}` cannot corrupt data it never reaches. Unreachability does not merely hide
  > defects, it **suppresses** them — so they accumulate silently and go live together the moment
  > someone wires the thing up. Fixing them in the same commit as the wiring is not tidiness; it is
  > the only ordering that never ships the hole.
  >
  > Two design points the entry could not have anticipated:
  >
  > - **The same identity is resolved two different ways.** The PUT creates the caller's `Reviewer`
  >   row on demand (`resolve_session_reviewer`, shared with screening); the GET must **look up
  >   only** and return `viewer_reviewer_id: int | None`, because a read must not have the side
  >   effect of creating a row. One shared helper would have been the obvious refactor and would
  >   have made every page load write to the database. No test can see the difference — only
  >   reading the code can.
  > - **`0` is a valid reviewer id on both sides.** The backend must not coerce a missing lookup to
  >   `0`; the frontend must not treat a received `0` as missing. Same value, opposite errors, each
  >   invisible in the other half's tests. Pinned by
  >   `prefills correctly when viewer_reviewer_id is legitimately 0, not just truthy`.
  >
  > Incidentally fixed: `get_quality_scores` re-queried `CandidatePaper` **and** refetched the
  > checklist inside its per-reviewer loop, with an `import` in the function body — an N+1 that ran
  > once per reviewer. A nonexistent `candidate_paper_id` now 404s instead of answering 200 with an
  > empty score list; membership cannot be checked without resolving the owning study, so the
  > lookup has to happen and its failure has to mean something.
  >
  > `_resolve_session_reviewer` lost its underscore and is now `resolve_session_reviewer`: an
  > underscore claims module-private, and it is imported across modules. **TREF10** renamed
  > `_ensure_*` to `ensure_*` in `scripts/seed_helpers.py` on the same rule, in this same feature.
  >
  > Backend 1182 passed (from 1174), frontend 1371 (from 1365), 22 new tests.

- [x] TFIX7 **REWRITTEN 2026-08-09 — the original complaint was dissolved by TFIX9, and what is underneath is worse.** As first written this said Tertiary phase 4 was unreachable because the gate demanded a `QualityAssessmentScore` that no UI writes. TFIX9 re-keyed that gate to accepted papers, so the deadlock is gone and phase 4 opens. Revisiting it showed the premise was also wrong in a second way: **Tertiary quality assessment is captured**, just not in `QualityAssessmentScore`. It lives on `TertiaryDataExtraction.reviewer_quality_rating` — a single `float | None` (`db/src/db/models/tertiary.py:227`) driven by a slider at `TertiaryExtractionForm.tsx:317`. Three defects remain, none of which the original entry named:
  1. **The rating defaults to `0.5` and is submitted as a judgement.** `TertiaryExtractionForm.tsx:108` seeds the form with `extraction.reviewer_quality_rating ?? 0.5`, and line 126 submits whatever the form holds. A reviewer who never touches the slider persists a mid-scale quality rating they never made. This is the same class as the rejected TFIX8 "make the form save `validated`" fix — fabricated evidence of an assessment that did not happen — except that this one already ships. The honest default is `null`, with the control showing "not assessed".
  2. **The report says quality assessment was performed whether or not it was.** `_build_qa_results` (`tertiary_report_service.py:388`) never reads a quality rating at all — it branches on `synthesis.computed_statistics` and returns _"Quality assessment was performed. Computed statistics: …"_ or _"Quality assessment was completed. No computed statistics are available."_ Both assert it happened. A tertiary report therefore claims quality assessment for a study where nobody assessed anything, which is a reporting-integrity defect, not a UI gap.
  3. **A single float is the wrong instrument.** `04-tertiary.md` specifies DARE's four anchored Y/P/N questions for tertiary studies, and `07-quality-assessment.md` warns explicitly against collapsing methodological quality into one number. `reviewer_quality_rating` is exactly that number. Correcting the shape is feature-sized and should not be bundled with (1) and (2), which are small and independently correct.

  > Worth keeping as a lesson about this ledger rather than about the code: TFIX7 was written from a gate condition and an absent UI, and it inferred a missing capability from them. The capability was present the whole time, one table over, and the real defects were a fabricating default and a report that asserts an unperformed step. **A defect entry is a restatement too, and this file's own preamble warns that restatements go stale.** It survived three days and one commit that cited it.

  > **Status 2026-08-09 — parts 1 and 2 fixed in `5eb9582`; part 3 remains open, which is why this
  > entry stays unchecked.** The form now defaults `reviewer_quality_rating` to `null` rather than
  > `0.5`, and `_build_qa_results` reads the ratings it describes — reporting coverage, the mean,
  > how many were not assessed, and how many meet the protocol threshold — instead of asserting
  > "Quality assessment was performed" from `SynthesisResult.computed_statistics`. Backend
  > 1190 → 1194.
  >
  > A **third** test was found encoding its own defect: `defaults reviewer_quality_rating to 0.50
when null is passed`, whose comment described the fabrication as intended behaviour. The other
  > two were `QualityAssessmentPage.test.tsx` asserting the placeholder exists (TFIX5) and
  > `test_phase_4_locked_without_qa_scores` asserting the deadlock (TFIX9). All three were green,
  > and none could be fixed without first deleting an assertion.
  >
  > The report tests asserted only `isinstance(quality_assessment_results, str)`. **A type
  > assertion cannot tell a true sentence from a false one** — which is how a report claiming an
  > unperformed methodological step survived from feature 009. Four real assertions replace it.
  >
  > **Part 3 — the DARE shape — was deliberately not bundled**, and was then done on its own.
  > `reviewer_quality_rating` is a single 0–1 float where `04-tertiary.md` specifies four anchored
  > Y/P/N questions and `07-quality-assessment.md` warns against collapsing quality into one
  > number.

  > **Status 2026-08-09 — part 3 complete, so this entry now closes.** DARE is implemented,
  > reachable from Tertiary phase 4, and read by the report.
  >
  > **The sizing in the line above was wrong, and wrong in the useful direction.** "A new
  > instrument, new storage, and a migration" assumed DARE needed a table of its own. It did not:
  > `QualityAssessmentChecklist` → `QualityChecklistItem` → `QualityAssessmentScore` already models
  > a study-scoped anchored checklist with per-item notes, and DARE *is* a four-item anchored
  > checklist. Reuse also inherits the Cohen's κ pipeline, which matters rather than being a bonus
  > — `07-quality-assessment.md` records agreement on quality scoring at **0.54** on average score
  > even between two expert authors, so a tertiary study that cannot measure its own disagreement
  > is reporting a number it has no grounds to trust. What was actually missing was one enum value
  > and one column.
  >
  > | Assumed | Actual |
  > | ------- | ------ |
  > | New table for DARE | Reuse the existing checklist tables |
  > | New scoring UI | Reuse `QualityScoreForm`, the component TFIX5 made reachable |
  > | — | `ChecklistScoringMethod` had only `binary`/`scale_1_3`/`scale_1_5`; **none can express Y=1/P=0.5/N=0** — binary has no middle, both scales start at 1 so N=0 is unreachable |
  > | — | Nowhere to store the three anchors per question, so they could not reach the reviewer |
  > | — | `notes` was labelled "Notes (optional)" where the corpus makes justification **mandatory** |
  >
  > **Migration `0021_dare_quality_instrument`** adds `yes_partial_no` to
  > `checklist_scoring_method_enum` and a nullable `anchors` JSON column on
  > `quality_checklist_item`. **Executed against PostgreSQL 16**, not merely written: `upgrade` to
  > head, enum confirmed to carry all four values, `anchors json` confirmed present, `downgrade -1`
  > confirmed to drop the column, and `upgrade` re-applied. The enum value is left in place on
  > downgrade — PostgreSQL has no `ALTER TYPE ... DROP VALUE`, the same call 0016 made.
  >
  > **This takes revision `0021`, so T043's rescreen migration becomes `0022`** — corrected in that
  > task. That number has now moved twice (`0019` → `0021` → `0022`); it is a plan artefact, and
  > `(cd db && uv run alembic heads)` is the only trustworthy source.
  >
  > **Four decisions worth keeping, because each was a chance to fabricate:**
  >
  > 1. **Nothing is preselected.** A `yes_partial_no` item defaults to unanswered, and submission
  >    is blocked until every item has both a score and a justification. Defaulting to "Yes" would
  >    have reproduced part 1's defect exactly — a judgement the reviewer never made, submitted on
  >    their behalf — one instrument over.
  > 2. **The optional fifth question is CRD's criterion 3, "Were the included studies
  >    synthesized?"** — mandatory in the original DARE, dropped by SE, and
  >    `10-reporting-and-evaluation.md` calls restoring it "worth" doing. **The corpus gives no
  >    Y/P/N anchors for it**, because CRD scored it binary, so the three written here are marked
  >    *platform-authored* in the constant, in the docstring, and in the anchor text itself. This is
  >    the failure this repo already has on record — agent prompts once scored "five Petersen
  >    rubrics" where four used anchors Petersen never published.
  > 3. **The score is reported out of 4, and the instrument is named.**
  >    `compute_aggregate_score` returns a weighted *mean* (0–1); presenting that unchanged would
  >    show "0.75" where DARE says "3 out of 4". `04-tertiary.md` warns DARE scores are not
  >    comparable across review types, and an unlabelled number invites exactly that comparison.
  > 4. **A second copy of the checklist routes under `/tertiary` was built and then removed.** It
  >    looked tidier than a Tertiary study calling `/api/v1/slr/...`, but the frontend calls the
  >    `/slr` paths, so the duplicate answered nobody. Adding an unreachable endpoint to tidy a
  >    prefix is the defect this whole feature exists to delete. Only `POST
  >    /tertiary/studies/{id}/quality-checklist/dare` is new. Moving those routes out of `/slr`
  >    entirely is the real fix and breaks existing callers, so it belongs in its own change.
  >
  > **`reviewer_quality_rating` is deprecated, not dropped** — the user's call. Existing rows keep
  > their data; nothing reads it. Dropping it would destroy values that are partly real and partly
  > the fabricated 0.5 the old default wrote, irreversibly and without being able to tell which.
  >
  > Two silent data-loss paths were found while wiring it, neither of which any test would have
  > caught: the frontend's `scoring_method` Zod enum is **strict**, so an unlisted
  > `yes_partial_no` fails the *whole* checklist response rather than one field; and
  > `QualityChecklistEditor` rebuilds items field-by-field while `upsert_checklist` replaces all
  > items, so opening a DARE checklist and pressing Save would have stripped every anchor.
  >
  > Backend 1245 passed · frontend 1379 passed · db 164 passed · mypy clean · audit unchanged at 7.

- [x] ~~TFIX7 (original — superseded, kept because how it was wrong is the reusable part)~~ **Tertiary phase 4 gates on a quality score no UI can write.** `tertiary_phase_gate.py` unlocks phase 4 only when a `QualityAssessmentScore` exists for one of the study's candidate papers. The single writer of that table is `backend/src/backend/services/quality_assessment_service.py:195`, reached from `PUT /api/v1/slr/papers/{id}/quality-scores`; the single frontend caller is `useSubmitScores` in `frontend/src/hooks/slr/useQualityAssessment.ts`, whose single consumer is `frontend/src/components/slr/QualityScoreForm.tsx` — which nothing imports but its own test. So **no user can open Tertiary phase 4**, and phase 5 sits behind it. This is TFIX5's root cause with a consequence TFIX5 does not mention: an unreachable SLR form silently locks an unrelated study type out of two entire phases. **Blocks the extraction and report legs of T025**

- [x] TFIX8 **Tertiary phase 5 gates on a status literal the form never sends.** The gate requires ≥2 `TertiaryDataExtraction` rows with `extraction_status == "validated"`. `frontend/src/components/tertiary/TertiaryExtractionForm.tsx:127` hardcodes `extraction_status: 'human_reviewed'` on save, and **nothing in `backend/src` or `frontend/src` writes `"validated"` for a `TertiaryDataExtraction` at all** — the column is a free-form string and the PUT endpoint accepts any value, so neither side is individually wrong and neither side's tests can notice. A one-word disagreement between a gate and the only form meant to satisfy it. **Blocks the report leg of T025**

  > **Both are seeded, not skipped — the user's call on 2026-08-08**, in preference to marking the
  > blocked legs `test.fixme`. `_seed_tertiary_study` now creates the `QualityAssessmentScore`
  > (with the `QualityChecklist`, item and human `Reviewer` its unique triple requires) and two
  > `validated` extractions, so T025 can drive all five phases through the UI.
  >
  > **State the consequence wherever the result is read**: an e2e that reaches Tertiary phases 4
  > and 5 demonstrates that those panels work. It does **not** demonstrate that a user can navigate
  > to them, because the fixture opened the gate rather than the UI. Read as reachability evidence
  > it is precisely the "green and wrong" artefact this feature exists to delete.
  >
  > Neither defect is visible to `scripts/audit_unreachable_frontend.py`. After T024 the audit
  > counts `TertiaryExtractionForm`, `TertiaryReportPage` and `LandscapeSummarySection` as
  > reachable — correctly, by its own definition, because they are imported. The audit answers
  > _is this module in the import graph_; these two defects live in the gap between that and _can a
  > user get there_. Worth a `MEMORY.md` entry under TDOC7.
  >
  > Verified empirically rather than by reading, against a live PostgreSQL:
  > `get_tertiary_unlocked_phases` returns `[1]` for the seeded study, `[1, 2, 3, 4, 5]` once a
  > validated protocol is inserted, and `[1]` again after that insert is rolled back — confirming
  > the fixture opens phases 4 and 5 and that the study still ends with no protocol row, so T025
  > still starts where it is meant to.

  > **TFIX8 resolved 2026-08-09 in `23030f6` — the gate was wrong, not the form.** Phase 5 now
  > accepts `extraction_status.in_(("validated", "human_reviewed"))`. Two independent methodology
  > investigations were run against `docs/methodology/`, the second deliberately not told the
  > first's conclusion, and **they disagreed**. The first read `04-tertiary.md` §2.4's two-reviewer
  > consensus protocol and concluded the gate should stay strict while the platform grew a
  > validation workflow. The second found the passages that limit §2.4's force — it is framed as
  > "the only fully specified multi-rater extraction protocol in the corpus", an exemplar, and the
  > same chapter records a tertiary study where _"One person seeing every paper is a known bias,
  > **accepted deliberately**… Record the trade-off rather than pretending it does not exist"_,
  > while `08-extraction-and-synthesis.md` asks for double extraction _"where feasible"_. The
  > corpus prescribes **disclosure, not prohibition**. Verified both citations directly before
  > adjudicating.
  >
  > The first investigation inferred a requirement from an exemplar and stopped twelve lines above
  > the caveat that contradicts it. Had it been accepted, the platform would have grown a
  > multi-reviewer consensus workflow the corpus never demanded.
  >
  > **The opposite fix was rejected as worse than the defect**: making the form save `"validated"`
  > asserts a consensus event that never happened. Apparent conformance outranks an unreachable
  > phase under Principle XI.
  >
  > **Deliberately not widened to `!= "pending"`**, which is how `phase_gate.py` gates SMS — that
  > admits `ai_complete`, an AI pre-fill no reviewer has read. A guard test pins this so a later
  > tidy-up cannot align the two gates by loosening the correct one. The SMS gate's own weakness is
  > **TFIX10**.
  >
  > The seeded `validated` extractions stay in the fixture; they now exercise a value the gate
  > still accepts rather than one nothing writes.

- [x] TFIX13 **`TertiaryQAGuidancePanel` teaches an instrument that does not exist.** Found while wiring TFIX7 part 3, because its name made it look like the thing to reuse. `frontend/src/components/tertiary/TertiaryQAGuidancePanel.tsx:3` describes "the six **mandatory** secondary-study quality assessment dimensions used in Tertiary Studies", and line 93 states it to the user as fact. **There is no such set.** `07-quality-assessment.md:146` assigns tertiary studies **DARE — four questions**, and the same chapter says omission is permissible *with a rationale*, so nothing here is mandatory in that sense. Four of its six map loosely onto DARE (Inclusion/Exclusion Criteria Clarity ≈ Q1, Search Strategy Adequacy ≈ Q2, Quality Assessment Approach ≈ Q3, Synthesis Method Appropriateness ≈ the dropped CRD criterion 3); it **invents two** — Protocol Documentation Completeness and Validity Threats Discussion — **omits DARE Q4 entirely** (traceability, "were the basic data adequately described"), and supplies neither anchors nor scoring.

  > **Deliberately left unwired.** It is one of the seven modules the audit reports, and wiring it
  > would have taken that to six — a tempting trade that is the wrong way round. An unreachable
  > component misleads nobody; a reachable one that presents a fabricated standard as mandatory
  > misleads every reviewer who reads it, and under Principle XI that is a correctness defect, not
  > a copy problem. Its nine tests pass, and pass against the fabrication — a fourth instance of a
  > green test pinning a defect, after `QualityAssessmentPage.test.tsx` (TFIX5),
  > `test_phase_4_locked_without_qa_scores` (TFIX9) and `defaults reviewer_quality_rating to 0.50`
  > (TFIX7).
  >
  > **Not fixed here because the fix is a choice, not a correction**: delete it as superseded — the
  > real DARE guidance now ships with anchors in `dare_instrument.py` and renders beside each
  > option — or rewrite it to describe DARE and mount it above the scoring form. Deleting a
  > component and its test suite is beyond "finish TFIX7".
  >
  > This is the same shape as **G51** and as the "five Petersen rubrics" entry in `CLAUDE.md`'s own
  > table: plausible methodological content, authored rather than sourced, surviving because
  > nothing checks prose against the corpus. See [[verify_consequence_claims]].

  **Fixed 2026-08-10 — deleted, plus one sourced rule the UI was missing.** User chose delete over
  rewrite after the evidence was laid out.

  > **Deletion was the right call because the component was wholly superseded, not merely wrong.**
  > `TertiaryQualityPanel` is already mounted at `TertiaryStudyPage.tsx:340` and already states, in
  > user-visible text, everything a corrected guidance panel would have said: *"DARE — four
  > anchored questions scored Yes (1) / Partly (0.5) / No (0) — is the instrument for tertiary
  > studies. Omitting quality assessment is a legitimate choice, but it should be stated and
  > justified in the report rather than left silent."* Per-question anchors render beside each
  > option in `QualityScoreForm`, sourced from `dare_instrument.py`. Rewriting would have created a
  > **second** copy of guidance that already renders from the seeded checklist — a copy free to
  > drift, which is the mechanism that produced this defect.
  >
  > **A detail the entry did not record:** the panel's own usage note said *"Render this component
  > above the existing `QualityChecklistEditor`"* — the **SLR** path. Tertiary uses
  > `TertiaryQualityPanel`. Its mounting instruction pointed at the wrong component for its own
  > study type, so wiring it as written would not even have put it where it claimed to belong.
  >
  > 124 lines of component and 60 of test deleted. **Reachability 7 → 6** — by removing something
  > misleading rather than by wiring it, which is the trade this entry argued for.
  >
  > **One rule was genuinely missing, and it is the counter-intuitive one.**
  > `07-quality-assessment.md` records that DARE Q3 scores **N** for *"quality data extracted but
  > not used"*, so **collecting scores and ignoring them is worse than not collecting them** — a
  > reviewer who appraises diligently and then files the result away scores *below* one who never
  > appraised. Nothing in the UI said so. Added to `TertiaryQualityPanel`, attributed to Q3 rather
  > than asserted, so a reader can check it.
  >
  > **`TertiaryQualityPanel` had no test file at all** — which is how a component carrying
  > user-visible methodological claims came to have none of them pinned. Eight tests added, and
  > deliberately written to assert the *sourced claim* rather than that some text rendered: each
  > names the chapter line it protects. The deleted panel's nine tests passed against a
  > fabrication precisely because they asserted the latter.
  >
  > Frontend 1395 → 1394 (−9 deleted, +8 added), 129 files, tsc/eslint/prettier clean.

- [x] TFIX9 **Three phase gates required the output of the phase they gate, so they could never open.** `slr_phase_gate.py` unlocked phase 4 only once a `QualityAssessmentScore` existed — and `QualityAssessmentPage`, mounted at phase 4, is the only UI that defines a checklist or submits a score. Phase 5 wanted a completed `SynthesisResult`, and `SynthesisPage` at phase 5 is the only thing that starts one. `tertiary_phase_gate.py` phase 4 carried the same predicate. Each is unsatisfiable by construction: the artifact is produced inside the phase the artifact unlocks.

  **Fixed 2026-08-09 in `23030f6`**, re-keying each gate to the **previous** phase's output:

  | Gate             | Was                 | Now                   |
  | ---------------- | ------------------- | --------------------- |
  | slr phase 4      | QA score exists     | accepted papers exist |
  | slr phase 5      | synthesis completed | QA scores exist       |
  | tertiary phase 4 | QA score exists     | accepted papers exist |

  Tertiary phase 5 was left alone: it asks for phase 4's extractions, so its **shape** was already
  right and only its literal was wrong — that is TFIX8, decided on separate grounds.

  > **This is what completes TFIX5.** That commit made `QualityScoreForm` importable and the audit
  > dropped 8 → 7, and I reported it as fixed. No user could reach it: SLR phase 4 never opened.
  > An import-graph audit cannot see a phase gate — "reachable" and "navigable" are different
  > properties and only one of them has a tool. I walked into that distinction two hours after
  > writing it into TDOC7.
  >
  > An existing test encoded the deadlock: `test_phase_4_locked_without_qa_scores` asserted that an
  > accepted paper with no QA score keeps phase 4 locked. Its precondition **is** the bug. Flipped,
  > renamed, and a real guard test added so the fix cannot degenerate into "always unlock".
  >
  > `StudyPage.tsx`'s hardcoded `[...unlocked_phases, 6, 7]` was suspected to be a workaround for
  > this and is **not**: `get_slr_unlocked_phases` never computes 6 or 7 at all, so those tabs
  > would be unreachable without it. Left in place.
  >
  > Backend 1182 → 1187. **TFIX12** was found while building its fixtures.

- [x] TFIX12 **A phase gate 500s once a study has two of something it asks for one of.** The gates ask `scalar_one_or_none()`, which raises `MultipleResultsFound` on more than one row — it is not a "give me any one" helper.

  > **This entry originally said "eight such calls". It is four**, and the error is the same one the
  > entry below describes in someone else's work. I wrote it from a grep for `scalar_one_or_none()`
  > without checking whether each table can actually return two rows. Four of the eight are
  > uniqueness-protected and correct as written — `ReviewProtocol.study_id`, `RapidReviewProtocol
.study_id`, `TertiaryStudyProtocol.study_id` and `PICOComponent.study_id` are all declared
  > `unique=True`, so a second row is a genuine data defect and raising is the right response.
  > Corrected 2026-08-09 while fixing it. See [[defect_entries_go_stale]].

  **The search-execution case is reachable in ordinary use, on every study type.** `db/src/db/models/search_exec.py` has **no** unique constraint scoping executions to a study — its only `UniqueConstraint` is on `search_metrics` — so two completed rows are perfectly legal, and a full search **plus a snowball** produces exactly that (TREF9 made `run_snowball` mark its own `SearchExecution` completed, which is correct, and which makes this easier to reach). The moment a study runs both, `GET /studies/{id}` raises and the workspace cannot compute its unlocked phases at all.

  Fix by asking the question actually being asked — existence, not uniqueness: `select(...).limit(1)` with `scalar_one_or_none()`, or `select(func.count())`. The protocol lookups differ from the search ones: for `ReviewProtocol` / `RapidReviewProtocol` / `TertiaryStudyProtocol` a second row per study may be a genuine data defect worth surfacing rather than silently taking the first — decide per call site rather than applying `.limit(1)` everywhere by reflex.

  > Found by the TFIX9 agent, which hit it while building a fixture and **worked around it** by reusing one execution rather than reporting it as blocking — the comment it left at `test_slr_phase_gate.py:98` documents the bug inside the fixture that avoids it. A workaround in a test is a defect nobody has to look at: the fixture went green and the bug stayed live.

  > **Fixed 2026-08-09.** `.limit(1)` at all four sites, because every one is an existence check —
  > the selected row is discarded — so no per-site judgement was needed after all. The four
  > uniqueness-protected calls are deliberately left bare.
  >
  > **The Rapid case was the worst and I had ranked it last.** `RRNarrativeSynthesisSection` is
  > `UniqueConstraint(study_id, rq_index)` — one row per research question — so two completed
  > sections is the _ordinary_ path for any multi-RQ review, not a rare combination. The
  > search-execution cases need a full search plus a snowball.
  >
  > **Why this was invisible in the Rapid suite**: every existing phase-5 test there stubs
  > `session.execute` and returns a `MagicMock` whose `scalar_one_or_none` yields whatever it is
  > told. A mocked result never raises `MultipleResultsFound` however many rows the real query
  > would match, so those tests assert that the code _calls_ the method, not that the query behind
  > it is correct. The SMS gate had a real-session test and reproduced the failure on the first
  > run. Two real-session tests added here; `db.models.search` / `db.models.search_exec` had to be
  > registered in that module for the tables to exist at all.
  >
  > Both reproductions proven RED by temporarily removing the limit —
  > `sqlalchemy.exc.MultipleResultsFound: Multiple rows were found when one or none was required`.
  > Backend 1194 → 1197.

- [x] TFIX10 **The SMS phase gate admits extractions no human has looked at.** `backend/src/backend/services/phase_gate.py:85` unlocks phases 4 and 5 on `DataExtraction.extraction_status != ExtractionStatus.PENDING`. That set includes **`ai_complete`** — a record the AI pre-fill wrote and no reviewer has touched. So an SMS study can reach reporting on wholly unreviewed AI output. `01-slr.md` §2.4 is the corpus's sharpest warning for a platform like this one: extracting without checking whether a study used an invalid metric yields results _"very quickly but will be wrong"_ — _"It does not forbid automation; it forbids extraction decoupled from appraisal."_ Gating on `!= pending` is exactly that decoupling. Narrow the SMS gate the way TFIX8 narrows Tertiary's: accept `human_reviewed` and `validated`, not `ai_complete`
  - Found while deciding TFIX8, by asking why Tertiary should _not_ simply copy the SMS precedent. The precedent turned out to be the weaker of the two — which is the argument for never treating in-repo consistency as evidence of correctness
  - Related and separate: `ExtractionStatus.VALIDATED` is **never assigned anywhere in `backend/src`** — only read in filters. The general extraction lifecycle has the same dead terminal state TFIX8 found in the tertiary one

  **Fixed 2026-08-09.** `phase_gate.py` now reads `extraction_status.in_([VALIDATED, HUMAN_REVIEWED])`.
  `validated` is kept admissible even though nothing writes it: a status ranked above
  `human_reviewed` must not be *less* able to unlock a phase than the one below it.

  > **The one-line fix was not sufficient, and shipping it alone would have recreated TFIX9.**
  > Tracing who *writes* each status — rather than trusting this entry — turned up the reason:
  >
  > | Status | Written by |
  > | ------ | ---------- |
  > | `ai_complete` | `extraction_job.py:222`, unattended |
  > | `human_reviewed` | `extractions.py:404` — **only when a PATCH changes a field value** |
  > | `validated` | nothing, anywhere |
  >
  > So a reviewer who read an AI pre-fill and **agreed with it** changed nothing, and the record
  > stayed `ai_complete` for ever. Gate on `human_reviewed` alone and the platform asks "did
  > somebody *edit* the AI?" while claiming to ask "did somebody *check* it" — and pays for a
  > token edit that invents a disagreement the reviewer never had. Appraisal that confirms is
  > still appraisal. Worse, the only writer of `human_reviewed` sits behind `ExtractionView`,
  > which the reachability audit lists as unreachable, so phases 4 and 5 would have become
  > **unsatisfiable through the UI** — TFIX9's defect exactly, one gate over.
  >
  > Delivered as two halves:
  >
  > 1. `phase_gate.py` narrowed, matching `tertiary_phase_gate.py` (TFIX8).
  > 2. New `POST /api/v1/studies/{id}/extractions/{eid}/review` recording appraisal that changes
  >    nothing — `version_id` optimistic locking and a 409 identical to PATCH's, 422 on a
  >    `pending` record (no extracted data to appraise), idempotent so a repeated click cannot
  >    bump `version_id` out from under another member's open edit form. It is the first writer
  >    of `validated_by_reviewer_id`, a column both extraction APIs already read back and nothing
  >    had ever populated. A "Mark reviewed" control in `ExtractionView` calls it, shown only for
  >    `ai_complete`, alongside a line stating that reporting stays locked until an extraction
  >    has been appraised.
  >
  > The endpoint deliberately accepts **only** `version_id`. One that could confirm *and* edit
  > would let "confirmed as written" and "rewritten" arrive as a single indistinguishable event.
  >
  > **Reachability is unchanged at 7 and the gate is still UI-unsatisfiable until US3 lands** —
  > `ExtractionPage`/`ExtractionView` are two of the seven, and **T030** mounts them. That is an
  > ordering dependency, not a regression: phases 4 and 5 currently render "will be available in
  > a future sprint" placeholders (**T032** deletes them), so nothing of value is behind the gate
  > yet. The backend contract is complete and tested; the button is wired to a component US3
  > mounts.
  >
  > Three tests in `test_phase_gate.py` seeded `AI_COMPLETE` as their stand-in for "non-pending".
  > Two of them are TFIX1's cross-study isolation guards, and leaving them would have kept them
  > green for the **new** reason (inadmissible status) rather than the one they exist to check
  > (wrong study) — a passing test quietly losing its coverage. Both were re-seeded with
  > `HUMAN_REVIEWED`.

- [ ] TFIX14 **Every downstream consumer of extractions still aggregates `ai_complete`.** Found while fixing TFIX10, by asking what the narrowed gate actually protects. `results_job.py:118`, `quality_job.py:168`, `validity_job.py:163` and `export.py:86` each filter `extraction_status.in_([AI_COMPLETE, VALIDATED, HUMAN_REVIEWED])`. So the gate now requires **one** appraised extraction to open reporting, and reporting then computes over **all** of them — a study that AI-extracted 200 papers and had one checked reports charts, quality figures and validity threats derived from 199 unread records. This is the same `01-slr.md` §2.4 clause TFIX10 turns on, applied one layer down: the gate governs *entry* to reporting, these four govern *what reporting says*.
  - **Not fixed under TFIX10 because the remedy is a choice, not a correction.** Excluding `ai_complete` outright would make a large study's first report near-empty, which may be honest or may be useless; labelling each figure with its appraised/total denominator keeps the data and states its provenance; a third option gates the export but not the working charts. Picking one silently, inside a task scoped to a phase gate, would be deciding what the platform's numbers *mean* without saying so
  - `08-extraction-and-synthesis.md` should be read before choosing — this entry cites §2.4 of `01-slr.md` only, which is about extraction, not about what synthesis may consume

- [x] TFIX11 **Single-reviewer bias is declared for one study type out of four, and its prescribed mitigation does not exist.** A lone researcher — or a study with a single reviewer — is a legitimate configuration, not an error. The corpus's position is disclosure plus mitigation, never prohibition: `04-tertiary.md` records that _"One person seeing every paper is a known bias, **accepted deliberately**… Record the trade-off rather than pretending it does not exist,"_ and `01-slr.md` §2.4 names the remedy — _"A lone researcher uses supervisor cross-check on a sample, or test–retest."_ Two gaps:
  1. **The threat is recorded only for Rapid Reviews.** `rr_protocol_service.set_single_reviewer_mode` creates an `RRThreatToValidity` of type `SINGLE_REVIEWER` and surfaces it through `SingleReviewerWarningBanner`. SLR, SMS and Tertiary have no equivalent, so on three of four study types the bias is accepted silently — precisely what the corpus says not to do.
  2. **Test-retest does not cover the step that needs it.** `frontend/src/components/phase2/TestRetest.tsx` is _search-string_ test-retest — iterations, `test_set_recall`, adequacy judgement. There is no test-retest for **screening** or **extraction** consistency, which is the mitigation `01-slr.md` actually prescribes for a lone researcher.

  > The right shape is a **disclosure**, not a gate. The platform must not block a single-reviewer study from proceeding; it must make the study say so, and offer the consistency check that makes the claim defensible. Blocking would contradict the corpus; staying silent already does.

  **Fixed 2026-08-09 — the disclosure half. The test-retest half is deliberately deferred.**
  Four decisions were put to the user before any code was written; all four recommendations were
  accepted.

  > **Reading `09-threats-to-validity.md` changed the shape of the fix, and this entry did not cite
  > it.** The entry's two quotes both verify verbatim — `04-tertiary.md` 259-261 and `01-slr.md`
  > 256-257 — but the chapter that governs the *shape of a threat record* was never consulted when
  > the entry was written, and it contradicts the entry's prescription in three places:
  >
  > 1. **"Copy the Rapid pattern to the other three" would have imported the wrong framework.**
  >    Ch.09 255-262 assigns frameworks *by study type*: Rapid gets **Cartaxo's disclosure regime**
  >    ("every methodological concession is itself a threat"), SLR/SMS/Tertiary get **Ampatzoglou's
  >    catalogue**. `RRThreatType`'s members — `year_range`, `language`, `qa_skipped` — are Cartaxo
  >    concessions, a different vocabulary answering a different question.
  > 2. **The model the entry says to copy is itself incomplete.** Ampatzoglou's **step 4** requires
  >    every identified threat to carry *either* a mitigation *or* an explicit acknowledgement, and
  >    ch.09 173 singles it out as the enforceable one — "an identified threat with neither … is an
  >    incomplete study". `RRThreatToValidity` has **neither column**. Copying it three more times
  >    would have tripled that omission.
  > 3. **Single-reviewer bias is three threats, not one.** Ch.09 catalogues them at three separate
  >    steps: **TV7** (selection), **TV13.4** (unverified extraction) and **TV16** (researcher bias,
  >    defined as "including **only one author doing the synthesis**"). That is also why `01-slr.md`
  >    prescribes test-retest *twice* — 2.2 for screening, 2.4 for extraction. One generic "single
  >    reviewer" row would have collapsed three distinct mitigations into one box.
  >
  > **Decisions taken** (user-approved, recommendations in each case):
  >
  > | Decision | Choice | Why |
  > | -------- | ------ | --- |
  > | Scope | Disclosure only | The disclosure is the correctness defect; test-retest is a tracked feature (**G4** screening, **G84** extraction) with its own sizing |
  > | Threat record | New study-generic table | Keeps Cartaxo and Ampatzoglou apart, and adds the step-4 columns the Rapid model lacks |
  > | Detection | Derived from `Reviewer` rows | Cannot be forgotten, and is knowable *before* screening — a flag can go stale, and observed-decision counting is only knowable too late to act on |
  > | Enforcement | Report/export only | Ch.09 makes step 4 enforceable; TFIX11 forbids blocking progress. Gating publication satisfies both, and acknowledging always clears it |
  >
  > **Delivered.** `db/models/validity.py` (`StudyValidityThreat`, `ValidityThreatId`,
  > `ValidityCategory`) + migration **0022**; `validity_threat_service` (derive, list, address,
  > report gate); `GET`/`PATCH /api/v1/studies/{id}/validity/threats` on the existing validity
  > router; `ValidityThreatPanel` mounted on the SLR export page, the Tertiary report page and the
  > SMS results export tab. Reachability **unchanged at 7** — the panel is mounted, not orphaned.
  >
  > **`is_addressed` rejects whitespace.** A gate a space bar satisfies is not a gate. It is a
  > Python property rather than a column so that the API, the panel and the report gate cannot
  > drift apart about what "addressed" means; the gate filters in Python for the same reason.
  >
  > **`is_applicable` is a flag, not a delete.** Human `Reviewer` rows are created *lazily* — the
  > first time a member records a decision — so a study genuinely crosses from one reviewer to two
  > long after screening starts. Deleting on that transition would discard the text the first
  > reviewer wrote, and lose it for good if the study dropped back to one. Derivation therefore
  > runs on *read* and is idempotent, which the `(study_id, threat_id)` unique constraint enforces.
  >
  > **A trap found while wiring the frontend.** `TertiaryReportPage` fetches its report with
  > `useQuery` and returns early on error — and the gate makes that very GET return 409. Mounted
  > naïvely, an unaddressed threat would have rendered "Failed to load report" while the early
  > return hid the only control that fixes it. **A gate on a GET that a page uses to render itself
  > can conceal its own remedy.** The panel is mounted on both branches there. SLR and SMS do not
  > have this shape — their exports are button actions, so the page still renders.
  >
  > **Zero reviewers derives nothing.** Treating "no reviewer rows yet" as single-reviewer would
  > announce the bias before anyone had the chance to introduce it. **AI reviewers do not count**
  > as a second reviewer either: the mitigations the corpus names are human acts, so counting an
  > agent would let the platform declare the bias resolved by adding automation to it.
  >
  > One existing test needed its harness widened: `slr/__tests__/ReportPage.test.tsx` rendered the
  > page with no `QueryClientProvider`, which the newly mounted panel requires. Assertions
  > unchanged; the mock returns the empty-threat-list case.
  >
  > **Still open, and named as such:** gap 2 of this entry. There is still no test-retest for
  > screening (**G4**) or extraction (**G84**), so a single-reviewer study can currently only
  > *acknowledge* these three threats, never *mitigate* them. That is a valid step-4 outcome and
  > the study is never blocked — but it is the weaker branch, and the corpus prescribes the other.

  **Step 1 completed 2026-08-10, after the first commit shipped without it.**

  > The first pass enforced Ampatzoglou's **step 4** and did not implement **step 1** — "create a
  > dedicated threats-to-validity section in … the final report". Checking rather than assuming
  > found the consequence, and it was not cosmetic: **the gate compelled a researcher to record a
  > mitigation or an acknowledgement, and then published neither.**
  >
  > | Report | Before |
  > | ------ | ------ |
  > | SLR | `_build_validity()` returned a fixed sentence reading **no study data at all** |
  > | Tertiary | **No threats or validity section existed** |
  > | SMS export | Archive carried charts and extractions, no threats |
  >
  > The SLR boilerplate was worse than absent. It asserted *"publication bias, database coverage
  > limitations, and inter-rater variability during screening"* for every study — and
  > **inter-rater variability is false for exactly the study that trips the gate**, which has one
  > rater and therefore no inter-rater variability to report. A canned threat profile that can
  > contradict the derived one is a fabrication, not a placeholder.
  >
  > `build_threats_section` now renders catalogue id, reporting category, description and the
  > step-4 outcome, shared by all three surfaces. The two outcomes are **labelled differently** —
  > "Mitigation:" versus "Acknowledged as not fully mitigated:" — because collapsing them would let
  > a reader take "accepted, not mitigated" for "handled", which is the misreading step 4 exists to
  > prevent.
  >
  > **Every section states that its threats were derived automatically.** The platform encodes 3 of
  > ~22 catalogue entries, so it does *not* satisfy **step 3** ("check every threat for whether it
  > pertains to the study"). A section that listed three threats without saying so would claim a
  > completeness it has not earned — the exact failure the chapter's closing caution names.
  >
  > `TertiaryReport` gained a required `threats_to_validity` field, carried into JSON, CSV and
  > Markdown, with the frontend Zod schema made **required** to match: a stale backend should fail
  > loudly rather than silently drop the section. The SMS export is a data archive rather than a
  > narrative report, so it gets the section as a payload key — the export gate refuses to run
  > while a threat is unaddressed, and an archive omitting what *was* addressed makes that refusal
  > pointless.
  >
  > Backend 1288 → 1295, frontend 1394 → 1395.

  **Two conformance gaps remain open, deliberately. Both are carried forward as TFIX15.**

- [ ] TFIX15 **The threat catalogue is three entries deep, and the Rapid map records good practice as a threat.** Both found while closing TFIX11 — the first by asking what the platform does *not* check, the second by verifying a claim rather than repeating it. `09-threats-to-validity.md` and `03-rapid-review.md` are the sources; neither part is a matter of taste.

  1. **Ampatzoglou's step 3 is not performed.** The step is _"**Check every threat** for whether it pertains to the study"_, against the TV1–TV22 catalogue. `ValidityThreatId` encodes **three** entries — TV7, TV13.4 and TV16 — because those are the only ones the platform currently derives from configuration. Every generated section says so in as many words, so no report *claims* the completeness it lacks, but the check itself is absent. The chapter is explicit that the fix is derivation rather than a form: threats _"should be **derived from the protocol configuration** rather than presented as a flat checklist … This chapter supplies the full mapping"_ (ch.09 ⚙ IMPLEMENTATION, §Category 1). Closing this means partitioning TV1–TV22 into what the platform can compute — search-source counts, language limits, date windows, reviewer counts, whether QA ran, whether synthesis was formal — and what can only be *asked* of the author, then deriving the first set and prompting for the second.
     - Ch.09 also supplies a **mutual-exclusivity rule that must be encoded, not just listed**: if digital-library selection is used, TV1.3 (venue selection) _does not apply_ — "normally only one of the two strategies is chosen" — with a quasi-gold-standard exception where both apply, while TV1.1 (string construction) applies in **both** cases. A flat checklist cannot express that; a derivation rule can, which is the chapter's own argument for deriving.

  2. **The Rapid concession→threat map is inverted in one row and missing three others.** `03-rapid-review.md` §"Threats to validity in an RR" gives the full mapping and marks one row **"Explicitly NOT a threat — good practice"**: _narrowing criteria to the practitioner's context_. Its ⚙ IMPLEMENTATION note names this as load-bearing — the chapter supplies _"the full mapping, **and the exception that must not generate a threat**"_. `rr_protocol_service._auto_create_threats` does the opposite: it walks `protocol.context_restrictions` and creates a `CONTEXT_RESTRICTION` threat for **every** entry. So a Rapid Review that scopes itself to its practitioner's context — the thing Cartaxo calls good practice — has that recorded against it as a threat to validity, and rendered under "Limitations & Threats to Validity" in the published briefing.
     - Separately, three of the eight mapped concessions have **no `RRThreatType` member at all**: title-only first screening pass → _false negatives_; narrative synthesis → _limited synthesis rigour_; excluding studies with missing data → _missing-data exclusions_. Under a regime whose whole content is "every methodological concession is itself a threat that must be recorded", an unrecordable concession is a hole in the regime.

  > **A correction to what closing TFIX11 first reported.** That work claimed Rapid was non-conformant because `RRThreatToValidity` has no mitigation or acknowledgement column. Checking `03-rapid-review.md` rather than reasoning from Ampatzoglou shows that is **wrong**. Cartaxo defines no taxonomy and requires no per-threat mitigation: _"every methodological concession is itself a threat that must be recorded. All concessions go in the protocol; the report carries a disclaimer about methodological limitations, with detail deferred to the protocol"_ — the concession record **is** the acknowledgement. And the disclaimer exists: `evidence_briefing.html.j2:282` renders a "Limitations & Threats to Validity" block over those records. Rapid does not need step-4 columns. It needs its map corrected.

  > **Do not fold part 2 into part 1.** They look like one "threats are incomplete" task and are not. Part 1 extends a catalogue the platform *chose* to encode partially; part 2 fixes a mapping that contradicts its own source. Part 2 also carries a data question part 1 does not: existing studies already have `CONTEXT_RESTRICTION` rows written under the wrong rule, so the remedy has to say what happens to them — the safe reading is that they were never threats, but deleting rows a researcher may have cited in a published briefing is a decision, not a migration.

---

## Phase 3: User Story 1 — Record a screening decision (Priority: P1) 🎯 MVP

**Goal**: A reviewer can select a paper, see prior decisions and disagreement, and record accept / reject / duplicate with reasons and an annotation.

**Independent test**: Open a study with candidate papers, select one, submit an accept decision with a reason, and confirm the queue reflects the new status — with nothing else in this feature present.

### Tests for User Story 1 ⚠️ write first, must fail

- [x] T007 [P] [US1] Integration test in `backend/tests/integration/test_papers_decisions.py`: a submission whose `observed_status` differs from the stored status returns 409 carrying both statuses (FR-025, FR-027)
- [x] T008 [P] [US1] Integration test in `backend/tests/integration/test_papers_decisions.py`: a second decision by the same reviewer without `overrides_decision_id` returns 409 carrying their earlier decision (FR-022)
- [x] T009 [P] [US1] Integration test in `backend/tests/integration/test_papers_decisions.py`: resubmitting with `overrides_decision_id` succeeds, sets `is_override`, retains the original, and does **not** raise the paper's conflict flag (FR-022)
- [x] T010 [US1] Migrate the ~10 existing `POST …/decisions` calls in `backend/tests/integration/test_papers_decisions.py` to supply `observed_status` (C5 — required field, so existing callers stop working; migrating them is part of this task, not follow-up)
- [x] T011 [P] [US1] Component test in `frontend/src/components/studies/__tests__/ScreeningView.test.tsx`: selecting a queue row opens the reviewer panel for that candidate
- [x] T012 [P] [US1] Component test in `frontend/src/components/studies/__tests__/ScreeningView.test.tsx`: reasons and annotation already entered survive a re-confirmation prompt (FR-025)

### Implementation for User Story 1

- [x] T013 [US1] Add required `observed_status` and the stale-state 409 to `DecisionRequest` and `submit_decision` in `backend/src/backend/api/v1/papers.py` (FR-025, FR-027)
- [x] T014 [US1] Add the unacknowledged-prior-decision 409 to `submit_decision` in `backend/src/backend/api/v1/papers.py`, returning the reviewer's earlier decision in the payload (FR-022)
- [x] T015 [US1] Create `frontend/src/components/studies/ScreeningView.tsx` composing `PaperQueue`, selection state, `ReviewerPanel`, `PaperCard`, and `MetricsDashboard` (≤100 JSX lines — decompose if it grows)
- [x] T016 [US1] Mount `ScreeningView` at phase 3 for the SMS branch and inside `SLRScreeningView` in `frontend/src/pages/StudyPage.tsx`, so both paths gain decisions from one change (FR-006)
- [x] T017 [US1] Send `observed_status` and `overrides_decision_id` from the reviewer panel in `frontend/src/components/phase2/ReviewerPanel.tsx`, preserving entered input across a re-confirmation
- [x] T018 [US1] Remove `test.fixme` from the three cases in `frontend/e2e/screen-paper.spec.ts` and make them assert real behaviour (no `isVisible()` guards, no conditional skips — Principle VI). **Two of the three, not three.** The accept/reject cases are un-fixme-able now that `ReviewerPanel` is mounted. The third — `job progress panel is visible during a screening run` — clicks a `/run screening/` button that US1 does not deliver; it is the re-screen control from **T049**. It stays `test.fixme` and its comment is re-pointed from G18 to US4/T049, which is the form Principle VI permits (`test.fixme` plus a gap citation, per T052). Blocked on **TFIX4**
- [x] T019 [US1] Extend `frontend/e2e/screen-paper.spec.ts` to record a decision end-to-end on an SMS study and on an SLR study against a live backend (FR-021). Blocked on **TFIX4**, and needs one fixture that Phase 2 does not create: **there is no seeded SLR study**. `slr-workflow.spec.ts` builds one through the wizard, but a wizard-created study sits at phase 1 with no candidates, so screening is locked and there is nothing to decide on. Add `_seed_slr_study` to `scripts/seed_e2e_user.py` — SLR type, PICO, completed search execution, pending candidates — mirroring `_seed_main_study`
  - Delivered with **three** fixture additions the task did not anticipate, each forced by something only running the spec revealed. (a) The SLR gate does not read PICO at all — `slr_phase_gate` wants a **validated `ReviewProtocol`** for phase 2 and a completed `SearchExecution` for phase 3 — so `ensure_validated_review_protocol` replaces the PICO the task called for. (b) `ReviewerPanel` renders its reason selector only for a study that already has criteria, so `ensure_criteria` seeds them on both screening studies; without it the spec could record a decision but never a _reason_, which is half of FR-002. (c) `reset_screening_queue` returns the queue candidates to pending, because a second run of the spec otherwise hits the 409 this feature itself added — see **TREF10** below.

**Checkpoint**: A reviewer can screen papers on SMS and SLR studies. Agreement measurement becomes exercisable. Tertiary is covered in Phase 4, which is where that study type becomes reachable.

> **Status 2026-08-08 — US1 complete, T007–T019.**
> The reachability audit moved **23 → 20**: `ReviewerPanel`, `PaperCard` and `MetricsDashboard`
> are now reached through `ScreeningView` at phase 3 for SMS, SLR and Rapid. Backend 1164 tests
> pass, frontend 1364 across 127 files, 9/9 pre-commit hooks, eslint and prettier clean.
>
> The e2e was deliberately held until TFIX4 landed. `ReviewerPanel` required the reviewer to type
> their numeric reviewer id by hand, so an e2e written before that would have typed a raw database
> id — a test passing against a UI no researcher can actually use, which is the exact "green and
> wrong" outcome this feature exists to remove.
>
> **e2e result**: full suite **87 passed, 6 skipped** against a live PostgreSQL and backend.
> `screen-paper.spec.ts` goes from 5 tests (3 `test.fixme`) to 8 (1 `test.fixme`, re-pointed at
> T049). Both decision tests record a real decision — outcome, criterion reason, and annotation —
> and assert the queue status changes without further action (FR-003) and that the annotation
> comes back from the API into the paper card, which is what makes it a stored column (TFIX3)
> rather than form state.
>
> **Three things only running it could have told us**, each recorded because each contradicted a
> reasonable assumption written down beforehand:
>
> 1. **The SLR phase gate ignores PICO.** T019 specified "SLR type, PICO, completed search
>    execution". `slr_phase_gate.get_slr_unlocked_phases` never reads PICO — phase 2 needs a
>    **validated `ReviewProtocol`**, and without it the study sits at `[1]` and the Screening tab
>    stays disabled. Seeding PICO as specified would have produced a locked study and an e2e that
>    could not start.
> 2. **A "green" health check proved nothing.** A leftover `uvicorn` from 2026-08-06 still held
>    port 8000, so `curl /health` returned 200 from **stale code** and the first spec run measured
>    a two-day-old backend. It even showed `GET /groups/{id}/studies` returning duplicate rows,
>    which read exactly like a live join-fan-out defect; HEAD has no such defect — the filter is
>    present, the compiled SQL carries it, and a direct call returns the right count. Note that
>    uvicorn logs `Application startup complete` **before** it binds, so the bind failure appears
>    _after_ the success line and is easy to scroll past.
> 3. **`VITE_API_URL` is not just a proxy target.** `frontend/src/services/api.ts` uses it as the
>    client's base URL too, and the backend registers no `CORSMiddleware`, so pointing it at a
>    second backend port fails preflight in the browser while `curl` through the proxy still
>    returns 200. In dev the backend must be on the port the proxy defaults to.

- [x] TREF10 [P] Split `scripts/seed_e2e_user.py` (783 lines, against the 800 maximum) — the ten generic row factories move to `scripts/seed_helpers.py`, leaving the study-specific fixtures and the entry point behind. Landed as its own `refactor:` commit before T019's fixture, per Principle IV, because that fixture would have carried the file to ~900 lines. `_ensure_*` / `_upsert_*` become `ensure_*` / `upsert_*`: a leading underscore claims module-private, and they are now imported across modules

- [x] TFIX6 **A repeated e2e run defeats itself.** `screen-paper.spec.ts` records real decisions, and the suite is run repeatedly against a database it also writes to — so run 2 submits against a candidate that already holds the reviewer's decision and gets the 409 `unacknowledged_prior_decision` that T014 added. Handling both outcomes would need an `isVisible()` branch, which Principle VI forbids. Fixed in the fixture, not the spec: `reset_screening_queue` clears decisions on the queue candidates and returns them to pending, following the precedent already in the script — the TOTP counters are cleared on every run because the lockout spec deliberately locks its account. Scoped to the queue DOIs so the conflict fixture's two disagreeing decisions, which are the subject of their own assertions, survive. **Verified by observation, not by argument**: re-running the spec without re-seeding fails exactly the two decision tests and nothing else

---

## Phase 4: User Story 2 — Conduct a Tertiary Study (Priority: P2)

**Goal**: A Tertiary study opens its own workspace and its five phases, and a seed study can be imported from the owning research group.

**Independent test**: Create a Tertiary study, open it, confirm the tertiary workspace appears, then import a seed study from the group.

### Tests for User Story 2 ⚠️ write first, must fail

- [x] T020 [P] [US2] Integration test in `backend/tests/integration/test_studies.py`: `GET /studies/{id}` returns `research_group_id` matching the owning group, for **every** study type (FR-010)
  - **`test_studies.py` does not exist** — the file is `backend/tests/integration/test_studies_router.py`. Added there as `TestGetStudyResearchGroupId`, parametrised over `list(StudyType)` rather than a hand-written list, so a study type added later is covered without anyone remembering to extend it. RED for the right reason: `201` on create, `200` on GET, then `KeyError: 'research_group_id'` — not an import, fixture or 404 failure
- [x] T021 [P] [US2] Component test in `frontend/src/pages/__tests__/StudyPage.dispatch.test.tsx`: a study whose type is Tertiary renders the tertiary workspace, not the SMS phase panels (FR-007)
  - Replaces the two `Tertiary (current defect — see G19)` cases the file was written to carry until this task. RED for the right reason: the DOM dump showed `pico-form` and `seed-papers` still rendering for a Tertiary study, and all 8 of `StudyPage`'s own `Phase N:` tabs present. The other 24 cases in the file were untouched and stayed green

### Implementation for User Story 2

- [x] T022 [US2] Add `research_group_id: int` to `StudyDetail` and populate it in `backend/src/backend/api/v1/studies/__init__.py` (FR-009, FR-010 — seed import cannot function without it)
  - **The type is `int | None`, not `int`.** `db/src/db/models/__init__.py:256` declares `Mapped[int | None]` with `ForeignKey(..., ondelete="SET NULL")`, so deleting a research group nulls the field on every study that belonged to it. Populated at **all three** `return StudyDetail(` sites — create, get, patch. A missed site would not fail at import or type-check: the field is required, so it raises `ValidationError` at request time on one endpoint only, and `create_study` / `patch_study` are far less covered than `get_study`
- [x] T023 [P] [US2] Add `research_group_id: number` to the `StudyDetail` interface in `frontend/src/pages/StudyPage.tsx`, mirroring the backend model
  - **The interface is not in `StudyPage.tsx`** — that file imports the type. It is declared in `frontend/src/components/studies/studyTypeDispatch.tsx:55`, and is typed `number | null` to mirror the nullable column
- [x] T024 [US2] Register Tertiary in `frontend/src/components/studies/studyTypeDispatch.tsx` so `StudyPage` renders its header then delegates wholesale to `TertiaryStudyPage`, passing `studyId`, `unlockedPhases`, and `groupId` (R7 — takeover, not per-phase dispatch)
  - **Audit 20 → 8.** Still **exit 1**, and correctly so — the script exits 0 only at zero
    unreachable, which is T055's definition of done, not T024's. (Recorded because this entry first
    read "exit 0": `$?` was sampled after a pipe into `tail`, so it reported `tail`'s status rather
    than the script's. Any audit check written as `audit.py | tail; echo $?` measures nothing.)
    The eight that remain are US3's four (`ExtractionPage`, `ExtractionView`, `ValidityForm`,
    `QualityReport`), TFIX5's `QualityScoreForm`, `TertiaryQAGuidancePanel`, and the two G21
    modules. Twelve modules became reachable from one dispatch entry: `TertiaryStudyPage`, `TertiaryReportPage`, four `components/tertiary/*`, three `hooks/tertiary/*`, three `services/tertiary/*`. Frontend suite 1365 tests green
  - A takeover needs a **second** map, not a `STUDY_TYPE_PHASES` entry: that map is keyed by phase, and `StudyPage` renders `PHASE_META` unconditionally, so a phase entry would have left its own Phase 1–7 strip above the workspace's own — the .
  
  two phase bars R7 rejects. `STUDY_TYPE_TAKEOVER` is consulted _before_ the tab strip is built
  - **"Wholesale" was refined to exclude phase 0** — see the dated note on R7 in `research.md`. A literal reading deletes the tab strip, and phase 0 is the Protocol tab; `assign_default_protocol` runs for every study type at creation, so every Tertiary study would have had a `ProtocolGraph` and `ExecutionStateView` no user could open — closing G19 by opening a gap of the same kind. Takeover types get a two-button strip, **Protocol Graph** and **Workspace**, whose labels also avoid colliding with `TertiaryStudyPage`'s own `Phase 1: Protocol`
  - `groupId` is `number | null` and **not** coerced with `?? 0`; `Phase2Panel` explains the absence, because the group is needed by phase 2 alone. Coercing would have rebuilt the `reviewerId={0}` shape TFIX5 catalogues
  - `STUDY_TYPE_TAKEOVER` is typed `Partial<Record<string, StudyTakeover>>`: this repo does not set `noUncheckedIndexedAccess`, so a plain `Record` makes indexing always-defined and `tsc` rejects the truthiness check with `TS2774`. `Partial` is also the honest type — most study types have no takeover
- [x] T025 [US2] Create `frontend/e2e/tertiary-workflow.spec.ts` covering protocol → seed import → screening → extraction → report against a live backend (FR-021 — this workflow has no e2e coverage today because it could not be reached)
  - Delivered in `55d116b` as one sequential test with five `test.step`s, one per leg. Full e2e **89 passed, 6 skipped**, up from 87/6
  - **The extraction and report legs pass because the fixture opened the gate, not the UI** — stated in the spec's own docblock so the result is never read as reachability evidence. Half of that has since changed: **TFIX8** made phase 5 reachable through the UI, so the seeded `validated` extractions now exercise a value the gate genuinely accepts. Phase 4 still depends on the seeded `QualityAssessmentScore`, because Tertiary has no quality-assessment UI — the open remainder of **TFIX7**
  - Found while writing it: `TertiaryStudyProtocol.synthesis_approach` enumerated three of `SynthesisApproach`'s five members, so saving "Narrative" — which the form offers — wrote successfully and then raised `LookupError` on every read, including its own `db.refresh()`. Fixed separately in `703ed13` with a regression test, since it is a production defect rather than feature work
- [x] T026 [US2] Extend `frontend/e2e/screen-paper.spec.ts` to record a decision on a Tertiary study, completing FR-006 across all three screening study types
  - Needed a component change the task did not anticipate: `TertiaryStudyPage`'s `Phase3Panel` rendered a bare `PaperQueue`, and `ReviewerPanel` — the only control that records a decision — arrives via `ScreeningView`. **No control on a Tertiary study could record a decision at all**, so the e2e had nothing to click. `Phase3Panel` now renders `ScreeningView`, the same composition SMS and SLR reach screening through
  - **Runs against its own study**, `E2E Tertiary Screening Study` rather than `E2E Tertiary Seed Study`. Both specs drive a Tertiary study to phase 3, protocol validation is a one-way transition, and `screen-paper` sorts before `tertiary-workflow` alphabetically — so sharing one study raced them reproducibly, confirmed even at `--workers=1`

  > **Both were finished in `55d116b` on 2026-08-08 and left unticked here until 2026-08-09.** T020–T024 were marked off and these two were missed. A third form of the staleness this file keeps exhibiting: TFIX7's _content_ went stale, TFIX12's _scope_ was overstated, and here the _status_ was simply wrong. Same cause each time — the ledger is maintained by hand and nothing checks it against the code. See [[defect_entries_go_stale]].

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
- [ ] T041 [P] [US4] Migration test in `db/tests/integration/test_migrations.py`: `0021` upgrades and downgrades cleanly — **against PostgreSQL**, since `0014` alters a constraint outside batch mode and SQLite refuses it outright (TFIX2)

### Implementation for User Story 4

- [ ] T042 [US4] Add `RESCREEN = "rescreen"` to `JobType` in `db/src/db/models/jobs.py` (R1)
- [ ] T043 [US4] Create Alembic migration `db/alembic/versions/0022_rescreen_job_type.py` adding the value to `background_job_type_enum`, with a working `downgrade()` (R1 — the PRD's "no migration" claim is wrong on this point). **Revision `0022`, revising `0021`.** This number has now moved twice: planned as `0019`, corrected to `0021` when `0019_candidate_citation_intent` and `0020_paper_decision_annotation` took those ids, and corrected again to `0022` when TFIX7 part 3 landed `0021_dare_quality_instrument` on 2026-08-09. Alembic rejects a duplicate revision id, so `plan.md`, `data-model.md`, `research.md` R1 and `CLAUDE.md` are all stale on this point and **`(cd db && uv run alembic heads)` is the only source worth trusting** — it currently returns `0021 (head)`
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
- [ ] TDOC7 [P] Add a `MEMORY.md` entry if implementation surfaces a further non-obvious trap, per that file's own guidance. **Three are already owed, found during US2:**
  1. **"Reachable" and "navigable" are different properties, and only one has an instrument.**
     `scripts/audit_unreachable_frontend.py` walks the import graph from `main.tsx`; it answers
     _is this module imported_. It cannot answer _can a user get there_. After T024 the audit
     counts `TertiaryExtractionForm`, `TertiaryReportPage` and `LandscapeSummarySection` as
     reachable — correctly by its own definition — while **TFIX7** and **TFIX8** keep every user
     out of the phases that render them. A green audit is necessary and not sufficient; the
     complement is an e2e that actually navigates, which is why FR-021 exists. Note the two
     failures are of different kinds and both invisible to the same tool: TFIX7 is a missing
     writer (nothing imports `QualityScoreForm`, so no `QualityAssessmentScore` can be created),
     TFIX8 is a mismatched literal (`TertiaryExtractionForm` saves `human_reviewed`; the gate
     wants `validated`).

  2. **`unlocked_phases` carries two different numbering schemes.** `StudyPage`'s `PHASE_META`
     runs 0–7, where 0 is the protocol tab; a Tertiary study's gate returns 1–5, and
     `TertiaryStudyPage` labels those `Phase 1: Protocol` … `Phase 5: Synthesis & Report`. One
     field, two vocabularies. Nothing is broken today only because the takeover means the two
     strips never render together — a study type that dispatched per phase _and_ had a five-phase
     gate would mis-index in silence. Anyone adding a study type must decide which scheme it
     speaks before writing a gate.

  3. **`Record<string, T>` indexing is typed as always-defined here.** This repo does not set
     `noUncheckedIndexedAccess`, so `const t = MAP[key]; t ? a : b` fails `tsc` with `TS2774` —
     the compiler calls the check pointless while the runtime value really is `undefined` for
     every unmapped key. Declare such maps `Partial<Record<string, T>>`, which is also the honest
     type. `STUDY_TYPE_PHASES` escapes this only because it is always read through
     `?? DEFAULT_PHASE_MAP` and so never asks whether the lookup succeeded.

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

| Phase               | Tasks        | Count  |
| ------------------- | ------------ | ------ |
| Refactoring (C1–C3) | TREF1–TREF10 | 10     |
| Setup ✅            | T001–T002    | 2      |
| Foundational ✅     | T003–T006    | 4      |
| Defects found       | TFIX1–TFIX15 | 15     |
| US1 (P1) 🎯 MVP ✅  | T007–T019    | 13     |
| US2 (P2)            | T020–T026    | 7      |
| US3 (P3)            | T027–T033    | 7      |
| US4 (P4)            | T034–T050    | 17     |
| Polish              | T051–T055    | 5      |
| Documentation       | TDOC1–TDOC7  | 7      |
| **Total**           |              | **87** |

TREF1–TREF10, T001–T019 and TFIX1–TFIX4 plus TFIX6 are complete — **the MVP is delivered**: a
reviewer can screen papers on SMS and SLR studies, driven end-to-end by an e2e against a live
backend. TFIX5 is written up but unfixed; US2–US4 and Phase 7 remain.

TFIX2 turned up a further staleness while it was being fixed, corrected in place rather than
given a number of its own: **the rescreen migration is `0021`, not `0019`.**
`0019_candidate_citation_intent` landed on this branch after the plan was written and now holds
head, and alembic rejects a duplicate revision id — confirmed with
`(cd db && uv run alembic heads)` → `0019 (head)`. Corrected on T041, T043, `plan.md`,
`data-model.md`, `quickstart.md`, and `CLAUDE.md`; `research.md` R1 never named a number.
