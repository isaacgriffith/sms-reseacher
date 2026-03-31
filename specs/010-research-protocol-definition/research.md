# Research: Research Protocol Definition (Feature 010)

**Branch**: `010-research-protocol-definition`
**Date**: 2026-03-30
**Status**: Complete — all unknowns resolved

---

## Decision 1: Graph Storage Strategy

**Decision**: Adjacency-list in relational tables (`protocol_node` + `protocol_edge`).

**Rationale**: The codebase has no graph database dependency. A simple relational adjacency list is idiomatic with SQLAlchemy 2.x, supports all required queries (topological traversal, predecessor/successor lookup, dangling-input detection, cycle detection), and aligns with how every other structured entity in the project is stored. Graph size is small (typical research protocol ≤ 20 nodes).

**Alternatives considered**:
- **JSON blob on `ResearchProtocol`**: Simpler writes but makes graph queries expensive and opaque. Querying for "all tasks that feed into node X" requires full deserialisation. Rejected.
- **networkx in-memory + serialised JSON**: Requires converting back and forth; complicates migrations and makes database-level integrity constraints impossible. Rejected.
- **Dedicated graph database (Neo4j)**: Out of scope; introduces a new infrastructure dependency not covered by the constitution and disproportionate for graphs of ≤ 20 nodes. Rejected.

---

## Decision 2: Protocol Task Type Vocabulary

**Decision**: Single Python `enum.Enum` class `ProtocolTaskType` covering all supported task types across all four study types. A companion mapping dict `VALID_TASK_TYPES_BY_STUDY_TYPE: dict[StudyType, frozenset[ProtocolTaskType]]` enforces which types are valid for each study type at the service layer.

**Task type vocabulary** (29 types across all study types):

| Task Type | SMS | SLR | Rapid | Tertiary |
|-----------|-----|-----|-------|----------|
| `DefinePICO` | ✓ | | ✓ | |
| `DefineProtocol` | | ✓ | | |
| `DefineScope` | | | | ✓ |
| `BuildSearchString` | ✓ | ✓ | ✓ | ✓ |
| `ExecuteSearch` | ✓ | ✓ | ✓ | ✓ |
| `GreyLiteratureSearch` | | ✓ | | |
| `SearchSecondaryStudies` | | | | ✓ |
| `ScreenPapers` | ✓ | ✓ | ✓ | ✓ |
| `FullTextReview` | ✓ | ✓ | ✓ | ✓ |
| `SnowballSearch` | ✓ | ✓ | | |
| `AssessQuality` | | ✓ | | ✓ |
| `AppraiseQuality` | | | ✓ | |
| `CheckInterRaterReliability` | | ✓ | | |
| `ImportSeedStudies` | | | | ✓ |
| `ExtractData` | ✓ | ✓ | | ✓ |
| `AppraiseQualityItems` | | | ✓ | |
| `IdentifyThreatsToValidity` | | | ✓ | |
| `NarrativeSynthesis` | | | ✓ | |
| `SynthesizeData` | ✓ | ✓ | | ✓ |
| `ProduceBriefing` | | | ✓ | |
| `ValidateResults` | ✓ | | | |
| `GenerateReport` | ✓ | ✓ | | ✓ |
| `StakeholderEngagement` | | | ✓ | |

**Rationale**: A single enum with a per-study-type allowlist is simpler than separate enums per study type. Adding a new study type requires only a new allowlist entry, not a new enum or migration column. The allowlist lives in application code (not in the database) so it can evolve without migrations.

**Alternatives considered**:
- Separate enums per study type: leads to duplicate types and complex migration management. Rejected.
- Free-form task type strings: removes the constraint that makes the system safe and predictable. Rejected (spec FR-011).

---

## Decision 3: Quality Gate Configuration Storage

**Decision**: `QualityGate` table with `gate_type` enum column (metric_threshold / completion_check / human_sign_off) and a `config` JSONB column for type-specific parameters. Validated at the service layer using a discriminated Pydantic model (`MetricThresholdConfig`, `CompletionCheckConfig`, `HumanSignOffConfig`).

**Metric threshold config**:
```json
{"metric_name": "kappa_coefficient", "operator": "gte", "threshold": 0.6}
```

