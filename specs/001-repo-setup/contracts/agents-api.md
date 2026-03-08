# Contract: Agents REST API (v1 Skeleton)

**Sub-project**: `agents` | **Date**: 2026-03-08

The `agents` service exposes a lightweight FastAPI application on port 8001. The `backend` calls it via `httpx`. This contract defines the minimal surface for the repo-setup harness.

---

## Base URL

```
http://<host>:8001
```

---

## Health Check

### `GET /health`

**Response 200**:
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

## Jobs

### `POST /jobs`

Submit an analysis job.

**Request body**:
```json
{
  "study_id": 1,
  "task_type": "screen_abstract",
  "payload": {}
}
```

`task_type` MUST be one of: `screen_abstract`, `extract_data`, `synthesise` (expanded in later features).

**Response 202**:
```json
{
  "job_id": "abc123",
  "status": "queued"
}
```

### `GET /jobs/{job_id}`

**Response 200**:
```json
{
  "job_id": "abc123",
  "status": "completed",
  "result": { "decision": "include", "rationale": "..." }
}
```

`status` MUST be one of: `queued`, `running`, `completed`, `failed`.

---

## Error Format

```json
{ "detail": "<human-readable message>" }
```
