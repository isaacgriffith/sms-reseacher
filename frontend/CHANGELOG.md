# Changelog — sms-frontend

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.10.0] — 2026-03-31 — feature/010-research-protocol-definition

### Added
- **`ProtocolGraph` component** (`src/components/protocols/ProtocolGraph.tsx`):
  D3 force-directed SVG; read-only mode in StudyPage (click-to-select node); edit mode in
  `ProtocolEditorPage` adds drag-to-reposition (updates `position_x`/`position_y` in reducer)
  and click-to-select-edge; imperative D3 setup extracted to `useProtocolD3.ts`
- **`ProtocolNodePanel` component** (`src/components/protocols/ProtocolNodePanel.tsx`):
  MUI Drawer showing `label`, `task_type`, `description`, `inputs`, `outputs`, `quality_gates`,
  `assignees` in read-only mode; edit mode adds react-hook-form fields and delegates save to
  `onSave` callback dispatching `UPDATE_NODE` to the editor reducer
- **`ProtocolTextEditor` component** (`src/components/protocols/ProtocolTextEditor.tsx`):
  monospace `<textarea>` YAML editor; inline parse-error display; `onChange` triggers
  `dispatchYamlDebounced` from `useProtocolEditor`
- **`ProtocolList` component** (`src/components/protocols/ProtocolList.tsx`):
  MUI List of `ProtocolListItem`s; per-row Copy, Assign, Export, and Delete action buttons;
  `is_default_template` badge; `study_type` chip
- **`QualityGateEditor` component** (`src/components/protocols/QualityGateEditor.tsx`):
  `gate_type` MUI Select with conditional config fields per type; Zod-validated; dispatches
  gate config to editor reducer
- **`EdgeConditionBuilder` component** (`src/components/protocols/EdgeConditionBuilder.tsx`):
  `output_name` selector, operator MUI Select (`gt`/`gte`/`lt`/`lte`/`eq`/`neq`), numeric
  `value` input; null condition = unconditional edge
- **`ExecutionStateView` component** (`src/components/protocols/ExecutionStateView.tsx`):
  task status table showing `label`, `task_type`, `status`, `activated_at`, `completed_at`;
  Mark Complete button (calls `useCompleteTask`); Approve button for `human_sign_off` failures
  (calls `useApproveTask`); reads from `useExecutionState` 5 s polling hook
- **`ProtocolLibraryPage`** (`src/pages/protocols/ProtocolLibraryPage.tsx`):
  registered at `/protocols`; `useProtocolList` query with `study_type` MUI Select filter;
  renders `ProtocolList`; Copy dialog (name input → `useCopyProtocol`, redirects to editor);
  Assign dialog (study ID input → `useAssignProtocol`); Import YAML button (hidden
  `<input type="file">` → `useImportProtocol`); per-row Export calls `exportProtocol` (blob
  download via anchor)
- **`ProtocolEditorPage`** (`src/pages/protocols/ProtocolEditorPage.tsx`):
  registered at `/protocols/:id`; loads protocol via `useProtocolDetail`; initialises
  `useProtocolEditor` reducer; dual-pane layout (left: `ProtocolGraph` edit mode, right:
  `ProtocolTextEditor`); Save calls `useUpdateProtocol` with `version_id`; conflict dialog
  on 409; Discard navigates back
- **`useProtocol.ts`** hooks (`src/hooks/protocols/useProtocol.ts`):
  `useProtocolList`, `useProtocolDetail`, `useProtocolAssignment` queries;
  `useCopyProtocol`, `useCreateProtocol`, `useUpdateProtocol`, `useDeleteProtocol`,
  `useImportProtocol`, `useResetProtocol`, `useAssignProtocol` mutations;
  all with appropriate `queryKey` invalidations on success
- **`useExecutionState.ts`** hooks (`src/hooks/protocols/useExecutionState.ts`):
  `useExecutionState` — polls every 5 s while any task status is `active`, stops when all
  terminal (satisfies SC-005); `useCompleteTask`, `useApproveTask` mutations invalidate the
  execution-state query on success
- **`useProtocolEditor.ts`** (`src/hooks/protocols/useProtocolEditor.ts`):
  `useProtocolEditor` — `useReducer` with `graphReducer`; actions: `SET_GRAPH`, `ADD_NODE`,
  `REMOVE_NODE`, `UPDATE_NODE`, `ADD_EDGE`, `REMOVE_EDGE`, `UPDATE_EDGE`, `SELECT_NODE`,
  `SET_YAML`; `graphToYaml` / `yamlToGraph` serialisation utilities using `js-yaml`;
  `dispatchYamlDebounced` with 300 ms debounce