**Completion check config**:
```json
{"description": "All candidate papers have been reviewed"}
```

**Human sign-off config**:
```json
{"required_role": "study_admin", "prompt": "Confirm this phase is complete"}
```

**Rationale**: The three gate types have fundamentally different configuration shapes. Using a JSONB column with a discriminated Pydantic validator is the established pattern for polymorphic config in this codebase (see `metadata_` JSON column on `Study`). A flat table with nullable columns for each gate type would create a wide, sparse table with implicit nullability rules — harder to maintain and validate.

**Alternatives considered**:
- Separate tables per gate type (`MetricThresholdGate`, `HumanSignOffGate`): normalised but introduces three joins for a simple fetch. Overkill for small config payloads. Rejected.
- Single flat table with all columns nullable: sparse, ambiguous, violates SRP. Rejected.

---

## Decision 4: Edge Condition Storage

**Decision**: Three optional columns on `ProtocolEdge`: `condition_output_name VARCHAR`, `condition_operator` (enum), `condition_value FLOAT`. A null `condition_output_name` means an unconditional edge. The point-and-click builder produces exactly one `(output_name, operator, value)` triple per edge.

**Supported operators**: `gt`, `gte`, `lt`, `lte`, `eq`, `neq` (covers numeric comparisons and equality checks for paper counts, percentages, Boolean flags).

**Rationale**: The spec (clarification Q5) constrains conditions to the output of a single structured builder. No compound expressions (AND/OR) are needed. Three flat columns are simpler, more queryable, and more type-safe than JSON. The operator set covers all practical research protocol conditions.

**Alternatives considered**:
- JSON condition column: more flexible but harder to validate and query. Overkill for a single triple. Rejected.
- Support compound AND/OR expressions: not requested; YAGNI. Rejected.

---

## Decision 5: Dual-Editor Synchronisation

**Decision**: Client-side shared state. Both the visual graph editor and the YAML text editor operate on the same in-memory React state object (a structured JS graph: `{nodes: [...], edges: [...]}`). Visual editor mutations (add node, draw edge, update property) update the graph state object. The YAML editor displays a serialised view of the graph state; when the researcher edits YAML text, the client parses it and updates the graph state. Both editors re-render reactively from the same state. A single "Save" action persists the full graph to the API.

**Rationale**: The spec requires immediate sync between editors (FR-006). Client-side shared state achieves this without any server round-trips, which would introduce latency and complexity. The protocol graph is small (≤ 20 nodes) so JSON parse/serialise is instant. This approach matches the pattern used by tools like draw.io (local state + export).

**Alternatives considered**:
- Server-side canonical state with WebSocket push: achieves the same sync but adds WebSocket complexity and server load for a single-user editing session (protocols are edited by one person at a time — optimistic locking covers the multi-session conflict case). Rejected.
- Operational transformation (CRDTs): extreme overkill for a research protocol editor where two people editing simultaneously is an edge case handled by optimistic locking. Rejected.

---

## Decision 6: YAML Export Schema

**Decision**: A versioned YAML schema. Top-level key `protocol_schema_version: "1.0"` allows future non-breaking extensions. Structure:

```yaml
protocol_schema_version: "1.0"
name: "Custom SMS Protocol"
study_type: SMS
nodes:
  - task_id: "define_pico"
    task_type: DefinePICO
    label: "Define PICO"
    description: "Define Population, Intervention, Comparison, Outcome components"
    is_required: true
    inputs:
      - name: research_questions
        data_type: text
        is_required: true
    outputs:
      - name: pico_components
        data_type: pico_struct
    assignees:
      - type: human_role
        role: study_admin
    quality_gates:
      - gate_type: completion_check
        config:
          description: "PICO document is complete"
edges:
  - edge_id: "e1"
    source_task_id: define_pico
    source_output: pico_components
    target_task_id: build_search_string
    target_input: pico_components
    condition:
      output_name: pico_components
      operator: neq
      value: null
```

**Rationale**: YAML is the assumption recorded in the spec. A schema version field makes the format extensible. `task_id` values are researcher-defined string keys (not database IDs) so they survive round-trips cleanly and work in version control diffs.

---

## Decision 7: Runtime Execution Model

**Decision**: Synchronous gate evaluation triggered by task completion, with ARQ background jobs for metric-computation-heavy gates.

