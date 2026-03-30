
# Tasks: Tertiary Studies Workflow

**Input**: Design documents from `/specs/009-tertiary-studies-workflow/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/api.md ✓, quickstart.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Exact file paths are included in every task description

## Path Conventions

Web app layout: `backend/src/`, `db/src/`, `agents/src/`, `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the directory skeletons that all subsequent tasks write into.

- [X] T001 Create `backend/src/backend/api/v1/tertiary/` directory with empty `__init__.py` module docstring stubs for the tertiary API router package
- [X] T002 [P] Create `db/src/db/models/tertiary.py` file with module docstring and required imports (SQLAlchemy, enums); no model bodies yet

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: ORM models, migration, routing registration, and phase gate plumbing that every user story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Implement `TertiaryProtocolStatus` enum (`draft`, `validated`) and `SecondaryStudyType` enum (`SLR`, `SMS`, `RAPID_REVIEW`, `UNKNOWN`) in `db/src/db/models/tertiary.py`
- [X] T004 [P] Implement `TertiaryStudyProtocol` ORM model in `db/src/db/models/tertiary.py` with all fields from data-model.md (study_id FK unique, status, background, research_questions JSON, secondary_study_types JSON, inclusion_criteria JSON, exclusion_criteria JSON, recency_cutoff_year, search_strategy, quality_threshold, synthesis_approach, dissemination_strategy, version_id, created_at, updated_at)
- [X] T005 [P] Implement `SecondaryStudySeedImport` ORM model in `db/src/db/models/tertiary.py` with all fields (target_study_id FK, source_study_id FK, imported_at, records_added, records_skipped, imported_by_user_id FK nullable)
- [X] T006 [P] Implement `TertiaryDataExtraction` ORM model in `db/src/db/models/tertiary.py` with all nine secondary-study-specific fields plus extraction_status, extracted_by_agent, validated_by_reviewer_id, version_id, created_at, updated_at
- [X] T007 Export new models from `db/src/db/models/__init__.py` so they are importable by Alembic autogenerate and the backend
- [X] T008 Add nullable `source_seed_import_id` FK column to `CandidatePaper` ORM model in `db/src/db/models/__init__.py` pointing to `secondary_study_seed_import.id`
- [X] T009 Write Alembic migration `db/alembic/versions/0017_tertiary_studies_workflow.py`: create `tertiary_protocol_status_enum`, `secondary_study_type_enum`; create tables `tertiary_study_protocol`, `secondary_study_seed_import`, `tertiary_data_extraction` in dependency order; add `source_seed_import_id` column to `candidate_paper`; implement full `downgrade()` in reverse order
- [X] T010 Create `backend/src/backend/services/tertiary_phase_gate.py` with module docstring and `get_tertiary_unlocked_phases(study_id: int, db: AsyncSession) -> list[int]` implementing the 5-phase gate logic from data-model.md (Phase 1 always open; Phase 2 requires validated TertiaryStudyProtocol; Phase 3 requires ≥1 CandidatePaper; Phase 4 requires all accepted papers have QA scores; Phase 5 requires ≥2 validated TertiaryDataExtraction records)
- [X] T011 Register `get_tertiary_unlocked_phases` in the `_PHASE_GATE_DISPATCH` dict in `backend/src/backend/api/v1/studies/__init__.py` under `StudyType.TERTIARY`
- [X] T012 Create `backend/src/backend/api/v1/tertiary/__init__.py` defining the `router = APIRouter(prefix="/tertiary")` and registering all sub-routers (protocol, seed_imports, extractions, report) that will be created in later phases
- [X] T013 Mount the tertiary router in the FastAPI app by importing and including it in `backend/src/backend/main.py` (or the v1 router aggregator, following the same pattern used for `slr` and `rapid` routers)

**Checkpoint**: Migration applied (`uv run alembic upgrade head` succeeds), phase gate dispatch registered, tertiary router mounted at `/api/v1/tertiary/`.

---

## Phase 3: User Story 1 — Create Tertiary Study (Priority: P1) 🎯 MVP

