# Tasks: SLR Workflow

**Input**: Design documents from `/specs/007-slr-workflow/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/api-contracts.md ✓, quickstart.md ✓

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US6)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add new dependencies, register the SLR router package, and scaffold new directories.

- [x] T001 Add `scipy>=1.13`, `scikit-learn>=1.5`, `numpy>=1.26` to `[project].dependencies` in `backend/pyproject.toml`
- [x] T002 Create `backend/src/backend/api/v1/slr/__init__.py` and `backend/src/backend/api/v1/slr/router.py` (empty `APIRouter(prefix="/slr")` that will aggregate sub-routers)
- [x] T003 [P] Register the SLR router in `backend/src/backend/api/v1/router.py` (`include_router(slr_router, ...)`)
- [x] T004 [P] Create package stubs: `frontend/src/pages/slr/.gitkeep`, `frontend/src/components/slr/.gitkeep`, `frontend/src/services/slr/.gitkeep`, `frontend/src/hooks/slr/.gitkeep`
- [x] T005 [P] Create `agents/src/agents/prompts/protocol_reviewer/` directory with empty `system.md` and `user.md.j2` placeholder files
+
---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: All six ORM models, the Alembic migration, shared config settings, the statistics computation module, and Forest/Funnel plot generation must exist before any user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T006 Implement all six SLR ORM models and their enums in `db/src/db/models/slr.py`: `ReviewProtocolStatus`, `SynthesisApproach`, `ChecklistScoringMethod`, `AgreementRoundType`, `SynthesisStatus`, `GreyLiteratureType`, `ReviewProtocol`, `QualityAssessmentChecklist`, `QualityChecklistItem`, `QualityAssessmentScore`, `InterRaterAgreementRecord`, `SynthesisResult`, `GreyLiteratureSource` — all with `created_at`/`updated_at` audit columns; optimistic locking (`version_id`) on `ReviewProtocol`, `QualityAssessmentScore`, and `SynthesisResult`
- [x] T007 Export all new models and enums from `db/src/db/models/__init__.py`
- [x] T008 Create Alembic migration `db/alembic/versions/0015_slr_workflow.py` with `upgrade()` (create all 7 tables and 6 enum types) and `downgrade()` (drop in reverse dependency order); verify `uv run alembic upgrade head` succeeds
- [x] T009 [P] Add `slr_kappa_threshold: float = 0.6` and `slr_min_synthesis_papers: int = 3` to the `Settings` Pydantic BaseSettings class in `backend/src/backend/core/config.py`; add both vars to `.env.example`
- [x] T010 [P] Implement `backend/src/backend/services/statistics.py` with: `safe_cohen_kappa(decisions_a, decisions_b) -> float | None` (uses `sklearn.metrics.cohen_kappa_score`; handles zero-variance edge case), `compute_q_test(effect_sizes, weights) -> QTestResult`, `fixed_effects_meta_analysis(effect_sizes, ses, ci) -> MetaAnalysisResult`, `random_effects_meta_analysis(effect_sizes, ses, ci) -> MetaAnalysisResult`; all inputs/outputs typed with Pydantic models; Google-style docstrings throughout
- [x] T011 [P] Add `generate_forest_plot(studies, pooled_estimate, title) -> str` and `generate_funnel_plot(studies, pooled_estimate, title) -> str` to `backend/src/backend/services/visualization.py`; use existing `matplotlib.use("Agg")` + `StringIO` + `fig.savefig(buf, format="svg")` pattern; raise `ValueError` if fewer than `settings.slr_min_synthesis_papers` studies are provided to `generate_forest_plot`
- [x] T012 [P] Write unit tests for `statistics.py` in `backend/tests/test_statistics.py`: test Kappa with perfect/chance/zero-variance inputs; test Q-test formula; test fixed/random-effects pooled effect and CIs against known values; ≥ 85% coverage
- [x] T013 [P] Write unit tests for new visualization functions in `backend/tests/test_visualization_slr.py`: test SVG output is non-empty; test `ValueError` raised for < 3 studies in Forest plot; test Funnel plot envelope math; ≥ 85% coverage
- [x] T014 [P] Write unit tests for all six new ORM models in `db/tests/test_slr_models.py`: verify table names, column types, unique constraints, optimistic locking, enum values, and audit field defaults

**Checkpoint**: Run `uv run pytest db/tests/test_slr_models.py backend/tests/test_statistics.py backend/tests/test_visualization_slr.py` — all must pass before beginning user story phases.

---

## Phase 3: User Story 1 — Protocol Editor (Priority: P1) 🎯 MVP

**Goal**: A researcher can create, submit for AI review, iterate on, and validate a full SLR protocol before any database search is run.

**Independent Test**: Create a new SLR study; navigate to Protocol tab; fill all sections; submit for AI review; receive a `ProtocolReviewResult`; approve the protocol; verify the study phase endpoint shows the search phase as unlocked.

### Implementation for User Story 1

- [x] T015 [P] [US1] Write `agents/src/agents/prompts/protocol_reviewer/system.md`: agent persona (expert SLR methodologist); evaluation criteria (RQ-PICO alignment, completeness of all mandatory sections, feasibility of search strategy, checklist-to-RQ traceability); output format instruction (structured JSON with a list of issues)
- [x] T016 [P] [US1] Write `agents/src/agents/prompts/protocol_reviewer/user.md.j2`: Jinja2 template rendering all protocol fields (background, rationale, research_questions, pico_*, search_strategy, inclusion_criteria, exclusion_criteria, data_extraction_strategy, synthesis_approach, dissemination_strategy, timetable) into the prompt context
- [x] T017 [US1] Implement `agents/src/agents/services/protocol_reviewer.py`: `ProtocolIssue(BaseModel)` with `section: str`, `severity: str`, `description: str`, `suggestion: str`; `ProtocolReviewResult(BaseModel)` with `issues: list[ProtocolIssue]`, `overall_assessment: str`; `ProtocolReviewerAgent.__init__` accepting `llm_client`, `provider_config`, `system_message_override`; `async def review(self, protocol_data: dict[str, Any]) -> ProtocolReviewResult` rendering the user template and parsing JSON response; Google-style docstrings throughout
- [x] T018 [US1] Write unit tests for `ProtocolReviewerAgent` in `agents/tests/test_protocol_reviewer.py`: mock `LLMClient`; assert well-formed JSON is parsed into `ProtocolReviewResult`; assert malformed JSON response raises a handled exception; ≥ 85% coverage
- [x] T019 [US1] Write metamorphic tests for `ProtocolReviewerAgent` in `agents/tests/metamorphic/test_protocol_reviewer_meta.py` using `hypothesis`: define metamorphic relation — paraphrased protocol with same content should produce the same set of issue sections (not necessarily same wording); verify the agent does not raise on arbitrarily long inputs
- [x] T020 [US1] Add `ProtocolReviewerAgent` deepeval evaluation pipeline in `agent-eval/src/agent_eval/evals/protocol_reviewer_eval.py`: define representative dataset (5–10 protocol inputs with known issues); define `FaithfulnessMetric` and `AnswerRelevancyMetric`; pass threshold 0.7; follow the pattern of `agent-eval/src/agent_eval/evals/screener_eval.py`
- [x] T021 [US1] Implement `backend/src/backend/jobs/protocol_review_job.py`: `async def run_protocol_review(ctx, *, study_id: int, protocol_id: int)` — fetches `ReviewProtocol`, calls `ProtocolReviewerAgent.review()`, stores JSON result in `ReviewProtocol.review_report`, updates `status` back to `draft` (so researcher can iterate); uses `structlog` bound with `study_id`
- [x] T022 [US1] Register `run_protocol_review` in `backend/src/backend/jobs/worker.py` `functions` list
- [x] T023 [US1] Implement `backend/src/backend/services/slr_protocol_service.py`: `get_protocol(study_id, db)`, `upsert_protocol(study_id, data, db) -> ReviewProtocol`, `submit_for_review(study_id, db, arq_pool) -> str` (validates completeness, sets `status=under_review`, enqueues `run_protocol_review`), `validate_protocol(study_id, db) -> ReviewProtocol` (sets `status=validated`); raises `HTTPException(409)` if editing a validated protocol; Google-style docstrings
- [x] T024 [US1] Implement `backend/src/backend/services/slr_phase_gate.py`: `async def get_slr_unlocked_phases(study_id, db) -> list[int]` — phase 2 requires `ReviewProtocol.status == "validated"`, phase 3 requires completed search execution, phase 4 requires all accepted papers have QA scores from all assigned reviewers, phase 5 requires a `SynthesisResult` with `status=completed`; delegates shared logic to `phase_gate.get_unlocked_phases` for phases 1/3
- [x] T025 [US1] Write unit tests for `slr_protocol_service.py` in `backend/tests/test_slr_protocol_service.py`: test upsert creates and updates; test submit_for_review enqueues job and sets status; test validate_protocol sets status; test 409 on editing a validated protocol; SQLite async session; ≥ 85% coverage
- [x] T026 [US1] Write unit tests for `slr_phase_gate.py` in `backend/tests/test_slr_phase_gate.py`: test each phase gate condition independently; verify phase 2 is locked until protocol is validated; ≥ 85% coverage
- [x] T027 [US1] Implement `backend/src/backend/api/v1/slr/protocol.py`: `GET /slr/studies/{study_id}/protocol` (404 if none), `PUT /slr/studies/{study_id}/protocol` (409 if validated), `POST /slr/studies/{study_id}/protocol/submit-for-review` (202), `POST /slr/studies/{study_id}/protocol/validate` (200); Pydantic request/response models; `Depends(get_db)` + `Depends(get_current_user)`; include router in `backend/src/backend/api/v1/slr/router.py`
- [x] T028 [US1] Implement `backend/src/backend/api/v1/slr/phases.py`: `GET /slr/studies/{study_id}/phases` returning `unlocked_phases`, `protocol_status`, `quality_complete`, `synthesis_complete`; dispatches to `slr_phase_gate.get_slr_unlocked_phases` for SLR studies; include router in `slr/router.py`
- [x] T029 [US1] Write API integration tests for protocol routes in `backend/tests/api/v1/slr/test_protocol.py`: test full CRUD lifecycle; test phase gate blocking; test ARQ job enqueued on submit; SQLite test DB; ≥ 85% coverage
- [x] T030 [P] [US1] Implement Zod schemas and `protocolApi.ts` in `frontend/src/services/slr/protocolApi.ts`: `ReviewProtocolSchema`, `ProtocolReviewResultSchema`; `getProtocol(studyId)`, `upsertProtocol(studyId, data)`, `submitForReview(studyId)`, `validateProtocol(studyId)`, `getPhases(studyId)` — all use `unknown` + Zod parse; JSDoc on all exports
- [x] T031 [P] [US1] Implement `useProtocol` TanStack Query hook in `frontend/src/hooks/slr/useProtocol.ts`: `useProtocol(studyId)` query; `useUpsertProtocol()`, `useSubmitForReview()`, `useValidateProtocol()` mutations; `refetchInterval` polling while `status === "under_review"` to detect when review_report arrives; JSDoc
- [x] T032 [P] [US1] Implement `ProtocolForm` component in `frontend/src/components/slr/ProtocolForm.tsx`: `react-hook-form` + `zod` validation; `useWatch` for conditional `pico_context` field; all 11 protocol fields as controlled inputs; blocked and read-only when `status === "validated"`; ≤ 100 JSX lines (split sections into `ProtocolSection` sub-component); JSDoc
- [x] T033 [P] [US1] Implement `ProtocolReviewReport` component in `frontend/src/components/slr/ProtocolReviewReport.tsx`: renders `ProtocolReviewResult.issues` as a grouped MUI list (by section, with severity chip colours); renders `overall_assessment`; shows loading skeleton while `status === "under_review"`; `React.memo` applied; JSDoc
- [x] T034 [US1] Implement `ProtocolEditorPage` in `frontend/src/pages/slr/ProtocolEditorPage.tsx`: composes `ProtocolForm` + `ProtocolReviewReport` + Submit/Approve action buttons; uses `useProtocol` + `usePhases`; renders MUI `Stepper` showing protocol status (`draft → under_review → validated`); ≤ 100 JSX lines (delegate rendering to sub-components); JSDoc
- [x] T035 [US1] Route SLR study type to `ProtocolEditorPage` as the Phase 1 tab in `frontend/src/pages/StudyPage.tsx`; guard all other phase tabs with `usePhases` — disable/hide if phase not unlocked
- [x] T036 [P] [US1] Write component tests for `ProtocolForm` in `frontend/src/components/slr/__tests__/ProtocolForm.test.tsx`: render, field interaction, Zod validation errors, read-only state; ≥ 85% coverage
- [x] T037 [P] [US1] Write component tests for `ProtocolReviewReport` in `frontend/src/components/slr/__tests__/ProtocolReviewReport.test.tsx`: renders issues list, loading state, empty state; ≥ 85% coverage

**Checkpoint**: `uv run pytest backend/tests/test_slr_protocol_service.py backend/tests/test_slr_phase_gate.py backend/tests/api/v1/slr/test_protocol.py && uv run pytest agents/tests/test_protocol_reviewer.py && cd frontend && npm test` — all pass; manually verify the Protocol tab works end-to-end in the running app.

---

## Phase 4: User Story 2 — Multi-Reviewer Screening with Inter-Rater Agreement (Priority: P2)

**Goal**: Two or more reviewers independently assess candidate papers; the system computes Cohen's Kappa after each round; if Kappa < threshold the Think-Aloud discussion workflow is triggered; pre- and post-discussion Kappa values are recorded.

**Independent Test**: Assign two reviewer accounts to an SLR study; have each independently submit decisions for ≥ 10 papers at the title/abstract stage; verify the system computes a Kappa value, displays it on the study dashboard, and surfaces `DiscussionFlowPanel` when Kappa < 0.6.

### Implementation for User Story 2

- [x] T038 [US2] Implement `backend/src/backend/services/inter_rater_service.py`: `compute_and_store_kappa(study_id, reviewer_a_id, reviewer_b_id, round_type, phase, db) -> InterRaterAgreementRecord` — fetches both reviewers' `PaperDecision` rows for the given round, calls `statistics.safe_cohen_kappa`, stores `InterRaterAgreementRecord`, checks `kappa_value >= settings.slr_kappa_threshold`; `get_records(study_id, db) -> list[InterRaterAgreementRecord]`; structlog bound with `study_id`, `round_type`; Google-style docstrings
- [x] T039 [US2] Write unit tests for `inter_rater_service.py` in `backend/tests/test_inter_rater_service.py`: test Kappa computed and stored correctly; test `threshold_met` flag set correctly; test `kappa_undefined_reason` populated when Kappa is None; SQLite async session; ≥ 85% coverage
- [x] T040 [US2] Implement `backend/src/backend/api/v1/slr/inter_rater.py`: `GET /slr/studies/{study_id}/inter-rater` (list records), `POST /slr/studies/{study_id}/inter-rater/compute` (422 if reviewer hasn't completed the round), `POST /slr/studies/{study_id}/inter-rater/post-discussion` (records post-discussion Kappa); include router in `slr/router.py`
- [x] T041 [US2] Write API integration tests for inter-rater routes in `backend/tests/api/v1/slr/test_inter_rater.py`: test compute endpoint returns correct Kappa; test 422 when assessment round is incomplete; test post-discussion creates a second record; ≥ 85% coverage
- [x] T042 [P] [US2] Implement Zod schemas and `interRaterApi.ts` in `frontend/src/services/slr/interRaterApi.ts`: `InterRaterRecordSchema`; `getInterRaterRecords(studyId)`, `computeKappa(studyId, body)`, `recordPostDiscussionKappa(studyId, body)`; JSDoc
- [x] T043 [P] [US2] Implement `useInterRater` TanStack Query hook in `frontend/src/hooks/slr/useInterRater.ts`: `useInterRaterRecords(studyId)` query; `useComputeKappa()`, `usePostDiscussionKappa()` mutations; JSDoc
- [x] T044 [P] [US2] Implement `InterRaterPanel` component in `frontend/src/components/slr/InterRaterPanel.tsx`: displays latest Kappa value per reviewer pair per round as MUI `Table`; shows threshold status badge (green ✓ / red ✗); shows "Compute Kappa" button when both reviewers have completed the round; `React.memo`; ≤ 100 JSX lines; JSDoc
- [x] T045 [P] [US2] Implement `DiscussionFlowPanel` component in `frontend/src/components/slr/DiscussionFlowPanel.tsx`: renders when `threshold_met === false`; lists disagreed-on papers one at a time; each paper shows reviewer A's and reviewer B's decisions side-by-side; "Mark resolved" action per paper; "Re-compute Kappa" button after all disagreements resolved; useReducer for multi-step flow state; ≤ 100 JSX lines; JSDoc
- [x] T046 [US2] Integrate `InterRaterPanel` and `DiscussionFlowPanel` into the Phase 2 screening view in `frontend/src/pages/phase2/` (add as a collapsible section below the paper list; only visible for SLR study type)
- [x] T047 [P] [US2] Write component tests for `InterRaterPanel` in `frontend/src/components/slr/__tests__/InterRaterPanel.test.tsx`: renders Kappa values; shows threshold status; button state; ≥ 85% coverage
- [x] T048 [P] [US2] Write component tests for `DiscussionFlowPanel` in `frontend/src/components/slr/__tests__/DiscussionFlowPanel.test.tsx`: renders disagreed papers; "Mark resolved" transitions state; ≥ 85% coverage

**Checkpoint**: Verify `InterRaterPanel` appears in the screening view for an SLR study and Kappa is computed after both reviewers submit decisions.

---

## Phase 5: User Story 3 — Study Quality Assessment (Priority: P3)

**Goal**: A researcher configures a quality assessment checklist; each accepted paper generates a pending QA task for each assigned reviewer; quality scores are aggregated per paper; inter-rater Kappa is computed on QA scores.

**Independent Test**: Configure a QA checklist for an SLR study; accept ≥ 3 papers; submit QA scores from two reviewer accounts; verify aggregate quality scores are displayed and Kappa is computed.

### Implementation for User Story 3

- [x] T049 [US3] Implement `backend/src/backend/services/quality_assessment_service.py`: `get_checklist(study_id, db)`, `upsert_checklist(study_id, data, db) -> QualityAssessmentChecklist` (replaces items), `submit_scores(candidate_paper_id, reviewer_id, scores, db) -> list[QualityAssessmentScore]`, `get_scores(candidate_paper_id, db) -> dict[int, list[QualityAssessmentScore]]`, `compute_aggregate_score(scores, checklist_items) -> float` (weighted average); triggers `inter_rater_service.compute_and_store_kappa` for `quality_assessment` round when both reviewers have submitted; structlog; Google-style docstrings
- [x] T050 [US3] Write unit tests for `quality_assessment_service.py` in `backend/tests/test_quality_assessment_service.py`: test checklist CRUD; test weighted aggregate score formula; test Kappa triggered when both reviewers submit; ≥ 85% coverage
- [x] T051 [US3] Implement `backend/src/backend/api/v1/slr/quality.py`: `GET /slr/studies/{study_id}/quality-checklist`, `PUT /slr/studies/{study_id}/quality-checklist`, `GET /slr/papers/{candidate_paper_id}/quality-scores`, `PUT /slr/papers/{candidate_paper_id}/quality-scores`; include router in `slr/router.py`
- [x] T052 [US3] Write API integration tests for quality routes in `backend/tests/api/v1/slr/test_quality.py`: test checklist create/update; test score submission; test aggregate score in response; ≥ 85% coverage
- [x] T053 [P] [US3] Implement Zod schemas and `qualityApi.ts` in `frontend/src/services/slr/qualityApi.ts`: `ChecklistSchema`, `QualityScoresSchema`; `getChecklist(studyId)`, `upsertChecklist(studyId, body)`, `getQualityScores(candidatePaperId)`, `submitQualityScores(candidatePaperId, body)`; JSDoc
- [x] T054 [P] [US3] Implement `useQualityAssessment` TanStack Query hook in `frontend/src/hooks/slr/useQualityAssessment.ts`: queries for checklist and scores; `useUpsertChecklist()` and `useSubmitScores()` mutations; JSDoc
- [x] T055 [P] [US3] Implement `QualityChecklistEditor` component in `frontend/src/components/slr/QualityChecklistEditor.tsx`: `react-hook-form` + Zod for checklist name and dynamic item list; add/remove/reorder items; `scoring_method` select per item; `weight` numeric input; ≤ 100 JSX lines; JSDoc
- [x] T056 [P] [US3] Implement `QualityScoreForm` component in `frontend/src/components/slr/QualityScoreForm.tsx`: renders one row per checklist item with the appropriate input control (checkbox for `binary`, MUI `Slider` for `scale_1_3`/`scale_1_5`); shows notes `TextField`; displays computed aggregate score live via `useWatch`; ≤ 100 JSX lines; JSDoc
- [x] T057 [US3] Implement `QualityAssessmentPage` in `frontend/src/pages/slr/QualityAssessmentPage.tsx`: tab layout — "Checklist Setup" tab (renders `QualityChecklistEditor`) and "Score Papers" tab (renders list of accepted papers, each expandable to show `QualityScoreForm` for the current reviewer); ≤ 100 JSX lines per tab sub-component; JSDoc
- [x] T058 [US3] Add `QualityAssessmentPage` routing in `frontend/src/pages/StudyPage.tsx` for SLR studies (gated by QA phase unlock)
- [x] T059 [P] [US3] Write component tests for `QualityChecklistEditor` in `frontend/src/components/slr/__tests__/QualityChecklistEditor.test.tsx`: add/remove items, validation, submit; ≥ 85% coverage
- [x] T060 [P] [US3] Write component tests for `QualityScoreForm` in `frontend/src/components/slr/__tests__/QualityScoreForm.test.tsx`: renders correct control per scoring method; live aggregate score; ≥ 85% coverage

**Checkpoint**: QA checklist configured, scores submitted from two reviewers, aggregate quality scores displayed, Kappa computed for quality round.

---

## Phase 6: User Story 4 — Data Synthesis (Priority: P4)

**Goal**: A researcher selects a synthesis approach (meta-analysis, descriptive, or qualitative), runs it, views a Forest plot or Funnel plot, and receives a sensitivity analysis result.

**Independent Test**: Use descriptive synthesis on a study with ≥ 3 accepted papers; enter effect-size data; click "Run Synthesis"; verify a Forest plot SVG is displayed and a sensitivity analysis result is returned.

### Implementation for User Story 4

- [x] T061 [US4] Define `SynthesisStrategy` `typing.Protocol` in `backend/src/backend/services/synthesis_strategies.py` with `async def run(self, study_id: int, parameters: dict[str, Any], db: AsyncSession) -> SynthesisOutput` where `SynthesisOutput` is a Pydantic model with `computed_statistics`, `forest_plot_svg`, `funnel_plot_svg`, `qualitative_themes`, `sensitivity_analysis`
- [x] T062 [P] [US4] Implement `MetaAnalysisSynthesizer` in `backend/src/backend/services/synthesis_strategies.py`: fetches effect-size data from `DataExtraction` for all accepted papers; calls `statistics.fixed_effects_meta_analysis` or `random_effects_meta_analysis` based on `parameters["model_type"]` (or auto-selects via Q-test p-value vs `parameters["heterogeneity_threshold"]`); calls `visualization.generate_funnel_plot`; runs sensitivity analysis by re-running meta-analysis on each defined paper subset; Google-style docstrings
- [x] T063 [P] [US4] Implement `DescriptiveSynthesizer` in `backend/src/backend/services/synthesis_strategies.py`: tabulates sample sizes, effect sizes, mean differences, CIs, units per accepted paper; calls `visualization.generate_forest_plot` (raises `ValueError` if < `settings.slr_min_synthesis_papers`); runs sensitivity analysis on defined subsets; Google-style docstrings
- [x] T064 [P] [US4] Implement `QualitativeSynthesizer` in `backend/src/backend/services/synthesis_strategies.py`: accepts `parameters["themes"]` as a list of `{theme_name, paper_ids}` dicts; validates all paper_ids are accepted; stores theme-to-paper mapping in `SynthesisOutput.qualitative_themes`; runs sensitivity by excluding lowest-quality papers and re-mapping themes; Google-style docstrings
- [x] T065 [US4] Implement `backend/src/backend/jobs/synthesis_job.py`: `async def run_synthesis(ctx, *, synthesis_id: int)` — loads `SynthesisResult`, resolves the correct `SynthesisStrategy` implementation via a dispatch map (not if/elif), calls `strategy.run()`, stores results back to `SynthesisResult` with `status=completed` or `status=failed`; structlog bound with `synthesis_id`, `study_id`
- [x] T066 [US4] Register `run_synthesis` in `backend/src/backend/jobs/worker.py` `functions` list
- [x] T067 [US4] Implement `backend/src/backend/services/synthesis_service.py`: `list_results(study_id, db)`, `start_synthesis(study_id, approach, model_type, parameters, db, arq_pool) -> SynthesisResult` (validates QA complete via phase gate, creates `SynthesisResult(status=pending)`, enqueues `run_synthesis`), `get_result(synthesis_id, db)`; structlog; Google-style docstrings
- [x] T068 [US4] Write unit tests for synthesis strategies in `backend/tests/test_synthesis_strategies.py`: mock DB and stats functions; test each strategy produces a `SynthesisOutput` with the expected fields; test `ValueError` for < 3 papers in `DescriptiveSynthesizer`; test heterogeneity threshold auto-selection in `MetaAnalysisSynthesizer`; ≥ 85% coverage
- [x] T069 [US4] Write unit tests for `synthesis_service.py` in `backend/tests/test_synthesis_service.py`: test start_synthesis creates a pending record and enqueues job; test 422 if QA is incomplete; ≥ 85% coverage
- [x] T070 [US4] Implement `backend/src/backend/api/v1/slr/synthesis.py`: `GET /slr/studies/{study_id}/synthesis`, `POST /slr/studies/{study_id}/synthesis` (202), `GET /slr/synthesis/{synthesis_id}`; include router in `slr/router.py`
- [x] T071 [US4] Write API integration tests for synthesis routes in `backend/tests/api/v1/slr/test_synthesis.py`: test list/create/get; test 422 when QA incomplete; test job enqueued; ≥ 85% coverage
- [x] T072 [P] [US4] Implement Zod schemas and `synthesisApi.ts` in `frontend/src/services/slr/synthesisApi.ts`: `SynthesisResultSchema`; `listSynthesisResults(studyId)`, `startSynthesis(studyId, body)`, `getSynthesisResult(synthesisId)`; JSDoc
- [x] T073 [P] [US4] Implement `useSynthesis` TanStack Query hook in `frontend/src/hooks/slr/useSynthesis.ts`: `useSynthesisResults(studyId)` query; `useStartSynthesis()` mutation; `useSynthesisResult(synthesisId)` with `refetchInterval` polling while `status === "running" || status === "pending"`; JSDoc
- [x] T074 [P] [US4] Implement `ForestPlotViewer` component in `frontend/src/components/slr/ForestPlotViewer.tsx`: renders `forest_plot_svg` inline using `dangerouslySetInnerHTML` (SVG is internally generated, not user-supplied); shows loading skeleton while synthesis is running; `React.memo`; ≤ 100 JSX lines; JSDoc
- [x] T075 [P] [US4] Implement `FunnelPlotViewer` component in `frontend/src/components/slr/FunnelPlotViewer.tsx`: same pattern as `ForestPlotViewer` for `funnel_plot_svg`; `React.memo`; JSDoc
- [x] T076 [P] [US4] Implement `SynthesisConfigForm` component in `frontend/src/components/slr/SynthesisConfigForm.tsx`: `react-hook-form` + Zod; `approach` radio group; conditional `model_type` select (meta-analysis only); `heterogeneity_threshold` and `confidence_interval` numeric inputs (meta-analysis); qualitative theme builder (add/remove theme with paper multi-select); `useWatch` for conditional fields; ≤ 100 JSX lines; JSDoc
- [x] T077 [US4] Implement `SynthesisPage` in `frontend/src/pages/slr/SynthesisPage.tsx`: renders `SynthesisConfigForm` + "Run Synthesis" button + results list with `ForestPlotViewer` / `FunnelPlotViewer` / qualitative themes table + sensitivity analysis summary; `useReducer` for multi-step flow state; ≤ 100 JSX lines per sub-component; JSDoc
- [x] T078 [US4] Add `SynthesisPage` routing in `frontend/src/pages/StudyPage.tsx` for SLR studies (gated by synthesis phase unlock)
- [x] T079 [P] [US4] Write component tests for `ForestPlotViewer` in `frontend/src/components/slr/__tests__/ForestPlotViewer.test.tsx`: SVG rendered, loading state, empty state; ≥ 85% coverage
- [x] T080 [P] [US4] Write component tests for `SynthesisConfigForm` in `frontend/src/components/slr/__tests__/SynthesisConfigForm.test.tsx`: conditional fields per approach; validation; ≥ 85% coverage

**Checkpoint**: Run synthesis end-to-end with each of the three approaches on a study with ≥ 3 accepted papers; verify Forest/Funnel plots render and sensitivity analysis is returned.

---

## Phase 7: User Story 5 — Structured SLR Report Export (Priority: P5)

**Goal**: A researcher generates a structured SLR report in LaTeX/Markdown or JSON/CSV after all prior phases are complete; the report contains all required SLR section headings and is populated with study data.

**Independent Test**: Complete all prior phases for a small SLR study; call the report export endpoint with `format=markdown`; verify the response is a downloadable file containing all required section headings populated with study data.

### Implementation for User Story 5

- [x] T081 [US5] Implement `backend/src/backend/services/slr_report_service.py`: `generate_report(study_id, db) -> SLRReport` — assembles a `SLRReport` Pydantic model with all 10 required sections (background, review questions, protocol summary, search process, inclusion/exclusion decisions, quality assessment results, extracted data, synthesis results, validity discussion, recommendations) from the study's DB state; `export_report(report, format) -> tuple[bytes, str, str]` — renders the report as LaTeX/Markdown/JSON/CSV and returns content, MIME type, and filename; raise `HTTPException(422)` if synthesis is not yet complete; structlog; Google-style docstrings
- [x] T082 [US5] Write unit tests for `slr_report_service.py` in `backend/tests/test_slr_report_service.py`: test all 10 sections populated; test each format produces correct MIME type; test 422 if synthesis incomplete; ≥ 85% coverage
- [x] T083 [US5] Implement `backend/src/backend/api/v1/slr/report.py`: `GET /api/v1/studies/{study_id}/export/slr-report?format=latex|markdown|json|csv` — calls `slr_report_service.generate_report` + `export_report`; returns `FileResponse` or `StreamingResponse` with correct `Content-Disposition: attachment` header; include router in `slr/router.py`
- [x] T084 [US5] Write API integration tests for report export in `backend/tests/api/v1/slr/test_report.py`: test each format returns a download with correct MIME type; test 422 when synthesis is incomplete; ≥ 85% coverage
- [x] T085 [P] [US5] Implement `reportApi.ts` and `ReportPage` sub-components in `frontend/src/services/slr/reportApi.ts`: `downloadSLRReport(studyId, format)` — triggers browser download using `fetch` + `URL.createObjectURL`; JSDoc
- [x] T086 [P] [US5] Implement `ReportPage` in `frontend/src/pages/slr/ReportPage.tsx`: renders a format selector (radio: LaTeX, Markdown, JSON, CSV) and a "Download Report" button; shows a disabled state with tooltip if synthesis phase is not complete; uses `useState` for format selection; ≤ 100 JSX lines; JSDoc
- [x] T087 [US5] Add `ReportPage` routing in `frontend/src/pages/StudyPage.tsx` for SLR studies (gated by report phase unlock)
- [x] T088 [P] [US5] Write component tests for `ReportPage` in `frontend/src/pages/slr/__tests__/ReportPage.test.tsx`: format selector, download trigger, disabled state; ≥ 85% coverage

**Checkpoint**: Download a Markdown-format report for a completed SLR study; verify all 10 section headings are present and populated.

---

## Phase 8: User Story 6 — Grey Literature Tracking (Priority: P6)

**Goal**: A researcher can add, list, and remove grey literature sources (technical reports, dissertations, rejected publications, works-in-progress) for a study; sources appear in the generated report.

**Independent Test**: Add a grey literature source with type `dissertation` to an SLR study; verify it appears in the grey literature list and in the generated report's search process section.

### Implementation for User Story 6

- [x] T089 [US6] Implement `backend/src/backend/api/v1/slr/grey_literature.py`: `GET /slr/studies/{study_id}/grey-literature`, `POST /slr/studies/{study_id}/grey-literature` (201), `DELETE /slr/studies/{study_id}/grey-literature/{source_id}` (204); inline service logic is acceptable here (thin CRUD, no complex orchestration); include router in `slr/router.py`
- [x] T090 [US6] Write API integration tests for grey literature routes in `backend/tests/api/v1/slr/test_grey_literature.py`: test list, create, and delete; test 404 on missing source; ≥ 85% coverage
- [x] T091 [P] [US6] Implement Zod schemas and `greyLiteratureApi.ts` in `frontend/src/services/slr/greyLiteratureApi.ts`: `GreyLiteratureSourceSchema`; `listGreyLiterature(studyId)`, `addGreyLiteratureSource(studyId, body)`, `deleteGreyLiteratureSource(studyId, sourceId)`; JSDoc
- [x] T092 [P] [US6] Implement `useGreyLiterature` TanStack Query hook in `frontend/src/hooks/slr/useGreyLiterature.ts`: `useGreyLiterature(studyId)` query; `useAddSource()`, `useDeleteSource()` mutations; JSDoc
- [x] T093 [P] [US6] Implement `GreyLiteraturePanel` component in `frontend/src/components/slr/GreyLiteraturePanel.tsx`: MUI `Table` listing sources with type chip, title, authors, year, and delete action; "Add Source" button opens a `Dialog` with `react-hook-form` form (type select, title, authors, year, url, description); `React.memo`; ≤ 100 JSX lines; JSDoc
- [x] T094 [US6] Implement `GreyLiteraturePage` in `frontend/src/pages/slr/GreyLiteraturePage.tsx`: wraps `GreyLiteraturePanel` with a page header and description; ≤ 100 JSX lines; JSDoc
- [x] T095 [US6] Add `GreyLiteraturePage` routing in `frontend/src/pages/StudyPage.tsx` for SLR studies
- [x] T096 [P] [US6] Write component tests for `GreyLiteraturePanel` in `frontend/src/components/slr/__tests__/GreyLiteraturePanel.test.tsx`: list render, add dialog, delete confirmation; ≥ 85% coverage

**Checkpoint**: Add a grey literature source; verify it appears in the list and is reflected in the report's search process section.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: E2e tests, agent evaluation pipeline, coverage and lint gates, SLR phase gate wired into the existing study phase endpoint.

- [X] T097 Wire `slr_phase_gate.get_slr_unlocked_phases` into the existing `GET /api/v1/studies/{study_id}/phases` endpoint in `backend/src/backend/api/v1/studies/__init__.py` — dispatch to SLR gate when `study.study_type == "systematic_literature_review"`, existing SMS gate otherwise (no if-chain: use a dispatch dict keyed on study type)
- [X] T098 Write Playwright e2e test in `frontend/e2e/slr-workflow.spec.ts`: end-to-end happy path covering protocol creation → AI review → approval → search → screening → Kappa computation → QA → synthesis (descriptive) → Forest plot visible → report download
- [X] T099 [P] Run `uv run ruff check backend/src agents/src db/src` and `uv run ruff format --check` — fix all violations introduced by this feature
- [X] T100 [P] Run `uv run mypy backend/src agents/src db/src` with `strict = true` — resolve all new type errors
- [X] T101 [P] Run `cd frontend && npm run lint && npm run format:check` — resolve all ESLint and Prettier violations
- [X] T102 [P] Run full coverage check: `uv run pytest backend/tests/ --cov=src/backend --cov-fail-under=85` + `uv run pytest agents/tests/ --cov=src/agents --cov-fail-under=85` + `uv run pytest db/tests/ --cov=src/db --cov-fail-under=85` + `cd frontend && npm run test:coverage` — add `# pragma: no cover` annotations with justifications for any intentionally uncovered lines

