# Feature Specification: SLR Workflow

**Feature Branch**: `007-slr-workflow`
**Created**: 2026-03-18
**Status**: Draft
**Input**: User description: "number 7 slr-workflow @docs/features/003-slr-workflow.md"

## Overview

Extend the existing research platform to support Systematic Literature Reviews (SLRs) — the most rigorous form of secondary study. SLRs aggregate and synthesise empirical evidence on a focused research question through a strict 3-phase process: Planning (protocol creation and validation), Conducting (search, screening, quality assessment, data extraction), and Reporting (structured academic output). This feature implements the SLR-specific logic behind the "Systematic Literature Review" study type already offered in the New Study Wizard.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Define and Validate an SLR Protocol (Priority: P1)

A researcher who has created a new SLR study needs to document a complete review protocol — covering background, research questions, PICO(C) formulation, search strategy, inclusion/exclusion criteria, quality assessment checklists, data extraction strategy, and synthesis approach — before any search is executed. An AI agent reviews the draft for internal consistency and the researcher can iterate until the protocol is formally approved.

**Why this priority**: The protocol is the foundation of a rigorous SLR; without it the study cannot proceed to Phase 2. Getting this right first prevents costly rework and ensures methodological soundness.

**Independent Test**: Can be fully tested by creating an SLR study, completing the protocol form, submitting it for AI review, receiving feedback, revising, and receiving a "validated" status — all without executing any database search.

**Acceptance Scenarios**:

1. **Given** an SLR study exists with no protocol, **When** the researcher opens the Protocol Editor and completes all required sections, **Then** the system saves the draft protocol and displays a summary of all entered fields.
2. **Given** a draft protocol exists, **When** the researcher submits it for AI review, **Then** the system returns a structured evaluation report identifying any internal inconsistencies or missing elements.
3. **Given** the AI review report has been addressed, **When** the researcher approves the protocol, **Then** the protocol is marked "Validated" and Phase 2 search controls become available.
4. **Given** a protocol has not been validated, **When** the researcher attempts to initiate a database search, **Then** the system blocks the action and explains that protocol validation is required.

---

### User Story 2 — Multi-Reviewer Independent Screening with Inter-Rater Agreement (Priority: P2)

Two or more reviewers independently assess the same candidate papers (by title/abstract, then introduction/conclusions, then full-text) using the configured inclusion/exclusion criteria. After each independent round, the system calculates Cohen's Kappa between each reviewer pair and — if agreement is below threshold — initiates a Think-Aloud discussion flow, then re-measures and records both pre- and post-discussion Kappa values.

**Why this priority**: Multi-reviewer consensus is the core methodological safeguard that separates SLRs from less rigorous review types; it must be operational before quality assessment or data extraction can begin.

**Independent Test**: Can be tested by assigning two reviewer accounts to an SLR study with at least 10 candidate papers, having each reviewer independently submit decisions, then verifying that the system computes a Kappa value and surfaces the discussion flow when the value falls below the configured threshold.

**Acceptance Scenarios**:

1. **Given** two reviewers have independently assessed the same set of papers at the title/abstract stage, **When** the last reviewer submits their decisions, **Then** the system calculates Cohen's Kappa between the reviewer pair and displays it on the study dashboard.
2. **Given** the computed Kappa is below the configured threshold, **When** the Kappa result is displayed, **Then** the system triggers the Think-Aloud discussion workflow to resolve disagreements paper by paper.
3. **Given** the discussion workflow is complete, **When** reviewers re-submit their decisions, **Then** the system records both the pre-discussion and post-discussion Kappa values in the audit log.
4. **Given** a paper is marked for exclusion by one reviewer but not by another, **When** consensus has not been reached, **Then** the paper is retained (not excluded) until both reviewers agree on exclusion.
5. **Given** both a conference paper and its journal extension exist in the candidate set, **When** deduplication is run, **Then** only the most recently published version is retained.

---

### User Story 3 — Study Quality Assessment with Configurable Checklists (Priority: P3)

For each paper that passes inclusion screening, a reviewer performs a formal quality assessment using a configurable checklist that evaluates the quality of the underlying study (not merely its reporting). Quality scores are recorded per paper and can be used to weight evidence during synthesis and to investigate contradictory findings.

