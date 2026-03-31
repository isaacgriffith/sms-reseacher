# Tasks: Research Protocol Definition

**Input**: Design documents from `/specs/010-research-protocol-definition/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/api.md ✓, quickstart.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create all new directories and stub files so downstream parallel tasks never conflict on file creation.

- [X] T001 Create `db/src/db/models/protocols.py` stub (module docstring + empty file) to establish the module path
- [X] T002 [P] Create `backend/src/backend/api/v1/protocols/` package directory with empty `__init__.py` stub
- [X] T003 [P] Create `backend/src/backend/services/` stub files: `protocol_service.py`, `protocol_executor.py`, `protocol_yaml.py` (module docstrings only)
- [X] T004 [P] Create `frontend/src/services/protocols/` directory with stub `protocolsApi.ts` (file-level JSDoc only)
- [X] T005 [P] Create `frontend/src/hooks/protocols/` directory with stub files: `useProtocol.ts`, `useExecutionState.ts`, `useProtocolEditor.ts`
- [X] T006 [P] Create `frontend/src/components/protocols/` directory with stub `.tsx` files: `ProtocolGraph.tsx`, `ProtocolTextEditor.tsx`, `ProtocolNodePanel.tsx`, `QualityGateEditor.tsx`, `EdgeConditionBuilder.tsx`, `ExecutionStateView.tsx`, `ProtocolList.tsx`
- [X] T007 [P] Create `frontend/src/pages/protocols/` directory with stub files: `ProtocolLibraryPage.tsx`, `ProtocolEditorPage.tsx`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: ORM models, migration, and validation utilities that ALL user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T008 Implement all new Python enums in `db/src/db/models/protocols.py`: `ProtocolTaskType` (23 values), `QualityGateType`, `EdgeConditionOperator`, `TaskNodeStatus`, `NodeAssigneeType`, `NodeDataType` — each as `str, enum.Enum` subclasses with Google-style docstrings and PostgreSQL enum names as per data-model.md
- [X] T009 Implement `ResearchProtocol` ORM model in `db/src/db/models/protocols.py`: id, name, description, study_type, is_default_template, owner_user_id FK, version_id (optimistic lock), created_at, updated_at, mapper args, relationships stub — per data-model.md schema
- [X] T010 [P] Implement `ProtocolNode`, `ProtocolNodeInput`, `ProtocolNodeOutput` ORM models in `db/src/db/models/protocols.py`: all columns, FKs, UNIQUE constraints, relationships — per data-model.md
- [X] T011 [P] Implement `QualityGate`, `NodeAssignee` ORM models in `db/src/db/models/protocols.py`: all columns, FKs, JSONB config column — per data-model.md
- [X] T012 Implement `ProtocolEdge` ORM model in `db/src/db/models/protocols.py`: all columns including three optional condition columns (condition_output_name, condition_operator, condition_value), FKs, UNIQUE constraint — per data-model.md (depends on T010)
- [X] T013 [P] Implement `StudyProtocolAssignment` ORM model in `db/src/db/models/protocols.py`: study_id UNIQUE FK, protocol_id FK, assigned_at, assigned_by_user_id — per data-model.md
- [X] T014 [P] Implement `TaskExecutionState` ORM model in `db/src/db/models/protocols.py`: study_id + node_id UNIQUE constraint, status enum, gate_failure_detail JSONB, activated_at, completed_at, audit fields — per data-model.md
- [X] T015 Export all new models from `db/src/db/models/__init__.py` (add imports for all models in protocols.py)
- [X] T016 Write Alembic migration `db/alembic/versions/0018_research_protocol_definition.py`: create all 5 PostgreSQL enum types, create 9 new tables in dependency order (research_protocol → protocol_node → protocol_node_input/output → quality_gate → node_assignee → protocol_edge → study_protocol_assignment → task_execution_state), with full `downgrade()` path — per data-model.md
- [X] T017 Write migration data seeding in `0018_research_protocol_definition.py`: INSERT default protocol templates for all 4 study types (SMS 10 nodes, SLR 12 nodes, Rapid 10 nodes, Tertiary 9 nodes) with correct edges, quality gates encoding FR-022 SMS phase-gate conditions — per data-model.md Migration Seeding section
- [X] T018 Write migration back-fill in `0018_research_protocol_definition.py`: INSERT `study_protocol_assignment` rows for all existing studies (join to default template by study_type) and seed `task_execution_state` rows with status derived from `study.current_phase`
- [X] T019 Implement Pydantic gate config discriminated models in `backend/src/backend/services/protocol_service.py`: `MetricThresholdConfig`, `CompletionCheckConfig`, `HumanSignOffConfig` with Google-style docstrings — per research.md Decision 3
- [X] T020 Implement `VALID_TASK_TYPES_BY_STUDY_TYPE` allowlist dict and `validate_task_type()` helper in `backend/src/backend/services/protocol_service.py` — per data-model.md Validation Rules
- [X] T021 Implement graph validation helpers in `backend/src/backend/services/protocol_service.py`: `_dfs_visit()`, `_detect_cycle()`, `_find_dangling_required_inputs()`, `_check_ambiguous_connections()`, `validate_graph()` — each ≤ 20 lines, per research.md Decision 1
- [X] T022 Write unit tests for graph validation helpers in `backend/tests/services/test_protocol_service.py`: cycle detection (no cycle, simple cycle, complex cycle), dangling input detection, ambiguous connection detection, task type allowlist
- [X] T023 Write ORM model tests in `db/tests/test_protocol_models.py`: create ResearchProtocol with nodes/edges, verify cascade deletes, verify UNIQUE constraints, verify version_id increments on update

**Checkpoint**: Migration can be run (`uv run alembic upgrade head`), default templates exist, graph validation passes — user story work can begin.

---

## Phase 3: User Story 1 — View Default Protocol Graph (Priority: P1) 🎯 MVP

**Goal**: Researcher can open any study, navigate to the Protocol tab, and see the default protocol rendered as a visual graph. Clicking any task node shows its full detail.

**Independent Test**: Create an SMS study, navigate to /studies/{id}/protocol, see the 10-node SMS default graph rendered. Click "Define PICO" node and see inputs, outputs, quality gates, and assignees in a side panel.

### Implementation for User Story 1

- [X] T024 [P] [US1] Implement Pydantic response schemas in `backend/src/backend/api/v1/protocols/schemas.py`: `ProtocolListItemResponse`, `ProtocolNodeInputResponse`, `ProtocolNodeOutputResponse`, `AssigneeResponse`, `QualityGateResponse`, `ProtocolNodeDetailResponse`, `ProtocolEdgeResponse`, `ProtocolDetailResponse`, `ProtocolAssignmentResponse` — all with `model_config = {"from_attributes": True}` and JSDoc/docstrings
- [X] T025 [P] [US1] Implement `ProtocolService.list_protocols(user_id, study_type_filter, db)` in `backend/src/backend/services/protocol_service.py`: query returns researcher's custom protocols + all default templates, optional study_type filter — async, with structlog logging
- [X] T026 [US1] Implement `ProtocolService.get_protocol_detail(protocol_id, user_id, db)` in `backend/src/backend/services/protocol_service.py`: load protocol with all nodes (inputs, outputs, quality gates, assignees) and edges; raise 403 if not owner and not default template; raise 404 if not found (depends on T025)
- [X] T027 [US1] Implement `GET /protocols` and `GET /protocols/{protocol_id}` endpoints in `backend/src/backend/api/v1/protocols/library.py`: auth via `Depends(get_current_user)`, delegate to ProtocolService, return Pydantic responses — per contracts/api.md (depends on T024, T026)
- [X] T028 [US1] Register protocol router in `backend/src/backend/api/v1/protocols/__init__.py` and include in `backend/src/backend/main.py` under prefix `/api/v1`
- [X] T029 [US1] Implement `GET /studies/{study_id}/protocol-assignment` endpoint in `backend/src/backend/api/v1/protocols/assignment.py`: load `StudyProtocolAssignment` for study, verify requester is a study member — per contracts/api.md
- [X] T030 [P] [US1] Implement `protocolsApi.ts` service functions in `frontend/src/services/protocols/protocolsApi.ts`: `listProtocols(studyType?)`, `getProtocol(id)`, `getProtocolAssignment(studyId)` — typed with Zod schemas for response validation
- [X] T031 [P] [US1] Implement `useProtocol.ts` custom hooks in `frontend/src/hooks/protocols/useProtocol.ts`: `useProtocolList(studyType?)` and `useProtocolDetail(id)` using TanStack Query `useQuery` — with Google-style JSDoc
- [X] T032 [US1] Implement `ProtocolGraph.tsx` read-only D3 visualization in `frontend/src/components/protocols/ProtocolGraph.tsx`: D3 force-directed layout, SVG nodes (rect+label) and edges (path+arrowhead), click handler to select node, `useEffect` with simulation cleanup, position_x/y initialization from data or force layout — ≤ 100 JSX lines (D3 logic in `useEffect`)
- [X] T033 [P] [US1] Implement `ProtocolNodePanel.tsx` read-only detail panel in `frontend/src/components/protocols/ProtocolNodePanel.tsx`: MUI Drawer/Card showing selected node's label, description, task_type, inputs, outputs, quality gates, assignees — ≤ 100 JSX lines
- [X] T034 [P] [US1] Implement `ProtocolList.tsx` in `frontend/src/components/protocols/ProtocolList.tsx`: MUI List of ResearchProtocol items (name, study_type badge, is_default_template indicator) — used in ProtocolLibraryPage; ≤ 100 JSX lines
- [X] T035 [US1] Implement `ProtocolLibraryPage.tsx` in `frontend/src/pages/protocols/ProtocolLibraryPage.tsx`: uses `useProtocolList`, renders `ProtocolList`, links to ProtocolEditorPage for each item — read-only view for US1; ≤ 100 JSX lines
- [X] T036 [US1] Add "Protocol" tab to the study detail page (update `frontend/src/pages/StudyPage.tsx` or equivalent study routing): shows `ProtocolGraph` + `ProtocolNodePanel` for the study's assigned protocol, fetched via `useProtocolDetail` + `getProtocolAssignment`
- [X] T037 [US1] Write integration tests for protocol list and detail endpoints in `backend/tests/integration/api/protocols/test_protocols_library.py`: GET /protocols returns default templates + researcher's protocols; GET /protocols/{id} returns full graph; 403 on other researcher's protocol; 404 on missing
- [X] T038 [US1] Write integration test for protocol assignment endpoint in `backend/tests/integration/api/protocols/test_protocols_assignment.py`: GET /studies/{id}/protocol-assignment returns default template assignment for existing study

**Checkpoint**: Run `uv run pytest backend/tests/api/v1/test_protocols_library.py backend/tests/api/v1/test_protocols_assignment.py -v` — all pass. Navigate to any study → Protocol tab to see D3 graph.

---

## Phase 4: User Story 2 — Create and Edit a Custom Protocol (Priority: P2)

**Goal**: Researcher can copy a default protocol, edit it in either the visual or YAML editor (with immediate sync), save, and reopen with all changes intact. Validation catches cycles, dangling inputs, and unknown task types before save.

**Independent Test**: Copy the default SMS protocol, remove the SnowballSearch node in the visual editor, verify the YAML editor reflects the removal immediately, save successfully, reopen the protocol — SnowballSearch node is absent.

### Implementation for User Story 2

- [X] T039 [US2] Implement `ProtocolService.copy_protocol(source_id, user_id, new_name, db)` in `backend/src/backend/services/protocol_service.py`: deep-copy all nodes (inputs, outputs, quality gates, assignees) and edges; set new owner_user_id; reject if source is another researcher's non-default protocol
- [X] T040 [US2] Implement `ProtocolService.create_protocol(payload, user_id, db)` in `backend/src/backend/services/protocol_service.py`: validate full graph (calls validate_graph), persist all nodes/edges/gates; 400 on validation failure; 409 on duplicate name
- [X] T041 [US2] Implement `ProtocolService.update_protocol(protocol_id, payload, user_id, db)` in `backend/src/backend/services/protocol_service.py`: check version_id for optimistic lock (raise 409 on mismatch); reject if not owner or is_default_template; validate full updated graph; persist atomically
- [X] T042 [US2] Implement `ProtocolService.delete_protocol(protocol_id, user_id, db)` in `backend/src/backend/services/protocol_service.py`: reject if not owner or is_default_template; check no active StudyProtocolAssignment; raise 409 with blocking study IDs if assigned
- [X] T043 [US2] Add Pydantic request schemas to `backend/src/backend/api/v1/protocols/schemas.py`: `ProtocolCopyRequest`, `ProtocolCreateRequest`, `ProtocolUpdateRequest` (with version_id) — per contracts/api.md
- [X] T044 [US2] Implement `POST /protocols`, `PUT /protocols/{id}`, `DELETE /protocols/{id}` endpoints in `backend/src/backend/api/v1/protocols/library.py`: auth + delegate to ProtocolService; 201/200/204 success; proper error codes — per contracts/api.md
- [X] T045 [P] [US2] Implement `useProtocolEditor.ts` graph editor state in `frontend/src/hooks/protocols/useProtocolEditor.ts`: `useReducer(graphReducer, ...)` with actions: `SET_GRAPH`, `ADD_NODE`, `REMOVE_NODE`, `UPDATE_NODE`, `ADD_EDGE`, `REMOVE_EDGE`, `UPDATE_EDGE`, `SELECT_NODE`, `SET_YAML`; `yamlText` derived from graph state via serialisation; `graphState` derived from YAML parse (debounced 300ms)
- [X] T046 [P] [US2] Implement graph↔YAML serialisation utilities in `frontend/src/hooks/protocols/useProtocolEditor.ts`: `graphToYaml(graph): string` and `yamlToGraph(yaml): GraphState | ParseError` — using a YAML library (js-yaml, already a transitive dependency)
- [X] T047 [US2] Upgrade `ProtocolGraph.tsx` to edit mode in `frontend/src/components/protocols/ProtocolGraph.tsx`: add drag-to-reposition nodes (D3 drag behaviour updating position_x/y in graph state), add click-to-select-edge, add button to add/remove nodes/edges dispatching to `useProtocolEditor` reducer — keep ≤ 100 JSX lines; extract D3 imperative setup to `useProtocolD3.ts` hook
- [X] T048 [P] [US2] Create `frontend/src/hooks/protocols/useProtocolD3.ts`: extracts all D3 force simulation + drag setup from ProtocolGraph.tsx; returns ref for SVG container and render function; with cleanup
- [X] T049 [US2] Implement `ProtocolTextEditor.tsx` in `frontend/src/components/protocols/ProtocolTextEditor.tsx`: MUI-styled `<textarea>` or CodeMirror-lite YAML editor (no new dep — use `<textarea>` with monospace styling); `onChange` dispatches `SET_YAML` to editor reducer; shows parse errors inline; value from `yamlText` in editor state — ≤ 100 JSX lines
- [X] T050 [P] [US2] Upgrade `ProtocolNodePanel.tsx` to edit mode in `frontend/src/components/protocols/ProtocolNodePanel.tsx`: add react-hook-form form for editing label, description, is_required; `QualityGateEditor` and `EdgeConditionBuilder` sub-forms; form submit dispatches `UPDATE_NODE` to reducer — keep ≤ 100 JSX lines; split sub-forms into separate components if needed
- [X] T051 [P] [US2] Implement `QualityGateEditor.tsx` in `frontend/src/components/protocols/QualityGateEditor.tsx`: gate_type selector (MUI Select); conditional fields per type using `useWatch`; Zod validation schema; dispatches gate config to reducer — ≤ 100 JSX lines
- [X] T052 [P] [US2] Implement `EdgeConditionBuilder.tsx` in `frontend/src/components/protocols/EdgeConditionBuilder.tsx`: output_name selector (populated from source node's output names), operator MUI Select (gt/gte/lt/lte/eq/neq), numeric value input; all Zod-validated; null condition = unconditional edge — ≤ 100 JSX lines
- [X] T053 [US2] Implement `ProtocolEditorPage.tsx` in `frontend/src/pages/protocols/ProtocolEditorPage.tsx`: loads protocol via `useProtocolDetail`, initialises `useProtocolEditor` reducer, renders split-pane layout (left: ProtocolGraph edit mode, right: ProtocolTextEditor); Save button calls `PUT /protocols/{id}` with current graph + version_id; shows 409 conflict dialog — ≤ 100 JSX lines
- [X] T054 [US2] Add "Copy to Custom Protocol" button to ProtocolLibraryPage / protocol view panel in `frontend/src/pages/protocols/ProtocolLibraryPage.tsx`: calls `POST /protocols` with `copy_from_protocol_id`, redirects to ProtocolEditorPage on success
- [X] T055 [US2] Add `createProtocol`, `updateProtocol`, `deleteProtocol` mutation functions to `frontend/src/services/protocols/protocolsApi.ts` and corresponding `useMutation` hooks to `frontend/src/hooks/protocols/useProtocol.ts`
- [X] T056 [US2] Write integration tests for create/update/delete endpoints in `backend/tests/api/v1/test_protocols_library.py`: POST copy (deep-copy verified); PUT success; PUT 409 version conflict; PUT 403 on default template; DELETE success; DELETE 409 when assigned
- [X] T057 [US2] Write service unit tests in `backend/tests/services/test_protocol_service.py`: copy_protocol (deep copy verified), update_protocol (optimistic lock), delete_protocol (assigned study blocked), validate_graph comprehensive (cycle, dangling, ambiguous, task type allowlist violations)

**Checkpoint**: Run `uv run pytest backend/tests/services/test_protocol_service.py backend/tests/api/v1/test_protocols_library.py -v` — all pass. Complete editor round-trip: copy default → edit in both editors simultaneously → save → reopen → verify changes.

---

## Phase 5: User Story 3 — Assign Protocol to a Study and Execute It (Priority: P2)

**Goal**: Researcher assigns a protocol to a study; the system activates tasks in topological order as predecessors complete and quality gates pass; all study members see live execution state.

**Independent Test**: Assign a custom protocol to a study, mark the first task complete (via API), verify the second task becomes active, verify all study members see the updated state via the execution state endpoint.

### Implementation for User Story 3

- [X] T058 [P] [US3] Implement `ProtocolAssignmentService` in `backend/src/backend/services/protocol_executor.py`: `assign_protocol(study_id, protocol_id, user_id, db)` — checks requester is study admin, validates protocol study_type matches study's, checks no active TaskExecutionState, upserts StudyProtocolAssignment, creates TaskExecutionState rows (all PENDING), activates start nodes (no predecessors)
- [X] T059 [P] [US3] Implement `ProtocolExecutorService.activate_eligible_tasks(study_id, db)` in `backend/src/backend/services/protocol_executor.py`: load all PENDING task states, for each check if all predecessor edges have source node in COMPLETE status, transition qualifying tasks to ACTIVE via topological traversal — O(V+E), decomposed into `_get_predecessor_statuses()` and `_should_activate()`
- [X] T060 [US3] Implement `ProtocolExecutorService.complete_task(study_id, task_id, db)` in `backend/src/backend/services/protocol_executor.py`: mark task ACTIVE→COMPLETE; call gate evaluation (to be implemented in US4 — stub returning all-pass for now); call `activate_eligible_tasks()`; handle conditional edges (evaluate condition against study model data, skip target if false); return updated execution state — per research.md Decision 7
- [X] T061 [US3] Implement `PUT /studies/{study_id}/protocol-assignment` and `GET /studies/{study_id}/execution-state` endpoints in `backend/src/backend/api/v1/protocols/assignment.py`: delegate to ProtocolAssignmentService and ProtocolExecutorService — per contracts/api.md
- [X] T062 [US3] Implement `POST /studies/{study_id}/execution-state/{task_id}/complete` endpoint in `backend/src/backend/api/v1/protocols/execution_state.py`: auth check (study admin or task assignee), delegate to `ProtocolExecutorService.complete_task()`, return full execution state response — per contracts/api.md
- [X] T063 [US3] Register `execution_state.py` router in `backend/src/backend/api/v1/protocols/__init__.py` alongside existing protocol endpoints
- [X] T064 [P] [US3] Add `assignProtocol(studyId, protocolId)` and `getExecutionState(studyId)` and `completeTask(studyId, taskId)` to `frontend/src/services/protocols/protocolsApi.ts`
- [X] T065 [P] [US3] Implement `useExecutionState.ts` in `frontend/src/hooks/protocols/useExecutionState.ts`: `useQuery` with `refetchInterval: 5000` for studies with any ACTIVE task, disabled polling once all tasks COMPLETE or SKIPPED — per research.md Decision 7 (5-second update SC-005)
- [X] T066 [US3] Implement `ExecutionStateView.tsx` in `frontend/src/components/protocols/ExecutionStateView.tsx`: renders all tasks grouped by status (kanban columns: Pending / Active / Complete / Skipped / Gate Failed); each task card shows label, task_type, activated_at / completed_at; "Mark Complete" button on ACTIVE tasks; uses `useExecutionState` with polling — ≤ 100 JSX lines
- [X] T067 [US3] Add "Execution" sub-tab to the study Protocol tab (added in US1 T036): shows `ExecutionStateView`; visible to all study members; "Mark Complete" only visible to study admin or task assignees
- [X] T068 [US3] Implement protocol assignment UI in `ProtocolLibraryPage.tsx`: "Assign to Study" action on each protocol card, study selector dialog, calls `assignProtocol` mutation with confirmation if replacing existing assignment — requires study to not be actively executing
- [X] T069 [US3] Write integration tests for assignment and execution endpoints in `backend/tests/integration/api/protocols/test_protocols_execution.py`: assign protocol, verify TaskExecutionState created; complete first task, verify downstream task becomes ACTIVE; 409 on reassign during execution; 403 on non-admin complete-task call
- [X] T070 [US3] Write executor service unit tests in `backend/tests/unit/services/test_protocol_executor.py`: activate_eligible_tasks (linear chain, diamond DAG, conditional edge evaluation), complete_task state transitions, assign_protocol creates correct TaskExecutionState count


**Checkpoint**: Run `uv run pytest backend/tests/api/v1/test_protocols_execution.py backend/tests/services/test_protocol_executor.py -v` — all pass. Full protocol assign + execute round-trip works end-to-end.

---

## Phase 6: User Story 4 — Quality Gate Failure Remediation (Priority: P3)

**Goal**: When a task's quality gate fails, the researcher sees the exact measured metric, the threshold, and a specific remediation recommendation in the same view. Human sign-off gates surface an approve button to the study admin.

**Independent Test**: Mark a ScreenPapers task complete on a study where Cohen's Kappa is below 0.6; the API response includes `gate_result: "failed"` with measured_value, threshold, and remediation text. The frontend ExecutionStateView shows a failure card with the remediation message.

### Implementation for User Story 4

- [X] T071 [P] [US4] Implement `QualityGateEvaluator` strategy in `backend/src/backend/services/protocol_executor.py`: `_GATE_EVALUATORS: dict[QualityGateType, GateEvaluator]` dispatch dict; three strategy functions `_eval_metric_threshold(gate, study_id, db)`, `_eval_completion_check(gate, study_id, db)`, `_eval_human_sign_off(gate)` — each ≤ 20 lines; `evaluate_all_gates(node_id, study_id, db) -> GateResult`
- [X] T072 [P] [US4] Implement `REMEDIATION_MESSAGES: dict[str, str]` in `backend/src/backend/services/protocol_executor.py`: hardcoded remediation strings for known metric names (kappa_coefficient, accepted_paper_count, test_set_recall, coverage_recall) — per contracts/api.md Remediation Notes section
- [X] T073 [US4] Implement metric readers for `_eval_metric_threshold` in `backend/src/backend/services/protocol_executor.py`: `_read_metric(metric_name, study_id, db) -> float | None` — dispatch dict mapping metric names to async reader functions that query existing study models (InterRaterAgreementRecord.kappa, CandidatePaper count, etc.) — ≤ 20 lines per reader
- [X] T074 [US4] Wire gate evaluation into `ProtocolExecutorService.complete_task()` (replace stub from US3): call `evaluate_all_gates()` after task marked ACTIVE, on any gate failure persist `gate_failure_detail` JSONB to TaskExecutionState and set status = GATE_FAILED (not COMPLETE), return failure detail in response — per contracts/api.md `/complete` endpoint response
- [X] T075 [US4] Implement `POST /studies/{study_id}/execution-state/{task_id}/approve` endpoint in `backend/src/backend/api/v1/studies/execution_state.py`: verify task is in GATE_FAILED status with a pending human_sign_off gate; verify requester is study admin; clear gate failure, set COMPLETE, call activate_eligible_tasks — per contracts/api.md
- [X] T076 [P] [US4] Add `approveTask(studyId, taskId)` to `frontend/src/services/protocols/protocolsApi.ts` and corresponding `useMutation` hook in `frontend/src/hooks/protocols/useExecutionState.ts`
- [X] T077 [US4] Upgrade `ExecutionStateView.tsx` gate failure display in `frontend/src/components/protocols/ExecutionStateView.tsx`: GATE_FAILED task cards show MUI Alert (severity=error) with measured_value, threshold, remediation text from `gate_failure_detail`; "Approve" button visible on GATE_FAILED tasks with human_sign_off gate type (study admin only); calls `approveTask` mutation
- [X] T078 [US4] Write gate evaluation unit tests in `backend/tests/services/test_protocol_executor.py`: metric_threshold gate pass/fail (mock metric reader), completion_check gate pass/fail, human_sign_off gate detection, REMEDIATION_MESSAGES coverage for all metric names, full complete_task with gate failure → GATE_FAILED status → approve → COMPLETE sequence
- [X] T079 [US4] Write integration tests for gate failure + approve endpoints in `backend/tests/api/v1/test_protocols_execution.py`: complete_task with failing kappa gate returns 200 with gate_result=failed; task status = GATE_FAILED in DB; approve by admin succeeds; approve by non-admin returns 403; approve on non-GATE_FAILED task returns 409

**Checkpoint**: Run `uv run pytest backend/tests/services/test_protocol_executor.py backend/tests/api/v1/test_protocols_execution.py -v` — all pass. Mark ScreenPapers complete with low Kappa → see failure card with remediation in UI.

---

## Phase 7: User Story 5 — Export, Version Control, and Re-import Protocol (Priority: P4)

**Goal**: Researcher can export any of their custom protocols (or a default template) as a YAML file, commit it to version control, re-import it, and get an identical graph.

**Independent Test**: Export a 10-node SMS protocol as YAML, re-import it, compare node count / edge count / quality gate configs — 100% identical. Import a YAML with a cycle → 400 with specific error.

### Implementation for User Story 5

- [X] T080 [P] [US5] Implement `ProtocolYamlService.export(protocol_id, user_id, db) -> str` in `backend/src/backend/services/protocol_yaml.py`: serialize ResearchProtocol to YAML string using `ProtocolExportSchema` Pydantic model (schema version, name, study_type, nodes with all sub-entities, edges with optional condition) — per research.md Decision 6
- [X] T081 [P] [US5] Implement `ProtocolYamlService.import_yaml(yaml_str, user_id, db) -> ResearchProtocol` in `backend/src/backend/services/protocol_yaml.py`: parse YAML → `ProtocolExportSchema` (raise 400 on parse error or unsupported schema_version); validate graph (reuse `ProtocolService.validate_graph()`); persist as new custom protocol owned by user_id
- [X] T082 [US5] Implement `GET /protocols/{id}/export` endpoint in `backend/src/backend/api/v1/protocols/library.py`: call `ProtocolYamlService.export()`; return `StreamingResponse` with `application/x-yaml` content type and `Content-Disposition: attachment; filename="protocol-{name}.yaml"` — per contracts/api.md
- [X] T083 [US5] Implement `POST /protocols/import` endpoint in `backend/src/backend/api/v1/protocols/library.py`: accept `multipart/form-data` with `file` field; read bytes, decode UTF-8, call `ProtocolYamlService.import_yaml()`; return 201 with full ProtocolDetailResponse — per contracts/api.md
- [X] T084 [P] [US5] Add `exportProtocol(id)` (triggers file download) and `importProtocol(file: File)` to `frontend/src/services/protocols/protocolsApi.ts`; add `useImportProtocol` mutation hook to `frontend/src/hooks/protocols/useProtocol.ts`
- [X] T085 [US5] Add Export and Import buttons to `ProtocolLibraryPage.tsx` in `frontend/src/pages/protocols/ProtocolLibraryPage.tsx`: Export button on each protocol row triggers `exportProtocol` download; Import button opens file picker (`<input type="file" accept=".yaml,.yml">`), calls `importProtocol` mutation, refreshes list on success, shows validation errors inline
- [X] T086 [US5] Write YAML round-trip tests in `backend/tests/services/test_protocol_yaml.py`: export→import produces identical graph (node count, edge count, quality gate configs, condition operators); import cycle → ValidationError; import unknown task type → ValidationError; import unsupported schema version → 400
- [X] T087 [US5] Write integration tests for export/import endpoints in `backend/tests/api/v1/test_protocols_library.py`: GET export returns YAML bytes with correct Content-Type; POST import with valid YAML returns 201 with matching graph; POST import with cycle returns 400 with specific error message

**Checkpoint**: Run `uv run pytest backend/tests/services/test_protocol_yaml.py -v` — all round-trip tests pass. Export a protocol → download YAML → re-import → verify identical.

---

## Phase 8: User Story 6 — Reset Protocol to Default (Priority: P4)

**Goal**: Researcher can reset a study's protocol to the platform default for its study type, with a confirmation prompt, and the reset is blocked while the study is executing.

**Independent Test**: Assign a custom protocol to a study, call `DELETE /studies/{id}/protocol-assignment` with `{"confirm_reset": true}`, verify the study's assignment now points to the default template. Attempt same on an actively-executing study → 409.

### Implementation for User Story 6

- [X] T088 [US6] Implement `ProtocolAssignmentService.reset_to_default(study_id, user_id, db)` in `backend/src/backend/services/protocol_executor.py`: verify requester is study admin; block if any TaskExecutionState has status=ACTIVE; look up default template for study's study_type; update StudyProtocolAssignment.protocol_id; re-seed TaskExecutionState rows for the new (default) protocol (delete old states, create new PENDING states, activate start nodes)
- [X] T089 [US6] Implement `DELETE /studies/{study_id}/protocol-assignment` endpoint in `backend/src/backend/api/v1/protocols/assignment.py`: require `{"confirm_reset": true}` in body; 400 if not confirmed; delegate to `ProtocolAssignmentService.reset_to_default()` — per contracts/api.md
- [X] T090 [P] [US6] Add `resetProtocol(studyId)` mutation to `frontend/src/services/protocols/protocolsApi.ts` and `useResetProtocol` hook to `frontend/src/hooks/protocols/useProtocol.ts`
- [X] T091 [US6] Add "Reset to Default" button in the study Protocol tab (added in US1 T036): clicking opens MUI Dialog with warning text ("All custom configuration will be lost.") and Confirm/Cancel buttons; Confirm calls `useResetProtocol` mutation; on success, refetch protocol assignment and execution state
- [X] T092 [US6] Write integration tests for reset endpoint in `backend/tests/api/v1/test_protocols_assignment.py`: reset succeeds when study not executing (assignment points to default, old TaskExecutionStates replaced); reset blocked when ACTIVE task exists (409); reset without confirm_reset=true returns 400; non-admin reset returns 403

**Checkpoint**: Run `uv run pytest backend/tests/api/v1/test_protocols_assignment.py -v` — all pass. Full reset flow: custom protocol → Reset → confirm → default template restored.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation, performance checks, and coverage gate.

- [X] T093 Write Playwright e2e test in `frontend/e2e/protocols.spec.ts`: full happy path — create SMS study → view default protocol graph → click node to see detail → copy to custom → edit YAML (remove a node) → verify visual updates → save → assign to study → mark first task complete → verify downstream task activates → export YAML → re-import → verify identical graph
- [X] T094 Validate 85% test coverage gate for backend: run `uv run --package sms-backend pytest backend/tests/ --cov=src/backend --cov-report=term-missing --cov-fail-under=85`; remediate any gaps in protocol_service.py, protocol_executor.py, or protocol_yaml.py
- [X] T095 [P] Validate 85% test coverage gate for db: run `uv run --package sms-db pytest db/tests/ --cov=src/db --cov-report=term-missing --cov-fail-under=85`; remediate any gaps in protocols.py model file
- [X] T096 [P] Validate frontend coverage gate: run `cd frontend && npm run test:coverage`; remediate any gaps in protocol hooks and service functions
- [X] T097 Run full linting + type check pass: `uv run ruff check backend/src agents/src db/src` and `uv run mypy backend/src db/src`; fix any issues in new files; `cd frontend && npm run lint && npm run format:check`
- [X] T098 [P] Verify SC-005 (5-second update latency): manually test that `ExecutionStateView` receives updated task status within 5 seconds of task completion; adjust `refetchInterval` if needed in `useExecutionState.ts`
- [X] T099 Verify SC-007 (FR-022 backward compat): run existing SMS workflow integration tests without modification; confirm all pass with migration applied — `uv run pytest backend/tests/ -k "sms" -v`

---

## Phase 10: Feature Completion Documentation *(mandatory — Constitution Principle X)*

**Purpose**: Update all required documentation before the feature branch is merged.

- [X] TDOC1 [P] Update `CLAUDE.md` at repository root: add `010-research-protocol-definition` section under Active Technologies (Python 3.14/TS 5.4, no new deps, migration 0018); add Research Protocol Definition section under Recent Changes describing all new capabilities (protocol graph model, dual editor, quality gates, YAML export/import, protocol executor service, 4 default templates)
- [X] TDOC2 [P] Update root `README.md` to reflect new protocol definition capability in the project capabilities section
- [X] TDOC3 [P] Update root `CHANGELOG.md` with new versioned entry: list all added capabilities (protocol graph model, dual editor, quality gates with remediation, YAML import/export, runtime execution, default templates for all 4 study types, migration 0018)
- [X] TDOC4 [P] Update `README.md` in `backend/`, `db/`, `frontend/` subproject directories to document new modules (protocol_service, protocol_executor, protocol_yaml; protocols.py models; protocols API routes; frontend protocol components)
- [X] TDOC5 [P] Update `CHANGELOG.md` in `backend/`, `db/`, `frontend/` subproject directories with feature-level detail matching root changelog entry

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — **BLOCKS all user stories**
- **Phase 3 (US1)**: Depends on Phase 2 — first deliverable, MVP
- **Phase 4 (US2)**: Depends on Phase 2 (and reuses ProtocolService from Phase 3 T025-T026)
- **Phase 5 (US3)**: Depends on Phase 2 + Phase 3 (needs GET /protocols, assignment endpoint)
- **Phase 6 (US4)**: Depends on Phase 5 (wires into complete_task stub from US3)
- **Phase 7 (US5)**: Depends on Phase 2 + Phase 4 (uses ProtocolService.validate_graph)
- **Phase 8 (US6)**: Depends on Phase 5 (uses ProtocolAssignmentService)
- **Phase 9 (Polish)**: Depends on all prior phases
- **Phase 10 (Docs)**: Depends on Phase 9

### User Story Dependencies

- **US1 (P1)**: Independent — only needs Foundational phase
- **US2 (P2)**: Reuses ProtocolService methods from US1 — start after US1 T025-T026 complete
- **US3 (P2)**: Needs US1 GET /protocols + assignment endpoint — start after US1 T029
- **US4 (P3)**: Wires into US3 complete_task stub — start after US3 T060
- **US5 (P4)**: Independent of US3/US4 — needs only US2 validate_graph
- **US6 (P4)**: Needs US3 ProtocolAssignmentService — start after US3 T058

### Within Each User Story

- Models/enums before services before endpoints
- Backend services before frontend API client
- Frontend service before hooks before components before pages

---

## Parallel Opportunities

### Phase 2 (Foundational) — run together

```
T008 (enums) → T009 (ResearchProtocol) → T010, T011 in parallel → T012 → T013, T014 in parallel
→ T015 → T016+T017+T018 (migration) → T019+T020+T021 in parallel → T022, T023 in parallel
```

### Phase 3 (US1) — backend + frontend in parallel after T028

```
Backend: T024 → T025 → T026 → T027 → T028 → T029, T037, T038 in parallel
Frontend (starts after T027): T030, T031 in parallel → T032, T033, T034 in parallel → T035 → T036
```

### Phase 4 (US2) — many parallel groups

```
Backend: T039, T040, T041, T042 in parallel → T043 → T044
Frontend: T045, T046 in parallel → T047, T048, T049, T050, T051, T052 in parallel → T053, T054, T055 in parallel
Tests: T056, T057 in parallel (after backend complete)
```

### Phase 6 (US4) — parallel evaluator implementation

```
T071, T072 in parallel → T073 → T074 → T075 → T076, T077 in parallel → T078, T079 in parallel
```

---

## Implementation Strategy

### MVP (Phase 1 + 2 + Phase 3 only)

1. Complete Phase 1: Setup (T001–T007)
2. Complete Phase 2: Foundational (T008–T023)
3. Complete Phase 3: US1 (T024–T038)
4. **STOP and VALIDATE**: Researcher can view default protocol graph and inspect any node. Run `uv run alembic upgrade head`, start app, navigate to any study → Protocol tab.
5. Demo: default SMS protocol as D3 graph, click nodes to inspect.

### Incremental Delivery

1. Phases 1+2+3 → **US1 MVP**: view-only protocol graphs
2. Phase 4 → **US2**: create and edit custom protocols (dual editor)
3. Phase 5 → **US3**: assign and execute protocols
4. Phase 6 → **US4**: quality gate failure remediation
5. Phases 7+8 → **US5+US6**: export/import + reset
6. Phase 9 → polish + e2e
7. Phase 10 → documentation

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Verify migration seeds correctly before starting US1 frontend work (`uv run alembic upgrade head` + check ResearchProtocol count = 4)
- Commit refactor vs feature tasks separately per Constitution Principle IV
- No long methods (>20 lines), no if-chains — use dispatch dicts throughout (gate evaluators, task type allowlist, metric readers)
- All new `.py` files: module docstring as first statement; all new `.ts/.tsx` files: JSDoc block before imports
- All new Python functions/classes: Google-style docstrings; all new exported TS functions: JSDoc
- New DB models include created_at/updated_at audit fields; ResearchProtocol + TaskExecutionState include version_id
- React components ≤ 100 JSX lines; D3 imperative logic extracted to useProtocolD3.ts hook
- useReducer for graph editor state (>3 related useState); useWatch for reactive gate form fields
- Before marking complete: run `uv run pytest --cov-fail-under=85` (backend + db), `npm run test:coverage` (frontend), `uv run mypy`, `uv run ruff check`, mutation testing on backend + db + frontend subprojects
