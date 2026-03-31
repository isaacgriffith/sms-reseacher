# API Contracts: Research Protocol Definition (Feature 010)

**Branch**: `010-research-protocol-definition`
**Date**: 2026-03-30
**Base path**: `/api/v1`
**Auth**: All endpoints require `Authorization: Bearer <JWT>` unless noted.

---

## Protocol Library Endpoints

### `GET /protocols`

List all protocols visible to the authenticated researcher: their own custom protocols plus all default templates matching the optional `study_type` filter.

**Query params**:
- `study_type` (optional): `SMS | SLR | Rapid | Tertiary`

**Response `200`**:
```json
[
  {
    "id": 1,
    "name": "Default SMS Protocol",
    "study_type": "SMS",
    "is_default_template": true,
    "owner_user_id": null,
    "version_id": 1,
    "created_at": "2026-03-30T00:00:00Z",
    "updated_at": "2026-03-30T00:00:00Z"
  },
  {
    "id": 42,
    "name": "My Custom SMS Protocol",
    "study_type": "SMS",
    "is_default_template": false,
    "owner_user_id": 7,
    "version_id": 3,
    "created_at": "2026-03-30T12:00:00Z",
    "updated_at": "2026-03-30T14:00:00Z"
  }
]
```

---

### `POST /protocols`

Create a new custom protocol. Body must include either `copy_from_protocol_id` (copy an existing protocol or default template) or a full graph definition. The authenticated user becomes the owner.

**Request body**:
```json
{
  "name": "My Custom SMS Protocol",
  "description": "Adapted from default with snowball removed",
  "copy_from_protocol_id": 1
}
```
_or_ (full graph):
```json
{
  "name": "From Scratch",
  "study_type": "SMS",
  "nodes": [ ... ],
  "edges": [ ... ]
}
```

**Response `201`**: Full `ProtocolDetailResponse` (see GET /protocols/{id}).

**Errors**:
- `400` — validation error (cycle, dangling input, unknown task type)
- `409` — name already exists for this researcher

---

### `GET /protocols/{protocol_id}`

Retrieve full protocol details including all nodes, edges, quality gates, assignees, inputs, and outputs.

**Response `200`**:
```json
{
  "id": 42,
  "name": "My Custom SMS Protocol",
  "study_type": "SMS",
  "is_default_template": false,
  "owner_user_id": 7,
  "version_id": 3,
  "description": "...",
  "nodes": [
    {
      "id": 101,
      "task_id": "define_pico",
      "task_type": "DefinePICO",
      "label": "Define PICO",
      "description": "Define research components",
      "is_required": true,
      "position_x": 100.0,
      "position_y": 200.0,
      "inputs": [
        { "id": 201, "name": "research_questions", "data_type": "text", "is_required": true }
      ],
      "outputs": [
        { "id": 301, "name": "pico_components", "data_type": "pico_struct" }
      ],
      "assignees": [
        { "id": 401, "assignee_type": "human_role", "role": "study_admin", "agent_id": null }
      ],
      "quality_gates": [
        {
          "id": 501,
          "gate_type": "completion_check",
          "config": { "description": "PICO document is complete" }
        }
      ]
    }
  ],
  "edges": [
    {
      "id": 601,
      "edge_id": "e1",
      "source_task_id": "define_pico",
      "source_output_name": "pico_components",
      "target_task_id": "build_search_string",
      "target_input_name": "pico_components",
      "condition": null
    }
  ],
  "created_at": "2026-03-30T12:00:00Z",
  "updated_at": "2026-03-30T14:00:00Z"
}
```

**Errors**:
- `403` — protocol belongs to another researcher (and is not a default template)
- `404` — not found

---

### `PUT /protocols/{protocol_id}`

Replace the full protocol graph. Requires `version_id` matching the current database value (optimistic lock). Default templates return `403`.

**Request body**:
```json
{
  "name": "My Custom SMS Protocol v2",
  "description": "Updated with QA gate",
  "version_id": 3,
  "nodes": [ ... ],
  "edges": [ ... ]
}
```

**Response `200`**: Updated `ProtocolDetailResponse`.

**Errors**:
- `400` — validation error (cycle, dangling input, unknown task type, gate metric not in node outputs)
- `403` — not owner, or protocol is a default template
- `404` — not found
- `409` — version_id mismatch (concurrent edit); body: `{"detail": "conflict", "current_version_id": 4}`

---

### `DELETE /protocols/{protocol_id}`

Delete a custom protocol. Fails if the protocol is currently assigned to any study.

**Response `204`**: No body.

**Errors**:
- `403` — not owner, or is a default template
- `409` — protocol is assigned to one or more studies; body lists the blocking study IDs

---

### `GET /protocols/{protocol_id}/export`

Export the protocol as a YAML file download.

**Response `200`**:
- `Content-Type: application/x-yaml`
- `Content-Disposition: attachment; filename="protocol-{name}.yaml"`
- Body: YAML as described in research.md Decision 6

