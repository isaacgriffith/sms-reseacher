# Data Model: Systematic Mapping Study Workflow System

**Branch**: `002-sms-workflow` | **Date**: 2026-03-10

---

## Overview

This document describes the full data model for the SMS Workflow feature. It extends the existing scaffold (`Study`, `Paper`, `StudyPaper`) with ~18 new tables and significant extensions to existing ones. All tables use SQLAlchemy 2.0 async mapped columns with PostgreSQL 16 in production and SQLite+aiosqlite for tests.

---

## Existing Models (Extended)

### `Study` *(extend)*

Existing fields retained. New fields added:

| Field | Type | Notes |
|-------|------|-------|
| `topic` | `Text` | Brief topic description |
| `motivation` | `Text \| None` | Research motivation narrative |
| `current_phase` | `SmallInt` | 1–5; controlled by soft-gate logic |
| `research_group_id` | `FK → ResearchGroup` | Owning group |
| `snowball_threshold` | `SmallInt` | Min new papers to continue snowball; default 5 |

State machine (existing `StudyStatus`): `draft → active → completed / archived` — no change.

Phase unlock rules (enforced at service layer, not DB):
- Phase 1: always accessible
- Phase 2: `pico_components` non-empty
- Phase 3: at least one `SearchExecution` with `status=completed`
- Phase 4 & 5: at least one `DataExtraction` with `status=completed`

---

### `Paper` *(extend)*

Existing fields retained. New fields added:

| Field | Type | Notes |
|-------|------|-------|
| `authors` | `JSON` | `[{name, institution, locale}]` |
| `year` | `SmallInt \| None` | Publication year |
| `venue` | `String(512) \| None` | Journal/conference name |
| `source_url` | `Text \| None` | URL where paper was found |
| `full_text_available` | `Boolean` | True if PDF retrieved |

---

### `StudyPaper` → replaced by `CandidatePaper`

The existing `StudyPaper` join table is superseded by the richer `CandidatePaper` entity below. `StudyPaper` is retained for backward compatibility in the migration but no longer written to by new code.

---

## New Models

### `ResearchGroup`

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `name` | `String(255)` | Unique |
| `created_at` | `DateTime(tz)` | |

---

### `User`

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `email` | `String(255)` | Unique, indexed |
| `hashed_password` | `String(255)` | bcrypt |
| `display_name` | `String(255)` | |
| `created_at` | `DateTime(tz)` | |
| `last_login_at` | `DateTime(tz) \| None` | |

---

### `GroupMembership`

| Field | Type | Notes |
|-------|------|-------|
| `group_id` | `FK → ResearchGroup PK` | |
| `user_id` | `FK → User PK` | |
| `role` | `Enum(admin, member)` | |
| `joined_at` | `DateTime(tz)` | |

Unique constraint: `(group_id, user_id)`.

---

### `StudyMember`

| Field | Type | Notes |
|-------|------|-------|
| `study_id` | `FK → Study PK` | |
| `user_id` | `FK → User PK` | |
| `role` | `Enum(lead, member)` | |
| `joined_at` | `DateTime(tz)` | |

Unique constraint: `(study_id, user_id)`.

---

### `Reviewer`

A reviewer is either a human study member or a named AI agent configuration. Each study has a set of reviewers that evaluate papers and extractions.

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `study_id` | `FK → Study` | |
| `reviewer_type` | `Enum(human, ai_agent)` | |
| `user_id` | `FK → User \| None` | Set if human |
| `agent_name` | `String(255) \| None` | Set if AI agent (e.g., `"screener-v2"`) |
| `agent_config` | `JSON \| None` | LLM model, temperature, prompt variant |
| `created_at` | `DateTime(tz)` | |

Constraint: exactly one of `user_id` or `agent_name` must be non-null (enforced at service layer).

---

### `PICOComponent`

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `study_id` | `FK → Study` | One per study (upsert semantics) |
| `variant` | `Enum(PICO, PICOS, PICOT, SPIDER, PCC)` | |
| `population` | `Text \| None` | |
| `intervention` | `Text \| None` | |
| `comparison` | `Text \| None` | |
| `outcome` | `Text \| None` | |
| `context` | `Text \| None` | |
| `extra_fields` | `JSON \| None` | Variant-specific fields (S, T, Spider components) |
| `ai_suggestions` | `JSON \| None` | Last AI refinement suggestions per component |
| `updated_at` | `DateTime(tz)` | |

---

### `SeedPaper`

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `study_id` | `FK → Study` | |
| `paper_id` | `FK → Paper` | |
| `added_by_user_id` | `FK → User \| None` | Null if added by Librarian/Expert agent |
| `added_by_agent` | `String(255) \| None` | Agent name if AI-provided |
| `created_at` | `DateTime(tz)` | |

---

### `SeedAuthor`

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `study_id` | `FK → Study` | |
| `author_name` | `String(255)` | |
| `institution` | `String(255) \| None` | |
| `profile_url` | `Text \| None` | |
| `added_by_user_id` | `FK → User \| None` | |
| `added_by_agent` | `String(255) \| None` | |
| `created_at` | `DateTime(tz)` | |

