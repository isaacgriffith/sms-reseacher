# Implementation Plan: Models & Agents Management

**Branch**: `005-models-and-agents` | **Date**: 2026-03-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/005-models-and-agents/spec.md`

## Summary

Replace the hardcoded `agent_name` string on `Reviewer` with a full database-backed `Agent` entity. Introduce `Provider` and `AvailableModel` tables for multi-provider LLM support (Anthropic, OpenAI, Ollama). Add admin panel sections for managing providers, models, and agents — including a multi-step agent creation wizard with AI-generated system messages. Extend `LLMClient` with a `ProviderConfig` Protocol so agents use database-backed model configuration rather than environment variables.

## Technical Context

**Language/Version**: Python 3.14 (backend, agents, db); TypeScript 5.4 / Node 20 LTS (frontend)
**Primary Dependencies**: FastAPI + Pydantic v2, SQLAlchemy 2.0+ async, Alembic, LiteLLM, Jinja2, cryptography (Fernet), React 18, MUI v5, TanStack Query v5, react-hook-form + Zod
**Storage**: PostgreSQL 16 (production); SQLite + aiosqlite (tests)
**Testing**: pytest (asyncio_mode=auto), vitest, Playwright, deepeval, hypothesis (metamorphic)
**Target Platform**: Linux server (Docker Compose); browser (Chrome/Firefox)
**Project Type**: Web application (FastAPI backend + React frontend + Python agents)
**Performance Goals**: Provider model-list fetch completes in < 5 s; agent creation wizard submits in < 2 s (excluding AI generation); system message generation in < 30 s (LLM-bound)
**Constraints**: API keys never returned in API responses; Fernet encryption at rest; admin-only endpoints; zero downtime migration (agent_name retained temporarily)
**Scale/Scope**: Small number of providers (< 10), models per provider (< 200), agents (< 50) — admin-only configuration, not per-user

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| SOLID — no SRP violations in target modules | PASS | Provider/Model/Agent each have dedicated service classes; LLMClient concern is inference only |
| SOLID — extension points exist (OCP) where variation expected | PASS | ProviderConfig Protocol enables new providers without modifying LLMClient; AgentTaskType enum extensible |
| Structural — no DRY violations (duplication) | PASS | Single ProviderConfig abstraction; encryption logic in one utility module |
| Structural — no YAGNI violations (speculative generality) | PASS | Only three provider types in scope; no abstract factory beyond what's needed |
| Code clarity — no long methods (>20 lines) in touched code | PASS | Services decomposed into focused methods; agent creation wizard steps are separate components |
| Code clarity — no switch/if-chain smells in touched code | PASS | Provider-type dispatch uses a registry/strategy dict, not if-chain |
| Code clarity — no common code smells identified | PASS | Pre-implementation review: existing LLMClient is clean; Reviewer model will gain FK column only |
| Refactoring — pre-implementation review completed | PASS | Existing LLMClient, Reviewer, and AdminPage reviewed; no blocking violations found |
| Refactoring — any found refactors added to task list with tests | PASS | See Complexity Tracking — agent_name transitional column noted; cleanup task included |
| GRASP/patterns — responsibility assignments reviewed | PASS | ProviderConfig = Protected Variations; ProviderService = Information Expert; AgentService = Controller |
| Test coverage — existing tests pass; refactor tests written first | PASS | Existing coverage verified; new migration tested with upgrade/downgrade test |
| Toolchain (VII) — no unapproved deps or tool substitutions introduced | PASS | All deps already in approved stack (LiteLLM, Fernet, Jinja2, MUI v5, TanStack Query) |
| Toolchain (VII) — FastAPI/SQLAlchemy 2.x/ARQ/LiteLLM patterns followed | PASS | New routers use async def + Depends(); models use Mapped[T] + mapped_column() |
| Observability (VIII) — new models have audit fields + structlog used | PASS | All three new models have created_at/updated_at; version_id for optimistic locking; structlog in services |
| Observability (VIII) — config via Pydantic BaseSettings + lru_cache | PASS | No new settings classes needed; reuses existing BackendSettings and AgentSettings |
| Infrastructure (VIII) — Docker services have healthchecks if added | N/A | No new Docker services added |
| Language (IX) — React components functional, props typed, ≤100 JSX lines | PASS | All admin components planned as functional; SystemMessageEditor decomposed separately |
| Language (IX) — Hooks called at top level only (Rules of Hooks); no inline refs in deps | PASS | Wizard state managed via useReducer; no inline objects in dep arrays |
| Language (IX) — No React state mutation; no array-index keys in lists | PASS | Provider/model/agent lists keyed by UUID |
| Language (IX) — >3 related useState → useReducer; useCallback only when justified | PASS | AgentWizard uses useReducer for multi-step wizard state |
| Language (IX) — useEffect returns cleanup for all resource-acquiring effects | PASS | TanStack Query handles fetch lifecycle; no raw useEffect fetches |
| Language (IX) — React.memo applied deliberately; useImperativeHandle used for imperative APIs | PASS | SystemMessageEditor wrapped in React.memo (re-renders on large template changes would be costly) |
| Language (IX) — useWatch used (not watch) for reactive form field subscriptions | PASS | Provider type selector uses useWatch to conditionally show api_key/base_url fields |
| Language (IX) — Vite env vars use VITE_ prefix + import.meta.env | PASS | No new frontend env vars needed |
| Language (IX) — Python: no plain dict for domain data; pathlib used | PASS | ProviderConfig is a Protocol; all domain objects are Pydantic models or dataclasses |
| Language (IX) — Python: no mutable defaults; specific exception handling | PASS | Services raise specific HTTPException subtypes; no mutable defaults in new code |
| Language (IX) — TypeScript: no any/enum/non-null(!) without justification | PASS | API response types use Zod schemas; no any; string literal unions for provider type |
| Language (IX) — TypeScript: unknown + Zod at all external boundaries | PASS | All API responses parsed through Zod schemas before use |
| Code clarity — all functions/methods/classes have doc comments | PASS | Google-style docstrings required for all Python; JSDoc for all exported TS symbols |
| Feature completion docs (X) — CLAUDE.md, README, CHANGELOG update tasks in task list | PASS | TDOC tasks included in plan |

## Project Structure

### Documentation (this feature)

```text
specs/005-models-and-agents/
├── plan.md              # This file
├── research.md          # Decisions: LiteLLM format, model-list APIs, encryption, template vars
├── data-model.md        # Provider, AvailableModel, Agent entities + migration plan
├── quickstart.md        # Developer setup guide
├── contracts/
│   └── api-contracts.md # REST API endpoint contracts
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
# Database package (sms-db)
db/
├── src/db/
│   ├── models/
│   │   ├── agents.py        # NEW: Provider, AvailableModel, Agent models
│   │   ├── study.py         # MODIFIED: Reviewer gains agent_id FK
│   │   └── __init__.py      # MODIFIED: export new models
│   └── ...
└── alembic/versions/
    └── 0012_models_and_agents.py  # NEW: migration

