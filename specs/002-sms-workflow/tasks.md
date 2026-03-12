# Tasks: Systematic Mapping Study Workflow System

**Input**: Design documents from `/specs/002-sms-workflow/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓
**Constitution**: Aligned to v1.4.0 — includes refactoring tasks for compliance violations and new tasks for FR-044/045/046.

**Tests**: Included — Constitution v1.4.0 Principle VI mandates unit tests per module, integration tests per router, metamorphic tests per agent, deepeval pipelines per agent, and mutation testing (mutmut/Stryker). Test tasks are marked **[T]** in addition to any [P] marker.

**Organization**: Tasks grouped by user story for independent implementation and testing.

> **Terminology note**: "Phase N" in this task list refers to *implementation phases*. The SMS study workflow phases 1–5 are referred to as "SMS Phase N" throughout to avoid confusion.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story this task belongs to (US1–US7)

---

## Refactoring Tasks (Pre-feature, required by Constitution)

**Three BLOCKING violations identified in already-implemented code. These MUST be resolved
before any remaining unchecked tasks are started (Constitution Principle IV).**

### BLOCKING — Principle III: run_full_search / run_snowball exceed 20-line limit

- [ ] TREF1 Write unit tests covering the current behavior of `run_full_search()` and `run_snowball()` in `backend/tests/unit/test_search_job.py` before any refactoring begins (Principle IV: test-first refactoring prerequisite)
- [ ] TREF2 Decompose `run_full_search()` (~334 lines) in `backend/src/backend/jobs/search_job.py` into focused helpers: `_fetch_database_results()`, `_process_single_candidate()`, `_run_screening_pass()`, `_finalize_search_metrics()` — each ≤20 lines; no function mixes DB access with screening logic
- [ ] TREF3 Decompose `run_snowball()` (~243 lines) in `backend/src/backend/jobs/search_job.py` into `_fetch_snowball_papers()` and `_process_snowball_batch()` helpers — each ≤20 lines; threshold-check logic extracted to `_snowball_threshold_reached()`

### BLOCKING — Principle VII: Wrong logging module in search_job.py

- [ ] TREF4 [P] Replace `import logging; logger = logging.getLogger(__name__)` with structlog in `backend/src/backend/jobs/search_job.py` — add `from backend.core.config import get_logger; logger = get_logger(__name__)` and update all `logger.info`/`warning`/`error` calls to use bound-logger context binding (Principle VII — structlog is the only approved logger)

### MINOR — Principle VIII: Hardcoded secret_key default in config.py

- [ ] TREF5 [P] Replace `secret_key: str = "dev-secret-key-change-in-production"` with `secret_key: str = ""` in `backend/src/backend/core/config.py` to match the `anthropic_api_key` pattern (Principle VIII — no hardcoded secrets in code, even as defaults)

### BLOCKING — Principle II: Duplicated study-membership guard across 8 router files

- [ ] TREF6 Centralize the study-membership auth guard as `async def require_study_member(study_id: int, current_user: CurrentUser, db: AsyncSession) -> None` raising `HTTP 403` (not `404`) for non-members in `backend/src/backend/core/auth.py`; write unit test in `backend/tests/unit/test_auth.py` covering the 403 path before refactoring (Principle IV: test-first); then replace the 8 existing private `_require_study_member` duplicates in `pico.py`, `seeds.py`, `criteria.py`, `search_strings.py`, `searches.py`, `papers.py`, `jobs.py`, `metrics.py` with a single import of the shared guard; also apply to `extractions.py`, `results.py`, `quality.py`, `validity.py`, `audit.py` when those routers are created — this corrects a DRY violation AND a behavioral difference (403 vs 404) that affects client error handling (Principle II — DRY; Principle V — Protected Variation)

> **Checkpoint**: All TREF tasks complete → constitution blocking violations resolved → continue with Phase 3+ unchecked tasks.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add new dependencies and infrastructure needed by all user stories.

- [x] T001 Add ARQ, redis, matplotlib, networkx, plotly, kaleido, rapidfuzz to `backend/pyproject.toml` dependencies
- [x] T002 [P] Add react-router-dom, @tanstack/react-query, react-hook-form, zod, recharts, d3, @types/d3, diff to `frontend/package.json` dependencies
- [x] T003 [P] Add Redis service to `docker-compose.yml` (port 6379) and `docker-compose_2.yml`
- [x] T004 Extend `backend/src/backend/core/config.py` with Redis URL, ARQ worker, LLM model/API key, researcher-mcp URL settings
- [x] T005 [P] Add ARQ worker entrypoint `backend/src/backend/jobs/worker.py` (imports job modules, defines `WorkerSettings` with Redis DSN from config)
- [x] T006 [P] Create `backend/src/backend/jobs/__init__.py` and `backend/src/backend/services/__init__.py`

**Checkpoint**: Infrastructure dependencies and config in place.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Auth, User/Group data model, Study extensions, and core API skeleton that ALL user stories require.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Authentication

- [x] T007 Implement `POST /api/v1/auth/login` and `GET /api/v1/auth/me` endpoints in `backend/src/backend/api/v1/auth.py` using existing JWT logic from `backend/src/backend/core/auth.py`
- [x] T008 Add `get_current_user` FastAPI dependency in `backend/src/backend/core/auth.py` that validates Bearer JWT and returns user ID

### User & Group Models (Migration 1)

- [x] T009 Create `db/src/db/models/users.py` with `User` (id, email, hashed_password, display_name, created_at, last_login_at) and `ResearchGroup` (id, name, created_at) and `GroupMembership` (group_id FK, user_id FK, role Enum admin/member, joined_at) models
- [x] T010 Create Alembic migration `db/alembic/versions/0002_users_and_groups.py` for User, ResearchGroup, GroupMembership tables
- [x] T011 Add bcrypt password hashing helper to `backend/src/backend/core/auth.py` (hash_password, verify_password functions)

### Study Extensions (Migration 2)

- [x] T012 Extend `db/src/db/models.py` Study model: add topic (Text), motivation (Text nullable), current_phase (SmallInt default 1), research_group_id (FK ResearchGroup), snowball_threshold (SmallInt default 5); add StudyMember (study_id FK, user_id FK, role Enum lead/member, joined_at) and Reviewer (id, study_id FK, reviewer_type Enum human/ai_agent, user_id FK nullable, agent_name nullable, agent_config JSON nullable) models to `db/src/db/models/study.py`
- [x] T013 Create Alembic migration `db/alembic/versions/0003_study_extensions.py` for Study new columns, StudyMember, Reviewer tables
- [x] T014 Update `db/src/db/__init__.py` to export all new model modules

### Research Groups API

- [x] T015 Implement `GET /api/v1/groups`, `POST /api/v1/groups` in `backend/src/backend/api/v1/groups.py`
- [x] T016 [P] Implement `GET /api/v1/groups/{group_id}/members`, `POST /api/v1/groups/{group_id}/members`, `DELETE /api/v1/groups/{group_id}/members/{user_id}` in `backend/src/backend/api/v1/groups.py`

### Core API Router

- [x] T017 Register auth, groups routers in `backend/src/backend/api/v1/router.py`

### Frontend Foundation

- [x] T018 Add React Router with routes (/, /login, /groups, /groups/:groupId/studies, /studies/:studyId) in `frontend/src/main.tsx` and `frontend/src/App.tsx`
- [x] T019 [P] Create `frontend/src/services/api.ts` typed fetch wrapper with Bearer token injection and JSON error handling
- [x] T020 [P] Create `frontend/src/services/auth.ts` session management (store/read/clear JWT, current user state)
- [x] T021 Create `frontend/src/components/auth/LoginPage.tsx` (left-1/3 login form, right-2/3 product infographic, redirects to /groups on success)
- [x] T022 [P] Create `frontend/src/components/layout/AppShell.tsx` (side nav with avatar, Research Groups button, phase nav for active study) and `frontend/src/components/layout/SideNav.tsx`
- [x] T023 Create `frontend/src/components/groups/GroupsPage.tsx` and `GroupCard.tsx` (lists user's research groups, navigates to selected group's studies)

### Testing: Phase 2 Modules (Constitution Principle VI)

- [ ] T141 [P] [T] Write unit tests in `backend/tests/unit/test_auth.py` covering `get_current_user`, `hash_password`, `verify_password`, `require_study_member` (TREF6); write integration tests in `backend/tests/integration/test_auth_router.py` and `test_groups_router.py` covering all `/auth/*` and `/groups/*` endpoints including 401/403 error paths
- [ ] T143 [P] [T] Write unit tests for `db/src/db/models/users.py` and `db/src/db/models/study.py` extensions in `db/tests/test_models_users.py` and `db/tests/test_models_study.py` — verify FK constraints, Enum validation, and timestamp defaults

**Checkpoint**: Auth, groups, study model extended, router wired — user story work can begin in parallel.

---

## Phase 3: User Story 1 — Researcher Creates and Scopes a New Study (Priority: P1) 🎯 MVP

**Goal**: Researcher can log in, select a group, create a study via the wizard with PICO/C and reviewer config, add seed papers/authors, and use Librarian/Expert AI agents.

**Independent Test**: Log in → create a research group → complete New Study Wizard (name, SMS type, PICO/C, 1 reviewer) → study appears in list at Phase 1; Librarian agent returns suggestions.

### PICO/C & Seed Models (Migration 3)

- [x] T024 [P] [US1] Create `db/src/db/models/pico.py` with PICOComponent (id, study_id FK, variant Enum PICO/PICOS/PICOT/SPIDER/PCC, population/intervention/comparison/outcome/context Text nullable, extra_fields JSON nullable, ai_suggestions JSON nullable, updated_at)
- [x] T025 [P] [US1] Create `db/src/db/models/seeds.py` with SeedPaper (id, study_id FK, paper_id FK, added_by_user_id FK nullable, added_by_agent nullable, created_at) and SeedAuthor (id, study_id FK, author_name, institution nullable, profile_url nullable, added_by_user_id FK nullable, added_by_agent nullable, created_at)
- [x] T026 [US1] Create Alembic migration `db/alembic/versions/0004_pico_and_seeds.py` for PICOComponent, SeedPaper, SeedAuthor tables

### AI Agents: Librarian & Expert

- [x] T027 [P] [US1] Create Jinja2 prompt templates `agents/src/agents/prompts/librarian/system.jinja2` and `user.jinja2` for seed paper and author suggestions *(note: T178 will rename these to the approved `system.md` / `user.md.j2` convention — Principle VII)*
- [x] T028 [P] [US1] Create Jinja2 prompt templates `agents/src/agents/prompts/expert/system.jinja2` and `user.jinja2` for 10–20 high-confidence relevant papers *(note: T178 will rename these to the approved `system.md` / `user.md.j2` convention — Principle VII)*
- [x] T029 [P] [US1] Implement `LibrarianAgent` in `agents/src/agents/services/librarian.py` using LLMClient + PromptLoader; returns structured `{papers: [...], authors: [...]}` Pydantic model
- [x] T030 [US1] Implement `ExpertAgent` in `agents/src/agents/services/expert.py`; returns structured list of up to 20 papers with title, authors, year, venue, rationale fields

### Study & PICO API

- [x] T031 [US1] Implement study CRUD in `backend/src/backend/api/v1/studies.py`: `GET /groups/{group_id}/studies`, `POST /groups/{group_id}/studies` (wizard payload: name, type, motivation, objectives, questions, member_ids, reviewers, snowball_threshold), `GET /studies/{study_id}`, `PATCH /studies/{study_id}`, `POST /studies/{study_id}/archive`, `DELETE /studies/{study_id}`
- [x] T032 [US1] Add phase-gate unlock logic as a service helper in `backend/src/backend/services/phase_gate.py` (checks PICO saved → unlocks phase 2; search complete → unlocks phase 3; extraction complete → unlocks 4/5)
- [x] T033 [US1] Implement PICO/C endpoints in `backend/src/backend/api/v1/pico.py`: `GET /studies/{study_id}/pico`, `PUT /studies/{study_id}/pico` (saves PICOComponent, calls phase_gate), `POST /studies/{study_id}/pico/refine` (calls LibrarianAgent for component suggestions)
- [x] T034 [US1] Implement seed endpoints in `backend/src/backend/api/v1/seeds.py`: `GET/POST/DELETE /studies/{study_id}/seeds/papers`, `GET/POST /studies/{study_id}/seeds/authors`, `POST /studies/{study_id}/seeds/librarian` (enqueues LibrarianAgent job)
- [ ] T166 [US1] Add `POST /studies/{study_id}/seeds/expert` endpoint in `backend/src/backend/api/v1/seeds.py`: enqueues a BackgroundJob that calls `ExpertAgent` with the study's topic, motivation, and research questions; on completion, inserts the returned papers as `SeedPaper` records (with `added_by_agent="expert"`) and stores the full `ExpertAgent` response as job progress detail for frontend display — satisfies FR-014 (ExpertAgent was implemented in T030 but had no API surface)
- [x] T035 [US1] Register studies, pico, seeds routers in `backend/src/backend/api/v1/router.py`

### Frontend: Study Wizard & Phase 1 UI

- [x] T036 [US1] Create `frontend/src/pages/StudiesPage.tsx` (lists studies for selected group with name, topic, type, current_phase/status, archive/delete actions)
- [x] T037 [US1] Create `frontend/src/components/studies/NewStudyWizard.tsx` — multi-step wizard: (1) Name+Type, (2) Assign members, (3) Configure reviewers (add human or AI agent), (4) Motivation+Objectives+Questions, (5) PICO/C form with variant selector
- [x] T038 [P] [US1] Create `frontend/src/components/phase1/PICOForm.tsx` with variant selector (PICO/PICOS/PICOT/SPIDER/PCC), text areas per component, "Refine with AI" button calling `/pico/refine`
- [x] T039 [P] [US1] Create `frontend/src/components/phase1/SeedPapers.tsx` (add/remove seed papers by DOI or manual entry, trigger Librarian agent, show suggestions list)
- [ ] T167 [P] [US1] Add Expert agent UI to `frontend/src/components/phase1/SeedPapers.tsx`: "Find with Expert AI" button that calls `POST /seeds/expert` and displays a `JobProgressPanel` while running; on completion renders the returned papers as a selectable suggestion list alongside the Librarian suggestions, allowing researchers to add any Expert-suggested paper as a SeedPaper with one click — satisfies FR-014 frontend surface (depends on T166)
- [x] T040 [US1] Create `frontend/src/pages/StudyPage.tsx` as phase router (renders phase 1–5 tabs based on `unlocked_phases`, shows current progress)

### Testing: Phase 3 (US1) Modules (Constitution Principle VI)

- [ ] T144 [P] [T] Write unit tests for `LibrarianAgent` and `ExpertAgent` in `agents/tests/unit/test_librarian.py` and `test_expert.py` (mock LLMClient; verify Pydantic output shape and non-empty suggestions); write integration tests in `backend/tests/integration/test_studies_router.py`, `test_pico_router.py`, `test_seeds_router.py` covering wizard POST, PICO PUT/refine, seed CRUD, 404 paths, and `POST /seeds/expert` 202 response + SeedPaper insertion (T166)
- [ ] T145 [P] [T] Write Vitest + Testing Library tests for `NewStudyWizard.tsx`, `PICOForm.tsx`, `SeedPapers.tsx` in `frontend/src/components/studies/__tests__/` and `frontend/src/components/phase1/__tests__/` — verify step navigation, form validation errors, and API mock call shapes
- [ ] T162 [P] [T] Add deepeval evaluation pipelines for `LibrarianAgent` in `agent-eval/src/agent_eval/evals/librarian_eval.py` and `ExpertAgent` in `agent-eval/src/agent_eval/evals/expert_eval.py` — define representative input datasets, output criteria (non-empty paper suggestions, no hallucinated DOIs), and pass/fail thresholds (Constitution Principle VI — deepeval MUST be added when agent is first created)

**Checkpoint**: Full US1 flow functional — wizard, PICO/C, seed management, Librarian suggestions.

---

## Phase 4: User Story 2 — Researcher Builds and Evaluates a Search String (Priority: P2)

**Goal**: Researcher defines inclusion/exclusion criteria, generates a PICO/C-based search string, tests it against seed papers, iterates, and approves it for full search.

**Independent Test**: Open Phase 2 of a study with PICO/C saved → generate search string → run test search against one DB → view recall against seed test set → approve iteration; Phase 3 remains locked.

### Criteria & Search Models (Migration 4)

- [x] T041 [P] [US2] Create `db/src/db/models/criteria.py` with InclusionCriterion (id, study_id FK, description Text, order_index SmallInt, created_at) and ExclusionCriterion (same shape)
- [x] T042 [P] [US2] Create `db/src/db/models/search.py` with SearchString (id, study_id FK, version SmallInt, string_text Text, is_active Boolean, created_at, created_by_user_id FK nullable, created_by_agent nullable) and SearchStringIteration (id, search_string_id FK, iteration_number SmallInt, result_set_count Integer, test_set_recall Float, ai_adequacy_judgment Text nullable, human_approved Boolean nullable, created_at)
- [x] T043 [US2] Create Alembic migration `db/alembic/versions/0005_criteria_and_search.py` for InclusionCriterion, ExclusionCriterion, SearchString, SearchStringIteration tables

### Search String Builder Agent

- [x] T044 [P] [US2] Create Jinja2 prompt templates `agents/src/agents/prompts/search_builder/system.jinja2` and `user.jinja2` (generates Boolean search string from PICO/C + keywords + synonyms/thesaurus expansion) *(note: T178 will rename these to the approved `system.md` / `user.md.j2` convention — Principle VII)*
- [x] T045 [US2] Implement `SearchStringBuilderAgent` in `agents/src/agents/services/search_builder.py`; accepts PICOComponent dict + seed keywords, returns `{search_string: str, terms_used: [...], expansion_notes: str}` Pydantic model

### Search String & Criteria API

- [x] T046 [US2] Implement criteria endpoints in `backend/src/backend/api/v1/criteria.py`: `GET/POST/DELETE /studies/{study_id}/criteria/inclusion` and `GET/POST/DELETE /studies/{study_id}/criteria/exclusion`
- [x] T047 [US2] Implement search string endpoints in `backend/src/backend/api/v1/search_strings.py`: `GET /studies/{study_id}/search-strings`, `POST /studies/{study_id}/search-strings` (manual), `POST /studies/{study_id}/search-strings/generate` (calls SearchStringBuilderAgent, creates SearchString + first iteration comparing against seed test set),
- [x] T048 [US2] Add `POST /studies/{study_id}/search-strings/{id}/test` endpoint that enqueues a test-search ARQ job in `backend/src/backend/api/v1/search_strings.py`
- [ ] T172 [US2] Add `PATCH /studies/{study_id}/search-strings/{id}/iterations/{iter_id}` endpoint in `backend/src/backend/api/v1/search_strings.py`: accepts `{human_approved: bool}` body; sets `SearchStringIteration.human_approved`; when `human_approved=true` also sets `SearchString.is_active=true` and records an AuditRecord (entity_type="SearchString", action="update", field_name="is_active", after_value=true); returns 404 if the iteration does not belong to the given search string — satisfies FR-022 acceptance scenario 5 ("saved as the study's official search string, locked for the record")
- [x] T049 [US2] Implement test-search ARQ job in `backend/src/backend/jobs/search_job.py` (calls researcher-mcp `search_papers` with the string against selected DBs, computes recall against SeedPaper test set, creates SearchStringIteration, stores result) — ⚠️ **FR-027a compliance**: MUST create a `BackgroundJob` record at job start (status=running) and update it to completed/failed on exit, so users can navigate away and return to monitor progress via `GET /jobs/{job_id}/progress` SSE stream; `T048` must return the BackgroundJob `job_id` alongside the enqueue confirmation
- [x] T050 [US2] Register criteria and search_strings routers in `backend/src/backend/api/v1/router.py`

### Frontend: Phase 2 UI

- [x] T051 [US2] Create `frontend/src/components/phase2/CriteriaForm.tsx` (add/remove inclusion and exclusion criteria with order drag-reorder)
- [x] T052 [P] [US2] Create `frontend/src/components/phase2/SearchStringEditor.tsx` (text area for search string, "Generate with AI" button, version history list)
- [x] T053 [P] [US2] Create `frontend/src/components/phase2/TestRetest.tsx` (trigger test search, show iteration results: recall %, result count, AI adequacy judgment, approve/reject button)

### Testing: Phase 4 (US2) Modules (Constitution Principle VI)

- [ ] T146 [P] [T] Write unit tests for `SearchStringBuilderAgent` in `agents/tests/unit/test_search_builder.py` (mock LLMClient; verify boolean string output non-empty, terms_used present); write integration tests in `backend/tests/integration/test_criteria_router.py` and `test_search_strings_router.py` covering criteria CRUD, generate endpoint, test endpoint 202 response, iteration approval PATCH
- [ ] T147 [P] [T] Write Vitest + Testing Library tests for `CriteriaForm.tsx`, `SearchStringEditor.tsx`, `TestRetest.tsx` in `frontend/src/components/phase2/__tests__/` — verify add/remove criterion interactions, generate button call, iteration recall display and approval button
- [ ] T163 [P] [T] Add deepeval evaluation pipeline for `SearchStringBuilderAgent` in `agent-eval/src/agent_eval/evals/search_builder_eval.py` — define dataset of PICO inputs + seed keywords, output criteria (valid boolean syntax, non-empty terms_used, synonym expansion evidence), pass/fail threshold (Constitution Principle VI — deepeval MUST be added when agent is first created)

**Checkpoint**: Full US2 flow functional — criteria, search string generation, test-retest, iteration approval.

---

## Phase 5: User Story 3 — System Executes Full Paper Search with Snowball Sampling (Priority: P3)

**Goal**: Full search pipeline: execute across databases, deduplicate, AI screen against criteria, iterative snowball sampling until threshold, all tracked with phase tags and search metrics.

**Independent Test**: Trigger full search on a study with approved search string → monitor progress dashboard → view candidate paper list with A/R/D decisions and phase tags; search metrics show counts per phase.

### Candidate Paper & Job Models (Migrations 5 & 7)

- [x] T054 [P] [US3] Extend `db/src/db/models.py` Paper model: add authors JSON, year SmallInt nullable, venue String nullable, source_url Text nullable, full_text_available Boolean default False
- [x] T055 [P] [US3] Create `db/src/db/models/search_exec.py` with SearchExecution (id, study_id FK, search_string_id FK, status Enum pending/running/completed/failed, phase_tag String, databases_queried JSON, started_at nullable, completed_at nullable, job_id String nullable) and SearchMetrics (id, search_execution_id FK unique, total_identified Integer, accepted Integer, rejected Integer, duplicates Integer, computed_at)
- [x] T056 [P] [US3] Create `db/src/db/models/candidate.py` with CandidatePaper (id, study_id FK, paper_id FK, search_execution_id FK, phase_tag String, current_status Enum pending/accepted/rejected/duplicate, duplicate_of_id FK nullable, version_id Integer, created_at, updated_at; `__mapper_args__ = {"version_id_col": version_id}`; unique constraint study_id+paper_id) and PaperDecision (id, candidate_paper_id FK, reviewer_id FK, decision Enum, reasons JSON, is_override Boolean, overrides_decision_id FK nullable, created_at)
- [x] T057 [P] [US3] Create `db/src/db/models/jobs.py` with BackgroundJob (id String PK, study_id FK, job_type Enum full_search/snowball_search/batch_extraction/quality_eval, status Enum queued/running/completed/failed, progress_pct SmallInt, progress_detail JSON, error_message Text nullable, queued_at, started_at nullable, completed_at nullable)
- [x] T058 [US3] Create Alembic migration `db/alembic/versions/0006_candidate_papers.py` for SearchExecution, CandidatePaper, PaperDecision, BackgroundJob, SearchMetrics tables and Paper column extensions

### NFR-001 Audit Timestamp Compliance + AuditRecord Model (Migrations 9a & 9b)

> These tasks address Constitution v1.2.0 Principle VIII (every model MUST have created_at +
> updated_at) and add the AuditRecord model required by FR-044. They MUST precede Phase 7
> (US5) to ensure the migration is applied before extraction models are created.

- [ ] T120 [P] Add `updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())` to `SearchString` in `db/src/db/models/search.py`; add `created_at: Mapped[datetime]` to `PICOComponent` in `db/src/db/models/pico.py` (NFR-001)
- [ ] T121 [P] Add `updated_at` to `InclusionCriterion` and `ExclusionCriterion` in `db/src/db/models/criteria.py`; add `created_at` and `updated_at` columns to `SearchExecution` in `db/src/db/models/search_exec.py`; add `updated_at` to `BackgroundJob` in `db/src/db/models/jobs.py` and `SearchMetrics` in `db/src/db/models/search_exec.py` (NFR-001)
- [ ] T122 [P] Create `db/src/db/models/audit.py` with `AuditRecord` (id, study_id FK, actor_user_id FK nullable, actor_agent String nullable, entity_type String(64), entity_id Integer, action Enum create/update/delete, field_name String nullable, before_value JSON nullable, after_value JSON nullable, created_at; composite indexes on `(study_id, created_at DESC)` and `(entity_type, entity_id)`; append-only — no `updated_at`) (FR-044, NFR-002)
- [ ] T123 Create Alembic migration `db/alembic/versions/0010_audit_trail_and_updated_at.py` covering: AuditRecord table creation + all missing `updated_at`/`created_at` column additions from T120–T122 — use `revision = "0010"`, `down_revision = "0009"` (chaining after T093's results migration)
- [ ] T124 [P] Export `AuditRecord` from `db/src/db/__init__.py` alongside existing model exports

### researcher-mcp: Snowball & Scraper Tools

- [x] T059 [P] [US3] Implement `get_references(doi, max_results)` tool in `researcher-mcp/src/researcher_mcp/tools/snowball.py` (fetches paper reference list via OpenAlex/Semantic Scholar API)
- [x] T060 [P] [US3] Implement `get_citations(doi, max_results)` tool in `researcher-mcp/src/researcher_mcp/tools/snowball.py` (fetches citing papers)
- [x] T061 [P] [US3] Implement `scrape_journal(journal_url, year_from, year_to, max_results)` and `scrape_author_page(profile_url, max_results)` in `researcher-mcp/src/researcher_mcp/tools/scraper.py`
- [x] T062 [US3] Register new tools in `researcher-mcp/src/researcher_mcp/server.py`

### Paper Deduplication & Screener Extension

- [ ] T063 [US3] Implement `backend/src/backend/services/dedup.py`: two-stage dedup — (1) exact DOI match against existing CandidatePapers for study, (2) rapidfuzz title similarity ≥ 0.90 + author overlap → probable duplicate flagged for review; returns `DedupResult(is_duplicate, definite, candidate_id_if_dup)`
- [ ] T064 [US3] Extend `ScreenerAgent` in `agents/src/agents/services/screener.py` to accept structured InclusionCriterion/ExclusionCriterion lists and return `ScreeningResult(decision: accepted/rejected/duplicate, reasons: [{criterion_id, type, text}])` Pydantic model

### Full Search & Snowball ARQ Jobs

- [x] T065 [US3] Implement full search ARQ job `run_full_search(study_id, search_execution_id)` in `backend/src/backend/jobs/search_job.py`: (1) query each database via researcher-mcp `search_papers`, (2) dedup each result, (3) create CandidatePaper records, (4) call ScreenerAgent for each candidate, (5) create PaperDecision records, (6) update SearchMetrics, (7) write progress to BackgroundJob; writes progress_detail `{phase, database, papers_found, screened}` on each step — ⚠️ **GAP**: step (8) `Study.current_phase` not updated after completion (see T065b)
- [ ] T065b [US3] After committing `SearchExecution.status = COMPLETED` in `run_full_search()`, call `new_phase = await compute_current_phase(study_id, db)` (import from `backend.services.phase_gate`) and update `study.current_phase = max(study.current_phase, new_phase)` before final `db.commit()` — mirrors the pattern in `backend/src/backend/api/v1/pico.py` lines 202–206
- [x] T066 [US3] Implement snowball ARQ job `run_snowball(study_id, phase_tag, paper_dois, direction)` in `backend/src/backend/jobs/search_job.py`: calls `get_references` or `get_citations` via MCP client, deduplicates against existing candidates, screens new papers, updates SearchMetrics, stops if new non-duplicate count < snowball_threshold
- [x] T067 [US3] Add `POST /studies/{study_id}/searches` endpoint in `backend/src/backend/api/v1/searches.py` that creates SearchExecution record, enqueues `run_full_search` ARQ job, creates BackgroundJob record, returns `{job_id, search_execution_id}`

### SSE Progress Stream

- [x] T068 [US3] Implement SSE endpoint `GET /jobs/{job_id}/progress` in `backend/src/backend/api/v1/jobs.py` as FastAPI `StreamingResponse` with async generator polling BackgroundJob table every 0.5s, emitting `event: progress` and `event: complete/error` messages
- [x] T069 [US3] Implement `GET /studies/{study_id}/jobs` endpoint in `backend/src/backend/api/v1/jobs.py` returning recent BackgroundJob list for a study
- [x] T070 [US3] Register searches and jobs routers in `backend/src/backend/api/v1/router.py`

### Candidate Papers API

- [x] T071 [US3] Implement `GET /studies/{study_id}/papers` with pagination and filters (status, phase_tag) and `GET /studies/{study_id}/papers/{candidate_id}` in `backend/src/backend/api/v1/papers.py`
- [x] T072 [US3] Implement `GET /studies/{study_id}/metrics` endpoint in `backend/src/backend/api/v1/metrics.py` aggregating SearchMetrics per phase with totals

### Frontend: Progress Dashboard & Paper Queue

- [x] T073 [US3] Create `frontend/src/services/jobs.ts` SSE hook `useJobProgress(jobId)` wrapping `EventSource`, handling reconnect, exposing `{status, progressPct, detail}` state; auto-closes on complete/error — ⚠️ **Principle IX compliance**: the `useEffect` that opens the `EventSource` MUST return `() => eventSource.close()` as its cleanup function so the connection is always closed on component unmount, even if the job has not yet completed (prevents SSE memory leaks under `React.StrictMode` double-invocation and navigation-away scenarios)
- [x] T074 [US3] Create `frontend/src/components/jobs/JobProgressPanel.tsx` (live dashboard: phase name, % progress bar, papers found counter, current database label, complete/error state)
- [x] T075 [US3] Create `frontend/src/components/phase2/PaperQueue.tsx` (paginated list of candidate papers with status badge, phase tag, AI decision summary; filters by status/phase)

### Testing: Phase 5 (US3) Modules (Constitution Principle VI)

- [ ] T148 [P] [T] Write unit tests for `dedup.py` in `backend/tests/unit/test_dedup.py` (DOI exact match, fuzzy title similarity ≥0.90 boundary, below-threshold non-duplicate); write unit tests for extended `ScreenerAgent` in `agents/tests/unit/test_screener.py` (mock LLMClient; verify ScreeningResult decision values and reasons list); write integration tests in `backend/tests/integration/test_searches_router.py`, `test_jobs_router.py`, `test_papers_router.py`, `test_metrics_router.py` covering job enqueue response, SSE stream close on complete, paper filter params, metrics aggregation totals
- [ ] T149 [P] [T] Write Vitest + Testing Library tests for `JobProgressPanel.tsx` and `PaperQueue.tsx` in `frontend/src/components/jobs/__tests__/` and `frontend/src/components/phase2/__tests__/` — mock EventSource, verify progress bar state changes, paper list filter interaction

**Checkpoint**: Full US3 pipeline functional — search execution, snowball sampling, live progress, paper queue.

---

## Phase 6: User Story 4 — Researcher Reviews and Overrides Paper Decisions (Priority: P3)

**Goal**: Researcher views any paper's decision and reasoning, overrides it, adds annotation; multi-reviewer disagreements are flagged for resolution.

**Independent Test**: Open a candidate paper with an AI decision → override to opposite decision with reason → save → audit log shows both decisions; create two reviewers with conflicting decisions → paper is flagged.

### Paper Decision Endpoints

- [x] T076 [US4] Implement `POST /studies/{study_id}/papers/{candidate_id}/decisions` in `backend/src/backend/api/v1/papers.py`: validates reviewer_id belongs to study, creates PaperDecision record with is_override flag, updates CandidatePaper.current_status; detects multi-human-reviewer disagreement and sets conflict_flag on CandidatePaper
- [x] T077 [US4] Implement `POST /studies/{study_id}/papers/{candidate_id}/resolve-conflict` in `backend/src/backend/api/v1/papers.py`: creates binding PaperDecision, clears conflict_flag, sets current_status

### Frontend: Paper Detail & Override UI

- [x] T078 [US4] Create `frontend/src/components/shared/PaperCard.tsx` (paper metadata, abstract, AI decision + reasons, reviewer decision history timeline)
- [x] T079 [US4] Create `frontend/src/components/phase2/ReviewerPanel.tsx` (accept/reject/duplicate buttons, reason selector from study's criteria list, override annotation text area, submit decision)
- [x] T080 [US4] Add conflict badge and resolution UI to `PaperCard.tsx`: when `conflict_flag=true` show both conflicting decisions side-by-side with a "Resolve" action calling `/resolve-conflict`

### Testing: Phase 6 (US4) Modules (Constitution Principle VI)

- [ ] T150 [P] [T] Write integration tests in `backend/tests/integration/test_papers_decisions.py` covering: POST decision validates reviewer belongs to study, is_override flag recorded, conflict_flag set on disagreement, resolve-conflict clears flag and sets binding status; write Vitest tests for `PaperCard.tsx` and `ReviewerPanel.tsx` in `frontend/src/components/phase2/__tests__/` and `frontend/src/components/shared/__tests__/` — verify conflict badge renders, override form submits

**Checkpoint**: Full US4 flow functional — manual review, override with audit trail, conflict resolution.

---

## Phase 7: User Story 5 — System Extracts and Classifies Data from Accepted Papers (Priority: P4)

**Goal**: AI extracts research type, venue type, authors, summary, open codings, and question-specific data from each accepted paper; second reviewer validates; human can edit with full audit trail; optimistic locking prevents silent overwrites.

**Independent Test**: Trigger batch extraction on a study with ≥1 accepted paper → extraction record appears with all required fields populated; edit a field → audit log preserves original AI value; simulate concurrent edit → receive 409 with both versions.

### Extraction Models (Migration 6)

- [ ] T081 [P] [US5] Create `db/src/db/models/extraction.py` with DataExtraction (id, candidate_paper_id FK unique, research_type Enum evaluation/solution_proposal/validation/philosophical/opinion/personal_experience/unknown, venue_type String, venue_name nullable, author_details JSON, summary Text nullable, open_codings JSON, keywords JSON, question_data JSON, extraction_status Enum pending/ai_complete/validated/human_reviewed, version_id Integer, extracted_by_agent nullable, validated_by_reviewer_id FK nullable, conflict_flag Boolean, created_at, updated_at; `__mapper_args__ = {"version_id_col": version_id}`) and ExtractionFieldAudit (id, extraction_id FK, field_name String, original_value JSON, new_value JSON, changed_by_user_id FK, changed_at)
- [ ] T082 [US5] Create Alembic migration `db/alembic/versions/0008_extraction.py` for DataExtraction and ExtractionFieldAudit tables — use `revision = "0008"`, `down_revision = "0007"` (chaining after the existing `0007_conflict_flag.py` migration)

### Extractor Agent Extension

- [ ] T083 [P] [US5] Update Jinja2 prompt templates in `agents/src/agents/prompts/extractor/` to produce structured output covering: research_type (with R1–R6 decision rules applied), venue_type, venue_name, author_details, summary, open_codings `[{code, definition, evidence_quote}]`, keywords, question_data `{question_text: extracted_value}`
- [ ] T084 [US5] Extend `ExtractorAgent` in `agents/src/agents/services/extractor.py` to accept paper metadata + abstract/full_text + study research questions; return `ExtractionResult` Pydantic model with all fields from DataExtraction; apply R1–R6 decision rules for research_type classification

### Batch Extraction ARQ Job

- [ ] T161 Update `WorkerSettings.functions` in `backend/src/backend/jobs/worker.py` to ADD the new ARQ job functions to the **existing** list — do NOT replace or remove the existing entries (`run_test_search`, `run_full_search`, `run_snowball`). Add imports and append: `run_batch_extraction` (from `backend.jobs.extraction_job`), `run_generate_results` + `run_export` (from `backend.jobs.results_job`), `run_quality_eval` (from `backend.jobs.quality_job`). The resulting `functions` list MUST contain all seven functions: `[run_test_search, run_full_search, run_snowball, run_batch_extraction, run_generate_results, run_export, run_quality_eval]`. MUST run before T085 so the worker can discover these jobs at startup (ARQ silently ignores unregistered functions)

> **⚠️ SRP note (Constitution Principle I)**: T085, T097-T099, and T108 currently all target `extraction_job.py`. To avoid a God-module anti-pattern, implement as three separate files: `extraction_job.py` (batch extraction only), `results_job.py` (result generation + export), `quality_job.py` (quality evaluation). Update T097-T099 to target `backend/src/backend/jobs/results_job.py` and T108 to target `backend/src/backend/jobs/quality_job.py` before implementation begins.
- [ ] T085 [US5] Implement `run_batch_extraction(study_id)` ARQ job in `backend/src/backend/jobs/extraction_job.py`: iterates all accepted CandidatePapers without completed extraction, fetches full text via researcher-mcp `fetch_paper_pdf` (falls back to abstract), calls ExtractorAgent, creates DataExtraction record, calls configured AI reviewers for validation, flags conflict if they disagree, writes progress to BackgroundJob

### Extraction API with Optimistic Locking

- [ ] T086 [US5] Implement extraction endpoints in `backend/src/backend/api/v1/extractions.py`: `GET /studies/{study_id}/extractions` (with status filter + pagination), `GET /studies/{study_id}/extractions/{id}` (with audit history), `POST /studies/{study_id}/extractions/batch-run` (enqueues batch extraction job)
- [ ] T087 [US5] Implement `PATCH /studies/{study_id}/extractions/{id}` in `backend/src/backend/api/v1/extractions.py`: catches SQLAlchemy `StaleDataError` after `session.flush()`, rolls back, re-queries current state, returns `HTTP 409` with `{error: "conflict", your_version: {...}, current_version: {...}}`; on success creates ExtractionFieldAudit entries for changed fields
- [ ] T088 [US5] Register extractions router in `backend/src/backend/api/v1/router.py`

### Frontend: Extraction & Diff/Merge UI

- [ ] T089 [US5] Create `frontend/src/components/phase3/ExtractionView.tsx` (displays all extraction fields for an accepted paper; inline editable fields; version_id sent with PATCH; shows validation status badge)
- [ ] T090 [US5] Create `frontend/src/components/shared/DiffViewer.tsx` (shows two-column diff of `your_version` vs `current_version` from 409 response; "Keep Mine", "Keep Theirs", "Merge" actions; resubmits with updated version_id)
- [ ] T091 [US5] Create `frontend/src/pages/ExtractionPage.tsx` wrapping ExtractionView with DiffViewer modal on 409 conflict response

### Testing: Phase 7 (US5) Modules (Constitution Principle VI)

- [ ] T151 [P] [T] Write unit tests for extended `ExtractorAgent` in `agents/tests/unit/test_extractor.py` (mock LLMClient; verify ExtractionResult all fields present, research_type is valid R1–R6 Enum value); write integration tests in `backend/tests/integration/test_extractions_router.py` covering: batch-run 202 response, PATCH with correct version_id succeeds, PATCH with stale version_id returns 409 with both versions, ExtractionFieldAudit row created on successful PATCH
- [ ] T152 [P] [T] Write Vitest + Testing Library tests for `ExtractionView.tsx` and `DiffViewer.tsx` in `frontend/src/components/phase3/__tests__/` and `frontend/src/components/shared/__tests__/` — verify inline field edit triggers PATCH, 409 response opens DiffViewer with both versions, "Keep Mine" resubmits with original version_id

**Checkpoint**: Full US5 flow functional — batch extraction, AI classification, human edit with audit trail, concurrent edit conflict resolution.

---

## Phase 8: User Story 6 — System Generates Visualizations and Study Report (Priority: P5)

**Goal**: Generate all publication-ready SVG charts plus interactive D3.js domain model; export in four formats.

**Independent Test**: On a study with ≥5 extracted papers, trigger result generation → publications-per-year bar chart and keyword bubble map appear as downloadable SVGs; domain model renders in frontend; export as Full Study Archive downloads a zip.

### Results Models (Migration 9)

- [ ] T092 [P] [US6] Create `db/src/db/models/results.py` with DomainModel (id, study_id FK, version SmallInt, concepts JSON, relationships JSON, svg_content Text nullable, generated_at) and ClassificationScheme (id, study_id FK, chart_type Enum venue/author/locale/institution/year/subtopic/research_type/research_method, version SmallInt, chart_data JSON, svg_content Text nullable, generated_at) and QualityReport (id, study_id FK, version SmallInt, score fields SmallInt ×5, total_score SmallInt, rubric_details JSON, recommendations JSON, generated_at)
- [ ] T093 [US6] Create Alembic migration `db/alembic/versions/0009_results.py` for DomainModel, ClassificationScheme, QualityReport tables — use `revision = "0009"`, `down_revision = "0008"` (chaining after T082's extraction migration)

### Domain Model Agent

- [ ] T094 [P] [US6] Create Jinja2 prompt templates `agents/src/agents/prompts/domain_modeler/system.md` and `user.md.j2` (extracts concepts and relationships from open codings + keywords + summaries) — use `.md`/`.md.j2` convention matching existing librarian, expert, search_builder prompts
- [ ] T095 [US6] Implement `DomainModelAgent` in `agents/src/agents/services/domain_modeler.py`; returns `DomainModelResult(concepts: [{name, definition, attributes}], relationships: [{from, to, label, type}])` Pydantic model

### Visualization Service

- [ ] T096 [US6] Implement `backend/src/backend/services/visualization.py` with functions:
  - `generate_bar_chart(data, title, xlabel, ylabel) → str` (matplotlib SVG string, publications per year)
  - `generate_bubble_chart(items: [{label, value}], title) → str` (plotly + kaleido SVG string, keyword/classification bubbles)
  - `generate_classification_charts(extractions, chart_type) → str` (matplotlib SVG for venue/author/locale/institution/year/research_type/research_method)
  - `generate_frequency_infographic(year_counts) → str` (matplotlib custom SVG)

### Results & Export ARQ Job

- [ ] T097 [US6] Implement `run_generate_results(study_id)` ARQ job in `backend/src/backend/jobs/results_job.py` (separate from extraction_job.py — SRP): (1) calls DomainModelAgent with all open codings/keywords, stores DomainModel; (2) calls visualization service for each of 8 ClassificationScheme chart types, stores SVGs; (3) writes progress to BackgroundJob
- [ ] T098 [US6] Implement export service `backend/src/backend/services/export.py` with `build_export(study_id, format) → bytes`: handles svg_only (zip of SVGs), json_only (full study JSON), csv_json (tabular CSV + JSON), full_archive (zip of all)
- [ ] T099 [US6] Implement `run_export(study_id, format)` ARQ job in `backend/src/backend/jobs/results_job.py` that calls export service and stores result in temp storage, marks BackgroundJob complete with download URL

### Results API

- [ ] T100 [US6] Implement results endpoints in `backend/src/backend/api/v1/results.py`: `GET /studies/{study_id}/results`, `POST /studies/{study_id}/results/generate` (enqueues job), `GET /studies/{study_id}/results/charts/{id}/svg` (returns SVG content-type), `GET /studies/{study_id}/results/domain-model/svg`, `POST /studies/{study_id}/export` (enqueues export job), `GET /studies/{study_id}/export/{export_id}/download`
- [ ] T101 [US6] Register results router in `backend/src/backend/api/v1/router.py`

### Frontend: Results & Domain Model

- [ ] T102 [US6] Create `frontend/src/pages/ResultsPage.tsx` (shows all generated charts as SVG img tags with download buttons, export format selector panel)
- [ ] T103 [P] [US6] Create `frontend/src/components/results/ChartGallery.tsx` (grid of 8 classification SVG charts + publications bar chart + infographic, each downloadable)
- [ ] T104 [P] [US6] Create `frontend/src/components/results/DomainModelViewer.tsx` (D3.js force-directed graph rendering `concepts` and `relationships` JSON from DomainModel record; "Export SVG" button serializes current SVG node)
- [ ] T105 [US6] Create `frontend/src/components/results/ExportPanel.tsx` (radio buttons: SVG Only, JSON Only, CSV+JSON, Full Archive; "Export" triggers job; progress via SSE; "Download" on complete)

### Testing: Phase 8 (US6) Modules (Constitution Principle VI)

- [ ] T153 [P] [T] Write unit tests for `visualization.py` in `backend/tests/unit/test_visualization.py` (mock matplotlib/plotly; verify SVG string returned, non-empty, contains `<svg>` tag); write unit tests for `export.py` in `backend/tests/unit/test_export.py` (verify no Settings field names in any export payload — `_REDACTED_FIELDS` check); write integration tests in `backend/tests/integration/test_results_router.py` covering: generate 202, svg endpoint Content-Type image/svg+xml, export download 200
- [ ] T154 [P] [T] Write Vitest + Testing Library tests for `ChartGallery.tsx` and `ExportPanel.tsx` in `frontend/src/components/results/__tests__/` — verify SVG img tags render, export format selection triggers job, download button appears on completion
- [ ] T164 [P] [T] Add deepeval evaluation pipeline for `DomainModelAgent` in `agent-eval/src/agent_eval/evals/domain_modeler_eval.py` — define dataset of open-codings + keyword sets, output criteria (≥1 concept, ≥1 relationship, no duplicate concept names, valid relationship direction), pass/fail threshold (Constitution Principle VI — deepeval MUST be added when agent is first created)

**Checkpoint**: Full US6 flow functional — all 6+ chart types generated as SVGs, interactive domain model, all four export formats.

---

## Phase 9: User Story 7 — AI Quality Evaluation Judge Assesses Study (Priority: P5)

**Goal**: Quality judge agent evaluates study against all 5 rubrics, produces scores 0–11 with improvement recommendations; researcher can re-run at any time.

**Independent Test**: On a study with Phase 1 and Phase 2 data, run quality evaluation → report shows scores for all 5 rubrics (Need for Review 0–2, Search Strategy 0–2, Search Evaluation 0–3, Extraction & Classification 0–3, Study Validity 0–1) with justification and prioritized recommendations.

### Quality Judge Agent

- [ ] T106 [P] [US7] Create Jinja2 prompt templates `agents/src/agents/prompts/quality_judge/system.md` and `user.md.j2` encoding the 5 rubric definitions with scoring criteria — use `.md`/`.md.j2` convention matching existing agent prompts
- [ ] T107 [US7] Implement `QualityJudgeAgent` in `agents/src/agents/services/quality_judge.py`; accepts study snapshot JSON (PICO saved?, search strategies used, test-retest done?, reviewers configured?, extractions done?, validity section filled?); returns `QualityJudgeResult(scores: {rubric: int}, rubric_details: {rubric: {score, justification}}, recommendations: [{priority, action, target_rubric}])` Pydantic model

### Quality Evaluation ARQ Job & API

- [ ] T108 [US7] Implement `run_quality_eval(study_id)` ARQ job in `backend/src/backend/jobs/quality_job.py` (separate from extraction_job.py — SRP): assembles study snapshot, calls QualityJudgeAgent, creates QualityReport record, marks job complete
- [ ] T109 [US7] Implement quality report endpoints in `backend/src/backend/api/v1/quality.py`: `GET /studies/{study_id}/quality-reports`, `GET /studies/{study_id}/quality-reports/{id}`, `POST /studies/{study_id}/quality-reports` (enqueues quality eval job)
- [ ] T110 [US7] Register quality router in `backend/src/backend/api/v1/router.py`

### Validity Discussion API

- [ ] T111 [P] [US7] Add `validity` JSON column to Study model in `db/src/db/models/study.py` (stores descriptive/theoretical/generalizability_internal/generalizability_external/interpretive/repeatability text); create Alembic migration `db/alembic/versions/0011_study_validity_column.py` with `down_revision = "0010"` — ⚠️ **depends on T123 completing first** so the `down_revision` chain is correct (0010 = audit_trail migration from T123; see dependency note in Phase Dependencies)
- [ ] T112 [P] [US7] Implement `GET /studies/{study_id}/validity`, `PUT /studies/{study_id}/validity`, `POST /studies/{study_id}/validity/generate` (enqueues `run_validity_prefill` ARQ job from T170) in `backend/src/backend/api/v1/validity.py`

### ValidityAgent — AI Pre-fill (FR-037)

> **New tasks (remediation C2)**: T112's `/validity/generate` endpoint requires a ValidityAgent
> and ARQ job. These MUST be completed before T112 is marked done.

- [ ] T168 [P] [US7] Create Jinja2 prompt templates `agents/src/agents/prompts/validity/system.md` and `user.md.j2` — system prompt encodes the six validity dimensions (descriptive, theoretical, generalizability_internal, generalizability_external, interpretive, repeatability) with instructions to generate pre-populated draft text for each based on the study's process, decisions, and context
- [ ] T169 [US7] Implement `ValidityAgent` in `agents/src/agents/services/validity.py`; accepts study snapshot (PICO, search strategy summary, inclusion/exclusion criteria list, data extraction summary, reviewer configuration); returns `ValidityResult(descriptive: str, theoretical: str, generalizability_internal: str, generalizability_external: str, interpretive: str, repeatability: str)` Pydantic model; routes LLM call through `LLMClient` (Principle VII — no direct SDK calls); prompt loaded via `PromptLoader` (depends on T168)
- [ ] T170 [US7] Implement `run_validity_prefill(study_id)` ARQ job in `backend/src/backend/jobs/validity_job.py` (SRP — separate file from quality_job.py): assembles study snapshot from DB, calls `ValidityAgent`, updates `Study.validity` JSON with generated text, marks BackgroundJob complete (depends on T169)
- [ ] T171 [P] [US7] Register `run_validity_prefill` in `backend/src/backend/jobs/worker.py` `WorkerSettings.functions` alongside the other job functions (depends on T170 completing first — same pattern as T161 for extraction/results/quality jobs)
- [ ] T173 [P] [T] Add deepeval evaluation pipeline for `ValidityAgent` in `agent-eval/src/agent_eval/evals/validity_eval.py` — define dataset of study snapshots at varying completion states, output criteria (all 6 validity dimensions non-empty, no hallucinated citations, language reflects actual study decisions), pass/fail threshold (Constitution Principle VI — deepeval MUST be added when agent is first created; MUST complete before T169 is marked done)

### Frontend: Quality & Validity UI

- [ ] T113 [US7] Create `frontend/src/components/phase5/QualityReport.tsx` (rubric score cards with score/max, justification text, prioritized recommendation list with action buttons)
- [ ] T114 [P] [US7] Create `frontend/src/components/phase4/ValidityForm.tsx` (six text areas for validity dimensions, "Generate with AI" button, auto-save on blur) — ⚠️ **Principle IX compliance**: auto-save on blur MUST use `register` + `onBlur` (not `watch()`); if any cross-field conditional logic requires reactive subscription, use `useWatch` on the specific field(s) — never import the `watch` function from `useForm()` in the render path

### Testing: Phase 9 (US7) Modules (Constitution Principle VI)

- [ ] T155 [P] [T] Write unit tests for `QualityJudgeAgent` in `agents/tests/unit/test_quality_judge.py` (mock LLMClient; verify scores are within valid ranges per rubric, recommendations list non-empty); write unit tests for `ValidityAgent` in `agents/tests/unit/test_validity.py` (mock LLMClient; verify `ValidityResult` has all 6 fields non-empty, `ValueError` raised when study snapshot is missing required keys); write integration tests in `backend/tests/integration/test_quality_router.py` and `test_validity_router.py` covering: quality report POST 202, GET returns rubric details, validity PUT stores six fields, validity/generate POST 202 enqueues BackgroundJob
- [ ] T156 [P] [T] Write Vitest + Testing Library tests for `QualityReport.tsx` and `ValidityForm.tsx` in `frontend/src/components/phase5/__tests__/` and `frontend/src/components/phase4/__tests__/` — verify score cards render with score/max, recommendation list displays priority, validity text areas auto-save on blur
- [ ] T165 [P] [T] Add deepeval evaluation pipeline for `QualityJudgeAgent` in `agent-eval/src/agent_eval/evals/quality_judge_eval.py` — define dataset of study snapshots at varying completion levels, output criteria (all 5 rubrics scored, scores within valid 0–max ranges, ≥1 recommendation per low-scoring rubric), pass/fail threshold (Constitution Principle VI — deepeval MUST be added when agent is first created)

**Checkpoint**: Full US7 flow functional — quality rubric scoring, recommendations, validity discussion with AI pre-fill (T168–T171).

---

## Phase 10: Audit Trail, Admin Dashboard & Secrets Hygiene (FR-044, FR-045, FR-046)

**Goal**: Implement study-level audit log (FR-044), administrative health + job-retry
dashboard (FR-045), and export secrets hygiene (FR-046). Depends on T122–T124 (AuditRecord
model and migration) being complete.

**Independent Test**: Study admin can navigate to the audit log and see a paginated list of
study mutations; a system admin can view the health dashboard and retry a failed job from
the browser without touching infrastructure.

### Audit Trail Service & API (FR-044)

- [ ] T125 [P] Implement `backend/src/backend/services/audit.py` with `async def record(session, study_id, actor_user_id, actor_agent, entity_type, entity_id, action, field_name, before_value, after_value)` — thin write layer using structlog; raises `ValueError` if both actor_user_id and actor_agent are None
- [ ] T126 [P] Instrument existing write endpoints to call `AuditService.record()`: PICO saves in `backend/src/backend/api/v1/pico.py`, search string saves in `backend/src/backend/api/v1/search_strings.py`, criteria CRUD in `backend/src/backend/api/v1/criteria.py`, study PATCH in `backend/src/backend/api/v1/studies.py`, paper decision submission and conflict resolution in `backend/src/backend/api/v1/papers.py`, seed CRUD (papers + authors) in `backend/src/backend/api/v1/seeds.py`, StudyMember add/remove in `backend/src/backend/api/v1/groups.py`
- [ ] T127 Implement `backend/src/backend/api/v1/audit.py` — `GET /studies/{study_id}/audit` with pagination, optional `entity_type` and `actor_user_id` query filters, admin-only access guard (HTTP 403 for non-admins), returns paginated AuditRecord list per contracts/api-v1.md
- [ ] T128 Register `audit_router` in `backend/src/backend/api/v1/router.py`

### Admin Health Dashboard & Job Retry API (FR-045)

- [ ] T129 Implement `backend/src/backend/api/v1/admin.py` with: `GET /admin/health` (probe DB, Redis, ARQ worker, researcher-mcp; return `{status, services:[{name, status, latency_ms, detail?}], checked_at}`; admin-only; MUST NOT return any config secrets), `GET /admin/jobs` (cross-study BackgroundJob list with status filter + pagination), `POST /admin/jobs/{job_id}/retry` (re-enqueues a failed ARQ job; returns 409 if not in `failed` status)
- [ ] T130 Register `admin_router` in `backend/src/backend/api/v1/router.py`

### Admin Dashboard Frontend (FR-045)

- [ ] T131 [P] Create `frontend/src/components/admin/ServiceHealthPanel.tsx` — polls `GET /admin/health` every 30s via TanStack Query; renders color-coded status cards (green/amber/red) per service with latency and last-checked timestamp
- [ ] T132 [P] Create `frontend/src/components/admin/JobRetryPanel.tsx` — lists failed jobs via `GET /admin/jobs?status=failed` with study name, job type, error message; retry button calls `POST /admin/jobs/{id}/retry`; shows success confirmation with new job ID
- [ ] T133 Create `frontend/src/pages/AdminPage.tsx` — admin-only page composing `ServiceHealthPanel` and `JobRetryPanel`; redirects non-admins to /groups with a 403 message
- [ ] T134 Add `/admin` route to `frontend/src/main.tsx` and `frontend/src/App.tsx` (protected by admin role check)

### Export Secrets Hygiene (FR-046)

- [ ] T135 [P] When implementing `backend/src/backend/services/export.py` (T098): add `_REDACTED_FIELDS = {"database_url", "secret_key", "anthropic_api_key", "redis_url"}` safelist and assert no Settings field names appear in any JSON/archive export payload; add structlog warning if a key is stripped

### Testing: Phase 10 (Audit/Admin) Modules (Constitution Principle VI)

- [ ] T157 [P] [T] Write unit tests for `backend/src/backend/services/audit.py` in `backend/tests/unit/test_audit_service.py` (verify `AuditRecord` row created, ValueError raised when both actor fields None, structlog call made); write integration tests in `backend/tests/integration/test_audit_router.py` and `test_admin_router.py` covering: audit GET requires admin (403 for non-admin), entity_type filter applied, health endpoint returns all four services with status, retry 409 when job not failed, retry 404 when job not found
- [ ] T158 [P] [T] Write Vitest + Testing Library tests for `ServiceHealthPanel.tsx` and `JobRetryPanel.tsx` in `frontend/src/components/admin/__tests__/` — verify status card colors (green/amber/red), retry button triggers POST and shows confirmation with new job ID

**Checkpoint**: Study audit log accessible to admins; admin health dashboard shows service status; failed jobs retryable from UI; export bundles contain no secrets.

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Metrics display, agent evals, metamorphic tests, FastMCP style fix, quickstart validation.

- [ ] T115 [P] Create `frontend/src/components/phase2/MetricsDashboard.tsx` consuming `GET /studies/{study_id}/metrics` to display per-phase funnel (identified → accepted → rejected → duplicates)
- [ ] T116 [P] Verify all agent deepeval pipelines (T162: librarian+expert, T163: search_builder, T164: domain_modeler, T165: quality_judge, T173: validity, T139: screener, T140: extractor) are wired into the `agent-eval` CLI in `agent-eval/src/agent_eval/cli.py`; add an `eval all` subcommand that runs all pipelines in sequence and produces a combined pass/fail report (Principle VI — CI must run all eval pipelines on agent changes)
- [ ] T117 [P] Add `GET /studies/{study_id}/papers/{candidate_id}` audit trail section to `PaperCard.tsx` showing full `PaperDecision` history (reviewer, decision, timestamp, override chain)
- [ ] T118 Validate `quickstart.md` end-to-end: start all services per quickstart, create a group and study, confirm Phase 1–2 UI loads without errors; update quickstart if any steps are wrong
- [ ] T119 [P] Update `CLAUDE.md` Active Technologies with final resolved library choices (ARQ, matplotlib, networkx, plotly/kaleido, rapidfuzz, D3.js)
- [ ] T136 [P] Add metamorphic tests using `hypothesis` for `LibrarianAgent`, `ExpertAgent`, `SearchStringBuilderAgent` in `agents/tests/metamorphic/test_librarian.py`, `test_expert.py`, `test_search_builder.py` — define metamorphic relations (e.g., query expansion monotonicity, paraphrase consistency) (Principle VI — metamorphic tests required for every agent)
- [ ] T137 [P] Add metamorphic tests using `hypothesis` for `QualityJudgeAgent` and `DomainModelAgent` in `agents/tests/metamorphic/test_quality_judge.py` and `test_domain_modeler.py` — define relations for score monotonicity and concept-set stability (Principle VI)
- [ ] T174 [P] Add metamorphic tests using `hypothesis` for `ValidityAgent` in `agents/tests/metamorphic/test_validity.py` — define metamorphic relations: (1) **completeness monotonicity** — a study snapshot with more completed phases MUST produce validity text with equal or more specific detail than a less-complete snapshot; (2) **dimension independence** — modifying data relevant to one validity dimension MUST NOT change generated text for unrelated dimensions; (3) **paraphrase stability** — equivalent study descriptions phrased differently MUST produce semantically equivalent validity content (Principle VI — metamorphic tests MUST exist for every AI agent; MUST complete before T169 is marked done)
- [ ] T177 [P] Audit `frontend/src/components/studies/NewStudyWizard.tsx` for Principle IX.5 compliance: count related `useState` calls managing wizard step state; if >3 are found, write/update Vitest tests in `frontend/src/components/studies/__tests__/NewStudyWizard.test.tsx` that assert current step-state behavior (test-first, Principle IV), then refactor wizard step state into a single `useReducer` with a typed `WizardAction` discriminated union — each action variant must correspond to exactly one state transition; verify `useWatch` is used (not `watch()`) in any form-field subscriptions inside the wizard (Principle IX — >3 related useState MUST use useReducer; useWatch MUST replace watch())
- [ ] T138 [P] Verify that `mcp.add_tool(func)` in `researcher-mcp/src/researcher_mcp/server.py` satisfies FastMCP 2.0+ tool-registration requirements (docstrings present on all 4 functions ✅); if FastMCP 2.0+ requires the `@mcp.tool` Python decorator specifically, migrate `snowball.py` and `scraper.py` to use `@mcp.tool` and remove explicit `mcp.add_tool()` calls from `server.py`; confirm with FastMCP 2.0+ docs which form is canonical (Principle VII — must use approved FastMCP API pattern)
- [ ] T178 [P] Normalize prompt file extensions for already-implemented agents to match the approved `.md`/`.md.j2` convention (Principle VII): rename `agents/src/agents/prompts/librarian/system.jinja2` → `system.md`, `agents/src/agents/prompts/librarian/user.jinja2` → `user.md.j2`; rename `agents/src/agents/prompts/expert/system.jinja2` → `system.md`, `agents/src/agents/prompts/expert/user.jinja2` → `user.md.j2`; rename `agents/src/agents/prompts/search_builder/system.jinja2` → `system.md`, `agents/src/agents/prompts/search_builder/user.jinja2` → `user.md.j2`; update any hardcoded extension references in `LibrarianAgent`, `ExpertAgent`, `SearchStringBuilderAgent` service files and in `agents/src/agents/core/prompt_loader.py` if the loader uses a fixed `.jinja2` suffix — after rename, confirm `PromptLoader` resolves each template correctly by running the existing agent unit tests
- [ ] T179 [P] Verify `SynthesiserAgent` meets Constitution VI eval requirements: check whether `agent-eval/src/agent_eval/evals/synthesiser_eval.py` and `agents/tests/metamorphic/test_synthesiser.py` exist with passing pipelines from prior feature work; if either is absent or empty, create it — deepeval pipeline MUST define a representative input dataset and at least one metric (e.g., faithfulness, answer relevancy); metamorphic tests MUST define at least two relations (e.g., summary completeness monotonicity, paraphrase stability). Add to T116's `eval all` subcommand once verified (Principle VI — every AI agent MUST have deepeval + metamorphic coverage)
- [ ] T139 [P] Add deepeval evaluation pipeline + metamorphic tests (`hypothesis`) for `ScreenerAgent` in `agent-eval/src/agent_eval/evals/screener_eval.py` and `agents/tests/metamorphic/test_screener.py` — define output criteria (inclusion/exclusion decisions ≥85% agreement with ground truth), metamorphic relations (decision stability under abstract paraphrase, consistent rejection when criteria unmet) (Principle VI)
- [ ] T140 [P] Add deepeval evaluation pipeline + metamorphic tests (`hypothesis`) for `ExtractorAgent` in `agent-eval/src/agent_eval/evals/extractor_eval.py` and `agents/tests/metamorphic/test_extractor.py` — define output criteria (research_type accuracy ≥80% per R1–R6 decision rules), metamorphic relations (field extraction consistency under equivalent phrasings, completeness monotonicity when full text available) (Principle VI)

### Compliance Verification for Already-Implemented Code

> These tasks remediate compliance notes that were added to already-completed ([x]) tasks. The
> notes document *required* behaviour; these tasks verify the existing implementation satisfies
> it and patch it if not.

- [ ] T175 [P] Verify existing T049 implementation (`backend/src/backend/jobs/search_job.py` test-search job): confirm it creates a `BackgroundJob` record at job start with `status=running` and updates to `completed`/`failed` on exit, and that `T048` (`POST .../test`) returns the `job_id` in its response body (FR-027a). If not, patch the implementation and update the T048 endpoint response schema; add/update test coverage in `backend/tests/integration/test_search_strings_router.py` to assert `job_id` is present in the 202 response
- [ ] T176 [P] Verify existing T073 implementation (`frontend/src/services/jobs.ts` `useJobProgress` hook): confirm the `useEffect` that constructs the `EventSource` returns `() => eventSource.close()` as its cleanup function (Principle IX — mandatory cleanup for resource-acquiring effects). If not, patch the hook and add/update Vitest tests in `frontend/src/services/__tests__/` asserting the EventSource is closed when the hook unmounts (simulate with `cleanup()` from Testing Library)

### Mutation Testing (Constitution Principle VI — Final Quality Gate)

- [ ] T159 [P] [T] Run `mutmut run --paths-to-mutate backend/src/backend/` and `mutmut run --paths-to-mutate agents/src/agents/` targeting the new modules added in this feature (dedup.py, phase_gate.py, audit.py services, screener.py extension, extractor.py extension); achieve **≥85% mutation kill rate** (Constitution Principle VI mandates 85%); add surviving mutants that indicate test gaps as additional test cases in the relevant unit test files
- [ ] T160 [P] [T] Run `npx stryker run` against the new React components added in this feature (phase2/, phase3/, results/, admin/ directories); achieve **≥85% mutation kill rate** (Constitution Principle VI mandates 85%); add surviving mutants as additional Vitest test cases

---

## Dependencies & Execution Order

### Phase Dependencies

- **TREF tasks (TREF1–TREF6)**: MUST complete before any remaining unchecked task is started — resolves three blocking constitution violations (Principles II, III, VII)
- **T065b (Study.current_phase update in run_full_search)**: MUST complete before Phase 6 (US4) — the UI relies on correct current_phase for tab routing
- **T161 (worker.py registration)**: MUST complete before T085 — ARQ will not execute any job in `extraction_job.py`, `results_job.py`, or `quality_job.py` until functions are registered in `WorkerSettings`
- **T170 (validity ARQ job)**: MUST complete before T171 — worker.py cannot register a job function that does not yet exist; implementing T171 before T170 causes an `ImportError` at ARQ startup
- **T166 (Expert endpoint)**: MUST complete before T167 (Expert frontend) — frontend depends on the endpoint existing
- **T172 (iteration approval PATCH)**: MUST complete before T067 (full search trigger) is exercised — an approved `SearchString` (is_active=true) is a prerequisite for the full search; other Phase 5 tasks (model creation, MCP tools) may proceed in parallel
- **T123 (audit_trail migration 0010)**: MUST complete before T111 (validity migration 0011) — T111's `down_revision="0010"` chains to T123's migration; implementing T111 before T123 would create an orphaned migration head
- **Migration sequence note** (U1): `db/alembic/versions/0007_conflict_flag.py` was created during US3 implementation and adds `conflict_flag INTEGER` to `candidate_paper` (FR-043 / T077). It is not a planned task but is a real migration. The full chain is: `0001 → 0002 → 0003 → 0004 → 0005 → 0006 → 0007_conflict_flag → 0008_extraction (T082) → 0009_results (T093) → 0010_audit_trail (T123) → 0011_study_validity (T111)`
- **T168 (ValidityAgent prompts)**: MUST complete before T169 (ValidityAgent service)
- **T169 (ValidityAgent service)**: MUST complete before T170 (ARQ job) and before T173 (deepeval) is marked done
- **T173 (validity deepeval)**: MUST complete before T169 is marked done (Constitution VI)
- **T174 (ValidityAgent metamorphic tests)**: MUST complete before T169 is marked done (Constitution VI — metamorphic tests required for every AI agent)
- **T177 (NewStudyWizard useReducer audit)**: Write/update Vitest tests MUST precede any refactor (Principle IV test-first); no dependency on other Phase 11 tasks
- **T178 (prompt file extension normalization)**: No blocking dependencies; MUST complete before Phase 11 is considered done (Principle VII — approved naming convention)
- **T162 (librarian+expert deepeval)**: MUST complete before T029/T030 are marked done (Constitution VI)
- **T163 (search_builder deepeval)**: MUST complete before T045 is marked done (Constitution VI)
- **T164 (domain_modeler deepeval)**: MUST complete before T095 is marked done (Constitution VI)
- **T165 (quality_judge deepeval)**: MUST complete before T107 is marked done (Constitution VI)
- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — **BLOCKS all user stories**
- **Phase 3–9 (User Stories)**: All depend on Phase 2 completion
  - US1 (P3) → US2 (P4) → US3 (P5) sequentially (each phase unlocks the next)
  - US4 (P6) depends on US3 being complete (needs candidate papers)
  - US5 (P7) depends on US3 + US4 (needs accepted papers with decisions)
  - US6 (P8) depends on US5 (needs extraction data for charts)
  - US7 (P9) depends on US1 + US2 (quality judge needs PICO + search data)
- **T120–T124 (NFR-001 + AuditRecord)**: MUST complete before Phase 7 (US5) — migration must be applied before extraction models are created
- **Phase 10 (FR-044/045/046)**: Depends on T122–T124 (AuditRecord model) and Phase 9 (US7 complete)
- **Test tasks [T]**: Each test task depends on the implementation tasks within the same phase; test tasks marked [P] can run in parallel once their phase's implementation tasks begin
- **T159–T160 (mutation testing)**: Depends on all [T] tasks in Phases 2–10 being complete (requires a working test suite to measure mutation kill rates)
- **Phase 11 (Polish)**: Depends on all user stories and Phase 10 complete

### User Story Dependencies

- **US1 (P1)**: After Phase 2 — no other story dependency
- **US2 (P2)**: After US1 (needs PICO/C saved to generate search strings)
- **US3 (P3)**: After US2 (needs approved search string + criteria)
- **US4 (P3)**: After US3 (needs candidate papers to review)
- **US5 (P4)**: After US3 + US4 (needs accepted papers)
- **US6 (P5)**: After US5 (needs extraction data)
- **US7 (P5)**: After US1 + US2 (quality judge evaluates phases 1–5; partial evaluation valid after phase 2)

### Within Each User Story

- DB models → Alembic migration → agents/services → API endpoints → frontend components
- Models marked [P] within a phase can be created in parallel
- Agent tasks marked [P] within a phase can be done in parallel with models

### Parallel Opportunities (Within Phases)

**Phase 2**: T009 + T012 in parallel (different model files) → T010 + T013 (migrations, after models) → T015 + T016 + T018 + T019 + T020 all in parallel

**Phase 3**: T024 + T025 in parallel → T027 + T028 in parallel → T029 + T030 in parallel → T038 + T039 in parallel

**Phase 5**: T054 + T055 + T056 + T057 in parallel (different model files) → T059 + T060 + T061 in parallel (different MCP tool files)

---

## Parallel Execution Examples

### Phase 3 (US1) — Models + Agent Prompts in Parallel
```
Parallel set A (models):
  T024: Create pico.py model
  T025: Create seeds.py model

Parallel set B (agent prompts, after A starts):
  T027: Create librarian prompt templates
  T028: Create expert prompt templates
```

### Phase 5 (US3) — Models in Parallel
```
Parallel set (all different files):
  T054: Extend Paper model
  T055: Create search_exec.py
  T056: Create candidate.py
  T057: Create jobs.py
  T059: get_references tool
  T060: get_citations tool
  T061: scraper tools
```

---

## Implementation Strategy

### MVP First (US1 Only — Study Creation)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (auth, user/group model, study model, core API skeleton)
3. Complete Phase 3: US1 (wizard, PICO/C, seeds, Librarian agent)
4. **STOP and VALIDATE**: Create a study end-to-end, save PICO/C, see Phase 2 unlock
5. Deploy/demo

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 → Study creation MVP
3. US2 → Search string workflow
4. US3 → Full automated search pipeline (major milestone)
5. US4 → Human review + override
6. US5 → Data extraction (second major milestone)
7. US6 → Visualizations + export (publication-ready outputs)
8. US7 → Quality judge (completeness gate)
9. Polish → Agent evals, metrics UI

### Suggested MVP Scope

**Phases 1–3 only** (T001–T040) deliver a functional study scoping tool: researchers can create studies, define PICO/C, add seed papers, and get AI-powered seed suggestions. This represents demonstrable value with ~40 tasks.

---

## Notes

- **[P]** = different files, no dependency on incomplete tasks in same phase — safe to parallelize
- **[T]** = test task (unit, integration, UI, or mutation) — Constitution Principle VI mandated; appears alongside [P] when parallelizable
- **[USN]** = user story label for traceability to spec.md
- All DB model tasks must precede their Alembic migration tasks
- `version_id_col` configured via `__mapper_args__` (not mapped_column) — see research.md
- `expire_on_commit=False` must remain in session factory for optimistic lock conflict reporting
- researcher-mcp tools are MCP-protocol tools registered in `server.py`, not FastAPI endpoints
- Agent prompts live in `agents/src/agents/prompts/<agent_name>/` per existing pattern — system prompt is `system.md`, user prompt template is `user.md.j2` (Jinja2 template with `.md.j2` extension)
- Commit after each task or logical group (model + migration pair, or complete endpoint + service)
- **Constitution compliance (v1.4.0)**:
  - TREF tasks (TREF1–TREF6) are BLOCKING — resolve before continuing any unchecked tasks (Principles II, III, VII)
  - Every new Python service MUST use structlog (`from backend.core.config import get_logger`), not stdlib logging
  - Every new DB model MUST include `created_at` + `updated_at` with `server_default=func.now()` and `onupdate=func.now()`
  - Every new agent service MUST route LLM calls through `LLMClient`; prompts MUST live in `prompts/<agent_name>/`
  - All new endpoints MUST raise `HTTPException` for errors — never return plain error dicts
  - Metamorphic tests (T136, T137, T139, T140, T173, T174, T179) and deepeval pipelines (T116) MUST be completed before their respective agent tasks are marked done (Principle VI)
  - SC-012 (audit trail renders ≤3s for ≤500 events) has no automated performance test; validate manually during T118 quickstart with a seeded dataset of ≥500 AuditRecord rows and record the observed render time in the PR description
  - Export service (T098/T135) MUST redact all Settings-derived values from exported payloads (Principle VIII / FR-046)
