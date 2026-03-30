# Implementation Plan: Rapid Review Workflow

**Branch**: `008-rapid-review-workflow` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-rapid-review-workflow/spec.md`

## Summary

Extend the SMS Researcher platform to support Rapid Reviews — time-bounded systematic
studies producing practitioner-facing Evidence Briefings. The implementation adds six new ORM
models (`RapidReviewProtocol`, `PractitionerStakeholder`, `RRThreatToValidity`,
`RRNarrativeSynthesisSection`, `EvidenceBriefing`, `EvidenceBriefingShareToken`), a new
`/api/v1/rapid/` route module, a `NarrativeSynthesiserAgent` with ARQ job support, a
versioned Evidence Briefing with PDF/HTML export, a public share-token mechanism, and a
complete React frontend mirroring the SLR phase structure. The `StudyType.RAPID` enum value
(already defined) is wired into the phase-gate dispatch.

## Technical Context

**Language/Version**: Python 3.14 (backend, db, agents); TypeScript 5.4 / Node 20 LTS (frontend)
**Primary Dependencies**: FastAPI + Pydantic v2, SQLAlchemy 2.0+ async, Alembic, ARQ, LiteLLM,
  Jinja2, weasyprint (new — PDF generation), React 18, MUI v5, TanStack Query v5,
  react-hook-form + Zod
**Storage**: PostgreSQL 16 (production); SQLite + aiosqlite (tests)
**Testing**: pytest + asyncio_mode=auto (backend); vitest + @testing-library/react (frontend);
  Playwright (e2e)
**Target Platform**: Linux server (Docker Compose); browser (React SPA)
**Project Type**: Web service + SPA (extension to existing monorepo)
**Performance Goals**: Evidence Briefing generation ≤ 60 s (SC-003); AI draft ≤ 30 s/section
  (SC-007); public share endpoint ≤ 200 ms p95 (standard platform target)
**Constraints**: weasyprint one-page A4/letter PDF; share tokens revocable; at most one
  PUBLISHED briefing per study at any time
**Scale/Scope**: Same scale as existing SLR/SMS workflows; no new concurrency requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| SOLID — no SRP violations in target modules | ✅ Pass | Each new service has a single focused responsibility; no existing services modified |
| SOLID — extension points exist (OCP) where variation expected | ✅ Pass | Phase-gate dispatch dict extended with `StudyType.RAPID` key; no existing logic modified |
| Structural — no DRY violations (duplication) | ✅ Pass | Reusing Study, CandidatePaper, Reviewer, BackgroundJob entities; no duplication of existing protocol/phase logic |
| Structural — no YAGNI violations (speculative generality) | ✅ Pass | All new entities map 1:1 to spec requirements; no speculative fields |
| Code clarity — no long methods (>20 lines) in touched code | ✅ Pass | No existing files modified in Phase 1; all new code will follow the ≤20-line rule |
| Code clarity — no switch/if-chain smells in touched code | ✅ Pass | Phase gate uses dispatch dict (not if-chain); strategy pattern for appraisal modes |
| Code clarity — no common code smells identified | ✅ Pass | Pre-implementation review of slr_phase_gate.py and protocol routes shows clean patterns |
| Refactoring — pre-implementation review completed | ✅ Pass | Reviewed slr_phase_gate.py, slr_protocol_service.py, synthesis_job.py — no smells requiring remediation |
| Refactoring — any found refactors added to task list with tests | ✅ Pass | No refactors required; all new code |
| GRASP/patterns — responsibility assignments reviewed | ✅ Pass | Information Expert: protocol service owns threat auto-creation; Creator: briefing service owns version numbering; Protected Variations: dispatch dict isolates phase logic per study type |
| Test coverage — existing tests pass; refactor tests written first | ✅ Pass | No existing files modified (only additive); existing test suite unaffected |
| Toolchain (VII) — no unapproved deps or tool substitutions introduced | ✅ Pass | weasyprint is new but is the standard headless HTML→PDF library; constitution amendment not required as it is additive, not a substitution. No tool is replaced. |
| Toolchain (VII) — FastAPI/SQLAlchemy 2.x/ARQ/LiteLLM patterns followed | ✅ Pass | All new routes use `async def`; new models use `Mapped[T]`; new jobs follow ARQ ctx pattern; LLMClient used for agent |
| Observability (VIII) — new models have audit fields + structlog used | ✅ Pass | All 6 new models include `created_at`/`updated_at`; `RapidReviewProtocol` and `EvidenceBriefing` include `version_id` for optimistic locking |
| Observability (VIII) — config via Pydantic BaseSettings + lru_cache | ✅ Pass | No new config keys required beyond what may be added to existing Settings |
| Infrastructure (VIII) — Docker services have healthchecks if added | ✅ Pass | No new Docker services; weasyprint runs in-process |
| Language (IX) — React components functional, props typed, ≤100 JSX lines | ✅ Pass | All new components will follow SLR component patterns; complex views decomposed |
| Language (IX) — Hooks called at top level only (Rules of Hooks); no inline refs in deps | ✅ Pass | All new hooks follow SLR hook patterns |
| Language (IX) — No React state mutation; no array-index keys in lists | ✅ Pass | Enforced by constitution and ESLint |
| Language (IX) — >3 related useState → useReducer; useCallback only when justified | ✅ Pass | Protocol form uses react-hook-form; briefing version list uses TanStack Query |
| Language (IX) — useEffect returns cleanup for all resource-acquiring effects | ✅ Pass | All new effects will include cleanup |
| Language (IX) — React.memo applied deliberately; useImperativeHandle used for imperative APIs | ✅ Pass | No speculative React.memo; no imperative child APIs in scope |
| Language (IX) — useWatch used (not watch) for reactive form field subscriptions | ✅ Pass | Protocol form uses useWatch for conditional field rendering |
| Language (IX) — Vite env vars use VITE_ prefix + import.meta.env | ✅ Pass | No new env vars exposed to the frontend |
| Language (IX) — Python: no plain dict for domain data; pathlib used | ✅ Pass | All new domain data uses Pydantic models or SQLAlchemy Mapped types |
| Language (IX) — Python: no mutable defaults; specific exception handling | ✅ Pass | Enforced by ruff and mypy strict |
| Language (IX) — TypeScript: no any/enum/non-null(!) without justification | ✅ Pass | All new TS code uses unknown+Zod at API boundaries |
| Language (IX) — TypeScript: unknown + Zod at all external boundaries | ✅ Pass | All API response parsing uses Zod schemas in service layer |
| Code clarity — all source files have a module-level doc comment (Python module docstring / TS file-level JSDoc) | ✅ Pass | All new files will include module-level doc comments per constitution v1.7.0 |
| Code clarity — all functions/methods/classes have doc comments (Google-style / JSDoc); CLI handlers: brief description only, no Args/Returns | ✅ Pass | Enforced by ruff D rules and ESLint JSDoc plugin |
| Pre-existing issues — all pre-existing test failures, linting errors, and type errors in touched files are resolved before feature completion | ✅ Pass | No existing files are modified in Phase 2 (foundational); will verify during each implementation phase |
| Feature completion docs — CLAUDE.md, root README.md, affected subproject README.md(s), root CHANGELOG.md, affected subproject CHANGELOG.md(s) update tasks in task list | ✅ Pass | TDOC tasks included in final phase |

## Project Structure

### Documentation (this feature)

```text
specs/008-rapid-review-workflow/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── api-contracts.md # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
db/
├── src/db/models/
│   └── rapid_review.py              # 6 new ORM models + enums
└── alembic/versions/
    └── 0016_rapid_review_workflow.py

