# Feature Specification: Systematic Mapping Study Workflow System

**Feature Branch**: `002-sms-workflow`
**Created**: 2026-03-10
**Last Updated**: 2026-03-11
**Status**: Active
**Input**: User description: "analyze docs/systematic-mapping-studies.md to create a specification to implement the described process and UI"
**Constitution**: Aligned to v1.4.0 (Principles I–IX)

---

## Clarifications

### Session 2026-03-10

- Q: When the system executes a full search or batch data extraction (multi-minute operations), how should the UI behave? → A: Async background job — user sees a live progress dashboard (phase, papers found, % complete) and can navigate away; results appear when done.
- Q: Should study phases be enforced as a strict linear sequence, or can researchers access phases freely? → A: Guided sequence with soft gates — phases unlock progressively based on prior phase completion, but researchers can re-enter and edit any previously completed phase.
- Q: Should the second-reviewer role be human, AI, or configurable? → A: Configurable per study — each study can have any number of reviewers (human team members or AI agents) assigned to evaluate papers and extractions; not limited to exactly two reviewers.
- Q: What study data export formats should be supported? → A: Researcher chooses at export time from four options: SVG Only (visualizations), JSON Only (structured study data), CSV + JSON (tabular + structured data), or Full Study Archive (JSON + SVGs + audit log in a single downloadable bundle).
- Q: How should concurrent edits by two researchers on the same paper decision or extraction be handled? → A: Optimistic locking — the second concurrent save triggers a conflict notification with a diff view; the researcher chooses to keep theirs, keep the other's, or merge.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Researcher Creates and Scopes a New Study (Priority: P1)

A researcher logs in, selects or creates a research group, then launches the New Study Wizard to define a Systematic Mapping Study. They provide a name, study type, research objectives, research questions, and motivation. They also invite collaborators from the research group. The wizard guides them through the PICO(C) framework to formulate precise, answerable research questions, with AI-assisted refinement available at each step.

**Why this priority**: Without a study being properly scoped and created, no subsequent phases can proceed. This is the entry point for the entire workflow.

**Independent Test**: A researcher can create a complete study with a name, study type, research objectives, research questions, and PICO(C) components, save it, and see it appear in the studies list — without performing any search or data extraction.

**Acceptance Scenarios**:

1. **Given** a logged-in researcher with research group access, **When** they navigate to the studies list and click "New Study", **Then** the New Study Wizard opens and walks them through: study name, study type selection, member assignment, motivation, research objectives, and research questions.
2. **Given** the researcher is on the PICO(C) step, **When** they enter Population, Intervention, Comparison, Outcome, and Context values, **Then** the system provides AI-assisted suggestions to refine each component and allows PICO variation selection (PICOS, PICOT, SPIDER, PCC).
3. **Given** the researcher completes the wizard, **When** they submit the form, **Then** the study is saved to the database with all metadata, is visible in the research group's studies list, and shows current progress status.
4. **Given** the wizard is in progress, **When** the researcher adds known seed papers or known authors, **Then** those are persisted as part of the study's initial data for use in Phase 2.

---

### User Story 2 - Researcher Builds and Evaluates a Search String (Priority: P2)

A researcher working in Phase 2 uses the system to develop a search string based on the study's PICO(C) components and keywords extracted from seed papers. They iterate on the search string, testing it against known key papers (the test set) and refining until the comparison results are satisfactory.

**Why this priority**: The quality of the search string determines the quality of all papers found. This iterative refinement loop (test-retest) is central to academic rigor.

**Independent Test**: A researcher can enter PICO(C) components, generate a search string, execute it against at least one configured index, compare results against a known test set, and save a refined search string — independent of data extraction or reporting phases.

**Acceptance Scenarios**:

