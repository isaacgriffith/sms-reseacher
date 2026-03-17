# Feature Specification: Models & Agents Management

**Feature Branch**: `005-models-and-agents`
**Created**: 2026-03-16
**Status**: Draft
**Input**: User description: "number 5 models-and-agents @docs/features/008-models-and-agents.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure an LLM Provider (Priority: P1)

An administrator needs to connect the system to an AI provider so that agents can call language models. They navigate to the administration panel, open the Models section, and add a new provider (Anthropic, OpenAI, or Ollama). After saving, the system immediately loads the list of available models from that provider, which the administrator can browse and enable or disable.

**Why this priority**: Without at least one configured provider and at least one enabled model, no agent can be created or run. All other stories depend on this foundation.

**Independent Test**: Can be fully tested by adding a provider, verifying the model list loads, and toggling model availability — delivers the ability to connect an external AI service without touching config files.

**Acceptance Scenarios**:

1. **Given** no providers are configured, **When** an administrator enters provider credentials (type, API key or base URL) and saves, **Then** the provider appears in the provider list with "Enabled" status and the system loads its model list automatically.
2. **Given** a provider is configured, **When** the administrator views the available models list, **Then** only models retrieved from that provider are shown, with each model having an enable/disable toggle.
3. **Given** a provider is configured with an invalid API key, **When** the system tries to load models, **Then** a descriptive error is shown and no partial model list is saved.
4. **Given** a configured provider, **When** the administrator disables it, **Then** its models are no longer selectable when creating or editing agents.
5. **Given** an Ollama provider with a non-default base URL, **When** saving the provider, **Then** model discovery uses the configured URL rather than localhost.

---

### User Story 2 - Create a New Agent (Priority: P2)

An administrator wants to define a new AI agent for a specific research task (e.g., Screener, Extractor). They open the Agents section, launch the creation wizard, pick a task type, select a provider and model, fill in the role and persona details, optionally generate a persona image, and review the auto-generated system message before saving.

**Why this priority**: Agents are the core value of this feature. Without the ability to create agents, no research workflow can use the new abstraction.

**Independent Test**: Can be fully tested end-to-end by completing the creation wizard for one task type, saving the agent, and verifying it appears in the agent list with the correct role, persona, and model assignment.

**Acceptance Scenarios**:

1. **Given** at least one provider with enabled models, **When** the administrator completes the creation wizard and saves, **Then** the new agent appears in the agent list with its role name, persona name, and assigned model displayed.
2. **Given** the creation wizard is open, **When** the administrator selects a task type, **Then** only task types from the defined research process roles (Screener, Extractor, Librarian, Expert, QualityJudge, AgentGenerator, etc.) are available for selection.
3. **Given** role and persona details are entered, **When** the administrator requests a system message, **Then** the system generates a message that incorporates the role name, role description, persona name, persona description, and model characteristics.
4. **Given** the generated system message is displayed, **When** the administrator edits it manually and saves, **Then** the customized message is stored as the agent's system message template.
5. **Given** the creation wizard, **When** the administrator requests a persona SVG image, **Then** a generated SVG is displayed and can be accepted or re-generated before saving.

---

### User Story 3 - Edit an Existing Agent (Priority: P3)

An administrator needs to update an agent's persona, system message, or assigned model without losing the previous configuration. They open the agent in the edit view, make changes, and save. They can also regenerate the system message, with the previous version preserved in an undo buffer.

**Why this priority**: Agents will evolve as research domains and study types change; editability and safe regeneration prevent data loss.

**Independent Test**: Can be tested by editing each field of an existing agent, saving, and verifying the updated values persist. The undo buffer can be verified by regenerating the system message and then restoring the previous version.

**Acceptance Scenarios**:

1. **Given** an existing agent, **When** the administrator updates any field (role description, persona, model) and saves, **Then** the agent record reflects the new values immediately.
2. **Given** an existing agent with a system message, **When** the administrator clicks "Generate/Update System Message", **Then** a new system message is produced, the previous message is stored in an undo buffer, and the administrator can restore the previous version with one action.
3. **Given** an agent's system message template is open in the editor, **When** the administrator views it, **Then** the editor provides syntax highlighting for template variable placeholders.
4. **Given** an agent is assigned a model from a now-disabled provider, **When** the administrator opens the edit view, **Then** a warning is shown that the current model is unavailable, and the administrator is prompted to select an alternative.

