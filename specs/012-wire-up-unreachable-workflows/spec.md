# Feature Specification: Wire Up Unreachable Workflows

**Feature Branch**: `012-wire-up-unreachable-workflows`
**Created**: 2026-08-06
**Status**: Draft
**Input**: User description: "012 using docs/features/012-wire-up-unreachable-workflows.md as the PRD"

## Overview

Three parts of the platform were built, tested, and connected to working services — and then
never made reachable. A researcher cannot record a screening decision, cannot open a Tertiary
Study at all, and is told that the extraction and reporting phases "will be available in a
future sprint" even though they are finished.

This feature makes that work reachable. It adds one genuinely new capability — re-screening an
existing candidate set — and otherwise delivers value that has already been paid for.

## Clarifications

### Session 2026-08-06

- Q: What happens when a re-screen is requested while another assessment is already in flight for that study? → A: Refuse it, naming the run in progress. Two rounds must never interleave over the same candidates.
- Q: What happens when a paper's status changes while a reviewer has it open for decision? → A: The panel flags the change and shows the new state; the reviewer confirms before their decision is submitted. Work in progress is not discarded.
- Q: A re-screen fails part-way through — what happens to the assessments already made? → A: Keep them; mark the run failed with a count of what it covered; restarting assesses only the papers that round has not yet reached.
- Q: Who may start a re-screen, import a seed study, and record extraction data? → A: Any member of the study, uniformly — matching what every related service already enforces, including full search, which spends budget on a member's authority today.
- Q: When a reviewer records a decision on a paper they have already judged, what should happen? → A: Explicit override — the new decision is recorded as a distinct entry flagged as overriding the prior one, which is retained; the reviewer is shown their earlier judgement and must confirm they are changing it.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Record a screening decision (Priority: P1)

A reviewer works through the queue of candidate papers for a study, opens one, judges it
against the study's inclusion and exclusion criteria, and records whether it is accepted,
rejected, or a duplicate — adding the reasons that justify the call and a note for the record.
When a second reviewer has already judged the same paper differently, the disagreement is
visible before the decision is made, not discovered later.

**Why this priority**: Screening is the core activity of every study type the platform
supports, and it is currently impossible to perform. Until this lands, a study cannot progress
past its search by human judgement, and the inter-rater agreement measures the platform
already computes have no human decisions to compare.

**Independent Test**: Open a study with candidate papers, select one from the queue, submit an
accept decision with a reason, and confirm the queue reflects the new status. Delivers a
complete manual screening capability on its own, with nothing else in this feature present.

**Acceptance Scenarios**:

1. **Given** a study with candidate papers awaiting screening, **When** a reviewer selects a
   paper from the queue, **Then** the decision controls for that paper are presented.
2. **Given** a selected paper, **When** the reviewer records an accept, reject, or duplicate
   decision with at least one reason, **Then** the decision is saved and the paper's status in
   the queue updates without the reviewer refreshing the page.
3. **Given** a paper another reviewer has already judged differently, **When** a reviewer opens
   it, **Then** the prior decisions and the disagreement are shown before a decision is made.
4. **Given** a reviewer who is a member but not the lead of a study, **When** they record a
   decision, **Then** it is accepted — screening is a member activity, and agreement measures
   depend on more than one reviewer participating.
5. **Given** a Systematic Mapping Study, a Systematic Literature Review, and a Tertiary Study,
   **When** a reviewer reaches the screening step in each, **Then** the same decision
   capability is available in all three.
6. **Given** a study part-way through screening, **When** the reviewer views the screening
   step, **Then** the running totals of papers identified, accepted, rejected, and marked
   duplicate are visible alongside the queue.

---

### User Story 2 - Conduct a Tertiary Study (Priority: P2)

A researcher creates a Tertiary Study — a review of existing secondary studies — and works
through its five phases: defining the protocol, importing seed studies from their research
group, screening, extracting data about each secondary study, and generating the report with
its landscape-of-reviews section.

**Why this priority**: An entire supported study type currently delivers nothing. A researcher
who selects "Tertiary" is shown the Systematic Mapping Study workspace instead, operating on
their tertiary data — which is worse than an error, because it is not obviously wrong.

**Independent Test**: Create a Tertiary Study, open it, and confirm the tertiary workspace and
its five phases are presented. Then import a seed study from the owning research group.
Delivers the whole tertiary workflow independently of the other stories.

**Acceptance Scenarios**:

1. **Given** a study whose type is Tertiary, **When** a researcher opens it, **Then** the
   tertiary workspace is shown with its five phases — not the mapping-study workspace.
2. **Given** a Tertiary Study in its seed-import phase, **When** the researcher looks for
   source studies, **Then** the studies belonging to the same research group are offered, and
   one can be imported as a seed.
