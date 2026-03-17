# Tasks: Models & Agents Management

**Input**: Design documents from `/specs/005-models-and-agents/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US5)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create all new directories and module stubs so that subsequent tasks have valid import paths and file targets.

- [x] T001 Create new module file stubs: `db/src/db/models/agents.py`, `backend/src/backend/utils/encryption.py`, `agents/src/agents/core/provider_config.py`, `agents/src/agents/agent_generator.py` (empty files with module-level docstrings only)
- [x] T002 Create new router and service stubs: `backend/src/backend/api/v1/admin/providers.py`, `backend/src/backend/api/v1/admin/models_router.py`, `backend/src/backend/api/v1/admin/agents.py`, `backend/src/backend/services/provider_service.py`, `backend/src/backend/services/agent_service.py` (empty files with module-level docstrings only)
- [x] T003 Create new frontend directory stubs and empty index files: `frontend/src/components/admin/providers/`, `frontend/src/components/admin/models/`, `frontend/src/components/admin/agents/`, `frontend/src/types/provider.ts`, `frontend/src/types/agent.ts`, `frontend/src/services/providersApi.ts`, `frontend/src/services/agentsApi.ts`
- [x] T004 Create agent prompt directories and stub files: `agents/src/agents/prompts/agent_generator/system.md` and `agents/src/agents/prompts/agent_generator/user.md.j2` (placeholder content)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core DB models, migration, Protocol, and utilities that ALL user stories depend on. No user story work can begin until this phase is complete.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T005 [P] Define `ProviderType` (anthropic/openai/ollama) and `AgentTaskType` (screener/extractor/librarian/expert/quality_judge/agent_generator/domain_modeler/synthesiser/validity_assessor) as `StrEnum` subclasses in `db/src/db/models/agents.py`
- [x] T006 [P] Implement `Provider` SQLAlchemy model with all columns from data-model.md (id UUID PK, provider_type, display_name, api_key_encrypted LargeBinary nullable, base_url nullable, is_enabled, version_id, created_at, updated_at) in `db/src/db/models/agents.py`
- [x] T007 [P] Implement `AvailableModel` SQLAlchemy model with all columns from data-model.md (id UUID PK, provider_id FK, model_identifier, display_name, is_enabled, version_id, created_at, updated_at; unique constraint on provider_id+model_identifier) in `db/src/db/models/agents.py`
- [x] T008 Implement `Agent` SQLAlchemy model with all columns from data-model.md (id UUID PK, task_type, role_name, role_description, persona_name, persona_description, persona_svg, system_message_template, system_message_undo_buffer, model_id FK, provider_id FK, is_active, version_id, created_at, updated_at; SQLAlchemy optimistic locking via `__mapper_args__`) in `db/src/db/models/agents.py` (depends on T006, T007)
- [x] T009 Add nullable `agent_id` UUID FK column (FK → Agent, SET NULL on delete) to `Reviewer` model in `db/src/db/models/study.py`; retain existing `agent_name` column unchanged
- [x] T010 Export `ProviderType`, `AgentTaskType`, `Provider`, `AvailableModel`, `Agent` from `db/src/db/models/__init__.py`
- [x] T011 Create Alembic migration `db/alembic/versions/0012_models_and_agents.py` with `upgrade()` creating the `providertype` and `agenttasktype` PostgreSQL enums, then `provider`, `available_model`, and `agent` tables, then adding `agent_id` nullable FK column to `reviewer`; `downgrade()` reverses all steps in order
- [x] T012 [P] Implement Fernet encrypt/decrypt utility in `backend/src/backend/utils/encryption.py`: `encrypt_secret(plaintext: str, secret_key: str) -> bytes` and `decrypt_secret(ciphertext: bytes, secret_key: str) -> str` using `cryptography.fernet.Fernet`; derive key from SECRET_KEY via PBKDF2HMAC; include Google-style docstrings
- [x] T013 [P] Define `ProviderConfig` Protocol in `agents/src/agents/core/provider_config.py` with attributes `model_string: str`, `api_base: str | None`, `api_key: str | None`; use `typing.Protocol` (runtime-checkable); include JSDoc-equivalent Google-style docstring
- [x] T014 Extend `LLMClient.complete()` in `agents/src/agents/core/llm_client.py` to accept an optional `provider_config: ProviderConfig | None = None` parameter; when provided, override the model string, api_base, and api_key from the Protocol rather than `AgentSettings`; preserve all existing env-based behavior when `provider_config` is None (depends on T013)
- [x] T015 Register new admin sub-routers in the backend admin router (create `backend/src/backend/api/v1/admin/__init__.py` if absent, or extend the existing admin router file) to include `providers_router`, `models_router`, and `agents_router` under the `/admin` prefix

**Checkpoint**: Foundation ready — DB schema, encryption, ProviderConfig Protocol, and LLMClient extension are all in place. User story phases can now begin.

---

## Phase 3: User Story 1 — Configure an LLM Provider (Priority: P1) 🎯 MVP

**Goal**: Administrators can add Anthropic, OpenAI, or Ollama providers from the admin panel, see the fetched model list, and enable/disable individual models — without modifying config files.

**Independent Test**: Add an Anthropic provider via `POST /api/v1/admin/providers`, call `GET /api/v1/admin/providers/{id}/models`, verify at least one model is returned and can be toggled via `PATCH`.

### Implementation for User Story 1

- [x] T016 [P] [US1] Implement `ProviderService.fetch_models_anthropic(api_key: str) -> list[ModelRecord]` in `backend/src/backend/services/provider_service.py`: call `GET https://api.anthropic.com/v1/models` with `x-api-key` header, parse `.data[].id`, return list of `ModelRecord(model_identifier, display_name)` Pydantic models; raise `ProviderFetchError` on HTTP failure
- [x] T017 [P] [US1] Implement `ProviderService.fetch_models_openai(api_key: str) -> list[ModelRecord]` in `backend/src/backend/services/provider_service.py`: call `GET https://api.openai.com/v1/models` with `Authorization: Bearer` header, parse `.data[].id`; raise `ProviderFetchError` on HTTP failure
- [x] T018 [P] [US1] Implement `ProviderService.fetch_models_ollama(base_url: str) -> list[ModelRecord]` in `backend/src/backend/services/provider_service.py`: call `GET {base_url}/api/tags`, parse `.models[].name`; raise `ProviderFetchError` on HTTP failure
- [x] T019 [US1] Implement `ProviderService` CRUD methods in `backend/src/backend/services/provider_service.py`: `create_provider`, `list_providers`, `get_provider`, `update_provider`, `delete_provider`; `create_provider` and `update_provider` encrypt `api_key` via `encryption.encrypt_secret`; `delete_provider` raises `ProviderHasDependentsError` if agents reference it; all use `async with` SQLAlchemy sessions (depends on T012, T016–T018)
- [x] T020 [US1] Implement `ProviderService.refresh_models(provider_id, session)` in `backend/src/backend/services/provider_service.py`: decrypt api_key, call the correct fetcher based on `provider_type`, upsert `AvailableModel` rows (insert new, retain existing with updated display_name), return `ModelRefreshResult(models_added, models_removed, models_total)`; preserve existing model enable/disable state; retain previously loaded models if provider is unreachable (raise `ProviderFetchError` without mutating DB) (depends on T019)
- [x] T021 [US1] Implement `GET /api/v1/admin/providers` and `POST /api/v1/admin/providers` endpoints in `backend/src/backend/api/v1/admin/providers.py`; POST triggers `refresh_models` after successful creation; response schema never returns `api_key_encrypted`, instead returns `has_api_key: bool`; use FastAPI `Depends()` for session and auth injection
- [x] T022 [US1] Implement `GET`, `PATCH`, and `DELETE /api/v1/admin/providers/{provider_id}` endpoints in `backend/src/backend/api/v1/admin/providers.py`; PATCH supports partial update of display_name, api_key, base_url, is_enabled; DELETE raises HTTP 409 with dependent agent IDs if applicable
- [x] T023 [US1] Implement `POST /api/v1/admin/providers/{provider_id}/refresh-models` endpoint in `backend/src/backend/api/v1/admin/providers.py`; return `ModelRefreshResult` on success; return HTTP 502 on `ProviderFetchError`
- [x] T024 [US1] Implement `GET /api/v1/admin/providers/{provider_id}/models` and `PATCH /api/v1/admin/providers/{provider_id}/models/{model_id}` endpoints in `backend/src/backend/api/v1/admin/models_router.py`; PATCH accepts `{"is_enabled": bool}`; PATCH raises HTTP 409 with dependent agent IDs if disabling a model that has active agents
- [x] T025 [P] [US1] Define Zod schemas and inferred TypeScript interfaces for `Provider`, `ProviderCreate`, `ProviderUpdate`, `AvailableModel`, `ModelRefreshResult` in `frontend/src/types/provider.ts`; use `z.union([z.literal('anthropic'), z.literal('openai'), z.literal('ollama')])` for provider type (no TypeScript enum)
- [x] T026 [US1] Implement TanStack Query hooks in `frontend/src/services/providersApi.ts`: `useProviders()`, `useProvider(id)`, `useCreateProvider()`, `useUpdateProvider()`, `useDeleteProvider()`, `useRefreshModels()`, `useProviderModels(providerId)`, `useToggleModel()`; parse all API responses through Zod schemas before returning (depends on T025)
- [x] T027 [P] [US1] Implement `ProviderList.tsx` in `frontend/src/components/admin/providers/ProviderList.tsx`: MUI Table showing provider type, display name, enabled status, has_api_key badge, and action buttons (edit, delete, refresh-models); props typed with named interface; ≤100 JSX lines; JSDoc on all exported symbols
- [x] T028 [US1] Implement `ProviderForm.tsx` in `frontend/src/components/admin/providers/ProviderForm.tsx`: react-hook-form + Zod; `useWatch` on `provider_type` to conditionally show `api_key` field (Anthropic/OpenAI) or `base_url` field (Ollama); handles create and update modes; validates required fields per provider type
- [x] T029 [US1] Implement `ModelList.tsx` in `frontend/src/components/admin/models/ModelList.tsx`: MUI Table showing model_identifier, display_name, is_enabled toggle; calls `useProviderModels` and `useToggleModel`; scoped to a selected `providerId` prop
- [x] T030 [US1] Extend `AdminPage.tsx` at `frontend/src/pages/AdminPage.tsx` to add "Providers" and "Models" MUI Tabs; render `ProviderList` + `ProviderForm` under Providers tab; render `ModelList` (with selected-provider context) under Models tab; use `useReducer` if AdminPage accumulates more than 3 related `useState` calls

