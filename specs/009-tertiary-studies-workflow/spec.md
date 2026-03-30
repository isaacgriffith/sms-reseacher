# Feature Specification: Tertiary Studies Workflow

**Feature Branch**: `009-tertiary-studies-workflow`
**Created**: 2026-03-29
**Status**: Draft
**Input**: User description: "number 9 tertiary-studies-workflow using @docs/features/005-tertiary-studies-workflow.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Tertiary Study (Priority: P1)

A researcher who has completed an SMS and identified a significant body of secondary literature wants to launch a formal Tertiary Study. They open the New Study Wizard, select "Tertiary Study" as the study type, and are guided through setting up a study that treats SLRs, SMSs, and Rapid Reviews as its primary inputs rather than empirical papers.

**Why this priority**: The Tertiary Study type must exist and be creatable before any other workflow steps are possible. Without this, none of the downstream phases can be demonstrated or tested.

**Independent Test**: Can be fully tested by creating a new study of type "Tertiary Study" and verifying the wizard presents study-type-specific guidance and stores the study correctly.

**Acceptance Scenarios**:

1. **Given** a logged-in researcher on the New Study Wizard, **When** they select "Tertiary Study" as the study type, **Then** the wizard displays guidance explaining that a Tertiary Study reviews secondary literature (SLRs, SMSs, Rapid Reviews) and not empirical studies.
2. **Given** the researcher completes the wizard with a title and research questions, **When** they submit, **Then** a new study of type "Tertiary Study" is created and the researcher is taken to the study dashboard.
3. **Given** the researcher opens the study dashboard for a Tertiary Study, **When** they view the phases panel, **Then** phase progression mirrors the SLR workflow with secondary-study-specific labels and guidance.

---

### User Story 2 - Import Seed Secondary Studies (Priority: P2)

A researcher whose SMS uncovered a cluster of high-quality secondary studies wants to "promote" those findings into the seed corpus of a new Tertiary Study rather than re-discovering them through fresh database searches.

**Why this priority**: Seed import is a primary differentiator for the Tertiary Study type; without it, the workflow would require researchers to redundantly re-search for studies they already have.

**Independent Test**: Can be fully tested by importing an existing SMS study from the platform into a Tertiary Study and confirming it appears in the study corpus with appropriate metadata.

**Acceptance Scenarios**:

1. **Given** a Tertiary Study in Phase 1 (search), **When** the researcher selects "Import Seed Studies" and chooses an existing SMS study from the platform, **Then** all papers from that SMS are added as seed candidate studies in the Tertiary Study corpus.
2. **Given** the researcher imports a seed study, **When** they view the imported records, **Then** each record is tagged with its source study and study type (SLR/SMS/RR).
3. **Given** the researcher attempts to import a study that has already been imported, **When** they confirm the import, **Then** the system skips duplicate records and reports how many new records were added versus skipped.

---

### User Story 3 - Quality Assessment with Secondary-Study Checklists (Priority: P3)

A tertiary reviewer wants to appraise the quality of a secondary study in their corpus using criteria appropriate for evaluating SLRs and SMSs, not empirical studies. They open the quality assessment panel for an included secondary study and work through a checklist that covers protocol documentation, search strategy, inclusion criteria, synthesis method, and validity threats.

**Why this priority**: Quality assessment drives inclusion/exclusion decisions and the validity of the tertiary synthesis; using the wrong checklist schema would undermine the entire review.

**Independent Test**: Can be fully tested by opening a study in the quality assessment phase, selecting a secondary-study checklist, and scoring each item — confirming the checklist items match secondary study criteria.

**Acceptance Scenarios**:

1. **Given** an included secondary study in the quality assessment phase, **When** the reviewer opens the quality assessment form, **Then** the checklist items cover: protocol documentation completeness, search strategy adequacy, inclusion/exclusion criteria clarity, quality assessment approach, synthesis method appropriateness, and validity threats discussion.
2. **Given** the reviewer completes all checklist items, **When** they save the assessment, **Then** an overall quality score is calculated and associated with the secondary study record.
3. **Given** two reviewers assess the same secondary study independently, **When** the study coordinator views inter-rater reliability, **Then** Cohen's κ is displayed for quality scores across the two reviewers.

