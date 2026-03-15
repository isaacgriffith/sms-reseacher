# Feature: Tertiary Studies Workflow

**Feature ID**: 005-tertiary-studies-workflow
**Depends On**: 002-sms-workflow, 003-slr-workflow
**Reference**: `docs/all-together.md` (Tertiary Studies section), `docs/tertiary-studies.md`

---

## Overview

Extend the research platform to support Tertiary Studies. A Tertiary Study is a Systematic Literature Review of secondary studies (SLRs, SMSs, and Rapid Reviews). Its goal is to aggregate and synthesize knowledge from a large body of secondary literature, typically conducted when a Systematic Mapping Study uncovers a significant number of secondary studies within a topic area.

Tertiary Studies apply the same rigorous methodology as Systematic Literature Reviews, but the "primary studies" being reviewed are themselves secondary studies (SLRs, SMSs, Rapid Reviews) rather than direct empirical studies.

---

## Scope

### Trigger and Context

- A Tertiary Study is typically initiated when a Systematic Mapping Study or preliminary search surfaces a significant number of high-quality secondary studies on a topic.
- The system should support a workflow where a researcher can "promote" findings from an existing SMS into the seed set for a new Tertiary Study.
- The New Study Wizard must support "Tertiary Study" as a study type with appropriate guidance noting this is a review of secondary studies.

### Study Identification

- The search strategy targets secondary studies (SLRs, SMSs, Rapid Reviews) rather than primary empirical studies.
- Inclusion/exclusion criteria must accommodate the secondary study type: quality of the protocol, breadth of primary study coverage, synthesis approach used, and recency.
- The system should support searching for secondary studies in the same research databases (ACM, IEEE, Scopus, etc.) but with search strings and criteria adapted for secondary study identification.
- Snowball sampling applies in both directions (references of and citations to secondary studies).

### Quality Assessment of Secondary Studies

- Quality assessment checklists for secondary studies differ from those for primary studies. The system must support checklists designed to evaluate the rigor, completeness, and validity of secondary studies, including:
  - Protocol documentation completeness
  - Search strategy adequacy
  - Inclusion/exclusion criteria clarity
  - Quality assessment approach
  - Synthesis method appropriateness
  - Validity threats discussion
- AI-assisted quality assessment must be trained on secondary study quality criteria.

### Data Extraction

- Data extraction from secondary studies captures: study type (SLR/SMS/RR), research questions addressed, databases searched, study period covered, number of primary studies included, synthesis approach used, key findings, identified research gaps, quality rating assigned by the tertiary reviewer.
- The system maps extracted data against the tertiary study's own research questions.

### Synthesis

- The synthesis of tertiary studies typically uses qualitative approaches (narrative synthesis, thematic analysis) to identify convergent findings, divergent conclusions, and research gaps across the body of secondary literature.
- Meta-analysis is rarely applicable at this level but should not be excluded if the secondary studies are sufficiently homogeneous in their synthesis methods.

### Reporting

- The tertiary study report follows the standard SLR report structure, adapted for secondary study context.
- An additional section summarizing the landscape of secondary studies (timeline of reviews, evolution of research questions, shifts in synthesis methods) is included.
- Export formats match the SLR workflow (JSON, CSV+JSON, Full Archive, SVG).

---

## Integration Points

- Inherits all SMS and SLR workflow capabilities; the "Tertiary Study" type is essentially a specialized SLR targeting secondary studies.
- The `Study` entity's `study_type` field already includes "Tertiary Study" as a valid value.
- When creating a Tertiary Study, the researcher may import seed secondary studies (which may be existing studies within the platform) as the initial test set.
- Adds: `TertiaryStudyQualityChecklist` (checklist schema for secondary study quality evaluation), `SecondaryStudySeedImport` (import an existing platform study as a seed).

---

## Success Criteria

- A researcher can create a Tertiary Study and execute it end-to-end using the same platform UI as SLR, with study-type-specific guidance and checklist schemas.
- The system provides quality assessment checklists appropriate for secondary studies (SLR/SMS/RR quality criteria).
- Data extraction captures secondary-study-specific fields (study type, databases searched, primary study count, synthesis approach).
- A researcher can import an existing SMS study from the platform as a seed secondary study for a new Tertiary Study.
- The generated report includes a section summarizing the landscape of secondary studies reviewed.