**Why this priority**: Quality assessment is mandatory for SLR rigour and directly feeds the synthesis phase; it cannot be skipped or deferred.

**Independent Test**: Can be tested by configuring a quality checklist for an SLR study, assigning it to an accepted paper, completing the assessment form, and verifying that a numeric quality score is recorded and visible in the paper detail view.

**Acceptance Scenarios**:

1. **Given** a quality assessment checklist has been configured for the study, **When** a paper is marked as accepted, **Then** the system creates a pending quality assessment task for each assigned reviewer.
2. **Given** a reviewer opens the quality assessment form, **When** they complete and submit all checklist items, **Then** the system stores the item-level responses and computes an aggregate quality score for that paper.
3. **Given** two reviewers have independently completed quality assessments for the same paper, **When** both submissions are recorded, **Then** the system calculates inter-rater agreement (Cohen's Kappa) on quality scores and displays it alongside the assessments.
4. **Given** a paper has a recorded quality score, **When** the researcher views the data extraction or synthesis pages, **Then** the quality score is available as a weighting factor.

---

### User Story 4 — Data Synthesis (Meta-Analysis, Descriptive, and Qualitative) (Priority: P4)

After quality assessment is complete, the researcher selects a synthesis approach — meta-analysis, descriptive synthesis, or qualitative synthesis — and executes it against the accepted papers. Each approach produces a visualised or tabulated output (Forest plot, funnel plot, or thematic table) and is accompanied by a sensitivity analysis.

**Why this priority**: Synthesis is the analytical core that transforms raw extracted data into research conclusions; it is the final step before reporting.

**Independent Test**: Can be tested by configuring descriptive synthesis on a study with at least 3 accepted papers, entering effect-size data for each, running synthesis, and verifying that a Forest plot is generated and displayed.

**Acceptance Scenarios**:

1. **Given** descriptive synthesis is selected and at least 3 accepted papers have effect-size data entered, **When** the researcher runs synthesis, **Then** the system generates a Forest plot showing means and variance of differences between treatments per study.
2. **Given** meta-analysis is selected with homogeneous studies, **When** synthesis is run, **Then** the system applies a fixed-effects model and generates a funnel plot for publication bias analysis.
3. **Given** meta-analysis is selected with heterogeneous studies, **When** a heterogeneity test (Q-test or Likelihood Ratio) indicates inhomogeneity, **Then** the system switches to a random-effects model and reports the heterogeneity statistic.
4. **Given** qualitative synthesis is selected, **When** the researcher chooses thematic analysis and submits themes, **Then** the system stores the theme-to-paper mapping and renders a thematic summary table.
5. **Given** any synthesis approach is run, **When** synthesis completes, **Then** the system also runs a sensitivity analysis by re-running synthesis on defined paper subsets and reporting consistency of conclusions.

---

### User Story 5 — Structured SLR Report Export (Priority: P5)

Once synthesis is complete, the researcher generates a structured report covering all required SLR sections (background, review questions, protocol, search process, inclusion/exclusion decisions, quality assessment results, extracted data, synthesis results, validity discussion, recommendations) and exports it in at least one academic-ready format.

**Why this priority**: The report is the end deliverable of the SLR and must meet academic publication standards to be useful.

**Independent Test**: Can be tested by completing all prior phases for a small SLR study and invoking report generation, then verifying that the exported document contains all required section headings and data.

**Acceptance Scenarios**:

1. **Given** all SLR phases are complete (protocol validated, search done, quality assessed, synthesis run), **When** the researcher triggers report generation, **Then** the system produces a structured document containing all required SLR sections.
2. **Given** the report has been generated, **When** the researcher selects LaTeX/Markdown export, **Then** the system downloads a file using the SLR report template with all section data pre-populated.
3. **Given** the report has been generated, **When** the researcher selects JSON or CSV+JSON export, **Then** the system exports all study data in the chosen format consistent with SMS workflow exports.

---

### User Story 6 — Grey Literature Tracking (Priority: P6)

The researcher can register and track grey literature sources — technical reports, dissertations/theses, rejected publications, and works-in-progress — to explicitly address publication bias in the SLR.

**Why this priority**: Grey literature tracking is required by SLR methodology to guard against publication bias, though it is less central than protocol, screening, and synthesis.

**Independent Test**: Can be tested by adding a grey literature source to an SLR study, tagging it by type (e.g., dissertation), and verifying it appears in the grey literature section of the study dashboard.

**Acceptance Scenarios**:

1. **Given** an SLR study is in Phase 2, **When** a researcher adds a grey literature source with a type (technical report, dissertation, rejected publication, work-in-progress) and metadata, **Then** the source is stored and listed under Grey Literature for the study.
2. **Given** grey literature sources exist for a study, **When** the report is generated, **Then** the report section on search process includes a summary of grey literature sources consulted.

---

### Edge Cases

- What happens when a reviewer submits quality assessment for a paper that another reviewer has not yet assessed? The system should allow partial completion and calculate Kappa only when both reviewers have submitted.
- What happens when the heterogeneity test for meta-analysis is inconclusive? The system should present the raw statistic and allow the researcher to manually select fixed or random effects with a recorded justification.
- What happens when fewer than 3 accepted papers exist at the point descriptive synthesis is run? The system should warn the researcher that a Forest plot cannot be generated below the minimum paper count.
- What happens when a reviewer's Kappa cannot be calculated (e.g., one reviewer approved all papers, creating a zero-variance distribution)? The system should surface an informative warning explaining the calculation limitation rather than showing an error.
- What happens when a conference paper and its journal version are discovered post-inclusion? The system should support a late-deduplication workflow that allows both to be surfaced, compared, and the older one excluded.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Phase 1 — Planning

- **FR-001**: System MUST allow a researcher to create a full SLR review protocol within a study, covering: background and rationale, research questions with PICO(C) formulation, search strategy, inclusion/exclusion criteria, quality assessment checklist definitions, data extraction strategy, synthesis approach selection, dissemination strategy, and timetable.
- **FR-002**: System MUST prevent Phase 2 search from being initiated until the review protocol has been formally validated.
- **FR-003**: System MUST submit the draft review protocol to an AI agent for consistency and completeness review, returning a structured feedback report to the researcher.
- **FR-004**: Researchers MUST be able to revise and resubmit the protocol for AI review iteratively until they approve it, at which point it is marked "Validated."
- **FR-005**: System MUST support a pre-study validation phase in which search strings and inclusion/exclusion criteria can be tested against a representative sample before the main search is executed.

#### Phase 2 — Conducting the Review

- **FR-006**: System MUST support independent evaluation of candidate papers by multiple reviewers at each screening stage (title/abstract, introduction/conclusions, full-text), without reviewers being able to see each other's decisions until the independent round closes.
- **FR-007**: System MUST calculate Cohen's Kappa between each pair of reviewers after each independent assessment round and display the result on the study dashboard.
- **FR-008**: System MUST trigger a Think-Aloud discussion workflow when the computed Kappa between any reviewer pair falls below the configured minimum threshold.
- **FR-009**: System MUST record both pre-discussion and post-discussion Kappa values in the study audit log when the Think-Aloud workflow is used.
- **FR-010**: System MUST implement iterative exclusion: a paper is only excluded when all assigned reviewers agree; papers with any disagreement are retained and escalated.
- **FR-011**: System MUST detect and surface version-duplicate pairs (conference paper + journal extension) for reviewer adjudication, retaining only the most recently published version upon agreement.
- **FR-012**: System MUST support tracking of grey literature sources (technical reports, dissertations/theses, rejected publications, works-in-progress) as distinct from database search results.
- **FR-013**: System MUST allow configurable quality assessment checklists to be defined per study, with each checklist item recording a response that contributes to an aggregate quality score per paper.
- **FR-014**: System MUST create pending quality assessment tasks for each assigned reviewer for every paper that passes inclusion screening.
- **FR-015**: System MUST calculate inter-rater agreement (Cohen's Kappa) on quality assessment scores when two or more reviewers have independently assessed the same paper.
- **FR-016**: Quality scores MUST be available as weighting factors during data synthesis and for investigating causes of contradictory results.

#### Data Synthesis

- **FR-017**: System MUST support meta-analysis synthesis, including: fixed-effects model (for homogeneous studies), random-effects model (for inhomogeneous studies), Q-test and Likelihood Ratio test for heterogeneity, effect size extraction and normalisation across studies, and funnel plot generation for publication bias analysis.
- **FR-018**: System MUST support descriptive synthesis, including: tabulation of sample size per intervention, effect size estimates with standard errors, mean differences between interventions, confidence intervals, units of measurement, and Forest plot generation visualising means and variance of differences per study.
- **FR-019**: System MUST support at least one qualitative synthesis approach: thematic analysis, narrative synthesis, comparative analysis, case survey, or meta-ethnography.
- **FR-020**: System MUST run a sensitivity analysis for any synthesis approach by re-running synthesis on defined paper subsets and reporting consistency of conclusions.
- **FR-021**: System MUST generate a Forest plot for any study using descriptive synthesis with at least 3 accepted papers.

#### Phase 3 — Reporting

- **FR-022**: System MUST generate a structured SLR report containing all required sections: background, review questions, protocol summary, search process, inclusion/exclusion decisions, quality assessment results, extracted data, synthesis results, validity discussion, and recommendations.
- **FR-023**: System MUST export the SLR report in LaTeX/Markdown format using a structured SLR report template with all sections pre-populated from study data.
- **FR-024**: System MUST support the same export formats as the SMS workflow (JSON, CSV+JSON, Full Archive, SVG only) for all SLR study data.

### Key Entities

- **ReviewProtocol**: A versioned, structured document attached to an SLR study capturing all protocol sections; has a status (Draft, Under Review, Validated); linked to a study.
- **QualityAssessmentChecklist**: A named set of assessment items defined for a study; each item has a question and a scoring method (binary, scale, etc.); reusable across papers in the study.
- **QualityAssessmentScore**: A reviewer's response to a single checklist item for a specific paper; aggregated into a per-paper quality score; supports comparison between reviewers.
- **InterRaterAgreementRecord**: A record of a Cohen's Kappa calculation between two reviewers for a specific assessment round (screening or quality); stores pre- and post-discussion values and the round type.
- **SynthesisResult**: The output of a synthesis run for a study; stores the approach type, input parameters, computed statistics, generated visualisation references, and sensitivity analysis results.
- **GreyLiteratureSource**: A non-database literature source tracked for a study; attributes include type (technical report, dissertation, rejected publication, work-in-progress), title, author, year, and rationale for inclusion.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A researcher can define and submit a complete SLR protocol for AI review without leaving the study workspace, completing the process in a single session.
- **SC-002**: The system correctly calculates and displays Cohen's Kappa between any two reviewers who have independently assessed the same set of papers, producing a value within the expected range of −1 to 1.
- **SC-003**: At least one full synthesis approach (meta-analysis, descriptive, or qualitative) can be executed end-to-end from data input to visualised or tabulated output without manual intervention.
- **SC-004**: A Forest plot is generated automatically for any study using descriptive synthesis with at least 3 accepted papers.
- **SC-005**: The final report export contains all required SLR section headings and is populated with study data, requiring no manual restructuring before academic submission.
- **SC-006**: Inter-rater agreement (Kappa) is computed and the discussion workflow is triggered within one page navigation after both reviewers complete an independent assessment round.
- **SC-007**: Phase gates enforce correct sequencing: researchers cannot advance to search without a validated protocol, cannot run synthesis without completed quality assessments, and cannot generate a report without completed synthesis.
- **SC-008**: Grey literature sources are tracked separately from database search results and appear as a distinct section in both the study dashboard and generated report.

---

## Assumptions

- The "Systematic Literature Review" study type selection in the New Study Wizard (FR-006 of feature 002) is already in place; this feature delivers the SLR-specific phase logic and screens that appear after that selection.
- Existing entities (Study, CandidatePaper, DataExtraction, Reviewer, PaperDecision, AuditRecord) from the SMS workflow are reused without modification.
- "Configurable minimum Kappa threshold" defaults to 0.6 (substantial agreement), consistent with published SLR methodology guidelines; researchers may override this per study.
- PICO(C) formulation is captured as structured fields within the Review Protocol (not free text only), enabling downstream validation.
- The AI protocol review agent uses the same multi-provider LLM infrastructure introduced in feature 005.
- Sensitivity analysis is defined as researcher-specified paper subsets (e.g., "exclude papers with quality score below 3") rather than automated statistical bootstrapping.
- Version deduplication (conference vs. journal) applies only when both versions were retrieved in the same study's candidate pool; cross-study deduplication is out of scope.
