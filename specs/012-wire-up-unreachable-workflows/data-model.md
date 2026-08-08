# Phase 1 Data Model: Wire Up Unreachable Workflows

**Feature**: `012-wire-up-unreachable-workflows`
**Date**: 2026-08-06

Nearly every entity here already exists. This document states what each contributes to the
feature, which invariants the requirements impose on it, and the **one** change that needs a
migration.

---

## Change summary

| Entity          | Change                                                 | Migration?                   |
| --------------- | ------------------------------------------------------ | ---------------------------- |
| `JobType`       | New member `RESCREEN = "rescreen"`                     | **Yes** — `0020`, enum value |
| `Reviewer`      | Round metadata inside the existing `agent_config` JSON | No — column already nullable |
| `StudyDetail`   | New response field `research_group_id: int`            | No — response schema only    |
| Everything else | Unchanged                                              | No                           |

No table is created, dropped, or altered. No column is added. The migration adds a single value
to the `background_job_type_enum` PostgreSQL type and must provide a working `downgrade()`.

> **The revision is `0020`, not `0019` as first planned.** `0019_candidate_citation_intent` landed
> on this branch after this document was written and now holds head, and alembic rejects a
> duplicate revision id. Confirm before writing it: `(cd db && uv run alembic heads)` — and note
> that alembic runs from `db/`, not the repository root.

---

## Existing entities

### CandidatePaper

A paper retrieved by a study's search, awaiting or holding a screening outcome.

| Field                   | Role in this feature                                      |
| ----------------------- | --------------------------------------------------------- |
| `id`                    | Identifies the paper being judged                         |
| `study_id`              | Scopes the queue and the re-screen set                    |
| `current_status`        | What the queue displays; updated when a decision is saved |
| `conflict_flag`         | Drives the disagreement warning required by FR-004        |
| `duplicate_of_id`       | Set when a reviewer records a duplicate outcome           |
| `source_seed_import_id` | Links a candidate to the Tertiary seed it came from       |

**Invariants**

- FR-003 — after a decision is saved, `current_status` reflects it without the client refetching
  on the user's initiative.
- FR-025 — a decision must not be written against a `current_status` the reviewer never saw. The
  status the reviewer was shown is carried with the submission and checked before the write.

### PaperDecision

One reviewer's judgement on one candidate paper. Multiple decisions per paper are expected —
that is what makes agreement measurable.

| Field                   | Role in this feature                                               |
| ----------------------- | ------------------------------------------------------------------ |
| `candidate_paper_id`    | The paper judged                                                   |
| `reviewer_id`           | Who judged it — human, or the round's automated reviewer           |
| `decision`              | `accepted` / `rejected` / `duplicate`                              |
| `reasons`               | Criteria that justify the outcome                                  |
| `annotation`            | Free text for the record                                           |
| `overrides_decision_id` | **Central to FR-022** — points at the decision this one supersedes |
| `is_override`           | Set automatically when `overrides_decision_id` is provided         |

**Invariants**

- FR-022 — a reviewer's second decision on the same paper sets `overrides_decision_id` to their
  own earlier decision. The earlier row is retained.
- A correction (`is_override` true, same reviewer) must remain distinguishable from disagreement
  (different reviewers, no override link). Agreement calculations read the latter, never the
  former.
- FR-019 — an automated round never writes an override of a human decision.

### Reviewer

A participant in screening, human or automated.

| Field           | Role in this feature                                          |
| --------------- | ------------------------------------------------------------- |
| `study_id`      | Scopes the reviewer                                           |
| `reviewer_type` | `human` or `ai_agent`                                         |
| `user_id`       | Set for human reviewers                                       |
| `agent_config`  | Nullable JSON — **carries the round** for automated reviewers |

**Change**: today one shared `ai_agent` reviewer per study is reused by every automated pass
(`_get_or_create_ai_reviewer`). Each re-screen now creates its **own** reviewer row:

```json
{ "agent_name": "screener", "round": 2, "screening_run_id": "<job id>" }
```

**Invariants**

