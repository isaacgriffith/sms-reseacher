# Tasks: Database Search, Retrieval & Paper Processing

**Input**: Design documents from `/specs/006-database-search-and-retrieval/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Tests**: Included — Constitution Principle VI mandates 85% line/branch coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete task dependencies)
- **[Story]**: Which user story this task belongs to (US1–US6)

---

## Phase 1: Setup

**Purpose**: Install dependencies and document new environment variables.

- [x] T001 Add pybliometrics, semanticscholar, scholarly, unpywall, springernature-api-client, markitdown[all], scidownl to `researcher-mcp/pyproject.toml` dependencies
- [x] T002 [P] Add all new env vars (IEEE_XPLORE_API_KEY, ELSEVIER_API_KEY, ELSEVIER_INST_TOKEN, WOS_API_KEY, SPRINGER_API_KEY, SEMANTIC_SCHOLAR_API_KEY, UNPAYWALL_EMAIL, SCHOLARLY_PROXY_URL, SCIHUB_ENABLED) with placeholder values to `.env.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 [P] Create `db/src/db/models/search_integrations.py` with `DatabaseIndex`, `IntegrationType`, `TestStatus`, `FullTextSource` enums and `StudyDatabaseSelection`, `SearchIntegrationCredential` ORM models (audit fields, optimistic locking on credential model)
- [x] T004 Add `full_text_markdown` (Text, nullable), `full_text_source` (FullTextSource enum, nullable), `full_text_converted_at` (DateTime tz-aware, nullable) columns to `Paper` model in `db/src/db/models/__init__.py`
- [x] T005 Create Alembic migration `db/alembic/versions/0014_database_search_and_retrieval.py` — creates `study_database_selection`, `search_integration_credential` tables and adds three columns to `paper` table with correct downgrade
- [x] T006 [P] Export new models from `db/src/db/models/__init__.py` (`StudyDatabaseSelection`, `SearchIntegrationCredential`, all new enums)
- [x] T007 [P] Create `researcher-mcp/src/researcher_mcp/sources/base.py` — `DatabaseSource` `typing.Protocol` with `search()`, `get_paper()` signatures and `normalise_to_paper_record()` helper functions for common field mapping
- [x] T008 [P] Create `researcher-mcp/src/researcher_mcp/core/registry.py` — `SourceRegistry` class mapping `DatabaseIndex` enum values to `DatabaseSource` instances; `register()`, `get()`, `get_enabled()` methods
- [x] T009 [P] Create `researcher-mcp/src/researcher_mcp/core/dedup.py` — `deduplicate_paper_records()` function using DOI as primary key and `(normalised_title, first_author_last_name)` as fallback
- [x] T010 Extend `ResearcherSettings` in `researcher-mcp/src/researcher_mcp/core/config.py` with new credential fields: `ieee_xplore_api_key`, `elsevier_api_key`, `elsevier_inst_token`, `wos_api_key`, `springer_api_key`, `semantic_scholar_api_key`, `unpaywall_email`, `scholarly_proxy_url`

**Checkpoint**: Foundation ready — all user story phases can now begin.

---

## Phase 3: User Story 1 — Configure and Execute Multi-Database Search (Priority: P1) 🎯 MVP

**Goal**: Fan-out search across all configured database indices with merged, deduplicated results.

**Independent Test**: With IEEExplore and Semantic Scholar indices enabled and credentials configured, run `search_papers(query="...", indices=["ieee_xplore","semantic_scholar"])` and receive a merged `SearchPapersResult` with results from both sources, no duplicates, and a `sources_failed=[]`.

### Tests for User Story 1 ⚠️ Write FIRST — verify they FAIL before implementation

