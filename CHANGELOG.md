# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.10.0] — 2026-03-31 — feature/010-research-protocol-definition

### Added
- **Reusable protocol graph model**: `ResearchProtocol` with versioned directed acyclic graphs
  of `ProtocolNode` tasks (23 `ProtocolTaskType` values), typed I/O slots, `QualityGate`
  (JSONB config supporting `min_kappa`, `min_papers`, `completion_ratio`, `human_sign_off`
  gate types), `NodeAssignee`, and conditional `ProtocolEdge` triples
  (`output_name` / `operator` / `value`)
- **4 default protocol templates** seeded at migration time for all study types: SMS, SLR,
  Rapid Review, and Tertiary; each template encodes the canonical task sequence for that
  workflow; templates are immutable (`is_default_template = True`, no owner)
- **Protocol Library** (`GET/POST /api/v1/protocols`, `GET/PUT/DELETE /protocols/{id}`):
  authenticated CRUD with ownership checks; copy-from-existing shorthand; optimistic locking
  via `version_id`; filter by `study_type`
- **YAML export/import** (`GET /protocols/{id}/export`, `POST /protocols/import`):
  `ProtocolYamlService` serialises the full graph to schema-versioned YAML; import validates
  schema version `"1.0"` via Pydantic `@field_validator` and creates a new owned protocol
- **Study protocol assignment** (`GET/PUT/DELETE /studies/{id}/protocol-assignment`): assign
  any compatible protocol to a study; reset to default template (clears execution state;
  blocked while any task is `ACTIVE`); assignment tracked in `StudyProtocolAssignment`
- **Protocol execution engine** (`ProtocolAssignmentService`, `CompleteTaskService`,
  `ApproveTaskService`): seeds `TaskExecutionState` rows on assignment; activates eligible
  tasks (all required inputs satisfied); evaluates quality gates on task completion; unlocks
  downstream tasks; `human_sign_off` gate failures require explicit approval
- **Quality gate evaluators**: `kappa_coefficient` (reads Cohen's κ from SLR inter-rater
  service), `paper_count`, `paper_screened_ratio`, `qa_completeness` metric readers wired
  into a `_METRIC_READERS` dispatch dict
- **Execution state API** (`GET /studies/{id}/execution-state`,
  `POST /studies/{id}/execution-state/{task_id}/complete`,
  `POST /studies/{id}/execution-state/{task_id}/approve`): full task status list with
  `activated_at`, `completed_at`, `gate_failure_detail`
- **Frontend Protocol Library page** (`/protocols`): MUI list with study-type filter, Copy /
  Assign / Export / Import YAML actions; navigates to editor on copy or select
- **Frontend Protocol editor** (`/protocols/:id`): dual-pane layout — left: D3 force-directed
  graph with drag-to-reposition (edit mode); right: YAML `<textarea>` with 300 ms debounced
  bidirectional sync; Save calls `PUT /protocols/{id}` with `version_id`; conflict dialog on
  409; registered at `/protocols` and `/protocols/:id` in `App.tsx`
- **Protocol tab in StudyPage (Phase 0)**: always-unlocked tab showing ProtocolGraph (read
  only) + ProtocolNodePanel detail drawer; Execution sub-tab with task table, Mark Complete
  / Approve buttons; Reset to Default button with confirmation dialog
- **Real-time execution polling**: `useExecutionState` hook polls every 5 s while any task
  is `ACTIVE` (satisfies SC-005); stops polling when all tasks are terminal
- **Playwright e2e tests** (`frontend/e2e/protocols.spec.ts`): 5 tests covering graph view,
  node detail, protocol library copy, editor save, execution state, and YAML export/import
- **Alembic migration `0018_research_protocol_definition`**: creates 8 PostgreSQL enums and
  8 tables (`research_protocol`, `protocol_node`, `protocol_node_input`,
  `protocol_node_output`, `quality_gate`, `node_assignee`, `protocol_edge`,
  `study_protocol_assignment`, `task_execution_state`); seeds 4 default templates;
  full `downgrade()` path

## [0.9.0] — 2026-03-30 — feature/009-tertiary-studies-workflow

### Added
- **Tertiary Study type**: new `Tertiary` study type with a 5-phase workflow for aggregating
  and synthesising secondary studies (SLRs, SMSs, and Rapid Reviews)
