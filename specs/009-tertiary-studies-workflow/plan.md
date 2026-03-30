# Implementation Plan: Tertiary Studies Workflow

**Branch**: `009-tertiary-studies-workflow` | **Date**: 2026-03-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-tertiary-studies-workflow/spec.md`

## Summary

Extend the research platform with a Tertiary Study workflow — a specialised SLR that reviews secondary studies (SLRs, SMSs, Rapid Reviews) rather than empirical papers. The feature reuses the existing SLR infrastructure (phase gate dispatch, quality assessment checklists, synthesis strategies, ARQ job patterns) and adds: a `TertiaryStudyProtocol` ORM, a `SecondaryStudySeedImport` mechanism that promotes papers from existing platform studies, a `TertiaryDataExtraction` model with nine secondary-study-specific fields, a `TertiaryReportService` with a landscape-of-secondary-studies section, and dedicated API routes under `/api/v1/tertiary/`. Two new synthesis strategies (narrative, thematic) extend the existing Strategy pattern. Alembic migration `0017_tertiary_studies_workflow` creates three new tables and adds one column to `candidate_paper`.

## Technical Context

**Language/Version**: Python 3.14 (backend, db, agents); TypeScript 5.4 / Node 20 LTS (frontend)
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0+ async, Alembic, ARQ, LiteLLM, React 18, MUI v5, TanStack Query v5, react-hook-form + Zod
**Storage**: PostgreSQL 16 (production); SQLite + aiosqlite (tests)
**Testing**: pytest + pytest-cov (≥85% line coverage); vitest + @vitest/coverage-v8 (≥85%); Playwright (e2e)
**Target Platform**: Linux server (Docker Compose) + browser (Vite SPA)
**Project Type**: Web service (FastAPI backend + React SPA frontend)
**Performance Goals**: Phase gate evaluation <200 ms p95; seed import of 500 papers <5 s; report generation <10 s
**Constraints**: Optimistic locking on all mutable ORM models; full `downgrade()` path in migration; no breaking changes to existing SLR or Rapid Review endpoints
**Scale/Scope**: Same scale as SLR workflow; tertiary studies are expected to have 20–200 included secondary studies

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| SOLID — no SRP violations in target modules | PASS | Each new service has one responsibility; protocol, extraction, report, phase gate are separate modules |
| SOLID — extension points exist (OCP) where variation expected | PASS | Phase gate dispatch dict; synthesis strategy classes; new strategies added without editing existing ones |
| Structural — no DRY violations (duplication) | PASS | Checklist, synthesis, QA score, search models reused; no copy-paste |
| Structural — no YAGNI violations (speculative generality) | PASS | No speculative abstractions; only what spec requires |
| Code clarity — no long methods (>20 lines) in touched code | PASS | New services follow existing pattern of short, composable helpers |
| Code clarity — no switch/if-chain smells in touched code | PASS | Phase gate uses dispatch dict; synthesis uses Strategy pattern |
| Code clarity — no common code smells identified | PASS | Pre-implementation review showed clean extension points |
| Refactoring — pre-implementation review completed | PASS | Reviewed `_PHASE_GATE_DISPATCH`, `synthesis_strategies.py`, `SLRReportService` |
| Refactoring — any found refactors added to task list with tests | PASS | No blocking refactors found; minor shared synthesis base class opportunity noted but deferred (YAGNI) |
| GRASP/patterns — responsibility assignments reviewed | PASS | TertiaryReportService, TertiaryExtractionService, tertiary_phase_gate follow Information Expert |
| Test coverage — existing tests pass; refactor tests written first | PASS | Existing SLR/RR tests must remain green; new tests written alongside new code |
| Toolchain (VII) — no unapproved deps or tool substitutions introduced | PASS | No new Python or npm packages required |
| Toolchain (VII) — FastAPI/SQLAlchemy 2.x/ARQ/LiteLLM patterns followed | PASS | All patterns consistent with 007/008 feature implementations |
| Observability (VIII) — new models have audit fields + structlog used | PASS | `created_at`, `updated_at`, `version_id` on all new models; structlog in all services |
| Observability (VIII) — config via Pydantic BaseSettings + lru_cache | PASS | No new env vars; existing settings module used |
| Infrastructure (VIII) — Docker services have healthchecks if added | PASS | No new Docker services |
| Language (IX) — React components functional, props typed, ≤100 JSX lines | PASS | All new components follow existing SLR component patterns |
| Language (IX) — Hooks called at top level only (Rules of Hooks); no inline refs in deps | PASS | Enforced by existing ESLint config |
| Language (IX) — No React state mutation; no array-index keys in lists | PASS | Using entity `id` fields as keys |
| Language (IX) — >3 related useState → useReducer; useCallback only when justified | PASS | TertiaryProtocolForm uses react-hook-form; no raw useState chains |
| Language (IX) — useEffect returns cleanup for all resource-acquiring effects | PASS | TanStack Query used for data fetching; minimal useEffect |
| Language (IX) — React.memo applied deliberately; useImperativeHandle used for imperative APIs | PASS | No premature memoisation |
| Language (IX) — useWatch used (not watch) for reactive form field subscriptions | PASS | Enforced by existing team convention |
| Language (IX) — Vite env vars use VITE_ prefix + import.meta.env | PASS | No new env vars on frontend |
| Language (IX) — Python: no plain dict for domain data; pathlib used | PASS | Pydantic models for all domain data |
| Language (IX) — Python: no mutable defaults; specific exception handling | PASS | Follows existing patterns |
| Language (IX) — TypeScript: no any/enum/non-null(!) without justification | PASS | Zod schemas at all API boundaries |
| Language (IX) — TypeScript: unknown + Zod at all external boundaries | PASS | All API responses validated via Zod schemas |
| Code clarity — all source files have a module-level doc comment (Python module docstring / TS file-level JSDoc) | PASS | Required for all new files; enforced via ruff D rules |
| Code clarity — all functions/methods/classes have doc comments (Google-style / JSDoc); CLI handlers: brief description only, no Args/Returns | PASS | All new Python code uses Google-style docstrings; all exported TS uses JSDoc |
| Pre-existing issues — all pre-existing test failures, linting errors, and type errors in touched files are resolved before feature completion | PASS | Verified: existing tests pass on `main` |
| Feature completion docs — CLAUDE.md, root README.md, affected subproject README.md(s), root CHANGELOG.md, affected subproject CHANGELOG.md(s) update tasks in task list | PASS | TDOC tasks included in task list |

## Project Structure

### Documentation (this feature)

```text
specs/009-tertiary-studies-workflow/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── api.md           # REST API contracts
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code

