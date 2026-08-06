# Feature: Wire Up Unreachable Workflows

**Feature ID**: 012-wire-up-unreachable-workflows
**Depends On**: 002-sms-workflow, 009-tertiary-studies-workflow (specs `009`), 011-improve-testing-and-fix-ci
**Reference**: `docs/feature-gaps.md` — G18, G19, G20, and the "Built-but-never-wired audit" section
**Closes**: G18, G19, G20

> **Numbering note.** This document is numbered to follow `specs/` (the last branch is `011-improve-testing-and-fix-ci`), not the `docs/features/` sequence, which stops at `010` and has drifted from the spec numbering. See [README](./README.md).

---

## Overview

Three catalogued gaps share one shape: **the code is finished, tested, and served by a live endpoint — and no user can reach it.** Nothing imports it, or the router does not know it exists.

An import-graph audit of `frontend/src` on 2026-08-06 (`scripts/audit_unreachable_frontend.py`) found 23 of 142 modules unreachable from `main.tsx`. Twenty-one of those fall into the three clusters this feature closes:

| Gap     | Cluster                             | Unreachable modules | Backend status                                                  |
| ------- | ----------------------------------- | ------------------: | --------------------------------------------------------------- |
| **G18** | Screening decisions                 |                   2 | Complete — `POST /studies/{id}/papers/{candidate}/decisions`    |
| **G19** | Tertiary Studies frontend           |                  13 | Complete — 7 `/api/v1/tertiary/*` routes, migration `0017`      |
| **G20** | Extraction, phases 4–5, and metrics |                   6 | Complete — extraction, validity, quality, and metrics endpoints |

This is therefore **not feature work**. No new components, no new database tables, no migration. The deliverable is dispatch wiring, one small backend field, one modest new endpoint, and the end-to-end tests that would have caught the problem in the first place.