- [ ] T011 [P] [US1] Write unit tests for `dedup.py` covering DOI-keyed dedup and title/author fallback in `researcher-mcp/tests/unit/core/test_dedup.py`
- [ ] T012 [P] [US1] Write unit tests for `SourceRegistry` (register, get, get_enabled) in `researcher-mcp/tests/unit/core/test_registry.py`
- [ ] T013 [P] [US1] Write unit tests for upgraded `search_papers` fan-out (mocked sources, partial failure, dedup) in `researcher-mcp/tests/unit/tools/test_search.py`
- [ ] T014 [P] [US1] Write integration tests for `GET /api/v1/studies/{study_id}/database-selection` and `PUT` with valid/invalid payloads in `backend/tests/integration/test_database_selection.py`
- [ ] T015 [P] [US1] Write frontend component tests for `DatabaseSelectionPanel` (toggles, warning badge for missing credential, SciHub acknowledgment) in `frontend/src/components/studies/DatabaseSelectionPanel/DatabaseSelectionPanel.test.tsx`

### Implementation for User Story 1

- [ ] T016 [P] [US1] Create `researcher-mcp/src/researcher_mcp/sources/ieee.py` — `IEEESource` implementing `DatabaseSource` Protocol via `httpx` REST calls to `https://ieeexploreapi.ieee.org/api/v1/search/articles`; normalises results to `PaperRecord`; wraps sync call in `asyncio.to_thread`
- [ ] T017 [P] [US1] Create `researcher-mcp/src/researcher_mcp/sources/acm.py` — `ACMSource` implementing `DatabaseSource` Protocol via `httpx` + `BeautifulSoup` scraping; conservative rate limit (10 RPM via `TokenBucket`); returns `truncated=True` flag on rate-limit; abstract-only records when institutional access unavailable
- [ ] T018 [P] [US1] Create `researcher-mcp/src/researcher_mcp/sources/google_scholar.py` — `GoogleScholarSource` implementing `DatabaseSource` Protocol via `scholarly` library; wraps all calls in `asyncio.to_thread`; configures proxy from `scholarly_proxy_url` setting if present
- [ ] T019 [P] [US1] Create `researcher-mcp/src/researcher_mcp/sources/inspec.py` — `InspecSource` implementing `DatabaseSource` Protocol via `httpx` REST calls to Elsevier Engineering Village API; returns structured `AccessDenied` error when institutional access unavailable
- [ ] T020 [P] [US1] Create `researcher-mcp/src/researcher_mcp/sources/scopus.py` — `ScopusSource` implementing `DatabaseSource` Protocol via `pybliometrics.ScopusSearch` and `AbstractRetrieval`; writes `pybliometrics.cfg` from settings at init; wraps calls in `asyncio.to_thread`
- [ ] T021 [P] [US1] Create `researcher-mcp/src/researcher_mcp/sources/wos.py` — `WoSSource` implementing `DatabaseSource` Protocol via `httpx` REST calls to `https://api.clarivate.com/apis/wos-starter/v1`; normalises WoS record schema to `PaperRecord`
- [ ] T022 [P] [US1] Create `researcher-mcp/src/researcher_mcp/sources/science_direct.py` — `ScienceDirectSource` implementing `DatabaseSource` Protocol via `pybliometrics.ScienceDirectSearch` and `ArticleRetrieval`; shares Elsevier credentials with `ScopusSource`; wraps calls in `asyncio.to_thread`
- [ ] T023 [P] [US1] Create `researcher-mcp/src/researcher_mcp/sources/springer.py` — `SpringerSource` implementing `DatabaseSource` Protocol via `springernature_api_client.MetaAPI`; wraps calls in `asyncio.to_thread`
- [ ] T024 [US1] Register all new source classes (T016–T023) plus existing `SemanticScholarSource` in `SourceRegistry` default instance in `researcher-mcp/src/researcher_mcp/core/registry.py`
- [ ] T025 [US1] Upgrade `search_papers` in `researcher-mcp/src/researcher_mcp/tools/search.py` to fan-out via `asyncio.gather` across all `SourceRegistry`-enabled sources, collect `SourceFailure` records for failed sources, and deduplicate via `dedup.py`
- [ ] T026 [P] [US1] Add `search_ieee` and `get_ieee_paper` `@mcp.tool` functions to `researcher-mcp/src/researcher_mcp/tools/search.py`
- [ ] T027 [P] [US1] Add `search_acm`, `search_google_scholar`, `search_inspec` `@mcp.tool` functions to `researcher-mcp/src/researcher_mcp/tools/search.py`
- [ ] T028 [P] [US1] Add `search_scopus`, `get_scopus_paper`, `search_wos`, `search_sciencedirect`, `search_springer` `@mcp.tool` functions to `researcher-mcp/src/researcher_mcp/tools/search.py`
- [ ] T029 [P] [US1] Add `search_semantic_scholar` and `get_paper_semantic_scholar` `@mcp.tool` functions to `researcher-mcp/src/researcher_mcp/tools/search.py` (delegates to upgraded `SemanticScholarSource`)
- [ ] T030 [P] [US1] Create `backend/src/backend/services/database_selection.py` — `StudyDatabaseSelectionService` with `get_selection(study_id)`, `save_selection(study_id, selections)`, `compute_index_status(integration_type)` (checks DB credential + env var fallback); enforces SciHub dual-gate
- [ ] T031 [P] [US1] Create `backend/src/backend/api/v1/studies/database_selection.py` — `GET /studies/{study_id}/database-selection` and `PUT /studies/{study_id}/database-selection` endpoints with Pydantic v2 request/response schemas per contracts/backend-api.md
- [ ] T032 [US1] Register database-selection router in `backend/src/backend/api/v1/router.py`
- [ ] T033 [P] [US1] Create `frontend/src/components/studies/DatabaseSelectionPanel/index.tsx` — functional component with named `DatabaseSelectionPanelProps` interface; shows grouped index toggles (Primary / General / Supplementary), status badges, missing-credential warnings, SciHub acknowledgment dialog; uses `useReducer` for toggle state; ≤100 JSX lines
- [ ] T034 [P] [US1] Create `frontend/src/hooks/useStudyDatabaseSelection.ts` — TanStack Query hook wrapping `GET`/`PUT` database selection API endpoints
- [ ] T035 [US1] Integrate `DatabaseSelectionPanel` into study settings view in `frontend/src/pages/studies/StudySettingsPage.tsx` (or equivalent study settings location)