**Goal**: Researcher can select "Tertiary Study" in the New Study Wizard with study-type-specific guidance, create the study, set up and validate a protocol, and see the correct phase progression on the study dashboard.

**Independent Test**: Create a study of type `TERTIARY` via API, GET its protocol, PUT updated fields, POST to validate, then GET `/studies/{id}/phases` and confirm phases 1–2 are unlocked.

- [X] T014 Create `backend/src/backend/api/v1/tertiary/protocol.py` with module docstring; implement `GET /tertiary/studies/{study_id}/protocol` endpoint (auto-create draft if none exists) and `PUT /tertiary/studies/{study_id}/protocol` endpoint with `TertiaryProtocolUpdate` Pydantic schema and optimistic-lock check on `version_id`; return `TertiaryProtocolResponse` schema
- [X] T015 Implement `POST /tertiary/studies/{study_id}/protocol/validate` endpoint in `backend/src/backend/api/v1/tertiary/protocol.py`: transitions protocol status to `validated`, enqueues `ProtocolReviewerAgent` ARQ job using the tertiary-protocol Jinja2 template, returns 202 with job_id
- [X] T016 [P] Create Jinja2 prompt template `agents/src/agents/templates/tertiary_protocol_review.j2` for the tertiary protocol review agent; context variables: `study_title`, `research_questions`, `secondary_study_types`, `inclusion_criteria`, `exclusion_criteria`, `recency_cutoff_year`, `quality_threshold`
- [X] T017 [P] Create `frontend/src/components/tertiary/TertiaryProtocolForm.tsx` with file-level JSDoc; functional component with named `TertiaryProtocolFormProps` interface; react-hook-form + Zod schema covering all protocol fields (research_questions array editor, secondary_study_types multi-select, inclusion/exclusion criteria list editors, recency_cutoff_year number, quality_threshold slider 0–1, synthesis_approach select); uses `useWatch` for reactive field display; ≤100 JSX lines per component (split into sub-components if needed)
- [X] T018 [P] Update `frontend/src/components/studies/NewStudyWizard.tsx` (or the study-type-selection step component): add "Tertiary Study" as a selectable study type with a helper text block explaining that a Tertiary Study reviews secondary literature (SLRs, SMSs, Rapid Reviews), not empirical papers
- [X] T019 Create `frontend/src/pages/TertiaryStudyPage.tsx` with file-level JSDoc: top-level router/dashboard component for a Tertiary Study that renders the phase gate panel (reusing the existing `PhaseGatePanel` component) and routes to the `TertiaryProtocolForm` for Phase 1; wire up TanStack Query for protocol GET/PUT/validate mutations
- [X] T019b Wire Phase 3 (Screening) panel in `frontend/src/pages/TertiaryStudyPage.tsx`: replace the `PlaceholderPanel` with a `Phase3Panel` that renders the existing `PaperQueue` component (imported from `../components/phase2/PaperQueue`) for `studyId`; remove the now-unused `PlaceholderPanel` component and its interface

**Checkpoint**: User Story 1 fully functional — a researcher can create a Tertiary Study, edit and validate the protocol, observe the phase gate advance to Phase 2, and screen candidate papers in Phase 3 using the existing paper queue.

---

## Phase 4: User Story 2 — Import Seed Secondary Studies (Priority: P2)

**Goal**: Researcher can import included papers from an existing platform SMS/SLR/RR study as the seed corpus for a Tertiary Study; duplicate records are detected and skipped; an import record is persisted.

**Independent Test**: POST to `/tertiary/studies/{id}/seed-imports` with a source study that has ≥1 included paper; confirm `records_added > 0`, `CandidatePaper` records appear in the target study, and a second import of the same source returns `records_skipped == records_added` from the first run.