---

### User Story 4 - Migrate Existing Agents to New Abstraction (Priority: P4)

The system's existing hardcoded Screener and Extractor agents are migrated to the new agent abstraction automatically, so that research workflows continue to operate without manual re-configuration after the upgrade.

**Why this priority**: Continuity of existing functionality is required; the migration must be non-breaking.

**Independent Test**: Can be tested by running a study workflow after the upgrade and confirming the Screener and Extractor agents execute correctly using the new abstraction, with no changes required from the administrator.

**Acceptance Scenarios**:

1. **Given** a system with existing hardcoded Screener/Extractor agent configuration, **When** the database migration runs, **Then** Agent records are created for each existing agent and the study workflow references them by the new agent identifier.
2. **Given** the migration has run, **When** a study is screened or articles are extracted, **Then** results are identical in format and quality to pre-migration behavior.
3. **Given** the migrated agents, **When** the administrator views the agent list, **Then** Screener and Extractor appear with their original role names and prompt content preserved.

---

### User Story 5 - Use Domain & Study-Type Variables in System Messages (Priority: P5)

A researcher wants to reuse the same agent definition for different research domains (Software Engineering, Artificial Intelligence) and different study types (SMS, SLR, Rapid Review, Tertiary). System message templates include injectable variables so that one agent definition serves multiple contexts without duplication.

**Why this priority**: Reduces configuration overhead and allows a growing library of agent definitions to scale across research contexts.

**Independent Test**: Can be tested by creating one agent, assigning it to two studies with different domains and study types, and verifying that the system message rendered for each study includes the correct domain and study-type text.

**Acceptance Scenarios**:

1. **Given** a system message template with domain and study-type variables, **When** the agent runs in an SE/SMS study, **Then** the rendered system message contains "Software Engineering" and "Systematic Mapping Study" in the appropriate positions.
2. **Given** the same agent template, **When** the agent runs in an AI/SLR study, **Then** the rendered system message contains "Artificial Intelligence" and "Systematic Literature Review".
3. **Given** a template variable is missing from the stored message, **When** the system attempts to render it, **Then** an informative error is raised rather than silently producing a malformed message.

---

### Edge Cases

- What happens when a provider's API is unreachable during model list refresh? The previously loaded model list is retained and an error notice is shown; no models are removed.
- What happens when an administrator tries to delete a provider that has agents actively using its models? The system prevents deletion and lists the dependent agents.
- What happens when a model is removed from a provider's catalog (e.g., deprecated upstream) but is still assigned to an agent? The agent remains functional with the last-known model identifier, and a warning is shown in the agent list.
- What happens when two administrators submit conflicting edits to the same agent simultaneously? The second save detects a conflict and prompts the administrator to review the diff before overwriting.
- What happens when the Agent Generator agent is invoked to generate a system message but no Agent Generator agent is configured yet? The system shows a clear message explaining the dependency and links to agent creation.
- What happens when a system message template variable references an undefined variable name? Validation at save time flags the unknown variable rather than silently ignoring it.

## Requirements *(mandatory)*

### Functional Requirements

**Provider Management**

- **FR-001**: Administrators MUST be able to add an LLM provider of type Anthropic, OpenAI, or Ollama from the administration panel without modifying configuration files.
- **FR-002**: Each provider record MUST store: provider type, display name, API key (for Anthropic/OpenAI), base URL (for Ollama), and enabled/disabled status.
- **FR-003**: API keys MUST be stored encrypted at rest and MUST NOT be exposed in any UI view after initial entry.
- **FR-004**: Administrators MUST be able to enable or disable a provider; disabling a provider makes its models unavailable for agent assignment.
- **FR-005**: Administrators MUST be able to update the base URL for an Ollama provider after initial creation.

**Model Management**

- **FR-006**: When a provider is saved or refreshed, the system MUST automatically fetch the list of available models from that provider's catalog.
- **FR-007**: Administrators MUST be able to enable or disable individual models; only enabled models are selectable when creating or editing agents.
- **FR-008**: The model list for a provider MUST be refreshable on demand without recreating the provider record.

**Agent Management**

