# Contract: Screening Runs

**Feature**: `012-wire-up-unreachable-workflows`
**Status**: Proposed — not yet implemented
**Requirements**: FR-017, FR-018, FR-019, FR-023, FR-024, FR-026

The only new endpoint in this feature. It mirrors `POST /studies/{id}/searches`
(`backend/src/backend/api/v1/searches.py:40`) in shape, status code, and response envelope, so
the existing job progress panel consumes it unchanged.

---

## `POST /api/v1/studies/{study_id}/screening-runs`

Re-assess a study's **existing** candidate papers against its **current** criteria. Performs no
database search.

### Authorisation

Any member of the study (`require_study_member`). Not lead-restricted — see FR-023, and note
that `POST /studies/{id}/searches` is member-level today despite spending more.

### Request

```json
{
  "phase_tag": "rescreen-after-criteria-revision"
}
```

| Field        | Type             | Required | Notes                                                       |
| ------------ | ---------------- | -------- | ----------------------------------------------------------- |
| `phase_tag`  | `string`         | No       | Free-text label for the round; defaults to `"rescreen"`     |
| `restart_of` | `string \| null` | No       | Job id of a failed run to resume. Omit to start a new round |

When `restart_of` names a failed run, the new job **reuses that run's reviewer** and therefore
assesses only the candidates that reviewer has not yet judged (R5, FR-024). When it is absent, a
new reviewer round is created.

### Responses

#### `202 Accepted` — enqueued

```json
{
  "job_id": "arq:rescreen:9f2c…",
  "reviewer_id": 41,
  "round": 2,
  "candidates_to_assess": 800
}
```

`job_id` is fed to the existing progress endpoint. `candidates_to_assess` is the count the run
starts with — for a restart, only the outstanding remainder.

#### `409 Conflict` — another assessment is in flight (FR-026)

```json
{
  "detail": {
    "message": "A full search is already running for this study.",
    "blocking_job_id": "arq:full_search:1a7b…",
    "blocking_job_type": "full_search"
  }
}
```

Raised when the study has a `BackgroundJob` in a non-terminal state whose `job_type` is
`full_search`, `snowball_search`, or `rescreen`. **Full search is included deliberately**: its
pipeline screens every candidate it retrieves, so allowing both would interleave two automated
rounds over the same papers.

The response **must** name the blocking run — a bare 409 gives the researcher nothing to act on.

#### `422 Unprocessable Entity` — nothing to assess

Returned when the study has no candidate papers, or when `restart_of` names a run that is not in
a failed state. An empty run is never queued.

#### `404 Not Found`

Study does not exist, or the caller is not a member of it.

---

## Progress and completion

Reported through the existing job endpoint — no new progress surface.

```json
{
  "job_id": "arq:rescreen:9f2c…",
  "status": "running",
  "progress_pct": 37,
  "progress_detail": {
    "assessed": 296,
    "total": 800,
    "reviewer_id": 41,
    "round": 2
  }
}
```

### Terminal states

| Status     | Meaning                                                                                                    |
| ---------- | ---------------------------------------------------------------------------------------------------------- |
| `complete` | Every candidate in scope holds a decision by this round's reviewer                                         |
| `failed`   | The run stopped early. `progress_detail.assessed` records real coverage; `error_message` records the cause |

**A run is never reported `complete` while its coverage is partial** (FR-024). This is why the
screening pass must propagate provider errors rather than returning a rejection — see research
R3. A paper the screener never actually judged must not be counted as assessed, and must not be
persisted as rejected.

---

## Invariants the implementation must uphold

| #   | Invariant                                                                                           | Requirement |
| --- | --------------------------------------------------------------------------------------------------- | ----------- |
| 1   | No database search is performed. The candidate set is exactly what already exists                   | FR-017      |
| 2   | Decisions are written under a reviewer distinct from every previous round                           | FR-019, R2  |
| 3   | A decision recorded by a human is never modified or overridden by a run                             | FR-019      |
| 4   | Assessments completed before a failure are retained                                                 | FR-024      |
| 5   | A restart assesses only candidates the round has not reached — derived from decisions, not a cursor | FR-024, R5  |
| 6   | Two automated rounds never run concurrently over the same candidates                                | FR-026      |
| 7   | Any study member may start a run                                                                    | FR-023      |

---

## Test obligations

| Level       | Case                                                                        |
| ----------- | --------------------------------------------------------------------------- |
| Unit        | Outstanding-candidate derivation, including after a partial run             |
| Unit        | In-flight guard matches each blocking job type and ignores terminal states  |
| Integration | `202` enqueues a job and creates exactly one new reviewer                   |
| Integration | `409` while a full search runs, and the payload names the blocking job      |
| Integration | `422` with no candidates                                                    |
| Integration | Failure mid-run leaves assessments in place; restart covers only the rest   |
| Integration | Human decisions survive a run untouched                                     |
| e2e         | Journey 4 — start from the UI, watch progress, confirm the prior round kept |
