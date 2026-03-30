# sms-frontend

React 18 / TypeScript 5.4 single-page application for SMS Researcher. Provides the researcher-facing UI for managing systematic studies, screening papers, and viewing results.

## Setup

```bash
# From this directory
npm install

# Start development server (http://localhost:5173)
npm run dev

# Production build
npm run build

# Run unit/component tests
npm test

# Run tests with coverage
npx vitest run --coverage

# Run e2e tests (requires backend + db running)
npx playwright test

# Lint
npm run lint

# Format check
npx prettier --check src/
```

## Mutation Testing

Stryker mutation testing is run via a manually-triggered GitHub Actions workflow. To run locally:

```bash
npx stryker run
```

Minimum acceptable mutation score: **85% mutants killed**.

## Tech Stack

| Concern | Library |
|---------|---------|
| Build / dev server | Vite 5 |
| UI framework | React 18 (functional components + hooks only) |
| Language | TypeScript 5.4 (`strict`, `noUnusedLocals`) |
| Routing | React Router DOM v6 |
| Server state / data fetching | TanStack Query v5 (`refetchInterval` polling) |
| Forms | React Hook Form v7 + Zod validation (`useWatch` — not `watch()`) |
| Data visualisation | D3.js v7 (network graphs), Recharts v2 (result charts) |
| Unit / component tests | Vitest + `@testing-library/react` + `jsdom` |
| E2e tests | Playwright (TypeScript) — full-stack browser + API |
| Mutation testing | Stryker (`@stryker-mutator/vitest-runner`) |
| Linting | ESLint 9 + `typescript-eslint` + `eslint-plugin-react-hooks` |
| Formatting | Prettier 3 (`singleQuote`, `trailingComma: "all"`, `printWidth: 100`) |
| Pre-commit | Husky + `lint-staged` (eslint + prettier on staged `.ts`/`.tsx`) |

## Environment Variables

All client-side variables **must** use the `VITE_` prefix and be accessed via `import.meta.env.VITE_*`.

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend REST API base URL |

## Admin Tabs

The `AdminPage` component (`src/pages/AdminPage.tsx`) exposes three MUI tabs:

| Tab | Components | Query hooks |
|-----|-----------|-------------|
| **Providers** | `ProviderList`, `ProviderForm` | `useProviders`, `useCreateProvider`, `useUpdateProvider`, `useDeleteProvider`, `useRefreshModels` |
| **Models** | `ModelList` | `useProviderModels`, `useToggleModel` |
| **Agents** | `AgentList`, `AgentWizard`, `AgentForm` | `useAgents`, `useCreateAgent`, `useUpdateAgent`, `useDeleteAgent`, `useGenerateSystemMessage`, `useUndoSystemMessage`, `useGeneratePersonaSvg`, `useAgentTaskTypes` |
| **Search Integrations** | `SearchIntegrationsTable` | `useSearchIntegrations`, `useUpsertSearchIntegration`, `useTestSearchIntegration` |

`AgentWizard` is a 5-step MUI `Stepper` (task type → model → role/persona → SVG → system
message review) with state managed via `useReducer`. `SystemMessageEditor` is a
`React.memo` component that highlights `{{ variable }}` template placeholders.

All API responses are parsed through Zod schemas before being returned from hooks.

## Rapid Review Components (008-rapid-review-workflow)

New components, hooks, and services supporting the accelerated Rapid Review workflow:

### RR Components (`src/components/rapid/`)

| Component | Description |
|-----------|-------------|
| `ProtocolForm` | react-hook-form + Zod form for RR protocol fields; `useWatch` throughout |
| `QAModeSelector` | MUI radio group for quality appraisal mode (`full` / `critical_appraisal_only` / `descriptive`) |
| `SearchRestrictionPanel` | Date range, language, and source type restriction controls |
| `StakeholderPanel` | MUI Table for practitioner stakeholder CRUD; `readOnly` prop for locked phases |
| `SingleReviewerWarningBanner` | MUI `Alert` when QA mode implies single-reviewer risk |
| `ThreatToValidityList` | Read-only list of auto-created validity threat records |
| `NarrativeSectionEditor` | Per-RQ section editor with AI draft request, `is_complete` toggle, pending/error state |
| `BriefingPreview` | Read-only evidence briefing renderer (Title, Summary, Findings, Target Audience, Reference, Logos) |
| `BriefingVersionPanel` | MUI Table of briefing versions with Publish, Download PDF/HTML, Copy Share Link actions |