# Backend package (sms-backend)
backend/
└── src/backend/
    ├── api/v1/admin/
    │   ├── providers.py     # NEW: Provider CRUD router
    │   ├── models.py        # NEW: AvailableModel management router
    │   ├── agents.py        # NEW: Agent CRUD + generate-system-message router
    │   └── router.py        # MODIFIED: register new sub-routers
    ├── services/
    │   ├── provider_service.py  # NEW: provider + model-fetch service
    │   └── agent_service.py     # NEW: agent CRUD + system-message generation service
    └── utils/
        └── encryption.py    # NEW (or extend existing): Fernet encrypt/decrypt utility

# Agents package (sms-agents)
agents/
└── src/agents/
    ├── core/
    │   ├── llm_client.py        # MODIFIED: ProviderConfig overload
    │   └── provider_config.py   # NEW: ProviderConfig Protocol
    ├── agent_generator.py       # NEW: AgentGeneratorAgent
    ├── screener.py              # MODIFIED: accept ProviderConfig override
    ├── extractor.py             # MODIFIED: accept ProviderConfig override
    └── prompts/
        └── agent_generator/
            ├── system.md        # NEW: static system prompt for AgentGenerator
            └── user.md.j2       # NEW: user prompt template for system-message generation

# Frontend package (sms-frontend)
frontend/
└── src/
    ├── pages/
    │   └── AdminPage.tsx             # MODIFIED: add Providers/Models/Agents tabs
    ├── components/admin/
    │   ├── providers/
    │   │   ├── ProviderList.tsx       # NEW
    │   │   └── ProviderForm.tsx       # NEW
    │   ├── models/
    │   │   └── ModelList.tsx          # NEW
    │   └── agents/
    │       ├── AgentList.tsx          # NEW
    │       ├── AgentWizard.tsx        # NEW: multi-step wizard (useReducer)
    │       ├── AgentForm.tsx          # NEW: edit form
    │       └── SystemMessageEditor.tsx # NEW: syntax-highlighted template editor
    ├── services/
    │   ├── providersApi.ts            # NEW: TanStack Query hooks + API calls
    │   └── agentsApi.ts               # NEW: TanStack Query hooks + API calls
    └── types/
        ├── provider.ts                # NEW: Zod schemas + inferred types
        └── agent.ts                   # NEW: Zod schemas + inferred types
```

**Structure Decision**: Web application layout (Option 2 from template). The feature touches four sub-packages: `sms-db` (models + migration), `sms-backend` (routers + services), `sms-agents` (LLMClient extension + new AgentGeneratorAgent), and the `frontend` (admin panel components + API clients). No new workspace packages are created — YAGNI.

## Complexity Tracking

| Item | Type | Why Accepted / Resolution |
|------|------|--------------------------|
| `agent_name` retained on Reviewer during transition | Tech debt | Zero-downtime migration requirement (R-007). Cleanup task T-CLEANUP-001 added: remove `agent_name` column in follow-up migration once all rows migrated. |
| `provider_id` denormalized on Agent | Design decision | Fast join path for provider display without multi-hop join; enforced by application-layer validation (model.provider_id == agent.provider_id). Documented in data-model.md. |
| AgentGenerator bootstrap seed | Architectural necessity | Bootstrapping chicken-and-egg (R-005); seed record uses static default prompt; documented in research.md. |

## Phase 0 Output

All unknowns resolved. See [research.md](research.md) for:
- R-001: LiteLLM model string format
- R-002: Provider model-list API endpoints
- R-003: API key encryption (Fernet reuse)
- R-004: Jinja2 system message template variables
- R-005: AgentGenerator bootstrapping strategy
- R-006: Persona SVG generation (optional, LLM-based)
- R-007: Reviewer migration strategy (nullable agent_id + agent_name retained)
- R-008: Optimistic locking for new models
- R-009: LLMClient ProviderConfig Protocol

## Phase 1 Output

- [data-model.md](data-model.md) — Entity definitions, columns, relationships, migration plan
- [contracts/api-contracts.md](contracts/api-contracts.md) — All REST endpoint contracts
- [quickstart.md](quickstart.md) — Developer setup guide and key file index