**Checkpoint**: User Story 1 fully functional — multi-database search with fan-out, per-study selection UI, and merged deduplicated results.

---

## Phase 4: User Story 2 — Retrieve Full-Text Papers (Priority: P2)

**Goal**: Priority waterfall PDF retrieval (Unpaywall → direct → SciHub opt-in) with dual-gate SciHub protection.

**Independent Test**: Call `fetch_paper_pdf(doi="10.1038/s41586-021-03380-y")` and verify `available=True`, `source="unpaywall"`, and `pdf_bytes_b64` is non-empty base64 string.

### Tests for User Story 2 ⚠️ Write FIRST

- [ ] T036 [P] [US2] Write unit tests for upgraded `fetch_paper_pdf` tool covering Unpaywall success, Unpaywall miss → direct fallback, SciHub disabled guard, SciHub allowed path in `researcher-mcp/tests/unit/tools/test_pdf.py`
- [ ] T037 [P] [US2] Write integration tests for `GET /api/v1/papers/{paper_id}/markdown` endpoint in `backend/tests/integration/test_paper_markdown.py`

### Implementation for User Story 2

- [ ] T038 [P] [US2] Upgrade `researcher-mcp/src/researcher_mcp/sources/unpaywall.py` — replace any direct HTTP logic with `unpywall.Unpywall.get_pdf_link(doi)` wrapped in `asyncio.to_thread`; return structured result with `open_access_url`
- [ ] T039 [P] [US2] Upgrade `researcher-mcp/src/researcher_mcp/sources/scihub.py` — replace scraping implementation with `scidownl.scihub_download` wrapped in `asyncio.to_thread`; conditional import guarded by `scihub_enabled` setting; raise `MCPError("SciHubDisabled")` when guard fails
- [ ] T040 [US2] Upgrade `researcher-mcp/src/researcher_mcp/tools/pdf.py` — rewrite `fetch_paper_pdf` waterfall as `Unpaywall → direct URL → SciHub`; decompose into named helper functions (`_try_unpaywall`, `_try_direct`, `_try_scihub`); return `PdfFetchResult` Pydantic model
- [ ] T041 [P] [US2] Create `GET /api/v1/papers/{paper_id}/markdown` endpoint in `backend/src/backend/api/v1/papers/markdown.py` returning `PaperMarkdownResponse` (markdown, full_text_source, converted_at, available); register on papers router

