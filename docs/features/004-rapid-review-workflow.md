# Feature: Rapid Review Workflow

**Feature ID**: 004-rapid-review-workflow
**Depends On**: 002-sms-workflow (existing SMS pipeline)
**Reference**: `docs/rapid-reviews.md`

---

## Overview

Extend the research platform to support Rapid Reviews. A Rapid Review is a secondary study designed to provide timely, actionable evidence to support practitioner decision-making within tight time and resource constraints. Unlike a full SLR or SMS, a Rapid Review trades comprehensiveness for speed while maintaining a systematic, documented protocol.

Rapid Reviews are:
- Bounded to a specific practical problem defined in close collaboration with practitioners
- Conducted within a practical context (days or weeks, not months)
- Reported through practitioner-friendly mediums (Evidence Briefings, not academic papers)
- Still systematic: a well-documented protocol is mandatory

Rapid Reviews are **not** ad-hoc literature reviews and are **not** an excuse for scientific non-rigor.

---

## Scope

### Phase 1: Planning

- **Problem Definition Support**: The system guides the researcher through defining the practical problem motivating the review. If the problem is not yet well-defined, the system supports qualitative problem-scoping activities (recording interview notes, focus group summaries).
- **Stakeholder Roles**: The protocol must identify the roles of researchers and practitioners. The system tracks these roles and enforces that at least one practitioner stakeholder is defined.
- **Research Questions**: Questions in Rapid Reviews must be framed around practitioner-actionable answers. The system provides templates for exploratory questions (e.g., "What strategies exist to address X? What is their effectiveness?") and warns when questions are framed toward research-gap identification (which belongs in an SLR/SMS instead).
- **Protocol Creation**: Same protocol structure as SLR (background, questions, search strategy, criteria, etc.) but with explicit fields for: time budget, effort budget, context restrictions (company size, geography, development model), and planned dissemination medium.

### Phase 2: Conducting the Review

- **Single Search Source**: Rapid Reviews may use a single database (e.g., Scopus) or a single search strategy rather than multiple. The system allows configuring a single-source search without flagging it as a quality issue, provided the threat is documented in the protocol.
- **Search Restriction Options**: The system supports the following search restriction strategies, all of which must be transparently documented as threats to validity when applied:
  1. Limit by publication year range
  2. Restrict to a specific publication language
  3. Focus on a specific geographic area
  4. Restrict to a single study design type (e.g., controlled experiments only, case studies only)
- **Single Reviewer Mode**: The system allows paper selection, quality appraisal, and data extraction to be performed by a single reviewer. When single-reviewer mode is active, the system warns that this introduces selection bias and prompts the researcher to document this as a limitation.
- **Optional Quality Appraisal**: Quality appraisal can be skipped entirely or simplified to a "peer-reviewed venues only" filter. The system records which approach was taken and includes it in the validity section of the report.
- **Narrative Synthesis**: The primary synthesis mode is narrative synthesis. The system provides a structured narrative synthesis editor where findings are organized by research question, with AI assistance in drafting and organizing the narrative.
- **Restrictive Inclusion/Exclusion Criteria**: Practitioners may define context-specific restrictive criteria (e.g., "studies must involve small/medium companies", "studies must not involve distributed teams"). The system supports this without treating it as a quality defect, provided the context restriction is explained.

### Phase 3: Reporting

- **Evidence Briefing Generator**: The primary output is a one-page Evidence Briefing document. The system generates an Evidence Briefing from the Rapid Review results, following the standard template structure:
  1. **Title**: Concise (1–2 lines)
  2. **Summary**: One paragraph ("This briefing reports scientific evidence on \<RESEARCH GOAL\>.")
  3. **Findings**: Main findings per research question, in short readable sentences, with bullets, charts, and tables. No research methodology details.
  4. **Target Audience Box**: Describes the intended audience, what is and is not included.
  5. **Reference to Complementary Material**: Link to the full protocol and primary study list.
  6. **Institution Logos**: Fields for institutional branding.
- **Export**: Evidence Briefing exported as PDF and HTML. Full protocol and study data exported in same formats as SMS/SLR (JSON, CSV, Archive). Complementary material package (protocol + primary study list) generated for hosting.

---

## Key Differences from SMS/SLR Workflows

| Dimension | SLR/SMS | Rapid Review |
|---|---|---|
| Problem framing | Research gap / knowledge aggregation | Practical problem bounded to context |
| Stakeholders | Researchers only | Researchers + practitioners (mandatory) |
| Time frame | Months to years | Days to weeks |
| Search sources | Multiple databases required | Single source allowed |
| Reviewers | Multi-reviewer (with Kappa) | Single reviewer allowed |
| Quality appraisal | Mandatory (SLR) / recommended | Optional or peer-review-only filter |
| Synthesis | Meta-analysis, descriptive, qualitative | Narrative synthesis (primary) |
| Output | Academic journal/conference paper | Evidence Briefing (one-page) + complementary material |

---

## Integration Points

- Reuses the existing Study, CandidatePaper, DataExtraction, Reviewer, and AuditRecord entities.
- Adds new entities: `RapidReviewProtocol` (with time/effort budget and context restriction fields), `PractitionerStakeholder`, `EvidenceBriefing`.
- The New Study Wizard already supports "Rapid Review" as a study type; this feature implements the RR-specific phases and logic.
- Phase gates for Rapid Review: Protocol validated (Phase 1) → Search executed with restrictions documented (Phase 2) → Narrative synthesis complete (Phase 3) → Evidence Briefing generated.

---

## Success Criteria

- A researcher can create and execute a complete Rapid Review using a single search source in single-reviewer mode.
- The system generates an Evidence Briefing document that includes all required sections (title, summary, findings, target audience box, reference, logos).
- All search restrictions and single-reviewer decisions are automatically surfaced in the protocol's threats-to-validity section.
- The Evidence Briefing is exportable as both PDF and HTML.
- A researcher can complete a Rapid Review from protocol creation to Evidence Briefing generation within the configured time budget.
