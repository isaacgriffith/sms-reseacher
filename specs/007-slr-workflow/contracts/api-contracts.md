# API Contracts: SLR Workflow (007)

**Branch**: `007-slr-workflow` | **Date**: 2026-03-18

All endpoints are prefixed `/api/v1/` and require JWT authentication (existing pattern). All request/response bodies use `Content-Type: application/json`. Error responses follow the existing `HTTPException` pattern.

New router package: `backend/src/backend/api/v1/slr/` — mounted in the main router at prefix `/slr`.

---

## Review Protocol

### `GET /api/v1/slr/studies/{study_id}/protocol`
Retrieve the current protocol for a study. Returns 404 if no protocol exists yet.

**Response 200**
```json
{
  "id": 1,
  "study_id": 42,
  "status": "draft",
  "background": "...",
  "rationale": "...",
  "research_questions": ["RQ1: ...", "RQ2: ..."],
  "pico_population": "...",
  "pico_intervention": "...",
  "pico_comparison": "...",
  "pico_outcome": "...",
  "pico_context": null,
  "search_strategy": "...",
  "inclusion_criteria": ["..."],
  "exclusion_criteria": ["..."],
  "data_extraction_strategy": "...",
  "synthesis_approach": "descriptive",
  "dissemination_strategy": "...",
  "timetable": "...",
  "review_report": null,
  "created_at": "2026-03-18T10:00:00Z",
  "updated_at": "2026-03-18T10:00:00Z"
}
```

---

### `PUT /api/v1/slr/studies/{study_id}/protocol`
Create or update the draft protocol. Blocked if `status = validated`.

**Request Body**
```json
{
  "background": "...",
  "rationale": "...",
  "research_questions": ["RQ1: ...", "RQ2: ..."],
  "pico_population": "...",
  "pico_intervention": "...",
  "pico_comparison": "...",
  "pico_outcome": "...",
  "pico_context": null,
  "search_strategy": "...",
  "inclusion_criteria": ["..."],
  "exclusion_criteria": ["..."],
  "data_extraction_strategy": "...",
  "synthesis_approach": "descriptive",
  "dissemination_strategy": "...",
  "timetable": "..."
}
```

**Response 200**: Same as GET.
**Error 409**: Protocol already validated (cannot edit).

---

### `POST /api/v1/slr/studies/{study_id}/protocol/submit-for-review`
Submits the protocol to the AI reviewer agent (async ARQ job). Sets `status = under_review`.

**Response 202**
```json
{ "job_id": "uuid-...", "status": "under_review" }
```

**Error 422**: Protocol incomplete (required fields missing).

---

### `POST /api/v1/slr/studies/{study_id}/protocol/validate`
Researcher approves the protocol. Sets `status = validated`.

**Response 200**
```json
{ "status": "validated" }
```

**Error 422**: Protocol has not been reviewed yet (`review_report` is null).

---

## Quality Assessment

### `GET /api/v1/slr/studies/{study_id}/quality-checklist`
Get the study's quality assessment checklist and items.

**Response 200**
```json
{
  "id": 1,
  "study_id": 42,
  "name": "SLR Quality Checklist v1",
  "description": "...",
  "items": [
    {
      "id": 10,
      "order": 1,
      "question": "Is the study design clearly described?",
      "scoring_method": "binary",
      "weight": 1.0
    }
  ]
}
```

---

### `PUT /api/v1/slr/studies/{study_id}/quality-checklist`
Create or replace the checklist.

**Request Body**
```json
{
  "name": "...",
  "description": "...",
  "items": [
    { "order": 1, "question": "...", "scoring_method": "binary", "weight": 1.0 }
  ]
}
```

---

### `GET /api/v1/slr/papers/{candidate_paper_id}/quality-scores`
All quality scores submitted by any reviewer for a specific paper.

**Response 200**
```json
{
  "candidate_paper_id": 7,
  "reviewer_scores": [
    {
      "reviewer_id": 3,
      "items": [
        { "checklist_item_id": 10, "score_value": 1.0, "notes": null }
      ],
      "aggregate_quality_score": 0.85
    }
  ]
}
```

---

### `PUT /api/v1/slr/papers/{candidate_paper_id}/quality-scores`
Submit (or update) a reviewer's quality scores for a paper.

**Request Body**
```json
{
  "reviewer_id": 3,
  "scores": [
    { "checklist_item_id": 10, "score_value": 1.0, "notes": null }
  ]
}
```