- [X] T020 Create `backend/src/backend/services/tertiary_extraction_service.py` with module docstring; implement `TertiaryExtractionService` class with `import_seed_study(target_study_id, source_study_id, user_id, db) -> SecondaryStudySeedImport` method: queries included CandidatePapers from source study; deduplicates against existing target corpus by DOI (primary) or normalised title+first-author (fallback); bulk-inserts new CandidatePaper records with `source_seed_import_id` set; persists `SecondaryStudySeedImport` record with counts; raises `ValueError` if source has no included papers
- [X] T021 Create `backend/src/backend/api/v1/tertiary/seed_imports.py` with module docstring; implement `GET /tertiary/studies/{study_id}/seed-imports` (list imports with source study title/type joined) and `POST /tertiary/studies/{study_id}/seed-imports` (delegates to `TertiaryExtractionService.import_seed_study`; returns 201 with import record; 404 if source study not found; 409 if already imported from that source; 422 if source has no included papers)
- [X] T022 [P] Create `frontend/src/components/tertiary/SeedImportPanel.tsx` with file-level JSDoc: functional component showing a list of completed imports with source study name, import date, records_added/skipped; a "Import from Platform Study" button opening a dialog that lists available SMS/SLR/RR studies on the platform and confirms selection; uses TanStack Query for GET list and POST mutation; ≤100 JSX lines (split dialog into sub-component if needed)
- [X] T023 Wire `SeedImportPanel` into `TertiaryStudyPage.tsx`: render it inside the Phase 2 (Search & Import) panel alongside the existing database search UI

**Checkpoint**: User Story 2 fully functional — seed import creates CandidatePaper records in the Tertiary Study corpus and persists the import audit record.

---

## Phase 5: User Story 3 — Quality Assessment with Secondary-Study Checklists (Priority: P3)

**Goal**: Reviewer can assess secondary studies using a checklist covering protocol documentation, search strategy, inclusion/exclusion criteria clarity, QA approach, synthesis method appropriateness, and validity threats; Cohen's κ is available when two reviewers have scored the same studies.

**Independent Test**: Seed a Tertiary Study with two included papers; use the existing QA checklist endpoint to upsert a checklist with secondary-study items; score both papers as two reviewers; call the inter-rater reliability endpoint and confirm κ is returned.

- [X] T024 Create `backend/src/backend/services/tertiary_qa_service.py` with module docstring; implement `get_or_create_default_secondary_study_checklist(study_id: int, db: AsyncSession) -> QualityAssessmentChecklist` that auto-creates a `QualityAssessmentChecklist` (if none exists for the study) pre-seeded with the 6 mandatory secondary-study items (protocol documentation completeness, search strategy adequacy, inclusion/exclusion criteria clarity, quality assessment approach, synthesis method appropriateness, validity threats discussion), each using `SCALE_1_3` scoring and weight `1.0`
- [X] T025 Call `get_or_create_default_secondary_study_checklist` from the `GET /tertiary/studies/{study_id}/protocol` endpoint (after protocol auto-creation) so the QA checklist is ready the moment a Tertiary Study reaches Phase 4
- [X] T026 [P] Add a `TertiaryQAGuidancePanel` sub-component in `frontend/src/components/tertiary/TertiaryQAGuidancePanel.tsx` with file-level JSDoc: renders a read-only info banner above the existing `QualityChecklistEditor` when the current study type is `TERTIARY`, listing the six secondary-study QA dimensions with brief explanations; rendered inside the existing Quality Assessment page for Tertiary studies

**Checkpoint**: User Story 3 fully functional — Tertiary Study reaches Phase 4 with a pre-seeded secondary-study checklist; reviewers can score; κ is computable via the existing inter-rater reliability endpoint.

---

## Phase 6: User Story 4 — Data Extraction for Secondary Studies (Priority: P4)

**Goal**: Reviewer can open a data extraction form for an included secondary study and fill in the nine secondary-study-specific fields; AI-assisted pre-population is available; the validated extraction is used in synthesis.

**Independent Test**: Include a paper in a Tertiary Study; confirm a `TertiaryDataExtraction` record is auto-created with `extraction_status = pending`; PUT all nine fields; confirm `extraction_status` can be set to `human_reviewed`.

- [X] T027 Create `backend/src/backend/api/v1/tertiary/extractions.py` with module docstring; implement:
  - `GET /tertiary/studies/{study_id}/extractions` (list all extractions with paper title joined, optional status filter)
  - `GET /tertiary/studies/{study_id}/extractions/{extraction_id}` (single record)
  - `PUT /tertiary/studies/{study_id}/extractions/{extraction_id}` with `TertiaryExtractionUpdate` Pydantic schema and optimistic-lock check on `version_id`
  - `POST /tertiary/studies/{study_id}/extractions/ai-assist` (enqueues ARQ job, returns 202)
