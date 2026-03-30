# Data Model: 008-Rapid-Review-Workflow

**Generated**: 2026-03-21
**Migration**: `0016_rapid_review_workflow`
**Module**: `db/src/db/models/rapid_review.py`

---

## New Enums

### `RRProtocolStatus`
| Value | Meaning |
|-------|---------|
| `DRAFT` | Protocol created or reset after edit; search phase gated |
| `VALIDATED` | Protocol validated; search phase unlocked |

### `RRQualityAppraisalMode`
| Value | Meaning |
|-------|---------|
| `FULL` | Standard quality appraisal (uses existing QualityChecklist) |
| `PEER_REVIEWED_ONLY` | Simplified filter: only peer-reviewed venues |
| `SKIPPED` | No quality appraisal; recorded as threat to validity |

### `RRInvolvementType`
| Value | Meaning |
|-------|---------|
| `PROBLEM_DEFINER` | Defined the practical problem motivating the review |
| `ADVISOR` | Provided domain guidance during the review |
| `RECIPIENT` | Intended audience for the Evidence Briefing |

### `RRThreatType`
| Value | Meaning |
|-------|---------|
| `SINGLE_SOURCE` | Only one database searched |
| `YEAR_RANGE` | Search limited by publication year |
| `LANGUAGE` | Search limited by publication language |
| `GEOGRAPHY` | Search limited by geographic area |
| `STUDY_DESIGN` | Search limited to a specific study design type |
| `SINGLE_REVIEWER` | Papers reviewed by a single reviewer |
| `QA_SKIPPED` | Quality appraisal was skipped entirely |
| `QA_SIMPLIFIED` | Quality appraisal simplified to peer-reviewed only |
| `CONTEXT_RESTRICTION` | Inclusion criteria restrict to a specific context |

### `BriefingStatus`
| Value | Meaning |
|-------|---------|
| `DRAFT` | Generated but not yet published |
| `PUBLISHED` | Promoted by researcher; accessible via share token |

### `CandidatePaperStatus` (extension to existing enum)
| New Value | Meaning |
|-----------|---------|
| `PROTOCOL_INVALIDATED` | Protocol was amended after this paper was collected; must be re-screened |

---

## New Tables

### `rapid_review_protocol`

One-per-study protocol record for Rapid Review studies.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK | |
| `study_id` | `Integer` | FK → `study.id`, UNIQUE, NOT NULL | One protocol per study |
| `status` | `Enum(RRProtocolStatus)` | NOT NULL, default `DRAFT` | |
| `practical_problem` | `Text` | nullable | Problem motivating the review |
| `research_questions` | `JSON` | nullable | `list[str]` |
| `time_budget_days` | `Integer` | nullable | Planned review duration |
| `effort_budget_hours` | `Integer` | nullable | Planned person-hours |
| `context_restrictions` | `JSON` | nullable | `list[{type: str, description: str}]` |
| `dissemination_medium` | `String(255)` | nullable | e.g., "Evidence Briefing", "Presentation" |
| `problem_scoping_notes` | `Text` | nullable | Interview/focus-group notes |
| `search_strategy_notes` | `Text` | nullable | |
| `inclusion_criteria` | `JSON` | nullable | `list[str]` |
| `exclusion_criteria` | `JSON` | nullable | `list[str]` |
| `single_reviewer_mode` | `Boolean` | NOT NULL, default `False` | |
| `single_source_acknowledged` | `Boolean` | NOT NULL, default `False` | Set True when single-source threat recorded |
| `quality_appraisal_mode` | `Enum(RRQualityAppraisalMode)` | NOT NULL, default `FULL` | |
| `version_id` | `Integer` | NOT NULL | Optimistic locking (`version_id_col`) |
| `created_at` | `DateTime(timezone=True)` | NOT NULL, server_default `now()` | |
| `updated_at` | `DateTime(timezone=True)` | NOT NULL, server_default `now()`, onupdate `now()` | |

**Relationships**: `study` (many-to-one), `threats` (one-to-many → `rr_threat_to_validity`)

---

### `practitioner_stakeholder`

Named practitioner contacts with no platform account.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK | |
| `study_id` | `Integer` | FK → `study.id`, NOT NULL, indexed | |
| `name` | `String(255)` | NOT NULL | |
| `role_title` | `String(255)` | NOT NULL | |
| `organisation` | `String(255)` | NOT NULL | |
| `involvement_type` | `Enum(RRInvolvementType)` | NOT NULL | |
| `created_at` | `DateTime(timezone=True)` | NOT NULL, server_default `now()` | |
| `updated_at` | `DateTime(timezone=True)` | NOT NULL, server_default `now()`, onupdate `now()` | |

**Validation**: At least one record per study required before protocol can reach `VALIDATED`.

---

### `rr_threat_to_validity`

Auto-created entries when restrictions or omissions are applied to a Rapid Review.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK | |
| `study_id` | `Integer` | FK → `study.id`, NOT NULL, indexed | |
| `threat_type` | `Enum(RRThreatType)` | NOT NULL | |
| `description` | `Text` | NOT NULL | Human-readable explanation |
| `source_detail` | `String(500)` | nullable | e.g., "2015–2025", "English", "RCT only" |
| `created_at` | `DateTime(timezone=True)` | NOT NULL, server_default `now()` | |
| `updated_at` | `DateTime(timezone=True)` | NOT NULL, server_default `now()`, onupdate `now()` | |

