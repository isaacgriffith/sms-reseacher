# Research: Tertiary Studies Workflow

**Feature**: 009-tertiary-studies-workflow
**Date**: 2026-03-29
**Status**: Complete — all NEEDS CLARIFICATION items resolved

---

## Decision 1: Protocol Model Strategy

**Decision**: Create a dedicated `TertiaryStudyProtocol` ORM model rather than reusing `ReviewProtocol`.

**Rationale**: `ReviewProtocol` carries SLR-specific fields (PICO/S, `synthesis_approach` enum tied to `SynthesisApproach`) and is already `UNIQUE` to `study_id` with SLR semantics. Tertiary protocols need different fields: secondary study scope definition, recency constraints, and criteria for evaluating secondary study types. Sharing the model would violate SRP (the model would have two reasons to change).

**Alternatives considered**:
- Subclass ReviewProtocol via SQLAlchemy single-table inheritance — rejected because it would require nullable columns or a discriminator on the existing table, complicating SLR queries.
- Add nullable tertiary-specific columns to `ReviewProtocol` — rejected; this is Data Clumps smell and violates SRP.

---

## Decision 2: Quality Assessment Checklist Strategy

**Decision**: Reuse the existing generic `QualityAssessmentChecklist` / `QualityChecklistItem` / `QualityAssessmentScore` models with tertiary-specific item content — no new ORM models needed for the checklist itself.

**Rationale**: The existing models are deliberately generic: checklist items are stored as text with a scoring method. A Tertiary Study can populate the checklist with secondary-study-quality questions (protocol documentation, search strategy, etc.) through the same upsert endpoint already used by SLR. No structural difference exists.

**Alternatives considered**:
- New `TertiaryQualityChecklist` model — unnecessary duplication; rejected (YAGNI).

---

## Decision 3: Data Extraction Strategy

**Decision**: Create a dedicated `TertiaryDataExtraction` model linked to `CandidatePaper`, storing the nine secondary-study-specific fields. This coexists with (does not replace) the existing `DataExtraction` model.

**Rationale**: The existing `DataExtraction` model uses a `ResearchType` enum and `question_data` JSON blob suited to primary empirical studies. Secondary study extraction requires strongly typed fields (study type, primary study count, databases searched) that would be awkward as opaque JSON and would corrupt the semantics of `ResearchType`. A separate model maintains SRP and LSP.

**Alternatives considered**:
- Extend `DataExtraction` with nullable columns — rejected; Tertiary studies would always have NULL on those columns, creating confusion.
- Use `question_data` JSON for all secondary fields — rejected; untyped JSON prevents querying and synthesis aggregation.

---

## Decision 4: Seed Import Mechanism

**Decision**: `SecondaryStudySeedImport` is a new ORM model that records the link between a source study (any `Study` on the platform) and a target Tertiary Study. The import operation reads `CandidatePaper` records from the source study and creates new `CandidatePaper` records in the target study, tagging them via a `source_seed_import_id` FK.

**Rationale**: This approach leverages the existing `CandidatePaper` pipeline for screening, QA, and extraction without creating parallel code paths. The `SecondaryStudySeedImport` record provides deduplication tracking (added count, skipped count) and audit trail.

**Alternatives considered**:
- Copy-on-write at the paper level only (no import record) — rejected; loses audit trail and makes deduplication reporting impossible.
- Import directly from an external file — deferred; out of scope for this feature (spec FR-003 specifies platform studies).

---

## Decision 5: Phase Gate Strategy

**Decision**: Implement a standalone `get_tertiary_unlocked_phases()` function in `backend/src/backend/services/tertiary_phase_gate.py` and register it in the `_PHASE_GATE_DISPATCH` dict. Phase sequence mirrors SLR (5 phases) but gates are adapted for tertiary semantics.

**Rationale**: The SLR phase gate is already extracted into its own module and injected via the dispatch dict — the OCP extension point exists and MUST be used. Copy-pasting and modifying inline would violate DRY and Shotgun Surgery.

**Phase gate sequence for Tertiary Studies**:
- Phase 1: Protocol editor (always accessible)
- Phase 2: Database search / seed import (requires validated `TertiaryStudyProtocol`)
- Phase 3: Screening (requires ≥1 completed `SearchExecution` or ≥1 seeded `CandidatePaper`)
- Phase 4: Quality assessment (requires all accepted papers to have QA scores from all assigned reviewers)
- Phase 5: Synthesis & report (requires ≥2 extracted secondary studies)

---

## Decision 6: Synthesis Strategy

**Decision**: Reuse the existing `SynthesisResult` ORM model and add two new strategy classes — `NarrativeSynthesisStrategy` and `ThematicAnalysisStrategy` — to `synthesis_strategies.py`. Meta-analysis remains available via the existing `MetaAnalysisSynthesizer`.

**Rationale**: The `SynthesisResult` model is generic (approach-agnostic fields + JSON blobs for computed statistics). New strategies follow the existing Strategy pattern already established by `MetaAnalysisSynthesizer`, `DescriptiveSynthesizer`, and `QualitativeSynthesizer`. The tertiary-specific landscape section is generated as part of the report, not the synthesis result.

**Alternatives considered**:
- New `TertiarySynthesisResult` model — YAGNI; the existing model is sufficiently generic.

---

## Decision 7: Report Landscape Section

**Decision**: The `TertiaryReportService` extends the report data model with a `landscape_of_secondary_studies` field (covering timeline, RQ evolution, synthesis method shifts). Export formats match SLR: JSON, CSV+JSON, Full Archive, SVG.

**Rationale**: The `SLRReportService` pattern (Pydantic model → serialization methods) is clean and replicable. Adding a new service (not patching the SLR one) respects SRP and avoids merge conflicts with the SLR module.

---

## Decision 8: AI Agent

**Decision**: Reuse `ProtocolReviewerAgent` for tertiary protocol review with updated prompt context. No new agent class is needed for extraction assistance since secondary-study field suggestions are prompted inline via the existing extraction agent patterns.

**Rationale**: The `ProtocolReviewerAgent` accepts a `ProviderConfig` and renders a Jinja2 template for the study context. Adding a tertiary-specific system message template is a configuration change, not a structural one.

---

## Decision 9: Alembic Migration

**Decision**: New migration `0017_tertiary_studies_workflow` creates three tables:
1. `tertiary_study_protocol` — protocol record (one per Tertiary study)
2. `secondary_study_seed_import` — seed import records
3. `tertiary_data_extraction` — secondary-study-specific extraction data

No changes to existing tables or enums are required (`StudyType.TERTIARY` is already present in the DB enum).

**Rationale**: The minimal migration footprint avoids accidental table locks in production and keeps downgrade paths clean.

---

## Decision 10: API Routing Structure

**Decision**: New router module `backend/src/backend/api/v1/tertiary/` with sub-routers for protocol, seed imports, and report. Quality assessment and synthesis reuse existing SLR endpoints (they operate on `study_id` and are study-type-agnostic).

**Rationale**: Consistent with the existing `/slr/` and `/rapid/` subdirectory pattern; tertiary-specific resources live under `/api/v1/tertiary/`; shared resources (QA, synthesis) under existing `/api/v1/slr/` endpoints that already accept any study_id.
