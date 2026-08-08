# Contract: Submit a screening decision

**Feature**: `012-wire-up-unreachable-workflows` (US1)
**Endpoint**: `POST /api/v1/studies/{study_id}/papers/{candidate_id}/decisions`
**Router**: `backend/src/backend/api/v1/papers.py`
**Requirements**: FR-002, FR-003, FR-004, FR-005, FR-022, FR-025, FR-027

Written before implementation so the backend and frontend build to the same shape. Everything
marked **NEW** does not exist today.

---

## Request

```jsonc
{
  "decision": "accepted",           // accepted | rejected | duplicate
  "observed_status": "pending",     // NEW, REQUIRED — see below
  "reasons": [
    { "criterion_id": 3, "criterion_type": "inclusion", "text": "Peer-reviewed" }
  ],
  "overrides_decision_id": null     // int when superseding the caller's own earlier decision
}
```

### `reviewer_id` — **REMOVED** (TFIX4)

Who is reviewing is a property of **who is asking**, not a parameter the caller chooses. The
backend resolves it from the session: `(study_id, current_user.user_id)` → the caller's `human`
`Reviewer` row, created on demand if absent.

Creating on demand is what makes FR-005 true — *any member of a study* can record a decision.
Reviewer rows are otherwise only created at study creation from the `reviewers` list, so a member
added later had no row and therefore no way to screen.

This closes three defects at once, and they are worth naming because each looked like a UI nicety
and was actually an attribution bug:

| Where | What it did |
| ----- | ----------- |
| `ReviewerPanel.tsx` | Asked the researcher to **type their own database id**, and refused to submit until they did. Its own comment: *"simplified — in real use would be populated from auth context"* |
| `submit_decision` | Checked only that the supplied `reviewer_id` belonged to the **study**, never that it belonged to the **caller** — so any member could record a decision under a colleague's name |
| `PaperCard.tsx:389` | Resolved a conflict as `onResolve(lastTwo[0]?.reviewer_id ?? 0, …)` — attributing the binding resolution to **the first disagreeing reviewer**, or to reviewer `0` |

`ResolveConflictRequest` loses `reviewer_id` for the same reason and by the same mechanism.

Not fixed here, recorded as **TFIX5**: `studyTypeDispatch.tsx:304` passes
`<QualityAssessmentPage … reviewerId={0} />`, hardcoded, so SLR quality scores are attributed to
reviewer `0`. Same root cause, different workflow.

### `observed_status` — **NEW, required**

The `current_status` of the candidate paper **as the reviewer was shown it**. Not a duplicate of
`decision`: it is the *before*, where `decision` is the *after*.

Required rather than optional, deliberately. FR-027 gives the reason: an optional field lets any
client skip it, and a client that skips it regains exactly the ability FR-025 removes. A default
would make the guarantee unenforceable while looking enforced.

This breaks every existing caller, which is why migrating them is part of the same task (T010) and
the same commit — a required field and its callers cannot move separately without leaving the
suite red in between. **14 `POST …/decisions` calls across 9 test functions** in
`backend/tests/integration/test_papers_decisions.py` need it.

Valid values are the four `CandidatePaperStatus` values — `pending`, `accepted`, `rejected`,
`duplicate`. Note this is a **wider** set than `decision` accepts: a reviewer routinely observes
`pending`, but can never decide it.

---

## Responses

### 201 Created

`DecisionResponse`, unchanged:

```jsonc
{
  "id": 12, "candidate_paper_id": 5, "reviewer_id": 7,
  "decision": "accepted", "reasons": [ /* … */ ],
  "is_override": false, "overrides_decision_id": null,
  "decided_at": "2026-08-08T17:04:11.921Z"
}
```

### 409 — the paper moved under the reviewer (FR-025, FR-027)

Raised when `observed_status` differs from the stored `current_status`. Carries **both**, so the
client can show what changed rather than merely refusing.

