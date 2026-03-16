# Feature Specification: Project Setup & Quality Improvements

**Feature Branch**: `003-project-setup-improvements`
**Created**: 2026-03-15
**Status**: Draft
**Input**: User description: "003 @/docs/features/006-project-setup-improvements.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First-Time Contributor Onboarding (Priority: P1)

A new contributor (human or AI agent) clones the repository and needs to verify the codebase is healthy before making changes. They open `CLAUDE.md`, follow the instructions step-by-step, and are able to run all test suites, linters, and mutation tests without consulting external resources or asking questions.

**Why this priority**: This is the foundation of contributor confidence. If a contributor cannot reliably run the quality suite on a clean checkout, all other quality improvements lose their value — no one can verify their changes are correct.

**Independent Test**: Can be fully tested by cloning the repository into a fresh directory, following only the `CLAUDE.md` instructions, and confirming every command succeeds.

**Acceptance Scenarios**:

1. **Given** a freshly cloned repository with no prior setup, **When** a contributor follows the environment setup section of `CLAUDE.md`, **Then** all prerequisites are installed and ready without errors.
2. **Given** a prepared environment, **When** a contributor runs the test suite commands from `CLAUDE.md` for each service (backend, agents, db, researcher-mcp, and frontend), **Then** all unit, integration, and e2e tests pass and a coverage report is produced.
3. **Given** a prepared environment, **When** a contributor runs the linter commands from `CLAUDE.md`, **Then** no configuration errors occur and results are displayed.
4. **Given** a prepared environment, **When** a contributor runs the mutation test command from `CLAUDE.md`, **Then** the mutation suite completes without errors and a kill-rate report is shown.

---

### User Story 2 - Confident Code Change Verification (Priority: P2)

A developer makes a change to a Python service and wants to confirm they have not broken any existing behaviour or introduced untested code paths. They run the test suite and coverage report, see all tests pass and coverage remains at or above the threshold, then submit their change.

**Why this priority**: Reliable test coverage gives developers and reviewers confidence that changes are safe. Without a passing, high-coverage test suite, the project's quality guarantees are meaningless.

**Independent Test**: Can be fully tested by introducing a deliberate regression in a Python service, running the test suite, and confirming the failure is detected; then confirming coverage drops below 85% when a function is left untested.

**Acceptance Scenarios**:

1. **Given** a passing test suite, **When** a developer introduces a bug into any Python service, **Then** at least one test fails and identifies the affected area.
2. **Given** the full test suite runs, **When** coverage is measured across all Python services, **Then** line coverage is at or above 85% for each service.
3. **Given** a test has been failing without justification, **When** the remediation work is complete, **Then** the test passes or has a documented justification for its disabled state.

---

### User Story 3 - Mutation Testing Confidence (Priority: P3)

A developer wants to know whether the test suite actually detects meaningful logic errors, not just exercises code paths. They run the mutation testing suite and see that at least 85% of injected faults are caught by the existing tests.

**Why this priority**: High line coverage alone can be misleading. Mutation testing validates that tests assert meaningful behaviour. This story builds on P2 — coverage must be achieved before mutation quality is meaningful.

**Independent Test**: Can be fully tested by running the mutation suite against a Python service and verifying the kill rate report shows 85% or higher.

**Acceptance Scenarios**:

1. **Given** the mutation testing tool is configured, **When** a developer runs the mutation suite, **Then** the tool executes without errors and produces a kill-rate report.
2. **Given** the mutation suite report, **When** the kill rate is reviewed, **Then** at least 85% of generated mutants are killed across all Python services.
3. **Given** a mutant survives (is not killed), **When** a developer inspects it, **Then** either a new test is added to kill it or it is documented as an acceptable survivor with justification.

---

### User Story 4 - Feature Completion Documentation (Priority: P4)

A developer completes all quality improvements and is ready to merge the feature branch. Before opening the pull request, they update the root `README.md` and `CHANGELOG.md` and the `README.md` and `CHANGELOG.md` for every subproject they touched, so that all documentation accurately reflects the new tools, commands, and quality thresholds introduced by this work.

**Why this priority**: Per Constitution Principle X, documentation updates are a mandatory merge gate. Undocumented changes leave contributors unable to discover or use the improvements made by this feature.

