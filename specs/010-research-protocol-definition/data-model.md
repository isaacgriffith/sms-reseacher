# Data Model: Research Protocol Definition (Feature 010)

**Branch**: `010-research-protocol-definition`
**Date**: 2026-03-30
**Migration**: `0018_research_protocol_definition`

---

## New Enumerations

### `ProtocolTaskType` (Python enum, PostgreSQL enum `protocol_task_type_enum`)

All valid task types across all supported study types:

```
DefinePICO, DefineProtocol, DefineScope,
BuildSearchString, ExecuteSearch,
GreyLiteratureSearch, SearchSecondaryStudies,
ScreenPapers, FullTextReview, SnowballSearch,
AssessQuality, AppraiseQuality, CheckInterRaterReliability,
ImportSeedStudies,
ExtractData, AppraiseQualityItems, IdentifyThreatsToValidity,
NarrativeSynthesis, SynthesizeData, ProduceBriefing,
ValidateResults, GenerateReport, StakeholderEngagement
```

**Allowlist by study type** (enforced in service layer, not DB):

| StudyType | Allowed ProtocolTaskTypes                                                                                                                                                                                    |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SMS       | DefinePICO, BuildSearchString, ExecuteSearch, ScreenPapers, FullTextReview, SnowballSearch, ExtractData, SynthesizeData, ValidateResults, GenerateReport                                                     |
| SLR       | DefineProtocol, BuildSearchString, ExecuteSearch, GreyLiteratureSearch, ScreenPapers, FullTextReview, SnowballSearch, AssessQuality, CheckInterRaterReliability, ExtractData, SynthesizeData, GenerateReport |
| Rapid     | DefinePICO, BuildSearchString, ExecuteSearch, ScreenPapers, FullTextReview, AppraiseQuality, AppraiseQualityItems, IdentifyThreatsToValidity, StakeholderEngagement, NarrativeSynthesis, ProduceBriefing     |
| Tertiary  | DefineScope, BuildSearchString, ExecuteSearch, SearchSecondaryStudies, ScreenPapers, FullTextReview, AssessQuality, ImportSeedStudies, ExtractData, SynthesizeData, GenerateReport                           |

### `QualityGateType` (Python enum, PostgreSQL enum `quality_gate_type_enum`)

```
metric_threshold, completion_check, human_sign_off
```

### `EdgeConditionOperator` (Python enum, PostgreSQL enum `edge_condition_operator_enum`)

```
gt, gte, lt, lte, eq, neq
```

### `TaskNodeStatus` (Python enum, PostgreSQL enum `task_node_status_enum`)

```
pending, active, complete, skipped, gate_failed
```

### `NodeAssigneeType` (Python enum, PostgreSQL enum `node_assignee_type_enum`)

```
human_role, ai_agent
```

### `NodeDataType` (Python enum, PostgreSQL enum `node_data_type_enum`)

Typed output/input slot types:

```
text, pico_struct, search_string, candidate_paper_list,
full_text_content, extraction_record_list, synthesis_result,
quality_score, paper_count, boolean, report
```

---

## New Tables

### `research_protocol`

The header record for a named protocol graph. Default templates have `owner_user_id = NULL`.

| Column                | Type            | Constraints                              | Notes                               |
| --------------------- | --------------- | ---------------------------------------- | ----------------------------------- |
| `id`                  | INTEGER         | PK, autoincrement                        |                                     |
| `name`                | VARCHAR(255)    | NOT NULL                                 | User-defined name                   |
| `description`         | TEXT            | nullable                                 |                                     |
| `study_type`          | Enum(StudyType) | NOT NULL                                 | Constrains valid task types         |
| `is_default_template` | BOOLEAN         | NOT NULL, default false                  | True for platform-supplied defaults |
| `owner_user_id`       | INTEGER         | FK → user.id SET NULL, nullable          | NULL = default template             |
| `version_id`          | INTEGER         | NOT NULL, default 1                      | Optimistic locking counter          |
| `created_at`          | TIMESTAMPTZ     | NOT NULL, server_default=now()           |                                     |
| `updated_at`          | TIMESTAMPTZ     | NOT NULL, server_default=now(), onupdate |                                     |

**Indexes**: `(owner_user_id, study_type)`, `(is_default_template, study_type)`

