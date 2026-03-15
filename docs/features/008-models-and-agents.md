# Feature: Models & Agents Management

**Feature ID**: 008-models-and-agents
**Depends On**: 001-repo-setup, 002-sms-workflow
**Reference**: `docs/todo.md` (Models and Agents section)

---

## Overview

Introduce a flexible, database-backed abstraction for AI agents and their underlying LLM models. This feature replaces any hardcoded model/agent configuration with a manageable system where administrators can add LLM providers and models, and create/customize agents through a dedicated administration panel.

---

## Scope

### LLM Provider & Model Management

The administration panel gains a **Models** section with two subsections:

#### Providers

Administrators can configure one or more LLM providers. The following providers are supported out of the box:

| Provider | Notes |
|---|---|
| **Anthropic** | API key required; uses Anthropic Messages API |
| **OpenAI** | API key required; uses OpenAI Chat Completions API |
| **Ollama** | No API key; configurable base URL (defaults to localhost, can point to a remote server) |

Each provider record stores:
- Provider name and type
- API key (for Anthropic/OpenAI; stored encrypted, never exposed in the UI)
- Base URL (for Ollama; required, editable)
- Enabled/disabled status

#### Available Models

Once a provider is configured, the system loads the list of available models from that provider:
- Anthropic: fetched via the Anthropic models list API
- OpenAI: fetched via the OpenAI models list API
- Ollama: fetched via `GET /api/tags` on the configured base URL

Administrators can view, enable, or disable individual models. Only enabled models are selectable when configuring agents.

### Agent Abstraction

Each agent in the system is represented as a database entity with the following fields:

| Field | Type | Description |
|---|---|---|
| `agentId` | UUID | Unique identifier |
| `roleName` | string | Name of the role the agent performs (e.g., "Screener", "Extractor") |
| `roleDescription` | string | Description of the role |
| `personaName` | string | Agent's persona name (e.g., "Dr. Aria") |
| `personaDescription` | string | Narrative description of the persona |
| `personaImage` | SVG | An SVG image representing the agent's persona (can be AI-generated) |
| `systemMessageTemplate` | string | Templated system message using the agent's role, persona, and other fields |
| `modelId` | UUID (FK) | The specific model this agent uses |
| `modelProviderId` | UUID (FK) | The provider this agent's model comes from |

System message templates support variables for role name, role description, persona name, persona description, and any study-type-specific context. Agent creation is restricted to the task types defined as part of the supported research processes (Screener, Extractor, Librarian, Expert, QualityJudge, AgentGenerator, etc.).

### Agent Administration Panel

The administration panel gains an **Agents** section:

- **Agent List**: Displays all configured agents with their role, persona name, and assigned model.
- **Create Agent**: A wizard that walks the administrator through:
  1. Selecting a task type (restricted to the defined research process task types)
  2. Selecting a model provider and model
  3. Defining role name and description, persona name and description
  4. Optionally generating a persona SVG image via an AI image generation tool
  5. Reviewing and customizing the generated system message
- **Edit Agent**: All agent fields are editable. The system message template field is displayed in a syntax-highlighted editor.
- **Generate/Update System Message**: A button that invokes an Agent Generator Agent to produce an optimized system message based on the current role, persona, and model. The generated message replaces the current template, with the previous version preserved in an undo buffer.

### Prompt Template Updates

- All existing agent prompt templates are updated to be domain-specific to Software Engineering and Artificial Intelligence research.
- The domain field (SE/AI or other) becomes a configurable variable in the system message template, allowing the same agent type to be instantiated for different research domains.
- Study type context (SMS, SLR, Rapid Review, Tertiary) is injected as a variable into agent system messages so that a single agent definition can serve multiple study types with appropriate context.

---

## Integration Points

- The existing `ScreenerAgent` and `ExtractorAgent` referenced in `FR-006`/`FR-021`/`FR-031` of the SMS spec must be migrated to the new agent abstraction.
- The `Reviewer` entity in the study workflow references agents by their `agentId` rather than by hardcoded name strings.
- A database migration adds the `Provider`, `AvailableModel`, and `Agent` tables and adds a foreign key from `Reviewer.agent_id` to `Agent.agentId`.
- The `agent_config` override field in the `Reviewer` entity can still override model and threshold settings at the study level.

---

## Success Criteria

- An administrator can add an Anthropic, OpenAI, or Ollama provider and load the list of available models without modifying any configuration files.
- An administrator can create a new agent by selecting a task type, a model, and providing role/persona details, with an AI-generated system message.
- The "Generate/Update System Message" button produces a system message that incorporates the agent's role, persona, and model characteristics.
- All existing agent functionality (Screener, Extractor, Librarian, Expert, QualityJudge) continues to work after migration to the new agent abstraction.
- Agent system messages include domain (SE/AI) and study type as injectable variables.