**Checkpoint**: User Story 2 functional — full-text retrieval waterfall works; SciHub dual-gate enforced.

---

## Phase 5: User Story 3 — Citation and Reference Network Tracing (Priority: P3)

**Goal**: Structured citation and reference lists from Semantic Scholar (primary) with CrossRef fallback.

**Independent Test**: Call `get_references(doi="10.1145/3377811.3380376")` and receive a non-empty list of `ReferenceRecord` objects each with title and DOI where available; verify `get_citations` returns the same shape.

### Tests for User Story 3 ⚠️ Write FIRST

- [ ] T042 [P] [US3] Write unit tests for upgraded `get_references` and `get_citations` (S2 primary path, CrossRef fallback path, empty result for unknown DOI) in `researcher-mcp/tests/unit/tools/test_snowball.py`

### Implementation for User Story 3

- [ ] T043 [US3] Upgrade `get_references` in `researcher-mcp/src/researcher_mcp/tools/snowball.py` — use `AsyncSemanticScholar.get_paper_references(doi)` as primary; fall back to existing `CrossRefSource` if Semantic Scholar returns empty; map to `ReferenceRecord` with `intent` field
- [ ] T044 [US3] Upgrade `get_citations` in `researcher-mcp/src/researcher_mcp/tools/snowball.py` — use `AsyncSemanticScholar.get_paper_citations(doi)` as primary; fall back to CrossRef; map to `CitationRecord` with `citation_source` field

**Checkpoint**: User Story 3 functional — citation and reference lookups return structured `PaperRecord`-based data, not stubs.

---

## Phase 6: User Story 4 — Convert Retrieved Papers to Plain Text (Priority: P4)

**Goal**: MarkItDown-based PDF-to-Markdown conversion with stored output and optional OCR.

**Independent Test**: Call `convert_paper_to_markdown(doi="...")` (triggers internal `fetch_paper_pdf`), receive a non-empty `MarkdownConversionResult.markdown`, then call `get_paper_markdown(doi="...")` and verify the stored result is returned without re-conversion.

### Tests for User Story 4 ⚠️ Write FIRST

- [ ] T045 [P] [US4] Write unit tests for `convert_paper_to_markdown` (pdf_bytes_b64 path, url path, doi path, OCR path, conversion failure path) and `get_paper_markdown` (hit, miss) in `researcher-mcp/tests/unit/tools/test_convert.py`
- [ ] T046 [P] [US4] Write integration tests for paper markdown storage via `backend/src/backend/services/paper_service.py` in `backend/tests/integration/test_paper_markdown.py` (extends T037 file or separate)

### Implementation for User Story 4

- [ ] T047 [P] [US4] Create `researcher-mcp/src/researcher_mcp/tools/convert.py` — `convert_paper_to_markdown` and `get_paper_markdown` `@mcp.tool` functions; `MarkItDown` instantiated with optional LLM client from settings; PDF bytes wrapped in `io.BytesIO`; all `MarkItDown.convert*` calls wrapped in `asyncio.to_thread`; output persisted to `Paper.full_text_markdown` via backend API call
- [ ] T048 [US4] Register `convert_paper_to_markdown` and `get_paper_markdown` tools in `researcher-mcp/src/researcher_mcp/server.py`
- [ ] T049 [P] [US4] Add `store_paper_markdown(paper_id, markdown, source)` and `get_paper_markdown(paper_id)` methods to `backend/src/backend/services/paper_service.py` (or equivalent paper service); updates `full_text_markdown`, `full_text_source`, `full_text_converted_at` columns via SQLAlchemy async session