- **`TertiaryStudyProtocol`** ORM + `GET/PUT /api/v1/tertiary/studies/{id}/protocol`:
  background, research questions, secondary study type filter (`SLR`, `SMS`, `RAPID_REVIEW`,
  `UNKNOWN`), inclusion/exclusion criteria, recency cutoff year, search strategy,
  quality threshold, synthesis approach, dissemination strategy; status lifecycle
  (`draft` → `validated`); `TertiaryProtocolForm` frontend component with read-only state
  when validated
- **Tertiary Phase Gate** (`backend/src/backend/services/tertiary_phase_gate.py`):
  `get_tertiary_unlocked_phases()` progressively unlocks 5 phases — Phase 1 always open;
  Phase 2 requires validated `TertiaryStudyProtocol`; Phase 3 requires ≥1 `CandidatePaper`;
  Phase 4 requires all accepted papers have QA scores; Phase 5 requires ≥2 validated
  `TertiaryDataExtraction` records; wired into `GET /api/v1/studies/{id}/phases` via
  `StudyType.TERTIARY` dispatch entry
- **`SecondaryStudySeedImport`** ORM + seed import API
  (`GET/POST /api/v1/tertiary/studies/{id}/seed-imports`): import candidate secondary
  studies from other platform studies; records `source_study_id`, `records_added`,
  `records_skipped`; `source_seed_import_id` FK column added to `CandidatePaper`
- **`TertiaryDataExtraction`** ORM + extraction API
  (`GET/PUT /api/v1/tertiary/papers/{id}/extraction`): nine secondary-study-specific
  fields (`secondary_study_type`, `research_questions_addressed`, `databases_searched`,
  `study_period_start`/`end`, `primary_study_count`, `synthesis_approach_used`,
  `key_findings`, `research_gaps`); `reviewer_quality_rating` (0–1); `extraction_status`
  lifecycle (`pending` → `ai_complete` → `human_reviewed`); AI pre-fill via ARQ job
  (`tertiary_extraction_job.py`) and `TertiaryExtractionAgent`
- **Tertiary Report** (`GET /api/v1/tertiary/studies/{id}/report`): `TertiaryReportService`
  assembles a landscape section (secondary study type distribution, year range, total
  primary study count), per-RQ synthesis from validated extraction records, and
  cross-cutting recommendations; `TertiaryReportPage` frontend with JSON/CSV/Markdown export
- **`NarrativeSynthesisStrategy`** and **`ThematicAnalysisStrategy`**: two new synthesis
  strategies in `backend/src/backend/services/synthesis_strategies.py` supporting tertiary
  synthesis jobs; dispatched via existing ARQ `synthesis_job.py` extended for `Tertiary`
  study type
- **`TertiaryQAService`** (`services/tertiary_qa_service.py`): computes per-paper QA
  gate status (accepted / needs-review / rejected) based on `reviewer_quality_rating`
  against protocol `quality_threshold`
- **Tertiary API router** (`api/v1/tertiary/`): mounted at `/api/v1/tertiary/`; sub-routers
  for `protocol`, `seed_imports`, `extractions`, and `report`
- **Alembic migration `0017_tertiary_studies_workflow`**: creates
  `tertiary_protocol_status_enum`, `secondary_study_type_enum`; creates tables
  `tertiary_study_protocol`, `secondary_study_seed_import`, `tertiary_data_extraction`;
  adds `source_seed_import_id` FK column to `candidate_paper`; full `downgrade()` path
- **Frontend Tertiary components** (`src/components/tertiary/`): `TertiaryProtocolForm`,
  `TertiaryExtractionForm`, `TertiaryQAGuidancePanel`, `SeedImportPanel`
- **Frontend Tertiary pages**: `TertiaryStudyPage` (5-phase tab layout),
  `TertiaryReportPage` (landscape + synthesis + recommendations with export actions)
- **Frontend Tertiary hooks** (`src/hooks/tertiary/`): `useProtocol`, `useExtractions`,
  `useSeedImports` — all TanStack Query v5 with Zod-parsed responses
- **Frontend Tertiary services** (`src/services/tertiary/`): `protocolApi.ts`,
  `extractionApi.ts`, `seedImportApi.ts`