**Checkpoint**: US1 fully functional — provider creation, model list fetch, and model enable/disable all work end-to-end.

---

## Phase 4: User Story 2 — Create a New Agent (Priority: P2)

**Goal**: Administrators can create a new agent via a multi-step wizard: select task type, pick a model, fill role/persona, optionally generate persona SVG, generate and review the AI-produced system message, then save.

**Independent Test**: Complete the wizard for `task_type=screener`, click "Generate System Message," verify a Jinja2 template is returned with `{{ role_name }}` and `{{ domain }}` variables, save the agent, and confirm it appears in the agent list.

### Implementation for User Story 2

- [x] T031 [US2] Write `agents/src/agents/prompts/agent_generator/system.md`: static system prompt instructing the AgentGenerator to produce a Jinja2 system message template incorporating role, persona, model, domain, and study_type variables; include instructions on using `{{ role_name }}`, `{{ persona_name }}`, `{{ domain }}`, `{{ study_type }}` placeholders
- [x] T032 [US2] Write `agents/src/agents/prompts/agent_generator/user.md.j2`: Jinja2 user prompt template for system-message generation requests; variables: `task_type`, `role_name`, `role_description`, `persona_name`, `persona_description`, `model_display_name`
- [x] T033 [US2] Implement `AgentGeneratorAgent` class in `agents/src/agents/agent_generator.py`: `async def generate_system_message(task_type, role_name, role_description, persona_name, persona_description, model_display_name, provider_config) -> str`; loads prompts via `prompt_loader`; routes LLM call through `LLMClient.complete()` with `provider_config`; returns the raw template string; include Google-style docstrings (depends on T014, T031, T032)
- [x] T034 [US2] Implement `AgentService.create_agent` and `AgentService.list_agents` in `backend/src/backend/services/agent_service.py`: `create_agent` validates that `model_id` references an enabled model whose `provider_id` matches the supplied `provider_id`, validates Jinja2 template syntax with `StrictUndefined` and known-variable allowlist (role_name, role_description, persona_name, persona_description, domain, study_type), then persists; `list_agents` supports optional `task_type` and `is_active` filters
- [x] T035 [US2] Implement `AgentService.get_agent_task_types() -> list[str]` in `backend/src/backend/services/agent_service.py` returning all `AgentTaskType` enum values as strings
- [x] T036 [US2] Implement `AgentService.generate_system_message(agent_id_or_draft, session) -> str` in `backend/src/backend/services/agent_service.py`: resolve the bootstrap `AgentGenerator` Agent record from DB, build its `ProviderConfig` (decrypt api_key), instantiate `AgentGeneratorAgent`, call `generate_system_message`; if the agent already has a `system_message_template`, move it to `system_message_undo_buffer` before overwriting (depends on T033, T034)
- [x] T037 [US2] Implement `AgentService.generate_persona_svg(persona_name, persona_description, provider_config) -> str` in `backend/src/backend/services/agent_service.py`: call LLM with a prompt requesting only SVG markup; validate response starts with `<svg`; raise `PersonaSvgGenerationError` if invalid
- [x] T038 [US2] Implement `GET /api/v1/admin/agents`, `POST /api/v1/admin/agents`, and `GET /api/v1/admin/agent-task-types` endpoints in `backend/src/backend/api/v1/admin/agents.py`; POST response includes full agent record with `system_message_template`
- [x] T039 [US2] Implement `POST /api/v1/admin/agents/{agent_id}/generate-system-message` and `POST /api/v1/admin/agents/generate-persona-svg` endpoints in `backend/src/backend/api/v1/admin/agents.py`; generate-system-message returns HTTP 409 if no AgentGenerator agent is configured; returns HTTP 502 on LLM failure
- [x] T040 [P] [US2] Define Zod schemas and TypeScript interfaces for `Agent`, `AgentCreate`, `AgentSummary`, `SystemMessageGenerateResult`, `PersonaSvgGenerateResult` in `frontend/src/types/agent.ts`; agent `task_type` typed as string literal union matching `AgentTaskType` values
- [x] T041 [US2] Implement TanStack Query hooks in `frontend/src/services/agentsApi.ts`: `useAgents()`, `useAgent(id)`, `useCreateAgent()`, `useGenerateSystemMessage()`, `useGeneratePersonaSvg()`, `useAgentTaskTypes()`; all responses parsed through Zod schemas (depends on T040)
- [x] T042 [P] [US2] Implement `AgentList.tsx` in `frontend/src/components/admin/agents/AgentList.tsx`: MUI Table with columns role_name, persona_name, task_type, model display name, is_active badge, and action buttons (edit, view); keyed by agent UUID; ≤100 JSX lines
- [x] T043 [US2] Implement `SystemMessageEditor.tsx` in `frontend/src/components/admin/agents/SystemMessageEditor.tsx`: MUI `TextField` multiline with syntax-highlighted template variable placeholders (highlight `{{ variable }}` patterns); wraps a `React.memo` component for render efficiency; exposes `value`, `onChange`, `onUndo`, `canUndo` props; typed with named interface; `useImperativeHandle` + `forwardRef` if parent needs to programmatically focus
- [x] T044 [US2] Implement `AgentWizard.tsx` in `frontend/src/components/admin/agents/AgentWizard.tsx`: MUI `Stepper` with 5 steps (task type → model selection → role/persona → SVG → system message review); wizard state managed via `useReducer` (not multiple `useState`); each step validates before advancing; "Generate System Message" calls `useGenerateSystemMessage` mutation; "Generate SVG" calls `useGeneratePersonaSvg`; final step submits via `useCreateAgent`; `useWatch` for reactive provider-type-dependent model list
- [x] T045 [US2] Extend `AdminPage.tsx` at `frontend/src/pages/AdminPage.tsx` to add "Agents" MUI Tab; render `AgentList` with a "Create Agent" button that opens `AgentWizard`; wire `useAgents` query to `AgentList`

