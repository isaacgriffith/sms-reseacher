# Implementation Plan: Project Setup & Quality Improvements

**Branch**: `003-project-setup-improvements` | **Date**: 2026-03-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-project-setup-improvements/spec.md`

## Summary

Replace `mutmut` with `cosmic-ray` for Python mutation testing; move all mutation jobs
(Python and frontend Stryker) from per-PR CI to manually-triggered `workflow_dispatch`
workflows; add Cobertura/JSON-summary coverage PR comments to the existing CI pipeline;
enforce `reason=` on all pytest skip/xfail markers via a root conftest.py hook; add
Playwright end-to-end tests for each service's primary user journeys; audit and close any
coverage gaps below 85% in all five Python packages; and update `CLAUDE.md`, all
`README.md`s, and all `CHANGELOG.md`s to reflect the changes.

## Technical Context

**Language/Version**: Python 3.14 (backend, agents, db, agent-eval, researcher-mcp);
TypeScript 5.4 / Node 20 LTS (frontend)
**Primary Dependencies**:
- New: `cosmic-ray` (Python mutation); `@playwright/test` (e2e); `@vitest/coverage-v8`
  (vitest coverage provider); `MishaKav/pytest-coverage-comment` (GHA action);
  `davelosert/vitest-coverage-report-action` (GHA action)
- Existing: `pytest-cov`, `vitest`, `@stryker-mutator/core`,
  `@stryker-mutator/vitest-runner`, `ruff`, `mypy`, `eslint`, `prettier`
**Storage**: N/A (no new database entities; SQLite used by e2e test stack)
**Testing**: pytest + pytest-cov; vitest + @vitest/coverage-v8; Playwright; cosmic-ray; Stryker
**Target Platform**: GitHub Actions CI (ubuntu-latest) + local developer machine
**Project Type**: Tooling and quality improvement — no new product features
**Performance Goals**: N/A (no latency/throughput requirements)
**Constraints**:
- `cosmic-ray` must be compatible with Python 3.14 and `asyncio_mode = "auto"` pytest
- Playwright e2e tests must be runnable locally with `docker compose up` providing the stack
- Mutation workflows must NOT run on every PR (workflow_dispatch / workflow_call only)
**Scale/Scope**: 5 Python packages + 1 TypeScript/React frontend; ~25 GitHub Actions jobs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| SOLID — no SRP violations in target modules | ✅ Pass | Only config files, CI YAML, and test additions; no new OOP units |
| SOLID — extension points exist (OCP) where variation expected | ✅ Pass | N/A — tooling config has no variation points |
| Structural — no DRY violations (duplication) | ⚠ Justified | `cosmic-ray.toml` repeated per package; cosmic-ray has no include/inheritance mechanism. Accepted — each file differs only in `module-path` |
| Structural — no YAGNI violations (speculative generality) | ✅ Pass | All additions are directly required by the spec |
| Code clarity — no long methods (>20 lines) in touched code | ✅ Pass | conftest.py hook ≤15 lines |
| Code clarity — no switch/if-chain smells in touched code | ✅ Pass | No dispatch logic |
| Code clarity — no common code smells identified | ✅ Pass | No production application code modified |
| Refactoring — pre-implementation review completed | ✅ Pass | Existing pyproject.toml and ci.yml reviewed |
| Refactoring — any found refactors added to task list with tests | ✅ Pass | No refactoring needed; mutations tool swap is config-only |
| GRASP/patterns — responsibility assignments reviewed | ✅ Pass | N/A — tooling feature |
| Test coverage — existing tests pass; refactor tests written first | ⚠ Unknown | Current coverage levels unknown; audit task T002 will assess |
| Toolchain (VII) — no unapproved deps or tool substitutions introduced | ✅ Pass | cosmic-ray approved in constitution v1.5.1; Playwright approved v1.6.1; @vitest/coverage-v8 is the vitest-standard coverage provider |
| Toolchain (VII) — FastAPI/SQLAlchemy 2.x/ARQ/LiteLLM patterns followed | ✅ Pass | No backend application code modified |
| Observability (VIII) — new models have audit fields + structlog used | ✅ Pass | No new models |
| Observability (VIII) — config via Pydantic BaseSettings + lru_cache | ✅ Pass | No new config classes |
| Infrastructure (VIII) — Docker services have healthchecks if added | ✅ Pass | No new Docker services; existing healthchecks unchanged |
| Language (IX) — React components functional, props typed, ≤100 JSX lines | ✅ Pass | No React component changes |
| Language (IX) — Hooks called at top level only (Rules of Hooks); no inline refs in deps | ✅ Pass | N/A |
| Language (IX) — No React state mutation; no array-index keys in lists | ✅ Pass | N/A |
| Language (IX) — >3 related useState → useReducer; useCallback only when justified | ✅ Pass | N/A |
| Language (IX) — useEffect returns cleanup for all resource-acquiring effects | ✅ Pass | N/A |
| Language (IX) — React.memo applied deliberately; useImperativeHandle used for imperative APIs | ✅ Pass | N/A |
| Language (IX) — useWatch used (not watch) for reactive form field subscriptions | ✅ Pass | N/A |
| Language (IX) — Vite env vars use VITE_ prefix + import.meta.env | ✅ Pass | N/A |
| Language (IX) — Python: no plain dict for domain data; pathlib used | ✅ Pass | conftest.py uses no domain data |
| Language (IX) — Python: no mutable defaults; specific exception handling | ✅ Pass | conftest.py has no mutable defaults |
| Language (IX) — TypeScript: no any/enum/non-null(!) without justification | ✅ Pass | Playwright tests use typed Page/Locator APIs |
| Language (IX) — TypeScript: unknown + Zod at all external boundaries | ✅ Pass | N/A — e2e tests have no external API parsing |
| Code clarity — all functions/methods/classes have doc comments | ✅ Pass | conftest.py hook and Playwright helpers will have docstrings/JSDoc |
| Feature completion docs (X) — CLAUDE.md, README.md, CHANGELOG.md update tasks in task list | ✅ Pass | TDOC tasks explicitly planned (see tasks.md) |

## Project Structure

### Documentation (this feature)

```text
specs/003-project-setup-improvements/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── quickstart.md        ← Phase 1 output
└── tasks.md             ← /speckit.tasks output (not yet created)
```

*(No data-model.md or contracts/ — this feature adds no new entities or external APIs.)*

### Source Code (repository root)

```text
.github/
└── workflows/
    ├── ci.yml                     # Updated: remove mutation jobs; add coverage PR comments;
    │                              #   add Playwright e2e job; add workflow_call trigger
    ├── mutation-python.yml        # New: workflow_dispatch + workflow_call; cosmic-ray matrix
    └── mutation-frontend.yml      # New: workflow_dispatch + workflow_call; Stryker

