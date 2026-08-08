# Implementation Plan: Wire Up Unreachable Workflows

**Branch**: `012-wire-up-unreachable-workflows` | **Date**: 2026-08-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-wire-up-unreachable-workflows/spec.md`

## Summary

Make three finished-but-unreachable capabilities reachable — recording screening decisions, the
Tertiary Studies workspace, and the extraction/reporting phases — and add one genuinely new
capability, re-screening an existing candidate set against revised criteria.

The approach is deliberately additive: almost every component and service involved already
exists and is unit-tested. The work is (a) replacing a boolean study-type chain in `StudyPage`
with a dispatch map before adding a third branch to it, (b) mounting components that nothing
currently imports, (c) one field on the study detail response, and (d) one endpoint plus one ARQ
job composed from the existing screening helpers.

Phase 0 research contradicted the PRD in three places, each of which enlarges the work:

1. Re-screening **does** need a migration — one `JobType` enum value (R1).
2. The shared AI reviewer must become **one reviewer per round**, or rounds are
   indistinguishable (R2).
3. `_run_screening_pass` **swallows exceptions and returns "rejected"**, so a provider fault is
   recorded as a legitimate rejection. FR-024 cannot be satisfied on top of that, so this
   pre-existing defect must be fixed as part of the feature (R3).

## Technical Context

**Language/Version**: Python 3.14 (backend, db, agents); TypeScript 5.4 / Node 20 LTS (frontend)
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 async, Alembic, ARQ, LiteLLM;
React 18, MUI v5, TanStack Query v5. **No new dependencies.**
**Storage**: PostgreSQL 16 (production), SQLite + aiosqlite (tests). One Alembic migration —
`0020`, adding a `JobType` enum value only. No table or column changes. (Planned as `0019`;
`0019_candidate_citation_intent` has since taken that number and holds head.)
**Testing**: pytest (unit + integration), Vitest + React Testing Library (component), Playwright
(e2e against a live backend), cosmic-ray / Stryker (mutation)
**Target Platform**: Linux server + modern browsers
**Project Type**: Web application — `uv` workspace (backend, db, agents) plus a Vite/React SPA
**Performance Goals**: A reviewer records a decision in under 30 s from opening the study
(SC-001); queue reflects a decision without a manual refresh (SC-002); re-screen progress
reported on the existing polling cadence
**Constraints**: No new stored entities beyond the enum value; no redesign of the components
being wired; a re-screen must never interleave with another automated round over the same
candidates
**Scale/Scope**: 4 user journeys, 26 functional requirements, 21 previously-unreachable frontend
modules made reachable, 1 new endpoint, 1 new ARQ job, 1 migration

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

Pre-implementation review performed against `StudyPage.tsx` (497 lines), `search_job.py` (941
lines), `searches.py`, `papers.py`, and the twenty-one unreachable frontend modules. Violations
found are recorded in Complexity Tracking with an explicit remediation task, per Principle IV —
not fixed silently inline.

| Gate                                                                                                     | Status | Notes                                                                                                                                      |
| -------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| SOLID — no SRP violations in target modules                                                              | ⚠      | `StudyPage` already mixes fetch, type dispatch, phase rendering, and dialogs. **C1** — extract dispatch before adding to it                |
| SOLID — extension points exist (OCP) where variation expected                                            | ⚠      | Study-type variation is expressed as boolean flags, closed to extension. **C1** resolves                                                   |
| Structural — no DRY violations (duplication)                                                             | ✅     | Re-screen composes existing helpers rather than copying the screening pass (R3)                                                            |
| Structural — no YAGNI violations (speculative generality)                                                | ✅     | Dispatch map is warranted by a third variant arriving now, not speculatively                                                               |
| Code clarity — no long methods (>20 lines) in touched code                                               | ⚠      | `StudyPage`'s render is far over. **C1**                                                                                                   |
| Code clarity — no switch/if-chain smells in touched code                                                 | ⚠      | Eleven `isSLR` / `isRapid` dispatch points — a direct Principle III violation. **C1**                                                      |
| Code clarity — no common code smells identified                                                          | ⚠      | `search_job.py` is 941 lines, over the 800 maximum, and this feature adds to that area. **C2**                                             |
| Refactoring — pre-implementation review completed                                                        | ✅     | This table plus Complexity Tracking                                                                                                        |
| Refactoring — any found refactors added to task list with tests                                          | ✅     | C1–C3 become explicit tasks, each test-first                                                                                               |
| GRASP/patterns — responsibility assignments reviewed                                                     | ✅     | Dispatch map mirrors the backend's `_PHASE_GATE_DISPATCH` (Protected Variations)                                                           |
| Test coverage — existing tests pass; refactor tests written first                                        | ✅     | C1 is behaviour-preserving and must be covered before it is performed                                                                      |
| Toolchain (VII) — no unapproved deps or tool substitutions introduced                                    | ✅     | Zero new dependencies                                                                                                                      |
| Toolchain (VII) — FastAPI/SQLAlchemy 2.x/ARQ/LiteLLM patterns followed                                   | ✅     | New endpoint mirrors `start_full_search`; new job mirrors `run_full_search`                                                                |
| Observability (VIII) — new models have audit fields + structlog used                                     | ✅     | No new models. Job uses `structlog`, consistent with `search_job`                                                                          |
| Observability (VIII) — config via Pydantic BaseSettings + lru_cache                                      | ✅     | No new configuration                                                                                                                       |
| Infrastructure (VIII) — Docker services have healthchecks if added                                       | ✅     | No new services                                                                                                                            |
| Language (IX) — React components functional, props typed, ≤100 JSX lines                                 | ✅     | New shared screening panel must be authored within the limit; existing components already comply                                           |
| Language (IX) — Hooks called at top level only (Rules of Hooks); no inline refs in deps                  | ✅     | Selection state is a single `useState` lifted into the screening view                                                                      |
| Language (IX) — No React state mutation; no array-index keys in lists                                    | ✅     | Queue rows key on candidate id                                                                                                             |
| Language (IX) — >3 related useState → useReducer; useCallback only when justified                        | ✅     | Selection plus confirmation state stays at two related values; revisit if it grows                                                         |
| Language (IX) — useEffect returns cleanup for all resource-acquiring effects                             | ✅     | Progress polling uses TanStack `refetchInterval`, not a hand-rolled effect                                                                 |
| Language (IX) — React.memo applied deliberately; useImperativeHandle used for imperative APIs            | ✅     | Neither warranted; not applied speculatively                                                                                               |
| Language (IX) — useWatch used (not watch) for reactive form field subscriptions                          | ✅     | No new forms; existing forms already comply                                                                                                |
| Language (IX) — Vite env vars use VITE\_ prefix + import.meta.env                                        | ✅     | No new environment variables                                                                                                               |
| Language (IX) — Python: no plain dict for domain data; pathlib used                                      | ✅     | Request and response bodies are Pydantic models                                                                                            |
| Language (IX) — Python: no mutable defaults; specific exception handling                                 | ⚠      | `_run_screening_pass` catches bare `Exception` and returns a rejection. **C3** — a correctness blocker for FR-024, not a style note        |
| Language (IX) — TypeScript: no any/enum/non-null(!) without justification                                | ✅     | Study type stays a string-literal union                                                                                                    |
| Language (IX) — TypeScript: unknown + Zod at all external boundaries                                     | ✅     | New response field parsed at the existing boundary                                                                                         |
| Code clarity — all source files have a module-level doc comment                                          | ✅     | New job, endpoint, and dispatch module each carry one                                                                                      |
| Code clarity — all functions/methods/classes have doc comments                                           | ✅     | Google-style (Python) / JSDoc (TS)                                                                                                         |
| Pre-existing issues — all pre-existing failures in touched files resolved before completion              | ✅     | Baseline is clean; C1–C3 are quality violations rather than failing checks, and are tasked regardless                                      |
| Feature completion docs — CLAUDE.md, READMEs, CHANGELOGs update tasks in task list                       | ✅     | Will appear as TDOC tasks. The root README route table and `docs/feature-gaps.md` G18–G20 both need updating when this lands               |
| Reachability (X) — every new component is routed or dispatched to; audit exits clean                     | ✅     | This is the feature's purpose. The audit is the acceptance oracle and gets wired into CI here                                              |
| Reachability (X) — every new APIRouter is registered; response schemas expose the fields the UI gates on | ✅     | `research_group_id` on `StudyDetail` is precisely this clause (R7)                                                                         |
| Reachability (X) — every user-facing feature has an e2e test driving it through the UI                   | ✅     | Four journeys, four e2e specs; three have no coverage today because they were unreachable                                                  |
| Test signalling (VI) — no state-conditional assertions or isVisible() guards                             | ⚠      | The three `test.fixme` cases in `screen-paper.spec.ts` must become real. The 5 conditional skips in `results-dashboard.spec.ts` are **C4** |

**Gate result**: PASS with four recorded violations, all pre-existing, each with a remediation
task. No unjustified violation blocks Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/012-wire-up-unreachable-workflows/
├── plan.md              # This file
├── spec.md              # Feature specification (clarified 2026-08-06)
├── research.md          # Phase 0 output — R1–R8
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── screening-runs.md
│   └── study-detail.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code (repository root)

```text
backend/
├── src/backend/
│   ├── api/v1/
│   │   ├── screening_runs.py        # NEW — POST /studies/{id}/screening-runs
│   │   ├── router.py                # MODIFIED — register the new router
│   │   └── studies/__init__.py      # MODIFIED — research_group_id on StudyDetail
│   └── jobs/
│       ├── rescreen_job.py          # NEW — composes the existing screening helpers
│       ├── search_job.py            # MODIFIED — C3 error propagation; C2 extraction
│       ├── screening_pipeline.py    # NEW (C2) — helpers shared by search and re-screen
│       └── worker.py                # MODIFIED — register the new job
└── tests/
    ├── unit/                        # rescreen job, in-flight guard, round derivation
    └── integration/                 # endpoint, 409 conflict, resume-after-failure