**Note**: Records are created automatically by `rr_protocol_service.py` when restrictions
are applied; they are NOT directly created by the researcher.

---

### `rr_narrative_synthesis_section`

One section per research question for the narrative synthesis editor.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK | |
| `study_id` | `Integer` | FK → `study.id`, NOT NULL, indexed | |
| `rq_index` | `Integer` | NOT NULL | Maps to `rapid_review_protocol.research_questions[rq_index]` |
| `narrative_text` | `Text` | nullable | Researcher-authored final content |
| `ai_draft_text` | `Text` | nullable | AI-generated draft (pre-acceptance) |
| `is_complete` | `Boolean` | NOT NULL, default `False` | |
| `created_at` | `DateTime(timezone=True)` | NOT NULL, server_default `now()` | |
| `updated_at` | `DateTime(timezone=True)` | NOT NULL, server_default `now()`, onupdate `now()` | |

**Constraints**: UNIQUE(`study_id`, `rq_index`) — one section per question per study.

**Note**: Sections are created automatically when the protocol is validated, one per
entry in `research_questions`. Deleting a research question from the protocol during
re-edit orphans the section (retained as soft history, not displayed in new synthesis).

---

### `evidence_briefing`

Versioned Evidence Briefing document.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK | |
| `study_id` | `Integer` | FK → `study.id`, NOT NULL, indexed | |
| `version_number` | `Integer` | NOT NULL | Auto-incremented per study (1, 2, 3…) |
| `status` | `Enum(BriefingStatus)` | NOT NULL, default `DRAFT` | At most one `PUBLISHED` per study |
| `title` | `String(500)` | NOT NULL | |
| `summary` | `Text` | NOT NULL | One-paragraph summary |
| `findings` | `JSON` | NOT NULL | `{rq_index: str}` — per-RQ findings text |
| `target_audience` | `Text` | NOT NULL | Audience box content |
| `reference_complementary` | `Text` | nullable | Link/reference to protocol + study list |
| `institution_logos` | `JSON` | nullable | `list[str]` — stored file paths |
| `pdf_path` | `String(1000)` | nullable | Server-side PDF file path |
| `html_path` | `String(1000)` | nullable | Server-side HTML file path |
| `generated_at` | `DateTime(timezone=True)` | NOT NULL | Timestamp of content generation |
| `created_at` | `DateTime(timezone=True)` | NOT NULL, server_default `now()` | |
| `updated_at` | `DateTime(timezone=True)` | NOT NULL, server_default `now()`, onupdate `now()` | |

**Constraints**: UNIQUE(`study_id`, `version_number`).
**Invariant**: At most one row with `status = PUBLISHED` per `study_id`. Enforced at
the service layer in a single transaction (UPDATE previous PUBLISHED → DRAFT, then UPDATE
target → PUBLISHED).

**Relationships**: `share_tokens` (one-to-many → `evidence_briefing_share_token`)

---

### `evidence_briefing_share_token`

Opaque tokens for practitioner access to published Evidence Briefings.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK | |
| `briefing_id` | `Integer` | FK → `evidence_briefing.id`, NOT NULL, indexed | |
| `study_id` | `Integer` | FK → `study.id`, NOT NULL, indexed | Denormalised for access-check performance |
| `created_by_user_id` | `Integer` | FK → `user.id`, NOT NULL | |
| `token` | `String(64)` | UNIQUE, NOT NULL, indexed | `secrets.token_urlsafe(32)` |
| `revoked_at` | `DateTime(timezone=True)` | nullable | NULL = active; set to revoke |
| `expires_at` | `DateTime(timezone=True)` | nullable | NULL = no expiry |
| `created_at` | `DateTime(timezone=True)` | NOT NULL, server_default `now()` | |
| `updated_at` | `DateTime(timezone=True)` | NOT NULL, server_default `now()`, onupdate `now()` | |

**Access rule**: Token is valid when `revoked_at IS NULL` AND (`expires_at IS NULL` OR
`expires_at > NOW()`). Token always resolves to the briefing's **current published
version** for the study (not the specific `briefing_id` version), so if a newer version
is published the token automatically serves the new one.

---

## Existing Entities Referenced (no schema changes)

| Entity | Usage |
|--------|-------|
| `Study` | Parent entity; `study_type = "Rapid"` discriminates RR studies |
| `CandidatePaper` | Reused for paper selection; `PROTOCOL_INVALIDATED` status added |
| `SearchExecution` | Reused for search tracking; single-source config stored via `StudyDatabaseSelection` |
| `Reviewer` | Reused for study team membership; access control for all RR endpoints |
| `BackgroundJob` | Reused for tracking ARQ job status (AI draft, briefing generation) |
| `DataExtraction` | Reused for data extraction if researcher chooses full extraction |

---

## Entity Relationship Summary

```
Study (study_type=RAPID)
 ├── RapidReviewProtocol [1:1]
 │    └── RRThreatToValidity [1:N]
 ├── PractitionerStakeholder [1:N]
 ├── RRNarrativeSynthesisSection [1:N]  (one per RQ)
 ├── EvidenceBriefing [1:N]  (versioned)
 │    └── EvidenceBriefingShareToken [1:N]
 ├── CandidatePaper [1:N]  (existing)
 └── Reviewer [1:N]  (existing, access control)
```
