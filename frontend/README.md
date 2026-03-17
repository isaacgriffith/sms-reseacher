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

`AgentWizard` is a 5-step MUI `Stepper` (task type → model → role/persona → SVG → system
message review) with state managed via `useReducer`. `SystemMessageEditor` is a
`React.memo` component that highlights `{{ variable }}` template placeholders.

All API responses are parsed through Zod schemas before being returned from hooks.

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
│   │   └── admin/
│   │       ├── providers/    # ProviderList, ProviderForm
│   │       ├── models/       # ModelList
│   │       └── agents/       # AgentList, AgentWizard, AgentForm, SystemMessageEditor
│   ├── pages/                # Page-level route components
│   ├── hooks/                # Shared custom hooks (use* pattern)
│   ├── services/             # API client and TanStack Query hooks
│   │   ├── providersApi.ts   # Provider + model TanStack Query hooks
│   │   └── agentsApi.ts      # Agent TanStack Query hooks
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
