# Feature Specification: Research Protocol Definition

**Feature Branch**: `010-research-protocol-definition`
**Created**: 2026-03-30
**Status**: Draft
**Input**: User description: "number 10 research-protocol-definition using @docs/features/009-research-protocol-definition.md"

## Clarifications

### Session 2026-03-30

- Q: Who can create, edit, and assign custom protocols? → A: Only the study creator/administrator; all other study members can view protocols but cannot modify or assign them.
- Q: What is the scope of a custom protocol library? → A: Per-researcher; a custom protocol is visible only to the researcher who created it and can be assigned to any study they administer, but is not accessible to other researchers.
- Q: How are concurrent edits to the same custom protocol handled? → A: Optimistic locking; a save is rejected if the protocol was modified by another session since it was loaded, and the user must reload and re-apply their changes.
- Q: Does the platform maintain a version history of custom protocols? → A: No in-platform version history; the version field is an internal optimistic-lock counter only. Export/import is the sole mechanism for rollback and external version control.
- Q: How do researchers author conditional edge expressions? → A: Point-and-click condition builder only; researcher selects an output name, a comparison operator, and a value from constrained UI controls. No free-form text expression entry.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Default Protocol Graph (Priority: P1)

A researcher opens their study and navigates to the protocol view. They see the default protocol for their study type (SMS, SLR, Rapid Review, or Tertiary Study) rendered as a visual graph showing all tasks and their connections. They can click any task node to see its inputs, outputs, assigned roles, and quality gate conditions.

**Why this priority**: This is the foundational capability — researchers must be able to understand what the current workflow looks like before they can customize it. It also delivers standalone value by making the research process transparent and inspectable.

**Independent Test**: A researcher with an SMS study can open the protocol view, see the default SMS graph with all tasks rendered as nodes and edges, and click any task node to view its configured properties in a detail panel.

**Acceptance Scenarios**:

1. **Given** a researcher has an SMS study, **When** they navigate to the protocol view, **Then** they see the default SMS protocol rendered as a directed graph with task nodes and connecting edges labeled with data flows.
2. **Given** the protocol graph is displayed, **When** the researcher clicks a task node (e.g., "Screen Papers"), **Then** a detail panel shows the task's inputs, outputs, assigned roles, and all quality gate conditions.
3. **Given** four different study types exist (SMS, SLR, Rapid Review, Tertiary Study), **When** a researcher views the protocol for any of them, **Then** the correct default protocol is shown for that study type.

---

### User Story 2 - Create and Edit a Custom Protocol (Priority: P2)

A researcher copies a default protocol template and customizes it — rearranging tasks, adjusting connections, modifying assignees, and configuring quality gates — using either a visual drag-and-drop editor or a structured text editor. Both editors stay in sync in real time.

**Why this priority**: Custom protocols are the core value proposition of this feature. Without the ability to create and edit protocols, the system remains inflexible and no more useful than the current hardcoded workflow.

**Independent Test**: A researcher copies the default SMS protocol, renames it, removes an optional task, adds a quality gate threshold on another task, saves the protocol, reopens it, and sees all changes intact exactly as configured.

**Acceptance Scenarios**:

1. **Given** a researcher views a default protocol, **When** they choose "Copy to Custom Protocol," **Then** a new editable copy is created and the researcher is taken to the editor.
2. **Given** the researcher is in the visual editor, **When** they drag a task node to a new position and draw an edge between two tasks, **Then** the graph updates immediately and the textual editor reflects the same change.
3. **Given** the researcher is in the textual editor, **When** they modify a task's quality gate condition, **Then** the visual editor immediately reflects the updated node configuration.
4. **Given** a researcher attempts to draw an edge that would create a cycle, **When** they confirm the action, **Then** the system rejects it with a clear explanation that protocol graphs must be acyclic.
5. **Given** a custom protocol has a required task with no incoming data (dangling input), **When** the researcher attempts to save, **Then** the system rejects the save and identifies which task has unsatisfied required inputs.

---

### User Story 3 - Assign Protocol to a Study and Execute It (Priority: P2)

