# Contract: Study Detail and Decision Submission

**Feature**: `012-wire-up-unreachable-workflows`
**Status**: Proposed — not yet implemented
**Requirements**: FR-007, FR-009, FR-010, FR-022, FR-025, FR-027

Two changes to existing contracts. The study-detail change is additive and breaks nothing. The
decision-submission change is **breaking**: `observed_status` is required, so every existing
caller must be updated in the same change (FR-027, plan item C5). No field is removed or
retyped.

---

## 1. `GET /api/v1/studies/{study_id}` — one new field

### Change

```diff
  {
    "id": 42,
    "name": "Microservice Testing Practices",
    "study_type": "Tertiary",
    "status": "active",
    "current_phase": 2,
    "unlocked_phases": [0, 1, 2],
    "viewer_role": "lead",
+   "research_group_id": 7,
    "created_at": "…",
    "updated_at": "…"
  }
```

| Field               | Type  | Nullable | Source                             |
| ------------------- | ----- | -------- | ---------------------------------- |
| `research_group_id` | `int` | No       | Existing `Study.research_group_id` |

### Why this is required, not convenient

The Tertiary workspace offers the researcher other studies in the owning group as seed
candidates (FR-009). It obtains them from `GET /api/v1/groups/{groupId}/studies`, which needs a
group id. The study route is `/studies/:studyId` — there is no group segment to fall back on,
and the study response does not currently carry one. **Seed import is the substance of Tertiary
phase 2, so the feature cannot function without this field.**

This is the clause in Principle X that says a response schema must expose the fields the UI
gates on. It is the same shape as the `viewer_role` addition in `342fc4b`, which was added
because Mark Complete and Approve were being rendered for nobody.

### Obligations

- The field is populated for **every** study type, not only Tertiary. A type-conditional payload
  would be a new source of the same class of bug.
- The frontend `StudyDetail` interface mirrors the backend model; both change together.
- Existing consumers ignore an unknown field, so no coordinated release is needed.

---

## 2. `POST /api/v1/studies/{id}/papers/{candidate_id}/decisions` — two guards

The endpoint exists and is covered by `backend/tests/integration/test_papers_decisions.py`. Two
guards are added; the request otherwise keeps its current shape.

### Added request fields

| Field                   | Type          | Required | Purpose                                                       |
| ----------------------- | ------------- | -------- | ------------------------------------------------------------- |
| `observed_status`       | `string`      | Yes      | The paper status the reviewer was shown (FR-025, FR-027)      |
| `overrides_decision_id` | `int \| null` | No       | The reviewer's own earlier decision being superseded (FR-022) |

`overrides_decision_id` and `is_override` already exist in the model and are honoured by the
endpoint. This contract makes their use by the UI explicit rather than adding them.

### Added responses

#### `409 Conflict` — the paper changed under the reviewer (FR-025)

```json
{
  "detail": {
    "message": "This paper's status changed while you were reviewing it.",
    "observed_status": "pending",
    "current_status": "accepted",
    "changed_by": "another reviewer"
  }
}
```

Raised when `observed_status` does not match the paper's stored `current_status`. The client
shows the new state and asks the reviewer to confirm; **the reasons and annotation they already
entered are preserved across that confirmation** and resubmitted with the updated
`observed_status`. A decision is never written against a state the reviewer did not see.

#### `409 Conflict` — an unacknowledged prior decision by the same reviewer (FR-022)

Raised when this reviewer already holds a decision on this paper and `overrides_decision_id` was
not supplied. The payload carries their earlier decision so the client can show it and require
explicit confirmation. Resubmitting with `overrides_decision_id` set succeeds and records an
override; the earlier decision is retained.

### Why override rather than replace

A reviewer changing their mind and two reviewers disagreeing look identical unless the override
link is recorded. Agreement measures read genuine disagreement; if a correction were
indistinguishable from it, every corrected misclick would depress the study's agreement figure.

---

## Test obligations

| Level       | Case                                                                                  |
| ----------- | ------------------------------------------------------------------------------------- |
| Unit        | `research_group_id` is serialised for every study type                                |
| Integration | Study detail returns the field and it matches the owning group                        |
| Integration | Stale `observed_status` yields `409` with both statuses in the payload                |
| Integration | Second decision without `overrides_decision_id` yields `409` carrying the earlier one |
| Integration | Second decision with it succeeds, sets `is_override`, and retains the original        |
| Integration | An override by the same reviewer does not raise the paper's conflict flag             |
| Component   | The panel preserves entered reasons and annotation across a re-confirmation           |
| e2e         | Journey 2 — a seed study is importable, proving the group id reached the panel        |
