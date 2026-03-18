# Changelog — sms-frontend

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — feature/006-database-search-and-retrieval

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

## [Unreleased] — feature/005-models-and-agents

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

## [Unreleased] — feature/004-frontend-improvements

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

## [Unreleased] — feature/003-project-setup-improvements

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
