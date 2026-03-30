# Feature Specification: Rapid Review Workflow

**Feature Branch**: `008-rapid-review-workflow`
**Created**: 2026-03-21
**Status**: Draft
**Input**: User description: "number 8 rapid-review-workflow @docs/features/004-rapid-review-workflow.md"

## Out of Scope

- In-app conversion of a Rapid Review to an SLR or SMS study type.
- Practitioner platform accounts, login, or in-app collaboration for practitioners.
- Multi-page Evidence Briefing layouts (briefing is constrained to one page).

## Overview

Extend the research platform to support Rapid Reviews — systematic, time-bounded secondary
studies designed to provide actionable evidence to practitioners within days or weeks. Unlike
a full SLR or SMS, a Rapid Review trades comprehensiveness for speed while maintaining a
well-documented protocol. The feature introduces Rapid Review-specific planning, search,
appraisal, synthesis, and reporting capabilities alongside the existing SMS/SLR workflows.

## Clarifications

### Session 2026-03-21

- Q: What is the authorization scope for Rapid Review studies — who can view and edit them? → A: Study-team scoped (Option B): all users assigned to the study via the existing Reviewer model can view and edit. This pattern applies to all study workflows, not just Rapid Reviews.
- Q: Do practitioner stakeholders need platform accounts, or are they named contacts only? → A: Named contacts only (A + C) — researchers record name, role, and organisation; no platform login required. The researcher can additionally generate a shareable link to the Evidence Briefing so practitioners can view it without an account.
- Q: Can the protocol be edited after it reaches "validated" status? → A: Re-validation required (Option C) — any edit resets the protocol to "draft", gates the search phase until re-validation, and invalidates all previously collected papers.
- Q: How are Evidence Briefing regenerations handled — overwrite or versioned? → A: Explicit versioning (Option C) — each regeneration creates a new numbered version; the researcher manually promotes one version to "published"; the shareable link always serves the published version.
- Q: Can a Rapid Review be converted to a full SLR in-app? → A: Out of scope (Option A) — no conversion path; researcher creates a new SLR study manually if broader coverage is needed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Configure a Rapid Review Protocol (Priority: P1)

A researcher creates a new Rapid Review study and defines its protocol: the practical problem
motivating the review, the research questions framed around practitioner-actionable answers,
the time and effort budget, context restrictions, and the practitioner stakeholders involved.
The system guides the researcher through these fields, warns when research questions are
framed as research-gap questions (which belong in an SLR/SMS instead), and enforces that at
least one practitioner stakeholder is recorded.

**Why this priority**: Without a validated protocol the review cannot proceed. Protocol
creation is the foundational blocking step for all downstream phases.

**Independent Test**: A researcher can create a Rapid Review study, complete the protocol
form, add a practitioner stakeholder, and have the protocol reach "validated" status — all
without requiring search or synthesis functionality to be present.

**Acceptance Scenarios**:

1. **Given** a researcher is on the New Study page, **When** they select study type "Rapid
   Review" and complete setup, **Then** they are directed to a Rapid Review protocol editor
   with fields for: practical problem, research questions, time budget, effort budget, context
   restrictions, search strategy, inclusion/exclusion criteria, and planned dissemination
   medium.
2. **Given** a researcher enters a research question framed toward identifying research gaps
   (e.g., "What gaps exist in the literature on X?"), **When** they save or validate the
   protocol, **Then** the system surfaces a warning that the question style is more appropriate
   for an SLR/SMS and prompts them to reframe toward practitioner-actionable answers.
3. **Given** a researcher attempts to validate a protocol with no practitioner stakeholder
   defined, **When** they submit the validation request, **Then** the system blocks validation
   and surfaces an error: "At least one practitioner stakeholder must be identified."
4. **Given** a protocol with at least one practitioner stakeholder and well-formed research
   questions, **When** the researcher validates the protocol, **Then** the protocol status
   transitions to "validated" and Phase 2 (search) becomes accessible.

---