3. **Given** a Tertiary Study whose phases are progressively unlocked, **When** the researcher
   opens it, **Then** only the phases their progress has unlocked are selectable.
4. **Given** a completed tertiary synthesis, **When** the researcher opens the reporting phase,
   **Then** the tertiary report is available, including its summary of the landscape of
   secondary studies.

---

### User Story 3 - Complete extraction, validity, and quality reporting (Priority: P3)

A researcher whose study has accepted papers moves into extraction: they work through the
accepted papers one at a time, recording the data each contributes, resolving any clash if a
collaborator edited the same record concurrently. They then record the study's threats to
validity, and review the quality report that scores the study against its rubric and lists
prioritised recommendations.

**Why this priority**: These phases exist and their services answer, but the workspace shows a
"future sprint" placeholder. Lower than the first two because a study can still be run to the
end of screening without them, and because both preceding stories unblock activities that are
prerequisites for this one.

**Independent Test**: Open a mapping study that has accepted papers, go to the extraction
phase, record data for one paper, then open the reporting phase and view the quality report.
No part of the other stories is required.

**Acceptance Scenarios**:

1. **Given** a study with accepted papers, **When** the researcher opens the extraction phase,
   **Then** the accepted papers are listed and one can be selected for data entry.
2. **Given** a paper selected for extraction, **When** the researcher records and saves data,
   **Then** it is persisted and reflected in the list.
3. **Given** two researchers editing the same extraction record, **When** the second saves over
   a change they had not seen, **Then** the conflict is surfaced with both versions and the
   second researcher chooses how to resolve it, rather than silently overwriting.
4. **Given** a study in the extraction phase, **When** the researcher records threats to
   validity, **Then** the entries are saved, and they may optionally request a drafted starting
   point rather than writing from scratch.
5. **Given** a study with a generated quality report, **When** the researcher opens the
   reporting phase, **Then** the rubric scores and prioritised recommendations are shown.
6. **Given** any supported study type, **When** a researcher opens any phase, **Then** no
   message stating that content will be available in a future sprint is ever shown.

---

### User Story 4 - Re-screen after revising criteria (Priority: P4)

A researcher realises their inclusion or exclusion criteria were too broad, revises them, and
re-screens the papers already retrieved — without repeating the expensive database search that
found them. Progress is visible while it runs, and the earlier round of judgements is retained
so the effect of the revision can be compared.

**Why this priority**: The only genuinely new capability here, and the only one with no
existing implementation behind it. Valuable but not blocking: today a researcher can achieve
the same outcome by re-running the full search, at greater cost.

**Independent Test**: Revise a study's criteria, start a re-screen, watch it report progress to
completion, and confirm the earlier round of decisions is still retrievable.

**Acceptance Scenarios**:

1. **Given** a study whose candidate papers have already been retrieved, **When** the
   researcher starts a re-screen, **Then** the existing candidates are assessed against the
   current criteria without a new database search being performed.
2. **Given** a re-screen in progress, **When** the researcher watches the study, **Then**
   progress is reported in the same way as any other long-running task.
3. **Given** a completed re-screen, **When** the researcher reviews a paper, **Then** the
   earlier automated judgement is still available alongside the new one, and any decision a
   human recorded is unchanged.

---

### Edge Cases

