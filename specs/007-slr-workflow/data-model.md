# Data Model: SLR Workflow (007)

**Branch**: `007-slr-workflow` | **Date**: 2026-03-18

All six new ORM models reside in `db/src/db/models/slr.py` and are exported from `db/src/db/models/__init__.py`. Every model follows the project's audit-field and optimistic-locking conventions.

---

## New Models

### ReviewProtocol

One protocol per SLR study. A study cannot advance to search until `status = validated`.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK, auto | |
| `study_id` | `Integer` | FK → `study.id`, UNIQUE | One protocol per study |
| `status` | `ReviewProtocolStatus` (enum) | NOT NULL | `draft`, `under_review`, `validated` |
| `background` | `Text` | nullable | |
| `rationale` | `Text` | nullable | |
| `research_questions` | `JSON` | nullable | List of RQ strings |
| `pico_population` | `Text` | nullable | |
| `pico_intervention` | `Text` | nullable | |
| `pico_comparison` | `Text` | nullable | |
| `pico_outcome` | `Text` | nullable | |
| `pico_context` | `Text` | nullable | Optional C in PICO(C) |
| `search_strategy` | `Text` | nullable | Narrative description |
| `inclusion_criteria` | `JSON` | nullable | List of criterion strings |
| `exclusion_criteria` | `JSON` | nullable | List of criterion strings |
| `data_extraction_strategy` | `Text` | nullable | |
| `synthesis_approach` | `SynthesisApproach` (enum) | nullable | `meta_analysis`, `descriptive`, `qualitative` |
| `dissemination_strategy` | `Text` | nullable | |
| `timetable` | `Text` | nullable | |
| `review_report` | `JSON` | nullable | AI reviewer JSON feedback |
| `version_id` | `Integer` | optimistic lock | |
| `created_at` | `DateTime(tz=True)` | server_default | |
| `updated_at` | `DateTime(tz=True)` | onupdate | |

**Enum**: `ReviewProtocolStatus` → `draft`, `under_review`, `validated`
**Enum**: `SynthesisApproach` → `meta_analysis`, `descriptive`, `qualitative`

**State Transitions**: `draft` → `under_review` (on AI review submission) → `draft` (on rejection) or `validated` (on researcher approval)

---

### QualityAssessmentChecklist

A named, study-scoped checklist of items. One study may have exactly one checklist.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK | |
| `study_id` | `Integer` | FK → `study.id`, UNIQUE | One checklist per study |
| `name` | `String(255)` | NOT NULL | |
| `description` | `Text` | nullable | |
| `created_at` | `DateTime(tz=True)` | server_default | |
| `updated_at` | `DateTime(tz=True)` | onupdate | |

**Relationship**: One-to-many → `QualityChecklistItem`

---

### QualityChecklistItem

Individual scored items within a checklist.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK | |
| `checklist_id` | `Integer` | FK → `quality_assessment_checklist.id` | |
| `order` | `Integer` | NOT NULL | Display order |
| `question` | `Text` | NOT NULL | |
| `scoring_method` | `ChecklistScoringMethod` (enum) | NOT NULL | `binary`, `scale_1_3`, `scale_1_5` |
| `weight` | `Float` | default=1.0 | Contribution to aggregate score |
| `created_at` | `DateTime(tz=True)` | server_default | |
| `updated_at` | `DateTime(tz=True)` | onupdate | |

**Enum**: `ChecklistScoringMethod` → `binary`, `scale_1_3`, `scale_1_5`

---

### QualityAssessmentScore

One row per (reviewer, paper, checklist item) triple.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK | |
| `candidate_paper_id` | `Integer` | FK → `candidate_paper.id` | |
| `reviewer_id` | `Integer` | FK → `reviewer.id` | |
| `checklist_item_id` | `Integer` | FK → `quality_checklist_item.id` | |
| `score_value` | `Float` | NOT NULL | Raw numeric response |
| `notes` | `Text` | nullable | Reviewer commentary |
| `version_id` | `Integer` | optimistic lock | |
| `created_at` | `DateTime(tz=True)` | server_default | |
| `updated_at` | `DateTime(tz=True)` | onupdate | |

**Unique constraint**: `(candidate_paper_id, reviewer_id, checklist_item_id)`

**Derived**: Aggregate `quality_score` per paper per reviewer = weighted average of `score_value × item.weight` across all items; computed at query time, not stored.

---

### InterRaterAgreementRecord