**Checkpoint**: User Story 4 functional — converted Markdown stored and retrievable; AI agents receive `full_text_markdown` instead of raw PDF bytes.

---

## Phase 7: User Story 5 — Administrator Credential Management (Priority: P5)

**Goal**: Admin panel Search Integrations section for managing API keys, viewing status, and running connectivity tests.

**Independent Test**: As admin, `PUT /api/v1/admin/search-integrations/ieee_xplore` with a valid key, then `POST /api/v1/admin/search-integrations/ieee_xplore/test` and receive `status: "success"`. Verify the key is never returned in plaintext in any response.

### Tests for User Story 5 ⚠️ Write FIRST

- [ ] T050 [P] [US5] Write unit tests for `CredentialService` (encrypt/decrypt round-trip, null key handling, env-var fallback detection) in `backend/tests/unit/services/test_credential_service.py`
- [ ] T051 [P] [US5] Write integration tests for admin search integrations endpoints (GET list, GET single, PUT upsert, POST test, version conflict 409, SciHub guard) in `backend/tests/integration/admin/test_search_integrations.py`
- [ ] T052 [P] [US5] Write frontend tests for `SearchIntegrationsTable` (masked key display, Test Now button, status badges, edit flow) in `frontend/src/components/admin/SearchIntegrationsTable/SearchIntegrationsTable.test.tsx`

### Implementation for User Story 5

- [ ] T053 [P] [US5] Create `backend/src/backend/services/credential_service.py` — `CredentialService` with `get_credential(integration_type)`, `upsert_credential(integration_type, api_key, auxiliary_token, config_json)`, `get_effective_key(integration_type)` (DB first, env-var fallback), `run_connectivity_test(integration_type)` methods; Fernet encryption reusing pattern from `Provider` model
- [ ] T054 [P] [US5] Create `backend/src/backend/api/v1/admin/search_integrations.py` — `GET /admin/search-integrations`, `GET /admin/search-integrations/{type}`, `PUT /admin/search-integrations/{type}`, `POST /admin/search-integrations/{type}/test` endpoints; requires `GroupRole.ADMIN`; never exposes raw key bytes
- [ ] T055 [US5] Register `search_integrations` router in `backend/src/backend/api/v1/admin/router.py`
- [ ] T056 [P] [US5] Create `frontend/src/hooks/useSearchIntegrations.ts` — TanStack Query hooks for list, single, upsert mutation, and test mutation
- [ ] T057 [P] [US5] Create `frontend/src/components/admin/SearchIntegrationsTable/index.tsx` — table with database name, status badge, access type, masked key indicator, Last Tested timestamp, Test Now button, edit modal; named `SearchIntegrationsTableProps` interface; ≤100 JSX lines per component
- [ ] T058 [US5] Extend `frontend/src/pages/admin/AdminPage.tsx` (or equivalent admin page) with a **Search Integrations** tab that renders `SearchIntegrationsTable`

**Checkpoint**: User Story 5 functional — admin can manage all integration credentials from the UI without touching env vars.

---

## Phase 8: User Story 6 — Author Search and Profile Lookup (Priority: P6)

**Goal**: Author search by name/institution and full paper list retrieval by author profile ID, via Semantic Scholar.

**Independent Test**: Call `search_author_semantic_scholar(name="Leslie Lamport")` and receive at least one `AuthorProfile` with a non-empty `author_id`; then call `get_author_semantic_scholar(author_id="...")` and receive an `AuthorDetail` with a non-empty `papers` list.

### Tests for User Story 6 ⚠️ Write FIRST

- [ ] T059 [P] [US6] Write unit tests for `search_author_semantic_scholar` and `get_author_semantic_scholar` (mocked `AsyncSemanticScholar`, empty-result path) in `researcher-mcp/tests/unit/tools/test_authors.py`

### Implementation for User Story 6

