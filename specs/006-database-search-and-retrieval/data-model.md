# Data Model: Database Search, Retrieval & Paper Processing

**Branch**: `006-database-search-and-retrieval`
**Date**: 2026-03-17

---

## New Models

### `StudyDatabaseSelection` (`db/src/db/models/search.py`)

Persists which database indices a study has enabled for its search strategy.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK, default uuid4 | |
| `study_id` | UUID | FK → `study.id` ON DELETE CASCADE, not null | |
| `database_index` | Enum(`DatabaseIndex`) | not null | See enum below |
| `is_enabled` | Boolean | not null, default `True` | |
| `created_at` | DateTime(tz=True) | server_default=now() | Audit field |
| `updated_at` | DateTime(tz=True) | server_default=now(), onupdate=now() | Audit field |

**Unique constraint**: `(study_id, database_index)`

**Relationships**: `study → Study` (many-to-one)

---

### `SearchIntegrationCredential` (`db/src/db/models/search.py`)

Encrypted credential storage for subscription-gated database integrations. One row per integration type.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK, default uuid4 | |
| `integration_type` | Enum(`IntegrationType`) | unique, not null | See enum below |
| `api_key_encrypted` | LargeBinary | nullable | Fernet-encrypted; never returned in API responses |
| `auxiliary_token_encrypted` | LargeBinary | nullable | Second credential where required (e.g., Elsevier institutional token) |
| `config_json_encrypted` | LargeBinary | nullable | Additional JSON config (e.g., proxy URL); Fernet-encrypted |
| `last_tested_at` | DateTime(tz=True) | nullable | Timestamp of last successful connectivity test |
| `last_test_status` | Enum(`TestStatus`) | nullable | `success \| rate_limited \| auth_failed \| unreachable \| untested` |
| `version_id` | Integer | not null, default 1 | Optimistic locking |
| `created_at` | DateTime(tz=True) | server_default=now() | |
| `updated_at` | DateTime(tz=True) | server_default=now(), onupdate=now() | |

**Mapper args**: `version_id_col = version_id`

---

### Extended `Paper` model (`db/src/db/models/__init__.py`)

Three new nullable columns added to the existing `Paper` table:

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `full_text_markdown` | Text | nullable | MarkItDown-converted content |
| `full_text_source` | Enum(`FullTextSource`) | nullable | See enum below |
| `full_text_converted_at` | DateTime(tz=True) | nullable | Timestamp of last successful conversion |

---

## New Enums

### `DatabaseIndex` (StrEnum)

```python
class DatabaseIndex(str, enum.Enum):
    IEEE_XPLORE       = "ieee_xplore"
    ACM_DL            = "acm_dl"
    SCOPUS            = "scopus"
    WEB_OF_SCIENCE    = "web_of_science"
    INSPEC            = "inspec"
    SCIENCE_DIRECT    = "science_direct"
    SPRINGER_LINK     = "springer_link"
    GOOGLE_SCHOLAR    = "google_scholar"
    SEMANTIC_SCHOLAR  = "semantic_scholar"
```

### `IntegrationType` (StrEnum)

```python
class IntegrationType(str, enum.Enum):
    IEEE_XPLORE       = "ieee_xplore"
    ELSEVIER          = "elsevier"       # Shared: Scopus, ScienceDirect, Inspec
    WEB_OF_SCIENCE    = "web_of_science"
    SPRINGER_NATURE   = "springer_nature"
    SEMANTIC_SCHOLAR  = "semantic_scholar"  # Optional key (rate limit upgrade)
    UNPAYWALL         = "unpaywall"         # Stores email address (not a key)
    GOOGLE_SCHOLAR    = "google_scholar"    # Stores proxy URL in config_json
```

### `TestStatus` (StrEnum)

```python
class TestStatus(str, enum.Enum):
    SUCCESS       = "success"
    RATE_LIMITED  = "rate_limited"
    AUTH_FAILED   = "auth_failed"
    UNREACHABLE   = "unreachable"
    UNTESTED      = "untested"
```

### `FullTextSource` (StrEnum)

```python
class FullTextSource(str, enum.Enum):
    UNPAYWALL    = "unpaywall"
    DIRECT       = "direct"
    SCIHUB       = "scihub"
    UNAVAILABLE  = "unavailable"
    PENDING      = "pending"
```

---

## Existing Models — No Structural Changes

| Model | Change |
|-------|--------|
| `Study` | No structural change; linked to `StudyDatabaseSelection` via relationship |
| `StudyPaper` | No change; full-text content belongs to `Paper`, not the association |
| `Provider` | No change |
| `AvailableModel` | No change |
| `Agent` | No change |

---

## Migration

**File**: `db/alembic/versions/0013_database_search_and_retrieval.py`

Operations:
1. Create `DatabaseIndex`, `IntegrationType`, `TestStatus`, `FullTextSource` PostgreSQL enum types.
2. Create `study_database_selection` table.
3. Create `search_integration_credential` table.
4. `ALTER TABLE paper ADD COLUMN full_text_markdown TEXT NULL`.
5. `ALTER TABLE paper ADD COLUMN full_text_source full_text_source_enum NULL`.
6. `ALTER TABLE paper ADD COLUMN full_text_converted_at TIMESTAMPTZ NULL`.

Downgrade reverses all six operations in reverse order.

---

## Entity Relationships

```text
Study (1) ──< StudyDatabaseSelection (many)
  study_id FK → study.id (CASCADE DELETE)

Paper (1)
  + full_text_markdown (nullable Text)
  + full_text_source   (nullable FullTextSource enum)
  + full_text_converted_at (nullable DateTime)

SearchIntegrationCredential (standalone, one per IntegrationType)
  No FK relationships — integration-type is the key
```

---

## Validation Rules

- `StudyDatabaseSelection.database_index` must be a valid `DatabaseIndex` value.
- `SearchIntegrationCredential.integration_type` is unique — only one credential record per integration.
- `Paper.full_text_source` must be `None` when `full_text_markdown` is `None`.
- `Paper.full_text_converted_at` must be `None` when `full_text_markdown` is `None`.
- When `full_text_source = FullTextSource.SCIHUB`, the API response must not expose the markdown content unless the requesting study has SciHub explicitly enabled and acknowledged.