db/
├── src/db/models/jobs.py            # MODIFIED — JobType.RESCREEN
└── alembic/versions/0020_*.py       # NEW — enum value, with downgrade

frontend/
├── src/
│   ├── pages/
│   │   ├── StudyPage.tsx            # MODIFIED — dispatch map (C1), phases 4–5, Tertiary
│   │   └── ExtractionPage.tsx       # MODIFIED — optional studyId prop (R8)
│   ├── components/studies/
│   │   ├── studyTypeDispatch.tsx    # NEW (C1) — study type → workspace renderer map
│   │   └── ScreeningView.tsx        # NEW — queue + selection + reviewer panel + funnel
│   └── services/
│       └── screeningRunsApi.ts      # NEW — start a re-screen, read its progress
└── e2e/
    ├── screen-paper.spec.ts         # MODIFIED — three test.fixme become real
    ├── tertiary-workflow.spec.ts    # NEW — journey 2, no coverage today
    ├── extraction-phases.spec.ts    # NEW — journey 3, no coverage today
    └── rescreen.spec.ts             # NEW — journey 4

scripts/
└── audit_unreachable_frontend.py    # UNCHANGED — becomes a CI gate

.github/workflows/ci.yml             # MODIFIED — run the reachability audit
```

**Structure Decision**: Web application layout, matching the existing repository. Only three of
the six workspace packages are touched: `backend/` (endpoint, job, response field), `db/` (enum
value plus migration), and `frontend/` (dispatch, mounting, e2e). `agents/`, `agent-eval/`, and
`researcher-mcp/` are untouched — the screening agent is reused through the backend job exactly
as the search path already calls it.

## Post-Design Constitution Re-Check

Re-evaluated after Phase 1. **No gate moved from pass to fail**, and two moved the other way —
the design resolves C1 (`studyTypeDispatch.tsx` replaces the boolean chain) and C2
(`screening_pipeline.py` extraction brings `search_job.py` under the 800-line maximum while
giving the re-screen job a shared home rather than a copy).

One consequence the design introduces is tracked as **C5** below: making the reviewer's
observed state mandatory on decision submission is a breaking change to an endpoint that already
has callers and tests. It is planned work with an explicit test-migration obligation, not a
surprise to be discovered during implementation.

Everything else holds: no new dependencies, no new models, no new configuration, no new services,
and the new modules each carry the required module-level doc comment.

## Complexity Tracking

> Violations found during the Principle IV pre-implementation review. Each is pre-existing; none
> is introduced by this feature. Per Principle IV they are recorded and tasked, not fixed
> silently inline, and each refactoring task is separate from the feature commits it enables.

| Item                                                                                   | Type            | Why Accepted / Resolution                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **C1** — `StudyPage` dispatches on study type via 11 paired boolean flags              | Anti-pattern    | Direct Principle III violation (type-switching). Adding Tertiary as a third flag deepens it, and this is precisely how the Tertiary UI became unreachable. Refactor to a study-type → renderer map **before** adding the branch; behaviour-preserving, tests first                                                                                                                                                                                                                                                                                                                   |
| **C2** — `search_job.py` is 941 lines, over the 800 maximum                            | Code smell      | This feature adds a second consumer of its screening helpers. Extract them into `screening_pipeline.py`, which both the search job and the re-screen job import — reducing the file and satisfying DRY in one move rather than growing it further                                                                                                                                                                                                                                                                                                                                    |
| **C3** — `_run_screening_pass` catches bare `Exception` and returns `("rejected", [])` | Correctness     | Not a style issue: a provider fault is persisted as a legitimate rejection of a paper. FR-024 requires distinguishing _assessed and rejected_ from _never assessed_, so this must be fixed for the feature to be correct. Behaviour change to the existing search path — own commit, own test                                                                                                                                                                                                                                                                                        |
| **C4** — 5 conditional `test.skip()` calls in `results-dashboard.spec.ts`              | Anti-pattern    | Forbidden by Principle VI as of constitution v1.8.0, and already recorded there as a known outstanding violation. Not caused by this feature and not on its critical path; fix opportunistically, or carry forward as a tracked exception                                                                                                                                                                                                                                                                                                                                            |
| **C5** — `observed_status` becomes a required field on an existing endpoint            | Breaking change | FR-027. The guard cannot be optional: a caller that omits it regains precisely the ability FR-025 removes, so a nullable field with a skipped check would be security theatre. Accepted because the only callers are this repository's own frontend and its integration tests. **Obligation**: `DecisionRequest`, the endpoint's 409 path, the ~10 existing `POST …/decisions` calls in `backend/tests/integration/test_papers_decisions.py`, and the new stale-state tests all land in one change within journey 1. Migrating the existing tests is part of the task, not follow-up |
| Migration required despite the PRD saying otherwise                                    | Scope           | R1 — one `JobType` enum value. Accepted: the alternative (reusing `FULL_SEARCH`) would defeat FR-026's in-flight discrimination and misreport the job list. Table structure is genuinely unchanged                                                                                                                                                                                                                                                                                                                                                                                   |