A researcher assigns a custom (or default) protocol to a new study. At runtime, the system executes the protocol in topological order, activating tasks as their predecessors complete and quality gates pass. All study members can see which tasks are complete, in-progress, blocked, or skipped.

**Why this priority**: Without runtime execution the protocol definition is a static document with no practical effect. This story closes the loop between protocol definition and actual study conduct.

**Independent Test**: A researcher creates a study, assigns a custom protocol to it, and as tasks are completed the system automatically activates the next eligible tasks while displaying the current execution state to all study members.

**Acceptance Scenarios**:

1. **Given** a new study is created, **When** the researcher selects a protocol (default or custom) to assign, **Then** the study's workflow follows the assigned protocol rather than any hardcoded default.
2. **Given** a study is running under its protocol, **When** a task's predecessor completes and all quality gates pass, **Then** the blocked downstream task automatically becomes active and is surfaced to its assigned members.
3. **Given** a conditional edge exists (e.g., "if snowball round adds sufficient new papers, continue snowballing"), **When** the condition evaluates to false, **Then** the conditional branch is skipped and the alternative downstream path activates.
4. **Given** all study members view the study, **When** any task status changes, **Then** all members see the updated execution state (complete, in-progress, blocked, or skipped) without needing to manually refresh.

---

### User Story 4 - Quality Gate Failure Remediation (Priority: P3)

When a task's quality gate fails (e.g., inter-rater agreement is below threshold, too few papers accepted), the system shows the researcher the current metric value, the required threshold, and a specific recommendation for how to remediate the failure before the study can proceed.

**Why this priority**: Quality gates without actionable failure messages leave researchers stuck with no guidance. This story ensures gates function as active guidance, not just barriers.

**Independent Test**: A researcher completes a screening task with inter-rater agreement below the configured threshold; the system shows them the exact agreement score, the required threshold, and a recommendation such as "conduct a reconciliation round."

**Acceptance Scenarios**:

1. **Given** a task has a metric-threshold quality gate (e.g., "Kappa ≥ 0.6"), **When** the task is completed with a metric below threshold, **Then** the system surfaces a failure notice showing the measured value, the threshold, and a remediation recommendation.
2. **Given** a task has a human sign-off gate, **When** the task is otherwise complete, **Then** the system prompts the designated approver (e.g., study administrator) to explicitly approve before downstream tasks activate.
3. **Given** a quality gate fails, **When** the researcher takes the recommended remediation action and re-evaluates, **Then** if the gate now passes the downstream tasks activate normally.

---

### User Story 5 - Export, Version Control, and Re-import Protocol (Priority: P4)

A researcher exports a custom protocol to a structured text file, commits it to version control, and later re-imports it to produce an identical protocol graph with all tasks, edges, quality gates, and configurations preserved.

**Why this priority**: Exportability enables reproducibility — a cornerstone of systematic research. It also allows teams to share and audit protocol changes over time.

**Independent Test**: A researcher exports a protocol, the resulting file is re-imported into the platform, and the resulting graph is identical to the original (same tasks, edges, quality gates, assignee types, and conditions).

**Acceptance Scenarios**:

1. **Given** a researcher has a saved custom protocol, **When** they choose "Export Protocol," **Then** a structured text file is downloaded that fully describes the protocol (all nodes, edges, quality gates, and conditions).
2. **Given** a previously exported protocol file, **When** a researcher imports it, **Then** the system produces a protocol graph identical to the original, with all configurations preserved.
3. **Given** the imported protocol file contains an unknown task type or a cycle, **When** the import is processed, **Then** the system rejects it with a specific validation error identifying the problem.

---

### User Story 6 - Reset Protocol to Default (Priority: P4)

A researcher who has customized a study's protocol can reset it to the standard default for that study type, with a clear warning that their custom configuration will be lost.

**Why this priority**: Recovery and simplicity matter — researchers who over-customize or make errors need a reliable fallback path back to the standard workflow.

**Independent Test**: A researcher with a heavily modified custom protocol chooses "Reset to Default," confirms the warning prompt, and the protocol reverts to the unmodified default for their study type.