conftest.py                        # New: root skip/xfail reason enforcement hook
pyproject.toml                     # Updated: mutmut → cosmic-ray in dev-dependencies

backend/
├── pyproject.toml                 # Updated: [tool.mutmut] → [tool.cosmic-ray]; add cosmic-ray dep
├── cosmic-ray.toml                # New: cosmic-ray configuration for backend
└── tests/                        # Updated: new unit/integration tests to reach 85% coverage

agents/
├── pyproject.toml                 # Updated: [tool.mutmut] → [tool.cosmic-ray]
├── cosmic-ray.toml                # New
└── tests/                        # Updated: additional tests as needed

db/
├── pyproject.toml                 # Updated: [tool.mutmut] → [tool.cosmic-ray]
├── cosmic-ray.toml                # New
└── tests/                        # Updated: additional tests as needed

agent-eval/
├── pyproject.toml                 # Updated: [tool.mutmut] → [tool.cosmic-ray]
├── cosmic-ray.toml                # New
└── tests/                        # Updated: additional tests as needed

researcher-mcp/
├── pyproject.toml                 # Updated: [tool.mutmut] → [tool.cosmic-ray]
├── cosmic-ray.toml                # New
└── tests/                        # Updated: additional tests as needed

frontend/
├── package.json                   # Updated: add @playwright/test, @vitest/coverage-v8
├── vite.config.ts                 # Updated: add vitest coverage config (v8 provider, thresholds)
├── playwright.config.ts           # New: baseURL, webServer (Vite dev server), CI settings
└── e2e/                           # New: Playwright test files for primary user journeys

CLAUDE.md                          # Updated: all new commands (cosmic-ray, playwright, coverage)
README.md                          # Updated: tech stack (already done)
CHANGELOG.md                       # Updated: Unreleased section (already done)
```

**Structure Decision**: This is an existing web application mono-repo. The feature touches all six subprojects (five Python, one TypeScript) and the GitHub Actions CI layer. No new subprojects are created. Mutation test configs are extracted into separate workflow files to satisfy the `workflow_dispatch` requirement (FR-013).

## Complexity Tracking

| Item | Type | Why Accepted / Resolution |
|------|------|--------------------------|
| `cosmic-ray.toml` repeated per package | Config duplication | Accepted — cosmic-ray has no workspace-level config inheritance. Each file is 10 lines and differs only in `module-path` and `test-command`. |
| Mutation workflows run per-PR in existing `ci.yml` | Existing violation | Resolved — mutation jobs extracted to separate `mutation-python.yml` and `mutation-frontend.yml` with `workflow_dispatch` + `workflow_call` only. |
| No Playwright installed in frontend | Missing tool | Resolved — `@playwright/test` added to `devDependencies` and `playwright.config.ts` created in this feature. |
| Coverage levels for 5 Python packages unknown | Risk | Mitigated — T002 (coverage audit) runs first; gap-closing tests written before any other task in Phase 3+. |
| `vitest` coverage not configured | Existing gap | Resolved — `vite.config.ts` updated with `v8` provider and `thresholds: { lines: 85 }`; `@vitest/coverage-v8` added as dev dependency. |