- FR-019 — one automated reviewer per round. Reusing the shared reviewer would make two rounds
  indistinguishable, defeating round-over-round comparison.
- R5 — the papers a round still has to assess are derived as: candidates of the study, minus
  those already holding a decision by that round's reviewer. No cursor is stored.

### BackgroundJob

A long-running task with observable progress. Reused unchanged.

| Field                             | Role in this feature                                 |
| --------------------------------- | ---------------------------------------------------- |
| `id`                              | The job identifier returned to the client            |
| `study_id`, `job_type`, `status`  | **The FR-026 in-flight query** — no new state needed |
| `progress_pct`, `progress_detail` | FR-018 progress; carries papers assessed vs. total   |
| `error_message`                   | FR-024 — why a run stopped                           |

**Invariants**

- FR-026 — a re-screen is refused while this study has a job in a non-terminal state whose type
  is `FULL_SEARCH`, `SNOWBALL_SEARCH`, or `RESCREEN`. The refusal names that job.
- FR-024 — a run that fails part-way ends `failed` with `progress_detail` recording the papers
  it covered. It is never marked complete while its coverage is partial.

### JobType _(changed)_

```text
full_search · snowball_search · batch_extraction · generate_results
export · quality_eval · validity_prefill · expert_seed · test_search
+ rescreen                                                       ← NEW
```

**Why a migration**: this is a PostgreSQL enum type (`background_job_type_enum`), so a new member
requires `ALTER TYPE … ADD VALUE`. Adding it to the Python enum alone would fail on insert. This
is the single point where the PRD's "no migration" claim is wrong.

**Constitution note**: the column is declared with `values_callable`, so the stored value is
`"rescreen"`, not `"RESCREEN"`. See MEMORY.md.

### Study / StudyDetail _(response change)_

| Field                         | Role in this feature                                       |
| ----------------------------- | ---------------------------------------------------------- |
| `study_type`                  | Selects the workspace via the dispatch map (FR-007)        |
| `unlocked_phases`             | Already correct for Tertiary — the gate dispatch exists    |
| `viewer_role`                 | Existing; the precedent for the field below                |
| `research_group_id` **(new)** | **FR-009/FR-010** — without it seed import cannot function |

`research_group_id` is read from the existing `Study.research_group_id` column. Nothing is stored
that was not stored before; the field was simply never returned.

### DataExtraction, ValidityAssessment, QualityReport

Unchanged, and reached rather than modified. `DataExtraction` carries a version used for
optimistic locking, which is what surfaces the concurrent-edit conflict FR-012 requires — the
mechanism exists and is exercised by the conflict path today.

---

## New conceptual entity

### Screening Run

An assessment of a study's existing candidate papers against its current criteria.

**It has no table of its own.** A screening run is the composition of:

- a `BackgroundJob` of type `rescreen` — identity, status, progress, failure reason;
- a `Reviewer` row carrying the round — authorship of every decision the run writes;
- the `PaperDecision` rows the run produces — which double as its completion record (R5).

Modelling it as a table was considered and rejected: every attribute already lives on one of the
three, and a fourth row would be a second source of truth about how far a run got — the precise
failure R5 avoids.

**Lifecycle**

```text
requested ──[another run in flight?]──> refused (409, names the blocking job)
    │ no
    ▼
queued ──> running ──> complete        all candidates assessed by this round's reviewer
             │
             └──────> failed           partial: assessments kept, coverage reported
                         │
                         └─[restart]─> running   assesses only papers this round has not reached
```

---

## Validation rules drawn from the requirements

| Rule                                                                                   | Source         |
| -------------------------------------------------------------------------------------- | -------------- |
| A decision carries at least one reason                                                 | FR-002         |
| A second decision by the same reviewer on the same paper links to the one it overrides | FR-022         |
| A submission is rejected if the paper's status changed since the reviewer saw it       | FR-025         |
| Any study member may write; the lead is not required                                   | FR-005, FR-023 |
| A re-screen is refused while another assessment of the same candidates is in flight    | FR-026         |
| A failed run retains its assessments and reports coverage                              | FR-024         |
| An automated round never alters a human decision                                       | FR-019         |
