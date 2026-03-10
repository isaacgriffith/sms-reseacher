# REST API Contracts: SMS Workflow System (v1)

**Branch**: `002-sms-workflow` | **Date**: 2026-03-10
**Base path**: `/api/v1`
**Auth**: Bearer JWT in `Authorization` header for all routes except `/auth/login`

---

## Auth

### `POST /auth/login`
Authenticate and receive a JWT session token.

**Request**:
```json
{ "email": "string", "password": "string" }
```

**Response 200**:
```json
{ "access_token": "string", "token_type": "bearer", "user_id": 1, "display_name": "string" }
```

**Response 401**: Invalid credentials.

---

### `GET /auth/me`
Return the current authenticated user's profile.

**Response 200**:
```json
{ "id": 1, "email": "string", "display_name": "string", "groups": [{ "id": 1, "name": "string", "role": "admin|member" }] }
```

---

## Research Groups

### `GET /groups`
List all research groups the current user belongs to.

**Response 200**: `[{ "id": 1, "name": "string", "role": "admin|member", "study_count": 3 }]`

### `POST /groups`
Create a new research group (current user becomes admin).

**Request**: `{ "name": "string" }`
**Response 201**: `{ "id": 1, "name": "string" }`

### `GET /groups/{group_id}/members`
**Response 200**: `[{ "user_id": 1, "display_name": "string", "email": "string", "role": "admin|member" }]`

### `POST /groups/{group_id}/members`
Invite a user by email. Admin only.

**Request**: `{ "email": "string", "role": "admin|member" }`
**Response 201**: `{ "user_id": 1, "role": "member" }`

### `DELETE /groups/{group_id}/members/{user_id}`
Remove a member. Admin only. Cannot remove the last admin.

**Response 204**

---

## Studies

### `GET /groups/{group_id}/studies`
List all studies for a research group.

**Response 200**:
```json
[{
  "id": 1, "name": "string", "topic": "string",
  "study_type": "SMS|SLR|Tertiary|Rapid",
  "status": "draft|active|completed|archived",
  "current_phase": 1,
  "created_at": "ISO8601"
}]
```

### `POST /groups/{group_id}/studies`
Create a new study via the wizard payload.

**Request**:
```json
{
  "name": "string",
  "topic": "string",
  "study_type": "SMS",
  "motivation": "string|null",
  "research_objectives": ["string"],
  "research_questions": ["string"],
  "member_ids": [1, 2],
  "reviewers": [
    { "type": "human", "user_id": 1 },
    { "type": "ai_agent", "agent_name": "screener-v2", "agent_config": {} }
  ],
  "snowball_threshold": 5
}
```

**Response 201**: Full study object with `id`.

### `GET /studies/{study_id}`
**Response 200**: Full study object including `current_phase`, `unlocked_phases: [1,2]`, all metadata.

### `PATCH /studies/{study_id}`
Update study metadata (name, topic, motivation, research questions, etc.).

**Request**: Partial update (any subset of study fields)
**Response 200**: Updated study object.

### `POST /studies/{study_id}/archive`
**Response 200**: `{ "status": "archived" }`

### `DELETE /studies/{study_id}`
Permanent delete. Admin only.
**Response 204**

---

## Phase 1: PICO/C & Seeds

### `GET /studies/{study_id}/pico`
**Response 200**: Full `PICOComponent` object, or `404` if not yet defined.

### `PUT /studies/{study_id}/pico`
Create or replace PICO/C components.

**Request**:
```json
{
  "variant": "PICO|PICOS|PICOT|SPIDER|PCC",
  "population": "string|null",
  "intervention": "string|null",
  "comparison": "string|null",
  "outcome": "string|null",
  "context": "string|null",
  "extra_fields": {}
}
```
**Response 200**: Saved `PICOComponent`. Unlocks Phase 2 if previously locked.

### `POST /studies/{study_id}/pico/refine`
Request AI suggestions for PICO/C refinement.

**Request**: `{ "component": "population|intervention|comparison|outcome|context" }`
**Response 200**: `{ "suggestions": ["string", "string"] }`

### `GET /studies/{study_id}/seeds/papers`
**Response 200**: `[{ "id": 1, "paper": { ...paper fields... }, "added_by": "user|agent" }]`

### `POST /studies/{study_id}/seeds/papers`
**Request**: `{ "paper_id": 1 }` or `{ "doi": "10.xxx/yyy" }` or `{ "title": "...", "authors": [...] }`
**Response 201**: Created `SeedPaper` object.

