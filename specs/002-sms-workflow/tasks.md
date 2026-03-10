# Tasks: Systematic Mapping Study Workflow System

**Input**: Design documents from `/specs/002-sms-workflow/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Tests**: Not requested — implementation tasks only (no TDD tasks generated).

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story this task belongs to (US1–US7)

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

**Checkpoint**: Auth, groups, study model extended, router wired — user story work can begin in parallel.

---

## Phase 3: User Story 1 — Researcher Creates and Scopes a New Study (Priority: P1) 🎯 MVP

**Goal**: Researcher can log in, select a group, create a study via the wizard with PICO/C and reviewer config, add seed papers/authors, and use Librarian/Expert AI agents.

**Independent Test**: Log in → create a research group → complete New Study Wizard (name, SMS type, PICO/C, 1 reviewer) → study appears in list at Phase 1; Librarian agent returns suggestions.

### PICO/C & Seed Models (Migration 3)

- [ ] T024 [P] [US1] Create `db/src/db/models/pico.py` with PICOComponent (id, study_id FK, variant Enum PICO/PICOS/PICOT/SPIDER/PCC, population/intervention/comparison/outcome/context Text nullable, extra_fields JSON nullable, ai_suggestions JSON nullable, updated_at)
- [ ] T025 [P] [US1] Create `db/src/db/models/seeds.py` with SeedPaper (id, study_id FK, paper_id FK, added_by_user_id FK nullable, added_by_agent nullable, created_at) and SeedAuthor (id, study_id FK, author_name, institution nullable, profile_url nullable, added_by_user_id FK nullable, added_by_agent nullable, created_at)
- [ ] T026 [US1] Create Alembic migration `db/alembic/versions/0004_pico_and_seeds.py` for PICOComponent, SeedPaper, SeedAuthor tables

### AI Agents: Librarian & Expert

- [ ] T027 [P] [US1] Create Jinja2 prompt templates `agents/src/agents/prompts/librarian/system.jinja2` and `user.jinja2` for seed paper and author suggestions
- [ ] T028 [P] [US1] Create Jinja2 prompt templates `agents/src/agents/prompts/expert/system.jinja2` and `user.jinja2` for 10–20 high-confidence relevant papers
- [ ] T029 [P] [US1] Implement `LibrarianAgent` in `agents/src/agents/services/librarian.py` using LLMClient + PromptLoader; returns structured `{papers: [...], authors: [...]}` Pydantic model
- [ ] T030 [US1] Implement `ExpertAgent` in `agents/src/agents/services/expert.py`; returns structured list of up to 20 papers with title, authors, year, venue, rationale fields

### Study & PICO API

- [ ] T031 [US1] Implement study CRUD in `backend/src/backend/api/v1/studies.py`: `GET /groups/{group_id}/studies`, `POST /groups/{group_id}/studies` (wizard payload: name, type, motivation, objectives, questions, member_ids, reviewers, snowball_threshold), `GET /studies/{study_id}`, `PATCH /studies/{study_id}`, `POST /studies/{study_id}/archive`, `DELETE /studies/{study_id}`
- [ ] T032 [US1] Add phase-gate unlock logic as a service helper in `backend/src/backend/services/phase_gate.py` (checks PICO saved → unlocks phase 2; search complete → unlocks phase 3; extraction complete → unlocks 4/5)
- [ ] T033 [US1] Implement PICO/C endpoints in `backend/src/backend/api/v1/pico.py`: `GET /studies/{study_id}/pico`, `PUT /studies/{study_id}/pico` (saves PICOComponent, calls phase_gate), `POST /studies/{study_id}/pico/refine` (calls LibrarianAgent for component suggestions)
- [ ] T034 [US1] Implement seed endpoints in `backend/src/backend/api/v1/seeds.py`: `GET/POST/DELETE /studies/{study_id}/seeds/papers`, `GET/POST /studies/{study_id}/seeds/authors`, `POST /studies/{study_id}/seeds/librarian` (enqueues LibrarianAgent job)
- [ ] T035 [US1] Register studies, pico, seeds routers in `backend/src/backend/api/v1/router.py`

### Frontend: Study Wizard & Phase 1 UI

- [ ] T036 [US1] Create `frontend/src/pages/StudiesPage.tsx` (lists studies for selected group with name, topic, type, current_phase/status, archive/delete actions)
- [ ] T037 [US1] Create `frontend/src/components/studies/NewStudyWizard.tsx` — multi-step wizard: (1) Name+Type, (2) Assign members, (3) Configure reviewers (add human or AI agent), (4) Motivation+Objectives+Questions, (5) PICO/C form with variant selector
- [ ] T038 [P] [US1] Create `frontend/src/components/phase1/PICOForm.tsx` with variant selector (PICO/PICOS/PICOT/SPIDER/PCC), text areas per component, "Refine with AI" button calling `/pico/refine`
- [ ] T039 [P] [US1] Create `frontend/src/components/phase1/SeedPapers.tsx` (add/remove seed papers by DOI or manual entry, trigger Librarian agent, show suggestions list)
- [ ] T040 [US1] Create `frontend/src/pages/StudyPage.tsx` as phase router (renders phase 1–5 tabs based on `unlocked_phases`, shows current progress)

**Checkpoint**: Full US1 flow functional — wizard, PICO/C, seed management, Librarian suggestions.

---

## Phase 4: User Story 2 — Researcher Builds and Evaluates a Search String (Priority: P2)

**Goal**: Researcher defines inclusion/exclusion criteria, generates a PICO/C-based search string, tests it against seed papers, iterates, and approves it for full search.

**Independent Test**: Open Phase 2 of a study with PICO/C saved → generate search string → run test search against one DB → view recall against seed test set → approve iteration; Phase 3 remains locked.

### Criteria & Search Models (Migration 4)

- [ ] T041 [P] [US2] Create `db/src/db/models/criteria.py` with InclusionCriterion (id, study_id FK, description Text, order_index SmallInt, created_at) and ExclusionCriterion (same shape)
- [ ] T042 [P] [US2] Create `db/src/db/models/search.py` with SearchString (id, study_id FK, version SmallInt, string_text Text, is_active Boolean, created_at, created_by_user_id FK nullable, created_by_agent nullable) and SearchStringIteration (id, search_string_id FK, iteration_number SmallInt, result_set_count Integer, test_set_recall Float, ai_adequacy_judgment Text nullable, human_approved Boolean nullable, created_at)
- [ ] T043 [US2] Create Alembic migration `db/alembic/versions/0005_criteria_and_search.py` for InclusionCriterion, ExclusionCriterion, SearchString, SearchStringIteration tables

### Search String Builder Agent

- [ ] T044 [P] [US2] Create Jinja2 prompt templates `agents/src/agents/prompts/search_builder/system.jinja2` and `user.jinja2` (generates Boolean search string from PICO/C + keywords + synonyms/thesaurus expansion)
- [ ] T045 [US2] Implement `SearchStringBuilderAgent` in `agents/src/agents/services/search_builder.py`; accepts PICOComponent dict + seed keywords, returns `{search_string: str, terms_used: [...], expansion_notes: str}` Pydantic model

### Search String & Criteria API

- [ ] T046 [US2] Implement criteria endpoints in `backend/src/backend/api/v1/criteria.py`: `GET/POST/DELETE /studies/{study_id}/criteria/inclusion` and `GET/POST/DELETE /studies/{study_id}/criteria/exclusion`
- [ ] T047 [US2] Implement search string endpoints in `backend/src/backend/api/v1/search_strings.py`: `GET /studies/{study_id}/search-strings`, `POST /studies/{study_id}/search-strings` (manual), `POST /studies/{study_id}/search-strings/generate` (calls SearchStringBuilderAgent, creates SearchString + first iteration comparing against seed test set), `GET/PATCH /studies/{study_id}/search-strings/{id}/iterations`
- [ ] T048 [US2] Add `POST /studies/{study_id}/search-strings/{id}/test` endpoint that enqueues a test-search ARQ job in `backend/src/backend/api/v1/search_strings.py`
- [ ] T049 [US2] Implement test-search ARQ job in `backend/src/backend/jobs/search_job.py` (calls researcher-mcp `search_papers` with the string against selected DBs, computes recall against SeedPaper test set, creates SearchStringIteration, stores result)
- [ ] T050 [US2] Register criteria and search_strings routers in `backend/src/backend/api/v1/router.py`

### Frontend: Phase 2 UI

- [ ] T051 [US2] Create `frontend/src/components/phase2/CriteriaForm.tsx` (add/remove inclusion and exclusion criteria with order drag-reorder)
- [ ] T052 [P] [US2] Create `frontend/src/components/phase2/SearchStringEditor.tsx` (text area for search string, "Generate with AI" button, version history list)
- [ ] T053 [P] [US2] Create `frontend/src/components/phase2/TestRetest.tsx` (trigger test search, show iteration results: recall %, result count, AI adequacy judgment, approve/reject button)

**Checkpoint**: Full US2 flow functional — criteria, search string generation, test-retest, iteration approval.

---

## Phase 5: User Story 3 — System Executes Full Paper Search with Snowball Sampling (Priority: P3)

**Goal**: Full search pipeline: execute across databases, deduplicate, AI screen against criteria, iterative snowball sampling until threshold, all tracked with phase tags and search metrics.

**Independent Test**: Trigger full search on a study with approved search string → monitor progress dashboard → view candidate paper list with A/R/D decisions and phase tags; search metrics show counts per phase.

### Candidate Paper & Job Models (Migrations 5 & 7)

- [ ] T054 [P] [US3] Extend `db/src/db/models.py` Paper model: add authors JSON, year SmallInt nullable, venue String nullable, source_url Text nullable, full_text_available Boolean default False
- [ ] T055 [P] [US3] Create `db/src/db/models/search_exec.py` with SearchExecution (id, study_id FK, search_string_id FK, status Enum pending/running/completed/failed, phase_tag String, databases_queried JSON, started_at nullable, completed_at nullable, job_id String nullable) and SearchMetrics (id, search_execution_id FK unique, total_identified Integer, accepted Integer, rejected Integer, duplicates Integer, computed_at)
- [ ] T056 [P] [US3] Create `db/src/db/models/candidate.py` with CandidatePaper (id, study_id FK, paper_id FK, search_execution_id FK, phase_tag String, current_status Enum pending/accepted/rejected/duplicate, duplicate_of_id FK nullable, version_id Integer, created_at, updated_at; `__mapper_args__ = {"version_id_col": version_id}`; unique constraint study_id+paper_id) and PaperDecision (id, candidate_paper_id FK, reviewer_id FK, decision Enum, reasons JSON, is_override Boolean, overrides_decision_id FK nullable, created_at)
- [ ] T057 [P] [US3] Create `db/src/db/models/jobs.py` with BackgroundJob (id String PK, study_id FK, job_type Enum full_search/snowball_search/batch_extraction/quality_eval, status Enum queued/running/completed/failed, progress_pct SmallInt, progress_detail JSON, error_message Text nullable, queued_at, started_at nullable, completed_at nullable)
- [ ] T058 [US3] Create Alembic migration `db/alembic/versions/0006_candidate_papers.py` for SearchExecution, CandidatePaper, PaperDecision, BackgroundJob, SearchMetrics tables and Paper column extensions

### researcher-mcp: Snowball & Scraper Tools

- [ ] T059 [P] [US3] Implement `get_references(doi, max_results)` tool in `researcher-mcp/src/researcher_mcp/tools/snowball.py` (fetches paper reference list via OpenAlex/Semantic Scholar API)
- [ ] T060 [P] [US3] Implement `get_citations(doi, max_results)` tool in `researcher-mcp/src/researcher_mcp/tools/snowball.py` (fetches citing papers)
- [ ] T061 [P] [US3] Implement `scrape_journal(journal_url, year_from, year_to, max_results)` and `scrape_author_page(profile_url, max_results)` in `researcher-mcp/src/researcher_mcp/tools/scraper.py`
- [ ] T062 [US3] Register new tools in `researcher-mcp/src/researcher_mcp/server.py`

### Paper Deduplication & Screener Extension

- [ ] T063 [US3] Implement `backend/src/backend/services/dedup.py`: two-stage dedup — (1) exact DOI match against existing CandidatePapers for study, (2) rapidfuzz title similarity ≥ 0.90 + author overlap → probable duplicate flagged for review; returns `DedupResult(is_duplicate, definite, candidate_id_if_dup)`
- [ ] T064 [US3] Extend `ScreenerAgent` in `agents/src/agents/services/screener.py` to accept structured InclusionCriterion/ExclusionCriterion lists and return `ScreeningResult(decision: accepted/rejected/duplicate, reasons: [{criterion_id, type, text}])` Pydantic model

### Full Search & Snowball ARQ Jobs

- [ ] T065 [US3] Implement full search ARQ job `run_full_search(study_id, search_execution_id)` in `backend/src/backend/jobs/search_job.py`: (1) query each database via researcher-mcp `search_papers`, (2) dedup each result, (3) create CandidatePaper records, (4) call ScreenerAgent for each candidate, (5) create PaperDecision records, (6) update SearchMetrics, (7) write progress to BackgroundJob; writes progress_detail `{phase, database, papers_found, screened}` on each step
- [ ] T066 [US3] Implement snowball ARQ job `run_snowball(study_id, phase_tag, paper_dois, direction)` in `backend/src/backend/jobs/search_job.py`: calls `get_references` or `get_citations` via MCP client, deduplicates against existing candidates, screens new papers, updates SearchMetrics, stops if new non-duplicate count < snowball_threshold
- [ ] T067 [US3] Add `POST /studies/{study_id}/searches` endpoint in `backend/src/backend/api/v1/searches.py` that creates SearchExecution record, enqueues `run_full_search` ARQ job, creates BackgroundJob record, returns `{job_id, search_execution_id}`

### SSE Progress Stream

- [ ] T068 [US3] Implement SSE endpoint `GET /jobs/{job_id}/progress` in `backend/src/backend/api/v1/jobs.py` as FastAPI `StreamingResponse` with async generator polling BackgroundJob table every 0.5s, emitting `event: progress` and `event: complete/error` messages
- [ ] T069 [US3] Implement `GET /studies/{study_id}/jobs` endpoint in `backend/src/backend/api/v1/jobs.py` returning recent BackgroundJob list for a study
- [ ] T070 [US3] Register searches and jobs routers in `backend/src/backend/api/v1/router.py`

### Candidate Papers API

- [ ] T071 [US3] Implement `GET /studies/{study_id}/papers` with pagination and filters (status, phase_tag) and `GET /studies/{study_id}/papers/{candidate_id}` in `backend/src/backend/api/v1/papers.py`
- [ ] T072 [US3] Implement `GET /studies/{study_id}/metrics` endpoint in `backend/src/backend/api/v1/metrics.py` aggregating SearchMetrics per phase with totals

### Frontend: Progress Dashboard & Paper Queue

- [ ] T073 [US3] Create `frontend/src/services/jobs.ts` SSE hook `useJobProgress(jobId)` wrapping `EventSource`, handling reconnect, exposing `{status, progressPct, detail}` state; auto-closes on complete/error
- [ ] T074 [US3] Create `frontend/src/components/jobs/JobProgressPanel.tsx` (live dashboard: phase name, % progress bar, papers found counter, current database label, complete/error state)
- [ ] T075 [US3] Create `frontend/src/components/phase2/PaperQueue.tsx` (paginated list of candidate papers with status badge, phase tag, AI decision summary; filters by status/phase)

**Checkpoint**: Full US3 pipeline functional — search execution, snowball sampling, live progress, paper queue.

---

## Phase 6: User Story 4 — Researcher Reviews and Overrides Paper Decisions (Priority: P3)

**Goal**: Researcher views any paper's decision and reasoning, overrides it, adds annotation; multi-reviewer disagreements are flagged for resolution.

**Independent Test**: Open a candidate paper with an AI decision → override to opposite decision with reason → save → audit log shows both decisions; create two reviewers with conflicting decisions → paper is flagged.

### Paper Decision Endpoints

- [ ] T076 [US4] Implement `POST /studies/{study_id}/papers/{candidate_id}/decisions` in `backend/src/backend/api/v1/papers.py`: validates reviewer_id belongs to study, creates PaperDecision record with is_override flag, updates CandidatePaper.current_status; detects multi-human-reviewer disagreement and sets conflict_flag on CandidatePaper
- [ ] T077 [US4] Implement `POST /studies/{study_id}/papers/{candidate_id}/resolve-conflict` in `backend/src/backend/api/v1/papers.py`: creates binding PaperDecision, clears conflict_flag, sets current_status

### Frontend: Paper Detail & Override UI

- [ ] T078 [US4] Create `frontend/src/components/shared/PaperCard.tsx` (paper metadata, abstract, AI decision + reasons, reviewer decision history timeline)
- [ ] T079 [US4] Create `frontend/src/components/phase2/ReviewerPanel.tsx` (accept/reject/duplicate buttons, reason selector from study's criteria list, override annotation text area, submit decision)
- [ ] T080 [US4] Add conflict badge and resolution UI to `PaperCard.tsx`: when `conflict_flag=true` show both conflicting decisions side-by-side with a "Resolve" action calling `/resolve-conflict`

**Checkpoint**: Full US4 flow functional — manual review, override with audit trail, conflict resolution.

---

## Phase 7: User Story 5 — System Extracts and Classifies Data from Accepted Papers (Priority: P4)

**Goal**: AI extracts research type, venue type, authors, summary, open codings, and question-specific data from each accepted paper; second reviewer validates; human can edit with full audit trail; optimistic locking prevents silent overwrites.

**Independent Test**: Trigger batch extraction on a study with ≥1 accepted paper → extraction record appears with all required fields populated; edit a field → audit log preserves original AI value; simulate concurrent edit → receive 409 with both versions.

### Extraction Models (Migration 6)

- [ ] T081 [P] [US5] Create `db/src/db/models/extraction.py` with DataExtraction (id, candidate_paper_id FK unique, research_type Enum evaluation/solution_proposal/validation/philosophical/opinion/personal_experience/unknown, venue_type String, venue_name nullable, author_details JSON, summary Text nullable, open_codings JSON, keywords JSON, question_data JSON, extraction_status Enum pending/ai_complete/validated/human_reviewed, version_id Integer, extracted_by_agent nullable, validated_by_reviewer_id FK nullable, conflict_flag Boolean, created_at, updated_at; `__mapper_args__ = {"version_id_col": version_id}`) and ExtractionFieldAudit (id, extraction_id FK, field_name String, original_value JSON, new_value JSON, changed_by_user_id FK, changed_at)
- [ ] T082 [US5] Create Alembic migration `db/alembic/versions/0007_extraction.py` for DataExtraction and ExtractionFieldAudit tables

### Extractor Agent Extension

- [ ] T083 [P] [US5] Update Jinja2 prompt templates in `agents/src/agents/prompts/extractor/` to produce structured output covering: research_type (with R1–R6 decision rules applied), venue_type, venue_name, author_details, summary, open_codings `[{code, definition, evidence_quote}]`, keywords, question_data `{question_text: extracted_value}`
- [ ] T084 [US5] Extend `ExtractorAgent` in `agents/src/agents/services/extractor.py` to accept paper metadata + abstract/full_text + study research questions; return `ExtractionResult` Pydantic model with all fields from DataExtraction; apply R1–R6 decision rules for research_type classification

### Batch Extraction ARQ Job

- [ ] T085 [US5] Implement `run_batch_extraction(study_id)` ARQ job in `backend/src/backend/jobs/extraction_job.py`: iterates all accepted CandidatePapers without completed extraction, fetches full text via researcher-mcp `fetch_paper_pdf` (falls back to abstract), calls ExtractorAgent, creates DataExtraction record, calls configured AI reviewers for validation, flags conflict if they disagree, writes progress to BackgroundJob

### Extraction API with Optimistic Locking

- [ ] T086 [US5] Implement extraction endpoints in `backend/src/backend/api/v1/extractions.py`: `GET /studies/{study_id}/extractions` (with status filter + pagination), `GET /studies/{study_id}/extractions/{id}` (with audit history), `POST /studies/{study_id}/extractions/batch-run` (enqueues batch extraction job)
- [ ] T087 [US5] Implement `PATCH /studies/{study_id}/extractions/{id}` in `backend/src/backend/api/v1/extractions.py`: catches SQLAlchemy `StaleDataError` after `session.flush()`, rolls back, re-queries current state, returns `HTTP 409` with `{error: "conflict", your_version: {...}, current_version: {...}}`; on success creates ExtractionFieldAudit entries for changed fields
- [ ] T088 [US5] Register extractions router in `backend/src/backend/api/v1/router.py`

### Frontend: Extraction & Diff/Merge UI

- [ ] T089 [US5] Create `frontend/src/components/phase3/ExtractionView.tsx` (displays all extraction fields for an accepted paper; inline editable fields; version_id sent with PATCH; shows validation status badge)
- [ ] T090 [US5] Create `frontend/src/components/shared/DiffViewer.tsx` (shows two-column diff of `your_version` vs `current_version` from 409 response; "Keep Mine", "Keep Theirs", "Merge" actions; resubmits with updated version_id)
- [ ] T091 [US5] Create `frontend/src/pages/ExtractionPage.tsx` wrapping ExtractionView with DiffViewer modal on 409 conflict response

**Checkpoint**: Full US5 flow functional — batch extraction, AI classification, human edit with audit trail, concurrent edit conflict resolution.

---

## Phase 8: User Story 6 — System Generates Visualizations and Study Report (Priority: P5)

**Goal**: Generate all publication-ready SVG charts plus interactive D3.js domain model; export in four formats.

**Independent Test**: On a study with ≥5 extracted papers, trigger result generation → publications-per-year bar chart and keyword bubble map appear as downloadable SVGs; domain model renders in frontend; export as Full Study Archive downloads a zip.

### Results Models (Migration 8)

- [ ] T092 [P] [US6] Create `db/src/db/models/results.py` with DomainModel (id, study_id FK, version SmallInt, concepts JSON, relationships JSON, svg_content Text nullable, generated_at) and ClassificationScheme (id, study_id FK, chart_type Enum venue/author/locale/institution/year/subtopic/research_type/research_method, version SmallInt, chart_data JSON, svg_content Text nullable, generated_at) and QualityReport (id, study_id FK, version SmallInt, score fields SmallInt ×5, total_score SmallInt, rubric_details JSON, recommendations JSON, generated_at)
- [ ] T093 [US6] Create Alembic migration `db/alembic/versions/0008_results.py` for DomainModel, ClassificationScheme, QualityReport tables

### Domain Model Agent

- [ ] T094 [P] [US6] Create Jinja2 prompt templates `agents/src/agents/prompts/domain_modeler/system.jinja2` and `user.jinja2` (extracts concepts and relationships from open codings + keywords + summaries)
- [ ] T095 [US6] Implement `DomainModelAgent` in `agents/src/agents/services/domain_modeler.py`; returns `DomainModelResult(concepts: [{name, definition, attributes}], relationships: [{from, to, label, type}])` Pydantic model

### Visualization Service

- [ ] T096 [US6] Implement `backend/src/backend/services/visualization.py` with functions:
  - `generate_bar_chart(data, title, xlabel, ylabel) → str` (matplotlib SVG string, publications per year)
  - `generate_bubble_chart(items: [{label, value}], title) → str` (plotly + kaleido SVG string, keyword/classification bubbles)
  - `generate_classification_charts(extractions, chart_type) → str` (matplotlib SVG for venue/author/locale/institution/year/research_type/research_method)
  - `generate_frequency_infographic(year_counts) → str` (matplotlib custom SVG)

### Results & Export ARQ Job

- [ ] T097 [US6] Implement `run_generate_results(study_id)` ARQ job in `backend/src/backend/jobs/extraction_job.py`: (1) calls DomainModelAgent with all open codings/keywords, stores DomainModel; (2) calls visualization service for each of 8 ClassificationScheme chart types, stores SVGs; (3) writes progress to BackgroundJob
- [ ] T098 [US6] Implement export service `backend/src/backend/services/export.py` with `build_export(study_id, format) → bytes`: handles svg_only (zip of SVGs), json_only (full study JSON), csv_json (tabular CSV + JSON), full_archive (zip of all)
- [ ] T099 [US6] Implement `run_export(study_id, format)` ARQ job in `backend/src/backend/jobs/extraction_job.py` that calls export service and stores result in temp storage, marks BackgroundJob complete with download URL

### Results API

- [ ] T100 [US6] Implement results endpoints in `backend/src/backend/api/v1/results.py`: `GET /studies/{study_id}/results`, `POST /studies/{study_id}/results/generate` (enqueues job), `GET /studies/{study_id}/results/charts/{id}/svg` (returns SVG content-type), `GET /studies/{study_id}/results/domain-model/svg`, `POST /studies/{study_id}/export` (enqueues export job), `GET /studies/{study_id}/export/{export_id}/download`
- [ ] T101 [US6] Register results router in `backend/src/backend/api/v1/router.py`

### Frontend: Results & Domain Model

- [ ] T102 [US6] Create `frontend/src/pages/ResultsPage.tsx` (shows all generated charts as SVG img tags with download buttons, export format selector panel)
- [ ] T103 [P] [US6] Create `frontend/src/components/results/ChartGallery.tsx` (grid of 8 classification SVG charts + publications bar chart + infographic, each downloadable)
- [ ] T104 [P] [US6] Create `frontend/src/components/results/DomainModelViewer.tsx` (D3.js force-directed graph rendering `concepts` and `relationships` JSON from DomainModel record; "Export SVG" button serializes current SVG node)
- [ ] T105 [US6] Create `frontend/src/components/results/ExportPanel.tsx` (radio buttons: SVG Only, JSON Only, CSV+JSON, Full Archive; "Export" triggers job; progress via SSE; "Download" on complete)

**Checkpoint**: Full US6 flow functional — all 6+ chart types generated as SVGs, interactive domain model, all four export formats.

---

## Phase 9: User Story 7 — AI Quality Evaluation Judge Assesses Study (Priority: P5)

**Goal**: Quality judge agent evaluates study against all 5 rubrics, produces scores 0–11 with improvement recommendations; researcher can re-run at any time.

**Independent Test**: On a study with Phase 1 and Phase 2 data, run quality evaluation → report shows scores for all 5 rubrics (Need for Review 0–2, Search Strategy 0–2, Search Evaluation 0–3, Extraction & Classification 0–3, Study Validity 0–1) with justification and prioritized recommendations.

### Quality Judge Agent

- [ ] T106 [P] [US7] Create Jinja2 prompt templates `agents/src/agents/prompts/quality_judge/system.jinja2` and `user.jinja2` encoding the 5 rubric definitions with scoring criteria
- [ ] T107 [US7] Implement `QualityJudgeAgent` in `agents/src/agents/services/quality_judge.py`; accepts study snapshot JSON (PICO saved?, search strategies used, test-retest done?, reviewers configured?, extractions done?, validity section filled?); returns `QualityJudgeResult(scores: {rubric: int}, rubric_details: {rubric: {score, justification}}, recommendations: [{priority, action, target_rubric}])` Pydantic model

### Quality Evaluation ARQ Job & API

- [ ] T108 [US7] Add `run_quality_eval(study_id)` ARQ job to `backend/src/backend/jobs/extraction_job.py`: assembles study snapshot, calls QualityJudgeAgent, creates QualityReport record, marks job complete
- [ ] T109 [US7] Implement quality report endpoints in `backend/src/backend/api/v1/quality.py`: `GET /studies/{study_id}/quality-reports`, `GET /studies/{study_id}/quality-reports/{id}`, `POST /studies/{study_id}/quality-reports` (enqueues quality eval job)
- [ ] T110 [US7] Register quality router in `backend/src/backend/api/v1/router.py`

### Validity Discussion API

- [ ] T111 [P] [US7] Add `validity` JSON column to Study model in `db/src/db/models/study.py` (stores descriptive/theoretical/generalizability_internal/generalizability_external/interpretive/repeatability text); create Alembic migration `db/alembic/versions/0009_study_validity_column.py`
- [ ] T112 [P] [US7] Implement `GET /studies/{study_id}/validity`, `PUT /studies/{study_id}/validity`, `POST /studies/{study_id}/validity/generate` (AI pre-fill job) in `backend/src/backend/api/v1/validity.py`

### Frontend: Quality & Validity UI

- [ ] T113 [US7] Create `frontend/src/components/phase5/QualityReport.tsx` (rubric score cards with score/max, justification text, prioritized recommendation list with action buttons)
- [ ] T114 [P] [US7] Create `frontend/src/components/phase4/ValidityForm.tsx` (six text areas for validity dimensions, "Generate with AI" button, auto-save on blur)

**Checkpoint**: Full US7 flow functional — quality rubric scoring, recommendations, validity discussion.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Metrics display, agent evals, search metrics UI, quickstart validation.

- [ ] T115 [P] Create `frontend/src/components/phase2/MetricsDashboard.tsx` consuming `GET /studies/{study_id}/metrics` to display per-phase funnel (identified → accepted → rejected → duplicates)
- [ ] T116 [P] Add agent eval stubs in `agent-eval/src/agent_eval/evals/`: `librarian_eval.py`, `expert_eval.py`, `search_builder_eval.py`, `quality_judge_eval.py`, `domain_modeler_eval.py` using deepeval framework (extend existing patterns)
- [ ] T117 [P] Add `GET /studies/{study_id}/papers/{candidate_id}` audit trail section to `PaperCard.tsx` showing full `PaperDecision` history (reviewer, decision, timestamp, override chain)
- [ ] T118 Validate `quickstart.md` end-to-end: start all services per quickstart, create a group and study, confirm Phase 1–2 UI loads without errors; update quickstart if any steps are wrong
- [ ] T119 [P] Update `CLAUDE.md` Active Technologies with final resolved library choices (ARQ, matplotlib, networkx, plotly/kaleido, rapidfuzz, D3.js)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — **BLOCKS all user stories**
- **Phase 3–9 (User Stories)**: All depend on Phase 2 completion
  - US1 (P3) → US2 (P4) → US3 (P5) sequentially (each phase unlocks the next)
  - US4 (P6) depends on US3 being complete (needs candidate papers)
  - US5 (P7) depends on US3 + US4 (needs accepted papers with decisions)
  - US6 (P8) depends on US5 (needs extraction data for charts)
  - US7 (P9) depends on US1 + US2 (quality judge needs PICO + search data)
- **Phase 10 (Polish)**: Depends on all user stories complete

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
- **[USN]** = user story label for traceability to spec.md
- All DB model tasks must precede their Alembic migration tasks
- `version_id_col` configured via `__mapper_args__` (not mapped_column) — see research.md
- `expire_on_commit=False` must remain in session factory for optimistic lock conflict reporting
- researcher-mcp tools are MCP-protocol tools registered in `server.py`, not FastAPI endpoints
- Agent prompts live in `agents/src/agents/prompts/<agent_name>/` per existing pattern
- Commit after each task or logical group (model + migration pair, or complete endpoint + service)
