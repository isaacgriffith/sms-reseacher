# Quickstart: Models & Agents Management (005)

**For**: Developers implementing this feature
**Date**: 2026-03-16

---

## Overview

This feature introduces three new database tables (`provider`, `available_model`, `agent`) and extends the existing `reviewer` table with an `agent_id` FK. It replaces the hardcoded `agent_name` string on `Reviewer` with a full `Agent` entity, and extends the admin panel with provider, model, and agent management sections.

---

## Step 1: Apply the Database Migration

```bash
uv run alembic upgrade head
```

This creates the `provider`, `available_model`, and `agent` tables, adds `agent_id` to `reviewer`, and inserts the bootstrap AgentGenerator agent record.

---

## Step 2: Seed a Provider (Development)

For local development, use the admin API or the admin panel UI to add a provider:

```bash
# Example: Add Anthropic provider via API (requires admin JWT)
curl -X POST http://localhost:8000/api/v1/admin/providers \
  -H "Authorization: Bearer <admin-jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_type": "anthropic",
    "display_name": "Anthropic (dev)",
    "api_key": "<your-anthropic-api-key>"
  }'
```

The system automatically fetches the model list on creation.

For Ollama:
```bash
curl -X POST http://localhost:8000/api/v1/admin/providers \
  -H "Authorization: Bearer <admin-jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_type": "ollama",
    "display_name": "Ollama (local)",
    "base_url": "http://localhost:11434"
  }'
```

---

## Step 3: Create an Agent

1. Open the admin panel → **Agents** → **Create Agent**
2. Select a task type (e.g., `screener`)
3. Select a provider and model
4. Fill in role name, role description, persona name, persona description
5. Click **Generate System Message** to get an AI-generated template
6. Review/edit the template, then click **Save**

Or via API:
```bash
curl -X POST http://localhost:8000/api/v1/admin/agents \
  -H "Authorization: Bearer <admin-jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "screener",
    "role_name": "Screener",
    "role_description": "Evaluates papers against inclusion and exclusion criteria.",
    "persona_name": "Dr. Aria",
    "persona_description": "A meticulous systematic reviewer with deep expertise in software engineering research.",
    "system_message_template": "You are {{ persona_name }}, {{ persona_description }}. Your role is {{ role_name }}: {{ role_description }}. You are conducting a {{ study_type }} in the domain of {{ domain }}.",
    "model_id": "<model-uuid>",
    "provider_id": "<provider-uuid>"
  }'
```

---

## Step 4: Running Tests

```bash
# Backend (includes provider/model/agent service tests)
uv run --package sms-backend pytest backend/tests/ --cov=src/backend --cov-report=term-missing

# DB model tests
uv run --package sms-db pytest db/tests/ --cov=src/db --cov-report=term-missing

# Agents (includes updated LLMClient tests)
uv run --package sms-agents pytest agents/tests/ --cov=src/agents --cov-report=term-missing

# Frontend
cd frontend && npm test
```

---

## Key Files Changed / Added

### New Python files
| Package | Path | Purpose |
|---------|------|---------|
| `sms-db` | `db/src/db/models/agents.py` | Provider, AvailableModel, Agent SQLAlchemy models |
| `sms-db` | `db/alembic/versions/0012_models_and_agents.py` | Database migration |
| `sms-backend` | `backend/src/backend/api/v1/admin/providers.py` | Provider CRUD router |
| `sms-backend` | `backend/src/backend/api/v1/admin/models.py` | Model management router |
| `sms-backend` | `backend/src/backend/api/v1/admin/agents.py` | Agent CRUD router |
| `sms-backend` | `backend/src/backend/services/provider_service.py` | Provider + model-fetch service |
| `sms-backend` | `backend/src/backend/services/agent_service.py` | Agent CRUD + system-message-gen service |
| `sms-agents` | `agents/src/agents/core/provider_config.py` | ProviderConfig Protocol |
| `sms-agents` | `agents/prompts/agent_generator/system.md.j2` | AgentGenerator system prompt |

### Modified Python files
| Package | Path | Change |
|---------|------|--------|
| `sms-db` | `db/src/db/models/study.py` | Add `agent_id` FK to Reviewer |
| `sms-db` | `db/src/db/models/__init__.py` | Export new models |
| `sms-agents` | `agents/src/agents/core/llm_client.py` | Add ProviderConfig overload |
| `sms-agents` | `agents/src/agents/screener.py` | Accept ProviderConfig override |
| `sms-agents` | `agents/src/agents/extractor.py` | Accept ProviderConfig override |
| `sms-backend` | `backend/src/backend/api/v1/admin/router.py` | Register new sub-routers |

### New TypeScript/React files
| Package | Path | Purpose |
|---------|------|---------|
| `frontend` | `frontend/src/pages/AdminPage.tsx` | Extended with tabs |
| `frontend` | `frontend/src/components/admin/providers/ProviderList.tsx` | Provider list table |
| `frontend` | `frontend/src/components/admin/providers/ProviderForm.tsx` | Create/edit provider form |
| `frontend` | `frontend/src/components/admin/models/ModelList.tsx` | Model enable/disable table |
| `frontend` | `frontend/src/components/admin/agents/AgentList.tsx` | Agent list table |
| `frontend` | `frontend/src/components/admin/agents/AgentWizard.tsx` | Multi-step creation wizard |
| `frontend` | `frontend/src/components/admin/agents/AgentForm.tsx` | Edit agent form |
| `frontend` | `frontend/src/components/admin/agents/SystemMessageEditor.tsx` | Syntax-highlighted template editor |
| `frontend` | `frontend/src/services/providersApi.ts` | API client for providers/models |
| `frontend` | `frontend/src/services/agentsApi.ts` | API client for agents |

---

## Architecture Notes

### Provider → LLMClient bridge

When an agent runs, the backend resolves its `Agent` record, fetches the `Provider` + `AvailableModel`, decrypts the API key if present, and constructs a `ProviderConfig` object. This is passed to `LLMClient` alongside the agent's rendered system message.

```
Agent record → ProviderConfig(model_string, api_base, api_key) → LLMClient.complete()
```

### System message rendering

```python
from jinja2 import Environment, StrictUndefined

env = Environment(undefined=StrictUndefined)
template = env.from_string(agent.system_message_template)
rendered = template.render(
    role_name=agent.role_name,
    role_description=agent.role_description,
    persona_name=agent.persona_name,
    persona_description=agent.persona_description,
    domain=study.domain,  # "Software Engineering"
    study_type=study.study_type.label,  # "Systematic Mapping Study"
)
```

### Admin panel tab layout (AdminPage.tsx)

```
AdminPage
├── Tab: "Service Health"   (existing ServiceHealthPanel)
├── Tab: "Jobs"             (existing JobRetryPanel)
├── Tab: "Providers"        (NEW: ProviderList + ProviderForm)
├── Tab: "Models"           (NEW: ModelList — scoped to selected provider)
└── Tab: "Agents"           (NEW: AgentList + AgentWizard/AgentForm)
```
