# Research: Models & Agents Management

**Feature**: 005-models-and-agents
**Date**: 2026-03-16

---

## R-001: LiteLLM Model String Format per Provider

**Decision**: Use LiteLLM's provider-prefix model string convention for all three provider types.

| Provider | LiteLLM model string | API base override |
|----------|---------------------|-------------------|
| Anthropic | `anthropic/<model-id>` (e.g. `anthropic/claude-sonnet-4-6`) | None — key from env/passed header |
| OpenAI | `openai/<model-id>` (e.g. `openai/gpt-4o`) | None — key from env/passed header |
| Ollama | `ollama/<model-id>` (e.g. `ollama/llama3`) | `api_base=<configured_url>` |

**Rationale**: The existing `LLMClient` already uses this convention (`anthropic/<model>`, `ollama/<model>`). Extending it to OpenAI uses the same pattern with no architectural change. LiteLLM routes calls through the appropriate SDK based on the prefix.

**Alternatives considered**:
- Direct Anthropic/OpenAI SDK calls — rejected: prohibited by constitution (VII); breaks DIP.
- Unified URL-based routing — rejected: unnecessary indirection; LiteLLM handles this already.

---

## R-002: Provider Model-List API Endpoints

**Decision**: Fetch model lists from each provider's official catalog endpoint.

| Provider | Endpoint | Auth | Response key |
|----------|----------|------|--------------|
| Anthropic | `GET https://api.anthropic.com/v1/models` | `x-api-key: <key>` header | `.data[].id` |
| OpenAI | `GET https://api.openai.com/v1/models` | `Authorization: Bearer <key>` | `.data[].id` |
| Ollama | `GET <base_url>/api/tags` | None | `.models[].name` |

**Rationale**: Each provider exposes a canonical model-list endpoint. Fetching from these ensures the list is always current without hardcoding model identifiers.

**Alternatives considered**:
- Hardcoded model lists — rejected: stale as providers add/deprecate models.
- Scraping provider documentation — rejected: fragile and not machine-readable.

---

## R-003: API Key Encryption at Rest

**Decision**: Reuse the existing Fernet symmetric encryption pattern already established for TOTP secrets in Feature 004.

The `cryptography` library (`Fernet`) is already in the approved stack. The pattern is:
1. Derive encryption key from `SECRET_KEY` env var via `PBKDF2HMAC` (or use it as Fernet key directly if it is already 32-bytes base64url).
2. Encrypt API key on write; decrypt on use; never return plaintext in API responses.
3. Store the encrypted bytes as a base64 string column (`LargeBinary` or `String`).

**Rationale**: Consistent with Feature 004; no new dependency; Fernet provides authenticated encryption (tamper-evident).

**Alternatives considered**:
- AWS KMS / Vault — rejected: out of scope, external dependency, YAGNI.
- bcrypt — rejected: bcrypt is one-way; we need to recover the plaintext to make API calls.

---

## R-004: System Message Template Variable Injection

**Decision**: Use Jinja2 templates for system message rendering, consistent with the existing `prompt_loader.py` pattern.

Template variables:
- `{{ role_name }}` — the agent's role name (e.g., "Screener")
- `{{ role_description }}` — free-text description of the role
- `{{ persona_name }}` — persona display name (e.g., "Dr. Aria")
- `{{ persona_description }}` — narrative persona description
- `{{ domain }}` — research domain (e.g., "Software Engineering", "Artificial Intelligence")
- `{{ study_type }}` — study type label (e.g., "Systematic Mapping Study", "Systematic Literature Review")

**Rationale**: Jinja2 is already in the approved stack (agents/prompts). Using it for system messages keeps the prompt rendering path uniform. The existing `prompt_loader.py` already demonstrates the render pattern.

**Alternatives considered**:
- Python f-strings — rejected: cannot validate variable names at save time; no IDE support.
- Mustache/Handlebars — rejected: new dependency; Jinja2 already present.

---

## R-005: Agent Generator Agent Bootstrapping

**Decision**: Seed the database with a bootstrap Agent Generator agent during initial migration using a hardcoded default system message (not AI-generated). The seed record uses the existing `AgentSettings` (environment-based) model and Anthropic provider — these are created as seed Provider/Model records during migration.

**Rationale**: The Agent Generator agent is the only agent that cannot be created through the wizard (it would need to invoke itself). Bootstrapping via migration data ensures the system is immediately functional after upgrade.

**Alternatives considered**:
- Manual administrator creation — rejected: creates a chicken-and-egg problem (wizard needs AgentGenerator to generate messages, AgentGenerator doesn't exist yet).
- Embedded fallback prompt — rejected: hidden logic; violates SoC.

---

## R-006: Persona SVG Generation

**Decision**: Persona SVG generation is a best-effort optional step. It is implemented as a dedicated backend endpoint `POST /api/v1/admin/agents/generate-persona-svg` that calls a configured LLM with a prompt asking for an SVG illustration. The LLM must be instructed to return only valid SVG markup. The frontend displays the result in a preview before saving. If generation fails, the field is left empty and the agent is still functional.

**Rationale**: SVG generation quality varies by model; making it optional prevents it from blocking agent creation. The backend endpoint approach keeps the API key on the server side.

**Alternatives considered**:
- External image generation API (DALL-E, Stable Diffusion) — deferred: out of scope for initial implementation; API keys not yet in scope.
- Client-side generation — rejected: exposes API key to browser.

---

## R-007: Reviewer Migration Strategy

**Decision**: The `Reviewer` model gains a nullable `agent_id` FK column (UUID) pointing to the new `Agent` table. During migration, for every existing `Reviewer` row with `reviewer_type = 'ai_agent'`, an `Agent` record is created from the `agent_name` and default config values, and `agent_id` is back-filled. The `agent_name` column is retained (nullable) for one release cycle as a fallback, then removed in a follow-up migration.

**Rationale**: Zero-downtime migration: existing rows still function during the transition. The FK makes the new abstraction the authoritative reference. Retaining `agent_name` temporarily avoids a hard cutover that could break in-flight study operations.

**Alternatives considered**:
- Hard rename in single migration — rejected: risky for running studies; no rollback path.
- Dual-write to both columns — accepted as a transitional pattern, not permanent.

---

## R-008: Optimistic Locking for Agent Records

**Decision**: The `Agent`, `Provider`, and `AvailableModel` models all include a `version_id` column for SQLAlchemy optimistic locking (as required by the constitution for concurrently-updated models).

**Rationale**: Admin panel users may edit agents concurrently. Optimistic locking prevents silent overwrites.

---

## R-009: LLMClient Extension for Database-Backed Config

**Decision**: Introduce a `ProviderConfig` Protocol (TypeScript: interface) with `model_string: str`, `api_base: str | None`, `api_key: str | None`. The existing `LLMClient` gains an overload that accepts a `ProviderConfig` directly, bypassing `AgentSettings`. The existing environment-based path is preserved for backward compatibility.

**Rationale**: DIP compliance — agents depend on the `ProviderConfig` abstraction, not on a concrete settings object. Existing agents continue to work via `AgentSettings`; new agents use DB-backed config.

**Alternatives considered**:
- Replace AgentSettings entirely — rejected: breaks existing tests and env-based startup.
- Pass model string + api_base as raw strings — rejected: Primitive Obsession smell; no type safety.
