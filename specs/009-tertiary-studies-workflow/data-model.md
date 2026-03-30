# Data Model: Tertiary Studies Workflow

**Feature**: 009-tertiary-studies-workflow
**Date**: 2026-03-29
**Migration**: `0017_tertiary_studies_workflow`

---

## New ORM Models

### TertiaryStudyProtocol

Captures the research protocol for a Tertiary Study. One record per Tertiary Study.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, autoincrement | |
| `study_id` | Integer | FK → `study.id` CASCADE, UNIQUE, indexed | Owning study (must be `study_type = TERTIARY`) |
| `status` | Enum(`TertiaryProtocolStatus`) | NOT NULL, server_default `draft` | `draft` → `validated` |
| `background` | Text | nullable | Motivation for the tertiary study |
| `research_questions` | JSON (list[str]) | nullable | Research questions targeting secondary literature |
| `secondary_study_types` | JSON (list[str]) | nullable | Accepted secondary study types (SLR, SMS, Rapid Review) |
| `inclusion_criteria` | JSON (list[str]) | nullable | Criteria for including a secondary study |
| `exclusion_criteria` | JSON (list[str]) | nullable | Criteria for excluding a secondary study |
| `recency_cutoff_year` | Integer | nullable | Earliest year for included secondary studies |
| `search_strategy` | Text | nullable | Narrative description of the search strategy |
| `quality_threshold` | Float | nullable | Minimum quality score for inclusion |
| `synthesis_approach` | Enum(`SynthesisApproach`) | nullable | Planned synthesis strategy |
| `dissemination_strategy` | Text | nullable | Publication / dissemination plan |
| `version_id` | Integer | NOT NULL, server_default 0 | Optimistic locking |
| `created_at` | DateTime | NOT NULL, server_default NOW | |
| `updated_at` | DateTime | NOT NULL, server_default NOW, onupdate NOW | |

**New enum**: `TertiaryProtocolStatus` — `draft`, `validated`

**Relationships**:
- `study` — many-to-one → `Study`

---

### SecondaryStudySeedImport

Records a single import operation that copies included papers from a source study into a Tertiary Study's candidate corpus.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, autoincrement | |
| `target_study_id` | Integer | FK → `study.id` CASCADE, indexed | The Tertiary Study receiving the seed papers |
| `source_study_id` | Integer | FK → `study.id` RESTRICT, indexed | The SMS/SLR/RR study being imported |
| `imported_at` | DateTime | NOT NULL, server_default NOW | When the import was executed |
| `records_added` | Integer | NOT NULL, server_default 0 | Papers successfully added to target corpus |
| `records_skipped` | Integer | NOT NULL, server_default 0 | Duplicates detected and skipped |
| `imported_by_user_id` | Integer | FK → `user.id` SET NULL, nullable | Initiating user |

**Relationships**:
- `target_study` — many-to-one → `Study`
- `source_study` — many-to-one → `Study`
- `imported_by` — many-to-one → `User`

**Note**: `CandidatePaper` records created by a seed import receive a `source_seed_import_id` FK column pointing to this table (see migration notes below).

---

### TertiaryDataExtraction

Secondary-study-specific extraction fields for an included secondary study. One record per included `CandidatePaper` in a Tertiary Study.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, autoincrement | |
| `candidate_paper_id` | Integer | FK → `candidate_paper.id` CASCADE, UNIQUE, indexed | The included secondary study being extracted |
| `secondary_study_type` | Enum(`SecondaryStudyType`) | nullable | `SLR`, `SMS`, `RAPID_REVIEW`, `UNKNOWN` |
| `research_questions_addressed` | JSON (list[str]) | nullable | RQs the secondary study addressed |
| `databases_searched` | JSON (list[str]) | nullable | Databases covered by the secondary study |
| `study_period_start` | Integer | nullable | Earliest year of primary studies covered |
| `study_period_end` | Integer | nullable | Latest year of primary studies covered |
| `primary_study_count` | Integer | nullable | Number of primary studies included |
| `synthesis_approach_used` | Text | nullable | Synthesis method employed |
| `key_findings` | Text | nullable | Free-text summary of key findings |
| `research_gaps` | Text | nullable | Free-text summary of identified research gaps |
| `reviewer_quality_rating` | Float | nullable | Overall quality rating assigned by the tertiary reviewer (0–1 scale) |
| `extraction_status` | Enum(`ExtractionStatus`) | NOT NULL, server_default `pending` | Reuses existing `ExtractionStatus` enum |
| `extracted_by_agent` | String(256) | nullable | Agent model that populated the fields, if AI-assisted |
| `validated_by_reviewer_id` | Integer | FK → `user.id` SET NULL, nullable | |
| `version_id` | Integer | NOT NULL, server_default 0 | Optimistic locking |
| `created_at` | DateTime | NOT NULL, server_default NOW | |
| `updated_at` | DateTime | NOT NULL, server_default NOW, onupdate NOW | |

**New enum**: `SecondaryStudyType` — `SLR`, `SMS`, `RAPID_REVIEW`, `UNKNOWN`

**Relationships**:
- `candidate_paper` — many-to-one → `CandidatePaper`
- `validated_by` — many-to-one → `User`

---

## Existing Model Modifications

### CandidatePaper (additive column)

| New Field | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `source_seed_import_id` | Integer | FK → `secondary_study_seed_import.id` SET NULL, nullable, indexed | Set when a paper was added via seed import; NULL for normally searched papers |

---

## Reused Models (no changes)

| Model | Reuse Justification |
|-------|---------------------|
| `QualityAssessmentChecklist` | Generic; Tertiary Studies use it with secondary-study QA items |
| `QualityChecklistItem` | Generic; item text and scoring method cover secondary study criteria |
| `QualityAssessmentScore` | Generic; scores are per-reviewer, per-item, per-study |
| `SynthesisResult` | Generic approach + JSON blobs work for narrative/thematic synthesis |
| `SearchExecution` | Database search fan-out is reused unchanged |

---

## State Transitions

### TertiaryProtocolStatus
```
draft → validated
validated → draft  (on rejection via protocol review)
```

### Tertiary Study Phase Gate

| Phase | Label | Unlock Condition |
|-------|-------|-----------------|
| 1 | Protocol | Always unlocked |
| 2 | Search & Import | `TertiaryStudyProtocol.status == validated` |
| 3 | Screening | ≥1 `CandidatePaper` linked to this study (from search or seed import) |
| 4 | Quality Assessment | All accepted papers have QA scores from all assigned reviewers |
| 5 | Synthesis & Report | ≥2 `TertiaryDataExtraction` records with `extraction_status == validated` |

---

## Migration Notes

Migration file: `db/alembic/versions/0017_tertiary_studies_workflow.py`

Steps:
1. Create `tertiary_protocol_status_enum` (`draft`, `validated`)
2. Create `secondary_study_type_enum` (`SLR`, `SMS`, `RAPID_REVIEW`, `UNKNOWN`)
3. Create `tertiary_study_protocol` table
4. Create `secondary_study_seed_import` table
5. Create `tertiary_data_extraction` table
6. Add `source_seed_import_id` column to `candidate_paper` table

Downgrade reverses all steps in reverse order.

No changes to the `study_type_enum` are required — `TERTIARY` is already present.
