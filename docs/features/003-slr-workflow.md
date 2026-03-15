# Feature: Systematic Literature Review (SLR) Workflow

**Feature ID**: 003-slr-workflow
**Depends On**: 002-sms-workflow (existing SMS pipeline)
**Reference**: `docs/systematic-literature-reviews.md`

---

## Overview

Extend the existing research platform to support Systematic Literature Reviews (SLRs). An SLR is the most rigorous form of secondary study, aimed at aggregating and synthesizing empirical evidence (experiments, case studies, controlled trials) on a specific research question. It follows a strict 3-phase process: Planning, Conducting, and Reporting.

SLRs differ from Systematic Mapping Studies primarily in:
- Deeper focus on empirical study quality and evidence strength
- Formal study quality assessment using published checklists
- Advanced data synthesis techniques (meta-analysis, descriptive synthesis, qualitative approaches)
- PICO(C) framework used with explicit consideration of empirical study design types
- Multi-reviewer protocol with formal inter-rater agreement measurement (Cohen's Kappa)
- Pre-study protocol validation before execution

---

## Scope

### Phase 1: Planning

- **Protocol Creation**: Researchers must define and document a full review protocol before beginning search. The protocol covers: background and rationale, research questions, search strategy, inclusion/exclusion criteria, quality assessment checklists and procedures, data extraction strategy, data synthesis approach, dissemination strategy, and timetable.
- **PICO(C) Formulation**: Uses the same PICO(C) framework as the SMS workflow but emphasizes inclusion of experimental study types (e.g., controlled experiments, case studies, replication studies) in the research questions.
- **Pre-Study Validation**: System supports a pre-study phase to scope research questions, validate search strings, and validate inclusion/exclusion criteria against a known representative sample.
- **Protocol Review**: AI agent evaluates the draft protocol for internal consistency and validity before the study proceeds.

### Phase 2: Conducting the Review

All search strategies from the SMS workflow apply (Database Search, Manual Search, Snowball Sampling, Grey Literature). Key SLR-specific additions:

- **Grey Literature Support**: System supports tracking of technical reports, dissertations/theses, rejected publications, and works-in-progress to address publication bias.
- **Study Quality Assessment**: For each accepted paper, a formal quality assessment is performed using configurable checklists. Quality scores can be used to weight evidence in synthesis and to investigate causes of contradicting results. Quality of the study (not its reporting) is evaluated.
- **Multi-Reviewer with Inter-Rater Agreement**: Selection and quality assessment must support independent evaluation by multiple reviewers. The system calculates Cohen's Kappa between reviewer pairs after independent assessments. If agreement is insufficient, the Think-Aloud technique discussion flow is triggered, followed by re-measurement and reporting of both pre- and post-discussion Kappa values.
- **Iterative Exclusion**: Studies are excluded in iterative stages — by title/abstract, then introduction/conclusions, then full-text — with removal only upon reviewer agreement.
- **Version Deduplication**: When both a conference paper and its journal version exist, only the most recent version is retained.

### Data Synthesis

Three synthesis approaches must be supported, selectable per study:

1. **Meta-Analysis**: Statistical combination of effect sizes from homogeneous studies. Supports fixed-effects (homogeneous) and random-effects (inhomogeneous) models. Includes Q-test / Likelihood Ratio test for heterogeneity, funnel plot generation for publication bias analysis, effect size extraction and normalization across studies.

2. **Descriptive Synthesis**: Tabulation of primary study data including: sample size per intervention, estimates of effect size with standard errors, mean differences between interventions, confidence intervals, and units of measurement. Generates Forest plots visualizing means and variance of differences between treatments per study.

3. **Qualitative Synthesis**: Supports multiple approaches:
   - Thematic analysis (identifying and reporting patterns/themes)
   - Narrative synthesis (evidence-based storytelling)
   - Comparative analysis (Boolean logic for causal connections)
   - Case survey (applying a structured question instrument to each primary study)
   - Meta-ethnography (translating and synthesizing conceptual interpretations)

A sensitivity analysis must be performed for any synthesis approach, evaluating result consistency across different study subsets.

### Phase 3: Reporting

- System generates a structured research report suitable for submission to academic journals and conferences.
- Report sections follow the SLR standard structure: background, review questions, protocol, search process, inclusion/exclusion decisions, quality assessment results, extracted data, synthesis results, validity discussion, recommendations.
- Export formats include the same options as the SMS workflow (JSON, CSV+JSON, Full Archive, SVG only) plus a LaTeX/Markdown structured report template.

---

## Key Differences from the SMS Workflow

| Dimension | SMS Workflow (002) | SLR Workflow (003) |
|---|---|---|
| Study type | Broad mapping | Focused empirical synthesis |
| Protocol | Informal/light | Formal, must be validated before search |
| Quality assessment | Not required | Mandatory, per-study checklists |
| Inter-rater agreement | Optional | Required; Cohen's Kappa reported |
| Data synthesis | Classification scheme, domain model | Meta-analysis, descriptive synthesis, or qualitative |
| Grey literature | Not tracked | Tracked to address publication bias |
| Visualizations | Bubble charts, domain model | Forest plots, funnel plots, plus inherited visualizations |

---

## Integration Points

- Reuses the existing Study, CandidatePaper, DataExtraction, Reviewer, PaperDecision, and AuditRecord entities from the SMS workflow.
- Adds new entities: `ReviewProtocol`, `QualityAssessmentChecklist`, `QualityAssessmentScore`, `SynthesisResult`, `InterRaterAgreementRecord`, `GreyLiteratureSource`.
- The New Study Wizard (`FR-006` in 002) already supports "Systematic Literature Review" as a study type; this feature implements the SLR-specific phases and logic behind that selection.
- Phase gates for SLR: Protocol must be validated (Phase 1) → Search executed (Phase 2) → Quality assessment complete → Data synthesis complete (Phase 3) → Report generated.

---

## Success Criteria

- A researcher can define and validate a full SLR protocol before conducting any search.
- The system calculates and displays Cohen's Kappa for any two reviewers who have independently assessed the same set of papers.
- At least one synthesis approach (meta-analysis, descriptive synthesis, or qualitative) can be executed end-to-end, producing a visualized or tabulated output.
- A Forest plot is generated for any study using descriptive synthesis with at least 3 accepted papers.
- The final report export includes all required SLR sections and is structured for academic publication submission.