- **`NewStudyWizard` updated**: Tertiary Study type option with explanatory info banner
  describing the aggregation-of-secondary-studies workflow

## [0.8.0] — 2026-03-29 — feature/008-rapid-review-workflow

### Added
- **Rapid Review study type**: new `Rapid` study type with an accelerated 6-phase workflow
  aimed at producing practitioner-facing outputs within compressed timelines
- **Rapid Review Protocol** (`RapidReviewProtocol` ORM + `GET/PUT /api/v1/rapid/studies/{id}/protocol`):
  scope, research question, timeframe, team fields; quality appraisal mode select
  (`full` / `critical_appraisal_only` / `descriptive`); status lifecycle (`draft` → `validated`);
  `ProtocolForm` frontend component
- **RR Phase Gate** (`backend/src/backend/services/rr_phase_gate.py`): `get_rr_unlocked_phases()`
  progressively unlocks phases based on protocol validation, stakeholder count, and synthesis
  completion; wired into `GET /api/v1/studies/{id}/phases` via `StudyType` dispatch dict
- **Practitioner Stakeholders** (`PractitionerStakeholder` ORM; CRUD under
  `/api/v1/rapid/studies/{id}/stakeholders`): named practitioner contacts (no platform account);
  `involvement_type` — `advisor`, `co-investigator`, `reviewer`, `end_user`, `commissioner`;
  `StakeholderPanel` frontend component; minimum one practitioner required to unlock Phase 3
- **Search Configuration** (`RRSearchConfig` / `RRSearchRestriction` ORM;
  `GET/PUT /api/v1/rapid/studies/{id}/search-config`): date range, language, and source type
  restrictions; `SearchRestrictionPanel` frontend component
- **Quality Appraisal Config** (`RRQAConfig` / `RRQAItem` ORM;
  `GET/PUT /api/v1/rapid/studies/{id}/qa-config`): appraisal mode and individual item definitions;
  `QAModeSelector` + `QAConfigPage` frontend; `SingleReviewerWarningBanner` for single-reviewer risk
- **Threats to Validity** (`RRThreatToValidity` ORM): auto-created threat records seeded on
  protocol validation based on QA mode; `ThreatToValidityList` frontend component; exposed in
  Evidence Briefing target audience section
- **Narrative Synthesis** (`RRNarrativeSynthesisSection` ORM — one per research question;
  `GET /api/v1/rapid/studies/{id}/narrative-synthesis`,
  `PATCH /api/v1/rapid/studies/{id}/narrative-synthesis/{section_id}`,
  `POST /api/v1/rapid/studies/{id}/narrative-synthesis/{section_id}/ai-draft`,
  `POST /api/v1/rapid/studies/{id}/narrative-synthesis/complete`):
  per-section `narrative_text` editor with AI draft (ARQ job); `is_complete` flag;
  Mark All Complete bulk action; Finalize Synthesis CTA raises HTTP 422 when sections are incomplete;
  `NarrativeSectionEditor` + `NarrativeSynthesisPage` frontend with TanStack Query polling
- **`NarrativeSynthesiserAgent`** (`agents/src/agents/narrative_synthesiser_agent.py`):
  LLM-powered narrative draft generation for a single research question; prompt templates in
  `agents/src/agents/prompts/narrative_synthesiser/`
- **Evidence Briefing** (`EvidenceBriefing` ORM with versioning; `BriefingStatus`: `draft` →
  `published`; `GET/POST /api/v1/rapid/studies/{id}/briefings`,
  `GET/POST /api/v1/rapid/studies/{id}/briefings/{id}`,
  `POST /api/v1/rapid/studies/{id}/briefings/{id}/publish`,
  `GET /api/v1/rapid/studies/{id}/briefings/{id}/export`): auto-incremented
  `version_number` per study; `publish_version` atomically demotes prior published version then
  promotes; `generate_html` via Jinja2 A4 template; `generate_pdf` via WeasyPrint;
  `BriefingVersionPanel` + `BriefingPreview` + `EvidenceBriefingPage` frontend with 3 s polling
  while PDF is generating