Stores one Cohen's Kappa calculation between two reviewers for a specific round.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK | |
| `study_id` | `Integer` | FK → `study.id` | |
| `reviewer_a_id` | `Integer` | FK → `reviewer.id` | |
| `reviewer_b_id` | `Integer` | FK → `reviewer.id` | |
| `round_type` | `AgreementRoundType` (enum) | NOT NULL | `title_abstract`, `intro_conclusions`, `full_text`, `quality_assessment` |
| `phase` | `String(20)` | NOT NULL | `pre_discussion` or `post_discussion` |
| `kappa_value` | `Float` | nullable | `None` if calculation was undefined |
| `kappa_undefined_reason` | `String(255)` | nullable | Human-readable reason when kappa is None |
| `n_papers` | `Integer` | NOT NULL | Number of papers assessed |
| `threshold_met` | `Boolean` | NOT NULL | Whether kappa ≥ configured threshold |
| `created_at` | `DateTime(tz=True)` | server_default | |
| `updated_at` | `DateTime(tz=True)` | onupdate | |

**Enum**: `AgreementRoundType` → `title_abstract`, `intro_conclusions`, `full_text`, `quality_assessment`

---

### SynthesisResult

One completed synthesis run for a study.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK | |
| `study_id` | `Integer` | FK → `study.id` | |
| `approach` | `SynthesisApproach` (enum) | NOT NULL | Reuses `SynthesisApproach` from `ReviewProtocol` |
| `status` | `SynthesisStatus` (enum) | NOT NULL | `pending`, `running`, `completed`, `failed` |
| `model_type` | `String(20)` | nullable | `fixed` or `random` (meta-analysis only) |
| `parameters` | `JSON` | nullable | Input configuration |
| `computed_statistics` | `JSON` | nullable | Pooled effect, SE, CI, Q, τ², I², Kappa, etc. |
| `forest_plot_svg` | `Text` | nullable | SVG string for descriptive synthesis |
| `funnel_plot_svg` | `Text` | nullable | SVG string for meta-analysis |
| `qualitative_themes` | `JSON` | nullable | Theme-to-paper mapping for qualitative |
| `sensitivity_analysis` | `JSON` | nullable | Subset results |
| `error_message` | `Text` | nullable | Error detail if `status=failed` |
| `version_id` | `Integer` | optimistic lock | |
| `created_at` | `DateTime(tz=True)` | server_default | |
| `updated_at` | `DateTime(tz=True)` | onupdate | |

**Enum**: `SynthesisStatus` → `pending`, `running`, `completed`, `failed`

---

### GreyLiteratureSource

Non-database literature entries tracked per study.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `Integer` | PK | |
| `study_id` | `Integer` | FK → `study.id` | |
| `source_type` | `GreyLiteratureType` (enum) | NOT NULL | |
| `title` | `String(1024)` | NOT NULL | |
| `authors` | `String(1024)` | nullable | |
| `year` | `Integer` | nullable | |
| `url` | `String(2048)` | nullable | |
| `description` | `Text` | nullable | Why included / relevance |
| `created_at` | `DateTime(tz=True)` | server_default | |
| `updated_at` | `DateTime(tz=True)` | onupdate | |

**Enum**: `GreyLiteratureType` → `technical_report`, `dissertation`, `rejected_publication`, `work_in_progress`

---

## Alembic Migration

**File**: `db/alembic/versions/0015_slr_workflow.py`

**Creates**:
- Tables: `review_protocol`, `quality_assessment_checklist`, `quality_checklist_item`, `quality_assessment_score`, `inter_rater_agreement_record`, `synthesis_result`, `grey_literature_source`
- Enum types (PostgreSQL): `review_protocol_status_enum`, `synthesis_approach_enum`, `checklist_scoring_method_enum`, `agreement_round_type_enum`, `synthesis_status_enum`, `grey_literature_type_enum`

**`upgrade()`**: create all tables and enum types
**`downgrade()`**: drop all tables and enum types in reverse dependency order

---

## Entity Relationship Summary

```
Study (existing)
├── ReviewProtocol (1:1)
├── QualityAssessmentChecklist (1:1)
│   └── QualityChecklistItem (1:N)
├── InterRaterAgreementRecord (1:N)
├── SynthesisResult (1:N)
└── GreyLiteratureSource (1:N)

CandidatePaper (existing)
└── QualityAssessmentScore (1:N, via reviewer_id + checklist_item_id)

Reviewer (existing)
├── QualityAssessmentScore (1:N)
└── InterRaterAgreementRecord (referenced as reviewer_a / reviewer_b)
```