- **`useProtocolD3.ts`** (`src/hooks/protocols/useProtocolD3.ts`):
  extracts all D3 `forceSimulation`, drag behaviour, and SVG rendering from `ProtocolGraph`;
  returns `svgRef` and `render` function; simulation cleanup on unmount
- **`protocolsApi.ts`** (`src/services/protocols/protocolsApi.ts`):
  Zod-validated wrappers for all Protocol REST endpoints; `exportProtocol` uses raw `fetch`
  + blob anchor download; `importProtocol` uses raw `fetch` with `FormData` (bypasses
  `api.post` JSON-encoding); `resetProtocol` uses raw `fetch` DELETE with JSON body;
  `assignProtocol` uses `api.put`; `getExecutionState`, `completeTask`, `approveTask` use `api`
- **Protocol tab added to `StudyPage`** (`src/pages/StudyPage.tsx`): Phase 0 always unlocked;
  Graph sub-tab shows `ProtocolGraph` + `ProtocolNodePanel`; Execution sub-tab shows
  `ExecutionStateView`; Reset to Default button opens MUI Dialog
- **`/protocols` and `/protocols/:id` routes** registered in `src/App.tsx`
- **Playwright e2e tests** (`e2e/protocols.spec.ts`): 5 tests — graph view + node detail,
  protocol library copy, editor save, assign to study, execution state, YAML export/import

## [0.9.0] — 2026-03-30 — feature/009-tertiary-studies-workflow

### Added
- **`TertiaryProtocolForm` component** (`src/components/tertiary/TertiaryProtocolForm.tsx`):
  react-hook-form + Zod form for Tertiary protocol fields; all fields disabled when status
  is `validated`; validates that at least one research question and one secondary study type
  are provided; `useWatch` throughout
- **`TertiaryExtractionForm` component** (`src/components/tertiary/TertiaryExtractionForm.tsx`):
  data extraction form for nine secondary-study-specific fields plus `reviewer_quality_rating`
  slider; shows MUI `Alert` AI pre-fill banner when `extraction_status` is `ai_complete`;
  submits with `extraction_status` set to `human_reviewed`
- **`TertiaryQAGuidancePanel` component** (`src/components/tertiary/TertiaryQAGuidancePanel.tsx`):
  MUI Accordion listing six mandatory QA dimensions (Protocol Documentation Completeness, Search
  Strategy Adequacy, Inclusion/Exclusion Criteria Clarity, Quality Assessment Approach,
  Synthesis Method Appropriateness, Validity Threats Discussion)
- **`SeedImportPanel` component** (`src/components/tertiary/SeedImportPanel.tsx`):
  table of existing seed imports; dialog to select and import from another platform study within
  the same group; shows `records_added`/`records_skipped`; disables already-imported studies;
  "Importing…" pending state; mutation error display
- **`TertiaryStudyPage`** (`src/pages/TertiaryStudyPage.tsx`): 5-phase MUI Tab layout;
  Phase 1 — protocol editor + Validate Protocol action; Phase 2 — seed import panel;
  Phase 3 — paper queue (screening); Phase 4 — QA guidance + extraction forms; Phase 5 —
  synthesis config; locked phases shown with `LockIcon`
- **`TertiaryReportPage`** (`src/pages/TertiaryReportPage.tsx`): fetches tertiary report via
  `GET /tertiary/studies/{id}/report`; renders Background section, per-RQ landscape findings,
  Recommendations; JSON/CSV/Markdown download buttons using `window.open`
- **Tertiary hooks** (`src/hooks/tertiary/`):
  - `useProtocol.ts` — `useProtocol`, `useUpdateProtocol`
  - `useExtractions.ts` — `useExtractions`, `useUpdateExtraction`, `useAiAssist`
  - `useSeedImports.ts` — `useSeedImports`, `useCreateSeedImport`, `useGroupStudies`
- **Tertiary services** (`src/services/tertiary/`):
  - `protocolApi.ts` — Tertiary protocol read/update with Zod schemas
  - `extractionApi.ts` — extraction read/update and AI assist trigger; Zod-validated
  - `seedImportApi.ts` — seed import list and creation endpoints; Zod-validated
- **`NewStudyWizard` updated** (`src/components/studies/NewStudyWizard.tsx`): Tertiary Study
  type option; info banner explaining the aggregation-of-secondary-studies purpose when
  `selectedStudyType === 'Tertiary'`

