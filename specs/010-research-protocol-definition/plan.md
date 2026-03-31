# Implementation Plan: Research Protocol Definition

**Branch**: `010-research-protocol-definition` | **Date**: 2026-03-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-research-protocol-definition/spec.md`

## Summary

Replace the existing hardcoded phase-gate workflow with a flexible, graph-based research protocol system. Researchers can define protocols as directed acyclic graphs (DAGs) of typed task nodes connected by information-flow edges — authored through a dual visual/YAML editor — and assign them to studies for runtime execution. Quality gates on task nodes gate downstream activation; a point-and-click condition builder supports optional branching edges. Default protocol templates are provided for all four study types. Existing SMS phase-gate conditions are preserved as quality gates in the default SMS template; all existing studies are migrated to point to the appropriate default template via the Alembic migration.

---

## Technical Context

**Language/Version**: Python 3.14 (backend, db); TypeScript 5.4 / Node 20 LTS (frontend)
**Primary Dependencies**: FastAPI + Pydantic v2, SQLAlchemy 2.0+ async, Alembic, D3.js (already approved), ARQ, React 18, MUI v5, TanStack Query v5, react-hook-form + Zod. No new dependencies required.
**Storage**: PostgreSQL 16 (production); SQLite + aiosqlite (tests); Alembic migration `0018_research_protocol_definition`
**Testing**: pytest + pytest-cov (backend/db), vitest + @testing-library/react (frontend), Playwright (e2e)
**Target Platform**: Linux server (backend), browser (frontend)
**Project Type**: Web application (FastAPI backend + React frontend)
**Performance Goals**: Protocol save/load ≤ 200ms; execution state update (task complete + gate eval + downstream activation) ≤ 500ms; D3 graph render for ≤ 20 nodes ≤ 100ms
**Constraints**: 85% test coverage; mypy strict; ruff clean; no new npm/Python dependencies beyond existing approved stack
**Scale/Scope**: ≤ 20 nodes per protocol graph (typical); 4 default templates; researcher's protocol library (dozens of protocols per user)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| SOLID — no SRP violations in target modules | Pass | Each new service has a single responsibility: `ProtocolService` (CRUD + validation), `ProtocolExecutorService` (runtime execution), `ProtocolYamlService` (import/export). API routers delegate to services only. |
| SOLID — extension points exist (OCP) where variation expected | Pass | `QualityGateEvaluator` uses a strategy dispatch dict keyed on `QualityGateType`; adding a new gate type requires only a new strategy function, not editing existing logic. |
| Structural — no DRY violations (duplication) | Pass | Graph validation logic lives exclusively in `ProtocolService.validate_graph()`. Execution state activation logic lives exclusively in `ProtocolExecutorService.activate_eligible_tasks()`. |
| Structural — no YAGNI violations (speculative generality) | Pass | Compound edge conditions (AND/OR), compound assignee logic, and in-platform version history are all explicitly out of scope per spec + clarifications. |
| Code clarity — no long methods (>20 lines) in touched code | Pass | Topological sort, cycle detection, and gate evaluation are each isolated into named private methods ≤ 20 lines. DFS cycle detection is decomposed into `_dfs_visit()`. |
| Code clarity — no switch/if-chain smells in touched code | Pass | Gate type dispatch uses a dict (`_GATE_EVALUATORS: dict[QualityGateType, GateEvaluator]`); task type allowlist uses a dict (`VALID_TASK_TYPES_BY_STUDY_TYPE`). No if-chains. |
| Code clarity — no common code smells identified | Pass | No Feature Envy, Data Clumps, or God Objects identified in the planned design. |
| Refactoring — pre-implementation review completed | Pass | Existing `phase_gate.py` and `slr_phase_gate.py` reviewed; no refactoring required as they remain unchanged during this feature (additive integration approach). |
| Refactoring — any found refactors added to task list with tests | N/A | No refactors identified. |
| GRASP/patterns — responsibility assignments reviewed | Pass | Information Expert: `ProtocolService` knows graph shape; `ProtocolExecutorService` knows execution rules. Creator: `ProtocolService.copy_from_template()` creates new protocols. Protected Variations: `QualityGateEvaluator` isolates gate logic from executor. |
| Test coverage — existing tests pass; refactor tests written first | Pass | No existing tests modified; new tests written alongside new code per task plan. |
| Toolchain (VII) — no unapproved deps or tool substitutions introduced | Pass | D3.js already approved (feature 002). No new Python or npm packages required. YAML serialisation uses PyYAML (already in project via transitive dep) or standard-library alternatives. |
| Toolchain (VII) — FastAPI/SQLAlchemy 2.x/ARQ/LiteLLM patterns followed | Pass | All ORM models use `Mapped[]` + `mapped_column()`. All API handlers use `async def` + `Depends()`. No ARQ jobs needed for this feature (gate evaluation is synchronous). |
| Observability (VIII) — new models have audit fields + structlog used | Pass | All new ORM models include `created_at` / `updated_at`. `ResearchProtocol` and `TaskExecutionState` include `version_id`. All services use `structlog.get_logger(__name__)`. |
| Observability (VIII) — config via Pydantic BaseSettings + lru_cache | Pass | No new env vars required. Existing `get_settings()` used. |
| Infrastructure (VIII) — Docker services have healthchecks if added | N/A | No new Docker services. |
| Language (IX) — React components functional, props typed, ≤100 JSX lines | Pass | All new components will be functional with typed props. `ProtocolGraph.tsx` (D3 integration) will use `useEffect` for D3 mount + a `useRef` for the SVG element; JSX stays ≤ 100 lines. |
| Language (IX) — Hooks called at top level only (Rules of Hooks); no inline refs in deps | Pass | D3 setup lives in `useEffect`. `useRef` for SVG container. |
| Language (IX) — No React state mutation; no array-index keys in lists | Pass | Protocol node/edge lists keyed by `task_id` (stable string). |
| Language (IX) — >3 related useState → useReducer; useCallback only when justified | Pass | Graph editor state (nodes, edges, selected node) → `useReducer(graphReducer, initialState)`. |
| Language (IX) — useEffect returns cleanup for all resource-acquiring effects | Pass | D3 force simulation stopped in cleanup: `return () => simulation.stop()`. |
| Language (IX) — React.memo applied deliberately; useImperativeHandle used for imperative APIs | Pass | `ProtocolNodePanel` memoised (re-renders only on selected node change). |
| Language (IX) — useWatch used (not watch) for reactive form field subscriptions | Pass | Gate config form uses `useWatch` for dynamic field rendering based on `gate_type`. |
| Language (IX) — Vite env vars use VITE_ prefix + import.meta.env | Pass | No new env vars exposed to frontend. |
| Language (IX) — Python: no plain dict for domain data; pathlib used | Pass | YAML import/export uses Pydantic models (`ProtocolExportSchema`), not plain dicts. |
| Language (IX) — Python: no mutable defaults; specific exception handling | Pass | All service functions raise specific `HTTPException` / custom exceptions. No mutable defaults. |
| Language (IX) — TypeScript: no any/enum/non-null(!) without justification | Pass | D3 types from `@types/d3` (already present). All custom types explicitly defined. |
| Language (IX) — TypeScript: unknown + Zod at all external boundaries | Pass | YAML import response and protocol API responses validated with Zod schemas in the service layer. |
| Code clarity — all source files have a module-level doc comment | Pass | Every new `.py` and `.ts/.tsx` file will have a module-level docstring / JSDoc block. |
| Code clarity — all functions/methods/classes have doc comments | Pass | Google-style docstrings on all Python; JSDoc on all exported TypeScript. |
| Pre-existing issues — all pre-existing test failures, linting errors, and type errors in touched files are resolved before feature completion | Pass | No existing files are modified except `backend/src/backend/api/v1/studies/__init__.py` (add protocol assignment router). Pre-existing state of that file will be reviewed and any issues resolved before feature completion. |
| Feature completion docs — CLAUDE.md, root README.md, affected subproject README.md(s), root CHANGELOG.md, affected subproject CHANGELOG.md(s) update tasks in task list | Pass | Doc update tasks included in task plan (TDOC1–TDOC5). |

---

## Project Structure

### Documentation (this feature)

```text
specs/010-research-protocol-definition/
├── plan.md              # This file
├── research.md          # Phase 0 — all decisions resolved
├── data-model.md        # Phase 1 — ORM models + migration schema
├── quickstart.md        # Phase 1 — dev setup + key file index
├── contracts/
│   └── api.md           # Phase 1 — REST API contracts
└── tasks.md             # Phase 2 output (/speckit.tasks — not yet created)
```

### Source Code (repository root)

```text
# New files — db subproject
db/src/db/models/protocols.py          # All new ORM models (ResearchProtocol, ProtocolNode,
                                        # ProtocolEdge, QualityGate, TaskExecutionState, etc.)
