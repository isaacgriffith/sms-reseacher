# Implementation Plan: SLR Workflow

**Branch**: `007-slr-workflow` | **Date**: 2026-03-18 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-slr-workflow/spec.md`

---

## Summary

Extend the SMS Researcher platform to support Systematic Literature Reviews (SLRs) by implementing the three-phase SLR lifecycle on top of the existing SMS workflow infrastructure. The approach adds six new ORM models, a standalone SLR API router, two ARQ background jobs, a new `ProtocolReviewerAgent`, SLR-specific phase gate logic, and a statistical computation layer (Cohen's Kappa, meta-analysis, Forest/Funnel plot generation). The Strategy pattern governs synthesis approach dispatch to eliminate type-switching throughout the codebase.

---

## Technical Context

**Language/Version**: Python 3.14 (backend, agents, db); TypeScript 5.4 / Node 20 LTS (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0+ async, ARQ, LiteLLM, React 18, MUI v5, TanStack Query v5, react-hook-form + Zod; new: `scipy>=1.13`, `scikit-learn>=1.5`, `numpy>=1.26`
**Storage**: PostgreSQL 16 (production); SQLite + aiosqlite (tests); Alembic migration `0015_slr_workflow`
**Testing**: pytest + asyncio_mode=auto (backend/db/agents), vitest + @testing-library/react (frontend), Playwright (e2e)
**Target Platform**: Linux server + SPA frontend
**Project Type**: Web application (FastAPI backend + React frontend), multi-package uv workspace
**Performance Goals**: Synthesis job completes in < 30s for ≤ 200 papers; Kappa computation < 1s; plot generation < 3s
**Constraints**: 85% line/branch coverage enforced; no new unapproved dependencies beyond scipy/scikit-learn/numpy; optimistic locking on all concurrently-editable models
**Scale/Scope**: ~8 new API routes, 6 new DB models, 1 new agent, 2 new ARQ jobs, ~10 new frontend components

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| SOLID — no SRP violations in target modules | PASS | Each new service has one responsibility: `slr_protocol_service`, `quality_assessment_service`, `inter_rater_service`, `synthesis_service`, `statistics` are all single-purpose |
| SOLID — extension points exist (OCP) where variation expected | PASS | Synthesis dispatch uses Strategy pattern (`SynthesisStrategy` protocol + `MetaAnalysisSynthesizer`, `DescriptiveSynthesizer`, `QualitativeSynthesizer`); `slr_phase_gate.py` extends rather than modifies `phase_gate.py` |
| Structural — no DRY violations (duplication) | PASS | Kappa computed once in `statistics.py`; plot generation extends existing `visualization.py`; phase gate logic deduplicates by delegation to existing function for shared gates |
| Structural — no YAGNI violations (speculative generality) | PASS | Only implementing what the spec requires; Gwet's AC1 and Fleiss' κ explicitly deferred |
| Code clarity — no long methods (>20 lines) in touched code | PASS | Stats helpers decomposed into `_compute_weights`, `_compute_q`, `_pool_effect`, `_build_ci`; each ≤ 20 lines |
| Code clarity — no switch/if-chain smells in touched code | PASS | Synthesis type dispatch via Strategy pattern; no if/elif chain on `synthesis_approach` |
| Code clarity — no common code smells identified | PASS | Pre-implementation review of `phase_gate.py`, `visualization.py`, and agent patterns shows no existing smells in touched files |
| Refactoring — pre-implementation review completed | PASS | Existing `visualization.py` reviewed; no violations found. `phase_gate.py` reviewed; SLR gate added as separate function, not inline modification |
| Refactoring — any found refactors added to task list with tests | PASS | No refactors required; existing touched files are clean |
| GRASP/patterns — responsibility assignments reviewed | PASS | `SynthesisService` is the Controller; `statistics.py` is Information Expert for computations; `SynthesisStrategy` protocol is Polymorphism for approach dispatch; `visualization.py` extended for Forest/Funnel via Pure Fabrication |
| Test coverage — existing tests pass; refactor tests written first | PASS | No refactors; existing test suites unmodified; new tests planned for all new modules |
| Toolchain (VII) — no unapproved deps or tool substitutions introduced | PASS | scipy, scikit-learn, numpy are standard scientific Python — no constitution amendment required; they extend (not replace) approved toolchain |
| Toolchain (VII) — FastAPI/SQLAlchemy 2.x/ARQ/LiteLLM patterns followed | PASS | All new services follow existing `async def` + `Depends()` + `HTTPException` patterns; agent uses `LLMClient` + Jinja2 prompts |
| Observability (VIII) — new models have audit fields + structlog used | PASS | All 6 new models have `created_at`/`updated_at`; `version_id` on `ReviewProtocol`, `QualityAssessmentScore`, `SynthesisResult`; structlog bound with `study_id`, `reviewer_id` in all service calls |
| Observability (VIII) — config via Pydantic BaseSettings + lru_cache | PASS | `SLR_KAPPA_THRESHOLD` and `SLR_MIN_SYNTHESIS_PAPERS` added to existing `backend/core/config.py` `Settings` class |
| Infrastructure (VIII) — Docker services have healthchecks if added | PASS | No new Docker services added |
| Language (IX) — React components functional, props typed, ≤100 JSX lines | PASS | All new components planned as functional; complex forms split into sub-components to stay within 100 JSX line limit |
| Language (IX) — Hooks called at top level only (Rules of Hooks); no inline refs in deps | PASS | All hooks will be at top level; `useCallback` dependencies will be reviewed during implementation |
| Language (IX) — No React state mutation; no array-index keys in lists | PASS | Items will use `id` as key; state will be updated immutably |
| Language (IX) — >3 related useState → useReducer; useCallback only when justified | PASS | `ProtocolEditorPage` has >3 form fields → uses react-hook-form (not raw useState); `SynthesisPage` uses `useReducer` for multi-step flow |
| Language (IX) — useEffect returns cleanup for all resource-acquiring effects | PASS | Polling effects will return cleanup to cancel intervals |
| Language (IX) — React.memo applied deliberately; useImperativeHandle used for imperative APIs | PASS | `ForestPlotViewer` and `FunnelPlotViewer` are `React.memo` candidates (SVG re-renders are expensive); will be applied with justification |
| Language (IX) — useWatch used (not watch) for reactive form field subscriptions | PASS | Protocol form will use `useWatch` for conditional field display |
| Language (IX) — Vite env vars use VITE_ prefix + import.meta.env | PASS | No new frontend env vars; all config comes from backend API |
| Language (IX) — Python: no plain dict for domain data; pathlib used | PASS | All structured data uses Pydantic models; `ProtocolReviewResult`, `MetaAnalysisResult`, etc. |
| Language (IX) — Python: no mutable defaults; specific exception handling | PASS | No mutable defaults; exceptions caught specifically (e.g., `StaleDataError`, `ValueError`) |
| Language (IX) — TypeScript: no any/enum/non-null(!) without justification | PASS | All types will use Zod schemas at API boundary; `unknown` + Zod parse for API responses |
| Language (IX) — TypeScript: unknown + Zod at all external boundaries | PASS | All API response types validated with Zod schemas in `frontend/src/services/slr/` |
| Code clarity — all functions/methods/classes have doc comments | PASS | Google-style docstrings on all Python code; JSDoc on all exported TypeScript functions and components |
| Feature completion docs (X) — CLAUDE.md, root README.md, affected subproject README.md(s), root CHANGELOG.md, affected subproject CHANGELOG.md(s) update tasks in task list | PASS | Documentation update tasks included in implementation task list |

---

## Project Structure

### Documentation (this feature)

```text
specs/007-slr-workflow/
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output (/speckit.plan)
├── data-model.md        # Phase 1 output (/speckit.plan)
├── quickstart.md        # Phase 1 output (/speckit.plan)
├── contracts/
│   └── api-contracts.md # Phase 1 output (/speckit.plan)
└── tasks.md             # Phase 2 output (/speckit.tasks — not yet created)
```

### Source Code

```text
# Backend (sms-backend)
backend/src/backend/
├── api/v1/
│   └── slr/                          # NEW: SLR API router package
│       ├── __init__.py
│       ├── router.py                 # Mounts sub-routers; registered in v1/router.py
│       ├── protocol.py               # ReviewProtocol CRUD + submit/validate
│       ├── quality.py                # QA checklist + scores
│       ├── inter_rater.py            # Kappa compute + post-discussion
│       ├── synthesis.py              # Synthesis run + results
│       └── grey_literature.py        # GreyLiteratureSource CRUD
├── services/
│   ├── slr_protocol_service.py       # NEW: protocol CRUD + AI review trigger
│   ├── quality_assessment_service.py # NEW: checklist CRUD + score aggregation
│   ├── inter_rater_service.py        # NEW: Kappa computation + threshold check
│   ├── synthesis_service.py          # NEW: synthesis orchestration (Strategy dispatch)
│   ├── slr_phase_gate.py             # NEW: SLR-specific phase unlock logic
│   ├── slr_report_service.py         # NEW: structured report generation + export
│   └── statistics.py                 # NEW: Cohen's Kappa, Q-test, meta-analysis
├── jobs/
│   ├── protocol_review_job.py        # NEW: ARQ job → ProtocolReviewerAgent
│   └── synthesis_job.py              # NEW: ARQ job → SynthesisStrategy
└── core/
    └── config.py                     # MODIFIED: add SLR_KAPPA_THRESHOLD, SLR_MIN_SYNTHESIS_PAPERS