**Independent Test**: Can be fully tested by reviewing the root and subproject `README.md` and `CHANGELOG.md` files after the feature is complete and confirming all new tooling, commands, and quality standards are accurately described.

**Acceptance Scenarios**:

1. **Given** the feature is complete, **When** the root `README.md` is reviewed, **Then** it accurately describes the project's current tooling, test commands, and quality standards.
2. **Given** the feature is complete, **When** each modified subproject's `README.md` is reviewed, **Then** it reflects the changes made to that subproject.
3. **Given** the feature is complete, **When** the root and subproject `CHANGELOG.md` files are reviewed, **Then** each contains a new entry describing what was added, changed, or fixed by this feature.

---

### Edge Cases

- What happens when a service has zero existing tests? The coverage tool must still run and report 0%, making the gap visible.
- What if a test failure is caused by a missing external service (e.g., database, message broker) rather than a code defect? The environment setup instructions must document and provision all required dependencies.
- What if `cosmic-ray` cannot be made to run against a specific Python service (e.g., version incompatibility, async test framework conflict)? A documented workaround or per-service exclusion must be justified and tracked.
- What if a test is legitimately skipped (e.g., requires hardware unavailable in CI)? The skip must have a code comment or issue reference explaining why, and must not inflate the pass rate.
- What if e2e tests require a running database or external service that is unavailable in CI? The GitHub Actions workflow must provision all required services (e.g., via `services:` containers) before running e2e tests.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `CLAUDE.md` MUST contain accurate, runnable commands for executing all test suites (unit, integration) for each Python service (backend, agents, db, researcher-mcp) and the frontend (TypeScript/Node), plus the Playwright e2e suite (`npx playwright test`).
- **FR-002**: `CLAUDE.md` MUST contain accurate, runnable commands for executing all linters and static analysis tools across the project (`ruff` for linting/formatting and `mypy` for type checking on Python; `eslint` and `prettier` on TypeScript/frontend).
- **FR-003**: `CLAUDE.md` MUST contain accurate, runnable commands for executing the mutation test suite.
- **FR-004**: `CLAUDE.md` MUST document all environment setup steps required before any test or linter command can run successfully on a clean checkout, covering both Python services (correct Python version, `uv`) and the frontend (Node 20 LTS, `npm install`).
- **FR-005**: All instructions in `CLAUDE.md` MUST be verified to work on a clean checkout without modification.
- **FR-006**: If `constitution.md` exists in the repository, it MUST be updated with the same operational guidance as `CLAUDE.md`.
- **FR-007**: All existing tests MUST pass. Tests MUST NOT be skipped or marked as expected failures unless accompanied by a documented justification referencing a specific issue or code comment. A `pytest` build gate MUST enforce this: any `@pytest.mark.skip` or `@pytest.mark.xfail` without a `reason=` parameter MUST cause the test run to fail.
- **FR-008**: New tests MUST be added as needed so that line coverage is at or above 85% for each Python service (backend, agents, db, researcher-mcp) and for the frontend (TypeScript).
- **FR-009**: Coverage measurement MUST be integrated into the GitHub Actions CI pipeline for all services: the build MUST fail if line coverage drops below 85% for any Python service (`pytest-cov`) or the frontend (`vitest run --coverage`), and a coverage summary MUST be posted as a PR comment.
- **FR-010**: `cosmic-ray` MUST be configured as the Python mutation testing tool for the project's Python version and test framework. `mutmut` (previously referenced) is superseded by `cosmic-ray`.
- **FR-013**: Both the `cosmic-ray` (Python) and `stryker` (TypeScript) mutation suites MUST each be exposed as a **manually-triggered** GitHub Actions workflow (`workflow_dispatch`). Neither MUST run automatically on every PR. Both MUST also be triggered automatically at the completion of every speckit feature implementation.
- **FR-011**: The test suite MUST kill at least 85% of mutants generated by the mutation testing tool across all Python services (`cosmic-ray`) and the frontend (`stryker`).
- **FR-012**: `cosmic-ray` and its run command MUST be documented in `CLAUDE.md`.
- **FR-014**: The root `README.md` MUST be updated to reflect any user-facing changes to the project's capabilities, tooling, or usage introduced by this feature.
- **FR-015**: The `README.md` for each subproject whose source code is modified (backend, agents, db, researcher-mcp, frontend) MUST be updated to reflect those changes.
- **FR-016**: The root `CHANGELOG.md` MUST receive a new entry recording what was added, changed, fixed, or removed by this feature.
- **FR-017**: The `CHANGELOG.md` for each subproject whose source code is modified MUST be updated with the same level of detail as the root changelog entry.
- **FR-018**: All documentation updates (FR-014 through FR-017) MUST be completed and committed before the feature branch is merged.
- **FR-019**: End-to-end (e2e) tests using **Playwright** (TypeScript) MUST be created for each service's primary user journeys. E2e tests MUST exercise the full stack (frontend → backend → db) and be runnable via a documented command in `CLAUDE.md`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A contributor (human or AI agent) can clone the repository and successfully run all tests, linters, and mutation tests by following only the instructions in `CLAUDE.md`, with no additional research, trial and error, or external consultation required.
- **SC-002**: All test suites across all Python services pass with zero unexplained failures or skips.
- **SC-003**: Line coverage for every Python service (backend, agents, db, researcher-mcp) and the frontend is at or above 85% as measured by the CI-integrated coverage tools (`pytest-cov` and `vitest --coverage`).
- **SC-004**: At least 85% of mutants generated by the mutation testing suite are killed by the existing test suite across all Python services (`cosmic-ray`) and the frontend (`stryker`).
- **SC-005**: The mutation testing tool completes its run without errors in the CI environment.
- **SC-006**: Before the feature branch is merged, the root `README.md`, root `CHANGELOG.md`, and the `README.md` and `CHANGELOG.md` of every modified subproject are updated to accurately reflect the changes introduced by this feature.
- **SC-007**: End-to-end tests exist for each service's primary user journeys, all pass, and their run command is documented in `CLAUDE.md`.