## [0.8.0] — 2026-03-29 — feature/008-rapid-review-workflow

### Added
- **`ProtocolForm` component** (`src/components/rapid/ProtocolForm.tsx`): react-hook-form + Zod
  form for Rapid Review protocol fields (scope, research question, timeframe, team); `useWatch`
  throughout; save delegates to `useUpdateRRProtocol` mutation
- **`QAModeSelector` component** (`src/components/rapid/QAModeSelector.tsx`): MUI radio group
  for quality appraisal mode selection (`full`/`critical_appraisal_only`/`descriptive`)
- **`SearchRestrictionPanel` component** (`src/components/rapid/SearchRestrictionPanel.tsx`):
  date range, language filter, and source type restriction controls backed by `useSearchConfig`
- **`StakeholderPanel` component** (`src/components/rapid/StakeholderPanel.tsx`): MUI Table
  of practitioner stakeholders with Add/Edit/Delete actions; validation requires at least one
  practitioner before Phase 3 unlocks; `readOnly` prop for locked phases
- **`SingleReviewerWarningBanner` component** (`src/components/rapid/SingleReviewerWarningBanner.tsx`):
  MUI `Alert` warning displayed when QA mode implies single-reviewer risk
- **`ThreatToValidityList` component** (`src/components/rapid/ThreatToValidityList.tsx`):
  read-only MUI List of auto-created validity threat records embedded in Evidence Briefing
- **`NarrativeSectionEditor` component** (`src/components/rapid/NarrativeSectionEditor.tsx`):
  per-RQ section editor with MUI `TextField`, "Request AI Draft" action, `is_complete` checkbox,
  pending/error state from `useUpdateSection` and `useRequestAIDraft`
- **`BriefingPreview` component** (`src/components/rapid/BriefingPreview.tsx`): read-only MUI
  Paper rendering Title, Executive Summary, per-RQ Findings, Target Audience + threat Chips,
  Reference list, and Institution Logos sections
- **`BriefingVersionPanel` component** (`src/components/rapid/BriefingVersionPanel.tsx`):
  MUI Table of briefing versions with status Chip; Publish (with confirmation dialog), Download
  PDF/HTML (`URL.createObjectURL` Blob), Copy Share Link actions
- **`ProtocolEditorPage`** (`src/pages/rapid/ProtocolEditorPage.tsx`): RR protocol editor with
  `ProtocolForm` + phase gate status
- **`SearchConfigPage`** (`src/pages/rapid/SearchConfigPage.tsx`): search restriction management
- **`QAConfigPage`** (`src/pages/rapid/QAConfigPage.tsx`): QA mode and checklist item management
- **`StakeholderPage`** (`src/pages/rapid/StakeholderPage.tsx`): practitioner stakeholder management
- **`NarrativeSynthesisPage`** (`src/pages/rapid/NarrativeSynthesisPage.tsx`): renders one
  `NarrativeSectionEditor` per research question; Mark All Complete bulk action; Finalize
  Synthesis CTA (polls via `useCompleteSynthesis`); 422 error handling with incomplete section
  list display
- **`EvidenceBriefingPage`** (`src/pages/rapid/EvidenceBriefingPage.tsx`): Generate Briefing
  CTA; `BriefingVersionPanel` (version history table); `BriefingPreview` (selected version);
  3 s `refetchInterval` polling while any briefing lacks `pdf_available`
- **`PublicBriefingPage`** (`src/pages/rapid/PublicBriefingPage.tsx`): unauthenticated page at
  `/public/briefings/:token`; renders full briefing with Download PDF button; graceful 404/403
  error state; outside `RequireAuth` guard in `App.tsx`
- **RR hooks** (`src/hooks/rapid/`): `useRRProtocol`, `useUpdateRRProtocol`; `useSearchConfig`,
  `useUpdateSearchConfig`; `useQAConfig`, `useUpdateQAConfig`; `useStakeholders`,
  `useCreateStakeholder`, `useUpdateStakeholder`, `useDeleteStakeholder`;
  `useNarrativeSections`, `useUpdateSection`, `useRequestAIDraft`, `useCompleteSynthesis`;
  `useBriefings`, `useGenerateBriefing`, `usePublishBriefing`, `useCreateShareToken`,
  `useRevokeShareToken`; all use TanStack Query v5 with Zod-parsed responses