---

### `InclusionCriterion` / `ExclusionCriterion`

Both have identical shape (separate tables for clarity):

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `study_id` | `FK → Study` | |
| `description` | `Text` | Human-readable criterion text |
| `order_index` | `SmallInt` | Evaluation order |
| `created_at` | `DateTime(tz)` | |

---

### `SearchString`

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `study_id` | `FK → Study` | |
| `version` | `SmallInt` | Increments on each refinement |
| `string_text` | `Text` | The actual search query |
| `is_active` | `Boolean` | Only one active per study |
| `created_at` | `DateTime(tz)` | |
| `created_by_user_id` | `FK → User \| None` | Null if AI-generated |
| `created_by_agent` | `String(255) \| None` | |

---

### `SearchStringIteration`

Records each test-retest cycle comparing a search string against the test set.

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `search_string_id` | `FK → SearchString` | |
| `iteration_number` | `SmallInt` | |
| `result_set_count` | `Integer` | Total papers found |
| `test_set_recall` | `Float` | Fraction of seed papers found (0–1) |
| `ai_adequacy_judgment` | `Text \| None` | AI agent verdict |
| `human_approved` | `Boolean \| None` | Null until reviewed |
| `created_at` | `DateTime(tz)` | |

---

### `SearchExecution`

Represents one full execution of the active search string across all databases.

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `study_id` | `FK → Study` | |
| `search_string_id` | `FK → SearchString` | |
| `status` | `Enum(pending, running, completed, failed)` | |
| `phase_tag` | `String(64)` | e.g., `initial-search`, `backward-search-1`, `forward-search-2` |
| `databases_queried` | `JSON` | `["acm", "ieee", "scopus", ...]` |
| `started_at` | `DateTime(tz) \| None` | |
| `completed_at` | `DateTime(tz) \| None` | |
| `job_id` | `String(255) \| None` | ARQ background job ID |

---

### `CandidatePaper`

Central join entity: one row per (study, paper) pair discovered during any search phase.

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `study_id` | `FK → Study` | |
| `paper_id` | `FK → Paper` | |
| `search_execution_id` | `FK → SearchExecution` | Which search round found it |
| `phase_tag` | `String(64)` | Mirrors `SearchExecution.phase_tag` for fast queries |
| `current_status` | `Enum(pending, accepted, rejected, duplicate)` | Latest resolved status |
| `duplicate_of_id` | `FK → CandidatePaper \| None` | If duplicate |
| `version_id` | `Integer` | Optimistic lock counter |
| `created_at` | `DateTime(tz)` | |
| `updated_at` | `DateTime(tz)` | |

Unique constraint: `(study_id, paper_id)`.

---

### `PaperDecision`

Audit log of every decision (AI or human) made on a `CandidatePaper`.

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `candidate_paper_id` | `FK → CandidatePaper` | |
| `reviewer_id` | `FK → Reviewer` | |
| `decision` | `Enum(accepted, rejected, duplicate)` | |
| `reasons` | `JSON` | `[{criterion_id, criterion_type, text}]` |
| `is_override` | `Boolean` | True if overriding a prior decision |
| `overrides_decision_id` | `FK → PaperDecision \| None` | |
| `created_at` | `DateTime(tz)` | |

Conflict detection: when `len(decisions where reviewer_type='human') > 1` and decisions disagree → flag for resolution.

---

### `DataExtraction`

Structured extraction for one accepted paper within a study.

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `candidate_paper_id` | `FK → CandidatePaper` | Unique per CP |
| `research_type` | `Enum(evaluation, solution_proposal, validation, philosophical, opinion, personal_experience, unknown)` | Decision rule R1–R6 applied |
| `venue_type` | `String(128)` | Normalized venue type category |
| `venue_name` | `String(512) \| None` | |
| `author_details` | `JSON` | `[{name, institution, locale}]` |
| `summary` | `Text \| None` | Structured paper summary |
| `open_codings` | `JSON` | `[{code, definition, evidence_quote}]` |
| `keywords` | `JSON` | `[string]` |
| `question_data` | `JSON` | `{research_question_id: extracted_value}` |
| `extraction_status` | `Enum(pending, ai_complete, validated, human_reviewed)` | |
| `version_id` | `Integer` | Optimistic lock counter |
| `extracted_by_agent` | `String(255) \| None` | Primary extractor agent name |
| `validated_by_reviewer_id` | `FK → Reviewer \| None` | |
| `conflict_flag` | `Boolean` | True if reviewers disagree |
| `created_at` | `DateTime(tz)` | |
| `updated_at` | `DateTime(tz)` | |

---

### `ExtractionFieldAudit`

Preserves the original AI value when a human edits an extraction field.

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `extraction_id` | `FK → DataExtraction` | |
| `field_name` | `String(128)` | Which field was changed |
| `original_value` | `JSON` | AI-generated value before edit |
| `new_value` | `JSON` | Human-provided replacement |
| `changed_by_user_id` | `FK → User` | |
| `changed_at` | `DateTime(tz)` | |

