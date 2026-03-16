# Changelog — sms-frontend

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