- [ ] T060 [P] [US6] Upgrade `researcher-mcp/src/researcher_mcp/sources/semantic_scholar.py` — add `search_author(name, institution)` and `get_author(author_id)` async methods to `SemanticScholarSource` using `AsyncSemanticScholar.search_author()` and `get_author_papers()`; map to `AuthorProfile` / `AuthorDetail` Pydantic models
- [ ] T061 [US6] Upgrade `researcher-mcp/src/researcher_mcp/tools/authors.py` — replace existing stub implementations with `SemanticScholarSource` calls; add `search_author_semantic_scholar` and `get_author_semantic_scholar` `@mcp.tool` functions returning `AuthorProfile` / `AuthorDetail`

**Checkpoint**: User Story 6 functional — author search and paper list retrieval work end-to-end via Semantic Scholar.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Coverage validation, type checking, linting, and end-to-end verification.

- [ ] T062 [P] Run full researcher-mcp test suite with coverage: `uv run --package sms-researcher-mcp pytest researcher-mcp/tests/ --cov=src/researcher_mcp --cov-fail-under=85 --cov-report=term-missing`; fix any gaps
- [ ] T063 [P] Run full backend and db test suites with coverage: `uv run --package sms-backend pytest backend/tests/ --cov=src/backend --cov-fail-under=85`; `uv run --package sms-db pytest db/tests/ --cov=src/db --cov-fail-under=85`; fix any gaps
- [ ] T064 [P] Run frontend test suite with coverage: `cd frontend && npm run test:coverage`; confirm 85% threshold enforced in `vite.config.ts`; fix any gaps
- [ ] T065 [P] Run `mypy --strict` across all modified Python packages (`researcher-mcp/src`, `backend/src`, `db/src`); resolve all type errors
- [ ] T066 [P] Run `ruff check` and `ruff format --check` across all modified Python source directories; resolve all violations
- [ ] T067 [P] Run Playwright e2e tests covering: database selection in study settings, SciHub acknowledgment flow, admin Search Integrations table (add key, test connectivity) in `frontend/e2e/`

---

## Phase 10: Feature Completion Documentation *(mandatory — Constitution Principle X)*

**Purpose**: Update all required documentation before the feature branch is merged.

> **These tasks MUST be completed before the feature is marked done. Omitting them is a blocking violation of Constitution Principle X.**

- [ ] TDOC1 [P] Update `CLAUDE.md` at repository root — add feature 006 entry to Active Technologies and Recent Changes sections; document new env vars and researcher-mcp library additions
- [ ] TDOC2 [P] Update `README.md` at repository root — document new database search capabilities, full-text retrieval, and admin credential management panel
- [ ] TDOC3 [P] Update `CHANGELOG.md` at repository root — add new entry under `[Unreleased]` describing all additions (database integrations, MCP tools, PDF retrieval, Markdown conversion, admin UI)
- [ ] TDOC4 [P] Update `README.md` in each modified subproject: `researcher-mcp/README.md`, `backend/README.md`, `db/README.md`, `frontend/README.md`
- [ ] TDOC5 [P] Update `CHANGELOG.md` in each modified subproject with same level of detail as root entry

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user story phases
- **Phase 3–8 (User Stories)**: All depend on Phase 2 completion; can proceed in priority order or in parallel
- **Phase 9 (Polish)**: Depends on all desired user stories being complete
- **Phase 10 (TDOC)**: Depends on Phase 9 completion

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 2 only — no cross-story dependencies
- **US2 (P2)**: Depends on Phase 2 only — PDF retrieval is independent of database search
- **US3 (P3)**: Depends on Phase 2 only — Semantic Scholar upgrade is independent
- **US4 (P4)**: Depends on US2 (fetch_paper_pdf used internally by convert tool)
- **US5 (P5)**: Depends on Phase 2 only — credential service is independent
- **US6 (P6)**: Depends on Phase 2 only — author tools are independent

### Within Each User Story

- Test tasks must be written and confirmed failing before their corresponding implementation task
- Source classes (T016–T023) before SourceRegistry update (T024)
- SourceRegistry update (T024) before fan-out upgrade (T025)
- Backend service (T030) before backend endpoint (T031)
- Backend endpoint (T031) before frontend hook (T034)
- Frontend component (T033) and hook (T034) before page integration (T035)