**Response 200**: Same as GET shape.
**Error 409**: Optimistic lock conflict (`version_id` mismatch).

---

## Inter-Rater Agreement

### `GET /api/v1/slr/studies/{study_id}/inter-rater`
All Kappa records for the study.

**Response 200**
```json
{
  "records": [
    {
      "id": 1,
      "reviewer_a_id": 3,
      "reviewer_b_id": 4,
      "round_type": "title_abstract",
      "phase": "pre_discussion",
      "kappa_value": 0.62,
      "kappa_undefined_reason": null,
      "n_papers": 120,
      "threshold_met": true,
      "created_at": "2026-03-18T11:00:00Z"
    }
  ]
}
```

---

### `POST /api/v1/slr/studies/{study_id}/inter-rater/compute`
Trigger a Kappa computation between two reviewers for a given round.

**Request Body**
```json
{
  "reviewer_a_id": 3,
  "reviewer_b_id": 4,
  "round_type": "title_abstract"
}
```

**Response 200**: Single `InterRaterAgreementRecord` (same shape as record above).
**Error 422**: One or both reviewers have not completed their independent assessments for the round.

---

### `POST /api/v1/slr/studies/{study_id}/inter-rater/post-discussion`
Record post-discussion Kappa after the Think-Aloud workflow is complete.

**Request Body**: Same as `/compute`.
**Response 200**: New `InterRaterAgreementRecord` with `phase = "post_discussion"`.

---

## Data Synthesis

### `GET /api/v1/slr/studies/{study_id}/synthesis`
List all synthesis results for a study.

**Response 200**
```json
{
  "results": [
    {
      "id": 1,
      "approach": "descriptive",
      "status": "completed",
      "model_type": null,
      "computed_statistics": { "pooled_mean_difference": 0.42, "ci_lower": 0.11, "ci_upper": 0.73 },
      "forest_plot_svg": "<svg>...</svg>",
      "funnel_plot_svg": null,
      "qualitative_themes": null,
      "sensitivity_analysis": { "subsets": [] },
      "created_at": "2026-03-18T12:00:00Z"
    }
  ]
}
```

---

### `POST /api/v1/slr/studies/{study_id}/synthesis`
Start a new synthesis run (async ARQ job).

**Request Body**
```json
{
  "approach": "meta_analysis",
  "model_type": "random",
  "parameters": {
    "heterogeneity_threshold": 0.10,
    "confidence_interval": 0.95
  }
}
```

**Response 202**
```json
{ "synthesis_id": 1, "job_id": "uuid-...", "status": "pending" }
```

**Error 422**: `approach` requires at minimum 3 accepted papers with data; or quality assessment not yet complete.

---

### `GET /api/v1/slr/synthesis/{synthesis_id}`
Retrieve a single synthesis result by ID.

---

## Grey Literature

### `GET /api/v1/slr/studies/{study_id}/grey-literature`
List all grey literature sources for a study.

**Response 200**
```json
{
  "sources": [
    {
      "id": 1,
      "study_id": 42,
      "source_type": "dissertation",
      "title": "...",
      "authors": "...",
      "year": 2024,
      "url": null,
      "description": "...",
      "created_at": "2026-03-18T09:00:00Z"
    }
  ]
}
```

---

### `POST /api/v1/slr/studies/{study_id}/grey-literature`
Add a grey literature source.

**Request Body**
```json
{
  "source_type": "technical_report",
  "title": "...",
  "authors": "...",
  "year": 2025,
  "url": "https://...",
  "description": "..."
}
```

**Response 201**: Created source.

---

### `DELETE /api/v1/slr/studies/{study_id}/grey-literature/{source_id}`
Remove a grey literature source.

**Response 204**: No content.

---

## SLR Phase Gates

### `GET /api/v1/slr/studies/{study_id}/phases`
Returns the SLR-specific unlocked phases (equivalent to the SMS `GET /api/v1/studies/{id}/phases` for SLR studies).

**Response 200**
```json
{
  "unlocked_phases": [1, 2],
  "protocol_status": "validated",
  "quality_complete": false,
  "synthesis_complete": false
}
```

---

## Report Export (extends existing export)

### `GET /api/v1/studies/{study_id}/export/slr-report`
Generate and download a structured SLR report.

**Query params**: `format=latex|markdown|json|csv`

**Response 200**: File download with appropriate `Content-Type` and `Content-Disposition: attachment`.