- [X] T028 Extend `TertiaryExtractionService` in `backend/src/backend/services/tertiary_extraction_service.py`: add `ensure_extraction_records(study_id, db)` that bulk-creates pending `TertiaryDataExtraction` stubs for all accepted `CandidatePaper` records that do not yet have an extraction record; call this method from the Phase 4 unlock logic or the extractions list endpoint
- [X] T029 Create `backend/src/backend/jobs/tertiary_extraction_job.py` with module docstring; implement `run_tertiary_extraction(ctx, *, study_id: int) -> dict` ARQ job that: loads all pending `TertiaryDataExtraction` records for the study; for each paper, invokes the configured LLM agent to suggest values for the nine extraction fields; updates the record with AI-suggested values and sets `extraction_status = ai_complete`; logs progress with structlog; returns `{"status": "completed", "study_id": study_id, "papers_processed": N}`
- [X] T030 Register `run_tertiary_extraction` in the ARQ worker function list in `backend/src/backend/worker.py` (or wherever ARQ job functions are registered, following the pattern for `run_synthesis` and `narrative_synthesis_job`)
- [X] T031 [P] Create `frontend/src/components/tertiary/TertiaryExtractionForm.tsx` with file-level JSDoc: functional component with named `TertiaryExtractionFormProps` interface; react-hook-form + Zod schema; renders all nine secondary-study fields (secondary_study_type select, research_questions_addressed tag-input, databases_searched tag-input, study_period_start/end year inputs, primary_study_count number input, synthesis_approach_used text, key_findings textarea, research_gaps textarea, reviewer_quality_rating slider 0–1); shows AI-suggested values in read-only comparison mode when `extraction_status == ai_complete`; uses `useWatch` for derived display logic; ≤100 JSX lines per component
- [X] T032 [P] Wire `TertiaryExtractionForm` into `TertiaryStudyPage.tsx`: render it inside the Phase 4 (Quality Assessment & Extraction) section; add "AI Pre-fill" button that calls the `POST .../ai-assist` endpoint and polls for completion via TanStack Query `refetchInterval`

**Checkpoint**: User Story 4 fully functional — reviewers can manually fill and validate all nine secondary-study extraction fields; AI-assisted pre-fill is available as an optional step.

---

## Phase 7: User Story 5 — Synthesis and Reporting (Priority: P5)

**Goal**: Researcher can trigger narrative or thematic synthesis on a Tertiary Study with ≥2 extracted secondary studies, and generate a report that includes a "Landscape of Secondary Studies" section covering timeline, RQ evolution, and synthesis method shifts.

**Independent Test**: With ≥2 validated `TertiaryDataExtraction` records, trigger synthesis (narrative strategy); confirm `SynthesisResult.status == completed`; GET the report and confirm `landscape_of_secondary_studies` object is present with all three sub-fields non-empty.