---

## Phase 10: Feature Completion Documentation *(mandatory — Constitution Principle X)*

**Purpose**: Update all required documentation before the feature branch is merged.

> **These tasks MUST be completed before the feature is marked done. Omitting them is a blocking violation of Constitution Principle X.**

- [X] TDOC1 [P] Update `CLAUDE.md` at repository root: add `007-slr-workflow` entry to **Active Technologies** (already partially done by agent context script); add `scipy`, `scikit-learn`, `numpy` to Python Libraries section; add `SLR_KAPPA_THRESHOLD`, `SLR_MIN_SYNTHESIS_PAPERS` to environment variable documentation
- [X] TDOC2 [P] Update `README.md` at repository root to reflect SLR support: add SLR as a supported study type; note the three synthesis approaches; note grey literature tracking
- [X] TDOC3 [P] Update root `CHANGELOG.md` with a new entry for `007-slr-workflow`: added SLR protocol editor with AI review, multi-reviewer Kappa computation, quality assessment checklists, meta-analysis/descriptive/qualitative synthesis, Forest/Funnel plots, grey literature tracking, structured SLR report export
- [X] TDOC4 [P] Update `README.md` in `backend/`, `agents/`, `db/`, and `frontend/` with the new modules, models, agents, and components introduced by this feature
- [X] TDOC5 [P] Update `CHANGELOG.md` in `backend/`, `agents/`, `db/`, and `frontend/` with the same level of detail as the root changelog entry

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user story phases
- **Phase 3 (US1)**: Depends on Phase 2; independent of US2–US6
- **Phase 4 (US2)**: Depends on Phase 2; integrates with US1 (uses existing screening infrastructure + `statistics.py`); independently testable without US1's protocol flow
- **Phase 5 (US3)**: Depends on Phase 2 and US2 (Kappa computed on QA scores via `inter_rater_service`)
- **Phase 6 (US4)**: Depends on Phase 2 and US3 (synthesis gated on QA completion)
- **Phase 7 (US5)**: Depends on US4 (report requires synthesis results)
- **Phase 8 (US6)**: Depends on Phase 2 only — can run in parallel with US1–US5
- **Phase 9 (Polish)**: Depends on all user story phases
- **Phase 10 (Docs)**: Depends on Phase 9