### User Story 2 - Conduct a Restricted Search and Select Papers (Priority: P2)

A researcher executes a search against a single database using optional restriction strategies
(year range, language, geography, study design type), selects papers for inclusion in
single-reviewer mode, and records any applied restriction as a documented threat to validity
that will automatically appear in the report.

**Why this priority**: Search and selection is the primary evidence-gathering phase. It
can be tested independently of synthesis and reporting once the protocol exists.

**Independent Test**: A researcher with a validated Rapid Review protocol can configure a
single-source search with at least one restriction applied, run the search, select papers
for inclusion, and confirm that the restriction is recorded as a documented threat — without
synthesis or reporting phases being implemented.

**Acceptance Scenarios**:

1. **Given** a validated Rapid Review protocol, **When** the researcher opens the search
   configuration, **Then** they can select a single database source without the system
   flagging it as a quality defect, provided they acknowledge the threat to validity.
2. **Given** a researcher configures the search with a year-range restriction
   (e.g., 2015–2025), **When** they save the configuration, **Then** the year-range
   restriction is recorded as a threat to validity in the protocol and will appear in the
   report's validity section.
3. **Given** an active Rapid Review study, **When** the researcher enables single-reviewer
   mode, **Then** the system displays a persistent warning that single-reviewer selection
   introduces selection bias and prompts recording this as a limitation before proceeding.
4. **Given** search results are available, **When** a researcher in single-reviewer mode
   marks a paper as included or excluded, **Then** the decision is recorded without requiring
   a second reviewer, and the selection bias warning remains visible on the page.
5. **Given** multiple restriction strategies are applied (e.g., year range + language),
   **When** the researcher views the protocol, **Then** each restriction appears as a separate
   threat-to-validity entry.

---

### User Story 3 - Quality Appraisal (Optional or Simplified) (Priority: P3)

A researcher either skips quality appraisal entirely or applies a simplified "peer-reviewed
venues only" filter. The chosen approach is recorded and automatically included in the
validity section of the final report.

**Why this priority**: Quality appraisal is optional in Rapid Reviews. Its behaviour is
simpler than full SLR quality appraisal and can be independently validated.

**Independent Test**: A researcher can open the quality appraisal step, choose "skip" or
"peer-reviewed only", and confirm that the approach is stored and visible in the protocol
validity section — independently of synthesis and reporting.

**Acceptance Scenarios**:

1. **Given** included papers awaiting appraisal, **When** the researcher chooses "Skip
   quality appraisal", **Then** all included papers advance to the synthesis phase and the
   protocol records "Quality appraisal: skipped" in its validity section.
2. **Given** included papers awaiting appraisal, **When** the researcher chooses
   "Peer-reviewed venues only", **Then** papers from non-peer-reviewed venues are
   automatically excluded, and the protocol records "Quality appraisal: peer-reviewed venues
   filter applied" in its validity section.
3. **Given** a Rapid Review with quality appraisal skipped, **When** the researcher views
   the protocol or evidence briefing, **Then** the omission of quality appraisal is
   prominently surfaced as a limitation — not hidden.

---

### User Story 4 - Narrative Synthesis (Priority: P2)

A researcher organises the findings from included papers into a structured narrative
synthesis, with one narrative section per research question. The system provides a structured
editor with AI-assisted drafting and organising of findings, framed in practitioner-friendly
language.

**Why this priority**: Narrative synthesis is the primary synthesis mode for Rapid Reviews
and directly feeds the Evidence Briefing. It shares priority with search because both are
needed for a complete end-to-end flow.

**Independent Test**: A researcher with included papers can open the narrative synthesis
editor, create at least one findings section mapped to a research question, and use AI
assistance to draft or organise content — without the Evidence Briefing generation being
implemented.

**Acceptance Scenarios**:

1. **Given** at least one included paper, **When** the researcher opens the synthesis step,
   **Then** the narrative synthesis editor presents one section per research question defined
   in the protocol.
