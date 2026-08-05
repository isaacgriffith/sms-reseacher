# Feature Specification: Improve Testing and Fix CI

**Feature Branch**: `011-improve-testing-and-fix-ci`  
**Created**: 2026-03-31  
**Status**: Draft  
**Input**: User description: "Fix all failing CI pipelines (lint, test coverage, Docker build), configure pre-commit enforcement, and rename project from SMS to Researcher"

## Clarifications

### Session 2026-03-31

- Q: Should pre-commit hooks run full test suites with coverage threshold enforcement, or should coverage be CI-only? → A: Pre-commit runs full test suites with coverage threshold enforcement (Option A). Developers get full local guarantee before code reaches CI, even though commits are slower.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - All CI Pipelines Pass on Main Branch (Priority: P1)

As a developer, I want every CI pipeline to pass on the main branch so that the team has a green baseline and can confidently merge new features.

**Why this priority**: Nothing else matters if CI is red. All other improvements build on a working pipeline. Currently all 9 CI jobs fail.

**Independent Test**: Push the feature branch and verify all GitHub Actions jobs pass (Python lint, Python tests for all 5 packages, frontend lint, frontend tests, Docker build + scan).

**Acceptance Scenarios**:

1. **Given** the current codebase with 12 files needing reformatting, **When** the Python lint job runs, **Then** ruff check and ruff format pass with zero errors across all subproject source directories.
2. **Given** the current codebase with misconfigured coverage, **When** the Python test jobs run for each of the 5 packages, **Then** each package reports >= 85% line coverage and tests pass.
3. **Given** the current frontend with 158 formatting issues, **When** the frontend lint job runs, **Then** ESLint and Prettier checks pass with zero warnings or errors.
4. **Given** the current frontend with line coverage at 81.28% and branch coverage at 84.88%, **When** the frontend test job runs, **Then** line, branch, statement, and function coverage all meet or exceed 85%.
5. **Given** the current Docker build failure in the frontend image, **When** the Docker build + Hadolint + Trivy job runs, **Then** all three images build successfully, pass Hadolint linting, and pass Trivy security scanning.

---

### User Story 2 - Pre-Commit Hooks Enforce Quality Gates Locally (Priority: P2)

As a developer, I want pre-commit hooks to catch linting, formatting, type-check, and Dockerfile issues before code reaches CI, so that I get fast local feedback and avoid pushing broken commits.

**Why this priority**: Prevention is better than cure. Local enforcement reduces CI failure noise and shortens the feedback loop. The project already has a `.pre-commit-config.yaml` but it needs to be expanded and verified.

**Independent Test**: Run `pre-commit run --all-files` and verify that all configured hooks execute and report pass/fail appropriately.

**Acceptance Scenarios**:

1. **Given** a developer has set up the repository, **When** they run `pre-commit install`, **Then** hooks are registered for the `pre-commit` git hook stage.
2. **Given** a Python file with a formatting violation, **When** the developer attempts to commit, **Then** the ruff format hook blocks the commit and reports the violation.
3. **Given** a Python file with a type error, **When** the developer attempts to commit, **Then** the mypy hook blocks the commit and reports the error.
4. **Given** a Dockerfile with a Hadolint violation, **When** the developer modifies that Dockerfile and attempts to commit, **Then** the hadolint hook blocks the commit.
5. **Given** a frontend file with formatting issues, **When** the developer attempts to commit, **Then** the ESLint and Prettier hooks block the commit.
6. **Given** a Python subproject with test coverage below 85%, **When** the developer attempts to commit, **Then** the pytest coverage hook blocks the commit and reports which coverage thresholds were not met.
7. **Given** the frontend with test coverage below 85% on any metric, **When** the developer attempts to commit, **Then** the frontend test coverage hook blocks the commit.

---

### User Story 3 - Project Renamed from SMS to Researcher (Priority: P3)