db/alembic/versions/0018_research_protocol_definition.py  # Migration + default template seeding

# New files — backend subproject
backend/src/backend/services/protocol_service.py      # CRUD + graph validation
backend/src/backend/services/protocol_executor.py     # Runtime task activation + gate evaluation
backend/src/backend/services/protocol_yaml.py         # YAML export / import

backend/src/backend/api/v1/protocols/
├── __init__.py           # Router registration
├── schemas.py            # Pydantic request/response models
├── library.py            # GET/POST/PUT/DELETE /protocols, export, import
└── assignment.py         # GET/PUT/DELETE /studies/{id}/protocol-assignment

backend/src/backend/api/v1/studies/
└── execution_state.py    # GET/POST /studies/{id}/execution-state/{task_id}/...

# Modified files — backend subproject
backend/src/backend/api/v1/studies/__init__.py        # Register new protocol + execution routers
backend/src/backend/main.py                           # Include new router prefix

# New files — frontend subproject
frontend/src/services/protocols/
├── protocolsApi.ts              # API client (all protocol endpoints)
└── protocolsApi.test.ts

frontend/src/hooks/protocols/
├── useProtocol.ts               # TanStack Query hooks (list, detail, mutations)
├── useExecutionState.ts         # Polling hook (refetchInterval for active studies)
└── useProtocolEditor.ts         # useReducer-based editor state (graph mutations)