2. **Given** a synthesis section for a research question, **When** the researcher invokes
   AI assistance, **Then** the system drafts a practitioner-friendly narrative summary of
   findings from the included papers for that question, which the researcher can accept,
   edit, or discard.
3. **Given** a completed narrative synthesis, **When** the researcher marks the synthesis
   as complete, **Then** the synthesis status is recorded and the Evidence Briefing
   generation step becomes accessible.

---

### User Story 5 - Generate and Export an Evidence Briefing (Priority: P1)

A researcher generates a one-page Evidence Briefing document from the completed Rapid Review,
structured per the standard template (title, summary, findings, target audience box, reference
to complementary material, institution logos). The Evidence Briefing is exportable as PDF and
HTML. A complementary material package (protocol + primary study list) is also generated.

**Why this priority**: The Evidence Briefing is the primary deliverable of a Rapid Review —
the reason the feature exists. It shares P1 priority with protocol creation.

**Independent Test**: A researcher with a completed synthesis can generate an Evidence
Briefing, review all required sections, and export it as PDF and HTML — without any prior
story's individual components needing to be re-tested.

**Acceptance Scenarios**:

1. **Given** a completed Rapid Review synthesis, **When** the researcher triggers Evidence
   Briefing generation, **Then** the system produces a document containing all six required
   sections: Title, Summary, Findings, Target Audience Box, Reference to Complementary
   Material, and Institution Logos fields.
2. **Given** an Evidence Briefing has been generated, **When** the researcher downloads it,
   **Then** both PDF and HTML export formats are available.
3. **Given** an Evidence Briefing with applied search restrictions or a skipped quality
   appraisal, **When** the briefing is generated, **Then** those decisions appear in the
   briefing's Target Audience Box or complementary material — never buried or omitted.
4. **Given** a completed Rapid Review, **When** the researcher generates the complementary
   material package, **Then** it includes the full protocol document and the primary study
   list, suitable for hosting alongside the Evidence Briefing.
5. **Given** an Evidence Briefing is exported as PDF, **When** the researcher opens the PDF,
   **Then** the document is one page and formatted for practitioner readability (no
   methodology jargon, no academic citations style).

---

### Edge Cases

- What happens when a researcher attempts to generate the Evidence Briefing before the
  narrative synthesis is complete?
- How does the system handle a search that returns zero results (empty result set)?
- What happens if the researcher removes the only practitioner stakeholder after the
  protocol has already been validated? (Per FR-005a, this edit resets the protocol to
  "draft" and invalidates collected papers; the researcher is warned before saving.)
- How does the system behave if the time budget expires during an active review?
- What happens when a context restriction (e.g., "small/medium companies only") excludes all
  search results?
- Can a Rapid Review be converted to a full SLR? **Out of scope** — no in-app conversion
  path exists. The researcher must create a new SLR study manually.

## Requirements *(mandatory)*

### Functional Requirements

#### Access Control

- **FR-000**: All Rapid Review study data (protocol, search configuration, papers, synthesis,
  Evidence Briefing) MUST be accessible only to users assigned to the study via the Reviewer
  model. Unauthenticated users and authenticated users not assigned to the study MUST be
  denied access. This access control pattern is consistent across all study workflow types
  (SMS, SLR, Rapid Review).

#### Phase 1: Protocol

- **FR-001**: System MUST provide a Rapid Review protocol editor with the following fields:
  practical problem description, research questions, time budget (days), effort budget
  (person-hours), context restrictions (company size, geography, development model),
  search strategy notes, inclusion/exclusion criteria, and planned dissemination medium.
- **FR-002**: System MUST enforce that at least one practitioner stakeholder is recorded
  before a Rapid Review protocol can reach "validated" status.
- **FR-003**: System MUST surface a warning when a research question is framed toward
  research-gap identification (e.g., keywords: "gap", "future work", "what is missing")
  rather than practitioner-actionable answers.