Flow when researcher marks task complete:
1. API call `POST /studies/{id}/execution-state/{task_id}/complete`
2. `ProtocolExecutorService.complete_task()` runs synchronously:
   - Marks `TaskExecutionState.status = COMPLETE`
   - Evaluates all quality gates for this node
   - For completion_check and human_sign_off gates: synchronous evaluation
   - For metric_threshold gates: reads the metric from the relevant model (e.g., `InterRaterAgreementRecord.kappa`)
   - If any gate fails: sets status back to `GATE_FAILED`, returns failure detail
   - If all gates pass: calls `activate_eligible_tasks()`
3. `activate_eligible_tasks()`:
   - Loads all `PENDING` nodes
   - For each: check if all predecessor edges have `COMPLETE` source nodes
   - Activate those that qualify (set status = `ACTIVE`)
4. API response includes updated execution state for all tasks

Frontend polls execution state via TanStack Query with `refetchInterval` (same pattern as existing job polling).

**Rationale**: For a research workflow, metric values (Kappa, paper counts) are already computed and stored by the time a task is completed — no additional computation is needed. The gate check is just a database read + comparison. Synchronous execution keeps the UX simple (immediate feedback) and avoids the complexity of job status polling for what is essentially a fast operation. Background jobs are already in use for the actual computation that produces these metrics.

**Alternatives considered**:
- Fully async ARQ job for gate evaluation: adds job tracking overhead and polling latency for a ≤ 100ms operation. Rejected.
- Pre-compute task readiness eagerly: complex cache invalidation. Rejected.

---

## Decision 8: Integration with Existing Phase Gates

**Decision**: Additive approach. New studies (created after this feature ships) use the protocol execution system. Existing studies keep their existing `StudyProtocolAssignment` pointing to the default template (inserted by migration), but phase gate functions remain the authoritative source for the `/api/v1/studies/{id}/phases` response during a transition period. The Alembic migration creates `StudyProtocolAssignment` rows for all existing studies and creates `TaskExecutionState` rows reflecting current phase progress (deriving state from `current_phase` on the `Study` model).

**Rationale**: Attempting to fully replace the phase gate system in one feature is high-risk. The additive approach lets the two systems coexist: the protocol system manages task state for new workflows, while the existing phase gates continue to serve the phases endpoint unchanged. A future feature can remove the phase gate layer once the protocol system is fully proven.

**FR-022 compliance**: The default SMS protocol template encodes the three existing phase-gate conditions as quality gates on their respective task nodes (PICO saved → completion_check on DefinePICO task; search_run_at set → completion_check on ExecuteSearch task; extraction_started_at set → completion_check on ExtractData task). The `ProtocolExecutorService` reads the same `Study` timestamp columns that the phase gate currently reads, ensuring identical behaviour.

---

## Decision 9: Protocol Access Control Implementation

**Decision**: Checked at the service layer via the existing `get_current_user` dependency. Protocol endpoints that mutate state check `protocol.owner_user_id == current_user.id`. Study assignment endpoints check that the requesting user is the study's creator/admin (via `StudyMember` with `role = ADMIN`). Default templates (owner_user_id = null) are read-only for all users.

**Rationale**: Consistent with existing auth pattern (see SLR, Rapid, Tertiary protocol endpoints which check study membership). No new auth mechanism is needed — just role checks at the service layer.

---

## Decision 10: D3.js Graph Visualization Approach

**Decision**: Use D3.js force-directed layout with manual position override. Each `ProtocolNode` has `position_x / position_y` columns (nullable, server-persisted). If positions are null, the D3 force simulation computes initial layout. When the researcher drags a node, positions are updated in client state and persisted to the API on save. Edges are rendered as SVG `<path>` elements with arrowheads using D3's link generator.

**Rationale**: D3.js is already a declared project dependency (from feature 002). Force-directed layout gives a reasonable starting layout for any graph. Persisting positions enables the researcher to maintain a stable, organised diagram across sessions.

**Alternatives considered**:
- Dagre (hierarchical layout): better for DAGs but requires an additional npm dependency. Rejected (YAGNI — D3 is sufficient).
- React Flow: a dedicated graph editor library, but introduces a heavy new dependency when D3 is already approved. Rejected.