- **RR services** (`src/services/rapid/`): `protocolApi.ts`, `searchConfigApi.ts`,
  `qaConfigApi.ts`, `stakeholdersApi.ts`, `synthesisApi.ts`, `briefingApi.ts`; binary Blob
  PDF export via raw `fetch` with Bearer token; `ApiError` class with `status` + `detail` fields;
  all responses validated through Zod schemas before being returned to hooks
- **`App.tsx`**: `<Route path="/public/briefings/:token" element={<PublicBriefingPage />} />`
  added outside `RequireAuth`; RR phase routes added under study workspace
- **`StudyPage.tsx`**: phase 0–6 delegation to RR page components when `study.study_type === 'rapid'`

### Changed
- `StudyPage.tsx`: renders `RREvidenceBriefingPage` for phase 6 when study is Rapid type

## [0.7.0] — 2026-03-21 — feature/007-slr-workflow

### Added
- **`ProtocolForm` component** (`src/components/slr/ProtocolForm.tsx`): react-hook-form + Zod
  form for PICO/S protocol fields (population, intervention, comparator, outcome, context),
  synthesis approach selector, and inclusion/exclusion criteria; `useWatch` throughout;
  save delegates to `useUpdateProtocol` mutation
- **`ProtocolReviewReport` component** (`src/components/slr/ProtocolReviewReport.tsx`):
  renders per-section AI review output (strengths, weaknesses, recommendations) returned by
  `ProtocolReviewReport` ORM
- **`QualityChecklistEditor` component** (`src/components/slr/QualityChecklistEditor.tsx`):
  MUI DataGrid for configuring checklist items with binary/numeric scoring method and weight
- **`QualityScoreForm` component** (`src/components/slr/QualityScoreForm.tsx`): per-reviewer
  score submission form; conditionally renders checkbox (binary) or numeric input based on
  `scoring_method`
- **`InterRaterPanel` component** (`src/components/slr/InterRaterPanel.tsx`): displays
  Cohen's κ with colour-coded interpretation band (poor/fair/moderate/good/excellent) and
  percentage agreement
- **`DiscussionFlowPanel` component** (`src/components/slr/DiscussionFlowPanel.tsx`):
  step-by-step resolution panel for reconciling inter-rater disagreements
- **`SynthesisConfigForm` component** (`src/components/slr/SynthesisConfigForm.tsx`):
  synthesis approach selector (meta-analysis / descriptive / qualitative) with dynamic
  parameter fields per approach
- **`ForestPlotViewer` component** (`src/components/slr/ForestPlotViewer.tsx`): renders
  Forest plot SVG from meta-analysis synthesis result; download SVG button
- **`FunnelPlotViewer` component** (`src/components/slr/FunnelPlotViewer.tsx`): renders
  Funnel plot SVG for publication bias visualisation
- **`GreyLiteraturePanel` component** (`src/components/slr/GreyLiteraturePanel.tsx`):
  CRUD table for non-database literature sources (dissertation, report, preprint, conference,
  website)
- **`ProtocolEditorPage`** (`src/pages/slr/ProtocolEditorPage.tsx`, route
  `/slr/:studyId/protocol`): full-page protocol editor with inline `ProtocolReviewReport` and
  "Run AI Review" action
- **`QualityAssessmentPage`** (`src/pages/slr/QualityAssessmentPage.tsx`, route
  `/slr/:studyId/quality`): checklist editor and per-reviewer score forms side by side
- **`SynthesisPage`** (`src/pages/slr/SynthesisPage.tsx`, route `/slr/:studyId/synthesis`):
  synthesis config form, job trigger, and Forest/Funnel plot display on completion
- **`GreyLiteraturePage`** (`src/pages/slr/GreyLiteraturePage.tsx`, route
  `/slr/:studyId/grey-literature`): grey literature source management page
- **`ReportPage`** (`src/pages/slr/ReportPage.tsx`, route `/slr/:studyId/report`): renders
  Markdown SLR report with copy-to-clipboard and download actions
- **SLR hooks** (`src/hooks/slr/`): `useProtocol`, `useCreateProtocol`, `useUpdateProtocol`,
  `useTriggerProtocolReview`; `useQualityChecklist`, `useCreateChecklist`,
  `useUpdateChecklist`, `useSubmitScore`; `useInterRaterStats`, `useKappaScore`;
  `useSynthesisResult`, `useTriggerSynthesis`; `useGreyLiteratureSources`,
  `useAddGreyLiteratureSource`, `useDeleteGreyLiteratureSource`
