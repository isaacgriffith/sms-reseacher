# Implementation Plan: Systematic Mapping Study Workflow System

**Branch**: `002-sms-workflow` | **Date**: 2026-03-10 | **Last Updated**: 2026-03-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-sms-workflow/spec.md`
**Constitution**: Aligned to v1.5.0 (Principles I–IX)

---

## Summary

Implement the full Systematic Mapping Study (SMS) workflow system: a multi-phase, AI-augmented research automation platform that guides researchers through study scoping (PICO/C), database search with iterative refinement, automated paper screening with multi-reviewer support, structured data extraction, and publication-ready visualization generation. The system extends the existing FastAPI + SQLAlchemy + React mono-repo scaffold with substantial new data models, background job infrastructure, nine AI agent types, a FastMCP integration layer, and a multi-page React frontend covering all five SMS phases.

Updated (2026-03-11) to include: comprehensive study-level audit trail (FR-044, NFR-002), administrative health and job-retry dashboard (FR-045, NFR-004), secrets-hygiene controls across all export artefacts (FR-046, NFR-003), and system-managed audit timestamps on every persistent entity (NFR-001).

---

## Technical Context

**Language/Version**: Python 3.14 (backend, agents, db, researcher-mcp); TypeScript 5.4 / Node 20 LTS (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.111+, SQLAlchemy 2.0 async, LiteLLM 1.40+, structlog, python-jose (JWT), httpx, ARQ (async job queue with Redis), matplotlib (SVG charts), networkx (graph/domain model), plotly + kaleido (bubble charts)
- Agents: LiteLLM, FastMCP 2.0+, Jinja2 prompt templates, Pydantic 2
- DB: SQLAlchemy + asyncpg (PostgreSQL prod), aiosqlite (test), Alembic migrations
- Frontend: React 18, TypeScript 5.4, Vite 5, Vitest, React Query (server state + SSE), React Hook Form, Recharts (bar/bubble charts), D3.js (domain model UML SVG)
- researcher-mcp: FastMCP 2.0+, httpx, tenacity

**Storage**: PostgreSQL 16 (production/Docker); SQLite + aiosqlite (unit/integration tests)
**Testing**: pytest + pytest-asyncio (backend/agents/db); Vitest + Testing Library (frontend); deepeval (agent evals); mutmut / Stryker (mutation testing)
**Target Platform**: Linux server (Docker Compose); browser-based SPA (React)
**Project Type**: Web application — REST API backend + React SPA frontend + async background workers + MCP tool server
**Performance Goals**:
- Paper inclusion/exclusion decisions: ≥85% AI-human agreement
- Full search pipeline (≤500 papers + 1 snowball round): completes without manual intervention
- SVG visualization generation: all 6 charts in ≤2 minutes
- Quality judge report: ≤90 seconds
- AI extraction per paper: ≤60 seconds (full text accessible)
**Constraints**: 5 concurrent users without data conflicts; optimistic locking on all shared records; async background jobs with real-time SSE progress; session-based JWT auth
**Scale/Scope**: ~5–10 concurrent users; studies with up to 500–2000 candidate papers; 9 AI agent types; 5 frontend phase views; ~20 new DB tables/extensions

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify the following gates before proceeding to implementation planning. Record any violations
in the Complexity Tracking table below with justification.

| Gate | Status | Notes |
|------|--------|-------|
| SOLID — no SRP violations in target modules | PASS | New modules have single, focused responsibility (screener, extractor, search_builder, etc.) |
| SOLID — extension points exist (OCP) where variation expected | PASS | Agent services injected via constructor; reviewer set configurable per study |
| Structural — no DRY violations (duplication) | PASS | Shared audit trail logic in one service; LLMClient centralizes all LLM calls |
| Structural — no YAGNI violations (speculative generality) | PASS | Only the 5-phase SMS workflow + audit/health FRs from spec implemented |
| Code clarity — no long methods (>20 lines) in touched code | PASS | Existing services are short; new code plan follows same discipline |
| Code clarity — no switch/if-chain smells in touched code | PASS | Research type dispatch uses R1–R6 decision-rule objects, not if-chains |
| Code clarity — no common code smells identified | PASS | No God objects; each router/service/model is narrowly scoped |
| Refactoring — pre-implementation review completed | PASS | Existing router, screener, and db models reviewed; no blocking smells |
| Refactoring — any found refactors added to task list with tests | N/A | No refactors required before feature work |
| GRASP/patterns — responsibility assignments reviewed | PASS | Repository pattern for DB; Strategy for reviewers; Observer pattern for SSE job progress |
| Test coverage — existing tests pass; refactor tests written first | PASS | Existing test suite passes; all new modules require ≥85% coverage |
| Toolchain (VII) — no unapproved deps or tool substitutions introduced | PASS | All deps (FastAPI, SQLAlchemy 2.0, ARQ, LiteLLM, FastMCP, TanStack Query, RHF+Zod) are in the approved stack |
| Toolchain (VII) — FastAPI/SQLAlchemy 2.x/ARQ/LiteLLM patterns followed | PASS | async def routes, Depends() injection, Mapped[] annotations, ARQ ctx jobs, LLMClient wrapper |
| Observability (VIII) — new models have audit fields + structlog used | PASS | All new models include created_at/updated_at; structlog used in all service layers |
| Observability (VIII) — config via Pydantic BaseSettings + lru_cache | PASS | backend/core/config.py and agents/core/config.py follow this pattern; no new config patterns |
| Infrastructure (VIII) — Docker services have healthchecks if added | PASS | No new Docker services introduced; existing services already have healthchecks. NFR-004 satisfied: each service (backend, worker, db, redis, researcher-mcp) MUST have a `healthcheck:` block in `docker-compose.yml`; T134 admin dashboard reads these statuses at runtime |
| Language (IX) — React components functional, props typed, ≤100 JSX lines | PASS | All components are function components; props interfaces required per task descriptions |
| Language (IX) — Hooks at top level only; no inline object/function refs in dep arrays | ⚠ REVIEW | Must verify during implementation — SSE hook and wizard step effects are high-risk sites |
| Language (IX) — No React state mutation; no array-index keys | PASS | State updates via setter only per plan; list renders use entity IDs as keys |
| Language (IX) — >3 related useState → useReducer; useCallback only when justified | ⚠ REVIEW | NewStudyWizard (5-step state) MUST use useReducer; verify before T037 is marked done |
| Language (IX) — useEffect returns cleanup for all resource-acquiring effects | ⚠ REVIEW | T073 SSE EventSource MUST close on unmount; verify T073 before marking done |
| Language (IX) — React.memo applied deliberately; useImperativeHandle for imperative APIs | PASS | No imperative child APIs planned; React.memo applied only where noted in task comments |
| Language (IX) — useWatch (not watch) for reactive form field subscriptions | ⚠ REVIEW | Applies to NewStudyWizard, CriteriaForm, ValidityForm, ExtractionView — verify per component |
| Language (IX) — Vite env vars use VITE_ prefix; import.meta.env only | PASS | No client-side env vars added; API URL passed through services/api.ts config |
| Language (IX) — Python: no plain dict for domain data; pathlib used | PASS | All new agent outputs are Pydantic models; no dict-typed domain data in plan |
| Language (IX) — Python: no mutable defaults; specific exception handling | PASS | No default args in new service signatures; exceptions raised as HTTPException or specific types |
| Language (IX) — TypeScript: no any/enum/non-null(!); unknown+Zod at boundaries | ⚠ REVIEW | Zod schemas must wrap all API responses in frontend services; verify api.ts generics use unknown |
| Code clarity (III) — all functions/methods/classes have Google-style docstrings (Python) or JSDoc (TypeScript); CLI handlers: brief description only, no Args/Returns | ⚠ REVIEW | Added in v1.5.0; verify during T159 polish pass — ruff `D` rule set enforces Python; ESLint jsdoc plugin for TypeScript |

**Re-check result**: 4 gates require implementation-time verification (marked ⚠ REVIEW). No blocking violations at plan time. Add to Complexity Tracking if any ⚠ gates fail during implementation.

---

## Project Structure

### Documentation (this feature)

```text
specs/002-sms-workflow/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── api-v1.md        # REST API endpoint contracts
│   └── mcp-tools.md     # researcher-mcp tool contracts
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
# Web application layout (backend + frontend + workers)