---

### User Story 4 - Data Extraction for Secondary Studies (Priority: P4)

A tertiary reviewer wants to extract structured data from an included secondary study. The extraction form presents fields appropriate for secondary literature, including the type of the reviewed study, research questions it addressed, the databases it searched, the number of primary studies it included, the synthesis approach it used, key findings, and identified research gaps.

**Why this priority**: Secondary-study-specific extraction fields are essential for producing a meaningful tertiary synthesis; generic extraction forms would miss the structured metadata unique to secondary studies.

**Independent Test**: Can be fully tested by opening a data extraction form for an included secondary study and verifying the presence and behaviour of each secondary-study-specific field.

**Acceptance Scenarios**:

1. **Given** an included secondary study in the data extraction phase, **When** the reviewer opens the extraction form, **Then** the form contains fields for: study type (SLR / SMS / Rapid Review), research questions addressed, databases searched, study period covered, number of primary studies included, synthesis approach used, key findings (free text), identified research gaps (free text), and quality rating assigned by the tertiary reviewer.
2. **Given** a reviewer submits extraction data, **When** the coordinator views the extraction summary, **Then** all secondary-study-specific fields are displayed alongside standard extraction fields.
3. **Given** data is extracted for multiple secondary studies, **When** a synthesis is initiated, **Then** the extracted secondary-study fields are available as input dimensions for the synthesis stage.

---

### User Story 5 - Synthesis and Reporting (Priority: P5)

After quality assessment and data extraction are complete, the lead researcher generates a synthesis that identifies convergent findings, divergent conclusions, and research gaps across the body of secondary literature. They then export a final report that includes a landscape section summarising the timeline and evolution of the reviewed secondary studies.

**Why this priority**: Synthesis and reporting are the final deliverables of the workflow; they depend on all upstream phases being complete.

**Independent Test**: Can be fully tested by triggering synthesis on a study with at least two extracted secondary studies and confirming the report includes a landscape section.

**Acceptance Scenarios**:

1. **Given** a Tertiary Study with at least two fully extracted secondary studies, **When** the researcher initiates synthesis, **Then** the system produces a narrative synthesis identifying convergent findings, divergent conclusions, and research gaps.
2. **Given** the synthesis is complete, **When** the researcher views the report, **Then** a dedicated "Landscape of Secondary Studies" section is present, summarising: timeline of reviews, evolution of research questions, and shifts in synthesis methods.
3. **Given** the report is ready, **When** the researcher exports it, **Then** the report is available in JSON, CSV+JSON, Full Archive, and SVG formats, consistent with the SLR export options.

---

### Edge Cases

