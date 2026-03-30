# API Contracts: 008-Rapid-Review-Workflow

**Generated**: 2026-03-21
**Base path**: `/api/v1/rapid/`
**Auth**: JWT bearer (all routes except public share endpoint)
**Access control**: All `/api/v1/rapid/studies/{study_id}/` routes require the
authenticated user to be a member of the study via the `Reviewer` model.

---

## Protocol Routes

### `GET /api/v1/rapid/studies/{study_id}/protocol`

Retrieve the Rapid Review protocol for a study.

**Response 200**:
```json
{
  "id": 1,
  "study_id": 42,
  "status": "DRAFT",
  "practical_problem": "How to reduce onboarding time in SMEs?",
  "research_questions": ["What strategies exist to reduce onboarding time?"],
  "time_budget_days": 14,
  "effort_budget_hours": 40,
  "context_restrictions": [
    {"type": "company_size", "description": "Small and medium enterprises only"}
  ],
  "dissemination_medium": "Evidence Briefing",
  "problem_scoping_notes": null,
  "search_strategy_notes": null,
  "inclusion_criteria": ["Published 2015–2025"],
  "exclusion_criteria": ["Grey literature"],
  "single_reviewer_mode": false,
  "single_source_acknowledged": false,
  "quality_appraisal_mode": "FULL",
  "version_id": 1,
  "created_at": "2026-03-21T10:00:00Z",
  "updated_at": "2026-03-21T10:00:00Z"
}
```

**Errors**: `404` if study not found or not a Rapid Review study.

---

### `PUT /api/v1/rapid/studies/{study_id}/protocol`

Update the protocol. If the protocol is currently `VALIDATED`, this resets it to `DRAFT`
and marks all `CandidatePaper` records as `PROTOCOL_INVALIDATED`.

**Query params**:
- `acknowledge_invalidation=true` — Required if protocol is currently `VALIDATED`.
  If omitted and protocol is `VALIDATED`, returns `409 Conflict`.

**Request body**: Same shape as the GET response (all fields optional, partial update).

**Response 200**: Updated `RRProtocolResponse` (same shape as GET).

**Errors**:
- `409 Conflict` — Protocol is VALIDATED and `?acknowledge_invalidation=true` was not
  provided. Body: `{"detail": "Protocol is validated. All collected papers will be invalidated. Resend with ?acknowledge_invalidation=true to confirm.", "papers_at_risk": 23}`
- `404` if study not found.

---

### `POST /api/v1/rapid/studies/{study_id}/protocol/validate`

Attempt to validate the protocol. Runs pre-validation checks:
1. At least one `PractitionerStakeholder` exists for this study.
2. `research_questions` is non-empty.
3. `practical_problem` is non-empty.
4. If `single_source_acknowledged = false` and only one database is selected, returns
   validation error.

**Response 200**: Updated protocol with `status = VALIDATED`.

**Response 422 Unprocessable Entity**:
```json
{
  "detail": "Protocol validation failed",
  "errors": [
    "At least one practitioner stakeholder must be defined before validation.",
    "Research questions must not be empty."
  ]
}
```

---

## Stakeholder Routes

### `GET /api/v1/rapid/studies/{study_id}/stakeholders`

**Response 200**: `list[StakeholderResponse]`
```json
[
  {
    "id": 1,
    "study_id": 42,
    "name": "Jane Smith",
    "role_title": "Engineering Manager",
    "organisation": "Acme Corp",
    "involvement_type": "PROBLEM_DEFINER",
    "created_at": "2026-03-21T10:00:00Z",
    "updated_at": "2026-03-21T10:00:00Z"
  }
]
```

---

### `POST /api/v1/rapid/studies/{study_id}/stakeholders`

**Request body**:
```json
{
  "name": "Jane Smith",
  "role_title": "Engineering Manager",
  "organisation": "Acme Corp",
  "involvement_type": "PROBLEM_DEFINER"
}
```

**Response 201**: `StakeholderResponse`

---