- **SLR services** (`src/services/slr/`): `protocolApi.ts`, `qualityApi.ts`,
  `interRaterApi.ts`, `synthesisApi.ts`, `greyLiteratureApi.ts`, `reportApi.ts`; all
  responses parsed through Zod schemas; all hooks use TanStack Query v5
- **SLR routes** registered in `App.tsx` under `/slr/:studyId/` prefix; SideNav updated
  with SLR section links for SLR study type

---

## [0.6.0] — 2026-03-18 — feature/006-database-search-and-retrieval

### Added
- **`SearchIntegrationsTable` component** (`src/components/admin/SearchIntegrationsTable/`):
  MUI DataGrid listing all 9 academic database integration types; status chip (configured via
  database / environment / not_configured); last-tested timestamp; "Test" button per row;
  credential edit dialog with version-safe save (optimistic locking)
- **`DatabaseSelectionPanel` component** (`src/components/studies/DatabaseSelectionPanel/`):
  checkbox panel in Study Settings for toggling which database indices are queried
- **`useSearchIntegrations` hook** (`src/hooks/useSearchIntegrations.ts`): TanStack Query hooks —
  `useSearchIntegrations`, `useUpsertSearchIntegration`, `useTestSearchIntegration`
- **`useStudyDatabaseSelection` hook** (`src/hooks/useStudyDatabaseSelection.ts`): TanStack Query
  hooks — `useStudyDatabaseSelection`, `useUpdateStudyDatabaseSelection`
- **Admin panel**: Search Integrations tab added to `AdminPage.tsx`
- **Study page**: Database Selection panel added to Study Settings section of `StudyPage.tsx`

---

## [0.5.0] — 2026-03-17 — feature/005-models-and-agents

### Added
- **`src/types/provider.ts`**: Zod schemas and inferred TypeScript interfaces for `Provider`,
  `ProviderCreate`, `ProviderUpdate`, `AvailableModel`, `ModelRefreshResult`; provider type
  as string literal union `'anthropic' | 'openai' | 'ollama'` (no TS enum)
- **`src/types/agent.ts`**: Zod schemas and inferred interfaces for `Agent`, `AgentCreate`,
  `AgentSummary`, `SystemMessageGenerateResult`, `PersonaSvgGenerateResult`; `task_type` as
  string literal union matching `AgentTaskType` values
- **`src/services/providersApi.ts`**: TanStack Query hooks — `useProviders`, `useProvider`,
  `useCreateProvider`, `useUpdateProvider`, `useDeleteProvider`, `useRefreshModels`,
  `useProviderModels`, `useToggleModel`; all responses parsed through Zod schemas
- **`src/services/agentsApi.ts`**: TanStack Query hooks — `useAgents`, `useAgent`,
  `useCreateAgent`, `useUpdateAgent`, `useDeleteAgent`, `useGenerateSystemMessage`,
  `useUndoSystemMessage`, `useGeneratePersonaSvg`, `useAgentTaskTypes`; Zod parse on all
- **`ProviderList.tsx`** (`components/admin/providers/`): MUI Table listing provider type,
  display name, enabled status, `has_api_key` badge, and action buttons (edit, delete,
  refresh-models)
- **`ProviderForm.tsx`** (`components/admin/providers/`): react-hook-form + Zod; `useWatch`
  on `provider_type` to conditionally show `api_key` (Anthropic/OpenAI) or `base_url`
  (Ollama) field
- **`ModelList.tsx`** (`components/admin/models/`): MUI Table with per-row enable/disable
  toggle; scoped to a `providerId` prop
- **`AgentList.tsx`** (`components/admin/agents/`): MUI Table with role_name, persona_name,
  task_type, model display name, is_active badge, and edit action
- **`SystemMessageEditor.tsx`** (`components/admin/agents/`): `React.memo` multiline
  TextField with `{{ variable }}` syntax highlighting; exposes `value`, `onChange`,
  `onUndo`, `canUndo` props
- **`AgentWizard.tsx`** (`components/admin/agents/`): 5-step MUI Stepper (task type → model
  → role/persona → SVG → system message review); `useReducer` wizard state; "Generate
  System Message" and "Generate SVG" mutation buttons; submits via `useCreateAgent`
- **`AgentForm.tsx`** (`components/admin/agents/`): react-hook-form + Zod edit form;
  embeds `SystemMessageEditor`; "Generate/Update System Message" and "Undo" buttons;
  `useWatch` on `model_id` to warn on disabled model
