# Feature Roadmap

This directory contains high-level feature documents (PRDs) for all planned work extending the existing SMS Workflow (`002-sms-workflow`). Each document is designed to be fed into `speckit` to drive spec-driven implementation.

## Feature Index

| ID | Feature | Status | Depends On |
|---|---|---|---|
| [003](./003-slr-workflow.md) | Systematic Literature Review (SLR) Workflow | Planned | 002 |
| [004](./004-rapid-review-workflow.md) | Rapid Review Workflow | Planned | 002 |
| [005](./005-tertiary-studies-workflow.md) | Tertiary Studies Workflow | Planned | 002, 003 |
| [006](./006-project-setup-improvements.md) | Project Setup & Quality Improvements | Planned | 001, 002 |
| [007](./007-frontend-improvements.md) | Frontend Improvements (MUI, 2FA, Swagger) | Planned | 001, 002 |
| [008](./008-models-and-agents.md) | Models & Agents Management | Planned | 001, 002 |
| [009](./009-research-protocol-definition.md) | Research Protocol Definition | Planned | 002, 003, 004 |
| [010](./010-database-search-and-retrieval.md) | Database Search, Retrieval & Paper Processing | Planned | 001, 002, 008 |

## Recommended Implementation Order

1. **006** (Project Setup) — foundational; improves test coverage and tooling before adding features
2. **007** (Frontend) — parallel-safe with 008 and 010; improves UX foundation
3. **008** (Models & Agents) — parallel-safe with 007; extends the agent system before adding study types
4. **010** (Database Search & Retrieval) — should be implemented alongside or immediately after 008; provides the real data acquisition layer that all study workflows depend on
5. **003** (SLR Workflow) — extends 002; most closely related to existing work
6. **004** (Rapid Review) — extends 002; simpler than SLR
7. **005** (Tertiary Studies) — extends 003; depends on SLR being implemented
8. **009** (Research Protocol Definition) — architectural upgrade; best done after all study types are implemented so the default protocols can be validated end-to-end

## Using with speckit

Each feature document in this directory can be provided directly to `speckit.specify` to generate a full feature spec:

```
/speckit.specify docs/features/003-slr-workflow.md
```

After specification, use the standard speckit workflow:
1. `/speckit.clarify` — identify and resolve underspecified areas
2. `/speckit.plan` — generate the implementation plan
3. `/speckit.tasks` — generate the task list
4. `/speckit.implement` — execute the implementation