**Checkpoint**: US2 fully functional — the full agent creation wizard works end-to-end including AI-generated system message and optional persona SVG.

---

## Phase 5: User Story 3 — Edit an Existing Agent (Priority: P3)

**Goal**: Administrators can edit any agent field, regenerate the system message (with previous version preserved in undo buffer), and restore the previous version with one click.

**Independent Test**: Open an existing agent in edit mode, update `persona_name`, save, verify the change persists; then click "Generate/Update System Message," verify a new template is returned and the previous is stored; click "Undo," verify the original message is restored.

### Implementation for User Story 3

- [x] T046 [US3] Implement `AgentService.get_agent`, `AgentService.update_agent`, and `AgentService.deactivate_agent` in `backend/src/backend/services/agent_service.py`: `update_agent` validates changed `system_message_template` via Jinja2 allowlist; raises HTTP 409 via `AgentHasDependentsError` if deactivating an agent referenced by active Reviewer records; uses optimistic locking via SQLAlchemy `version_id` (depends on T034)
- [x] T047 [US3] Implement `AgentService.restore_system_message(agent_id, session)` in `backend/src/backend/services/agent_service.py`: swaps `system_message_template` with `system_message_undo_buffer`; raises `NoUndoBufferError` if buffer is NULL
- [x] T048 [US3] Implement `GET /api/v1/admin/agents/{agent_id}`, `PATCH /api/v1/admin/agents/{agent_id}`, and `DELETE /api/v1/admin/agents/{agent_id}` endpoints in `backend/src/backend/api/v1/admin/agents.py`; GET returns full agent including `system_message_undo_buffer`; DELETE soft-deletes (is_active=false); PATCH returns HTTP 409 on version conflict
- [x] T049 [US3] Implement `POST /api/v1/admin/agents/{agent_id}/undo-system-message` endpoint in `backend/src/backend/api/v1/admin/agents.py`; returns updated full agent; HTTP 409 if no undo buffer available (depends on T047)
- [x] T050 [US3] Add TanStack Query hooks to `frontend/src/services/agentsApi.ts`: `useUpdateAgent()`, `useDeleteAgent()`, `useUndoSystemMessage()`; update existing `useGenerateSystemMessage` to update undo buffer state in TanStack Query cache after success (depends on T041)
- [x] T051 [US3] Implement `AgentForm.tsx` in `frontend/src/components/admin/agents/AgentForm.tsx`: react-hook-form + Zod edit form with all agent fields; embeds `SystemMessageEditor` for the template field; shows "Generate/Update System Message" button (calls `useGenerateSystemMessage`) and "Undo" button (calls `useUndoSystemMessage`, disabled when `canUndo` is false); `useWatch` on `model_id` to warn when selected model is disabled
- [x] T052 [US3] Wire `AgentForm` into the Agents tab in `frontend/src/pages/AdminPage.tsx`: clicking edit in `AgentList` opens `AgentForm` in an MUI Dialog or slide-over panel; on save, invalidates the `useAgents` TanStack query cache