backend/tests/
├── test_slr_protocol_service.py      # NEW
├── test_quality_assessment_service.py # NEW
├── test_inter_rater_service.py        # NEW
├── test_synthesis_service.py          # NEW
├── test_statistics.py                 # NEW
├── test_slr_phase_gate.py             # NEW
├── test_slr_report_service.py         # NEW
└── api/
    └── v1/
        └── slr/
            ├── test_protocol.py       # NEW
            ├── test_quality.py        # NEW
            ├── test_inter_rater.py    # NEW
            ├── test_synthesis.py      # NEW
            └── test_grey_literature.py # NEW

# Agents (sms-agents)
agents/src/agents/
├── services/
│   └── protocol_reviewer.py          # NEW: ProtocolReviewerAgent
└── prompts/
    └── protocol_reviewer/             # NEW: Jinja2 prompt templates
        ├── system.md
        └── user.md.j2

agents/tests/
├── test_protocol_reviewer.py          # NEW
└── metamorphic/
    └── test_protocol_reviewer_meta.py # NEW: hypothesis-based metamorphic tests

# DB (sms-db)
db/src/db/models/
└── slr.py                             # NEW: 6 SLR ORM models

db/src/db/models/__init__.py           # MODIFIED: export new models

db/alembic/versions/
└── 0015_slr_workflow.py               # NEW: Alembic migration