**Mapper args**: `version_id_col = version_id`

**Constraints**:

- A default template is immutable (enforced at service layer — `is_default_template = True` → rejects all PUT requests)
- `UNIQUE(name, owner_user_id)` — researcher cannot have two custom protocols with the same name

---

### `protocol_node`

A task vertex in a protocol graph.

| Column        | Type                   | Constraints                                        | Notes                                          |
| ------------- | ---------------------- | -------------------------------------------------- | ---------------------------------------------- |
| `id`          | INTEGER                | PK, autoincrement                                  |                                                |
| `protocol_id` | INTEGER                | FK → research_protocol.id CASCADE, NOT NULL, index |                                                |
| `task_id`     | VARCHAR(100)           | NOT NULL                                           | Researcher-defined key, unique within protocol |
| `task_type`   | Enum(ProtocolTaskType) | NOT NULL                                           | Validated against study_type allowlist         |
| `label`       | VARCHAR(255)           | NOT NULL                                           | Human-readable name                            |
| `description` | TEXT                   | nullable                                           |                                                |
| `is_required` | BOOLEAN                | NOT NULL, default true                             | Required nodes cannot be deleted               |
| `position_x`  | FLOAT                  | nullable                                           | D3 layout x-coordinate                         |
| `position_y`  | FLOAT                  | nullable                                           | D3 layout y-coordinate                         |
| `created_at`  | TIMESTAMPTZ            | NOT NULL, server_default=now()                     |                                                |
| `updated_at`  | TIMESTAMPTZ            | NOT NULL, server_default=now(), onupdate           |                                                |

**Constraints**: `UNIQUE(protocol_id, task_id)`

---

### `protocol_node_input`

Named typed input slot on a protocol node.

| Column        | Type               | Constraints                                    | Notes                             |
| ------------- | ------------------ | ---------------------------------------------- | --------------------------------- |
| `id`          | INTEGER            | PK, autoincrement                              |                                   |
| `node_id`     | INTEGER            | FK → protocol_node.id CASCADE, NOT NULL, index |                                   |
| `name`        | VARCHAR(100)       | NOT NULL                                       | Input slot name                   |
| `data_type`   | Enum(NodeDataType) | NOT NULL                                       |                                   |
| `is_required` | BOOLEAN            | NOT NULL, default true                         | Required inputs must be connected |

**Constraints**: `UNIQUE(node_id, name)`

---

### `protocol_node_output`

Named typed output slot on a protocol node.

| Column      | Type               | Constraints                                    | Notes            |
| ----------- | ------------------ | ---------------------------------------------- | ---------------- |
| `id`        | INTEGER            | PK, autoincrement                              |                  |
| `node_id`   | INTEGER            | FK → protocol_node.id CASCADE, NOT NULL, index |                  |
| `name`      | VARCHAR(100)       | NOT NULL                                       | Output slot name |
| `data_type` | Enum(NodeDataType) | NOT NULL                                       |                  |

**Constraints**: `UNIQUE(node_id, name)`

---

### `quality_gate`

A quality gate condition attached to a protocol node.

| Column       | Type                  | Constraints                                    | Notes                                             |
| ------------ | --------------------- | ---------------------------------------------- | ------------------------------------------------- |
| `id`         | INTEGER               | PK, autoincrement                              |                                                   |
| `node_id`    | INTEGER               | FK → protocol_node.id CASCADE, NOT NULL, index |                                                   |
| `gate_type`  | Enum(QualityGateType) | NOT NULL                                       |                                                   |
| `config`     | JSONB                 | NOT NULL                                       | Type-specific config (see research.md Decision 3) |
| `created_at` | TIMESTAMPTZ           | NOT NULL, server_default=now()                 |                                                   |

**Config schemas** (validated by Pydantic in service layer):

- `metric_threshold`: `{metric_name: str, operator: EdgeConditionOperator, threshold: float}`
- `completion_check`: `{description: str}`
- `human_sign_off`: `{required_role: str, prompt: str}`

---

### `node_assignee`

An assignee (human role or AI agent) on a protocol node.