### RR Pages (`src/pages/rapid/`)

| Page | Route | Description |
|------|-------|-------------|
| `ProtocolEditorPage` | study phase 0 | RR protocol editor |
| `SearchConfigPage` | study phase 1 | Search restriction configuration |
| `QAConfigPage` | study phase 2 | Quality appraisal mode and item configuration |
| `StakeholderPage` | study phase 3 | Practitioner stakeholder management |
| `NarrativeSynthesisPage` | study phase 5 | Narrative synthesis editor with AI draft and finalize CTA |
| `EvidenceBriefingPage` | study phase 6 | Evidence Briefing generation, versioning, and export |
| `PublicBriefingPage` | `/public/briefings/:token` | Unauthenticated briefing view via share token |

### RR Hooks (`src/hooks/rapid/`)

| Hook file | Exported hooks |
|-----------|---------------|
| `useRRProtocol.ts` | `useRRProtocol`, `useUpdateRRProtocol` |
| `useSearchConfig.ts` | `useSearchConfig`, `useUpdateSearchConfig` |
| `useQAConfig.ts` | `useQAConfig`, `useUpdateQAConfig` |
| `useStakeholders.ts` | `useStakeholders`, `useCreateStakeholder`, `useUpdateStakeholder`, `useDeleteStakeholder` |
| `useNarrativeSynthesis.ts` | `useNarrativeSections`, `useUpdateSection`, `useRequestAIDraft`, `useCompleteSynthesis` |
| `useBriefingVersions.ts` | `useBriefings`, `useGenerateBriefing`, `usePublishBriefing`, `useCreateShareToken`, `useRevokeShareToken` |

### RR Services (`src/services/rapid/`)

| Service | Description |
|---------|-------------|
| `protocolApi.ts` | RR protocol read/update endpoints |
| `searchConfigApi.ts` | Search config read/update endpoints |
| `qaConfigApi.ts` | QA config read/update endpoints |
| `stakeholdersApi.ts` | Stakeholder CRUD endpoints |
| `synthesisApi.ts` | Narrative synthesis sections; AI draft job; finalize; `ApiError` class |
| `briefingApi.ts` | Briefing version CRUD; publish; binary PDF export; share token management |

## SLR Workflow Components (007-slr-workflow)

New components, hooks, and services supporting the full Systematic Literature Review workflow:

### SLR Components (`src/components/slr/`)

| Component | Description |
|-----------|-------------|
| `ProtocolForm` | react-hook-form + Zod form for PICO/S protocol fields; `useWatch` on all fields; saves via `useUpdateProtocol` mutation |
| `ProtocolReviewReport` | Renders AI-generated per-section strengths/weaknesses/recommendations from `ProtocolReviewReport` |
| `QualityChecklistEditor` | Editable MUI DataGrid for configuring quality checklist items (binary/numeric scoring, weights) |
| `QualityScoreForm` | Per-reviewer score submission form; conditional numeric input vs checkbox based on scoring method |
| `InterRaterPanel` | Displays Cohen's κ score with interpretation band (poor/fair/moderate/good/excellent) |
| `DiscussionFlowPanel` | Step-by-step discussion resolution panel for resolving inter-rater disagreements |
| `SynthesisConfigForm` | Synthesis approach selector (meta-analysis / descriptive / qualitative) with parameter fields |
| `ForestPlotViewer` | Renders Forest plot SVG returned by meta-analysis synthesis with download action |
| `FunnelPlotViewer` | Renders Funnel plot SVG for publication bias visualisation |
| `GreyLiteraturePanel` | CRUD panel for non-database literature sources (dissertation, report, preprint, conference, website) |