- **Evidence Briefing Share Tokens** (`EvidenceBriefingShareToken` ORM;
  `POST /api/v1/rapid/studies/{id}/briefings/{id}/share-token`,
  `DELETE /api/v1/rapid/briefings/share-token/{token}`): `secrets.token_urlsafe(32)`;
  optional `expires_at`; revocable at any time; unauthenticated public endpoints return
  published briefing data + binary PDF
- **Public Briefing Endpoints** (`GET /api/v1/public/briefings/{token}`,
  `GET /api/v1/public/briefings/{token}/export`): no authentication required; validate token
  expiry and revocation; return published `EvidenceBriefing` content or PDF;
  `PublicBriefingPage` frontend at `/public/briefings/:token` (outside `RequireAuth`)
- **Jinja2 A4 HTML template** (`backend/src/backend/templates/rapid/evidence_briefing.html.j2`):
  6 sections — title page, executive summary, per-RQ findings, target audience + validity
  threats, complementary reference list, institution logos; print CSS with
  `@page { size: A4; margin: 1.5cm; }`
- **ARQ background jobs**: `evidence_briefing_job.py` (Jinja2→HTML→WeasyPrint PDF, stored on
  disk at `/tmp/briefings/{id}/`); `narrative_synthesis_job.py` (per-section AI draft via
  `NarrativeSynthesiserAgent`)
- **Alembic migration `0016_rapid_review_workflow`**: creates `rr_protocol`, `rr_search_config`,
  `rr_search_restriction`, `rr_qa_config`, `rr_qa_item`, `practitioner_stakeholder`,
  `rr_threat_to_validity`, `rr_narrative_section`, `evidence_briefing`,
  `evidence_briefing_share_token` tables; full `downgrade()` path
- **New Python dependency**: `weasyprint` for HTML→PDF generation
- **RR rapid router** (`/api/v1/rapid/`): registered in `backend/src/backend/api/v1/router.py`;
  sub-routers for protocol, search_config, qa_config, stakeholders, narrative synthesis,
  and briefings
- **Frontend RR components** (`src/components/rapid/`): `ProtocolForm`, `QAModeSelector`,
  `SearchRestrictionPanel`, `StakeholderPanel`, `SingleReviewerWarningBanner`,
  `ThreatToValidityList`, `NarrativeSectionEditor`, `BriefingPreview`, `BriefingVersionPanel`
- **Frontend RR pages** (`src/pages/rapid/`): `ProtocolEditorPage`, `SearchConfigPage`,
  `QAConfigPage`, `StakeholderPage`, `NarrativeSynthesisPage`, `EvidenceBriefingPage`,
  `PublicBriefingPage`
- **Frontend RR hooks** (`src/hooks/rapid/`): `useRRProtocol`, `useSearchConfig`,
  `useQAConfig`, `useStakeholders`, `useNarrativeSynthesis`, `useBriefingVersions`; all use
  TanStack Query v5 with Zod-parsed responses
- **Frontend RR services** (`src/services/rapid/`): `protocolApi.ts`, `searchConfigApi.ts`,
  `qaConfigApi.ts`, `stakeholdersApi.ts`, `synthesisApi.ts`, `briefingApi.ts`; binary Blob
  export via raw `fetch` with Bearer token; all responses Zod-validated
- **`StudyPage.tsx` wired for Rapid**: phase 0–6 routing delegates to RR page components
  when `study.study_type === 'rapid'`; phase 6 renders `EvidenceBriefingPage`

## [0.7.0] — 2026-03-21 — feature/007-slr-workflow

### Added
- **SLR Protocol editor** (`ReviewProtocol` ORM + `GET/PUT /api/v1/slr/studies/{id}/protocol`):
  full PICO/S fields, synthesis approach select, status lifecycle (`draft` → `validated`);
  `ProtocolForm` frontend component with Zod validation and read-only state when validated
- **Protocol review agent** (`ProtocolReviewerAgent` in `agents/src/agents/services/protocol_reviewer.py`):
  LLM-powered structured review of protocol sections; `POST /api/v1/slr/studies/{id}/protocol/review`
  triggers ARQ job; `ProtocolReviewReport` stores strengths, weaknesses, and recommendations per section
- **SLR Phase Gate** (`backend/src/backend/services/slr_phase_gate.py`): unlocks study phases
  progressively as protocol is validated, papers are screened, and QA thresholds are met;
  wired into `GET /api/v1/studies/{id}/phases` via dispatch dict keyed on `StudyType`
