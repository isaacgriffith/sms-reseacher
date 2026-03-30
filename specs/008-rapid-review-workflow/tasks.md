-
---

description: "Task list for 008-Rapid-Review-Workflow"
---

# Tasks: Rapid Review Workflow

**Input**: Design documents from `/specs/008-rapid-review-workflow/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/api-contracts.md ✅ quickstart.md ✅

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Include exact file paths in descriptions

## Path Conventions

- **DB models**: `db/src/db/models/`
- **Backend services**: `backend/src/backend/services/`
- **Backend routes**: `backend/src/backend/api/v1/`
- **Backend jobs**: `backend/src/backend/jobs/`
- **Agent prompts**: `agents/src/agents/prompts/`
- **Agent classes**: `agents/src/agents/`
- **Frontend pages**: `frontend/src/pages/`
- **Frontend components**: `frontend/src/components/`
- **Frontend hooks**: `frontend/src/hooks/`
- **Frontend services**: `frontend/src/services/`

---

## Phase 1: Setup

**Purpose**: Add new dependency and create directory/file scaffolding.

- [x] T001 Add `weasyprint` to `backend/pyproject.toml` under `[project.dependencies]`
- [x] T002 [P] Create `db/src/db/models/rapid_review.py` with module docstring and empty stubs for enums and models (no logic yet)
- [x] T003 [P] Create `backend/src/backend/api/v1/rapid/__init__.py` with module docstring and empty `APIRouter` (no routes yet)
- [x] T004 [P] Create `backend/src/backend/api/v1/public/__init__.py` with module docstring and empty `APIRouter`
- [x] T005 [P] Create `agents/src/agents/prompts/narrative_synthesiser/` directory with empty `system.md` and `user.md.j2` stubs

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: ORM models, migration, phase gate wiring, and worker registration that every
user story depends on.

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete.

- [x] T006 [P] Define all six enums (`RRProtocolStatus`, `RRQualityAppraisalMode`, `RRInvolvementType`, `RRThreatType`, `BriefingStatus`; extend `CandidatePaperStatus` with `PROTOCOL_INVALIDATED`) in `db/src/db/models/rapid_review.py` per `data-model.md`
- [x] T007 Define all six ORM models (`RapidReviewProtocol`, `PractitionerStakeholder`, `RRThreatToValidity`, `RRNarrativeSynthesisSection`, `EvidenceBriefing`, `EvidenceBriefingShareToken`) with all columns, constraints, relationships, `version_id` optimistic locking, and audit fields in `db/src/db/models/rapid_review.py` per `data-model.md`
- [x] T008 Export all new models and enums from `db/src/db/models/__init__.py`
- [x] T009 Add `PROTOCOL_INVALIDATED` value to `CandidatePaperStatus` PostgreSQL enum definition in `db/src/db/models.py`
- [x] T010 Create Alembic migration `db/alembic/versions/0016_rapid_review_workflow.py`: creates all six new tables, adds `PROTOCOL_INVALIDATED` to `candidate_paper_status` enum via `ALTER TYPE ... ADD VALUE`; includes full `upgrade()` and best-effort `downgrade()` per `data-model.md`
- [x] T011 Create `backend/src/backend/services/rr_phase_gate.py` implementing `get_rr_unlocked_phases(study_id, db)` with the five phase-unlock conditions from `contracts/api-contracts.md` Phase Gate section
- [x] T012 Add `StudyType.RAPID: get_rr_unlocked_phases` entry to `_PHASE_GATE_DISPATCH` dict in `backend/src/backend/api/v1/studies/__init__.py`
- [x] T013 [P] Register `run_narrative_draft` and `run_generate_evidence_briefing` as stub async functions in `backend/src/backend/jobs/worker.py` `WorkerSettings.functions` list (stubs filled in US4/US5 phases)
- [x] T014 [P] Create `backend/src/backend/templates/rapid/` directory and empty `evidence_briefing.html.j2` stub

**Checkpoint**: Migration applies cleanly (`uv run alembic upgrade head`); `GET /api/v1/studies/{id}/phases` returns correct unlocked phases for a `RAPID` study.

---

## Phase 3: User Story 1 — Create and Configure a Rapid Review Protocol (Priority: P1)

**Goal**: A researcher can create a Rapid Review study, define its protocol (including
practitioner stakeholders, time/effort budget, context restrictions, research questions),
receive warnings for research-gap-style questions, and validate the protocol to unlock
the search phase.

**Independent Test**: Create a `RAPID` study → call `PUT /protocol` → call `POST /protocol/validate` → confirm status=`VALIDATED` and `GET /studies/{id}/phases` returns `[1, 2]`. Verify 422 when no stakeholder exists.

### Backend — US1

- [x] T015 [P] [US1] Create `backend/src/backend/services/rr_protocol_service.py` with: `get_or_create_protocol`, `update_protocol` (with invalidation cascade when `VALIDATED`), `validate_protocol` (pre-validation checks: stakeholder count, non-empty `research_questions`, non-empty `practical_problem`), `_detect_research_gap_questions` (keyword heuristic: "gap", "future work", "what is missing"), `_auto_create_threats` (creates `RRThreatToValidity` rows for active restrictions and mode choices)
- [x] T016 [P] [US1] Create `backend/src/backend/services/rr_protocol_service.py` — add `invalidate_papers_for_study(study_id, db)` helper that bulk-updates `CandidatePaper.status` to `PROTOCOL_INVALIDATED` for all papers belonging to the study
- [x] T017 [P] [US1] Create `backend/src/backend/api/v1/rapid/protocol.py`: `GET /rapid/studies/{study_id}/protocol`, `PUT /rapid/studies/{study_id}/protocol` (with `?acknowledge_invalidation=true` query param and 409 guard), `POST /rapid/studies/{study_id}/protocol/validate`; use `Depends` for auth and study-membership check
- [x] T018 [P] [US1] Create `backend/src/backend/api/v1/rapid/stakeholders.py`: `GET`, `POST`, `PUT /{stakeholder_id}`, `DELETE /{stakeholder_id}` for `PractitionerStakeholder`; `DELETE` of last stakeholder when protocol is `VALIDATED` triggers same 409 + invalidation cascade as protocol PUT
- [x] T019 [P] [US1] Create `backend/src/backend/api/v1/rapid/threats.py`: `GET /rapid/studies/{study_id}/threats` returning all `RRThreatToValidity` records (read-only)
- [x] T020 [US1] Register rapid router (`/api/v1/rapid`) in `backend/src/backend/api/v1/router.py` and wire `protocol.py`, `stakeholders.py`, `threats.py` routers into `rapid/__init__.py`

### Frontend — US1

- [x] T021 [P] [US1] Create `frontend/src/services/rapid/protocolApi.ts`: Zod schemas for `RRProtocol`, `RRProtocolUpdate`, `ValidationError`; typed fetch functions `getProtocol`, `updateProtocol` (passes `acknowledge_invalidation` when needed), `validateProtocol`, `getThreats`
- [x] T022 [P] [US1] Create `frontend/src/services/rapid/stakeholdersApi.ts`: Zod schemas for `Stakeholder`, `StakeholderCreate`; typed fetch functions `listStakeholders`, `createStakeholder`, `updateStakeholder`, `deleteStakeholder`
- [x] T023 [P] [US1] Create `frontend/src/hooks/rapid/useRRProtocol.ts`: TanStack Query hooks for protocol get/update/validate; includes acknowledgment dialog trigger logic when 409 received
- [x] T024 [P] [US1] Create `frontend/src/hooks/rapid/useStakeholders.ts`: TanStack Query hooks for stakeholder CRUD with optimistic updates
- [x] T025 [P] [US1] Create `frontend/src/components/rapid/ThreatToValidityList.tsx`: displays list of `RRThreatToValidity` records; each item shows threat type badge and description; read-only
- [x] T026 [P] [US1] Create `frontend/src/components/rapid/StakeholderPanel.tsx`: table of practitioners with add/edit/delete; inline `StakeholderForm` using react-hook-form + Zod; shows "at least one required" error state
- [x] T027 [US1] Create `frontend/src/components/rapid/ProtocolForm.tsx`: form with all protocol fields; `useWatch` for conditional rendering of context restriction builder; research-gap warning banner when `_detect_research_gap_questions` heuristic fires (driven by API response); embeds `StakeholderPanel` and `ThreatToValidityList`
- [x] T028 [US1] Create `frontend/src/pages/rapid/ProtocolEditorPage.tsx`: wraps `ProtocolForm`; handles 409 invalidation confirmation dialog (MUI `Dialog` with paper count); "Validate Protocol" action button; phase-nav breadcrumb
- [x] T029 [US1] Register Rapid Review protocol page route in `frontend/src/pages/StudyPage.tsx` under the existing study-phase navigation pattern

**Checkpoint**: User can create a `RAPID` study, open the protocol editor, add a stakeholder, fill fields, validate — phase 2 unlocks. Removing last stakeholder when validated triggers confirmation dialog.

---

## Phase 4: User Story 2 — Restricted Search and Paper Selection (Priority: P2)

**Goal**: A researcher configures a single-source search with optional restrictions (year,
language, geography, study design); restrictions auto-generate threat entries; single-reviewer
mode is toggleable with a persistent warning.

**Independent Test**: With a validated protocol, call the search-config endpoint to apply a year-range restriction → confirm a `YEAR_RANGE` `RRThreatToValidity` record is created; toggle `single_reviewer_mode=true` → confirm a `SINGLE_REVIEWER` threat is recorded and `GET /threats` returns both.

### Backend — US2

- [x] T030 [P] [US2] Add `configure_search_restrictions(study_id, restrictions, db)` to `backend/src/backend/services/rr_protocol_service.py`: accepts list of `{type, source_detail}` dicts, idempotently upserts `RRThreatToValidity` rows for each restriction type, removes threats for restrictions no longer present
- [x] T031 [P] [US2] Add `set_single_reviewer_mode(study_id, enabled, db)` to `rr_protocol_service.py`: updates `RapidReviewProtocol.single_reviewer_mode`; creates/removes `SINGLE_REVIEWER` `RRThreatToValidity` record accordingly
- [x] T032 [P] [US2] Create `backend/src/backend/api/v1/rapid/search_config.py`: `PUT /rapid/studies/{study_id}/search-config` (sets restrictions and single-reviewer mode via request body, calls service helpers, acknowledges `single_source_acknowledged` flag); returns updated threat list

### Frontend — US2

- [x] T033 [P] [US2] Create `frontend/src/components/rapid/SearchRestrictionPanel.tsx`: checklist UI for the four restriction types (year range, language, geography, study design); each restriction opens a detail input; calls `updateSearchConfig` on save; shows current `ThreatToValidityList` inline
- [x] T034 [P] [US2] Create `frontend/src/components/rapid/SingleReviewerWarningBanner.tsx`: persistent MUI `Alert` (severity=warning) rendered when `single_reviewer_mode=true`; includes toggle to enable/disable the mode with a confirmation step
- [x] T035 [US2] Create `frontend/src/pages/rapid/SearchConfigPage.tsx`: wraps `SearchRestrictionPanel` and `SingleReviewerWarningBanner`; integrates with existing database-selection UI (reuses `DatabaseSelectionPanel` from 006); phase-nav breadcrumb
- [x] T036 [US2] Register RR search config page route in `frontend/src/App.tsx`

**Checkpoint**: Applying a year-range restriction in the UI creates a threat; enabling single-reviewer mode creates a `SINGLE_REVIEWER` threat and renders the persistent warning banner; disabling removes both.

---

## Phase 5: User Story 3 — Quality Appraisal (Optional or Simplified) (Priority: P3)

**Goal**: A researcher can skip quality appraisal entirely or apply a peer-reviewed-only
filter; the chosen approach is recorded as a validity entry; phase 4 unlocks accordingly.

**Independent Test**: Set `quality_appraisal_mode=SKIPPED` on protocol → confirm `QA_SKIPPED` threat exists; verify phase 4 unlocks without requiring any `QualityAssessmentScore` rows.

### Backend — US3

- [x] T037 [P] [US3] Update `rr_phase_gate.py` `_is_quality_complete` check: if `RapidReviewProtocol.quality_appraisal_mode` is `SKIPPED` or `PEER_REVIEWED_ONLY`, return `True` immediately (skip the QualityAssessmentScore join query)
- [x] T038 [P] [US3] Add `set_quality_appraisal_mode(study_id, mode, db)` to `rr_protocol_service.py`: updates `quality_appraisal_mode`; creates/removes `QA_SKIPPED` or `QA_SIMPLIFIED` threat; if `PEER_REVIEWED_ONLY`, bulk-marks non-peer-reviewed `CandidatePaper` records as excluded
- [x] T039 [P] [US3] Create `backend/src/backend/api/v1/rapid/quality.py`: `GET /rapid/studies/{study_id}/quality-config` and `PUT /rapid/studies/{study_id}/quality-config` (sets mode, triggers peer-reviewed filter if applicable, returns updated threats)

### Frontend — US3

- [x] T040 [P] [US3] Create `frontend/src/components/rapid/QAModeSelector.tsx`: three-option radio group (`FULL` / `PEER_REVIEWED_ONLY` / `SKIPPED`) with inline explanations and consequences; shows `ThreatToValidityList` preview when non-FULL mode is selected
- [x] T041 [US3] Add quality appraisal mode selection step to `frontend/src/pages/rapid/SearchConfigPage.tsx` (or a dedicated `QualityConfigPage.tsx` if phase navigation warrants it); integrates `QAModeSelector`
- [x] T042 [US3] Register QA config route in `frontend/src/App.tsx` if a dedicated page was created

**Checkpoint**: Selecting SKIPPED in the UI removes the quality gate; selecting PEER_REVIEWED_ONLY auto-excludes non-peer-reviewed papers; phase 4 unlocks correctly in both cases.

---

## Phase 6: User Story 4 — Narrative Synthesis (Priority: P2)

**Goal**: A researcher edits one narrative section per research question, requests an
AI-generated draft per section, and marks all sections complete to gate briefing generation.

**Independent Test**: With included papers and a validated protocol, call `GET /synthesis` → verify one section per RQ; call `POST /{section_id}/ai-draft` → poll `BackgroundJob` to completion → verify `ai_draft_text` populated; call `PUT /{section_id}` with `is_complete=true` for all sections then `POST /synthesis/complete` → returns `{"synthesis_complete": true}`.

### Agent & Job — US4

- [x] T043 [P] [US4] Write `agents/src/agents/prompts/narrative_synthesiser/system.md`: system prompt instructing the agent to produce a practitioner-friendly narrative paragraph per research question from provided paper abstracts and titles; no methodology jargon; structured as 3–5 sentences
- [x] T044 [P] [US4] Write `agents/src/agents/prompts/narrative_synthesiser/user.md.j2`: Jinja2 template injecting `{{ research_question }}`, `{{ papers | length }}` included papers with `{{ paper.title }}`, `{{ paper.abstract }}`
- [x] T045 [P] [US4] Create `agents/src/agents/narrative_synthesiser_agent.py`: `NarrativeSynthesiserAgent` class using `LLMClient` (LiteLLM); `draft_section(study_id, rq_index, rq_text, papers, provider_config)` method returning drafted text string; Google-style docstrings throughout
- [x] T046 [US4] Create `backend/src/backend/jobs/narrative_synthesis_job.py`: `run_narrative_draft(ctx, *, section_id)` ARQ job function; fetches section + protocol + included papers; calls `NarrativeSynthesiserAgent.draft_section`; writes result to `RRNarrativeSynthesisSection.ai_draft_text`; updates `BackgroundJob` status (`RUNNING` → `COMPLETED` / `FAILED`)
- [x] T047 [US4] Replace stub in `backend/src/backend/jobs/worker.py` `WorkerSettings.functions` with the real `run_narrative_draft` import from `narrative_synthesis_job`

### Backend — US4

- [x] T048 [P] [US4] Create `backend/src/backend/services/narrative_synthesis_service.py`: `get_or_create_sections(study_id, db)` (auto-creates one `RRNarrativeSynthesisSection` per entry in `RapidReviewProtocol.research_questions` when protocol transitions to `VALIDATED`); `update_section(section_id, text, is_complete, db)`; `is_synthesis_complete(study_id, db)` (checks all sections `is_complete=True`)
- [x] T049 [P] [US4] Update `backend/src/backend/services/rr_protocol_service.py` `validate_protocol` to call `narrative_synthesis_service.get_or_create_sections` after status update (creates synthesis sections on first validation)
- [x] T050 [P] [US4] Create `backend/src/backend/api/v1/rapid/synthesis.py`: `GET /rapid/studies/{study_id}/synthesis` (list sections, includes `research_question` text from protocol), `PUT /rapid/studies/{study_id}/synthesis/{section_id}`, `POST /rapid/studies/{study_id}/synthesis/{section_id}/ai-draft` (enqueues ARQ job, 409 if job already running), `POST /rapid/studies/{study_id}/synthesis/complete` (validates all sections complete, 422 with incomplete indices if not)
- [x] T051 [US4] Wire `synthesis.py` router into `backend/src/backend/api/v1/rapid/__init__.py`

### Frontend — US4

- [x] T052 [P] [US4] Create `frontend/src/services/rapid/synthesisApi.ts`: Zod schemas for `NarrativeSection`, `SynthesisCompleteResponse`; fetch functions `listSections`, `updateSection`, `requestAIDraft`, `completeSynthesis`
- [x] T053 [P] [US4] Create `frontend/src/hooks/rapid/useNarrativeSynthesis.ts`: TanStack Query hooks for section list (with `refetchInterval` polling when any `ai_draft_job_id` is active), section mutation, AI draft trigger, synthesis complete mutation
- [x] T054 [P] [US4] Create `frontend/src/components/rapid/NarrativeSectionEditor.tsx`: single-section editor with: research question header, AI Draft button (disabled when draft job running; shows `CircularProgress`), two-pane layout (AI draft preview | editable `textarea`), "Accept Draft" button copies `ai_draft_text` → `narrative_text`, `is_complete` checkbox; MUI components throughout; named `NarrativeSectionEditorProps` interface
- [x] T055 [US4] Create `frontend/src/pages/rapid/NarrativeSynthesisPage.tsx`: renders one `NarrativeSectionEditor` per section; "Mark All Complete" shortcut; "Finalize Synthesis" CTA (calls `completeSynthesis`, shows 422 incomplete-sections error list); phase-nav breadcrumb
- [x] T056 [US4] Register RR synthesis page route in `frontend/src/App.tsx`

**Checkpoint**: AI draft button triggers job → draft appears within 30 s; "Finalize Synthesis" blocked until all sections complete; phase 5 unlocks after synthesis is finalized.

---

## Phase 7: User Story 5 — Generate and Export an Evidence Briefing (Priority: P1)

**Goal**: A researcher generates a versioned Evidence Briefing, promotes one version to
published, downloads it as PDF and HTML, generates a shareable link for practitioners,
and revokes the link when done.

**Independent Test**: With complete synthesis, `POST /briefings` → poll job → `GET /briefings` → confirm `version_number=1 status=DRAFT`; `POST /{id}/publish` → `GET /briefings` confirms `PUBLISHED`; `GET /{id}/export?format=pdf` returns a PDF; `POST /{id}/share-token` → `GET /public/briefings/{token}` without auth returns briefing JSON; `DELETE /share-token/{token}` → token returns 404.

### Job & Service — US5

- [x] T057 [P] [US5] Complete `backend/src/backend/templates/rapid/evidence_briefing.html.j2`: full one-page Jinja2 HTML template with all six required sections (Title, Summary, Findings per RQ, Target Audience Box, Reference to Complementary Material, Institution Logos); uses print CSS for A4/letter single-page layout; inlines all RR threat entries in Target Audience section
- [x] T058 [P] [US5] Create `backend/src/backend/services/evidence_briefing_service.py`: `create_new_version(study_id, db)` (auto-increments `version_number` per study); `publish_version(briefing_id, db)` (atomic promote: UPDATE previous PUBLISHED→DRAFT, then UPDATE target→PUBLISHED in one transaction); `generate_html(briefing_id, db)` (renders Jinja2 template, writes to disk, stores path); `generate_pdf(briefing_id, db)` (calls `weasyprint` on HTML, writes to disk, stores path); `create_share_token(briefing_id, created_by, db)` (generates `secrets.token_urlsafe(32)`, stores in `EvidenceBriefingShareToken`); `revoke_token(token, db)`; `resolve_token(token, db)` (returns published briefing or raises 404 if revoked/expired/no published version)
- [x] T059 [US5] Create `backend/src/backend/jobs/evidence_briefing_job.py`: `run_generate_evidence_briefing(ctx, *, briefing_id)` ARQ job; calls `generate_html` then `generate_pdf`; updates `BackgroundJob` status; handles `WeasyPrintError` gracefully (logs + sets FAILED status)
- [x] T060 [US5] Replace stub in `backend/src/backend/jobs/worker.py` `WorkerSettings.functions` with real `run_generate_evidence_briefing` import

### Backend API — US5

- [x] T061 [P] [US5] Create `backend/src/backend/api/v1/rapid/briefing.py`: `GET /rapid/studies/{study_id}/briefings`, `POST /rapid/studies/{study_id}/briefings` (requires synthesis complete, enqueues ARQ job, 422 otherwise), `GET /rapid/studies/{study_id}/briefings/{briefing_id}`, `POST /rapid/studies/{study_id}/briefings/{briefing_id}/publish`, `GET /rapid/studies/{study_id}/briefings/{briefing_id}/export?format=pdf|html` (StreamingResponse), `POST /rapid/studies/{study_id}/briefings/{briefing_id}/share-token`, `DELETE /rapid/studies/{study_id}/briefings/share-token/{token}`
- [x] T062 [P] [US5] Create `backend/src/backend/api/v1/public/briefings.py`: `GET /public/briefings/{token}` (no auth dependency; calls `resolve_token`; 404 on invalid/revoked/expired; returns `PublicBriefingResponse` excluding internal file paths), `GET /public/briefings/{token}/export?format=pdf|html` (StreamingResponse, no auth)
- [x] T063 [US5] Wire `briefing.py` into `backend/src/backend/api/v1/rapid/__init__.py` and `public/briefings.py` into `backend/src/backend/main.py` under `/api/v1/public` prefix

### Frontend — US5

- [x] T064 [P] [US5] Create `frontend/src/services/rapid/briefingApi.ts`: Zod schemas for `BriefingSummary`, `BriefingDetail`, `ShareToken`; fetch functions `listBriefings`, `generateBriefing`, `getBriefing`, `publishBriefing`, `exportBriefing` (returns Blob), `createShareToken`, `revokeShareToken`
- [x] T065 [P] [US5] Create `frontend/src/hooks/rapid/useBriefingVersions.ts`: TanStack Query hooks for briefing list (with `refetchInterval` when any generation job is pending), publish mutation, share token mutations
- [x] T066 [P] [US5] Create `frontend/src/components/rapid/BriefingVersionPanel.tsx`: list of `BriefingSummary` rows with version number, status badge, generation timestamp; "Publish" button on each `DRAFT` row (with confirmation); "Download PDF" / "Download HTML" buttons; "Copy Share Link" button (generates token, copies to clipboard); "Revoke" button next to active tokens
- [x] T067 [P] [US5] Create `frontend/src/components/rapid/BriefingPreview.tsx`: read-only preview of the six briefing sections in styled MUI `Paper` blocks; shows embedded threat list in Target Audience section
- [x] T068 [US5] Create `frontend/src/pages/rapid/EvidenceBriefingPage.tsx`: "Generate New Version" CTA at top (disabled until synthesis complete); renders `BriefingVersionPanel` and `BriefingPreview` for selected version; phase-nav breadcrumb
- [x] T069 [P] [US5] Create `frontend/src/pages/rapid/PublicBriefingPage.tsx`: no-auth route; fetches briefing via share token from URL param; renders `BriefingPreview`; graceful 404 state if token invalid/revoked
- [x] T070 [US5] Register RR briefing page and public briefing page routes in `frontend/src/App.tsx`

**Checkpoint**: Full quickstart.md walkthrough passes end-to-end (curl commands in steps 8–10); public briefing accessible without auth; token revocation works; PDF is one page.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Verification, quality gates, and hardening across all stories.

- [x] T071 Run full quickstart.md validation end-to-end per `specs/008-rapid-review-workflow/quickstart.md`; fix any gaps found
- [ ] T072 [P] Create Playwright E2E test suite `frontend/e2e/rapid-review/` covering: RR study creation → protocol editor → stakeholder → validation → search config → synthesis (AI draft flow) → briefing generation → publish → share-link → public page → revoke
- [x] T073 [P] Run `uv run ruff check` and `uv run ruff format --check` across `backend/src`, `agents/src`, `db/src`; fix all violations (including pre-existing violations in touched files)
- [x] T074 [P] Run `uv run mypy backend/src agents/src db/src` in strict mode; fix all type errors including any pre-existing errors in touched files
- [x] T075 [P] Run `cd frontend && npm run lint && npm run format:check`; fix all ESLint and Prettier violations in new and touched files
- [x] T076 [P] Run full test suite across all modified subprojects (`uv run pytest backend/tests/ agents/tests/ db/tests/` + `cd frontend && npm test`); confirm all tests pass including pre-existing tests; fix any failures
- [x] T077 [P] Measure test coverage (`--cov-fail-under=85`) for `db`, `backend`, `agents`; add tests to reach ≥85% if below threshold
- [x] T078 [P] Measure frontend coverage (`npm run test:coverage`); add tests to reach ≥85% if below threshold
- [ ] T079 Run mutation testing on all modified Python subprojects (`uv run cosmic-ray run backend/cosmic-ray.toml`, `db/cosmic-ray.toml`, `agents/cosmic-ray.toml`); achieve ≥85% kill rate on each; add targeted test assertions for surviving mutants
- [ ] T080 Run frontend mutation testing (`cd frontend && npx stryker run`); achieve ≥85% kill rate; add targeted test assertions for surviving mutants

---

## Phase 9.
: Feature Completion Documentation *(mandatory — Constitution Principle X)*

**Purpose**: Update all required documentation before the feature branch is merged.

> **These tasks MUST be completed before the feature is marked done. Omitting them is a
> blocking violation of Constitution Principle X (Feature Completion Documentation).**

- [X] TDOC1 [P] Update `CLAUDE.md` at repository root: add `008-rapid-review-workflow` to Active Technologies section (new dep: `weasyprint`; new entities: `RapidReviewProtocol`, `EvidenceBriefing`, `EvidenceBriefingShareToken`; new agent: `NarrativeSynthesiserAgent`; new migration: `0016_rapid_review_workflow`)
- [X] TDOC2 [P] Update `README.md` at repository root to document Rapid Review as a supported study type alongside SMS and SLR
- [X] TDOC3 [P] Update `CHANGELOG.md` at repository root with a new entry describing what was added by this feature (RR workflow, Evidence Briefing, share tokens, narrative synthesis AI)
- [X] TDOC4 [P] Update `README.md` in `backend/`, `agents/`, `db/`, `frontend/` with Rapid Review-specific additions
- [X] TDOC5 [P] Update `CHANGELOG.md` in `backend/`, `agents/`, `db/`, `frontend/` with the same level of detail as the root changelog entry

> **All TDOC tasks MUST be completed and committed before merge.**

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS all user stories**
- **US1 — Protocol (Phase 3)**: Depends on Foundational
- **US2 — Search Config (Phase 4)**: Depends on US1 (protocol must exist to configure search)
- **US3 — Quality Appraisal (Phase 5)**: Depends on US2 (papers must be selected before QA)
- **US4 — Narrative Synthesis (Phase 6)**: Depends on US3 or US2 (if QA skipped)
- **US5 — Evidence Briefing (Phase 7)**: Depends on US4 (synthesis must be complete)
- **Polish (Phase 8)**: Depends on all US phases
- **Documentation (Phase 9)**: Depends on Polish

### Within Each Phase

- Tasks marked `[P]` can run in parallel (they touch different files)
- Backend service → Backend route → Frontend service → Frontend hook → Frontend component → Frontend page

### Parallel Opportunities per Story

```bash
# Phase 2 Foundational — parallel:
# T006 (enums) → T007 (models) → T008 (exports) → T009 (enum ext) → T010 (migration)
# T011 (worker stubs) — parallel with T006–T010
# T012 (template stub) — parallel with T006–T011
# T013 (phase gate) — can start after T007