backend/
├── src/backend/
│   ├── api/
│   │   └── v1/
│   │       ├── router.py                  # extend with new routers
│   │       ├── auth.py                    # login, session endpoints
│   │       ├── users.py                   # user profile endpoints
│   │       ├── groups.py                  # research group CRUD
│   │       ├── studies.py                 # study CRUD + wizard
│   │       ├── pico.py                    # PICO/C component endpoints
│   │       ├── search_strings.py          # search string versioning
│   │       ├── searches.py                # search execution + progress
│   │       ├── criteria.py                # inclusion/exclusion criteria
│   │       ├── papers.py                  # candidate paper CRUD + decisions
│   │       ├── reviewers.py               # reviewer config endpoints
│   │       ├── extractions.py             # data extraction endpoints
│   │       ├── jobs.py                    # background job status + SSE stream
│   │       ├── results.py                 # visualization + export endpoints
│   │       ├── quality.py                 # quality judge endpoints
│   │       ├── audit.py                   # FR-044: study audit log endpoints (admin)
│   │       └── admin.py                   # FR-045: system health + job-retry dashboard
│   ├── core/
│   │   ├── config.py                      # existing — extend with Redis/ARQ config
│   │   ├── auth.py                        # existing JWT auth
│   │   └── logging.py                     # existing structlog
│   ├── jobs/
│   │   ├── worker.py                      # ARQ worker entrypoint
│   │   ├── search_job.py                  # full search + snowball job
│   │   └── extraction_job.py              # batch data extraction job
│   └── services/
│       ├── dedup.py                       # paper deduplication: exact DOI match → fuzzy title (rapidfuzz WRatio ≥92) + author overlap (≥1 matching author surname); tie-break = earlier candidate_paper.id wins; "duplicate" tagged with duplicate_of_id pointing to the surviving record
│       ├── export.py                      # CSV/JSON/archive export builder (FR-046: redact secrets — see export redaction note below)
│       ├── audit.py                       # FR-044/NFR-002: AuditRecord write/query service
│       └── visualization.py              # SVG chart generation: matplotlib (frequency infographic, publications-per-year, venues, research locale, key authors) + plotly/kaleido (keyword bubble map, classification bubble charts); D3.js renders domain model in frontend