- **Quality Assessment system**: `QualityChecklist` / `QualityChecklistItem` / `QualityScore` ORM
  models; `GET/PUT /api/v1/slr/studies/{id}/quality-checklist` upsert endpoint;
  `GET/PUT /api/v1/slr/papers/{id}/quality-scores` per-reviewer scoring;
  `QualityChecklistEditor` and `QualityScoreForm` frontend components
- **Inter-Rater Reliability** (`backend/src/backend/services/inter_rater_service.py`):
  Cohen's κ computation via `scikit-learn`; `GET /api/v1/slr/studies/{id}/inter-rater-reliability`;
  `InterRaterPanel` frontend component with κ gauge and per-pair breakdown
- **Synthesis pipeline** (`backend/src/backend/services/synthesis_service.py` +
  `synthesis_strategies.py`): `SynthesisResult` ORM; ARQ background job triggered by
  `POST /api/v1/slr/studies/{id}/synthesis`; three strategies — `MetaAnalysisStrategy` (pooled
  effect size, Forest/Funnel SVG plots via `scipy` + `matplotlib`), `DescriptiveSynthesisStrategy`,
  `QualitativeSynthesisStrategy`; `SynthesisPage` frontend with `ForestPlotViewer` / `FunnelPlotViewer`
- **Grey Literature tracking** (`GreyLiteratureSource` ORM; `GET/POST/DELETE /api/v1/slr/studies/{id}/grey-literature`):
  dissertation, report, preprint, conference, website, other source types;
  `GreyLiteraturePanel` and `GreyLiteraturePage` frontend components
- **SLR Report generation** (`SLRReportService`; `GET /api/v1/slr/studies/{id}/report`):
  structured Markdown report aggregating protocol, search, screening, QA, and synthesis results;
  `ReportPage` frontend with download button
- **Alembic migration `0015_slr_workflow`**: creates `review_protocol`, `protocol_review_report`,
  `quality_checklist`, `quality_checklist_item`, `quality_score`, `synthesis_result`,
  `grey_literature_source` tables; full `downgrade()` path
- **New Python libraries**: `scipy>=1.13`, `scikit-learn>=1.5`, `numpy>=1.26`
- **E2e test** (`frontend/e2e/slr-workflow.spec.ts`): Playwright test covering the full SLR workflow
  happy path

## [0.6.0] — 2026-03-18 — feature/006-database-search-and-retrieval

### Added
- **Multi-database fan-out search**: `search_papers` MCP tool queries up to 9 academic databases
  in parallel (IEEE Xplore, ACM DL, Scopus, Web of Science, Inspec, ScienceDirect,
  SpringerNature, Google Scholar, Semantic Scholar); results merged and deduplicated by DOI
  then by normalised title + first author last name
- **`DatabaseSource` typing.Protocol** (`researcher-mcp/src/researcher_mcp/sources/base.py`):
  `search()` and `get_paper()` signatures; `normalise_to_paper_record()` helper; `VenueType`
  literal type
- **Source adapters**: `IEEESource`, `ACMSource`, `ScopusSource`, `WoSSource`, `InspecSource`,
  `ScienceDirectSource`, `SpringerSource`, `GoogleScholarSource`; existing `SemanticScholarSource`
  updated; all registered in `SourceRegistry`
- **`StudyDatabaseSelection` ORM model** (`db/src/db/models/search_integrations.py`): tracks
  active `DatabaseIndex` values per study; `selected_indices` JSON array column; `created_at`
  / `updated_at` audit fields
- **`SearchIntegrationCredential` ORM model**: stores Fernet-encrypted `api_key_encrypted` per
  `IntegrationType` with optional `base_url`, `inst_token`; `version_id` optimistic locking;
  `last_tested_at`, `test_status` (`TestStatus` enum), `test_message` for connectivity state
- **Alembic migration `0014_database_search_and_retrieval`**: creates both new tables; adds
  `full_text_markdown` (Text), `full_text_source` (enum), `full_text_converted_at` (DateTime)
  columns to `paper` table; full `downgrade()` path
