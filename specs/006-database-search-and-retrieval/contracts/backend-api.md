# Backend API Contracts: Database Search, Retrieval & Paper Processing

**Branch**: `006-database-search-and-retrieval`
**Date**: 2026-03-17
**Base path**: `/api/v1`

---

## Study Database Selection

### `GET /studies/{study_id}/database-selection`

Returns the database index selection for a study. If no selection has been saved, returns the default selection (Semantic Scholar enabled, all others disabled).

**Auth**: Authenticated user with access to the study.

**Response 200**:
```json
{
  "study_id": "uuid",
  "selections": [
    {
      "database_index": "ieee_xplore",
      "is_enabled": true,
      "status": "configured | not_configured | unreachable",
      "requires_credential": true,
      "credential_configured": false
    },
    ...
  ],
  "snowball_enabled": false,
  "scihub_enabled": false,
  "scihub_acknowledged": false
}
```

`status` is computed at request time by checking `SearchIntegrationCredential` and the corresponding env var fallbacks.

---

### `PUT /studies/{study_id}/database-selection`

Saves the database index selection for a study.

**Auth**: Authenticated user with write access to the study.

**Request body**:
```json
{
  "selections": [
    { "database_index": "ieee_xplore", "is_enabled": true },
    { "database_index": "scopus",      "is_enabled": true },
    { "database_index": "semantic_scholar", "is_enabled": true }
  ],
  "snowball_enabled": true,
  "scihub_enabled": false,
  "scihub_acknowledged": false
}
```

**Validation**:
- `scihub_enabled: true` requires `scihub_acknowledged: true` and the server environment variable `SCIHUB_ENABLED=true`. Returns `422` if either condition is unmet.
- `scihub_enabled: true` without `SCIHUB_ENABLED=true` in the server environment returns a `403` with `"SciHub is not enabled on this server"`.

**Response 200**: Same schema as `GET` response above.

---

## Paper Full-Text Markdown

### `GET /papers/{paper_id}/markdown`

Returns stored full-text Markdown for a paper. Used by AI agents and the frontend's paper detail view.

**Auth**: Authenticated user.

**Response 200**:
```json
{
  "paper_id": "uuid",
  "doi": "string | null",
  "markdown": "string | null",
  "available": true,
  "full_text_source": "unpaywall | direct | scihub | unavailable | pending | null",
  "converted_at": "ISO8601 | null"
}
```

**Response 404**: Paper not found.

---

## Admin — Search Integrations

All endpoints under `/admin/search-integrations` require `GroupRole.ADMIN` membership.

---

### `GET /admin/search-integrations`

Returns all integration credential records (one per `IntegrationType`), including status and whether a key is configured.

**Response 200**:
```json
[
  {
    "integration_type": "ieee_xplore",
    "display_name": "IEEE Xplore",
    "access_type": "official_api | unofficial_scraping | subscription_required",
    "has_api_key": false,
    "has_auxiliary_token": false,
    "configured_via": "database | environment | not_configured",
    "last_tested_at": "ISO8601 | null",
    "last_test_status": "success | rate_limited | auth_failed | unreachable | untested",
    "version_id": 1
  },
  ...
]
```

The response **never** includes raw key values (`api_key_encrypted` is never returned).

---

### `GET /admin/search-integrations/{integration_type}`

Returns details for a single integration credential record.

**Response 200**: Single object from the array schema above.
**Response 404**: If `integration_type` is not a valid `IntegrationType` value.

---

### `PUT /admin/search-integrations/{integration_type}`

Creates or updates the credential record for an integration type (upsert semantics — no separate POST/PATCH).

**Request body**:
```json
{
  "api_key": "string | null",
  "auxiliary_token": "string | null",
  "config_json": { "proxy_url": "...", "email": "..." },
  "version_id": 1
}
```

- Passing `api_key: null` clears the stored key (the integration falls back to env var).
- `version_id` required for updates (optimistic locking). Omit on first creation.

**Response 200**: Updated credential summary (same schema as `GET` item, without key values).
**Response 409**: Version conflict.
**Response 422**: Validation error (e.g., invalid `config_json` shape for the given type).

---

### `POST /admin/search-integrations/{integration_type}/test`

Runs a lightweight live connectivity probe for the integration (e.g., a one-paper search or metadata lookup).

**Response 200**:
```json
{
  "integration_type": "ieee_xplore",
  "status": "success | rate_limited | auth_failed | unreachable",
  "message": "string",
  "tested_at": "ISO8601"
}
```

The test result is also persisted to `SearchIntegrationCredential.last_tested_at` and `last_test_status`.

---

## Notes on SciHub Guarding

- `PUT /studies/{study_id}/database-selection` with `scihub_enabled: true` requires both server-level `SCIHUB_ENABLED=true` **and** `scihub_acknowledged: true` in the request body.
- Even when SciHub is enabled at the study level, `GET /papers/{paper_id}/markdown` only exposes SciHub-sourced content to users who are members of the study that enabled it. Cross-study leakage of SciHub content is prevented.