- What happens when a researcher attempts to create a Tertiary Study without the SMS or SLR workflow prerequisites being enabled on the platform?
- How does the system handle a seed import where the source SMS study contains zero included papers?
- What happens if a secondary study in the corpus cannot be classified as SLR, SMS, or Rapid Review during extraction?
- How does the system handle quality assessment when only one reviewer is assigned to a study (inter-rater reliability not computable)?
- What happens when the researcher tries to initiate synthesis before any secondary studies have completed data extraction?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The New Study Wizard MUST present "Tertiary Study" as a selectable study type with explanatory guidance that distinguishes it from SLR and SMS study types.
- **FR-002**: When a Tertiary Study is created, the system MUST apply the SLR phase gate structure with secondary-study-specific guidance text for each phase.
- **FR-003**: Researchers MUST be able to import an existing SMS, SLR, or Rapid Review study from within the platform as a seed corpus for a new Tertiary Study.
- **FR-004**: The seed import process MUST de-duplicate records by DOI or normalised title + first author, reporting counts of added versus skipped records.
- **FR-005**: The quality assessment module MUST provide a checklist schema designed for secondary studies, covering: protocol documentation completeness, search strategy adequacy, inclusion/exclusion criteria clarity, quality assessment approach, synthesis method appropriateness, and validity threats discussion.
- **FR-006**: AI-assisted quality assessment MUST apply secondary-study quality criteria when suggesting scores or flagging issues for Tertiary Study records.
- **FR-007**: The data extraction form for Tertiary Studies MUST include secondary-study-specific fields: study type (SLR / SMS / Rapid Review), research questions addressed, databases searched, study period covered, number of primary studies included, synthesis approach used, key findings, identified research gaps, and reviewer-assigned quality rating.
- **FR-008**: The search strategy configuration for a Tertiary Study MUST allow researchers to tailor search strings and inclusion/exclusion criteria toward identifying secondary studies in the supported research databases.
- **FR-009**: Snowball sampling (forward and backward citation chasing) MUST be available for Tertiary Studies, targeting citations to and from secondary studies.
- **FR-010**: Synthesis for Tertiary Studies MUST support narrative synthesis and thematic analysis as primary strategies; meta-analysis MUST remain available when secondary studies are sufficiently homogeneous.
- **FR-011**: The generated report MUST include a "Landscape of Secondary Studies" section summarising timeline of reviews, evolution of research questions, and shifts in synthesis methods.
- **FR-012**: Report export MUST support JSON, CSV+JSON, Full Archive, and SVG formats, consistent with the existing SLR report export capability.
- **FR-013**: Inter-rater reliability (Cohen's κ) MUST be computable and displayed when two or more reviewers have scored the same secondary studies during quality assessment.

### Key Entities

- **TertiaryStudy**: A Study record with `study_type = "Tertiary Study"`; inherits all Study attributes; phase progression follows the SLR workflow with secondary-study-specific guidance. Phase 3 (Screening) reuses the existing `PaperQueue` component without modification — no Tertiary-specific screening UI is required.
- **TertiaryStudyQualityChecklist**: Checklist schema for evaluating secondary study quality; contains items for protocol documentation, search strategy, inclusion/exclusion criteria, quality assessment approach, synthesis method, and validity threats; linked to a Tertiary Study.
- **SecondaryStudySeedImport**: Records the relationship between a source platform study (SMS/SLR/RR) and a Tertiary Study; tracks import date, number of records added, and number of duplicates skipped.
- **SecondaryStudyExtraction**: Data extraction record for an included secondary study; stores study type, research questions addressed, databases searched, study period, primary study count, synthesis approach, key findings, research gaps, and reviewer quality rating.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A researcher can create a Tertiary Study and complete all workflow phases (protocol, search, screening, quality assessment, extraction, synthesis, report) without leaving the platform or encountering study-type-inappropriate forms.
- **SC-002**: The system provides at least 6 distinct quality assessment checklist items specific to secondary study evaluation, covering all criteria defined in the feature scope.
- **SC-003**: Data extraction for Tertiary Studies captures all 9 secondary-study-specific fields listed in the feature scope, accessible in both the UI and all export formats.
- **SC-004**: A researcher can import seed secondary studies from an existing platform study in a single operation, with duplicate detection reducing re-entry effort to zero for previously catalogued records.
- **SC-005**: The generated report includes a "Landscape of Secondary Studies" section that covers all three landscape dimensions: timeline, evolution of research questions, and shifts in synthesis methods.
- **SC-006**: All existing export formats (JSON, CSV+JSON, Full Archive, SVG) are available for Tertiary Study reports, with no additional configuration required compared to SLR reports.

## Assumptions

- The `study_type` field on the `Study` entity already supports "Tertiary Study" as a valid value and no schema migration is needed for the top-level study record.
- The SLR phase gate logic can be reused with configuration overrides to supply secondary-study-specific guidance text, rather than requiring a wholly new phase gate implementation.
- Search database connectivity (ACM, IEEE, Scopus, etc.) is already operational via the 006-database-search-and-retrieval feature; Tertiary Studies reuse this infrastructure with adapted search strings.
- "Import seed studies" refers to importing the included-papers corpus of another platform study, not raw search results or external file uploads.
- Narrative synthesis and thematic analysis AI strategies are already available from the SLR workflow and can be applied to Tertiary Studies without re-implementation; only the prompt context and extraction schema differ.