```text
db/
├── src/db/models/
│   └── tertiary.py                         # TertiaryStudyProtocol, SecondaryStudySeedImport, TertiaryDataExtraction
└── alembic/versions/
    └── 0017_tertiary_studies_workflow.py   # Migration: 3 new tables + 1 column

backend/
├── src/backend/
│   ├── api/v1/tertiary/
│   │   ├── __init__.py                     # Router registration
│   │   ├── protocol.py                     # GET/PUT /tertiary/studies/{id}/protocol, POST .../validate
│   │   ├── seed_imports.py                 # GET/POST /tertiary/studies/{id}/seed-imports
│   │   ├── extractions.py                  # GET/PUT /tertiary/studies/{id}/extractions/*, POST .../ai-assist
│   │   └── report.py                       # GET /tertiary/studies/{id}/report
│   ├── services/
│   │   ├── tertiary_phase_gate.py          # get_tertiary_unlocked_phases()
│   │   ├── tertiary_report_service.py      # TertiaryReportService
│   │   └── tertiary_extraction_service.py  # TertiaryExtractionService (seed import + AI assist)
│   └── jobs/
│       └── tertiary_extraction_job.py      # ARQ job: AI-assisted extraction pre-population
└── tests/
    ├── test_tertiary_protocol.py
    ├── test_tertiary_seed_import.py
    ├── test_tertiary_extraction.py
    ├── test_tertiary_phase_gate.py
    └── test_tertiary_report.py

agents/
└── src/agents/
    └── templates/
        └── tertiary_protocol_review.j2    # Jinja2 prompt template for tertiary protocol review

frontend/
├── src/
│   ├── components/tertiary/
│   │   ├── TertiaryProtocolForm.tsx       # Protocol editor
│   │   ├── SeedImportPanel.tsx            # Seed import UI
│   │   ├── TertiaryExtractionForm.tsx     # Secondary-study extraction fields
│   │   └── LandscapeSummarySection.tsx    # Report landscape section viewer
│   └── pages/
│       ├── TertiaryStudyPage.tsx          # Study dashboard router
│       └── TertiaryReportPage.tsx         # Report view + export
└── tests/
    ├── TertiaryProtocolForm.test.tsx
    ├── SeedImportPanel.test.tsx
    └── TertiaryExtractionForm.test.tsx
```

**Structure Decision**: Web application (Option 2). Tertiary-specific code lives under dedicated subdirectories mirroring the existing `slr/` and `rapid/` patterns. Shared infrastructure (QA, synthesis, search) is accessed via existing endpoints without modification.

**Phase 3 Screening**: `TertiaryStudyPage` Phase 3 panel reuses the existing `PaperQueue` component (`components/phase2/PaperQueue.tsx`) directly — no Tertiary-specific screening component is needed because `PaperQueue` already handles accept/reject/duplicate decisions for any study type via `studyId`.

## Complexity Tracking

> No Constitution Check violations found. No blocking refactors identified.

| Item | Type | Why Accepted / Resolution |
|------|------|--------------------------|
| Two new synthesis strategies added to existing module | Extension | OCP satisfied — Strategy pattern extended, not modified |
| `candidate_paper` gains `source_seed_import_id` column | Additive migration | Nullable FK, backward-compatible; no existing queries affected |