- **`CredentialService`** (`backend/src/backend/services/credential_service.py`):
  `upsert_credential`, `get_credential`, `get_effective_key` (DB key → env var fallback),
  `configured_via` (database / environment / not_configured), `run_connectivity_test`,
  `_probe_ieee` (live HTTP probe with `TestStatus` result); `VersionConflictError` on stale write
- **Admin Search Integrations endpoints** (`GET/PUT /api/v1/admin/search-integrations`):
  list all integration types with configuration status; upsert credentials; trigger connectivity
  test; response never includes raw key
- **`SearchIntegrationsTable` frontend component**: MUI DataGrid listing all 9 integration types
  with status chip (configured/environment/not_configured), last-tested timestamp, test button;
  credential edit dialog with version-safe save
- **Study database-selection REST** (`GET/PUT /api/v1/studies/{id}/database-selection`): read and
  write active `DatabaseIndex` list for a study
- **`DatabaseSelectionPanel` frontend component**: checkbox panel inside Study Settings for
  toggling which databases are queried; `useStudyDatabaseSelection` hook
- **Full-text PDF retrieval** (`fetch_paper_pdf` MCP tool): tries Unpaywall open-access first;
  falls back to Sci-Hub when `SCIHUB_ENABLED=true` and `scihub_acknowledged=True` is passed;
  `scidownl` backend; result stored as `full_text_markdown` via `MarkItDown` conversion
- **Markdown conversion MCP tools**: `convert_pdf_to_markdown` (bytes → markdown),
  `convert_url_to_markdown` (URL → markdown via HTTP + MarkItDown),
  `fetch_stored_markdown` (retrieve previously stored markdown from DB)
- **`/api/v1/papers/{id}/markdown`** endpoint (`GET`): return stored `full_text_markdown` for a
  paper; `PaperMarkdownService` and `paper_markdown.py` API router
- **New env vars**: `IEEE_XPLORE_API_KEY`, `ELSEVIER_API_KEY`, `ELSEVIER_INST_TOKEN`,
  `WOS_API_KEY`, `SPRINGER_API_KEY`, `SEMANTIC_SCHOLAR_API_KEY`, `UNPAYWALL_EMAIL`,
  `SCHOLARLY_PROXY_URL`, `SCIHUB_ENABLED`

### Changed
- `researcher-mcp/pyproject.toml`: added `pybliometrics`, `semanticscholar`, `scholarly`,
  `unpywall`, `springernature-api-client`, `markitdown[all]`, `scidownl` dependencies
- `search_papers` tool updated to accept `indices: list[str] | None` and fan out via
  `SourceRegistry`; `SearchPapersResult` extended with `sources_failed` field
- `snowball_references` and `snowball_citations` tools updated for Semantic Scholar paths
- Admin page: added **Search Integrations** tab

---

## [0.5.0] — 2026-03-17 — feature/005-models-and-agents

### Added
- **`Provider` DB table**: stores Anthropic, OpenAI, and Ollama provider records; API key
  encrypted at rest via Fernet (PBKDF2HMAC key derivation from `SECRET_KEY`); `has_api_key`
  flag returned in API responses instead of the key itself
- **`AvailableModel` DB table**: models fetched from each provider's API; unique constraint on
  `(provider_id, model_identifier)`; individual models can be enabled or disabled
- **`Agent` DB table**: agent definitions with `task_type` (screener/extractor/librarian/
  expert/quality_judge/agent_generator/domain_modeler/synthesiser/validity_assessor),
  role/persona fields, Jinja2 `system_message_template`, `system_message_undo_buffer`, FK
  to provider and model; optimistic locking via `version_id`
- **`reviewer.agent_id`**: nullable UUID FK from `Reviewer` → `Agent` (SET NULL on delete);
  migration `0012_models_and_agents` seeds a default Anthropic provider, `AgentGenerator`,
  `Screener`, and `Extractor` agent records and backfills existing Reviewer rows
- **Stub migration `0013_remove_reviewer_agent_name`**: signals cleanup debt for the legacy
  `reviewer.agent_name` column without executing the removal prematurely
- **`ProviderService`**: CRUD for providers; `fetch_models_anthropic/openai/ollama` fetchers;
  `refresh_models` upserts model rows without losing enable/disable state; raises
  `ProviderHasDependentsError` (HTTP 409) when deletion is blocked