**Checkpoint**: US3 fully functional — full agent edit workflow with undo buffer works end-to-end.

---

## Phase 6: User Story 4 — Migrate Existing Agents to New Abstraction (Priority: P4)

**Goal**: After migration, existing Screener and Extractor research workflows continue to work without any manual administrator configuration.

**Independent Test**: After `alembic upgrade head`, verify that `SELECT * FROM agent` contains at least a Screener agent and an AgentGenerator agent; verify that all `reviewer` rows with `reviewer_type='ai_agent'` have `agent_id` populated; run the existing Screener integration test against a sample paper and confirm a valid result.

### Implementation for User Story 4

- [x] T053 [US4] Augment migration `db/alembic/versions/0012_models_and_agents.py` upgrade: add seed block that (1) inserts a default Anthropic Provider record if `ANTHROPIC_API_KEY` env var is set, (2) inserts a bootstrap `AgentGenerator` Agent record with a static default system message template and task_type `agent_generator`, (3) inserts `Screener` and `Extractor` Agent records with role descriptions and default system message templates derived from existing prompt content; all seeds are conditional (`INSERT ... WHERE NOT EXISTS`)
- [x] T054 [US4] Augment migration `db/alembic/versions/0012_models_and_agents.py` upgrade: add backfill block that updates `reviewer.agent_id` for every row where `reviewer_type='ai_agent'` and `agent_name` matches a known seeded agent name (screener → Screener Agent id, extractor → Extractor Agent id); rows with unknown `agent_name` values are logged as warnings but not failed
- [x] T055 [P] [US4] Update `ScreenerAgent` in `agents/src/agents/screener.py` to accept `provider_config: ProviderConfig | None = None` parameter in `__init__`; pass it through to `LLMClient.complete()` calls; preserve all existing default env-based behavior when `provider_config` is None
- [x] T056 [P] [US4] Update `ExtractorAgent` in `agents/src/agents/extractor.py` to accept `provider_config: ProviderConfig | None = None` parameter; same pattern as T055
- [x] T057 [US4] Update all remaining agent classes (`LibrarianAgent` in `librarian.py`, `ExpertAgent` in `expert.py`, `QualityJudgeAgent` in `quality_judge.py`, `DomainModelerAgent` in `domain_modeler.py`, `SynthesiserAgent` in `synthesiser.py`, `ValidityAgent` in `validity.py`) to accept optional `provider_config` parameter; consistent pattern across all agents (depends on T055, T056)

