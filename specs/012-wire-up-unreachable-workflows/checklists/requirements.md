# Specification Quality Checklist: Wire Up Unreachable Workflows

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-06
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Validation Log

**Iteration 1** — one item failed.

- _All functional requirements have clear acceptance criteria_: **FAIL**. FR-015 ("Summary
  counts of the screening funnel … MUST be visible from the phase those counts describe") had
  no Given/When/Then scenario anywhere in the user stories. Every other FR traced to at least
  one.
- **Fix applied**: added acceptance scenario 6 to User Story 1, since the funnel reports
  screening outcomes and therefore belongs with the screening journey rather than with
  extraction.

**Iteration 2** — all items pass.

Checked by scanning the spec for implementation vocabulary (framework names, file extensions,
component names, HTTP verbs, transport terms) — zero occurrences — and by tracing each of the
21 functional requirements to an acceptance scenario or measurable outcome.

**Iteration 3** — re-validated after `/speckit.clarify` (2026-08-06). Five clarifications were
integrated, adding FR-022 through FR-026 and resolving four previously open edge cases. All 16
items still pass: no new implementation vocabulary, no `[NEEDS CLARIFICATION]` markers, no
duplicate FR numbers, and no contradictory text left behind by a replaced statement.

## Notes

- **The source PRD is deliberately implementation-heavy**
  (`docs/features/012-wire-up-unreachable-workflows.md`) because it documents wiring for
  components that already exist by name. That detail was translated out of this spec, not
  carried into it: the PRD's "mount `ReviewerPanel` in the Phase 3 view" becomes "a reviewer
  can select a paper and record a decision". The PRD remains the right reference during
  `/speckit.plan`, where naming the existing modules is appropriate.
- **FR-020 and FR-021 are cross-cutting quality requirements** (reachability, and coverage by a
  test that drives the running system). They are deliberately not attached to a single user
  journey; they are verified by SC-009 and SC-010, which apply to all four journeys.
- **Assumptions are recorded rather than raised as clarifications** where a reasonable default
  exists. Assumption #1 was superseded by the clarification session and widened into FR-023.
  The two most likely to be revisited during planning are #4 (what the queue displays when a
  paper has multiple automated screening rounds) and #6 (extraction and validity sharing one
  phase view). Neither changes the feature's scope.
  **Iteration 4** — re-validated after `/speckit.plan` (2026-08-06). FR-027 was added once the
  plan established that the FR-025 guard cannot be optional; the spec now carries 27 functional
  requirements and 9 assumptions. All 16 items still pass.

- Items marked incomplete require spec updates before `/speckit.clarify` or `/speckit.plan`.