```jsonc
{
  "detail": {
    "error": "stale_state",
    "observed_status": "pending",
    "current_status": "accepted"
  }
}
```

The client re-confirms rather than discarding: FR-025 requires reasons and annotation already
entered to survive the prompt.

### 409 — an unacknowledged prior decision by the same reviewer (FR-022)

Raised when this reviewer already holds a decision on this candidate and `overrides_decision_id`
is absent. Carries their earlier decision so the client can show what is being superseded.

```jsonc
{
  "detail": {
    "error": "unacknowledged_prior_decision",
    "prior_decision": {
      "id": 9, "decision": "rejected",
      "reasons": [ /* … */ ],
      "decided_at": "2026-08-08T16:55:02.113Z"
    }
  }
}
```

Resubmitting with `overrides_decision_id: 9` succeeds, sets `is_override: true`, and **retains**
the original row.

### 422 — unchanged

`Invalid decision value: …` for a `decision` outside the three enum values; `Reviewer does not
belong to this study` when the reviewer is not on the study.

---

## Check order

1. Study membership (`require_study_member`) — as today
2. **Resolve the caller's reviewer row** from the session, creating it if absent (replaces the
   former "reviewer belongs to the study" 422, which no longer has an input to validate)
3. Candidate exists — 404 as today
4. `decision` parses to `PaperDecisionType` — 422 as today
5. **`observed_status` matches `current_status`** — 409 `stale_state`
6. **No unacknowledged prior decision by this reviewer** — 409 `unacknowledged_prior_decision`
7. Write

5 precedes 6 because a stale view makes the prior-decision question unanswerable: the reviewer is
being told about a paper state they have not seen yet.

`detail` is a **dict**, not a string, matching the optimistic-locking precedent at
`backend/src/backend/api/v1/extractions.py:378-385`. Both forms exist in this codebase; the dict
form is the one used for "your view of a mutable resource is stale", which is exactly this case.

---

## Conflict flag — a correction is not a disagreement

**This is a behaviour change, and the substance of T009.**

Conflict detection today (`papers.py:297-303`) counts *every* human decision on the candidate and
flags a conflict when outcomes differ. Under FR-022 that is wrong the moment it matters: a
reviewer who overrides their own earlier decision leaves two rows with differing outcomes, and the
paper is flagged as a disagreement between reviewers when one reviewer simply changed their mind.

`data-model.md` states the invariant this must satisfy:

> A correction (`is_override` true, same reviewer) must remain distinguishable from disagreement
> (different reviewers, no override link). Agreement calculations read the latter, never the
> former.

Required algorithm:

1. Load all decisions on the candidate, joined to their reviewer.
2. Keep human reviewers only — an AI decision against a human one is not a disagreement between
   reviewers, and the existing code is already right about this.
3. **Drop superseded decisions**: any decision whose `id` appears as another decision's
   `overrides_decision_id`.
4. Reduce to one decision per reviewer — the latest surviving one.
5. `conflict_flag = len(remaining) >= 2 and len({d.decision for d in remaining}) > 1`.

Step 3 is the new one. Steps 1, 2 and 5 already exist in some form.

---

## Out of scope, recorded so it is not lost

`PaperDecision` has **no `annotation` column**, contrary to the field list in `data-model.md`.
`ReviewerPanel.tsx:82-83` stores the free-text annotation inside the `reasons` array as
`{"criterion_type": "annotation", "text": "…"}`.

FR-002 requires an annotation and the capability does work, so nothing is broken for a user. But
FR-002 also says reasons are "drawn from the study's criteria", and an annotation carried as a
pseudo-reason is counted by anything counting reasons. Recorded as **TFIX3**; not fixed in US1,
because a dedicated column means a migration and `data-model.md` states this feature has exactly
one.

Until then, treat `reasons` entries with `criterion_type == "annotation"` as annotation, not as a
criterion — and do not add a second encoding.