As the project owner, I want the project identity to reflect its broader scope beyond Systematic Mapping Studies. All "sms" prefixes on subproject package names should be dropped, the project title should become "Researcher", and all documentation (README, CLAUDE.md, speckit constitution, speckit templates) should reflect this new name.

**Why this priority**: The rename is important for project identity and clarity, but it is a mechanical change that does not affect CI health. It must be done carefully to avoid breaking imports and package references.

**Independent Test**: After renaming, verify that `uv sync --all-packages` succeeds, all tests pass, CI references are updated, and Docker images build with updated names.

**Acceptance Scenarios**:

1. **Given** the package `sms-backend` in `backend/pyproject.toml`, **When** the rename is applied, **Then** the package name becomes `backend` and all references (CI matrix, Docker tags, GHCR push, `uv run --package`) are updated.
2. **Given** the package `sms-agent-eval` in `agent-eval/pyproject.toml`, **When** the rename is applied, **Then** the package name becomes `agent-eval` and all references are updated.
3. **Given** the package `sms-researcher-mcp` in `researcher-mcp/pyproject.toml`, **When** the rename is applied, **Then** the package name becomes `researcher-mcp` and all references are updated.
4. **Given** the README title "SMS Researcher", **When** the rename is applied, **Then** the title becomes "Researcher" and all references to "SMS Researcher" throughout documentation are updated.
5. **Given** Docker image tags like `sms-backend:ci`, **When** the rename is applied, **Then** image tags and GHCR push references drop the `sms-` prefix.
6. **Given** the CI E2E test service uses database name `sms_test` and user `sms`, **When** the rename is applied, **Then** these are updated to `researcher_test` and `researcher` (or equivalent non-sms names).
7. **Given** the speckit constitution and CLAUDE.md reference "SMS" as the project scope, **When** the rename is applied, **Then** all references reflect the broader "Researcher" identity.

---

### User Story 4 - Governance Documents Enforce Whole-Project Quality (Priority: P4)

As the project owner, I want CLAUDE.md, the speckit constitution, and speckit templates to mandate that at feature completion, the entire project (all subprojects) must pass linting, static analysis, and coverage thresholds -- not just the changed files. This prevents quality drift across features.

**Why this priority**: Process enforcement prevents the root cause of the current failures (AI agents only checking changed files). However, it is only meaningful after the current issues are fixed.

**Independent Test**: Review the updated governance documents and verify they contain explicit whole-project quality gate language.

**Acceptance Scenarios**:

1. **Given** the current CLAUDE.md, **When** updated, **Then** it contains a section requiring all linting, formatting, type-checking, and coverage to pass across all subprojects before a feature is considered complete.
2. **Given** the current speckit constitution, **When** updated, **Then** it contains a principle requiring whole-project quality validation at feature completion.
3. **Given** speckit templates (plan, tasks), **When** updated, **Then** they include quality gate steps for full-project lint, type-check, and coverage verification.

---

### Edge Cases

- What happens when a pre-commit hook fails due to a missing tool (e.g., hadolint not installed)? The hook should provide a clear error message explaining how to install the tool, and should not silently skip the check.
- What happens when a subproject has 0% coverage due to misconfiguration (no `--cov` flag pointing to the right source)? The CI configuration must specify the correct `--cov=src/<package>` path for each subproject.
- What happens when the package rename breaks internal cross-package imports? All workspace dependency references must be updated alongside the package name.
- What happens when the Docker frontend build fails due to lockfile inconsistency? The `package-lock.json` must be committed and in sync with `package.json`.

## Requirements _(mandatory)_

### Functional Requirements

#### CI Pipeline Fixes

