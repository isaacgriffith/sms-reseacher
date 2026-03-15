# Feature: Research Protocol Definition

**Feature ID**: 009-research-protocol-definition
**Depends On**: 002-sms-workflow, 003-slr-workflow, 004-rapid-review-workflow
**Reference**: `docs/todo.md` (Research Protocol Definition section)

---

## Overview

Replace the currently rigid, fixed-path study workflow with a flexible, graph-based research protocol description system. Researchers and administrators can define, visualize, and edit the workflow (protocol) of any study type as a directed graph of tasks, enabling customization of the research process beyond the default linear paths.

---

## Scope

### Protocol Graph Model

A research protocol is represented as a directed acyclic graph (DAG) where:

#### Nodes (Tasks)

Each node represents a task in the research process. Nodes have:

| Property | Description |
|---|---|
| `taskId` | Unique identifier |
| `taskType` | The task category — must be one of the defined task types for the supported study types (e.g., `DefinePICO`, `BuildSearchString`, `ExecuteSearch`, `ScreenPapers`, `ExtractData`, `SynthesizeData`, `GenerateReport`, etc.) |
| `label` | Human-readable name |
| `description` | Description of what this task accomplishes |
| `inputs` | Named inputs flowing into the task (typed: e.g., `CandidatePaperList`, `SearchString`, `PICOComponents`) |
| `outputs` | Named outputs produced by the task |
| `assignees` | One or more Human Agents (study members) and/or AI Agents assigned to complete the task |
| `qualityGates` | Zero or more quality gate conditions that must be satisfied for the task to be considered complete (e.g., "Kappa ≥ 0.6", "Coverage recall ≥ 80%", "At least 5 accepted papers") |
| `isRequired` | Whether this task is mandatory or optional |

#### Edges (Information Flow)

Each edge represents the flow of information from one task's output to another task's input:

| Property | Description |
| --- | --- |
| `edgeId` | Unique identifier |
| `sourceNodeId` | The task producing the data |
| `sourceOutput` | The named output from the source task |
| `targetNodeId` | The task consuming the data |
| `targetInput` | The named input on the target task |
| `condition` | Optional: a boolean expression on the source task's outputs that must be true for data to flow (enables conditional branching) |

### Protocol Editing

Protocols can be defined and edited through two complementary interfaces:

#### Visual Editor

- A graph visualization (using the existing D3.js dependency) renders the protocol as a node-link diagram.
- Researchers can drag-and-drop tasks, draw edges between them, and configure node and edge properties through inline panels.
- The visual editor reflects the same underlying graph model as the textual editor; changes in one are immediately reflected in the other.

#### Textual Editor

- Protocols can be defined in a structured text format (YAML or a simple DSL).
- The textual editor is syntax-highlighted and provides inline validation, flagging unknown task types, missing required inputs/outputs, and cycles.
- The textual representation can be exported and imported, enabling version control of protocol definitions.

### Default Protocols

- Default protocol graphs are provided for each study type (SMS, SLR, Rapid Review, Tertiary Study), representing the standard processes defined in the research documentation.
- These defaults are read-only templates; a researcher creates a copy to customize.
- A study's protocol can be reset to the default at any time (with a confirmation prompt noting that custom configurations will be lost).

### Quality Gates

Quality gates are conditions attached to task nodes that gate progression. The system evaluates quality gates automatically where possible (for measurable metrics) and flags them for human confirmation where evaluation requires judgement.

Examples of supported quality gate types:
- **Metric threshold**: "Kappa coefficient ≥ 0.6", "Test set recall ≥ 80%", "Accepted papers ≥ N"
- **Completion check**: "All candidate papers have been reviewed", "Protocol document is complete"
- **Human sign-off**: "Study admin has approved this phase"

When a quality gate fails, the system surfaces the failure with the current metric value, the threshold, and a recommendation for remediation.

### Runtime Execution

- At study runtime, the system executes the study's assigned protocol graph, activating tasks in topological order.
- Tasks are blocked until all incoming edges carry data (i.e., predecessor tasks are complete and quality gates passed).
- Conditional edges allow branching (e.g., "if snowball round adds ≥ threshold papers, continue snowball; else proceed to extraction").
- The current execution state (which tasks are complete, in-progress, blocked, or skipped) is visible to all study members.

---

## Integration Points

- Replaces the hardcoded `phase_gate` service in `FR-008a` of the SMS spec with a general-purpose protocol executor.
- Each study is associated with one `ResearchProtocol` (a named graph definition). Multiple studies can share the same protocol template.
- Phase gates defined in `FR-008a` (pico_saved_at, search_run_at, extraction_started_at) become quality gate conditions on the respective task nodes in the default SMS protocol.
- Adds entities: `ResearchProtocol`, `ProtocolNode`, `ProtocolEdge`, `QualityGate`, `ProtocolExecutionState`.

---

## Constraints

- Task types in protocol nodes are strictly constrained to the defined set for the supported study types. Researchers cannot introduce arbitrary task types.
- Protocol graphs must be acyclic (DAGs). The editor enforces this constraint and rejects cycles with an explanatory error.
- A protocol with unsatisfied required inputs (dangling edges) cannot be saved or assigned to a study.

---

## Success Criteria

- A researcher can view the default SMS protocol as a visual graph and navigate to any task node to see its inputs, outputs, assignees, and quality gates.
- A researcher can create a custom protocol by copying a default, modifying it in either the visual or textual editor, and assigning it to a new study.
- A custom protocol runs correctly at study execution time, respecting topological order, quality gates, and conditional edges.
- The textual protocol format can be exported to a file, checked into version control, re-imported, and produce an identical graph.
- A quality gate failure surfaces the measured metric value, the threshold, and a remediation recommendation to the researcher.
