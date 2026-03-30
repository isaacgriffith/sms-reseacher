# API Contracts: Tertiary Studies Workflow

**Feature**: 009-tertiary-studies-workflow
**Base path**: `/api/v1`
**Auth**: Bearer JWT required on all endpoints unless noted

---

## Tertiary Study Protocol

### GET `/tertiary/studies/{study_id}/protocol`

Returns the protocol for a Tertiary Study. Creates a draft protocol if none exists.

**Path params**: `study_id: int`

**Response 200**:
```json
{
  "id": 1,
  "study_id": 42,
  "status": "draft",
  "background": "string | null",
  "research_questions": ["string"] ,
  "secondary_study_types": ["SLR", "SMS", "RAPID_REVIEW"],
  "inclusion_criteria": ["string"],
  "exclusion_criteria": ["string"],
  "recency_cutoff_year": 2015,
  "search_strategy": "string | null",
  "quality_threshold": 0.6,
  "synthesis_approach": "narrative | thematic | meta_analysis | null",
  "dissemination_strategy": "string | null",
  "version_id": 0,
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

**Response 404**: Study not found or not of type `TERTIARY`.

---

### PUT `/tertiary/studies/{study_id}/protocol`

Update the protocol. Returns updated record.

**Path params**: `study_id: int`

**Request body** (all fields optional, partial update):
```json
{
  "background": "string | null",
  "research_questions": ["string"],
  "secondary_study_types": ["SLR", "SMS"],
  "inclusion_criteria": ["string"],
  "exclusion_criteria": ["string"],
  "recency_cutoff_year": 2015,
  "search_strategy": "string | null",
  "quality_threshold": 0.6,
  "synthesis_approach": "narrative",
  "dissemination_strategy": "string | null",
  "version_id": 0
}
```

**Response 200**: Updated protocol object (same shape as GET).
**Response 409**: Optimistic lock conflict (`version_id` mismatch).
**Response 422**: Validation error.

---

### POST `/tertiary/studies/{study_id}/protocol/validate`

Validates the protocol and transitions it to `validated` status. Triggers `ProtocolReviewerAgent` as a background ARQ job.

**Path params**: `study_id: int`

**Response 202**:
```json
{
  "job_id": "arq:job:uuid",
  "status": "queued"
}
```

**Response 409**: Protocol already validated, or study type mismatch.

---

## Seed Imports

### GET `/tertiary/studies/{study_id}/seed-imports`

Lists all seed import operations for a Tertiary Study.

**Path params**: `study_id: int`

**Response 200**:
```json
[
  {
    "id": 1,
    "target_study_id": 42,
    "source_study_id": 17,
    "source_study_title": "string",
    "source_study_type": "SMS",
    "imported_at": "ISO-8601",
    "records_added": 34,
    "records_skipped": 2,
    "imported_by_user_id": 5
  }
]
```

---

### POST `/tertiary/studies/{study_id}/seed-imports`

Imports included papers from a source platform study into this Tertiary Study's candidate corpus.

**Path params**: `study_id: int`

**Request body**:
```json
{
  "source_study_id": 17
}
```

**Response 201**:
```json
{
  "id": 1,
  "records_added": 34,
  "records_skipped": 2,
  "imported_at": "ISO-8601"
}
```

**Response 404**: Source study not found.
**Response 409**: Import from this source study already exists for this Tertiary Study.
**Response 422**: Source study has no included papers.

---

## Tertiary Data Extraction

### GET `/tertiary/studies/{study_id}/extractions`

Lists all tertiary extraction records for a study.

**Path params**: `study_id: int`
**Query params**: `status: pending | ai_complete | validated | human_reviewed` (optional filter)

**Response 200**:
```json
[
  {
    "id": 1,
    "candidate_paper_id": 88,
    "paper_title": "string",
    "secondary_study_type": "SLR | SMS | RAPID_REVIEW | UNKNOWN | null",
    "research_questions_addressed": ["string"],
    "databases_searched": ["string"],
    "study_period_start": 2010,
    "study_period_end": 2020,
    "primary_study_count": 45,
    "synthesis_approach_used": "string | null",
    "key_findings": "string | null",
    "research_gaps": "string | null",
    "reviewer_quality_rating": 0.75,
    "extraction_status": "pending",
    "extracted_by_agent": "string | null",
    "validated_by_reviewer_id": null,
    "version_id": 0,
    "created_at": "ISO-8601",
    "updated_at": "ISO-8601"
  }
]
```

---

### GET `/tertiary/studies/{study_id}/extractions/{extraction_id}`

Returns a single extraction record.

**Response 200**: Single extraction object (same shape as list item).
**Response 404**: Not found.

---

### PUT `/tertiary/studies/{study_id}/extractions/{extraction_id}`

Update an extraction record (human review).

**Request body** (all fields optional):
```json
{
  "secondary_study_type": "SLR",
  "research_questions_addressed": ["string"],
  "databases_searched": ["ACM DL", "IEEE Xplore"],
  "study_period_start": 2010,
  "study_period_end": 2022,
  "primary_study_count": 52,
  "synthesis_approach_used": "narrative synthesis",
  "key_findings": "string",
  "research_gaps": "string",
  "reviewer_quality_rating": 0.8,
  "extraction_status": "human_reviewed",
  "version_id": 0
}
```

**Response 200**: Updated extraction object.
**Response 409**: Optimistic lock conflict.

---

### POST `/tertiary/studies/{study_id}/extractions/ai-assist`

Triggers AI-assisted pre-population of extraction fields for all pending papers in this study.

**Response 202**:
```json
{
  "job_id": "arq:job:uuid",
  "status": "queued",
  "paper_count": 12
}
```

---

## Tertiary Report

### GET `/tertiary/studies/{study_id}/report`

Generates and returns the Tertiary Study report. Includes the landscape-of-secondary-studies section.

**Path params**: `study_id: int`
**Query params**: `format: json | csv | markdown` (default `json`)

**Response 200** (JSON format):
```json
{
  "study_id": 42,
  "study_name": "string",
  "generated_at": "ISO-8601",
  "background": "string",
  "review_questions": ["string"],
  "protocol_summary": "string",
  "search_process": "string",
  "inclusion_exclusion_decisions": "string",
  "quality_assessment_results": "string",
  "extracted_data": "string",
  "synthesis_results": "string",
  "validity_discussion": "string",
  "recommendations": "string",
  "landscape_of_secondary_studies": {
    "timeline_summary": "string",
    "research_question_evolution": "string",
    "synthesis_method_shifts": "string"
  }
}
```

**Response 404**: Study not found or not of type `TERTIARY`.
**Response 409**: Study has not reached synthesis phase.

---

## Existing Endpoints Reused Without Modification

The following endpoints already support Tertiary Studies by operating on `study_id` generically:

| Endpoint | Use in Tertiary Workflow |
|----------|--------------------------|
| `GET /studies/{id}/phases` | Phase gate dispatch (tertiary gate registered) |
| `GET/POST /slr/studies/{id}/quality-checklist` | Checklist setup with secondary-study items |
| `GET/POST /slr/studies/{id}/inter-rater-reliability` | Cohen's κ across reviewers |
| `POST /slr/studies/{id}/synthesis` | Triggers synthesis job (narrative/thematic strategies added) |
| `GET /slr/studies/{id}/synthesis/{result_id}` | Poll synthesis result |
| `GET/POST researcher-mcp search_papers` | Multi-database search |
