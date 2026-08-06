# Phase 0 Research: Wire Up Unreachable Workflows

**Feature**: `012-wire-up-unreachable-workflows`
**Date**: 2026-08-06

Every question below was resolved by reading the code rather than by assumption. Three findings
contradict the source PRD; they are called out explicitly because they change the work.

---

## R1 — Re-screening needs a schema change after all

**Decision**: Add a `RESCREEN` member to the `JobType` enumeration and ship an Alembic migration
for it.

**Rationale**: `BackgroundJob.job_type` is a PostgreSQL enum column
(`background_job_type_enum`). Its members are `full_search`, `snowball_search`,
`batch_extraction`, `generate_results`, `export`, `quality_eval`, `validity_prefill`,
`expert_seed`, `test_search` — there is no re-screen. Progress reporting, the job listing
endpoint, and the FR-026 in-flight check all key off `job_type`, so a re-screen must be
representable as one. Adding a value to a PostgreSQL enum type requires a migration
(`ALTER TYPE … ADD VALUE`); it is not a no-op the way adding a Python enum member is.

**This contradicts the PRD and the spec.** The PRD states "No migration. Every table involved
exists as of `0018`", and spec Assumption 8 says "No new stored data is required". Both are
wrong in this one respect. No table changes; one enum type does.

**Alternatives considered**:

- _Reuse `FULL_SEARCH` for re-screens_ — rejected. FR-026 must distinguish a re-screen from a
  search to refuse the right things, and the job list would misreport what ran.
- _Add a free-text discriminator column_ — rejected. Violates the constitution's rule against
  magic strings where an enum is the domain-constrained representation.

---

## R2 — A re-screen round needs its own reviewer, and `agent_config` can carry it

**Decision**: Create a distinct `Reviewer` row per re-screen run, recording the round in the
existing `agent_config` JSON payload. No schema change.

**Rationale**: FR-019 requires each re-screen to be a distinct round that does not overwrite
earlier automated judgements. Today `_get_or_create_ai_reviewer` (`search_job.py:526`) returns
**one shared AI reviewer per study**, so a second automated pass would append decisions under
the same reviewer identity and become indistinguishable from the first. `Reviewer` already has
a nullable `agent_config` JSON column holding `{"agent_name": "screener"}`, which extends to
`{"agent_name": "screener", "round": 2, "screening_run_id": …}` without a migration.

**Alternatives considered**:

- _A dedicated round column on `Reviewer`_ — cleaner to query, but a second migration for data
  that JSON already accommodates. Revisit if round-filtered queries become hot.
- _Reuse the shared reviewer and rely on timestamps_ — rejected. It makes a round implicit, and
  FR-022 requires a reviewer's correction to stay distinguishable from disagreement; timestamps
  alone cannot carry that.

---

## R3 — The screening pipeline is reusable, but its error handling is not fit for FR-024

**Decision**: Compose the re-screen job from the existing helpers, and change
`_run_screening_pass` to propagate failures instead of swallowing them.

**Rationale**: The seams are already right — `_load_criteria`, `_build_screener_with_context`,
`_process_single_candidate`, `_record_paper_decision`, and `_run_screening_pass` are each
independent of the search that currently calls them, so the new job is composition, not
duplication (DRY holds).

But `_run_screening_pass` (`search_job.py:303`) catches `Exception` and **returns
`("rejected", [])`**. A provider timeout is therefore recorded as a legitimate rejection of the
paper. That is a pre-existing silent-failure defect, and FR-024 cannot be met on top of it: a
run that must "retain what it completed and report how many papers it covered" cannot count a
paper the screener never actually judged. The distinction between _assessed and rejected_ and
_never assessed_ has to be real.

**Alternatives considered**:

- _Leave it and count attempts_ — rejected. It would report coverage the run did not achieve and
  silently reject papers on infrastructure faults.
- _Catch narrowly at the call site only_ — insufficient; the swallow is inside the helper both
  callers share.

**Consequence**: this is a behaviour change to the existing search path, not only to the new
one. It needs its own test and its own commit, separate from the wiring.

---

## R4 — Refusing a concurrent run is a `BackgroundJob` query

