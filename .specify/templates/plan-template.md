# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify the following gates before proceeding to implementation planning. Record any violations
in the Complexity Tracking table below with justification.

| Gate | Status | Notes |
|------|--------|-------|
| SOLID — no SRP violations in target modules | | |
| SOLID — extension points exist (OCP) where variation expected | | |
| Structural — no DRY violations (duplication) | | |
| Structural — no YAGNI violations (speculative generality) | | |
| Code clarity — no long methods (>20 lines) in touched code | | |
| Code clarity — no switch/if-chain smells in touched code | | |
| Code clarity — no common code smells identified | | |
| Refactoring — pre-implementation review completed | | |
| Refactoring — any found refactors added to task list with tests | | |
| GRASP/patterns — responsibility assignments reviewed | | |
| Test coverage — existing tests pass; refactor tests written first | | |
| Toolchain (VII) — no unapproved deps or tool substitutions introduced | | |
| Toolchain (VII) — FastAPI/SQLAlchemy 2.x/ARQ/LiteLLM patterns followed | | |
| Observability (VIII) — new models have audit fields + structlog used | | |
| Observability (VIII) — config via Pydantic BaseSettings + lru_cache | | |
| Infrastructure (VIII) — Docker services have healthchecks if added | | |
| Language (IX) — React components functional, props typed, ≤100 JSX lines | | |
| Language (IX) — Hooks called at top level only (Rules of Hooks); no inline refs in deps | | |
| Language (IX) — No React state mutation; no array-index keys in lists | | |
| Language (IX) — >3 related useState → useReducer; useCallback only when justified | | |
| Language (IX) — useEffect returns cleanup for all resource-acquiring effects | | |
| Language (IX) — React.memo applied deliberately; useImperativeHandle used for imperative APIs | | |
| Language (IX) — useWatch used (not watch) for reactive form field subscriptions | | |
| Language (IX) — Vite env vars use VITE_ prefix + import.meta.env | | |
| Language (IX) — Python: no plain dict for domain data; pathlib used | | |
| Language (IX) — Python: no mutable defaults; specific exception handling | | |
| Language (IX) — TypeScript: no any/enum/non-null(!) without justification | | |
| Language (IX) — TypeScript: unknown + Zod at all external boundaries | | |

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill if Constitution Check has violations that must be justified, OR if code smells /
> refactoring opportunities were identified during pre-implementation review.**

| Item | Type | Why Accepted / Resolution |
|------|------|--------------------------|
| [e.g., 4th project] | Architecture | [why 3 packages insufficient] |
| [e.g., long method in X] | Code smell | Refactor task TXX added to plan |
| [e.g., if-chain in Y] | Anti-pattern | Strategy pattern task TXX added to plan |