- **AdminPage tabs**: "Providers", "Models", and "Agents" MUI Tabs added to
  `src/pages/AdminPage.tsx`
- Playwright e2e tests: `frontend/e2e/admin/test_provider_management.spec.ts`,
  `frontend/e2e/admin/test_agent_wizard.spec.ts`

---

## [0.4.0] — 2026-03-16 — feature/004-frontend-improvements

### Added
- **Preferences page** (`/preferences`): tabbed UI for Password, Theme, and 2FA settings
- **Password change form**: React Hook Form + Zod (min 12 chars, uppercase, digit, special);
  real-time complexity indicator via `useWatch`
- **Theme selector**: MUI `ToggleButtonGroup` — Light / Dark / System; persisted to DB and
  localStorage; `useColorMode` hook registers `matchMedia` listener for System mode
- **Two-factor authentication UI**: `TwoFactorSetupDialog` (4-step `useReducer` flow with
  Stepper — idle → QR display → code entry → backup codes); `TwoFactorSettings` panel
  (status badge, disable form, backup code regeneration)
- **TOTP login second step**: `LoginPage` shows TOTP code input after `requires_totp: true`
  response; handles 429 lockout message and "Back to sign in" navigation
- **API docs page** (`/api-docs`): TanStack Query fetches authenticated OpenAPI schema;
  renders `<SwaggerUI>` from `swagger-ui-react`
- **Side nav**: "Preferences" and "API Docs" links added
- `useTotp` hooks: `useTotpSetup`, `useTotpConfirm`, `useTotpDisable`, `useBackupCodesRegenerate`
- `loginUser` function in `api.ts` with Zod discriminated union (`LoginSuccess | LoginTotpRequired`)
- E2e Playwright specs: `preferences-password`, `two-factor-auth`, `theme`, `api-docs`
- Vitest tests: `useColorMode`, `ThemeSelector`, `TwoFactorSetupDialog`, `TwoFactorSettings`

### Changed
- **Full MUI v5 migration**: all 30+ components replaced inline styles with MUI `sx` prop,
  `Box`, `Typography`, `Button`, `TextField`, `Alert`, `Paper`, `Card`, `Grid`, `Tabs`, etc.
- `ThemeContext`: reads `themePreference` from auth store; `setThemePreference` calls API
- `LoginPage`: migrated to MUI; now handles optional TOTP second-step screen

---

## [0.3.0] — 2026-03-16 — feature/003-project-setup-improvements

### Added
- Playwright (TypeScript) added as the e2e testing tool for full-stack browser and API tests
- Frontend environment setup (Node 20 LTS, `npm install`) documented in `CLAUDE.md`
- `vitest run --coverage` coverage command documented in `CLAUDE.md`
- GitHub Actions CI gate: build fails if TypeScript line coverage drops below 85%;
  coverage summary posted as PR comment
- Stryker mutation testing exposed as manual `workflow_dispatch` GitHub Actions workflow;
  also triggered automatically at end of every speckit feature implementation

---

## [0.2.0] — 2026-03-12 — feature/002-sms-workflow

### Added
- React 18 / TypeScript 5.4 SPA bootstrapped with Vite 5
- Routing via React Router DOM v6
- Server-state management with TanStack Query v5 (`@tanstack/react-query`) and
  `refetchInterval` polling for long-running job status
- Form handling with React Hook Form v7 + Zod validation schemas; `useWatch` used
  throughout (not `watch()`) for reactive field subscriptions
- Data visualisation with D3.js v7 (network graphs) and Recharts v2 (result charts)
- Component and unit tests with Vitest + `@testing-library/react` + `jsdom`
- Mutation testing with `@stryker-mutator/core` + `@stryker-mutator/vitest-runner`
- ESLint 9 with `typescript-eslint` and `eslint-plugin-react-hooks`; Prettier 3
  (`singleQuote`, `trailingComma: "all"`, `printWidth: 100`, `tabWidth: 2`)
- Husky + `lint-staged`: `eslint --fix` and `prettier --write` on staged `.ts`/`.tsx`
- TypeScript config: `strict`, `noUnusedLocals`, `noUnusedParameters`,
  `noFallthroughCasesInSwitch`

---

## [0.1.0] — 2026-03-11 — feature/001-repo-setup

### Added
- Initial `package.json` with Node 20 LTS / TypeScript 5.4 baseline
- Vite 5 build and dev-server configuration
- ESLint, Prettier, and Husky pre-commit hook setup