### `PUT /api/v1/rapid/studies/{study_id}/stakeholders/{stakeholder_id}`

**Request body**: Same as POST (all fields optional, partial update).
**Response 200**: `StakeholderResponse`
**Errors**: `404` if stakeholder not found.

---

### `DELETE /api/v1/rapid/studies/{study_id}/stakeholders/{stakeholder_id}`

**Response 204 No Content**

**Note**: If this is the last stakeholder and the protocol is `VALIDATED`, the deletion
resets the protocol to `DRAFT` (with the same acknowledgment flow as protocol PUT).

---

## Threats to Validity Routes

### `GET /api/v1/rapid/studies/{study_id}/threats`

Read-only. Threats are auto-created by the service layer when restrictions are applied.

**Response 200**: `list[ThreatResponse]`
```json
[
  {
    "id": 1,
    "study_id": 42,
    "threat_type": "YEAR_RANGE",
    "description": "Search restricted to publications from 2015 to 2025.",
    "source_detail": "2015–2025",
    "created_at": "2026-03-21T11:00:00Z"
  }
]
```

---

## Narrative Synthesis Routes

### `GET /api/v1/rapid/studies/{study_id}/synthesis`

Returns all synthesis sections for the study (one per research question).
Sections are auto-created when the protocol is first validated.

**Response 200**: `list[NarrativeSectionResponse]`
```json
[
  {
    "id": 1,
    "study_id": 42,
    "rq_index": 0,
    "research_question": "What strategies exist to reduce onboarding time?",
    "narrative_text": null,
    "ai_draft_text": null,
    "is_complete": false,
    "ai_draft_job_id": null,
    "created_at": "2026-03-21T12:00:00Z",
    "updated_at": "2026-03-21T12:00:00Z"
  }
]
```

---

### `PUT /api/v1/rapid/studies/{study_id}/synthesis/{section_id}`

Update a narrative section's text or completion status.

**Request body**:
```json
{
  "narrative_text": "Studies consistently show that structured mentoring...",
  "is_complete": true
}
```

**Response 200**: `NarrativeSectionResponse`

---

### `POST /api/v1/rapid/studies/{study_id}/synthesis/{section_id}/ai-draft`

Enqueue an ARQ background job to generate an AI draft for this section.

**Response 202 Accepted**:
```json
{
  "job_id": "arq:job:abc123",
  "section_id": 1,
  "status": "queued"
}
```

**Notes**:
- If a draft job is already running for this section, returns `409 Conflict`.
- The draft is written to `ai_draft_text` when the job completes. The researcher must
  explicitly copy or edit the draft into `narrative_text` — it is never auto-applied.

---

### `POST /api/v1/rapid/studies/{study_id}/synthesis/complete`

Mark the overall synthesis as complete (gates Evidence Briefing generation).
All sections must have `is_complete = true`.

**Response 200**: `{"synthesis_complete": true}`

**Response 422**: If any section is not complete:
```json
{
  "detail": "All synthesis sections must be marked complete before synthesis can be finalised.",
  "incomplete_sections": [0, 2]
}
```

---

## Evidence Briefing Routes

### `GET /api/v1/rapid/studies/{study_id}/briefings`

List all Evidence Briefing versions for the study.

**Response 200**: `list[BriefingSummaryResponse]`
```json
[
  {
    "id": 3,
    "study_id": 42,
    "version_number": 2,
    "status": "PUBLISHED",
    "title": "Evidence on Onboarding Time Reduction in SMEs",
    "generated_at": "2026-03-21T14:00:00Z",
    "pdf_available": true,
    "html_available": true
  },
  {
    "id": 1,
    "study_id": 42,
    "version_number": 1,
    "status": "DRAFT",
    "title": "Evidence on Onboarding Time Reduction in SMEs",
    "generated_at": "2026-03-21T13:00:00Z",
    "pdf_available": true,
    "html_available": true
  }
]
```

---

### `POST /api/v1/rapid/studies/{study_id}/briefings`