- **A paper is selected for decision and the queue then changes** (a re-screen finishes, or a
  collaborator's decision alters its status). The change is flagged with the paper's new state
  and the reviewer confirms before their decision is submitted; the reasons and annotation they
  have already entered are preserved.
- **A reviewer records a decision on a paper they have already judged.** Their earlier
  judgement is shown and they must confirm they are changing it; the new decision is recorded
  as an override and the original is retained.
- **The extraction phase is opened when no papers have been accepted yet.** An empty state must
  explain why, rather than presenting an empty list with no cause.
- **A Tertiary Study's research group contains no other studies.** Seed import must say so
  instead of offering an empty picker.
- **A re-screen is started while another assessment is in flight** for the same study — a
  second re-screen, or a full search whose pipeline also screens candidates. It is refused,
  naming the run already in progress.
- **A re-screen is started when the study has no candidate papers at all.** It reports that
  there is nothing to assess rather than starting an empty run.
- **A re-screen fails part-way through.** Completed assessments are kept and the run is
  reported as failed with its coverage; a restart picks up only the papers it did not reach.
- **A researcher opens a study type the workspace does not recognise.** It must fail visibly
  rather than falling through to another type's workspace over the wrong data — the failure
  mode this feature exists to eliminate.
- **A reviewer loses their study membership while a decision is in flight.**

## Requirements _(mandatory)_

### Functional Requirements

**Screening decisions**

- **FR-001**: Reviewers MUST be able to select an individual candidate paper from the screening
  queue and record a decision on it.
- **FR-002**: A decision MUST support the outcomes accept, reject, and duplicate, MUST allow
  one or more reasons drawn from the study's criteria, and MUST allow a free-text annotation.
- **FR-003**: After a decision is recorded, the queue MUST reflect the paper's new status
  without the reviewer taking any further action.
- **FR-004**: Before recording a decision, a reviewer MUST be shown the decisions previously
  recorded on that paper and whether reviewers disagree.
- **FR-025**: If a paper's status changes while a reviewer has it open, the system MUST flag
  the change and show the new state, and MUST require confirmation before submitting the
  decision. Any reasons or annotation already entered MUST be preserved across that
  confirmation, and a decision MUST NOT be recorded against a state the reviewer never saw.
- **FR-027**: Recording a decision MUST carry the reviewer's view of the paper's state, and a
  submission that omits it MUST be refused. The check MUST NOT be optional: a caller able to
  skip it regains exactly the ability FR-025 removes. This tightens an existing capability, so
  every existing caller and every automated check that records a decision MUST be updated in
  the same change rather than left to fail afterwards.
- **FR-005**: Any member of a study MUST be able to record a decision; the capability MUST NOT
  be restricted to the study lead.
- **FR-023**: Every capability in this feature — recording decisions, importing seed studies,
  recording extraction data and threats to validity, and starting a re-screen — MUST be
  available to any member of the study, not the lead alone. No capability here introduces a
  lead-only restriction that comparable existing capabilities do not already impose.
- **FR-006**: Screening decisions MUST be available in every study type that has a screening
  phase.
- **FR-022**: When a reviewer records a second decision on a paper they have already judged,
  the system MUST show their earlier judgement, MUST require explicit confirmation that they
  are changing it, and MUST retain the original as part of the paper's history — recording the
  new decision as an override rather than replacing or silently appending. A reviewer's
  correction MUST remain distinguishable from disagreement between reviewers, so that agreement
  measures are not distorted by it.

**Tertiary Studies**

- **FR-007**: Opening a study MUST present the workspace belonging to that study's type. A type
  with a dedicated workspace MUST NOT be shown another type's.
- **FR-008**: The Tertiary Study workspace MUST present its five phases, honouring which phases
  the study's progress has unlocked.
- **FR-009**: A researcher MUST be able to see the other studies in the research group that
  owns a Tertiary Study, and import one as a seed secondary study.
- **FR-010**: The system MUST make a study's owning research group available wherever a feature
  depends on it. No user-facing capability may depend on information the platform withholds
  from the screen that needs it.

**Extraction, validity, and quality reporting**

- **FR-011**: The extraction phase MUST list the study's accepted papers and allow data to be
  recorded against a selected one.
- **FR-012**: Concurrent edits to the same extraction record MUST be detected and presented for
  resolution, showing both versions. Silent overwriting is not acceptable.
- **FR-013**: The extraction phase MUST allow threats to validity to be recorded, with the
  option to request a drafted starting point.
- **FR-014**: The reporting phase MUST present the study's quality report, including rubric
  scores and prioritised recommendations.
- **FR-015**: Summary counts of the screening funnel — papers identified, accepted, rejected,
  and marked duplicate — MUST be visible from the phase those counts describe.
- **FR-016**: No phase of any study type may present a placeholder stating that its content is
  not yet available, where the capability exists.

**Re-screening**

- **FR-017**: A researcher MUST be able to re-assess a study's existing candidate papers
  against its current criteria without performing a new database search.
- **FR-018**: A re-screen MUST report progress while it runs, consistent with other
  long-running tasks.
- **FR-026**: A re-screen MUST be refused while another assessment of the same study's
  candidates is in flight, and the refusal MUST identify the run in progress. Two rounds of
  automated judgement MUST NOT interleave over the same candidate papers, since a round is the
  unit that round-over-round comparison depends on.
- **FR-019**: A re-screen MUST preserve earlier automated judgements as a distinct round rather
  than overwriting them, and MUST NOT alter decisions recorded by a human.
- **FR-024**: A re-screen that fails part-way MUST retain the assessments it completed, MUST
  report how many papers it covered, and MUST be restartable such that it assesses only the
  papers that round has not yet reached. Assessments already paid for MUST NOT be discarded by
  a failure, and a round MUST NOT be reported as complete while its coverage is partial.

**Reachability**

- **FR-020**: Every screen the platform contains for a supported study type MUST be reachable
  by a user through normal navigation.
- **FR-021**: Each capability delivered by this feature MUST be exercised by an automated test
  that drives it the way a user would, against a running system.

### Key Entities

- **Candidate Paper**: A paper retrieved by a study's search, awaiting or holding a screening
  outcome. Carries its current status and whether reviewers disagree about it.
- **Screening Decision**: One reviewer's judgement on one candidate paper — the outcome, the
  reasons, an optional annotation, and who recorded it. Multiple decisions may exist per paper;
  that is what makes agreement measurable.
- **Reviewer**: A participant in screening, human or automated. A re-screen introduces a new
  automated reviewer round rather than replacing the previous one.
- **Screening Run**: An assessment of a study's existing candidate papers against its current
  criteria, tracked as a long-running task with observable progress.
- **Study**: A research study of one of the supported types, belonging to a research group,
  progressing through phases that unlock as work completes.
- **Research Group**: The owner of a set of studies. Determines which studies are offered as
  seeds for a Tertiary Study.
- **Data Extraction**: The data recorded from one accepted paper, versioned so concurrent edits
  are detected rather than lost.
- **Validity Assessment**: A study's recorded threats to validity across its dimensions.
- **Quality Report**: Rubric scores and prioritised recommendations for a study.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: A reviewer can record a screening decision on a candidate paper in under 30
  seconds from opening the study, in every study type that screens papers.
- **SC-002**: 100% of screening decisions recorded by a reviewer are reflected in the paper
  queue without any manual refresh.
- **SC-003**: When two reviewers disagree about a paper, the disagreement is visible to the
  next reviewer before they record their own decision, in 100% of cases.
- **SC-004**: A researcher opening a study of any supported type reaches that type's workspace
  100% of the time; no study type presents another type's workspace.
- **SC-005**: A researcher can carry a Tertiary Study from creation through seed import,
  screening, extraction, and report generation without leaving the platform.
- **SC-006**: A researcher can record extraction data, record threats to validity, and view a
  quality report for a mapping study — none of which is possible today.
- **SC-007**: No phase of any study presents a placeholder saying its content is unavailable.
- **SC-008**: Re-screening an existing candidate set completes without performing a new
  database search, and preserves 100% of previously recorded human decisions.
- **SC-009**: Every screen built for a supported study type is reachable through normal
  navigation — measured by an automated check that fails when any is not.
- **SC-010**: Each of the four user journeys above is covered by an automated test that drives
  the running system, where today three of them have no such coverage because they could not be
  reached.

## Assumptions

Recorded rather than raised as blocking questions, because a reasonable default exists for
each. Any may be overturned during planning without changing the feature's scope.

1. **This feature is member-level throughout.** Any member of a study may record decisions,
   import seeds, extract data, and start a re-screen — see FR-023. Confirmed against the
   existing services rather than assumed: all of them gate on study membership today.
2. **Re-screening covers all of a study's candidate papers**, not only those still undecided.
   A researcher revising criteria wants to know the effect on the whole set.
3. **Re-screening does not touch human decisions.** It adds an automated round; a human
   judgement remains the paper's recorded outcome where one exists.
4. **The most recent decision per reviewer is what the queue displays**, with earlier rounds
   available in the paper's history rather than in the queue itself.
5. **The screening funnel counts belong with the screening phase**, since that is where the
   accepted, rejected, and duplicate figures are produced.
6. **Extraction and threats to validity share one phase view**, presented in sequence rather
   than as nested tabs — the phase bar is already the primary navigation, and a second level of
   tabs within it is the confusion this feature is removing elsewhere.
7. **The Tertiary workspace replaces the generic study workspace** for tertiary studies rather
   than being embedded within it, since it brings its own phase navigation.
8. **Tightening decision recording is a breaking change, and an accepted one.** FR-027 makes
   the reviewer's observed state mandatory on submission. Existing callers that omit it stop
   working. This is acceptable because the platform's only consumers are its own interface and
   its own automated checks, both updated together — there is no external caller. Were that not
   so, the guard would need a transition period instead.
9. **No new stored data is required.** Every entity above already exists; this feature changes
   what is reachable, not what is recorded — with the single exception of making a study's
   owning research group available to the screen that needs it.

## Dependencies

- Existing screening decision, extraction, validity, quality report, metrics, and tertiary
  study services — all in place and exercised by existing tests.
- Existing long-running task progress reporting, reused unchanged by re-screening.
- The automated screening capability invoked today as part of a full search, reused by
  re-screening against an existing candidate set.

## Out of Scope

- Changing how inter-rater agreement is calculated or how it gates progress. This feature makes
  human decisions recordable so that agreement becomes measurable in practice; it does not
  alter the measure.
- Changing the unit of analysis underlying extraction.
- Redesigning any existing screen. Where a screen proves wrong once reachable, that is a
  finding to record, not to fix here.
- Two remaining unreachable controls that sit inside features which are themselves already
  reachable, so no user journey is blocked by them.