| Column          | Type                   | Constraints                                    | Notes                                                             |
| --------------- | ---------------------- | ---------------------------------------------- | ----------------------------------------------------------------- |
| `id`            | INTEGER                | PK, autoincrement                              |                                                                   |
| `node_id`       | INTEGER                | FK → protocol_node.id CASCADE, NOT NULL, index |                                                                   |
| `assignee_type` | Enum(NodeAssigneeType) | NOT NULL                                       |                                                                   |
| `role`          | VARCHAR(100)           | nullable                                       | e.g., "study_admin", "reviewer" (when assignee_type = human_role) |
| `agent_id`      | INTEGER                | FK → agent.id SET NULL, nullable               | (when assignee_type = ai_agent)                                   |

**Constraints**: Either `role` or `agent_id` must be non-null (enforced at service layer)

---

### `protocol_edge`

A directed information-flow edge between two task nodes.

| Column                  | Type                        | Constraints                                        | Notes                                          |
| ----------------------- | --------------------------- | -------------------------------------------------- | ---------------------------------------------- |
| `id`                    | INTEGER                     | PK, autoincrement                                  |                                                |
| `protocol_id`           | INTEGER                     | FK → research_protocol.id CASCADE, NOT NULL, index |                                                |
| `edge_id`               | VARCHAR(100)                | NOT NULL                                           | Researcher-defined key, unique within protocol |
| `source_node_id`        | INTEGER                     | FK → protocol_node.id CASCADE, NOT NULL            |                                                |
| `source_output_name`    | VARCHAR(100)                | NOT NULL                                           | Must match an output on source node            |
| `target_node_id`        | INTEGER                     | FK → protocol_node.id CASCADE, NOT NULL            |                                                |
| `target_input_name`     | VARCHAR(100)                | NOT NULL                                           | Must match an input on target node             |
| `condition_output_name` | VARCHAR(100)                | nullable                                           | Edge is conditional if non-null                |
| `condition_operator`    | Enum(EdgeConditionOperator) | nullable                                           | Required if condition_output_name set          |
| `condition_value`       | FLOAT                       | nullable                                           | Required if condition_output_name set          |
| `created_at`            | TIMESTAMPTZ                 | NOT NULL, server_default=now()                     |                                                |

**Constraints**: `UNIQUE(protocol_id, edge_id)`. Cycle detection at service layer on save.

---

### `study_protocol_assignment`

Associates a study with its assigned protocol (one-to-one).

| Column                | Type        | Constraints                                  | Notes                  |
| --------------------- | ----------- | -------------------------------------------- | ---------------------- |
| `id`                  | INTEGER     | PK, autoincrement                            |                        |
| `study_id`            | INTEGER     | FK → study.id CASCADE, NOT NULL, UNIQUE      | One protocol per study |
| `protocol_id`         | INTEGER     | FK → research_protocol.id RESTRICT, NOT NULL |                        |
| `assigned_at`         | TIMESTAMPTZ | NOT NULL, server_default=now()               |                        |
| `assigned_by_user_id` | INTEGER     | FK → user.id SET NULL, nullable              |                        |

**Constraints**: `UNIQUE(study_id)`

---

### `task_execution_state`

Runtime state of each protocol node within a specific study's execution.

| Column                | Type                 | Constraints                              | Notes                                |
| --------------------- | -------------------- | ---------------------------------------- | ------------------------------------ |
| `id`                  | INTEGER              | PK, autoincrement                        |                                      |
| `study_id`            | INTEGER              | FK → study.id CASCADE, NOT NULL, index   |                                      |
| `node_id`             | INTEGER              | FK → protocol_node.id CASCADE, NOT NULL  |                                      |
| `status`              | Enum(TaskNodeStatus) | NOT NULL, default pending                |                                      |
| `gate_failure_detail` | JSONB                | nullable                                 | Populated on gate_failed status      |
| `activated_at`        | TIMESTAMPTZ          | nullable                                 | When status transitioned to active   |
| `completed_at`        | TIMESTAMPTZ          | nullable                                 | When status transitioned to complete |
| `created_at`          | TIMESTAMPTZ          | NOT NULL, server_default=now()           |                                      |
| `updated_at`          | TIMESTAMPTZ          | NOT NULL, server_default=now(), onupdate |                                      |

**Constraints**: `UNIQUE(study_id, node_id)`

**Gate failure detail schema**:

```json
{
  "gate_id": 42,
  "gate_type": "metric_threshold",
  "metric_name": "kappa_coefficient",
  "measured_value": 0.42,
  "threshold": 0.6,
  "operator": "gte",
  "remediation": "Conduct a reconciliation round between reviewers and re-screen disputed papers."
}
```

---

## State Transition Diagram: `TaskExecutionState.status`

```
           [study protocol assigned]
                     │
                     ▼
                  PENDING
                     │
      all predecessors complete + gates pass
                     │
                     ▼
                  ACTIVE ──────────────────────────────────┐
                     │                                      │
          researcher marks task complete                    │
                     │                                      │
                     ▼                                      │
            [gate evaluation]                               │
                     │                                      │
          ┌──────────┴──────────┐                          │
          │ gates pass          │ gate fails                │
          ▼                     ▼                           │
       COMPLETE           GATE_FAILED ─── remediation ─────┘
          │
   [conditional edge]
   condition false → SKIPPED
```

---

## Migration Seeding: Default Protocol Templates

The migration `0018_research_protocol_definition` inserts default protocol templates for all four study types. Each template mirrors the existing hardcoded phase logic:

**Default SMS Protocol nodes** (in topological order):

1. `define_pico` → DefinePICO (required) → QualityGate: completion_check (PICO doc complete)
2. `build_search_string` → BuildSearchString (required)
3. `execute_search` → ExecuteSearch (required) → QualityGate: completion_check (≥1 search execution)
4. `screen_papers` → ScreenPapers (required)
5. `full_text_review` → FullTextReview (optional)
6. `snowball_search` → SnowballSearch (optional) → conditional self-loop edge (if snowball adds ≥ threshold papers)
7. `extract_data` → ExtractData (required) → QualityGate: completion_check (extraction started)
8. `synthesize_data` → SynthesizeData (required)
9. `validate_results` → ValidateResults (optional)
10. `generate_report` → GenerateReport (required)

**FR-022 quality gate mapping**:

| Existing phase gate                            | Protocol quality gate location            |
| ---------------------------------------------- | ----------------------------------------- |
| `pico_saved_at` check (Phase 2 unlock)         | completion_check on `define_pico` node    |
| `search_run_at` check (Phase 3 unlock)         | completion_check on `execute_search` node |
| `extraction_started_at` check (Phase 4 unlock) | completion_check on `extract_data` node   |

The migration also creates `StudyProtocolAssignment` rows for all existing studies (pointing to the matching default template) and seeds `TaskExecutionState` rows with status derived from each study's `current_phase`.

---

## Relationship Summary

```
ResearchProtocol
  ├── ProtocolNode (many)
  │     ├── ProtocolNodeInput (many)
  │     ├── ProtocolNodeOutput (many)
  │     ├── QualityGate (many)
  │     └── NodeAssignee (many)
  ├── ProtocolEdge (many)
  └── StudyProtocolAssignment (many, via protocol_id)
        └── Study (one-to-one via study_id)
              └── TaskExecutionState (one per ProtocolNode)

User (owner)
  └── ResearchProtocol (many custom protocols)
```

---

## Validation Rules (Service Layer)

| Rule                                                                                         | Enforced at                          |
| -------------------------------------------------------------------------------------------- | ------------------------------------ |
| Task type must be in allowlist for study's StudyType                                         | `ProtocolService.validate_node()`    |
| Protocol graph must be acyclic (DFS cycle detection)                                         | `ProtocolService.validate_graph()`   |
| No dangling required inputs (every required input has an incoming edge)                      | `ProtocolService.validate_graph()`   |
| No duplicate outputs → same target input (ambiguous connection)                              | `ProtocolService.validate_graph()`   |
| Conditional edge columns are all-or-nothing (output_name + operator + value)                 | `ProtocolService.validate_edge()`    |
| Quality gate metric_name must match an output from the same node                             | `ProtocolService.validate_gate()`    |
| No protocol reassignment while study is executing (any `TaskExecutionState.status = ACTIVE`) | `ProtocolAssignmentService.assign()` |
| Custom protocol PUT rejected if version_id mismatch (optimistic lock)                        | SQLAlchemy mapper / service          |
| Default template is immutable                                                                | `ProtocolService.update_protocol()`  |
| Required node deletion blocked                                                               | `ProtocolService.delete_node()`      |