- **FR-004**: System MUST support recording qualitative problem-scoping material
  (interview notes, focus group summaries) when the practical problem is not yet
  well-defined at protocol creation time.
- **FR-005**: System MUST enforce the phase gate: no search phase is accessible until the
  protocol status is "validated".
- **FR-005a**: Any edit to a validated protocol MUST immediately reset its status to
  "draft", re-gate the search phase, and mark all previously collected papers as invalidated.
  The researcher MUST be shown a confirmation warning before the edit is saved, stating that
  previously collected papers will be invalidated and must be re-screened after re-validation.

#### Phase 2: Search and Selection

- **FR-006**: System MUST allow a Rapid Review to be configured with a single database
  source without treating the single-source choice as a quality defect, provided a
  threat-to-validity entry is recorded.
- **FR-007**: System MUST support the following search restriction strategies, each of
  which automatically generates a corresponding threat-to-validity entry in the protocol:
  (1) year range, (2) publication language, (3) geographic area, (4) study design type.
- **FR-008**: System MUST support single-reviewer mode for paper selection, quality
  appraisal, and data extraction. When single-reviewer mode is active, the system MUST
  display a persistent warning about selection bias and prompt the researcher to record it
  as a limitation.
- **FR-009**: System MUST allow context-specific restrictive inclusion/exclusion criteria
  (e.g., company size, team structure) without flagging them as quality defects, provided
  the context restriction is explained in the protocol.

#### Phase 3: Quality Appraisal

- **FR-010**: System MUST allow quality appraisal to be skipped entirely for a Rapid Review.
  When skipped, the protocol MUST record "Quality appraisal: skipped" as a validity entry.
- **FR-011**: System MUST support a simplified "peer-reviewed venues only" appraisal mode
  that automatically excludes papers from non-peer-reviewed venues. When applied, the
  protocol MUST record this as a validity entry.

#### Phase 4: Synthesis

- **FR-012**: System MUST provide a structured narrative synthesis editor with one section
  per research question as defined in the protocol.
- **FR-013**: System MUST provide AI-assisted drafting within the narrative synthesis editor,
  capable of producing practitioner-friendly summaries from included paper data for each
  research question section.
- **FR-014**: System MUST record synthesis completion status and gate Evidence Briefing
  generation on synthesis being marked complete.
- **FR-014a**: Each Evidence Briefing generation MUST produce a new numbered version
  (v1, v2, …). The researcher MUST explicitly promote a version to "published" status.
  Only the published version is accessible via the shareable link (FR-020). At most one
  version may be in "published" status at a time; promoting a new version automatically
  demotes the previous published version to read-only history.

#### Phase 5: Reporting

- **FR-015**: System MUST generate an Evidence Briefing document containing all six required
  sections: (1) Title, (2) Summary paragraph, (3) Findings per research question (with
  bullets, charts, tables as applicable), (4) Target Audience Box, (5) Reference to
  Complementary Material, (6) Institution Logos fields.
- **FR-016**: System MUST export the Evidence Briefing as both PDF and HTML formats.
- **FR-017**: Evidence Briefing content MUST be practitioner-facing — no methodology jargon
  or research gap framing in the generated text. Applied restrictions, skipped appraisals,
  and single-reviewer decisions MUST appear prominently in the Target Audience Box or
  validity notes, not be hidden.
- **FR-018**: System MUST generate a complementary material package containing the full
  protocol document and the primary study list.
- **FR-019**: System MUST export the full study data in the same formats as SMS/SLR exports
  (JSON, CSV, archive).
- **FR-020**: System MUST allow a study team member to generate a shareable, token-based
  link to a published Evidence Briefing. Accessing the link MUST NOT require the recipient
  to have a platform account. The link MUST be revocable by any study team member.

### Key Entities

- **RapidReviewProtocol**: Extends the base study protocol with fields for: time budget
  (days), effort budget (person-hours), context restrictions (structured list),
  dissemination medium, problem-scoping notes, and a collection of threat-to-validity
  entries (each linked to the restriction or decision that generated it). Lifecycle:
  `draft` → `validated`. Any edit to a validated protocol resets it to `draft`, gates the
  search phase, and invalidates all previously collected papers (which must be re-screened
  after re-validation).