**Acceptance Scenarios**:

1. **Given** a study with a custom protocol, **When** the researcher chooses "Reset to Default," **Then** the system shows a confirmation prompt explaining that all custom configuration will be lost.
2. **Given** the researcher confirms the reset, **Then** the protocol is replaced with the read-only default template for that study type and the researcher is returned to the protocol view.
3. **Given** the researcher cancels the reset prompt, **Then** their custom protocol is unchanged.

---

### Edge Cases

- What happens when a researcher tries to delete a required task from the protocol? The system should prevent deletion and explain that the task is marked as required.
- What happens when a protocol graph has no start node (all tasks have incoming edges)? The system should reject the save with a validation error explaining that at least one task must have no predecessors.
- What happens when two tasks produce outputs with the same name flowing into the same target input? The system should flag this as an ambiguous connection at save time.
- What if a quality gate references a metric not produced by that task's outputs? Validation should catch this at protocol save time with a specific error.
- What if a study is mid-execution when the researcher attempts to reset or reassign its protocol? The system should prevent the action and explain that protocol changes are not allowed while a study is actively running.
- What if a default protocol template is updated by the platform? Existing studies using that template as their protocol should be unaffected; only newly created copies use the updated template.
- What if two sessions attempt to save a custom protocol simultaneously? The second save is rejected with a conflict error; the user must reload the latest version and re-apply their changes (optimistic locking).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST represent each research protocol as a directed acyclic graph (DAG) of task nodes and information-flow edges.
- **FR-002**: Each task node MUST carry: a unique identifier, a task type constrained to the defined set for the study type, a human-readable label, a description, named typed inputs, named typed outputs, one or more assignees (human roles or AI agents), zero or more quality gate conditions, and a required/optional flag.
- **FR-003**: Each edge MUST record: source task identifier, source output name, target task identifier, target input name, and an optional condition that gates data flow. Conditions MUST be authored via a point-and-click builder (select output name → comparison operator → value); free-form text expression entry is not supported.
- **FR-004**: The system MUST provide a visual graph editor where researchers can add, remove, and reposition task nodes, draw edges between them, and configure node and edge properties via inline panels.
- **FR-005**: The system MUST provide a structured text editor for defining protocols, with inline validation that flags unknown task types, missing required inputs/outputs, and cycles.
- **FR-006**: Changes made in the visual editor and textual editor MUST be reflected in the other immediately without requiring a separate sync action.
- **FR-007**: The system MUST supply read-only default protocol templates for each supported study type (SMS, SLR, Rapid Review, Tertiary Study).
- **FR-008**: The study administrator (study creator) MUST be able to create an editable custom protocol by copying any default template; other study members have read-only access to the protocol.
- **FR-008a**: Only the study administrator MUST be permitted to assign or reassign a protocol to a study; other study members cannot change the assigned protocol.
- **FR-009**: The system MUST prevent saving any protocol that contains a directed cycle, reporting the offending cycle to the researcher.
- **FR-009a**: The system MUST use optimistic locking on custom protocol saves; if the protocol was modified by another session since it was loaded, the save MUST be rejected with a conflict error instructing the user to reload and re-apply their changes.
- **FR-010**: The system MUST prevent saving any protocol where a required task has unsatisfied (dangling) input connections, identifying the specific task and input.
- **FR-011**: Task types in protocol nodes MUST be strictly constrained to the defined set for each supported study type; researchers cannot introduce arbitrary task types.
- **FR-012**: The study administrator MUST be able to assign any of their own saved custom protocols, or any default template, to a new study at study creation time. Custom protocols created by other researchers are not visible or assignable.
- **FR-013**: At study runtime, the system MUST execute tasks in topological order, activating each task only when all predecessor tasks are complete and their quality gates have passed.
- **FR-014**: Conditional edges MUST be evaluated at runtime; when a condition evaluates to false the data does not flow and the target task is skipped or an alternative path activates.
- **FR-015**: The current execution state of all tasks (pending, active, complete, blocked, skipped) MUST be visible to all study members in near real time.
- **FR-016**: When a metric-threshold quality gate fails, the system MUST surface the measured value, the required threshold, and a remediation recommendation to the researcher in the same view.
- **FR-017**: Human sign-off quality gates MUST require explicit approval by the designated role before downstream tasks activate.
- **FR-018**: Researchers MUST be able to export a protocol to a structured text file suitable for storage in version control.
- **FR-019**: Researchers MUST be able to import a previously exported protocol file; the system MUST validate it before applying and reject invalid files with specific error messages.
- **FR-020**: Researchers MUST be able to reset a study's protocol to the default for that study type, preceded by a confirmation prompt warning that all custom configuration will be lost.
- **FR-021**: The system MUST prevent protocol reassignment or reset while a study is actively executing.
- **FR-022**: The existing SMS phase-gate conditions (PICO saved, search run, extraction started) MUST be preserved as quality gate conditions on the corresponding task nodes in the default SMS protocol, with no change in behavior for existing studies.