# Phase 3 (US1) backend tasks parallel:
# T015 (protocol service) / T016 (invalidation helper) / T018 (stakeholders route)
# / T019 (threats route) — all parallel after Foundational complete

# Phase 3 (US1) frontend tasks parallel:
# T021 (protocolApi) / T022 (stakeholdersApi) — parallel
# T023 (useRRProtocol) / T024 (useStakeholders) — parallel after T021/T022
# T025 (ThreatToValidityList) / T026 (StakeholderPanel) — parallel
```

---

## Implementation Strategy

### MVP: User Stories 1 + 5 only (P1 stories)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1 (Protocol) — validate: create RR study, add stakeholder, validate protocol
4. Skip US2 + US3 — treat as "search complete, QA skipped" for MVP by manually seeding papers
5. Complete Phase 6: US4 (Narrative Synthesis) — core AI-draft flow
6. Complete Phase 7: US5 (Evidence Briefing) — generation, publish, share link
7. **STOP and VALIDATE**: run quickstart.md steps 1–3, 7–10

### Incremental Delivery

1. Foundation + US1 → RR study with validated protocol (demo-able)
2. + US2 → Search restrictions and single-reviewer mode (demo-able)
3. + US3 → QA mode selection (demo-able)
4. + US4 → AI narrative drafting (demo-able)
5. + US5 → Evidence Briefing with share link (full feature)

---

## Notes

- `[P]` tasks = different files, no blocking dependencies on other incomplete tasks
- `[USN]` label maps each task to a user story for traceability
- Tests are integrated into the Polish phase (T072–T080); TDD is not requested for this feature
- Constitution compliance: all tasks MUST respect Principles I–X (SOLID, DRY, YAGNI, Code Clarity, Refactoring, GRASP/Patterns, Testing, Toolchain, Observability, Language, Feature Completion Docs)
- All source files MUST have a module-level doc comment (Python module docstring / TS file-level JSDoc) per Constitution v1.7.0 (Principle III)
- All functions/methods/classes MUST have Google-style docstrings (Python) or JSDoc (TS); CLI handlers: brief description only — no Args/Returns
- Before the feature is marked complete, all tests (including pre-existing), linting, and static analysis MUST pass with zero failures — pre-existing issues MUST be fixed (T073–T076)
- Before the feature is marked complete, mutation testing MUST be run against every modified subproject (T079–T080); ≥85% mutants killed each
- New DB models MUST include `created_at`/`updated_at` audit fields (Principle VIII) — all 6 new models comply per `data-model.md`
- `RapidReviewProtocol` and `EvidenceBriefing` include `version_id` for optimistic locking (Principle VIII)
- New agent services MUST route LLM calls through `LLMClient`; prompts in `prompts/` (Principle VII)
- TypeScript MUST NOT use `any`/`enum`/non-null(`!`); use `unknown`+Zod at all external API boundaries (Principle IX)
- React components MUST be functional, have a named props interface, and be ≤100 JSX lines (Principle IX)