- **FR-001**: Python lint CI job MUST pass ruff check, ruff format, and mypy across all subproject source directories with zero errors.
- **FR-002**: Python test CI jobs MUST specify the correct `--cov` source path for each package so that coverage is measured against the actual source, not reported as 0%.
- **FR-003**: All 5 Python subproject test suites MUST achieve >= 85% coverage for lines, statements, functions, and branches.
- **FR-004**: Frontend CI lint job MUST pass ESLint and Prettier with zero warnings or errors.
- **FR-005**: Frontend test suite MUST achieve >= 85% coverage for lines, branches, statements, and functions.
- **FR-006**: Docker build CI job MUST successfully build all three images (backend, researcher-mcp, frontend) without errors.
- **FR-007**: Hadolint and Trivy scans MUST pass for all three Docker images.

#### Pre-Commit Enforcement

- **FR-008**: Pre-commit hooks MUST enforce ruff check, ruff format, and mypy for Python files.
- **FR-009**: Pre-commit hooks MUST enforce ESLint and Prettier for frontend files.
- **FR-010**: Pre-commit hooks MUST enforce Hadolint for Dockerfiles when those files are modified.
- **FR-011**: Pre-commit hooks MUST run the full test suite for each Python subproject with coverage threshold enforcement (>= 85% line, statement, function, and branch coverage).
- **FR-012**: Pre-commit hooks MUST run the frontend test suite with coverage threshold enforcement (>= 85% line, branch, statement, and function coverage).
- **FR-013**: Pre-commit configuration MUST be documented in developer setup instructions.

#### Project Rename

- **FR-014**: The `sms-backend` package MUST be renamed to `backend`.
- **FR-015**: The `sms-agent-eval` package MUST be renamed to `agent-eval`.
- **FR-016**: The `sms-researcher-mcp` package MUST be renamed to `researcher-mcp`.
- **FR-017**: All CI workflow references to old package names MUST be updated.
- **FR-018**: All Docker image tags and GHCR push references MUST drop the `sms-` prefix.
- **FR-019**: The project README title MUST be changed from "SMS Researcher" to "Researcher".
- **FR-020**: All references to "SMS" as the project name in documentation (CLAUDE.md, README, speckit constitution, speckit templates) MUST be updated to "Researcher".

#### Governance Updates

- **FR-021**: CLAUDE.md MUST require whole-project linting, formatting, type-checking, and coverage validation before any feature is marked complete.
- **FR-022**: The speckit constitution MUST include a principle mandating full-project quality validation (not just changed files) at feature completion.
- **FR-023**: Speckit templates (plan, tasks) MUST include a mandatory quality gate step for full-project validation.

### Assumptions

- The 0% coverage in Python CI is caused by missing `--cov=src/<package>` flags in the CI test command, not by a lack of actual test files.
- The frontend Docker build failure is caused by a lockfile inconsistency (`package-lock.json` out of sync with `package.json`).
- The 12 Python formatting violations and 158 frontend formatting issues are mechanical fixes (auto-formattable) rather than logic changes.
- The `agents` and `db` packages already have non-prefixed names and do not need renaming.
- The repo name change is explicitly out of scope for this feature.
- Pre-commit hooks for Trivy are not included because Trivy requires built Docker images, which is too heavyweight for a pre-commit hook; Trivy scanning remains CI-only.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: All 9 CI jobs in the GitHub Actions pipeline pass on the feature branch before merge.
- **SC-002**: Each of the 5 Python subprojects reports >= 85% coverage for lines, statements, functions, and branches in CI.
- **SC-003**: Frontend reports >= 85% coverage for lines, branches, statements, and functions in CI.
- **SC-004**: `pre-commit run --all-files` completes with all hooks passing, including full test suites with coverage threshold enforcement for both Python and frontend.
- **SC-005**: Zero references to `sms-backend`, `sms-agent-eval`, or `sms-researcher-mcp` remain in CI workflows, Docker configurations, or documentation after the rename.
- **SC-006**: CLAUDE.md, speckit constitution, and speckit templates all contain explicit whole-project quality validation requirements.
- **SC-007**: A developer cloning the repository can set up pre-commit hooks with a single command (`uv run pre-commit install`) and be protected from committing code that violates quality gates.