**Checkpoint**: US4 fully functional — post-migration, existing Screener and Extractor workflows produce identical results to pre-migration behavior.

---

## Phase 7: User Story 5 — Domain & Study-Type Variable Injection (Priority: P5)

**Goal**: A single agent definition can serve multiple research domains (SE/AI) and study types (SMS, SLR, etc.) by injecting domain and study_type context variables into the system message at render time.

**Independent Test**: Create one Screener agent with a template containing `{{ domain }}` and `{{ study_type }}`; run screening for an SMS study with domain "Software Engineering" and confirm the rendered system message contains "Software Engineering" and "Systematic Mapping Study"; repeat for an SLR study and confirm different rendered text.

### Implementation for User Story 5

- [x] T058 [US5] Implement `render_system_message(template: str, agent: Agent, domain: str, study_type: str) -> str` in `backend/src/backend/services/agent_service.py`: use `jinja2.Environment(undefined=jinja2.StrictUndefined)`; bind `role_name`, `role_description`, `persona_name`, `persona_description`, `domain`, `study_type`; raise `TemplateRenderError` with the Jinja2 `UndefinedError` message if an unknown variable is referenced (depends on T034)
- [x] T059 [US5] Implement `build_study_context(study: Study) -> StudyContext` in `backend/src/backend/services/agent_service.py`: map `study.study_type` enum value to a human-readable label (e.g., `StudyType.sms` → `"Systematic Mapping Study"`); map `study.domain` (if present) or default to `"Software Engineering and Artificial Intelligence"`; return a `StudyContext` dataclass
- [x] T060 [US5] Update `AgentService.create_agent` and `AgentService.update_agent` to call `render_system_message` with dummy context values (`domain="[domain]"`, `study_type="[study_type]"`) during save-time validation; any `TemplateRenderError` due to unknown variable names (not the placeholder values) raises HTTP 422 with the variable name (depends on T058)
- [x] T061 [US5] Update the backend job/service that invokes `ScreenerAgent` (locate in `backend/src/backend/services/` or `backend/src/backend/jobs/`) to resolve the `Reviewer`'s `agent_id`, load the `Agent` record, call `render_system_message` with the study's domain and study_type context, and pass the rendered message as the system message to `ScreenerAgent`; use `ProviderConfig` built from the Agent's provider record (depends on T055, T058, T059)
- [x] T062 [US5] Apply the same study-context rendering to the `ExtractorAgent` invocation path in the backend: resolve agent record, render system message, build ProviderConfig, pass to ExtractorAgent (depends on T056, T058, T059)
- [x] T063 [US5] Apply the same study-context rendering to all remaining agent invocation paths (Librarian, Expert, QualityJudge, DomainModeler, Synthesiser, Validity) in the backend services/jobs (depends on T057, T058, T059)