### `DELETE /studies/{study_id}/seeds/papers/{seed_id}`
**Response 204**

### `POST /studies/{study_id}/seeds/librarian`
Trigger the Librarian AI agent to suggest seed papers and authors.

**Response 202**: `{ "job_id": "string" }` — results available when job completes.

### `GET /studies/{study_id}/seeds/authors`
**Response 200**: `[{ "id": 1, "author_name": "string", "institution": "string|null", "profile_url": "string|null" }]`

### `POST /studies/{study_id}/seeds/authors`
**Request**: `{ "author_name": "string", "institution": "string|null", "profile_url": "string|null" }`
**Response 201**: Created `SeedAuthor`.

---

## Phase 2: Search

### `GET /studies/{study_id}/criteria/inclusion`
**Response 200**: `[{ "id": 1, "description": "string", "order_index": 0 }]`

### `POST /studies/{study_id}/criteria/inclusion`
**Request**: `{ "description": "string", "order_index": 0 }`
**Response 201**

### `DELETE /studies/{study_id}/criteria/inclusion/{criterion_id}`
**Response 204**

*(Same pattern for `/criteria/exclusion`)*

### `GET /studies/{study_id}/search-strings`
**Response 200**: `[{ "id": 1, "version": 1, "string_text": "...", "is_active": true, "created_at": "..." }]`

### `POST /studies/{study_id}/search-strings`
Manually create a new search string version.

**Request**: `{ "string_text": "string" }`
**Response 201**: New `SearchString` with `is_active: true` (previous deactivated).

### `POST /studies/{study_id}/search-strings/generate`
AI-generate a search string from PICO/C + seed paper keywords.

**Response 200**: `{ "search_string": { ...object... }, "iteration": { ...SearchStringIteration... } }`

### `POST /studies/{study_id}/search-strings/{string_id}/test`
Execute test search and compare against seed test set.

**Request**: `{ "databases": ["acm", "ieee"] }` (optional, defaults to all configured)
**Response 202**: `{ "job_id": "string" }` — iteration results available when job completes.

### `GET /studies/{study_id}/search-strings/{string_id}/iterations`
**Response 200**: `[{ "id": 1, "iteration_number": 1, "result_set_count": 1200, "test_set_recall": 0.85, "ai_adequacy_judgment": "...", "human_approved": null }]`

### `PATCH /studies/{study_id}/search-strings/{string_id}/iterations/{iter_id}`
Human approval of a test iteration.

**Request**: `{ "human_approved": true }`
**Response 200**

### `POST /studies/{study_id}/searches`
Trigger full search execution using active search string.

**Response 202**: `{ "job_id": "string", "search_execution_id": 1 }`

---

## Candidate Papers & Decisions

### `GET /studies/{study_id}/papers`
List candidate papers with filtering.

**Query params**: `status=accepted|rejected|duplicate|pending`, `phase_tag=initial-search|backward-search-1`, `page=1`, `page_size=50`
**Response 200**:
```json
{
  "items": [{ "id": 1, "paper": {...}, "current_status": "pending", "phase_tag": "initial-search", "decisions": [...] }],
  "total": 450, "page": 1, "page_size": 50
}
```

### `GET /studies/{study_id}/papers/{candidate_id}`
Full candidate paper detail including all decisions and extraction status.

**Response 200**

### `POST /studies/{study_id}/papers/{candidate_id}/decisions`
Submit a reviewer decision (AI or human).

**Request**:
```json
{
  "reviewer_id": 1,
  "decision": "accepted|rejected|duplicate",
  "reasons": [{ "criterion_id": 1, "criterion_type": "exclusion", "text": "not peer-reviewed" }],
  "is_override": false
}
```
**Response 201**: `PaperDecision` object.

### `POST /studies/{study_id}/papers/{candidate_id}/resolve-conflict`
Resolve a reviewer disagreement by submitting a final binding decision.

**Request**: `{ "reviewer_id": 1, "final_decision": "accepted|rejected|duplicate", "resolution_note": "string" }`
**Response 200**: Updated `CandidatePaper` object.

---

## Phase 3: Data Extraction

### `GET /studies/{study_id}/extractions`
List all extractions with status filter.

**Query params**: `status=pending|ai_complete|validated|human_reviewed`, `page=1`, `page_size=50`