db/
└── src/db/
    ├── base.py                            # existing declarative base
    ├── models.py                          # extend existing Study/Paper/StudyPaper
    └── models/                            # new model modules (see data-model.md)
        ├── users.py                       # User, ResearchGroup, GroupMembership
        ├── study.py                       # extended Study, StudyMember, Reviewer
        ├── pico.py                        # PICOComponent
        ├── search.py                      # SearchString, SearchStringIteration
        ├── criteria.py                    # InclusionCriterion, ExclusionCriterion
        ├── paper.py                       # extend Paper + CandidatePaper, PaperDecision
        ├── extraction.py                  # DataExtraction, ExtractionField
        ├── jobs.py                        # BackgroundJob, JobProgress
        ├── results.py                     # DomainModel, ClassificationScheme, QualityReport
        ├── metrics.py                     # SearchMetrics
        └── audit.py                       # FR-044/NFR-001/NFR-002: AuditRecord (actor, timestamp, entity, field, before, after)

agents/
└── src/agents/
    ├── core/
    │   ├── config.py                      # existing
    │   ├── llm_client.py                  # existing
    │   ├── mcp_client.py                  # existing
    │   └── prompt_loader.py              # existing
    ├── services/
    │   ├── screener.py                    # existing ScreenerAgent — extend
    │   ├── extractor.py                   # existing ExtractorAgent — extend
    │   ├── synthesiser.py                 # existing SynthesiserAgent
    │   ├── librarian.py                   # new LibrarianAgent
    │   ├── expert.py                      # new ExpertAgent (10-20 seed papers)
    │   ├── search_builder.py              # new SearchStringBuilderAgent
    │   ├── quality_judge.py               # new QualityJudgeAgent (rubric-based)
    │   └── domain_modeler.py              # new DomainModelAgent (UML from codings)
    └── prompts/
        ├── screener/                      # existing
        ├── extractor/                     # existing
        ├── synthesiser/                   # existing
        ├── librarian/                     # new
        ├── expert/                        # new
        ├── search_builder/                # new
        ├── quality_judge/                 # new
        └── domain_modeler/               # new