**Checkpoint**: US5 fully functional — one agent definition serves multiple domains and study types via injected variables; saving a template with unknown variable names is rejected at the API level.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Test coverage, evaluation pipelines, metamorphic tests, e2e tests, and the agent_name cleanup stub.

- [x] T064 [P] Add unit tests for `ProviderService`: test model-list fetch for each provider type (mock HTTP), test encrypt/decrypt roundtrip, test CRUD validation rules, test `ProviderHasDependentsError` on delete in `backend/tests/unit/services/test_provider_service.py`
- [x] T065 [P] Add unit tests for `AgentService`: test create/list/update/deactivate, test Jinja2 template validation (accept valid, reject unknown variable), test `render_system_message` (correct substitution, StrictUndefined error), test undo buffer swap in `backend/tests/unit/services/agent_service.py`
- [x] T066 [P] Add unit tests for `encryption.py`: test encrypt→decrypt roundtrip, test that decryption with wrong key raises `InvalidToken`, test byte-stability across calls in `backend/tests/unit/utils/test_encryption.py`
- [x] T067 [P] Add unit tests for `ProviderConfig` Protocol and `LLMClient` ProviderConfig overload: test that `LLMClient.complete()` uses `provider_config.model_string` and `api_base` when provided; test fallback to `AgentSettings` when `provider_config` is None in `agents/tests/unit/core/test_llm_client.py`
- [x] T068 [P] Add integration tests for provider CRUD endpoints and refresh-models: test POST creates provider and returns has_api_key, test PATCH updates api_key, test DELETE returns 409 when agents depend on provider, test refresh-models returns 502 on unreachable provider in `backend/tests/integration/api/admin/test_providers.py`
- [x] T069 [P] Add integration tests for agent CRUD endpoints: test POST /agents with valid and invalid templates, test GET /agents filtering, test PATCH returns 409 on version conflict, test POST generate-system-message stores undo buffer, test POST undo-system-message restores previous message in `backend/tests/integration/api/admin/test_agents.py`
- [x] T070 [P] Add Alembic migration test for `0012_models_and_agents`: test `upgrade()` creates all three tables and `agent_id` column, test seed records are present, test `downgrade()` removes them cleanly in `db/tests/integration/test_migration_0012.py`
- [x] T071 [P] Add metamorphic tests for `AgentGeneratorAgent` in `agents/tests/metamorphic/test_agent_generator.py`: define metamorphic relation that paraphrasing the role description produces a system message that still contains all required Jinja2 variable placeholders; use `hypothesis` for property-based inputs
- [x] T072 [P] Add deepeval evaluation pipeline for `AgentGeneratorAgent` in `agent-eval/src/agent_eval/pipelines/agent_generator_eval.py`: dataset of 5 representative role/persona inputs; metrics: `AnswerRelevancyMetric` (generated message must reference role name) and `FaithfulnessMetric` (no hallucinated variable names); set minimum threshold 0.8
- [x] T073 [P] Add Playwright e2e test for provider management flow in `frontend/e2e/admin/test_provider_management.spec.ts`: log in as admin, navigate to Admin → Providers, create an Ollama provider, verify model list appears, toggle a model off, verify it is shown as disabled
- [x] T074 [P] Add Playwright e2e test for agent creation wizard in `frontend/e2e/admin/test_agent_wizard.spec.ts`: navigate to Admin → Agents, open wizard, complete all steps including system message generation, save, verify agent appears in list with correct role and persona name
- [x] T075 Run `uv run pytest` with `--cov-fail-under=85` across all modified packages (backend, agents, db, agent-eval) and `cd frontend && npm run test:coverage`; verify all packages meet ≥85% line/branch coverage; fix any gaps before marking polish complete
- [x] T076 Create stub migration `db/alembic/versions/0013_remove_reviewer_agent_name.py` with `upgrade()` body of `# TODO: remove reviewer.agent_name column once all rows have agent_id populated` and `downgrade()` as no-op; this signals the cleanup debt without executing it prematurely