- **PractitionerStakeholder**: Represents a practitioner involved in the review. Attributes:
  name, role/title, organisation, and involvement type (problem definer, advisor, recipient).
  Practitioners have no platform account and no system login. At least one MUST be associated
  with a Rapid Review before protocol validation.
- **EvidenceBriefing**: Represents a versioned output document. Each generation creates a
  new numbered version (v1, v2, …) containing all six required sections as structured fields,
  a generation timestamp, and a link back to the Rapid Review study. One version is
  designated "published" at any given time; only the published version is accessible via the
  shareable link. Prior versions are retained as read-only history. Lifecycle per version:
  `draft` → `published` (only one version may be published at a time).
- **ThreatToValidity**: A structured record automatically created when a search restriction,
  single-reviewer mode, or quality appraisal skip is applied. Contains: threat type, human-
  readable description, and linked decision. Surfaced in protocol, Evidence Briefing, and
  reports.
- **NarrativeSynthesisSection**: One section per research question in the narrative synthesis.
  Contains: research question reference, researcher-authored narrative text, AI-draft content
  (before acceptance), and completion status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A researcher can create a Rapid Review protocol, execute a search, select
  papers, and generate an Evidence Briefing end-to-end within a single working session
  (under 8 hours of actual research time, excluding waiting for search results).
- **SC-002**: All applied restrictions and methodology decisions (single source, single
  reviewer, skipped appraisal) appear automatically in the Evidence Briefing's validity
  section — with zero manual steps required from the researcher to surface them.
- **SC-003**: The Evidence Briefing generation step produces a complete, exportable document
  in both PDF and HTML within 60 seconds of the researcher triggering generation.
- **SC-004**: 100% of Evidence Briefings generated for a Rapid Review contain all six
  required structural sections; an incomplete briefing is never exported.
- **SC-005**: A researcher can complete Phase 1 (protocol validation with practitioner
  stakeholder) without any Phase 2–5 functionality being required.
- **SC-006**: The system rejects protocol validation for any Rapid Review missing at least
  one practitioner stakeholder in 100% of attempts.
- **SC-007**: AI-assisted narrative drafting produces at least a one-paragraph draft per
  research question section in under 30 seconds per section when included papers are
  available.

## Assumptions

- The existing Study entity already carries a `study_type` discriminator that includes
  "rapid_review"; no change to the study creation wizard is required beyond implementing
  the RR-specific phases and logic.
- The existing Reviewer, CandidatePaper, DataExtraction, and AuditRecord entities are
  reused without modification; RR-specific behaviour is additive.
- The existing phase gate mechanism (introduced in 007-slr-workflow) is extended to support
  the four Rapid Review phases.
- "Single-reviewer mode" is a per-study flag rather than a platform-wide setting.
- Institution logo fields in the Evidence Briefing accept image uploads (standard web image
  formats); logo placement and sizing follow a fixed template.
- The Evidence Briefing PDF is rendered from an HTML template and is expected to fit on a
  single A4/letter page using print CSS; complex multi-page layouts are out of scope for
  this feature.
- AI-assisted narrative drafting uses the same LLM infrastructure as existing agent
  services; no new provider integration is required.

## Dependencies

- **007-slr-workflow**: Phase gate mechanism, QualityChecklist infrastructure, and
  SynthesisResult ORM are dependencies or reference implementations.
- **006-database-search-and-retrieval**: Single-source search configuration builds on
  the existing `StudyDatabaseSelection` and `researcher-mcp` search infrastructure.
- **005-models-and-agents**: AI-assisted narrative drafting uses the existing `LLMClient`
  and agent prompt management infrastructure.
- **002-sms-workflow**: Study, CandidatePaper, DataExtraction, Reviewer, and AuditRecord
  entities are reused directly.