researcher-mcp/
└── src/researcher_mcp/
    ├── server.py                          # existing — add new tools
    └── tools/
        ├── search.py                      # existing search_papers, get_paper
        ├── authors.py                     # existing search_authors, get_author
        ├── pdf.py                         # existing fetch_paper_pdf
        ├── snowball.py                    # new: get_citations, get_references
        └── scraper.py                     # new: scrape_journal, scrape_author_page

frontend/
└── src/
    ├── components/
    │   ├── auth/                          # LoginPage, AuthProvider
    │   ├── layout/                        # AppShell, SideNav, Avatar
    │   ├── groups/                        # GroupsList, GroupCard
    │   ├── studies/                       # StudyList, StudyCard, NewStudyWizard
    │   ├── phase1/                        # PICOForm, SeedPapers, LibrarianChat
    │   ├── phase2/                        # SearchStringEditor, TestRetest, CriteriaForm, PaperQueue
    │   ├── phase3/                        # ExtractionView, ReviewerPanel
    │   ├── phase4/                        # ValidityForm
    │   ├── phase5/                        # QualityReport
    │   ├── results/                       # ChartGallery, ExportPanel
    │   ├── jobs/                          # JobProgressPanel (SSE-fed)
    │   ├── admin/                         # FR-045: ServiceHealthPanel, JobRetryPanel
    │   └── shared/                        # DiffViewer (conflict resolution), PaperCard, etc.
    ├── pages/
    │   ├── LoginPage.tsx
    │   ├── GroupsPage.tsx
    │   ├── StudiesPage.tsx
    │   ├── StudyPage.tsx                  # phase router
    │   ├── ResultsPage.tsx
    │   └── AdminPage.tsx                  # FR-045: health dashboard + job retry UI
    └── services/
        ├── api.ts                         # typed fetch wrappers
        ├── auth.ts                        # session management
        └── jobs.ts                        # SSE EventSource hook

agent-eval/
└── src/agent_eval/
    ├── cli.py                             # existing typer CLI
    └── evals/
        ├── screener_eval.py               # existing — extend
        ├── extractor_eval.py              # existing
        ├── librarian_eval.py              # new
        ├── expert_eval.py                 # new
        ├── search_builder_eval.py         # new
        └── quality_judge_eval.py          # new
```

**Structure Decision**: Option 2 (Web application) — existing mono-repo workspace with distinct backend/, agents/, db/, researcher-mcp/, frontend/, and agent-eval/ packages. New code fits entirely within existing packages; no new workspace members required.

---

## Complexity Tracking

| Item | Type | Why Accepted / Resolution |
|------|------|--------------------------|
| AuditRecord generic model (entity_type + entity_id + field) | Architecture | A single polymorphic audit table is simpler than per-entity audit tables at this scale; acceptable under YAGNI because a generic model covers all 20+ entity types without proliferating tables. Reviewed against SRP: audit write/query is a distinct service layer. |
| Admin health endpoint exposes internal service state | Security design | Health endpoint MUST be access-controlled (admin role only); no sensitive config values are ever included in health response payloads (Principle VIII / FR-046). |
| Export redaction (FR-046 / NFR-003) | Security design | `export.py` MUST use an explicit allowlist of exportable fields (defined in spec.md FR-046). Implementation: iterate `Settings.__fields__` and strip any key present in the exported payload; additionally strip `user.email`, `user.id`, and all FK-derived identifiers — replace with `display_name` strings. No auto-serialization of ORM objects; export uses hand-rolled serializers that only include allowlisted fields. |