---

## Phase 9: Feature Completion Documentation *(mandatory — Constitution Principle X)*

**Purpose**: Update all required documentation before the feature branch is merged.

> **These tasks MUST be completed before the feature is marked done. Omitting them is a blocking violation of Constitution Principle X.**

- [x] TDOC1 [P] Update `CLAUDE.md` at repository root: add `005-models-and-agents` to the Active Technologies and Recent Changes sections; document the new admin panel Providers/Models/Agents tabs; note the `ProviderConfig` Protocol pattern for agents
- [x] TDOC2 [P] Update `README.md` at repository root: add LLM provider configuration and agent management to the feature list; describe the three supported provider types; update architecture overview
- [x] TDOC3 [P] Update `CHANGELOG.md` at repository root with a new `## [Unreleased]` entry describing: new Provider/AvailableModel/Agent tables, multi-provider LLM support (Anthropic/OpenAI/Ollama), admin panel agent management wizard, system message template variables, Reviewer migration (follow Keep a Changelog format)
- [x] TDOC4 [P] Update `README.md` in each modified subproject: `backend/README.md` (new admin endpoints), `agents/README.md` (ProviderConfig Protocol, AgentGeneratorAgent), `db/README.md` (migration 0012), `frontend/README.md` (new admin tabs), `agent-eval/README.md` (AgentGeneratorAgent eval pipeline)
- [x] TDOC5 [P] Update `CHANGELOG.md` in each modified subproject (`backend/`, `agents/`, `db/`, `frontend/`, `agent-eval/`) with the same level of detail as the root changelog entry

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1, T001–T004)**: No dependencies — start immediately
- **Foundational (Phase 2, T005–T015)**: Depends on Phase 1 — **blocks all user story phases**
- **User Story phases (Phase 3–7)**: All depend on Phase 2 completion; can proceed in priority order or in parallel across stories if staffed
  - US2 (Phase 4) depends on US1 (Phase 3) being complete only for the `useAgents` TanStack integration in AdminPage — otherwise independently implementable
  - US3 (Phase 5) depends on US2 (Phase 4) for `AgentForm`/`SystemMessageEditor` reuse
  - US4 (Phase 6) is independent of US1–US3 on the backend; migration seed data can be written in parallel with frontend work
  - US5 (Phase 7) depends on US4 (Phase 6) for the agent invocation paths
- **Polish (Phase 8, T064–T076)**: Depends on all user story phases being functionally complete
- **Documentation (Phase 9)**: Depends on Phase 8 completion

### User Story Dependencies