### Key Entities

- **Research Protocol**: A named directed acyclic graph of tasks with an internal version counter (used for optimistic locking only — no user-visible version history). Exists as a read-only default template (platform-wide) or as an editable custom protocol owned by a specific researcher. A researcher's custom protocols are visible only to them and can be assigned to any study they administer; multiple of their studies may share the same custom protocol.
- **Protocol Node (Task)**: A vertex in the protocol graph representing a single research task, with typed inputs/outputs, assignees, quality gates, and a required/optional flag.
- **Protocol Edge**: A directed connection from one task's named output to another task's named input, optionally gated by a boolean condition expression enabling conditional branching.
- **Quality Gate**: A condition attached to a task node that must be satisfied before downstream tasks activate. Supported types: metric threshold (e.g., "Kappa ≥ 0.6"), completion check (e.g., "all papers reviewed"), and human sign-off.
- **Protocol Execution State**: The runtime record of a study's progress through its assigned protocol, tracking each task's status (pending, active, complete, skipped, gate-failed).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A researcher can view the full default protocol for any supported study type and inspect any task's complete properties within 2 interactions from the study dashboard.
- **SC-002**: A researcher can create a fully functional custom protocol (copy, modify, validate, save, assign) without leaving the platform or writing any code.
- **SC-003**: A custom protocol exported to a file and re-imported produces a graph identical to the original in 100% of cases, with all nodes, edges, conditions, and quality gates preserved exactly.
- **SC-004**: When a quality gate fails, researchers see the specific measured value, the threshold, and a remediation recommendation within the same view — no additional navigation required.
- **SC-005**: All study members see task status updates within 5 seconds of a status change during active study execution.
- **SC-006**: Protocol validation (cycle detection, dangling inputs, unknown task types) completes and surfaces specific, actionable errors before a researcher can save an invalid protocol.
- **SC-007**: 100% of existing SMS phase-gate behaviors (PICO saved, search run, extraction started) are preserved after migration to the quality gate system, verified by running existing SMS workflow test suites without modification.

## Assumptions

- Task type vocabularies (the constrained set of valid task types for each study type) are fully defined by the existing workflow implementations and require no new definition as part of this feature.
- Near real time execution state visibility is defined as updates appearing to all study members within 5 seconds; the necessary push-notification infrastructure is assumed to exist or be available.
- Conditional edge conditions are authored via a point-and-click builder (output name + comparison operator + value); free-form text expression entry is explicitly out of scope. The available output names and operators are constrained to what the system can validate and serialize.
- The protocol export format will be YAML; the exact schema will be defined during the planning phase.
- Existing studies with hardcoded phase gates will be migrated automatically to the default protocol equivalent during the database migration; no manual researcher action is required for migration.
- Custom protocols are scoped to their creator; a researcher's custom protocols are not visible to other researchers. Multiple studies administered by the same researcher may share the same custom protocol, but each study maintains its own independent execution state record.
- Default protocol templates are managed by platform administrators, not by researchers; researchers can only read and copy them.
- Only the study administrator (study creator) can create, edit, save, and assign custom protocols. All other study members have read-only access to view the protocol graph and execution state.