### SLR Pages (`src/pages/slr/`)

| Page | Route | Description |
|------|-------|-------------|
| `ProtocolEditorPage` | `/slr/:studyId/protocol` | Full-page protocol editor with AI review trigger |
| `QualityAssessmentPage` | `/slr/:studyId/quality` | Checklist editor + per-reviewer score forms |
| `SynthesisPage` | `/slr/:studyId/synthesis` | Synthesis config, job trigger, Forest/Funnel plot display |
| `GreyLiteraturePage` | `/slr/:studyId/grey-literature` | Grey literature source management |
| `ReportPage` | `/slr/:studyId/report` | Rendered Markdown SLR report with download |

### SLR Hooks (`src/hooks/slr/`)

| Hook file | Exported hooks |
|-----------|---------------|
| `useProtocol.ts` | `useProtocol`, `useCreateProtocol`, `useUpdateProtocol`, `useTriggerProtocolReview` |
| `useQualityAssessment.ts` | `useQualityChecklist`, `useCreateChecklist`, `useUpdateChecklist`, `useSubmitScore` |
| `useInterRater.ts` | `useInterRaterStats`, `useKappaScore` |
| `useSynthesis.ts` | `useSynthesisResult`, `useTriggerSynthesis` |
| `useGreyLiterature.ts` | `useGreyLiteratureSources`, `useAddGreyLiteratureSource`, `useDeleteGreyLiteratureSource` |

### SLR Services (`src/services/slr/`)

| Service | Description |
|---------|-------------|
| `protocolApi.ts` | CRUD + review-trigger endpoints for `ReviewProtocol` |
| `qualityApi.ts` | Checklist CRUD and score submission endpoints |
| `interRaterApi.ts` | Cohen's κ computation endpoint |
| `synthesisApi.ts` | Synthesis trigger and result fetch |
| `greyLiteratureApi.ts` | Grey literature source CRUD |
| `reportApi.ts` | Structured Markdown report fetch |

## Project Structure

```
frontend/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── stryker.config.json
├── .eslintrc.cjs
├── .prettierrc
├── src/
│   ├── main.tsx              # Application entry point
│   ├── App.tsx               # Root component and router setup
│   ├── components/           # Reusable UI components
│   │   ├── admin/
│   │   │   ├── providers/    # ProviderList, ProviderForm
│   │   │   ├── models/       # ModelList
│   │   │   └── agents/       # AgentList, AgentWizard, AgentForm, SystemMessageEditor
│   │   └── slr/              # SLR workflow components (007-slr-workflow)
│   ├── pages/                # Page-level route components
│   │   └── slr/              # SLR page-level routes (007-slr-workflow)
│   ├── hooks/                # Shared custom hooks (use* pattern)
│   │   └── slr/              # SLR-specific hooks (007-slr-workflow)
│   ├── services/             # API client and TanStack Query hooks
│   │   ├── providersApi.ts   # Provider + model TanStack Query hooks
│   │   ├── agentsApi.ts      # Agent TanStack Query hooks
│   │   └── slr/              # SLR API services (007-slr-workflow)
│   ├── types/
│   │   ├── provider.ts       # Zod schemas + inferred types for Provider/AvailableModel
│   │   └── agent.ts          # Zod schemas + inferred types for Agent
│   └── App.test.tsx          # Root component tests
└── tests/                    # Additional test suites
```

## Code Conventions

- All components **must** be functional; class components are forbidden.
- All component props **must** be typed with a named `interface`.
- Components **must** not exceed ~100 JSX lines; decompose larger ones.
- `useWatch` **must** be used for reactive form field subscriptions (not `watch()`).
- `useEffect` that acquires external resources **must** return a cleanup function.
- More than three related `useState` calls → refactor to `useReducer`.
- No `any`, `enum`, or non-null assertion (`!`) without an inline justification comment.
- All exported functions, classes, and methods **must** have JSDoc comments.

See the [project constitution](../.specify/memory/constitution.md) for the full set of rules.