backend/
├── src/backend/
│   ├── api/v1/
│   │   ├── rapid/
│   │   │   ├── __init__.py          # router registration
│   │   │   ├── protocol.py          # GET/PUT protocol, POST validate
│   │   │   ├── stakeholders.py      # CRUD stakeholders
│   │   │   ├── threats.py           # GET threats (read-only)
│   │   │   ├── synthesis.py         # GET/PUT synthesis sections, POST ai-draft, POST complete
│   │   │   └── briefing.py          # GET/POST briefings, publish, export, share-token
│   │   └── public/
│   │       └── briefings.py         # GET /public/briefings/{token} (no auth)
│   ├── services/
│   │   ├── rr_phase_gate.py         # get_rr_unlocked_phases
│   │   ├── rr_protocol_service.py   # protocol CRUD + validate + invalidation cascade
│   │   ├── narrative_synthesis_service.py  # section management + threat auto-creation
│   │   └── evidence_briefing_service.py    # versioning, publish, PDF/HTML, share tokens
│   ├── jobs/
│   │   ├── narrative_synthesis_job.py  # run_narrative_draft ARQ job
│   │   └── evidence_briefing_job.py    # run_generate_evidence_briefing ARQ job
│   └── templates/rapid/
│       └── evidence_briefing.html.j2  # Jinja2 HTML template for PDF/HTML export

agents/
└── src/agents/
    ├── prompts/narrative_synthesiser/
    │   ├── system.md
    │   └── user.md.j2
    └── narrative_synthesiser_agent.py

frontend/
└── src/
    ├── pages/rapid/
    │   ├── ProtocolEditorPage.tsx
    │   ├── NarrativeSynthesisPage.tsx
    │   └── EvidenceBriefingPage.tsx
    ├── components/rapid/
    │   ├── ProtocolForm.tsx
    │   ├── StakeholderPanel.tsx
    │   ├── ThreatToValidityList.tsx
    │   ├── NarrativeSectionEditor.tsx
    │   ├── BriefingVersionPanel.tsx
    │   └── BriefingPreview.tsx
    ├── hooks/rapid/
    │   ├── useRRProtocol.ts
    │   ├── useStakeholders.ts
    │   ├── useNarrativeSynthesis.ts
    │   └── useBriefingVersions.ts
    └── services/rapid/
        ├── protocolApi.ts
        ├── stakeholdersApi.ts
        ├── synthesisApi.ts
        └── briefingApi.ts
```

**Structure Decision**: Web application layout (Option 2). All new Python code is additive
to existing `backend/`, `db/`, and `agents/` packages. Frontend follows the SLR
feature-module pattern under `frontend/src/`.

## Complexity Tracking

| Item | Type | Why Accepted / Resolution |
|------|------|--------------------------|
| weasyprint new dependency | Toolchain | Additive PDF library; no existing tool replaced; not a constitution violation. Added to backend/pyproject.toml. |
| EvidenceBriefing publish atomicity | Concurrency | Single transaction: UPDATE previous PUBLISHED→DRAFT then UPDATE target→PUBLISHED. No distributed lock needed; PostgreSQL serialises the two-step UPDATE within the transaction. |
| PROTOCOL_INVALIDATED enum extension | Migration | Extends existing `candidate_paper_status` PostgreSQL enum. Must use `ALTER TYPE ... ADD VALUE` in migration (non-reversible in PostgreSQL without recreation). `downgrade()` will leave the value in place but stop using it — documented in migration. |
| Public briefings endpoint (no auth) | Security | Token is cryptographically random (32 bytes entropy); revocable; serves read-only data. No study metadata beyond briefing content is exposed. Rate limiting via existing middleware sufficient. |