- [X] T033 Add `NarrativeSynthesisStrategy` class to `backend/src/backend/services/synthesis_strategies.py` with Google-style docstring: accepts a list of `TertiaryDataExtraction` records (passed as structured data); uses the configured LLM to produce a narrative summary identifying convergent findings, divergent conclusions, and research gaps; returns `SynthesisOutput` with `qualitative_themes` populated
- [X] T034 [P] Add `ThematicAnalysisStrategy` class to `backend/src/backend/services/synthesis_strategies.py` with Google-style docstring: groups extracted key findings and research gaps by theme using LLM-assisted clustering; returns `SynthesisOutput` with `qualitative_themes` populated as a theme-to-paper mapping
- [X] T035 Register `NarrativeSynthesisStrategy` and `ThematicAnalysisStrategy` in the synthesis strategy dispatch map (wherever the existing strategies are dispatched by `SynthesisApproach` value) — add `narrative` and `thematic` as new `SynthesisApproach` enum values if not already present, or reuse existing values per the constitution's OCP guidance
- [X] T036 Create `backend/src/backend/services/tertiary_report_service.py` with module docstring; implement `TertiaryReportService` with `generate_report(study_id: int, db: AsyncSession) -> TertiaryReport`; `TertiaryReport` is a Pydantic model extending the SLR report fields with a `landscape_of_secondary_studies: LandscapeSection` nested model (`timeline_summary: str`, `research_question_evolution: str`, `synthesis_method_shifts: str`); the landscape section is derived from `TertiaryDataExtraction` records (aggregating study_period fields for timeline, research_questions_addressed for RQ evolution, synthesis_approach_used for method shifts); add `to_json()`, `to_csv()`, `to_markdown()` serialisation methods
- [X] T037 Create `backend/src/backend/api/v1/tertiary/report.py` with module docstring; implement `GET /tertiary/studies/{study_id}/report` endpoint accepting `format: json | csv | markdown` query param (default `json`); delegates to `TertiaryReportService.generate_report`; returns 409 if study has not reached Phase 5; returns 404 if study not found or not TERTIARY type
- [X] T038 [P] Create `frontend/src/components/tertiary/LandscapeSummarySection.tsx` with file-level JSDoc: functional component displaying the three landscape sub-fields (timeline, RQ evolution, synthesis method shifts) as collapsible MUI `Accordion` panels; receives `landscape: LandscapeSection` as a prop with a typed interface
- [X] T039 [P] Create `frontend/src/pages/TertiaryReportPage.tsx` with file-level JSDoc: page component that calls `GET /tertiary/studies/{id}/report` via TanStack Query; renders all report sections using MUI Typography/Divider; embeds `LandscapeSummarySection`; provides download buttons for JSON, CSV, and Markdown export formats using `window.open` with the `format` query param
- [X] T040 Wire synthesis trigger into `TertiaryStudyPage.tsx` Phase 5 panel: add "Run Synthesis" button that calls the existing `POST /slr/studies/{id}/synthesis` endpoint (passing `approach: narrative` or `thematic`); poll `SynthesisResult` status; on completion, navigate to `TertiaryReportPage`

**Checkpoint**: User Story 5 fully functional — narrative/thematic synthesis runs, landscape section is generated, and the report is downloadable in all formats.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Wire up remaining integration points, run full validation, verify quickstart scenarios.

- [X] T041 Write unit tests for `tertiary_phase_gate.py` in `backend/tests/test_tertiary_phase_gate.py`: test each phase transition condition (protocol not validated → Phase 2 locked; validated → unlocked; no papers → Phase 3 locked; etc.) using SQLite async session
- [X] T042 [P] Write unit tests for `TertiaryExtractionService.import_seed_study` in `backend/tests/test_tertiary_seed_import.py`: test happy path (N papers imported), deduplication (re-import skips all), edge case (source study with zero included papers raises ValueError)
- [X] T043 [P] Write unit tests for `TertiaryReportService.generate_report` in `backend/tests/test_tertiary_report.py`: test landscape section fields are derived from extraction records; test JSON/CSV/Markdown serialisation outputs correct structure
- [X] T044 [P] Write integration tests for protocol CRUD + validate in `backend/tests/test_tertiary_protocol.py`: test GET auto-creates draft; PUT updates and version_id increments; PUT with stale version_id returns 409; POST validate transitions status
- [X] T045 [P] Write frontend unit tests for `TertiaryProtocolForm.tsx` in `frontend/tests/TertiaryProtocolForm.test.tsx`, `SeedImportPanel.tsx` in `frontend/tests/SeedImportPanel.test.tsx`, and `TertiaryExtractionForm.tsx` in `frontend/tests/TertiaryExtractionForm.test.tsx` using vitest + React Testing Library
- [X] T046 Run full lint + type-check pass: `uv run ruff check backend/src db/src agents/src`, `uv run ruff format --check backend/src db/src agents/src`, `uv run mypy backend/src/backend/api/v1/tertiary/ backend/src/backend/services/tertiary_*.py db/src/db/models/tertiary.py`, `cd frontend && npm run lint && npm run format:check`; fix all reported issues
- [X] T047 Run full test suite and verify ≥85% coverage: `uv run --package sms-backend pytest backend/tests/ --cov=src/backend --cov-fail-under=85`, `uv run --package sms-db pytest db/tests/ --cov=src/db --cov-fail-under=85`, `cd frontend && npm run test:coverage`; fix any failures
- [ ] T048 Exercise the quickstart.md validation scenarios end-to-end against a running Docker Compose stack: create Tertiary Study, set up protocol, validate, seed-import, screen papers, run QA, run extraction (AI-assist), run synthesis, generate report; confirm all API calls return expected status codes and the report landscape section is non-empty