| User Story | Depends On | Notes |
|------------|-----------|-------|
| US1 (P1) | Phase 2 complete | Independent — pure provider/model CRUD |
| US2 (P2) | Phase 2 + US1 (frontend tab wiring) | AgentGeneratorAgent needs bootstrap Agent record from migration |
| US3 (P3) | US2 (reuses AgentForm, SystemMessageEditor) | Backend endpoints independent; frontend builds on US2 components |
| US4 (P4) | Phase 2 (migration file) | Backend agent class updates independent of US1–US3 |
| US5 (P5) | US4 (agent invocation paths) | Rendering depends on ProviderConfig overload from US4 |

### Within Each User Story

- Services before endpoints
- Endpoints before frontend hooks
- Frontend hooks before components
- Components before page integration

### Parallel Opportunities

- **Phase 2**: T005, T006, T007 (separate model definitions), T012, T013 can all start in parallel
- **Phase 3 (US1)**: T016, T017, T018 (three separate fetcher methods); T025, T027 (types + list component)
- **Phase 4 (US2)**: T031, T032 (two separate prompt files); T040, T042 (types + list component)
- **Phase 6 (US4)**: T055, T056 (Screener and Extractor updates are separate files)
- **Phase 8**: T064–T074 are all independent test files; all can run in parallel
- **Phase 9**: TDOC1–TDOC5 are all independent documentation files; all can run in parallel

---

## Parallel Example: Phase 2 (Foundation)

```bash
# These can run in parallel (different files):
Task T005: "Define ProviderType and AgentTaskType enums in db/src/db/models/agents.py"
Task T012: "Implement Fernet encryption utility in backend/src/backend/utils/encryption.py"
Task T013: "Define ProviderConfig Protocol in agents/src/agents/core/provider_config.py"

# Then these can run in parallel after T005, T006, T007 complete:
Task T008: "Implement Agent model (depends on Provider and AvailableModel)"
Task T011: "Create Alembic migration 0012"
```

## Parallel Example: User Story 1 (US1)

```bash
# These can run in parallel:
Task T016: "fetch_models_anthropic in provider_service.py"
Task T017: "fetch_models_openai in provider_service.py"
Task T018: "fetch_models_ollama in provider_service.py"
Task T025: "Zod schemas in frontend/src/types/provider.ts"
Task T027: "ProviderList.tsx component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T015) — **CRITICAL: blocks all stories**
3. Complete Phase 3: User Story 1 (T014–T030)
4. **STOP and VALIDATE**: Test provider creation + model fetch + model toggle end-to-end
5. Demo to stakeholders — administrators can now add providers without config files

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 → Provider/model management functional → Demo/Deploy (MVP)
3. US2 → Agent creation wizard functional → Demo/Deploy
4. US3 → Agent editing + undo buffer → Demo/Deploy
5. US4 → Migration + existing agent compatibility confirmed → Deploy to staging
6. US5 → Domain/study-type variable injection → Full feature complete

### Parallel Team Strategy

With multiple developers after Phase 2 completes:
- **Developer A**: US1 (Phase 3) — provider/model management
- **Developer B**: US4 (Phase 6) — migration seed data + agent class ProviderConfig updates
- Once US1 and US4 complete:
  - **Developer A**: US2 + US3 (Phases 4 + 5) — agent wizard and edit
  - **Developer B**: US5 (Phase 7) — domain/study-type injection

---

## Notes

- [P] tasks operate on different files or have no shared dependencies — safe to parallelize
- [Story] label maps each task to its user story for traceability
- Every user story is independently completable and testable at its checkpoint
- Constitution compliance: all tasks respect Principles I–X
- New DB models have `created_at`/`updated_at` + `version_id` (optimistic locking) — Principle VIII
- All LLM calls route through `LLMClient` with `ProviderConfig` — Principle VII
- Python: Google-style docstrings required on all functions/classes; no plain dict, use Pydantic/dataclass — Principle IX
- TypeScript: no `any`, no TS `enum`, Zod at all API boundaries, named props interfaces — Principle IX
- React: functional components ≤100 JSX lines; `useReducer` for wizard state; `useWatch` not `watch`; `React.memo` on `SystemMessageEditor`; `useImperativeHandle` for imperative child APIs — Principle IX
- API keys are never returned in API responses — always `has_api_key: bool` only
- Optimistic locking (`version_id`) on Provider, AvailableModel, and Agent — Principle VIII
- `agent_name` column on Reviewer is retained (not removed) — T076 creates the cleanup stub