db/tests/
└── test_slr_models.py                 # NEW

# Frontend
frontend/src/
├── pages/slr/                         # NEW: SLR-specific page views
│   ├── ProtocolEditorPage.tsx
│   ├── QualityAssessmentPage.tsx
│   ├── SynthesisPage.tsx
│   └── GreyLiteraturePage.tsx
├── components/slr/                    # NEW: SLR-specific reusable components
│   ├── ProtocolForm.tsx
│   ├── ProtocolReviewReport.tsx
│   ├── QualityChecklistEditor.tsx
│   ├── QualityScoreForm.tsx
│   ├── InterRaterPanel.tsx
│   ├── DiscussionFlowPanel.tsx
│   ├── SynthesisConfigForm.tsx
│   ├── ForestPlotViewer.tsx
│   ├── FunnelPlotViewer.tsx
│   └── GreyLiteraturePanel.tsx
├── services/slr/                      # NEW: API client + Zod schemas
│   ├── protocolApi.ts
│   ├── qualityApi.ts
│   ├── interRaterApi.ts
│   ├── synthesisApi.ts
│   └── greyLiteratureApi.ts
└── hooks/slr/                         # NEW: TanStack Query hooks
    ├── useProtocol.ts
    ├── useQualityAssessment.ts
    ├── useInterRater.ts
    ├── useSynthesis.ts
    └── useGreyLiterature.ts

frontend/src/pages/StudyPage.tsx       # MODIFIED: route SLR study type to new pages

frontend/e2e/
└── slr-workflow.spec.ts               # NEW: Playwright e2e tests
```

**Structure Decision**: Web application (Option 2) — existing `backend/` + `frontend/` layout extended; SLR code isolated in dedicated subdirectories (`api/v1/slr/`, `pages/slr/`, `components/slr/`, `services/slr/`, `hooks/slr/`) to avoid polluting existing SMS workflow namespaces.

---

## Complexity Tracking

| Item | Type | Why Accepted / Resolution |
|------|------|--------------------------|
| `statistics.py` (scipy + scikit-learn) | New external deps | Required for Q-test (chi2.sf) and Kappa (sklearn); industry-standard, Python 3.14 compatible; no approved alternative exists |
| Strategy pattern for synthesis (3 concrete implementations) | Architecture | OCP compliance; avoids branching on `synthesis_approach` in 4+ service methods; 3 is not premature — all 3 approaches are spec-required |
| SVG stored as `Text` in `SynthesisResult` | Design choice | Consistent with existing `DomainModel` pattern that stores SVG/JSON in DB columns; avoids file system complexity for an artifact that is study-scoped |