**Decision**: Before enqueuing, reject with `409 Conflict` if the study has a `BackgroundJob` in
a non-terminal state whose type is `FULL_SEARCH`, `SNOWBALL_SEARCH`, or `RESCREEN`. The response
names the run in progress.

**Rationale**: `BackgroundJob` carries `study_id`, `job_type`, and `status`, so the check is a
single indexed query with no new state. FR-026 covers full search as well as re-screens because
the search pipeline screens every candidate it retrieves — two automated rounds would interleave
over the same papers.

**Alternatives considered**: a queue (needs state the platform does not model) and an advisory
lock (invisible to the UI, which must name the blocking run).

---

## R5 — Resumability comes from decision rows, not from run state

**Decision**: A restarted re-screen assesses candidates that have no decision recorded by the
current round's reviewer. No checkpoint or cursor is stored.

**Rationale**: FR-024 requires a restart to cover only what the round did not reach. Because
each assessment is written as a decision row tied to the round's reviewer (R2), the set of
outstanding papers is derivable: candidates in the study minus those already judged by that
reviewer. A stored cursor would be a second source of truth that can disagree with the rows.

**Alternatives considered**: a persisted cursor or offset — rejected as derivable state, and it
would drift if candidates were added mid-run.

---

## R6 — The study-type dispatch must become a map before it grows

**Decision**: Replace the `isSLR` / `isRapid` boolean chain in `StudyPage` with a study-type to
renderer mapping, then add Tertiary to it.

**Rationale**: Constitution Principle III forbids `if`/`else` chains that dispatch on type,
requiring a dispatch map or polymorphism. `StudyPage.tsx` is 497 lines and currently dispatches
on type through paired boolean flags at eleven separate points. Adding Tertiary as a third flag
would deepen an existing violation, and Principle IV requires that a refactor identified during
pre-implementation review be an explicit task rather than a silent inline fix.

The backend already demonstrates the target shape: `_PHASE_GATE_DISPATCH` maps `StudyType` to a
gate function. This is the same pattern on the frontend.

**Alternatives considered**: adding `isTertiary` alongside the existing flags — rejected; it is
the cheapest change now and the one that guarantees the same defect recurs for the next study
type, which is exactly how the Tertiary UI became unreachable.

---

## R7 — Tertiary is hosted as a takeover; the group id must be served

**Decision**: `StudyPage` renders the study header and delegates wholesale to the Tertiary
workspace for tertiary studies. `StudyDetail` gains `research_group_id`.

**Rationale**: The Tertiary workspace owns its own phase navigation and keeps its five phase
panels module-private. Folding them into `StudyPage` would mean exporting five internals and
rendering two phase bars. Separately, the workspace requires the owning group to offer seed
studies, `StudyDetail` does not return it, and the route carries no group segment — so seed
import (the substance of Tertiary phase 2, FR-009) cannot function without the field. This is
the same shape as the `viewer_role` addition in `342fc4b`.

**Alternatives considered**: deriving the group from a separate lookup call — an extra
round-trip for data the study response should already carry; and a route change to
`/groups/:groupId/studies/:studyId` — breaks existing links for no benefit.

---

## R8 — `ExtractionPage` takes a prop rather than relying on a route coincidence

**Decision**: Give `ExtractionPage` an optional `studyId` prop that takes precedence over the
route parameter.

**Rationale**: It reads `useParams<{ studyId: string }>()`. The `StudyPage` route is
`studies/:studyId`, so mounting it as a child happens to work — by coincidence of a matching
parameter name, not by design. The sibling pages it will sit beside (`TertiaryReportPage`, the
SLR pages) all take an explicit prop.

---

## Resolved unknowns

| Question                                       | Resolution                                        |
| ---------------------------------------------- | ------------------------------------------------- |
| Does re-screening require a migration?         | Yes — one enum value (R1). Contradicts the PRD.   |
| How is a distinct automated round represented? | New `Reviewer` per run, round in `agent_config`   |
| Can the screening pipeline be reused as-is?    | Composition yes; error handling must change (R3)  |
| How is a concurrent run refused?               | `BackgroundJob` state query, `409` naming the run |
| How does a restart know what is left?          | Derived from decision rows, no cursor (R5)        |
| How does Tertiary get hosted?                  | Takeover, plus `research_group_id` on the study   |

No `NEEDS CLARIFICATION` markers remain.