Generate a new Evidence Briefing version from the current synthesis state.
Requires synthesis to be marked complete.

**Response 202 Accepted**:
```json
{
  "job_id": "arq:job:def456",
  "status": "queued",
  "estimated_version_number": 3
}
```

---

### `GET /api/v1/rapid/studies/{study_id}/briefings/{briefing_id}`

**Response 200**: Full `BriefingResponse`
```json
{
  "id": 3,
  "study_id": 42,
  "version_number": 2,
  "status": "PUBLISHED",
  "title": "Evidence on Onboarding Time Reduction in SMEs",
  "summary": "This briefing reports scientific evidence on onboarding time reduction...",
  "findings": {
    "0": "Three primary strategies were identified: structured mentoring..."
  },
  "target_audience": "Engineering managers in SMEs with fewer than 250 employees...",
  "reference_complementary": "Full protocol and study list: https://example.com/rr/42",
  "institution_logos": [],
  "pdf_available": true,
  "html_available": true,
  "generated_at": "2026-03-21T14:00:00Z",
  "created_at": "2026-03-21T14:00:00Z",
  "updated_at": "2026-03-21T14:05:00Z"
}
```

---

### `POST /api/v1/rapid/studies/{study_id}/briefings/{briefing_id}/publish`

Promote this version to `PUBLISHED`. Atomically demotes the previous published version
to `DRAFT`.

**Response 200**: Updated `BriefingResponse` with `status = PUBLISHED`.

---

### `GET /api/v1/rapid/studies/{study_id}/briefings/{briefing_id}/export`

Download the Evidence Briefing in the requested format.

**Query params**: `format=pdf|html` (required)

**Response 200**: `StreamingResponse` with appropriate `Content-Type` and
`Content-Disposition: attachment; filename="evidence-briefing-v{N}.{ext}"`.

**Errors**: `404` if the format file has not been generated yet.

---

### `POST /api/v1/rapid/studies/{study_id}/briefings/{briefing_id}/share-token`

Generate a new shareable token for the published version of this study's briefing.

**Response 201**:
```json
{
  "token": "abc123xyz...",
  "share_url": "/public/briefings/abc123xyz...",
  "briefing_id": 3,
  "created_at": "2026-03-21T14:10:00Z",
  "revoked_at": null,
  "expires_at": null
}
```

**Errors**: `422` if no published version exists for this study.

---

### `DELETE /api/v1/rapid/studies/{study_id}/briefings/share-token/{token}`

Revoke a share token (sets `revoked_at = NOW()`).

**Response 204 No Content**

---

## Public Share Endpoint (No Authentication Required)

### `GET /api/v1/public/briefings/{token}`

Serve the currently `PUBLISHED` Evidence Briefing for the token's study.

**Response 200**: `PublicBriefingResponse` (same fields as `BriefingResponse` minus
internal IDs and file paths; threats to validity included).

**Errors**:
- `404` — Token not found, revoked, or expired.
- `404` — No published briefing exists for the study.

---

### `GET /api/v1/public/briefings/{token}/export`

Download the published briefing as PDF or HTML (no authentication required).

**Query params**: `format=pdf|html`

**Response 200**: `StreamingResponse`

**Errors**: `404` if token invalid/revoked or format not generated.

---

## Phase Gate (Existing endpoint, extended)

### `GET /api/v1/studies/{study_id}/phases`

Existing endpoint. Rapid Review studies now dispatch to `get_rr_unlocked_phases`.

**RR Phase unlock rules**:
| Phase | Unlock Condition |
|-------|-----------------|
| 1 | Always unlocked |
| 2 | `RapidReviewProtocol.status == VALIDATED` |
| 3 | At least one completed `SearchExecution` for this study |
| 4 | All accepted papers have quality appraisal complete (or `quality_appraisal_mode != FULL`) |
| 5 | At least one `RRNarrativeSynthesisSection` with `is_complete = true` exists |

**Response 200**: `{"unlocked_phases": [1, 2, 3]}` (existing format, unchanged)