1. **Given** a study with PICO(C) defined and at least one seed paper, **When** the researcher opens Phase 2, **Then** the system generates an initial search string using PICO(C) terms, keywords from seed papers, and synonym/thesaurus expansion.
2. **Given** the researcher has a search string, **When** they run the test search, **Then** the system executes the string against selected research indices and returns a result set.
3. **Given** a result set and a test set of known papers, **When** the comparison is run, **Then** the system shows how many test-set papers were found, how many were missed, and the total result set size, with expert AI judgement on adequacy.
4. **Given** the comparison results are inadequate, **When** the researcher refines the search string and reruns, **Then** the system logs each iteration of the test-retest cycle with timestamps and changes made.
5. **Given** the search string is deemed adequate, **When** the researcher saves it, **Then** it is stored as the study's official search string, locked for the record, and used for the full search execution.

---

### User Story 3 - System Executes Full Paper Search with Snowball Sampling (Priority: P3)

Once the search string is finalized, the system executes it across all configured research databases, collects candidate papers, applies inclusion/exclusion criteria with AI evaluation, and then performs iterative backward and forward snowball sampling on accepted papers until the snowball threshold is reached.

**Why this priority**: This is the core automated data collection phase. The funnel of papers produced here feeds all downstream analysis.

**Independent Test**: Given a finalized search string and inclusion/exclusion criteria, the system can execute a full search across at least one database, produce a deduplicated list of papers with accept/reject/duplicate decisions, and complete one round of snowball sampling — delivering a visible candidate paper list.

**Acceptance Scenarios**:

1. **Given** a finalized search string, **When** the researcher triggers the full search, **Then** the system queries each configured database index in parallel, collects all results, and deduplicates them before adding to the candidate queue.
2. **Given** a candidate paper, **When** it is evaluated, **Then** the system checks each inclusion criterion and each exclusion criterion, and assigns status: Accepted (A), Rejected (R), or Duplicate (D) — with reason(s) logged per decision.
3. **Given** a paper is Accepted in round 1, **When** snowball sampling begins, **Then** the system initiates backward snowballing (from the paper's references) and forward snowballing (from papers citing it) in parallel, tagging found papers as `backward-search-1` or `forward-search-1`.
4. **Given** a snowball round is complete, **When** the number of non-duplicate new papers found is below the configured threshold (default: 5), **Then** snowball sampling stops and the final candidate set is frozen.
5. **Given** the full search is complete, **When** the researcher views search metrics, **Then** they see: total papers identified, accepted, rejected, duplicate — per phase/round.

---

### User Story 4 - Researcher Reviews and Overrides Paper Decisions (Priority: P3)

A researcher can review the AI-generated accept/reject/duplicate decisions for any paper, view the reasoning, override the decision if needed, and add their own notes. A second reviewer can independently evaluate, and the system flags disagreements for resolution.

**Why this priority**: Academic rigor requires human oversight of AI decisions, especially for borderline cases and dual-reviewer validation.

**Independent Test**: A researcher can open any candidate paper, view the AI decision and reasoning, override the decision with a new status and justification, and save — with the change logged and visible in audit history.

**Acceptance Scenarios**:

1. **Given** a paper with an AI-assigned decision, **When** the researcher opens the paper detail view, **Then** they see the paper metadata, the AI decision, the reasoning behind it, and buttons to accept, reject, or mark as duplicate.
2. **Given** a researcher overrides a decision, **When** they save, **Then** the original AI decision and the override are both logged with timestamps and the reviewer's identity.
3. **Given** two reviewers have both evaluated the same paper with different decisions, **When** the system detects the disagreement, **Then** it flags the paper for resolution and notifies both reviewers.

---

### User Story 5 - System Extracts and Classifies Data from Accepted Papers (Priority: P4)

For each accepted paper, an AI agent extracts: research type, venue type, author information, institution/locale, a structured summary, open-coded keywords/themes, and data relevant to the study's research questions. A second AI agent validates the extraction, and a human researcher can review and adjust the results.

**Why this priority**: Data extraction is the direct input to the classification scheme, domain model, and all output visualizations.

**Independent Test**: Given one accepted paper, the system can extract and save all required data fields (research type, venue type, author info, summary, keywords) and display them on the paper's detail page — without requiring the domain model or visualizations to be built yet.

**Acceptance Scenarios**:

1. **Given** a paper marked Accepted, **When** data extraction is triggered, **Then** the system extracts: research type (Evaluation Research, Proposal of Solution, Validation Research, Philosophical, Opinion, Personal Experience), venue type, venue name, authors with institution and locale, a structured summary, and open-coded keywords.
2. **Given** the primary extraction is complete, **When** the second validator agent reviews it, **Then** any disagreements between the two agents are flagged and surfaced to a human reviewer.
3. **Given** a researcher reviews extracted data, **When** they edit a field and save, **Then** the change is persisted with a reviewer annotation and the original AI value is preserved in the audit log.
4. **Given** the study has research questions defined, **When** data is extracted, **Then** the system also extracts specific answers or data points relevant to each research question, mapping them to the question by ID.

---

### User Story 6 - System Generates Visualizations and Study Report (Priority: P5)

Once data extraction is complete, the system produces publication-ready visualizations including: frequency of publication (infographic), publications per year (bar chart), venues, research locale, key authors, keyword bubble maps, and a domain model in UML notation.

**Why this priority**: This is the final deliverable of the mapping study — the outputs researchers and their audience will use.

**Independent Test**: Given at least 5 papers with extracted data, the researcher can navigate to the Results section and view at least a publications-per-year bar chart and a keyword frequency bubble map rendered as SVG.

**Acceptance Scenarios**:

1. **Given** extracted data from accepted papers, **When** the researcher navigates to the Results section, **Then** the system displays: publications per year (bar chart), venues (table/chart), research locale (map or chart), key authors (ranked list), and keyword bubble map.
2. **Given** the classification scheme is generated, **When** the researcher views it, **Then** bubble charts classifying research by venue, author, locale, institute, year, subtopic, research type, and research method are displayed as exportable SVG files.
3. **Given** the domain model is generated, **When** the researcher views it, **Then** a UML class/concept diagram representing key concepts and their relationships across the body of papers is displayed.

---

### User Story 7 - AI Quality Evaluation Judge Assesses Study (Priority: P5)

An LLM-as-a-Judge agent evaluates the current state of the study against the five-phase quality rubrics and produces a quality score per rubric, a total score, and a prioritized list of improvement recommendations that the researcher can act upon.

**Why this priority**: Study quality assessment closes the loop on academic rigor, helping researchers identify and fix gaps before publishing.

**Independent Test**: Given a study with at least Phase 1 and Phase 2 data, the quality judge can generate a rubric-based score report showing scores for "Need for Review", "Choosing the search strategy", "Evaluation of the search", "Extraction and classification", and "Study validity" — with specific improvement suggestions.

**Acceptance Scenarios**:

1. **Given** a study with some completed phases, **When** the researcher runs the quality evaluation, **Then** the system produces a score for each rubric (Need for Review 0-2, Search Strategy 0-2, Search Evaluation 0-3, Extraction & Classification 0-3, Study Validity 0-1) with specific justification per score.
2. **Given** the quality report is generated, **When** the researcher reviews it, **Then** they see a prioritized list of recommended actions to improve each rubric score, each actionable within the system.
3. **Given** the researcher addresses a recommendation (e.g., adds a second search strategy), **When** they re-run the quality evaluation, **Then** the updated score reflects the improvement.

---

### Edge Cases

- What happens when a paper's full text is unavailable for extraction — the system must fall back to abstract-only extraction and flag the paper accordingly?
- How does the system handle papers that appear in multiple database search results — deduplication must use DOI, title similarity, and author matching, with human review flagged for uncertain duplicates?
- What happens when a snowball round returns papers already in the candidate set — they are marked as duplicates for that round without reprocessing?
- How does the system handle a search string that returns zero results from a configured database — it logs the empty result with an error/warning and continues with other databases?
- What happens when a configured research database is unreachable — the search phase logs the failure per database and allows the researcher to retry that database independently?
- How are conflicting research type classifications handled (e.g., paper fits both Evaluation Research and Personal Experience) — the system applies the decision rules R1–R6 in order and selects the first matching rule, flagging conflicts for human review?
- What happens when two researchers concurrently save changes to the same paper decision or extraction field — the second save triggers a conflict notification with a diff view; the researcher must resolve by keeping their version, keeping the other, or merging before the save completes.
- What happens when the study has no seed papers (test set is empty) — the test-retest evaluation step is skipped or marked as incomplete, with a quality rubric deduction noted?

---

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Authorization

- **FR-001**: System MUST provide a login page where users authenticate with email and password, with session persistence across browser navigations.
- **FR-002**: System MUST redirect unauthenticated users attempting to access any page to the login page.
- **FR-003**: System MUST support Research Groups, where a group has one or more members and one or more admins.
- **FR-004**: System MUST allow research group admins to invite, remove, and assign roles to group members.
- **FR-005**: System MUST support study-level permissions, where only assigned study members can view and modify a study.

#### Study Management

- **FR-006**: System MUST provide a New Study Wizard that collects: study name, study type (Systematic Mapping Study, Systematic Literature Review, Rapid Review, Tertiary Study), assigned members, motivation, research objectives, research questions, and reviewer configuration (one or more human members and/or AI agents to serve as reviewers for paper decisions and data extraction).
- **FR-007**: System MUST allow users with appropriate permissions to archive or delete a study from the studies list.
- **FR-008**: System MUST display each study's name, topic, study type, and current phase/progress in the studies list.
- **FR-008a**: System MUST enforce soft phase gates: Phase 2 is unlocked only after PICO(C) is saved; Phase 3 is unlocked only after a full search is executed; Phases 4–5 are unlocked only after data extraction has been initiated. All previously unlocked phases remain editable.
- **FR-009**: System MUST persist study ownership to the creating research group.

#### Phase 1: Need for Map

- **FR-010**: System MUST allow users to define and edit PICO(C) components for a study, supporting variants: PICO, PICOS, PICOT, SPIDER, PCC.
- **FR-011**: System MUST provide AI-assisted refinement of each PICO(C) component based on the study's topic and research questions.
- **FR-012**: System MUST allow users to add seed papers (known key papers) and seed authors to a study as the initial test set.
- **FR-013**: System MUST provide a "Librarian" AI agent that suggests key papers and key authors relevant to the study topic. *(Research group discovery is out of scope for this iteration.)*
- **FR-014**: System MUST provide an "Expert" AI agent that identifies a small set of 10–20 papers highly relevant to the research topic without hallucination.

#### Phase 2: Study Identification

- **FR-015**: System MUST generate a search string from the study's PICO(C) components and keywords extracted from seed papers.
- **FR-016**: System MUST allow AI-assisted expansion of the search string using synonyms, thesaurus entries, standards, and encyclopedia terms.
- **FR-017**: System MUST support executing the search string against configured research databases (ACM Digital Library, IEEExplore, Web of Science, Scopus, ScienceDirect, Google Scholar).
- **FR-018**: System MUST support configuring inclusion and exclusion criteria for a study, where any exclusion criterion met immediately rejects a paper.
- **FR-019**: System MUST evaluate each candidate paper against inclusion/exclusion criteria using an AI agent and assign status: Accepted (A), Rejected (R), or Duplicate (D), with logged reasons.
- **FR-020**: System MUST allow researchers to view, override, and annotate any AI-generated paper decision, with full audit log of original and override decisions.
- **FR-021**: System MUST support a configurable multi-reviewer workflow where each study can have any number of reviewers (human team members or AI agents) assigned. Each reviewer independently evaluates papers and extractions. The system MUST flag papers where reviewer decisions disagree and surface them for resolution. There is no fixed limit of two reviewers; studies may configure one or many.
- **FR-022**: System MUST support iterative test-retest search string refinement by comparing result sets against the test set and logging each iteration.
- **FR-023**: System MUST execute backward snowball sampling on accepted papers using their reference lists.
- **FR-024**: System MUST execute forward snowball sampling on accepted papers using their citation lists.
- **FR-025**: System MUST tag each paper with the search phase/round in which it was found (e.g., `initial-search`, `backward-search-1`, `forward-search-2`).
- **FR-026**: System MUST stop snowball sampling when a round produces fewer non-duplicate papers than a configurable threshold (default: 5).
- **FR-027**: System MUST track and display search metrics per phase: total identified, accepted, rejected, duplicates.
- **FR-027a**: System MUST execute full database searches and batch data extraction as async background jobs, providing a live progress dashboard showing current phase, papers found so far, and percentage complete. Users MUST be able to navigate away from the progress view and return to it; results MUST be available when the job completes.
- **FR-028**: System MUST support web-scraping-based search as an alternative to database search, using PICO(C) criteria to assess relevance. *(Deferred: the underlying MCP scraper tools are implemented in this iteration (T061–T062); the full search-mode API endpoint, ARQ job variant, and frontend UI are planned for a subsequent iteration. FR-028 is partially satisfied.)*

#### Phase 3: Data Extraction & Classification

- **FR-029**: System MUST extract the following for each accepted paper: research type (using decision rules R1–R6), venue type (per the Venue Type Classification), venue name, author names, author institutions, author locales, a structured summary, open-coded keywords/themes, and data relevant to each study research question.
- **FR-030**: System MUST classify research type using decision rules R1–R6 in order, flagging conflicts for human review.
- **FR-031**: System MUST apply the study's configured reviewer set (human and/or AI) to validate each extraction. Disagreements across any reviewers MUST be flagged for resolution. Reviewer composition is configured per study, not hardcoded.
- **FR-032**: System MUST allow researchers to edit any extracted field and log the change with the original AI value preserved.
- **FR-043**: System MUST use optimistic locking for concurrent edits to paper decisions and extraction fields. When a conflict is detected, the system MUST present the conflicting researcher with a diff view showing both versions and require them to resolve the conflict (keep theirs, keep the other's, or merge) before the save completes. No silent overwrites are permitted.
- **FR-033**: System MUST generate a domain model (UML concept diagram) from the open coding, keywords, relationships, and summaries of accepted papers.
- **FR-034**: System MUST generate a classification scheme with bubble charts classifying research by: venue, author, locale, institution, year, area/subtopic, research type, and research method.
- **FR-035**: System MUST export all visualizations as publication-ready SVG files. *(The "SVG Only" format in FR-042 is the export mechanism that satisfies this requirement; FR-035 and FR-042 SVG Only are complementary.)*

#### Phase 4: Validity Discussion

- **FR-036**: System MUST provide a Validity Discussion section where researchers can document threats to: descriptive validity, theoretical validity, generalizability (internal and external), interpretive validity, and repeatability.
- **FR-037**: System MUST pre-populate validity discussion sections with AI-generated content based on the study's process and decisions made.

#### Phase 5: Quality Evaluation

- **FR-038**: System MUST implement an LLM-as-a-Judge agent that evaluates the study against all five quality rubrics and produces a score for each.
- **FR-039**: System MUST provide the judge's output as a scored report with justification per rubric and a prioritized list of improvement actions.
- **FR-040**: System MUST allow re-running the quality evaluation at any time to reflect updates.

#### Audit Trail & Operational Visibility

- **FR-044**: System MUST maintain a complete, immutable audit log of all study-level data
  mutations — including PICO(C) edits, search string changes, inclusion/exclusion criteria
  changes, study metadata edits, seed paper/author additions and removals, and paper decision
  overrides — capturing: actor identity, timestamp, the entity and field changed, and the
  before/after values. Study admins MUST be able to view the full audit log for their study
  from the study administration view.
  *Note: Data extraction field edits are tracked separately by the `ExtractionFieldAudit`
  entity (which preserves the original AI value for potential restoration). Extraction edits
  are therefore excluded from the general `AuditRecord` audit log to avoid data duplication.*
- **FR-045**: System MUST provide an administrative status dashboard showing the real-time
  health of all system services (data storage, background job processing, external search
  connections). The dashboard MUST allow an administrator to view details of any failed
  background job and trigger a retry without requiring direct access to the underlying
  infrastructure.
- **FR-046**: System MUST NOT expose secrets, API keys, database credentials, or security
  tokens through any user-visible interface, error message, log output visible to end users,
  or exported artefact. All sensitive configuration MUST be managed externally from the
  application codebase.

#### Results & Reporting

- **FR-041**: System MUST generate the following output visualizations: frequency of publication infographic, publications per year bar chart, venues of publication, research locale, key authors, keyword bubble map, and domain model.
- **FR-042**: System MUST provide an export function that allows researchers to choose from the following export formats at export time:
  - **SVG Only**: All generated visualizations as SVG files suitable for academic publication.
  - **JSON Only**: Full structured study data (candidate papers, decisions, extracted fields, search metrics, audit trail) in JSON format.
  - **CSV + JSON**: Tabular export of candidate papers and decisions (CSV) plus full structured data (JSON).
  - **Full Study Archive**: A single downloadable bundle containing all of the above (JSON, SVGs, and complete audit log) for full study replication and archival.

### Key Entities

- **User**: A registered individual with profile, credentials, and membership in one or more research groups.
- **ResearchGroup**: A named group of users, with at least one admin. Owns studies.
- **Study**: A named research study of a specific type, owned by a research group, with lifecycle phases (1–5), assigned members, and all study data (PICO, search string, criteria, papers, extractions). Phases unlock progressively: Phase 1 always accessible; Phase 2 unlocks when PICO(C) is saved; Phase 3 unlocks when the full search is complete; Phases 4–5 unlock when data extraction is complete. Previously completed phases remain editable at any time.
- **PICOComponent**: A structured set of PICO(C) values (Population, Intervention, Comparison, Outcome, Context) associated with a study, including the variant used.
- **SeedPaper**: A known key paper provided at study creation to serve as the test set for search string evaluation.
- **SeedAuthor**: A known key author provided to seed the study's search strategy.
- **InclusionCriterion / ExclusionCriterion**: Named criteria with description, associated with a study, used to evaluate candidate papers.
- **SearchString**: A versioned search string associated with a study, with history of test-retest iterations and comparison results.
- **CandidatePaper**: A paper found during any search phase, with metadata (title, authors, abstract, DOI, venue, year), current decision status (A/R/D), reasons, and search phase tag.
- **Reviewer**: A configured reviewer for a study — either a human study member or a named AI agent. Each study has a set of reviewers that evaluate papers and extractions. Configurable at study setup and editable by study admins.
- **PaperDecision**: An audit log entry capturing a decision (AI or human) on a candidate paper, with timestamp, reviewer identity, status, and rationale. Multiple decisions per paper are expected when multiple reviewers are configured.
- **DataExtraction**: Structured extraction data for an accepted paper, including research type, venue type, authors, summary, keywords, and question-specific data.
- **DomainModel**: A UML concept diagram generated from extracted paper data, stored as structured data and rendered as SVG.
- **ClassificationScheme**: A set of bubble chart definitions generated from extracted data, rendered as SVG.
- **QualityReport**: A rubric-based evaluation of a study at a point in time, with scores and improvement recommendations.
- **SearchMetrics**: Aggregate counts (identified, accepted, rejected, duplicates) per search phase/round for a study.

### Non-Functional Requirements

- **NFR-001**: Every persistent study entity MUST carry a creation timestamp and a
  last-modification timestamp. These are system-managed fields — researchers MUST NOT be
  able to alter them, and they MUST be reflected accurately in exported artefacts.
- **NFR-002**: All study data modifications MUST be captured in an immutable audit record.
  Silent overwrites of any study data are prohibited; every change MUST be attributable to
  an actor and a moment in time. Extraction field edits are specifically tracked via
  `ExtractionFieldAudit`; all other study-level mutations are tracked via `AuditRecord`
  (see FR-044). These two mechanisms are complementary and non-overlapping.
- **NFR-003**: All sensitive credentials required to operate the system (database access,
  external search API keys, token-signing secrets) MUST be managed outside of any
  application artefact or exported study bundle. Exposure of operational secrets through
  any user-facing channel is a critical defect.
- **NFR-004**: The system MUST be deployable as a set of independently health-checked
  services. Each service MUST report its own readiness status; dependent services MUST
  wait for their dependencies to be healthy before accepting traffic.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A researcher can complete the New Study Wizard (Phase 1, including PICO(C) definition) in under 15 minutes from login for a well-understood research topic.
- **SC-002**: The AI-generated search string, when tested against a known test set of 10 seed papers, recalls at least 80% of those papers in the initial result set without manual tuning.
- **SC-003**: Paper inclusion/exclusion decisions made by the AI agent agree with human reviewer decisions at a rate of at least 85% on a representative sample.
- **SC-004**: The full search pipeline (initial search + one round of snowball sampling) for a study with up to 500 candidate papers completes without user intervention, producing a fully classified candidate list.
- **SC-005**: Researchers can view the complete audit trail for any paper decision (original AI decision, any overrides, timestamps) within 2 clicks from the paper's detail view.
- **SC-006**: Data extraction fields for an accepted paper are populated by the AI agent within 60 seconds of triggering extraction for a paper with accessible full text.
- **SC-007**: The system generates all required result visualizations — publication frequency infographic, publications-per-year bar chart, venues, research locale, key authors, keyword bubble map, 8 classification scheme bubble charts, and the domain model — and makes them available as downloadable SVG files within 2 minutes of requesting the results report.
- **SC-008**: All generated visualizations export as valid, publication-ready SVG files that render correctly in standard vector graphics software.
- **SC-009**: The quality judge produces a complete rubric score report with improvement actions within 90 seconds of being triggered.
- **SC-010**: The system supports at least 5 concurrent users working on independent studies within the same research group without data conflicts or performance degradation.
- **SC-011**: A system administrator can view the real-time health of all dependent services and retry any failed background job from the administrative dashboard, without direct access to the underlying infrastructure.
- **SC-012**: The complete audit log for a study — including all PICO edits, search string iterations, and extraction field changes — is accessible to a study admin within 2 clicks from the study administration view and renders within 3 seconds for studies with up to 500 logged events.

---

## Assumptions

- The system integrates with external research databases (ACM, IEEExplore, Scopus, etc.) via MCP tools (researcher-mcp) or external MCPs; the availability and API terms of those services are assumed to be handled outside this spec.
- Full-text PDF retrieval for data extraction is assumed to be available for at least a subset of accepted papers; the system gracefully degrades to abstract-only extraction when full text is unavailable.
- The AI agents used for search string refinement, inclusion/exclusion evaluation, and data extraction are assumed to have access to the relevant paper metadata and abstract text.
- The "Librarian" and "Expert" agents are assumed to be LLM-backed agents that can reason over a topic description and return grounded suggestions; hallucination mitigation is the responsibility of those agents' implementations.
- User authentication uses standard session-based auth with secure credential storage; OAuth or SSO integration is out of scope for this feature.
- Multi-language paper support is out of scope; all papers must be in English (consistent with standard inclusion criteria examples in the domain document).
- The New Study Wizard and all study management pages are designed for desktop/laptop browser use; mobile responsiveness is a nice-to-have, not a requirement.
- The implementation follows the project's approved technology stack and toolchain conventions as defined in the project constitution; this specification intentionally avoids enumerating specific frameworks, libraries, or infrastructure tools so that it remains technology-agnostic at the requirements level.
- All sensitive operational configuration (database credentials, external API keys, security tokens) is managed as environment variables outside of application code; no secrets are stored in the repository or included in exported study artefacts.