---

## Phase 9: Feature Completion Documentation *(mandatory — Constitution Principle X)*

**Purpose**: Update all required documentation before the feature branch is merged.

- [X] TDOC1 [P] Update `CLAUDE.md` at repository root: add `009-tertiary-studies-workflow` entry under **Active Technologies** (same stack as SLR workflow) and under **Recent Changes**; add Alembic migration `0017_tertiary_studies_workflow` note; add new env vars section if any were added (none expected)
- [X] TDOC2 [P] Update `README.md` at repository root: add Tertiary Studies Workflow to the list of supported study types and high-level feature descriptions
- [X] TDOC3 [P] Update `CHANGELOG.md` at repository root: add new entry under `[Unreleased]` with **Added** bullets for: Tertiary Study type, TertiaryStudyProtocol, SecondaryStudySeedImport, TertiaryDataExtraction, tertiary phase gate, NarrativeSynthesisStrategy, ThematicAnalysisStrategy, TertiaryReportService with landscape section, seed import API, tertiary extraction API, frontend Tertiary Study components
- [X] TDOC4 [P] Update `README.md` in `backend/`, `db/`, `agents/`, and `frontend/` subproject directories to reflect new tertiary modules, endpoints, and components
- [X] TDOC5 [P] Update `CHANGELOG.md` in `backend/`, `db/`, `agents/`, and `frontend/` subproject directories with the same level of detail as the root changelog entry

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — **BLOCKS all user story phases**
- **Phase 3 (US1)**: Depends on Phase 2
- **Phase 4 (US2)**: Depends on Phase 2 (T020 needs `TertiaryExtractionService`; T021 needs seed_imports router)
- **Phase 5 (US3)**: Depends on Phase 2 + Phase 4 (US3 QA checklist auto-seed triggered after papers arrive via import or search)
- **Phase 6 (US4)**: Depends on Phase 2 + Phase 4 (extraction records reference `CandidatePaper` seeded by import)
- **Phase 7 (US5)**: Depends on Phase 6 (synthesis consumes `TertiaryDataExtraction` records)
- **Phase 8 (Polish)**: Depends on all story phases
- **Phase 9 (Docs)**: Depends on Phase 8

### User Story Dependencies

- **US1 (P1)**: After Foundational — no story dependencies
- **US2 (P2)**: After Foundational — no story dependencies (can run in parallel with US1)
- **US3 (P3)**: After US2 (seeded papers required to demonstrate QA); reuses existing checklist and inter-rater endpoints
- **US4 (P4)**: After US2 (extraction records are linked to CandidatePaper records created by import)
- **US5 (P5)**: After US4 (synthesis and report consume extraction data)

### Within Each User Story

- Backend model/service tasks before API endpoint tasks
- API endpoint tasks before frontend tasks
- Frontend tasks before wiring tasks
- Backend [P] tasks within same phase can run in parallel

### Parallel Opportunities

- T004, T005, T006: All ORM models in the same file — write sequentially (same file)
- T014, T015, T016: Protocol endpoints and Jinja2 template are independent files — [P] for T016
- T017, T018: Frontend form and wizard update are independent files — both [P]
- T020, T022: Service and frontend SeedImportPanel are independent — T022 is [P]
- T031, T032: Extraction form and page wiring are in different files — T031 is [P]
- T033, T034: Two new strategy classes in the same file — write sequentially (same file)
- T038, T039: LandscapeSummarySection and ReportPage are independent files — both [P]
- T041–T048: All Polish tasks marked [P] can run in parallel after story phases complete
- TDOC1–TDOC5: All doc tasks are independent files — all [P]