---

### `POST /protocols/import`

Import a protocol from an uploaded YAML file. Creates a new custom protocol owned by the authenticated researcher. Validates before creating.

**Request**: `multipart/form-data` with field `file` (YAML file).

**Response `201`**: Created `ProtocolDetailResponse`.

**Errors**:
- `400` — YAML parse error, schema version unsupported, cycle detected, unknown task type, dangling input; body includes specific field-level error

---

## Study Protocol Assignment Endpoints

### `GET /studies/{study_id}/protocol-assignment`

Get the protocol currently assigned to a study.

**Response `200`**:
```json
{
  "study_id": 10,
  "protocol_id": 42,
  "protocol_name": "My Custom SMS Protocol",
  "is_default_template": false,
  "assigned_at": "2026-03-30T15:00:00Z",
  "assigned_by_user_id": 7
}
```

**Errors**:
- `403` — not a study member
- `404` — study has no protocol assignment (should not occur post-migration)

---

### `PUT /studies/{study_id}/protocol-assignment`

Assign or reassign a protocol to a study. Only the study administrator can call this. Blocked if the study is actively executing (any task has status `active`).

**Request body**:
```json
{ "protocol_id": 42 }
```

**Response `200`**: Updated assignment response.

**Errors**:
- `400` — protocol's `study_type` does not match study's `study_type`
- `403` — not study administrator, or protocol is owned by another researcher
- `409` — study is currently executing (task statuses would be lost); body: `{"detail": "study_executing"}`

---

### `DELETE /studies/{study_id}/protocol-assignment`

Reset the study's protocol to the default template for the study's type. Blocked while study is executing.

**Request body**:
```json
{ "confirm_reset": true }
```

**Response `200`**: New assignment response (pointing to default template).

**Errors**:
- `400` — `confirm_reset` not true (confirmation gate)
- `403` — not study administrator
- `409` — study is currently executing

---

## Protocol Execution State Endpoints

### `GET /studies/{study_id}/execution-state`

Get the current execution state for all tasks in the study's protocol. Available to all study members.

**Response `200`**:
```json
{
  "study_id": 10,
  "protocol_id": 42,
  "tasks": [
    {
      "node_id": 101,
      "task_id": "define_pico",
      "task_type": "DefinePICO",
      "label": "Define PICO",
      "status": "complete",
      "activated_at": "2026-03-30T10:00:00Z",
      "completed_at": "2026-03-30T11:00:00Z",
      "gate_failure_detail": null
    },
    {
      "node_id": 102,
      "task_id": "build_search_string",
      "task_type": "BuildSearchString",
      "label": "Build Search String",
      "status": "active",
      "activated_at": "2026-03-30T11:00:00Z",
      "completed_at": null,
      "gate_failure_detail": null
    }
  ]
}
```

---

### `POST /studies/{study_id}/execution-state/{task_id}/complete`

Mark a task as complete. Triggers synchronous quality gate evaluation and activates eligible downstream tasks. Only the study administrator or an assignee of the task can call this.

**Request body**: `{}` (empty — all needed data is read from existing study models)

**Response `200`**:
```json
{
  "completed_task_id": "build_search_string",
  "gate_result": "passed",
  "gate_failure_detail": null,
  "newly_activated_task_ids": ["screen_papers"],
  "all_tasks": [ ... ]
}
```

_On gate failure_:
```json
{
  "completed_task_id": "screen_papers",
  "gate_result": "failed",
  "gate_failure_detail": {
    "gate_type": "metric_threshold",
    "metric_name": "kappa_coefficient",
    "measured_value": 0.42,
    "threshold": 0.6,
    "operator": "gte",
    "remediation": "Conduct a reconciliation round between reviewers and re-screen disputed papers."
  },
  "newly_activated_task_ids": [],
  "all_tasks": [ ... ]
}
```

**Errors**:
- `403` — not a study administrator or task assignee
- `404` — task_id not found in study's protocol
- `409` — task is not in `active` status

---

### `POST /studies/{study_id}/execution-state/{task_id}/approve`

Provide human sign-off approval for a task's `human_sign_off` quality gate. Only the study administrator can approve.

**Request body**: `{}` (empty)

**Response `200`**: Same shape as `/complete` response.

**Errors**:
- `403` — not study administrator
- `404` — task_id not found
- `409` — task has no pending human_sign_off gate, or task is not in `gate_failed` status

---

## Remediation Notes

Quality gate remediation messages are hardcoded per metric in the `QualityGateEvaluator` service:

| Metric name | Remediation message |
|-------------|---------------------|
| `kappa_coefficient` | "Conduct a reconciliation round between reviewers and re-screen disputed papers." |
| `accepted_paper_count` | "Review exclusion criteria or broaden the search string to capture more relevant papers." |
| `test_set_recall` | "Expand the search string with additional synonyms and re-run the search." |
| `coverage_recall` | "Add missed papers as seed papers for a snowball round." |