### User Story Dependencies

| Story | Can Start After | Depends On |
|-------|----------------|------------|
| US1 (Protocol) | Phase 2 | None |
| US2 (Kappa) | Phase 2 | `statistics.py` (Phase 2) |
| US3 (QA) | Phase 2 | US2 (`inter_rater_service`) |
| US4 (Synthesis) | Phase 2 | US3 (QA phase gate) |
| US5 (Report) | Phase 2 | US4 (`synthesis_service`) |
| US6 (Grey Lit) | Phase 2 | None — fully independent |

### Parallel Opportunities Within Each Phase

- **Phase 2**: T009–T014 all parallelizable after T006–T008 complete
- **Phase 3 (US1)**: T015–T016 (prompts), T030–T033 (frontend API/hooks/components) all parallelizable; T017–T020 can run after T015–T016
- **Phase 4 (US2)**: T042–T048 (frontend) parallelizable after T038–T041 (backend) complete
- **Phase 5 (US3)**: T053–T060 (frontend) parallelizable after T049–T052 (backend) complete
- **Phase 6 (US4)**: T062–T064 (three synthesizers) parallelizable; T072–T076 (frontend components) parallelizable
- **Phase 7 (US5)**: T085–T088 (frontend) parallelizable after T081–T084 (backend) complete
- **Phase 8 (US6)**: T091–T096 (frontend) parallelizable after T089–T090 (backend) complete
- **Phase 9**: T099–T102 all parallelizable
- **Phase 10**: TDOC1–TDOC5 all parallelizable