The remaining two unreachable modules are G21 (`QualityScoreForm`, `EdgeConditionBuilder`), which are out of scope — see [Non-Goals](#non-goals).

---

## Scope

### Part A — Record a screening decision (G18)

A human reviewer currently has no way to accept, reject, or mark a paper as a duplicate. Phase 3 renders `PaperQueue`, which is read-only.

Two complete components are orphaned:

| Module                                | What it does                                                                                    |
| ------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `components/phase2/ReviewerPanel.tsx` | Accept / reject / duplicate buttons, exclusion-reason selection, annotation; POSTs the decision |
| `components/shared/PaperCard.tsx`     | Renders a paper's decision history and offers conflict resolution when reviewers disagree       |

The backend is finished, including conflict detection (`_detect_conflict`, `backend/src/backend/api/v1/papers.py:223`) and integration coverage in `backend/tests/integration/test_papers_decisions.py`.

**Required behaviour**

- A paper in the Phase 3 queue can be selected; selecting it opens the reviewer panel for that candidate.
- The reviewer can record accept / reject / duplicate with reasons and an annotation, and the queue reflects the new status without a manual refresh.
- Prior decisions on the selected paper, and any conflict between reviewers, are visible at the point of decision.
- Decision recording is available for **SMS, Tertiary, and SLR** studies. SLR reaches Phase 3 through `SLRScreeningView`, which renders the same `PaperQueue`; the selection state and panel belong in a shared component so both paths gain it from one change.

**Interface constraints already settled by the existing code**

Both components take `studyId` and `candidateId` as numbers, so the only new state is _which candidate is selected_. `PaperCard` additionally requires `paperId`, `currentStatus`, `conflictFlag`, and `phaseTag` — all of which `PaperQueue` already holds in the row it renders, so they can be lifted rather than refetched.

**Correction to the gap record.** `docs/feature-gaps.md` states that a screening run cannot be started, and asks for a control that enqueues a screening job. That is wrong in its particulars: `StudyPage.tsx:436` already renders **Run Full Search**, which POSTs to `/studies/{id}/searches` and returns a `job_id` fed to `JobProgressPanel`; `backend/src/backend/jobs/search_job.py` runs `ScreenerAgent` over every candidate as part of that job. AI screening is therefore both reachable and observable today.

What genuinely does not exist is a way to **re-screen an existing candidate set** without re-running the search — there is no ARQ job and no endpoint for it. That is worth having (criteria change after a search; re-running the full fan-out is expensive and pollutes provenance), so it is in scope as the one piece of new backend surface:

- `POST /api/v1/studies/{id}/screening-runs` enqueues an ARQ job that re-screens existing candidates against the current criteria, returning `{job_id}` in the shape `JobProgressPanel` already consumes.
- The job must record a new `Reviewer` round rather than overwriting prior AI decisions, so inter-rater comparison across criteria revisions stays possible.

### Part B — Make Tertiary Studies reachable (G19)

Feature 009 (specs) is complete on both sides and connected on neither. Thirteen modules — the entire Tertiary UI — are unreachable.

**Root cause.** `StudyPage` branches on `isSLR` and `isRapid` only. A study whose `study_type` is `Tertiary` falls through to the SMS path and renders SMS phase panels over tertiary data.

**Correction to the gap record.** The gap lists four remediation steps, two of which are already done inside the unreachable subtree:

- `TertiaryReportPage` is **already mounted** by `Phase5Panel` (`TertiaryStudyPage.tsx:428`), gated on synthesis completion. No separate wiring is needed.
- The phase gate **already dispatches** on study type: `_PHASE_GATE_DISPATCH[StudyType.TERTIARY] = get_tertiary_unlocked_phases` (`backend/src/backend/api/v1/studies/__init__.py:118`), so `study.unlocked_phases` is already correct for a Tertiary study. No `usePhases`-style extra query is needed, unlike the SLR path.

**There is exactly one missing edge**, and adding it makes all thirteen modules reachable at once.

**Two design decisions this raises**

1. **Host as a takeover, not a per-phase dispatch.** `TertiaryStudyPage` owns its own `PhaseTabs`, and its `Phase1Panel`…`Phase5Panel` are module-private — not exported. Dispatching phase-by-phase from `StudyPage` (the `isSLR` / `isRapid` pattern) would require exporting five internals and would render two tab bars. Instead, `StudyPage` should render its header and then hand off wholesale to `<TertiaryStudyPage>` when the type is Tertiary, skipping its own tab bar. This respects how the component was built.

2. **`StudyDetail` must expose the owning group.** `TertiaryStudyPage` requires a `groupId` prop, which it passes to `SeedImportPanel` → `useGroupStudies` → `GET /api/v1/groups/{groupId}/studies`, so a researcher can pick an existing platform study to import as a seed. **`StudyDetail` does not currently include it**, and the route is `/studies/:studyId` — there is no group in the URL to fall back on. Seed import is the substance of Tertiary Phase 2, so this is not optional:
   - Add `research_group_id: int` to `StudyDetail` and populate it from the ORM.
   - This mirrors the `viewer_role` addition made in `342fc4b` for the same class of reason: the frontend cannot render a feature whose input the API does not return.

### Part C — Replace the phase 4 and 5 placeholders (G20)

For SMS and Tertiary studies, `StudyPage` renders _"Phase 4 content will be available in a future sprint."_ (`:468`) and the same for phase 5 (`:478`), while the components those phases need are written and their endpoints answer.

| Module                                   | Purpose                                                                    | Endpoint                              |
| ---------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------- |
| `pages/ExtractionPage.tsx`               | Lists accepted papers, hosts `ExtractionView`, opens `DiffViewer` on a 409 | `GET /studies/{id}/extractions`       |
| `components/phase3/ExtractionView.tsx`   | Per-paper extraction form                                                  | as above; `PATCH` for edits           |
| `components/shared/DiffViewer.tsx`       | Conflict resolution on concurrent edits                                    | the `PATCH` 409 path                  |
| `components/phase4/ValidityForm.tsx`     | Six validity dimensions, autosave, "Generate with AI" ARQ job              | `GET/PUT/POST /studies/{id}/validity` |
| `components/phase5/QualityReport.tsx`    | Rubric score cards and prioritised recommendations                         | `GET /studies/{id}/quality-reports`   |
| `components/phase2/MetricsDashboard.tsx` | identified → accepted → rejected → duplicates funnel                       | `GET /studies/{id}/metrics`           |

**Required behaviour**

- Phase 4 (non-SLR, non-Rapid) hosts extraction and the validity form; the placeholder is deleted.
- Phase 5 (non-SLR, non-Rapid) hosts the quality report; the placeholder is deleted.
- The metrics funnel is visible from the phase whose numbers it summarises.

**Layout decision.** Phase 4 must present two things at once — a paper list with a per-paper extraction form, and a study-level validity form. `ExtractionPage` already implements the master/detail half (selection state, conflict dialog). The open question is whether validity sits below extraction on the same tab or in a sub-tab; recommend below, since the tab bar is already the primary navigation and nesting a second one is the confusion Part B avoids.

**One refactor.** `ExtractionPage` reads its ID via `useParams<{ studyId: string }>()`. It happens that the `StudyPage` route is `studies/:studyId`, so mounting it as a child would work by coincidence of a matching param name. Do not rely on that — give it an optional `studyId` prop that takes precedence over the route param, matching how `TertiaryReportPage` and the SLR pages are written.

---

## Integration Points

- **`StudyPage.tsx`** is the single point of change for all three parts. It gains an `isTertiary` branch (B), two real phase bodies replacing placeholders (C), and hosts the screening selection state (A).
- **`StudyDetail`** (backend schema plus the frontend interface mirroring it) gains `research_group_id`.
- **No migration.** Every table involved exists as of `0018`.
- **No new component.** Every UI module named above is already written and unit-tested.
- **One new endpoint and one new ARQ job**, both in Part A (`POST /studies/{id}/screening-runs`).
- **`scripts/audit_unreachable_frontend.py`** is the acceptance oracle. It already exits non-zero when unreachable modules exist; this feature is the right point to add it to CI, since afterwards the count drops to the two G21 modules and a regression becomes detectable.

---

## Success Criteria

1. A reviewer can select a paper in the Phase 3 queue, record an accept / reject / duplicate decision with reasons, and see the queue status update — on an SMS, SLR, and Tertiary study.
2. Prior decisions and reviewer conflicts are visible at the point of decision.
3. Re-screening an existing candidate set against revised criteria can be triggered from the UI and reports progress through the existing job panel, without re-running the database search.
4. Opening a Tertiary study renders the Tertiary dashboard with its five phases, not SMS phase panels.
5. A researcher can import a seed study from their research group into a Tertiary study through the UI — that is, `research_group_id` reaches `SeedImportPanel`.
6. Phase 4 and Phase 5 of an SMS study render extraction, validity, and quality reporting. The string "will be available in a future sprint" does not appear in the codebase.
7. `python3 scripts/audit_unreachable_frontend.py` reports no unreachable modules in the Tertiary, extraction/phases-4–5, and screening clusters.
8. The three `test.fixme` tests in `frontend/e2e/screen-paper.spec.ts` are un-`fixme`d and pass, and new e2e specs cover the Tertiary workflow and phases 4–5 — neither of which has any end-to-end coverage today, because neither could be reached.

---

## Non-Goals

- **G21** (`QualityScoreForm`, `EdgeConditionBuilder`) — the same defect shape, but inside features that are already reachable, so no user-visible workflow is blocked. Cheap to fold in if convenient; not a criterion for this feature.
- **G4 / G5** (inter-rater reliability rules, intra-rater rounds) — unblocked by Part A, but separate work. This feature makes κ exercisable through the UI; it does not change how κ is computed or gated.
- **G6** (Study entity distinct from Paper) — the structural gap underneath extraction. Part C surfaces the existing extraction UI as built; it does not change the unit of analysis.
- Any redesign of the components being wired. If one is wrong, that is a finding to record, not to fix here — the value of this feature is that it is almost entirely additive edges.

---

## Risks

| Risk                                                                                                                                | Mitigation                                                                                                                        |
| ----------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Components unreachable for months may not match the current API shape — they were unit-tested against mocks, never against a server | Exercise each through e2e against a live backend before declaring the part done; mock-only green is precisely what hid these gaps |
| `StudyPage` is already long and gains three more branches                                                                           | Extract the per-study-type dispatch into a small component or map before adding to it, rather than after                          |
| Re-screening writes a second AI decision round, which downstream κ and metrics code may not expect                                  | Verify the metrics funnel and inter-rater queries against a study with two AI rounds as part of Part A                            |

---

## Verification

```bash
# 1. No unreachable frontend modules outside the G21 pair
python3 scripts/audit_unreachable_frontend.py

# 2. No placeholders left behind
grep -rn "future sprint" frontend/src && echo "FAIL: placeholder still present"

# 3. Full e2e suite, from frontend/ — running from the repo root picks up a
#    different playwright and fails with "test.describe() called here"
cd frontend && npx playwright test
```