### `GET /studies/{study_id}/extractions/{extraction_id}`
Full extraction detail with audit history.

### `PATCH /studies/{study_id}/extractions/{extraction_id}`
Human edit of extracted fields. Uses optimistic locking.

**Request**:
```json
{
  "version_id": 3,
  "research_type": "evaluation",
  "summary": "...",
  "open_codings": [...],
  "keywords": [...]
}
```

**Response 200**: Updated extraction with new `version_id`.
**Response 409 Conflict**:
```json
{
  "error": "conflict",
  "your_version": { ...client_payload... },
  "current_version": { ...server_state... }
}
```

### `POST /studies/{study_id}/extractions/batch-run`
Trigger batch data extraction for all accepted papers without completed extractions.

**Response 202**: `{ "job_id": "string" }`

---

## Background Jobs & Progress (SSE)

### `GET /studies/{study_id}/jobs`
List recent background jobs for a study.

**Response 200**: `[{ "id": "string", "job_type": "...", "status": "running", "progress_pct": 42, "progress_detail": {...} }]`

### `GET /jobs/{job_id}/progress`
**SSE stream** — sends `text/event-stream` events until job completes or client disconnects.

**Event format**:
```
event: progress
data: {"job_id": "...", "status": "running", "progress_pct": 55, "phase": "backward-search-1", "papers_found": 320, "current_database": "acm"}

event: complete
data: {"job_id": "...", "status": "completed", "progress_pct": 100}

event: error
data: {"job_id": "...", "status": "failed", "error_message": "ACM rate limit exceeded"}
```

---

## Phase 4: Validity Discussion

### `GET /studies/{study_id}/validity`
**Response 200**: `{ "descriptive": "...", "theoretical": "...", "generalizability_internal": "...", "generalizability_external": "...", "interpretive": "...", "repeatability": "..." }`

### `PUT /studies/{study_id}/validity`
**Request**: Any subset of the six validity fields.
**Response 200**

### `POST /studies/{study_id}/validity/generate`
AI-generate validity discussion pre-fill.
**Response 202**: `{ "job_id": "string" }`

---

## Phase 5: Quality Evaluation

### `GET /studies/{study_id}/quality-reports`
**Response 200**: `[{ "id": 1, "version": 1, "total_score": 7, "generated_at": "..." }]`

### `GET /studies/{study_id}/quality-reports/{report_id}`
Full report with rubric details and recommendations.

### `POST /studies/{study_id}/quality-reports`
Trigger quality judge evaluation.
**Response 202**: `{ "job_id": "string" }`

---

## Results & Export

### `GET /studies/{study_id}/results`
Summary of all generated visualizations.

**Response 200**:
```json
{
  "domain_model": { "id": 1, "version": 2, "generated_at": "..." },
  "classification_charts": [{ "id": 1, "chart_type": "year", "version": 1 }],
  "metrics_summary": { "total_accepted": 87, "date_range": "2015-2024", "top_venues": [...] }
}
```

### `POST /studies/{study_id}/results/generate`
Trigger full result generation (domain model + all charts).
**Response 202**: `{ "job_id": "string" }`

### `GET /studies/{study_id}/results/charts/{chart_id}/svg`
**Response 200**: `Content-Type: image/svg+xml` — raw SVG content.

### `GET /studies/{study_id}/results/domain-model/svg`
**Response 200**: `Content-Type: image/svg+xml`

### `POST /studies/{study_id}/export`
Trigger export bundle generation.

**Request**: `{ "format": "svg_only|json_only|csv_json|full_archive" }`
**Response 202**: `{ "job_id": "string" }`

### `GET /studies/{study_id}/export/{export_id}/download`
Download completed export file.
**Response 200**: File download with appropriate `Content-Type` (application/zip for archive, application/json, text/csv, or application/zip for SVGs).

---

## Search Metrics

### `GET /studies/{study_id}/metrics`
Aggregated metrics across all search phases.

**Response 200**:
```json
{
  "phases": [
    { "phase_tag": "initial-search", "total_identified": 1200, "accepted": 145, "rejected": 1032, "duplicates": 23 },
    { "phase_tag": "backward-search-1", "total_identified": 87, "accepted": 23, "rejected": 60, "duplicates": 4 }
  ],
  "totals": { "total_identified": 1287, "accepted": 168, "rejected": 1092, "duplicates": 27 }
}
```