- **`AgentService`**: CRUD, Jinja2 template validation (strict allowlist), `generate_system_message`
  via `AgentGeneratorAgent`, `generate_persona_svg`, undo buffer swap, study-context rendering
  `render_system_message(template, agent, domain, study_type)`
- **`backend/utils/encryption.py`**: `encrypt_secret` / `decrypt_secret` using Fernet
- **Admin API endpoints** under `/api/v1/admin/`:
  - `GET/POST /providers`, `GET/PATCH/DELETE /providers/{id}`,
    `POST /providers/{id}/refresh-models`, `GET /providers/{id}/models`,
    `PATCH /providers/{id}/models/{model_id}`
  - `GET/POST /agents`, `GET/PATCH/DELETE /agents/{id}`,
    `POST /agents/{id}/generate-system-message`, `POST /agents/{id}/undo-system-message`,
    `POST /agents/generate-persona-svg`, `GET /agent-task-types`
- **`ProviderConfig` Protocol** (`agents/core/provider_config.py`): runtime-checkable
  `typing.Protocol` with `model_string`, `api_base`, `api_key` attributes; all agent classes
  accept `provider_config: ProviderConfig | None = None` to override env-based settings
- **`LLMClient` update**: optional `provider_config` parameter overrides model, api_base, and
  api_key per-call; env-based behavior unchanged when omitted
- **`AgentGeneratorAgent`** (`agents/agent_generator.py`): generates Jinja2 system message
  templates given role and persona inputs; prompt templates in
  `agents/prompts/agent_generator/`
- **All existing agent classes updated**: `ScreenerAgent`, `ExtractorAgent`, `LibrarianAgent`,
  `ExpertAgent`, `QualityJudgeAgent`, `DomainModelerAgent`, `SynthesiserAgent`, `ValidityAgent`
  all accept optional `provider_config` and route it through `LLMClient`
- **Study-context rendering**: all agent invocation paths in backend services/jobs call
  `render_system_message` with study `domain` and `study_type` before dispatching to agents
- **Frontend admin components**: `ProviderList`, `ProviderForm`, `ModelList`, `AgentList`,
  `AgentWizard` (5-step MUI Stepper, `useReducer` state), `AgentForm`, `SystemMessageEditor`
- **Frontend types**: Zod schemas + inferred interfaces in `types/provider.ts` and `types/agent.ts`
- **TanStack Query hooks**: `providersApi.ts` and `agentsApi.ts` with full Zod parse on all responses
- **Admin panel tabs**: Providers, Models, and Agents tabs added to `AdminPage.tsx`
- **`AgentGeneratorAgent` eval pipeline** (`agent-eval/pipelines/agent_generator_eval.py`):
  DeepEval `AnswerRelevancyMetric` + `FaithfulnessMetric`; threshold 0.8
- **Metamorphic tests** for `AgentGeneratorAgent`: `hypothesis`-based property tests verifying
  all required Jinja2 variable placeholders survive role-description paraphrasing
- **Playwright e2e tests**: `test_provider_management.spec.ts`, `test_agent_wizard.spec.ts`
- Unit + integration tests for all new services, endpoints, and utilities; ≥85% coverage
  across all packages

---

## [0.4.0] — 2026-03-16 — feature/004-frontend-improvements

### Added
- **Password change**: `PUT /me/password` — verifies current password, enforces complexity
  (min 12 chars, uppercase, digit, special character), invalidates all prior sessions via
  `User.token_version` increment
- **Two-factor authentication (TOTP)**: full lifecycle — QR code setup, confirmation,
  disabling, backup codes (10 per batch, bcrypt-hashed, single-use), brute-force lockout
  after 5 failures; partial JWT for 2FA second step
- **Theme preference**: Light / Dark / System per-user setting stored in DB; MUI
  ThemeProvider with `matchMedia` listener for system mode
- **Full MUI v5 migration**: all frontend components migrated to MUI `sx` prop and component library
- **Authenticated API docs**: `GET /api/v1/openapi.json` requires valid JWT; Swagger UI
  at `/api-docs`; default `/docs` and `/redoc` endpoints disabled
- `SecurityAuditEvent` and `BackupCode` DB models
- E2e Playwright specs: `preferences-password`, `two-factor-auth`, `theme`, `api-docs`

