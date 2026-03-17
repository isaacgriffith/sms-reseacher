# Implementation Plan: Database Search, Retrieval & Paper Processing

**Branch**: `006-database-search-and-retrieval` | **Date**: 2026-03-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/006-database-search-and-retrieval/spec.md`

## Summary

Implement real academic database integrations (IEEE Xplore, ACM DL, Google Scholar, Inspec, Scopus, Web of Science, ScienceDirect, SpringerLink, Semantic Scholar) as FastMCP tools in `researcher-mcp`, upgrade full-text retrieval and citation/reference lookup stubs, add MarkItDown-based paper-to-Markdown conversion, and deliver per-study database selection UI plus admin panel credential management for subscription-gated services.

The primary architectural pattern is a **parallel fan-out registry**: a `SourceRegistry` maps `DatabaseIndex` enum values to source instances; `search_papers` queries all enabled sources concurrently via `asyncio.gather`, then deduplicates results. New sources extend the registry without modifying existing fan-out logic (OCP). Synchronous third-party libraries (pybliometrics, scholarly, unpywall, markitdown, scidownl) are wrapped with `asyncio.to_thread()` to honour the Constitution's async discipline requirement.

---

## Technical Context

**Language/Version**: Python 3.14 (researcher-mcp, backend, db); TypeScript 5.4 / Node 20 LTS (frontend)
**Primary Dependencies**:
- `researcher-mcp`: fastmcp 3.x, httpx, pybliometrics 4.4+, semanticscholar 0.11+, scholarly 1.7.11, unpywall 0.2.3, springernature-api-client 0.0.9, markitdown[all] 0.1.5, scidownl 1.0.2, beautifulsoup4, tenacity
- `backend`: FastAPI, Pydantic v2, SQLAlchemy 2.0+ async, cryptography (Fernet)
- `frontend`: React 18, MUI v5, TanStack Query v5, react-hook-form + Zod
**Storage**: PostgreSQL 16 (production); SQLite + aiosqlite (tests)
**Testing**: pytest (asyncio_mode=auto), vitest, Playwright; minimum 85% coverage
**Target Platform**: Linux server (Docker Compose)
**Project Type**: Web service (FastAPI backend) + MCP server (FastMCP) + React SPA frontend
**Performance Goals**: Fan-out search across 3+ indices should return in <30 seconds; individual source calls respect each API's rate limits
**Constraints**: All synchronous library calls offloaded via `asyncio.to_thread()`; SciHub gated at two levels; API keys never returned in plaintext
**Scale/Scope**: Up to 9 database indices per study; up to 200 results per source per search

---

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| SOLID — no SRP violations in target modules | PASS | Each source class handles exactly one external database |
| SOLID — extension points exist (OCP) where variation expected | PASS | `SourceRegistry` + `DatabaseSource` Protocol; new sources added by registration only |
| Structural — no DRY violations (duplication) | PASS | `PaperRecord` normalisation shared via `sources/base.py`; dedup logic in `core/dedup.py` |
| Structural — no YAGNI violations (speculative generality) | PASS | Only the 9 specified integrations are implemented; no future-proofing abstractions |
| Code clarity — no long methods (>20 lines) in touched code | PASS | Fan-out, dedup, and waterfall retrieval are decomposed into named helpers |
| Code clarity — no switch/if-chain smells in touched code | PASS | Source dispatch uses registry lookup (dict), not if/elif chains |
| Code clarity — no common code smells identified | PASS | No god objects; source classes are narrow; credential logic centralised in `CredentialService` |
| Refactoring — pre-implementation review completed | PASS | Existing stubs (`get_references`, `get_citations`, `fetch_paper_pdf`) are replaced entirely; no refactor tasks needed |
| Refactoring — any found refactors added to task list with tests | PASS | Stub replacement is a clean swap; pre-existing tests updated in same task |
| GRASP/patterns — responsibility assignments reviewed | PASS | SourceRegistry (Creator/Controller); each Source (Information Expert); CredentialService (Pure Fabrication) |
| Test coverage — existing tests pass; refactor tests written first | PASS | Existing tests updated before new source implementations in task ordering |
| Toolchain (VII) — no unapproved deps or tool substitutions introduced | PASS | All new libraries are approved in feature spec; no tool substitutions |
| Toolchain (VII) — FastAPI/SQLAlchemy 2.x/ARQ/LiteLLM patterns followed | PASS | New admin endpoints follow existing admin pattern (Depends, HTTPException, Pydantic v2) |
| Observability (VIII) — new models have audit fields + structlog used | PASS | `StudyDatabaseSelection` and `SearchIntegrationCredential` have `created_at`/`updated_at`; structlog used in all source classes |
| Observability (VIII) — config via Pydantic BaseSettings + lru_cache | PASS | `ResearcherSettings` extended with new env vars; `get_settings()` with `@lru_cache` |
| Infrastructure (VIII) — Docker services have healthchecks if added | PASS | No new Docker services; researcher-mcp healthcheck already present |
| Language (IX) — React components functional, props typed, ≤100 JSX lines | PASS | DatabaseSelectionPanel and SearchIntegrationsTable decomposed into sub-components |
| Language (IX) — Hooks called at top level only (Rules of Hooks); no inline refs in deps | PASS | Enforced via eslint-plugin-react-hooks |
| Language (IX) — No React state mutation; no array-index keys in lists | PASS | Source list items keyed by `database_index` string |
| Language (IX) — >3 related useState → useReducer; useCallback only when justified | PASS | Database selection state uses `useReducer` (multiple interdependent toggles) |
| Language (IX) — useEffect returns cleanup for all resource-acquiring effects | PASS | Connectivity status polling effect returns cleanup |
| Language (IX) — React.memo applied deliberately; useImperativeHandle for imperative APIs | PASS | No imperative APIs required in this feature |
| Language (IX) — useWatch used (not watch) for reactive form field subscriptions | PASS | SciHub acknowledgment checkbox uses `useWatch` |
| Language (IX) — Vite env vars use VITE_ prefix + import.meta.env | PASS | No new frontend env vars; backend vars never exposed to browser |
| Language (IX) — Python: no plain dict for domain data; pathlib used | PASS | `PaperRecord`, `AuthorProfile`, etc. are Pydantic models throughout |
| Language (IX) — Python: no mutable defaults; specific exception handling | PASS | All source classes catch specific HTTP/API exception types |
| Language (IX) — TypeScript: no any/enum/non-null(!) without justification | PASS | DatabaseIndex values typed as string literal union from backend response |
| Language (IX) — TypeScript: unknown + Zod at all external boundaries | PASS | All backend API responses validated with Zod schemas before use |
| Code clarity — all functions/methods/classes have doc comments (Google-style / JSDoc) | PASS | All new Python classes/methods get Google-style docstrings; exported TS symbols get JSDoc |
| Feature completion docs (X) — CLAUDE.md, README.md, CHANGELOG.md update tasks in task list | PASS | TDOC1–TDOC5 tasks included in tasks.md phase |

---

## Project Structure

### Documentation (this feature)

```text
specs/006-database-search-and-retrieval/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── backend-api.md   # REST API contracts
│   └── mcp-tools.md     # MCP tool contracts
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code Layout