- **FR-009**: Administrators MUST be able to create an agent via a multi-step wizard that captures: task type, provider and model selection, role name, role description, persona name, persona description, and system message template.
- **FR-010**: The task type selector MUST be restricted to the defined research process roles: Screener, Extractor, Librarian, Expert, QualityJudge, AgentGenerator, and any other roles defined in the research workflow.
- **FR-011**: Each agent MUST be associated with exactly one enabled model from one configured provider.
- **FR-012**: The administration panel MUST display a list of all configured agents showing role name, persona name, and assigned model.
- **FR-013**: All agent fields MUST be editable after creation.
- **FR-014**: The system message template field MUST be displayed in a syntax-highlighted editor that highlights template variable placeholders.
- **FR-015**: Administrators MUST be able to trigger AI-assisted generation of a system message; the previously saved message MUST be preserved in an undo buffer and restorable with a single action.
- **FR-016**: Administrators MUST be able to optionally generate a persona SVG image via an AI generation tool during agent creation or editing.

**System Message Templates**

- **FR-017**: System message templates MUST support injectable variables for: role name, role description, persona name, persona description, research domain (e.g., SE/AI), and study type (SMS, SLR, Rapid Review, Tertiary).
- **FR-018**: The system MUST validate that all variable placeholders in a saved template correspond to known variable names and warn on unknown variables.

**Migration & Compatibility**

- **FR-019**: A database migration MUST create Provider, AvailableModel, and Agent tables and add a foreign key from the Reviewer entity to Agent.
- **FR-020**: Existing Screener and Extractor agent configurations MUST be migrated automatically to Agent records during the database migration without manual administrator action.
- **FR-021**: All existing research workflow capabilities (screening, extraction, library management, expert review, quality judging) MUST continue to function correctly after migration.

### Key Entities

- **Provider**: Represents a configured LLM service (Anthropic, OpenAI, or Ollama). Stores type, display name, encrypted credentials or base URL, and enabled status. One provider may supply many models.
- **AvailableModel**: An individual model offered by a provider, fetched from that provider's catalog. Stores provider reference, model identifier, display name, and enabled status. Used by agents for inference.
- **Agent**: A configured AI participant in the research workflow. Stores a unique identifier, role name and description, persona name and description, persona SVG image, system message template, and references to its assigned provider and model.
- **Reviewer** (existing, extended): The study-level participant entity that now references an Agent by identifier instead of a hardcoded name string. May carry per-study model and threshold overrides.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An administrator can add a new provider (Anthropic, OpenAI, or Ollama) and view the loaded model list in under 2 minutes, without editing any configuration file.
- **SC-002**: An administrator can create a fully configured agent — from opening the wizard to saving — in under 5 minutes, including AI-generated system message review.
- **SC-003**: All existing research workflow tasks (Screener, Extractor, Librarian, Expert, QualityJudge) produce results equivalent in format and accuracy to pre-migration behavior on the same input dataset after migration.
- **SC-004**: 100% of prior hardcoded agent configurations are automatically migrated to Agent records with no manual administrator intervention required.
- **SC-005**: A single agent definition can be reused across at least two different research domains and two different study types by changing only injected variable values, with no duplicate agent records required.
- **SC-006**: The "Generate/Update System Message" action completes and the previous message is preserved in the undo buffer in 100% of invocations; the administrator can restore the previous message with one additional action.
- **SC-007**: Disabling a provider or model is immediately reflected in the agent creation wizard without requiring a page reload; no agent can be saved referencing a disabled model.

## Assumptions

- The research process task types (Screener, Extractor, Librarian, Expert, QualityJudge, AgentGenerator) are treated as an enumerated list defined in the codebase; new task types require a code change, not a UI configuration.
- API key encryption uses the same encryption mechanism already in place for other secrets in the system (Fernet symmetric encryption).
- The "Agent Generator Agent" used to produce system messages is itself an Agent record in the system; bootstrapping is handled by providing a default seed agent configuration.
- Persona SVG generation is treated as optional and a best-effort feature; agents without an SVG image are fully functional.
- The Ollama base URL defaults to `http://localhost:11434` when not specified.
- Model list fetching is a synchronous operation from the administrator's perspective; very large catalogs may take a few seconds but no background job is required.
- Study-level overrides in the Reviewer entity (model, threshold) continue to take precedence over agent-level defaults.