---

### `BackgroundJob`

Tracks async ARQ background jobs with their progress state.

| Field | Type | Notes |
|-------|------|-------|
| `id` | `String(255) PK` | ARQ job ID |
| `study_id` | `FK → Study` | |
| `job_type` | `Enum(full_search, snowball_search, batch_extraction, quality_eval)` | |
| `status` | `Enum(queued, running, completed, failed)` | |
| `progress_pct` | `SmallInt` | 0–100 |
| `progress_detail` | `JSON` | `{phase, papers_found, current_database, ...}` |
| `error_message` | `Text \| None` | Set on failure |
| `queued_at` | `DateTime(tz)` | |
| `started_at` | `DateTime(tz) \| None` | |
| `completed_at` | `DateTime(tz) \| None` | |

---

### `SearchMetrics`

Aggregate counts per search execution (one row per `SearchExecution`).

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `search_execution_id` | `FK → SearchExecution` | Unique |
| `total_identified` | `Integer` | |
| `accepted` | `Integer` | |
| `rejected` | `Integer` | |
| `duplicates` | `Integer` | |
| `computed_at` | `DateTime(tz)` | Updated incrementally |

---

### `DomainModel`

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `study_id` | `FK → Study` | One active per study |
| `version` | `SmallInt` | Increments on regeneration |
| `concepts` | `JSON` | `[{name, definition, attributes:[]}]` |
| `relationships` | `JSON` | `[{from, to, label, type}]` |
| `svg_content` | `Text \| None` | Rendered SVG |
| `generated_at` | `DateTime(tz)` | |

---

### `ClassificationScheme`

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `study_id` | `FK → Study` | |
| `chart_type` | `Enum(venue, author, locale, institution, year, subtopic, research_type, research_method)` | One row per chart |
| `version` | `SmallInt` | |
| `chart_data` | `JSON` | Vega-Lite / Altair spec or raw data |
| `svg_content` | `Text \| None` | Rendered SVG |
| `generated_at` | `DateTime(tz)` | |

---

### `QualityReport`

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Integer PK` | |
| `study_id` | `FK → Study` | |
| `version` | `SmallInt` | |
| `score_need_for_review` | `SmallInt` | 0–2 |
| `score_search_strategy` | `SmallInt` | 0–2 |
| `score_search_evaluation` | `SmallInt` | 0–3 |
| `score_extraction_classification` | `SmallInt` | 0–3 |
| `score_study_validity` | `SmallInt` | 0–1 |
| `total_score` | `SmallInt` | Sum of above (0–11) |
| `rubric_details` | `JSON` | `{rubric_name: {score, justification}}` |
| `recommendations` | `JSON` | `[{priority, action, target_rubric}]` |
| `generated_at` | `DateTime(tz)` | |

---

## State Transitions

### `CandidatePaper.current_status`

```
pending ──► accepted
        └─► rejected
        └─► duplicate
```

Decision is set by the last resolved `PaperDecision`. When multiple reviewers disagree, status stays `pending` until a conflict resolution decision is submitted.

### `DataExtraction.extraction_status`

```
pending ──► ai_complete ──► validated ──► human_reviewed
```

- `ai_complete`: primary agent has run
- `validated`: second reviewer (AI or human) agrees
- `human_reviewed`: human has reviewed/edited at least once

### `BackgroundJob.status`

```
queued ──► running ──► completed
                   └─► failed
```

---

## Deduplication Logic

Papers are deduplicated before creating a `CandidatePaper`:

1. **Exact DOI match** → definite duplicate
2. **Fuzzy title + author match** (threshold ≥ 0.90 similarity) → probable duplicate → flagged for human review
3. All others → new candidate

Implemented in `backend/src/backend/services/dedup.py`.

---

## Optimistic Locking

Tables with concurrent edit risk use `version_id_col` (SQLAlchemy built-in):
- `CandidatePaper.version_id`
- `DataExtraction.version_id`

On conflict (stale `version_id`), the API returns `HTTP 409 Conflict` with body containing both the client's attempted update and the current server state, enabling the frontend diff-and-merge UI.

---

## Alembic Migrations

Each new table and each extension to an existing table requires a separate, ordered Alembic migration. Migration files live in `db/alembic/versions/`. Migration sequence:

1. `users_and_groups` — User, ResearchGroup, GroupMembership
2. `study_extensions` — extend Study with new fields + StudyMember, Reviewer
3. `pico_and_seeds` — PICOComponent, SeedPaper, SeedAuthor
4. `criteria_and_search` — InclusionCriterion, ExclusionCriterion, SearchString, SearchStringIteration, SearchExecution
5. `candidate_papers` — CandidatePaper (replaces StudyPaper for new writes), PaperDecision
6. `extraction` — DataExtraction, ExtractionFieldAudit
7. `jobs_and_metrics` — BackgroundJob, SearchMetrics
8. `results` — DomainModel, ClassificationScheme, QualityReport