frontend/src/components/protocols/
├── ProtocolGraph.tsx            # D3.js visual graph editor
├── ProtocolGraph.test.tsx
├── ProtocolTextEditor.tsx       # YAML text editor (syntax highlight via highlight.js or similar)
├── ProtocolNodePanel.tsx        # Node detail / edit panel
├── ProtocolNodePanel.test.tsx
├── QualityGateEditor.tsx        # Gate type selector + config form
├── EdgeConditionBuilder.tsx     # Point-and-click condition builder
├── ExecutionStateView.tsx       # Runtime task status board (kanban-style)
├── ExecutionStateView.test.tsx
└── ProtocolList.tsx             # Protocol library list component

frontend/src/pages/protocols/
├── ProtocolLibraryPage.tsx      # /protocols — list + create + delete
└── ProtocolEditorPage.tsx       # /protocols/:id — dual editor (visual + YAML)

# New test files — backend
backend/tests/api/v1/
├── test_protocols_library.py    # Protocol library CRUD + export/import
├── test_protocols_assignment.py # Study protocol assignment endpoints
└── test_protocols_execution.py  # Execution state endpoints

backend/tests/services/
├── test_protocol_service.py     # Graph validation (cycle, dangling, task type allowlist)
├── test_protocol_executor.py    # Gate evaluation + task activation
└── test_protocol_yaml.py        # YAML round-trip tests

# New test files — db
db/tests/test_protocol_models.py  # ORM model construction + relationships

# New test files — frontend
frontend/src/services/protocols/protocolsApi.test.ts
frontend/src/hooks/protocols/useProtocol.test.ts
frontend/src/components/protocols/*.test.tsx
frontend/e2e/protocols.spec.ts        # Playwright e2e: view default, copy, edit, assign, execute
```

---

## Complexity Tracking

| Item | Type | Why Accepted / Resolution |
|------|------|--------------------------|
| Dual visual + YAML editor sync | Architecture | Client-side shared state (useReducer) keeps both views in sync without server round-trips. Complexity bounded to `useProtocolEditor.ts` reducer — clearly scoped. |
| Migration seeding default templates | Migration | Default protocols are seeded inside the Alembic migration using raw INSERT statements. Schema data (node/edge definitions) is version-controlled as migration data, not application code. Well-established pattern for reference data. |
| Topological cycle detection | Algorithm | Standard DFS on adjacency list in `ProtocolService._detect_cycle()`. Decomposed into `_dfs_visit(node, visited, in_stack)`. Complexity O(V+E) — trivial for ≤ 20 nodes. |
| D3 + React integration | Frontend | D3 DOM manipulation lives entirely in a `useEffect` with a cleanup. React renders the SVG container only; D3 owns all child elements. Pattern is well-established; scoped to `ProtocolGraph.tsx`. |
