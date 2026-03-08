# Contract: Backend REST API (v1 Skeleton)

**Sub-project**: `backend` | **Date**: 2026-03-08

This contract defines the minimal API surface exposed by the `backend` FastAPI application as part of the repo-setup feature. It is a skeleton that will be expanded in later features.

---

## Base URL

```
http://<host>:8000/api/v1
```

All responses use `Content-Type: application/json`.

---

## Health Check

### `GET /health`

Returns service health. Used by pre-commit smoke tests and deployment health probes.

**Response 200**:
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

## Studies

### `GET /studies`

List all studies.

**Response 200**:
```json
[
  {
    "id": 1,
    "name": "My First SMS",
    "study_type": "SMS",
    "status": "draft",
    "created_at": "2026-03-08T12:00:00Z"
  }
]
```

### `POST /studies`

Create a new study.

**Request body**:
```json
{
  "name": "My First SMS",
  "study_type": "SMS"
}
```

`study_type` MUST be one of: `SMS`, `SLR`, `Tertiary`, `Rapid`.

**Response 201**:
```json
{
  "id": 1,
  "name": "My First SMS",
  "study_type": "SMS",
  "status": "draft",
  "created_at": "2026-03-08T12:00:00Z"
}
```

**Response 422** (validation error):
```json
{
  "detail": [{ "loc": ["body", "study_type"], "msg": "value is not a valid enum member", "type": "value_error.enum" }]
}
```

### `GET /studies/{study_id}`

Get a single study.

**Response 200**: Same schema as POST 201.
**Response 404**: `{ "detail": "Study not found" }`

---

## Papers (stub — expanded in later features)

### `GET /studies/{study_id}/papers`

List papers associated with a study.

**Response 200**:
```json
[
  {
    "id": 1,
    "title": "A Survey of ...",
    "doi": "10.1234/example",
    "inclusion_status": "pending"
  }
]
```

---

## Agents Proxy

The backend proxies long-running agent tasks to the agents service.

### `POST /studies/{study_id}/analyse`

Trigger an analysis run via the agents service.

**Request body**: `{}` (parameters added in later features)

**Response 202**:
```json
{
  "job_id": "abc123",
  "status": "queued"
}
```

### `GET /studies/{study_id}/jobs/{job_id}`

Poll the status of a running agent job.

**Response 200**:
```json
{
  "job_id": "abc123",
  "status": "running",   // "queued" | "running" | "completed" | "failed"
  "result": null          // populated when status == "completed"
}
```

---

## Error Format

All errors follow RFC 7807 / FastAPI default:

```json
{
  "detail": "<human-readable message>"
}
```