### Parallel Opportunities

Within Phase 2: T003, T006, T007, T008, T009 all touch different files — run in parallel.
Within Phase 3 (US1): T011–T015 (tests) all parallel; T016–T023 (source classes) all parallel; T026–T029 (per-source tools) parallel after T025.
Within Phase 7 (US5): T050–T052 (tests) parallel; T053 and T056–T057 parallel after tests written.

---

## Parallel Example: User Story 1

```bash
# Write all US1 tests in parallel (before implementation):
Task T011: researcher-mcp/tests/unit/core/test_dedup.py
Task T012: researcher-mcp/tests/unit/core/test_registry.py
Task T013: researcher-mcp/tests/unit/tools/test_search.py
Task T014: backend/tests/integration/test_database_selection.py
Task T015: frontend/src/components/studies/DatabaseSelectionPanel/DatabaseSelectionPanel.test.tsx

# After tests confirmed failing — implement all source classes in parallel:
Task T016: sources/ieee.py
Task T017: sources/acm.py
Task T018: sources/google_scholar.py
Task T019: sources/inspec.py
Task T020: sources/scopus.py
Task T021: sources/wos.py
Task T022: sources/science_direct.py
Task T023: sources/springer.py

# After T016–T023 complete:
Task T024: Register in registry.py
→ Task T025: Upgrade search_papers fan-out

# After T025 — parallel tool additions:
Task T026: search_ieee, get_ieee_paper tools
Task T027: search_acm, search_google_scholar, search_inspec tools
Task T028: search_scopus, get_scopus_paper, search_wos, search_sciencedirect, search_springer tools
Task T029: search_semantic_scholar, get_paper_semantic_scholar tools

# Backend + frontend in parallel (after T025):
Task T030: database_selection.py service
Task T033: DatabaseSelectionPanel component
→ Task T031: database_selection.py endpoint (after T030)
→ Task T034: useStudyDatabaseSelection.ts hook (after T031)
→ Task T032: register router (after T031)
→ Task T035: page integration (after T033 + T034)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (multi-database search + study selection UI)
4. **STOP and VALIDATE**: Run `search_papers` across 3 indices; verify merged results and study selection persists
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 → Multi-database search (MVP)
3. US2 → Full-text PDF retrieval
4. US3 → Citation/reference snowball sampling
5. US4 → Paper-to-Markdown conversion
6. US5 → Admin credential management
7. US6 → Author search

### Parallel Team Strategy

With multiple developers, after Phase 2 completes:
- Developer A: US1 (database search + UI)
- Developer B: US2 + US3 (full-text + citations) → US4 (conversion)
- Developer C: US5 (admin credentials)

---

## Notes

- [P] tasks = different files, no incomplete task dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing (TDD order within each story phase)
- Commit after each logical group; refactoring commits must be separate from feature commits
- Stop at each phase checkpoint to validate the story independently
- `asyncio.to_thread()` is mandatory for pybliometrics, scholarly, unpywall, markitdown, scidownl, springernature-api-client (Constitution Principle IX async discipline)
- `scidownl` must be a conditional import guarded by `SCIHUB_ENABLED` — never imported at module level unconditionally
- All new Python classes/functions must have Google-style docstrings with `Args:`, `Returns:`, `Raises:` (Constitution Principle III)
- All exported TypeScript symbols must have JSDoc comments (Constitution Principle III)
- New DB models (`StudyDatabaseSelection`, `SearchIntegrationCredential`) must have `created_at`/`updated_at` audit fields and `SearchIntegrationCredential` must use optimistic locking via `version_id` (Constitution Principle VIII)
- All Pydantic schemas are v2 (`model_config`, `model_validator`, not v1 validators)
- API keys are never returned in plaintext — only `has_api_key: bool` or `configured_via: str` in responses
- React components: functional only, named `Props` interface, ≤100 JSX lines; SciHub acknowledgment uses `useWatch` not `watch`; database toggle state uses `useReducer` (>3 related state values)