```text
# researcher-mcp additions
researcher-mcp/
├── src/researcher_mcp/
│   ├── core/
│   │   ├── config.py             # Extended: new credential env vars
│   │   ├── http_client.py        # Unchanged
│   │   ├── registry.py           # New: SourceRegistry
│   │   └── dedup.py              # New: deduplication logic
│   ├── sources/
│   │   ├── base.py               # New: DatabaseSource Protocol + normalisation helpers
│   │   ├── ieee.py               # New: IEEESource
│   │   ├── acm.py                # New: ACMSource
│   │   ├── google_scholar.py     # New: GoogleScholarSource
│   │   ├── inspec.py             # New: InspecSource
│   │   ├── scopus.py             # New: ScopusSource
│   │   ├── wos.py                # New: WoSSource
│   │   ├── science_direct.py     # New: ScienceDirectSource
│   │   ├── springer.py           # New: SpringerSource
│   │   ├── semantic_scholar.py   # Upgraded: adds get_paper, search_author, get_author
│   │   ├── unpaywall.py          # Upgraded: async via to_thread, better error handling
│   │   ├── arxiv.py              # Unchanged
│   │   └── scihub.py             # Upgraded: scidownl instead of scraping
│   └── tools/
│       ├── search.py             # Upgraded: fan-out via SourceRegistry
│       ├── snowball.py           # Upgraded: Semantic Scholar primary, CrossRef fallback
│       ├── pdf.py                # Upgraded: cleaner waterfall, scidownl
│       ├── convert.py            # New: convert_paper_to_markdown, get_paper_markdown
│       ├── authors.py            # Upgraded: Semantic Scholar author tools
│       └── scraper.py            # Unchanged (grey literature scraping)
└── tests/
    ├── unit/
    │   ├── sources/              # Unit tests per source class (mocked HTTP)
    │   └── tools/                # Unit tests per tool (mocked sources)
    └── integration/
        └── sources/              # Integration tests (VCR cassettes or live with API keys)

# db additions
db/
├── src/db/models/
│   ├── __init__.py               # Extended: Paper gets full_text_* columns
│   └── search.py                 # New: StudyDatabaseSelection, SearchIntegrationCredential
└── alembic/versions/
    └── 0013_database_search_and_retrieval.py  # New migration

# backend additions
backend/src/backend/
├── api/v1/
│   ├── admin/
│   │   ├── search_integrations.py    # New: credential CRUD + test endpoint
│   │   └── router.py                 # Extended: register search_integrations router
│   ├── studies/
│   │   └── database_selection.py     # New: GET/PUT study database selection
│   └── papers/
│       └── markdown.py               # New: GET paper markdown
└── services/
    └── credential_service.py         # New: Fernet encrypt/decrypt for SearchIntegrationCredential

# frontend additions
frontend/src/
├── components/
│   ├── admin/
│   │   └── SearchIntegrationsTable/  # New: admin panel credential management
│   └── studies/
│       └── DatabaseSelectionPanel/   # New: per-study index selection UI
├── hooks/
│   └── useStudyDatabaseSelection.ts  # New: TanStack Query hook
└── pages/
    └── admin/
        └── AdminPage.tsx             # Extended: add Search Integrations tab
```

**Structure Decision**: Multi-project web application pattern (Option 2) — `backend/` + `frontend/` + `researcher-mcp/` + `db/`. Matches the established project layout from features 001–005. The feature adds source classes and tools to `researcher-mcp`, new DB models to `db/`, new API endpoints to `backend/`, and two new UI sections to `frontend/`.

---

## Complexity Tracking

No constitution violations requiring justification. No pre-existing code smells identified in the modules to be modified (stub tools, SemanticScholarSource, UnpaywallSource, config.py) during pre-implementation review.

| Item | Type | Why Accepted / Resolution |
|------|------|--------------------------|
| 8 new source classes + 3 upgrades | Scale | Each source has a unique external API with distinct auth, pagination, and normalisation logic. Sharing code via `base.py` Protocol prevents duplication while respecting SRP. No single source class can be combined with another without mixing concerns. |
| `asyncio.to_thread()` wrappers on 5 sync libraries | Constraint | Sync-only libraries (pybliometrics, scholarly, unpywall, markitdown, scidownl) cannot be made async without forking. The `to_thread` pattern is the approved Constitution approach for this boundary. |