### Changed
- `GET /api/v1/auth/me` response now includes `theme_preference` and `totp_enabled`
- `POST /api/v1/auth/login` returns TOTP challenge when 2FA is enabled
- `get_current_user` validates `token_version` via DB lookup to detect invalidated sessions

---

## [0.3.0] — 2026-03-16 — feature/003-project-setup-improvements

### Added
- `cosmic-ray` configured as the standard Python mutation testing tool (replaces `mutmut`)
- `stryker` and `cosmic-ray` exposed as manually-triggered `workflow_dispatch` GitHub Actions
  workflows; both are also triggered automatically at the end of every speckit feature
  implementation
- GitHub Actions coverage gate: build fails if line coverage drops below 85% for any service;
  PR comment posted with coverage summary
- `pytest` build gate: any `@pytest.mark.skip` or `@pytest.mark.xfail` without `reason=`
  causes the test run to fail
- Frontend environment setup (Node 20 LTS, `npm install`) documented in `CLAUDE.md`
- `vitest run --coverage` command and 85% CI gate added for frontend TypeScript coverage
- Constitution v1.6.0: Principle X — Feature Completion Documentation mandates `CLAUDE.md`,
  `README.md`, and `CHANGELOG.md` updates at the end of every feature

### Changed
- `CLAUDE.md` updated to reflect `cosmic-ray` as the mutation testing tool
- `README.md` tech stack updated: `mutmut` → `cosmic-ray`, CI description expanded

---

## [0.2.0] — 2026-03-12 — feature/002-sms-workflow

### Added
- Full six-subproject UV workspace: `backend`, `agents`, `db`, `agent-eval`,
  `researcher-mcp`, `frontend`
- **backend**: FastAPI REST gateway with endpoints for studies, papers, screening criteria,
  PICO elements, search strings, quality assessment, and results; JWT auth middleware;
  structlog request-scoped logging; ARQ background job queue
- **agents**: `ScreenerAgent`, `ExtractorAgent`, and `SynthesiserAgent` as an importable
  Python library; Jinja2 prompt templates; MCP tool integration via `MCPClient`
- **db**: SQLAlchemy 2.x async ORM with `Study`, `Paper`, and `StudyPaper` models; Alembic
  migrations; PostgreSQL 16 (production) and SQLite (development/test) support
- **agent-eval**: Typer CLI (`evaluate`, `report`, `compare`, `improve`) for LLM-as-a-Judge
  agent evaluation using DeepEval + LiteLLM
- **researcher-mcp**: FastMCP 2.0 server with five tools — `search_papers`, `get_paper`,
  `search_authors`, `get_author`, `fetch_paper_pdf`; Semantic Scholar → OpenAlex cascade;
  tenacity retry with exponential backoff; per-source token-bucket rate limiting
- **frontend**: React 18 / TypeScript 5.4 SPA; TanStack Query; React Hook Form + Zod;
  D3.js + Recharts; React Router v6; Vite 5; Vitest; Stryker mutation testing
- Docker Compose stack with multi-stage builds, health checks, and `depends_on` ordering
- GitHub Actions CI: lint, typecheck, pytest, Vitest coverage, Docker scan, GHCR push
- `ARQ`, `matplotlib`, `networkx`, `plotly + kaleido`, `rapidfuzz`, `deepeval`,
  `hypothesis` added as Python dependencies
- `D3.js`, `TanStack Query`, `React Hook Form` added as frontend dependencies

---

## [0.1.0] — 2026-03-11 — feature/001-repo-setup

### Added
- Initial UV workspace mono-repo structure with root `pyproject.toml`
- Python 3.14 runtime pinned across all packages
- TypeScript 5.4 / Node 20 LTS frontend toolchain
- Ruff (lint + format), MyPy strict, pytest + pytest-asyncio baseline configuration
- Pre-commit hooks: `ruff check`, `ruff format --check`, `mypy`, `hadolint`
- Docker multi-stage build base configuration (`python:3.14-slim`, `nginx:alpine`)
- `.env.example` with required environment variable documentation
- MIT License (Copyright 2026 Isaac Griffith, PhD)
- `CLAUDE.md` with Claude Code guidance for the repository
