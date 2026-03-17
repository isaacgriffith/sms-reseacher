# Data Model: Models & Agents Management

**Feature**: 005-models-and-agents
**Date**: 2026-03-16

---

## New Entities

### Provider

Represents a configured LLM service that the system can use to run agent inference.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID (PK) | NOT NULL | Server-generated |
| `provider_type` | Enum | NOT NULL | `ProviderType.anthropic \| openai \| ollama` |
| `display_name` | String(100) | NOT NULL | Human-readable label |
| `api_key_encrypted` | LargeBinary | NULLABLE | Fernet-encrypted; NULL for Ollama |
| `base_url` | String(500) | NULLABLE | Required for Ollama; NULL for cloud providers |
| `is_enabled` | Boolean | NOT NULL, DEFAULT true | Controls availability |
| `version_id` | Integer | NOT NULL | Optimistic locking |
| `created_at` | DateTime(tz) | NOT NULL, server_default | Audit field |
| `updated_at` | DateTime(tz) | NOT NULL, onupdate | Audit field |

**Relationships**:
- `available_models` → `AvailableModel[]` (CASCADE delete)
- `agents` → `Agent[]` (RESTRICT delete — must remove dependent agents first)

**Validation rules**:
- `provider_type == anthropic` → `api_key_encrypted` must not be NULL on save
- `provider_type == openai` → `api_key_encrypted` must not be NULL on save
- `provider_type == ollama` → `base_url` must not be NULL on save; `api_key_encrypted` must be NULL
- `display_name` unique constraint (prevents duplicate provider records with same name)

---

### AvailableModel

An individual model offered by a Provider, discovered via that provider's catalog API.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID (PK) | NOT NULL | Server-generated |
| `provider_id` | UUID (FK → Provider) | NOT NULL, CASCADE | Source provider |
| `model_identifier` | String(200) | NOT NULL | Provider's native model ID (e.g. `claude-sonnet-4-6`) |
| `display_name` | String(200) | NOT NULL | Friendly name shown in UI |
| `is_enabled` | Boolean | NOT NULL, DEFAULT true | Admins can disable individual models |
| `version_id` | Integer | NOT NULL | Optimistic locking |
| `created_at` | DateTime(tz) | NOT NULL, server_default | |
| `updated_at` | DateTime(tz) | NOT NULL, onupdate | |

**Unique constraint**: `(provider_id, model_identifier)` — prevents duplicate entries per provider.

**Relationships**:
- `provider` → `Provider` (many-to-one)
- `agents` → `Agent[]` (RESTRICT delete — disable model before removing it)

---

### Agent

A fully configured AI participant in the research workflow, combining a role, a persona, and a model assignment.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID (PK) | NOT NULL | Server-generated |
| `task_type` | Enum | NOT NULL | `AgentTaskType` (see enum below) |
| `role_name` | String(100) | NOT NULL | e.g. "Screener" |
| `role_description` | Text | NOT NULL | Plain-text role description |
| `persona_name` | String(100) | NOT NULL | e.g. "Dr. Aria" |
| `persona_description` | Text | NOT NULL | Narrative persona description |
| `persona_svg` | Text | NULLABLE | Raw SVG markup for persona image |
| `system_message_template` | Text | NOT NULL | Jinja2 template; variables: role_name, role_description, persona_name, persona_description, domain, study_type |
| `system_message_undo_buffer` | Text | NULLABLE | Previous system message (one undo level) |
| `model_id` | UUID (FK → AvailableModel) | NOT NULL, RESTRICT | Assigned model |
| `provider_id` | UUID (FK → Provider) | NOT NULL, RESTRICT | Denormalized for fast joins; must match model's provider_id |
| `is_active` | Boolean | NOT NULL, DEFAULT true | Soft-delete / deactivation flag |
| `version_id` | Integer | NOT NULL | Optimistic locking |
| `created_at` | DateTime(tz) | NOT NULL, server_default | |
| `updated_at` | DateTime(tz) | NOT NULL, onupdate | |

**Relationships**:
- `model` → `AvailableModel` (many-to-one)
- `provider` → `Provider` (many-to-one)
- `reviewers` → `Reviewer[]` (back-reference; RESTRICT delete)

**Validation rules**:
- `model.provider_id == provider_id` — enforced at application layer (not DB constraint, to avoid cross-table constraint complexity)
- `system_message_template` — validated by Jinja2 parse + unknown-variable check on save
- `task_type` — restricted to `AgentTaskType` enum values

---

### AgentTaskType (Enum)

```
screener
extractor
librarian
expert
quality_judge
agent_generator
domain_modeler
synthesiser
validity_assessor
```

---

### ProviderType (Enum)

```
anthropic
openai
ollama
```

---

## Modified Entities

### Reviewer (modified)

The existing `Reviewer` model in `db/src/db/models/study.py` gains:

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `agent_id` | UUID (FK → Agent) | NULLABLE, SET NULL | New reference to Agent record |

`agent_name` (existing `str | None` column) is retained as nullable for the migration transition period and will be removed in a follow-up migration once all rows have `agent_id` populated.

**Post-migration invariant**: `reviewer_type == 'ai_agent'` → `agent_id IS NOT NULL` (enforced at application layer; not a DB-level constraint to support the transition period).

---

## Migration Plan

### Migration 0012_models_and_agents.py

**upgrade()**:
1. Create `providertype` PostgreSQL enum
2. Create `agenttasktype` PostgreSQL enum
3. Create `provider` table
4. Create `available_model` table
5. Create `agent` table
6. Add `agent_id` nullable UUID FK column to `reviewer`
7. Seed: insert default Anthropic Provider record (if `ANTHROPIC_API_KEY` env var is set)
8. Seed: insert AgentGenerator bootstrap Agent record with default system message

**downgrade()**:
1. Remove `agent_id` from `reviewer`
2. Drop `agent` table
3. Drop `available_model` table
4. Drop `provider` table
5. Drop `agenttasktype` enum
6. Drop `providertype` enum

---

## Entity Relationship Summary

```
Provider (1) ──── (*) AvailableModel (1) ──── (*) Agent
                                                      │
                                                      │ agent_id (FK, nullable)
                                                      ▼
                                                  Reviewer
                                                      │ study_id (FK)
                                                      ▼
                                                    Study
```

---

## System Message Template Variable Reference

Templates stored in `Agent.system_message_template` use Jinja2 syntax. The following variables are guaranteed to be available at render time:

| Variable | Source | Example value |
|----------|--------|---------------|
| `role_name` | `Agent.role_name` | `"Screener"` |
| `role_description` | `Agent.role_description` | `"Determines inclusion/exclusion..."` |
| `persona_name` | `Agent.persona_name` | `"Dr. Aria"` |
| `persona_description` | `Agent.persona_description` | `"A meticulous researcher..."` |
| `domain` | Injected at render time from Study or request context | `"Software Engineering"` |
| `study_type` | Injected at render time from Study.study_type | `"Systematic Mapping Study"` |

Unknown variable names cause a `UndefinedError` from Jinja2. The backend validates templates using `jinja2.Environment(undefined=jinja2.StrictUndefined).parse()` plus a known-variable allowlist check before accepting a save.
