# Implementation Plan: Systematic Mapping Study Workflow System

**Branch**: `002-sms-workflow` | **Date**: 2026-03-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-sms-workflow/spec.md`

---

## Summary

Implement the full Systematic Mapping Study (SMS) workflow system: a multi-phase, AI-augmented research automation platform that guides researchers through study scoping (PICO/C), database search with iterative refinement, automated paper screening with multi-reviewer support, structured data extraction, and publication-ready visualization generation. The system extends the existing FastAPI + SQLAlchemy + React mono-repo scaffold with substantial new data models, background job infrastructure, six AI agent types, a FastMCP integration layer, and a multi-page React frontend covering all five SMS phases.

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
**Scale/Scope**: ~5–10 concurrent users; studies with up to 500–2000 candidate papers; 6 AI agent types; 5 frontend phase views; ~20 new DB tables/extensions

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution file is an unfilled template with no custom gates defined. Applying general software engineering quality gates:

| Gate | Status | Notes |
|------|--------|-------|
| All new DB tables have Alembic migrations | PASS (by convention — existing pattern) | |
| Test coverage ≥ 85% (enforced by pytest config) | PASS (enforced in all pyproject.toml configs) | |
| Type checking strict=true (mypy) | PASS (enforced in all pyproject.toml configs) | |
| No new packages beyond workspace members | PASS — all new code fits in existing packages | |
| Frontend test coverage via Vitest | PASS (enforced in package.json scripts) | |
| Background jobs use durable queue (not in-process) | PASS — ARQ + Redis chosen (see research.md) | |
| Agent evals via deepeval for all new agents | PASS — sms-agent-eval package exists for this | |

No gate violations. No Complexity Tracking entries required.

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
│   │       └── quality.py                 # quality judge endpoints
│   ├── core/
│   │   ├── config.py                      # existing — extend with Redis/ARQ config
│   │   ├── auth.py                        # existing JWT auth
│   │   └── logging.py                     # existing structlog
│   ├── jobs/
│   │   ├── worker.py                      # ARQ worker entrypoint
│   │   ├── search_job.py                  # full search + snowball job
│   │   └── extraction_job.py              # batch data extraction job
│   └── services/
│       ├── dedup.py                       # paper deduplication (DOI + fuzzy title)
│       ├── export.py                      # CSV/JSON/archive export builder
│       └── visualization.py              # SVG chart generation (Altair/matplotlib)

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
        └── metrics.py                     # SearchMetrics

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
    │   └── shared/                        # DiffViewer (conflict resolution), PaperCard, etc.
    ├── pages/
    │   ├── LoginPage.tsx
    │   ├── GroupsPage.tsx
    │   ├── StudiesPage.tsx
    │   ├── StudyPage.tsx                  # phase router
    │   └── ResultsPage.tsx
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

No constitution violations identified.