---

## Parallel Example: Phase 2 (Foundational)

```bash
# After T003 (enums) is done, these can start in parallel:
Task T004: "Implement TertiaryStudyProtocol ORM in db/src/db/models/tertiary.py"
Task T005: "Implement SecondaryStudySeedImport ORM in db/src/db/models/tertiary.py"
Task T006: "Implement TertiaryDataExtraction ORM in db/src/db/models/tertiary.py"
# Then sequentially:
Task T007: "Export models from db/src/db/models/__init__.py"
Task T008: "Add source_seed_import_id column to CandidatePaper"
Task T009: "Write migration 0017"
# T010, T011, T012, T013 can then proceed
```

## Parallel Example: Phase 3 (US1 — MVP)

```bash
# After T013 (router mounted):
Task T014: "Protocol GET/PUT endpoints in backend/src/backend/api/v1/tertiary/protocol.py"
Task T016: "Jinja2 template in agents/src/agents/templates/tertiary_protocol_review.j2"  # [P]
Task T017: "TertiaryProtocolForm.tsx in frontend/src/components/tertiary/"                 # [P]
Task T018: "Update NewStudyWizard.tsx for Tertiary Study type"                             # [P]
# After T014:
Task T015: "Protocol validate endpoint in protocol.py"
# After T017, T018:
Task T019: "TertiaryStudyPage.tsx wiring"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational) — **critical path**
2. Complete Phase 3 (US1: Create Tertiary Study)
3. **STOP and VALIDATE**: Create a Tertiary Study via the wizard, set up the protocol, validate it, and confirm phase 2 unlocks
4. Deploy/demo if ready

### Incremental Delivery

1. Phase 1 + 2 → Foundation ready (Alembic migration applied, router mounted)
2. Phase 3 (US1) → Researcher can create and configure a Tertiary Study (**MVP**)
3. Phase 4 (US2) → Seed import from existing SMS/SLR studies
4. Phase 5 (US3) → Secondary-study QA checklist auto-seeded
5. Phase 6 (US4) → Secondary-study extraction form with AI assist
6. Phase 7 (US5) → Synthesis + Landscape Report (**full feature**)
7. Phase 8 + 9 → Polish, tests, docs → ready to merge

### Parallel Team Strategy

With two developers after Phase 2 completes:
- **Developer A**: US1 (Phase 3) → US3 (Phase 5)
- **Developer B**: US2 (Phase 4) → US4 (Phase 6) → US5 (Phase 7)

---

## Notes

- [P] tasks = different files, no incomplete-task dependencies — safe to run in parallel
- [Story] label maps each task to a specific user story for traceability (US1–US5)
- Each user story phase is independently completable and testable; stop at any checkpoint to validate
- Constitution compliance: all tasks respect Principles I–X (SOLID, DRY, YAGNI, Code Clarity, Refactoring, GRASP, Testing, Toolchain, Observability, Language, Feature Completion Documentation)
- All new `.py` files MUST begin with a module docstring; all `.tsx`/`.ts` files MUST begin with a file-level JSDoc block
- All Python functions/methods/classes MUST have Google-style docstrings; all exported TypeScript symbols MUST have JSDoc
- New ORM models MUST include `created_at`/`updated_at` audit fields and `version_id` for optimistic locking (Principle VIII)
- ARQ jobs MUST follow the existing pattern: `async def job_fn(ctx, *, param: type)`, use `_session_maker`, log with structlog, return status dict
- React components MUST be functional, have a named props interface, and be ≤100 JSX lines (split sub-components if needed)
- `useWatch` MUST be used (not `watch`) for reactive react-hook-form subscriptions (Principle IX)
- TypeScript MUST NOT use `any`/`enum`/non-null `!` without justification; all API responses validated via Zod (Principle IX)
- Before the feature is marked complete: all tests, linting, and type checks MUST pass (including pre-existing failures in touched files); mutation testing MUST be run against every modified subproject (cosmic-ray for Python, stryker for frontend) with ≥85% mutants killed (Principle VI)
