# API Contracts: Models & Agents Management

**Feature**: 005-models-and-agents
**Date**: 2026-03-16
**Base path**: `/api/v1/admin`

All endpoints require admin authentication (existing admin auth middleware).

---

## Providers

### `GET /api/v1/admin/providers`

List all configured providers.

**Response 200**:
```json
[
  {
    "id": "uuid",
    "provider_type": "anthropic | openai | ollama",
    "display_name": "string",
    "base_url": "string | null",
    "is_enabled": true,
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
]
```
Note: `api_key_encrypted` is **never** returned. An `has_api_key: boolean` field indicates whether a key is stored.

---

### `POST /api/v1/admin/providers`

Create a new provider.

**Request body**:
```json
{
  "provider_type": "anthropic | openai | ollama",
  "display_name": "string (required)",
  "api_key": "string | null",
  "base_url": "string | null"
}
```

**Response 201**: Provider object (same shape as GET, with `has_api_key: boolean`).

**Error 422**: Validation failure (e.g., missing api_key for Anthropic/OpenAI, missing base_url for Ollama).

**Side effect**: On successful creation, asynchronously triggers model list refresh for the new provider.

---

### `GET /api/v1/admin/providers/{provider_id}`

Get a single provider.

**Response 200**: Provider object.
**Response 404**: Provider not found.

---

### `PATCH /api/v1/admin/providers/{provider_id}`

Update a provider's display name, API key, base URL, or enabled status.

**Request body** (all fields optional):
```json
{
  "display_name": "string",
  "api_key": "string",
  "base_url": "string",
  "is_enabled": true
}
```

**Response 200**: Updated provider object.
**Response 404**: Not found.
**Response 409**: Version conflict (optimistic locking).

---

### `DELETE /api/v1/admin/providers/{provider_id}`

Delete a provider and all its models (CASCADE).

**Response 204**: Deleted.
**Response 409**: Provider has dependent agents — list dependent agent IDs in error body.

---

### `POST /api/v1/admin/providers/{provider_id}/refresh-models`

Re-fetch the model list from the provider's catalog API and update `available_model` records.

**Response 200**:
```json
{
  "models_added": 3,
  "models_removed": 0,
  "models_total": 12
}
```
**Response 502**: Provider API unreachable — existing model list unchanged.

---

## Models

### `GET /api/v1/admin/providers/{provider_id}/models`

List all models for a provider.

**Response 200**:
```json
[
  {
    "id": "uuid",
    "provider_id": "uuid",
    "model_identifier": "claude-sonnet-4-6",
    "display_name": "Claude Sonnet 4.6",
    "is_enabled": true,
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
]
```

---

### `PATCH /api/v1/admin/providers/{provider_id}/models/{model_id}`

Enable or disable a model.

**Request body**:
```json
{
  "is_enabled": false
}
```

**Response 200**: Updated model object.
**Response 409**: Model is assigned to active agents — list dependent agent IDs in error body.

---

## Agents

### `GET /api/v1/admin/agents`

List all agents.

**Query params**:
- `task_type` (optional) — filter by AgentTaskType value
- `is_active` (optional, default true)

**Response 200**:
```json
[
  {
    "id": "uuid",
    "task_type": "screener",
    "role_name": "Screener",
    "persona_name": "Dr. Aria",
    "model_id": "uuid",
    "provider_id": "uuid",
    "model_display_name": "Claude Sonnet 4.6",
    "provider_display_name": "Anthropic Production",
    "is_active": true,
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  }
]
```

---

### `POST /api/v1/admin/agents`

Create a new agent.

**Request body**:
```json
{
  "task_type": "screener",
  "role_name": "string (required)",
  "role_description": "string (required)",
  "persona_name": "string (required)",
  "persona_description": "string (required)",
  "persona_svg": "string | null",
  "system_message_template": "string (required, Jinja2)",
  "model_id": "uuid (required)",
  "provider_id": "uuid (required)"
}
```

**Response 201**: Full agent object (including `system_message_template`, `persona_svg`).
**Response 422**: Validation failure (invalid template variables, model/provider mismatch, disabled model).

---

### `GET /api/v1/admin/agents/{agent_id}`

Get full agent details.

**Response 200**: Full agent object including `system_message_template`, `system_message_undo_buffer`, `persona_svg`.

---

### `PATCH /api/v1/admin/agents/{agent_id}`

Update an agent's fields.

**Request body** (all optional):
```json
{
  "role_name": "string",
  "role_description": "string",
  "persona_name": "string",
  "persona_description": "string",
  "persona_svg": "string | null",
  "system_message_template": "string",
  "model_id": "uuid",
  "provider_id": "uuid",
  "is_active": true
}
```

**Response 200**: Updated full agent object.
**Response 409**: Version conflict (optimistic locking).

---

### `DELETE /api/v1/admin/agents/{agent_id}`

Soft-delete (set `is_active = false`) an agent.

**Response 200**: Updated agent object with `is_active: false`.
**Response 409**: Agent is assigned to active Reviewer records — list study IDs.

---

### `POST /api/v1/admin/agents/{agent_id}/generate-system-message`

Invoke the AgentGenerator agent to produce a new system message for the given agent based on its current role, persona, and model. Stores the previous message in `system_message_undo_buffer`.

**Response 200**:
```json
{
  "system_message_template": "generated Jinja2 template string",
  "previous_message_preserved": true
}
```
**Response 409**: No active AgentGenerator agent configured.
**Response 502**: LLM call failed.

---

### `POST /api/v1/admin/agents/{agent_id}/undo-system-message`

Restore the system message from the undo buffer.

**Response 200**: Updated agent object.
**Response 409**: No undo buffer available (nothing to restore).

---

### `POST /api/v1/admin/agents/generate-persona-svg`

Generate a persona SVG image using the current LLM for a given persona name and description. Does not save — caller decides whether to include it in a create/update request.

**Request body**:
```json
{
  "persona_name": "string",
  "persona_description": "string",
  "agent_id": "uuid | null"
}
```

**Response 200**:
```json
{
  "svg": "<svg>...</svg>"
}
```
**Response 502**: LLM call failed or did not produce valid SVG.

---

## Agent Task Types (Reference)

`GET /api/v1/admin/agent-task-types`

**Response 200**:
```json
["screener", "extractor", "librarian", "expert", "quality_judge", "agent_generator", "domain_modeler", "synthesiser", "validity_assessor"]
```

Used to populate the task type selector in the agent creation wizard.
