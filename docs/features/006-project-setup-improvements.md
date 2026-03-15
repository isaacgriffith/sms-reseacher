# Feature: Project Setup & Quality Improvements

**Feature ID**: 006-project-setup-improvements
**Depends On**: 001-repo-setup, 002-sms-workflow
**Reference**: `docs/todo.md` (Project Setup section)

---

## Overview

Improve the foundational project setup to ensure the codebase is well-tested, mutation-tested, and easy for contributors (human or AI) to work with correctly on the first attempt. This feature is about hardening the existing implementation rather than adding new research functionality.

---

## Scope

### Documentation Updates

- Update `CLAUDE.md` to include accurate, runnable instructions for:
  - Running all test suites (unit, integration, end-to-end) for each service (backend, agents, db, frontend)
  - Running all linters and static analysis tools
  - Running mutation tests
  - Any required environment setup before running tests
- Update `constitution.md` (if present) with the same operational guidance.
- Instructions must be verified to work correctly on a clean checkout without guesswork.

### Test Suite Remediation

- Run all existing tests and identify any failures.
- Fix all failing tests. Do not skip or mark tests as expected failures unless there is a documented justification.
- Add new tests as needed to reach a minimum of 85% code coverage across all Python services (backend, agents, db, researcher-mcp).
- Coverage must be measured by a tool integrated into the CI pipeline (e.g., pytest-cov). The 85% threshold applies to line coverage at minimum; branch coverage is a stretch goal.

### Mutation Testing

- Evaluate the current state of mutation testing tooling (currently `mutmut`).
- If `mutmut` can be made to work correctly on this codebase, fix it and integrate it into the test workflow.
- If `mutmut` cannot be made to work, replace it with an alternative Python mutation testing tool (e.g., `cosmic-ray`, `mutpy`, or `mut.py`) that is compatible with the project's Python version and test framework.
- Run all tests against the mutation suite. Add new tests as needed to ensure that 85% or more of generated mutants are killed.
- Document the chosen mutation testing tool and how to run it in `CLAUDE.md`.

---

## Success Criteria

- A developer (or AI agent) can clone the repository and run all tests, linters, and mutation tests by following only the instructions in `CLAUDE.md`, with no additional research required.
- All existing tests pass.
- Code coverage for all Python services is at or above 85% line coverage.
- At least 85% of mutation testing mutants are killed by the test suite.
- The mutation testing tool runs without errors in CI.