## Assumptions

- The project uses `pytest` as the test runner for all Python services; coverage tooling integrates with it directly.
- "Clean checkout" means a machine with the correct Python version and standard system tools installed, but no project-specific dependencies pre-installed.
- Branch coverage (85%+) is a stretch goal; only line coverage (85%) is mandatory per this feature.
- Mutants that survive because they represent genuinely equivalent code (same observable behaviour) may be documented and excluded, provided each exclusion is justified individually.
- The CI pipeline already exists on **GitHub Actions** and supports adding new steps; this feature only adds to it, not rebuilds it.

## Clarifications

### Session 2026-03-15

- Q: Which CI system is this project using? → A: GitHub Actions
- Q: Which linting/static-analysis toolchain is used for Python services? → A: `ruff` (lint + format) + `mypy` (type checking)
- Q: Which mutation testing tool should be used? → A: `cosmic-ray` (supersedes `mutmut`; constitution updated to v1.5.1)
- Q: How should coverage results be surfaced in GitHub Actions? → A: Hard fail if < 85% + PR comment with coverage summary
- Q: How should unjustified test skips be enforced? → A: `pytest` build gate — skip/xfail without `reason=` causes test run to fail
- Q: When should mutation suites run in CI? → A: Both `cosmic-ray` and `stryker` — manually triggered (`workflow_dispatch`) + automatically at end of every speckit feature implementation; NOT per-PR. Constitution updated to v1.5.2.
- Q: Should `CLAUDE.md` environment setup cover the frontend (Node/npm)? → A: Yes — frontend setup (Node 20 LTS, `npm install`) MUST be included alongside Python service setup
- Q: Should frontend coverage be in `CLAUDE.md` and have a CI hard-fail gate? → A: Yes — `vitest run --coverage` in `CLAUDE.md`; CI gate at 85% with PR comment, same as Python
- Spec updated per Constitution v1.6.0 (Principle X): FR-014–FR-018, SC-006, and User Story 4 added to require README.md and CHANGELOG.md updates at feature completion
- Q: Should the 85% mutant kill-rate threshold apply to the frontend (stryker)? → A: Yes — 85% required for both Python (cosmic-ray) and frontend (stryker)
- Q: What is the expectation for e2e tests? → A: Create e2e tests as part of this feature (FR-019, SC-007 added)
- Q: Which e2e testing tool should be used? → A: Playwright (TypeScript) — full-stack browser + API tests; constitution updated to v1.6.1