---

## Parallel Example: Phase 2 (Foundational)

```bash
# After T006–T008 complete (sequential — DB models and migration first):

# Launch these in parallel:
Task T009: Add SLR settings to backend/src/backend/core/config.py
Task T010: Implement backend/src/backend/services/statistics.py
Task T011: Add Forest/Funnel plots to backend/src/backend/services/visualization.py
Task T012: Write unit tests for statistics.py
Task T013: Write unit tests for new visualization functions
Task T014: Write unit tests for new ORM models in db/tests/test_slr_models.py
```

## Parallel Example: User Story 1 (Protocol Editor)

```bash
# After Phase 2 complete:

# Launch these in parallel (prompts before agent):
Task T015: Write system.md prompt
Task T016: Write user.md.j2 template

# After T015–T016, in parallel:
Task T017: Implement ProtocolReviewerAgent   Task T030: Implement protocolApi.ts
Task T018: Agent unit tests                  Task T031: Implement useProtocol hook
Task T019: Metamorphic tests                 Task T032: Implement ProtocolForm
Task T020: deepeval pipeline                 Task T033: Implement ProtocolReviewReport
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) — 5 tasks
2. Complete Phase 2 (Foundational) — 9 tasks
3. Complete Phase 3 (US1 — Protocol Editor) — 23 tasks
4. **STOP and VALIDATE**: Protocol tab works end-to-end; AI review returns feedback; approval gates the search phase
5. Demo to stakeholders before building US2–US6

### Incremental Delivery

1. Setup + Foundational → foundation ready (T001–T014)
2. US1 → Protocol Editor working (T015–T037) — MVP
3. US6 → Grey Literature (T089–T096) — small, independent, can be done in parallel with US2
4. US2 → Multi-reviewer Kappa (T038–T048)
5. US3 → Quality Assessment (T049–T060)
6. US4 → Synthesis (T061–T080)
7. US5 → Report Export (T081–T088)
8. Polish + Docs (T097–T102, TDOC1–TDOC5)

### Parallel Team Strategy

With three developers:
- **Developer A**: US1 (Protocol Editor)
- **Developer B**: US6 (Grey Literature) → US2 (Kappa) in sequence
- **Developer C**: Phase 2 foundational (statistics + visualization) → US3 (QA) after US2 complete

---

## Notes

- [P] tasks operate on different files; no incomplete task dependencies
- [Story] label maps each task to its user story for traceability
- Each user story is independently testable after its Checkpoint
- Commit after each task or logical group; refactor commits must be separate from feature commits
- No long methods (>20 lines), switch/if-chain smells, or common code smells in new code
- All Python code: Google-style docstrings; all TypeScript exports: JSDoc
- All new DB models include `created_at`/`updated_at`; optimistic locking on `ReviewProtocol`, `QualityAssessmentScore`, `SynthesisResult`
- Synthesis type dispatch uses a dict map — not an if/elif chain (Constitution Principle III)
- `react-hook-form` with `useWatch` (not `watch`) for all SLR forms
- All API response types validated with Zod schemas (`unknown` + `.parse()`)
- `React.memo` applied deliberately to `ForestPlotViewer`, `FunnelPlotViewer`, `InterRaterPanel`, `GreyLiteraturePanel` (expensive renders)
- Mutation testing (`cosmic-ray` for Python, `stryker` for TypeScript) is triggered by `/speckit.implement` at feature completion — not per PR
