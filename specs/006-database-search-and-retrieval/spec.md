# Feature Specification: Database Search, Retrieval & Paper Processing

**Feature Branch**: `006-database-search-and-retrieval`
**Created**: 2026-03-17
**Status**: Draft
**Input**: User description: "number 6 database-search-and-retrieval @docs/features/010-database-search-and-retrieval.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure and Execute Multi-Database Search (Priority: P1)

A researcher creating or managing a systematic study needs to choose which academic databases to search. They open their study's search settings, select from available database indices grouped by type (primary databases, general indices, supplementary), and run a search query. Results from all selected sources are merged and deduplicated into a single unified list.

**Why this priority**: Searching multiple academic databases in parallel and merging results is the core value of the system — without this, no study can progress beyond the search phase.

**Independent Test**: Can be fully tested by creating a study, selecting at least two database indices, running a keyword search, and verifying a deduplicated merged result set is returned — delivering immediate value as a working multi-database search tool.

**Acceptance Scenarios**:

1. **Given** a study with IEEExplore and Scopus selected, **When** the researcher runs a keyword search, **Then** results from both sources are returned in a single merged list with duplicates removed.
2. **Given** a database index that requires an API key not yet configured, **When** the researcher views the index in the selection panel, **Then** a visible warning badge indicates the missing credential.
3. **Given** a study, **When** the researcher selects database indices and saves, **Then** the selection persists and is reused on the next search.
4. **Given** a search across multiple databases, **When** one database is temporarily unreachable, **Then** results from the remaining databases are returned along with a status message identifying the failed source.

---

### User Story 2 - Retrieve Full-Text Papers (Priority: P2)

After screening candidate papers, a researcher initiates full-text retrieval for accepted papers. The system attempts to obtain the full PDF via open-access channels first (Unpaywall), falling back to other configured methods. The researcher can optionally enable SciHub retrieval for papers unavailable via open access, after explicitly acknowledging a legal disclaimer.

**Why this priority**: Full-text retrieval is required for the data extraction phase — without it, AI-assisted extraction agents cannot process paper content beyond abstracts.

**Independent Test**: Can be tested independently by taking a paper with a known DOI and running full-text retrieval, verifying that a PDF is returned from an open-access source without any SciHub involvement.

**Acceptance Scenarios**:

1. **Given** a paper with a DOI available through open access, **When** full-text retrieval is triggered, **Then** the PDF is obtained via the open-access channel and stored against the paper record.
2. **Given** a paper not available through open access, **When** the researcher has not enabled SciHub for the study, **Then** the paper is marked as unavailable with a clear status, and no attempt is made via SciHub.
3. **Given** a researcher wishing to enable SciHub, **When** they attempt to enable it, **Then** an explicit acknowledgment dialog is shown before the option can be activated; the option is only available if the server operator has enabled it.
4. **Given** SciHub is disabled at the server level, **When** a client attempts to request SciHub retrieval, **Then** a clear error is returned and no SciHub request is made.

---

### User Story 3 - Search Citation and Reference Networks (Priority: P3)

A researcher conducting snowball sampling needs to find papers that cite or are cited by a known paper. They provide a paper identifier and the system returns structured lists of citing papers and referenced papers, enabling forward and backward citation tracing.

**Why this priority**: Citation network traversal (snowball sampling) is a standard systematic review technique that substantially expands result coverage beyond keyword search alone.

**Independent Test**: Can be tested by providing a DOI for a well-cited paper and verifying that both a reference list and a citation list are returned with structured paper metadata.

**Acceptance Scenarios**:

1. **Given** a paper with a known DOI, **When** a reference lookup is requested, **Then** a structured list of papers referenced by that paper is returned, each with at minimum a title and DOI where available.
2. **Given** a paper with a known DOI, **When** a citation lookup is requested, **Then** a structured list of papers that cite that paper is returned.
3. **Given** a DOI not found in the citation data source, **Then** an empty list is returned along with a status indicating the paper was not found (not an error).

---

### User Story 4 - Convert Retrieved Papers to Readable Text (Priority: P4)

After retrieving a paper's PDF, the system converts it to structured plain text. This converted content is stored against the paper record and is used by downstream AI agents for study screening and data extraction. The researcher can also trigger OCR for scanned or image-based PDFs that cannot be converted by standard means.

**Why this priority**: AI agents cannot reliably process raw binary PDFs — structured text conversion is a prerequisite for automated screening and extraction.

**Independent Test**: Can be tested independently by supplying a PDF and verifying that readable plain text is produced and stored against the paper record.

**Acceptance Scenarios**:

1. **Given** a paper whose PDF has been retrieved, **When** text conversion is triggered, **Then** the paper's plain text content is extracted and stored, and downstream agents use this text rather than the raw PDF.
2. **Given** a scanned PDF with no extractable text layer, **When** OCR-assisted conversion is requested, **Then** the system uses an optical text recognition process and returns text content with a note indicating OCR was used.
3. **Given** converted text already stored for a paper, **When** a retrieval request is made, **Then** the stored text is returned without re-running conversion.

---

### User Story 5 - Manage Academic Database Credentials (Priority: P5)

An administrator needs to configure API keys and credentials for subscription-gated academic databases. They can add, update, and test credentials for each integration from a central administration panel without needing to modify server configuration files.

**Why this priority**: Without valid credentials, subscription-gated databases cannot be searched. Administrator credential management reduces operational friction and removes the need for server restarts when updating keys.

**Independent Test**: Can be tested by adding a new credential for a database integration via the admin panel, then running a connectivity test that confirms the credential is accepted by the remote service.

**Acceptance Scenarios**:

1. **Given** an administrator in the credential management section, **When** they enter an API key for a database integration and save it, **Then** the key is stored securely and the integration status updates to "configured".
2. **Given** a configured credential, **When** the administrator triggers a connectivity test, **Then** a live test query is run and the result (success, rate-limit warning, or authentication failure) is displayed.
3. **Given** a stored credential, **When** it is displayed in the admin panel, **Then** the key value is masked and never shown in plaintext.
4. **Given** an API key set as a server environment variable, **When** no key has been stored via the admin panel, **Then** the system uses the environment variable and the admin panel displays "Configured via environment".

---

### User Story 6 - Author Search and Profile Lookup (Priority: P6)

A researcher needs to find papers by a specific author, or verify an author's profile to support grey literature or supplementary searches. They search by author name and institution, and can retrieve a full list of papers attributed to a specific author profile.

**Why this priority**: Author-based searches complement keyword searches and are particularly useful for grey literature and for verifying author affiliations in study inclusion decisions.

**Independent Test**: Can be tested independently by searching for a well-known author by name, verifying a profile is returned, and then retrieving that author's paper list.

**Acceptance Scenarios**:

1. **Given** an author name and optional institution, **When** an author search is performed, **Then** a list of matching author profiles is returned, each with name, affiliations, paper count, and a link to their public profile.
2. **Given** an author profile identifier, **When** the researcher requests full details, **Then** the author's full paper list is returned with structured metadata for each paper.

---

### Edge Cases

- What happens when a database returns no results for a valid query? — The system returns an empty result list with a success status; it does not raise an error.
- What happens when a search request exceeds the rate limit of one database mid-query? — The system returns a partial result set with a flag indicating which sources were truncated and why.
- What happens when a paper has no DOI? — Full-text retrieval attempts proceed using any available URL; citation and reference lookups that require a DOI return a "DOI not available" status.
- What happens when a PDF conversion fails entirely (corrupt file, password-protected PDF)? — The paper's text status is set to "conversion failed" with a reason; downstream agents fall back to abstract-only processing.
- What happens when the same paper appears in results from multiple databases? — Deduplication uses DOI as the primary key; papers without DOIs are deduplicated by normalised title and first author.
- What happens when SciHub is enabled at the server level but the researcher has not acknowledged the disclaimer? — The system does not invoke SciHub and returns "SciHub not acknowledged" as the retrieval status.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Database Index Selection (Study-Level)

- **FR-001**: The system MUST allow researchers to select which academic database indices are included in a study's search strategy during study creation and in study settings.
- **FR-002**: The system MUST group database indices into categories: Primary CS/SE Databases, General Indices, and Supplementary, with each index showing its current connectivity status.
- **FR-003**: The system MUST persist a study's database index selection so that it is applied consistently across all searches within that study.
- **FR-004**: The system MUST display a visible warning when a selected index requires a credential that has not been configured.
- **FR-005**: The system MUST allow researchers to enable snowball sampling (backward/forward citation tracing) as a supplementary search mode for any study.

#### Multi-Database Search

- **FR-006**: The system MUST execute searches across all indices selected for a study in parallel and return a merged, deduplicated result set.
- **FR-007**: Each paper record returned by any search MUST include at minimum: title, DOI (where available), abstract (where available), authors, publication year, venue, and the source database.
- **FR-008**: The system MUST deduplicate results across sources using DOI as the primary key, falling back to normalised title and first author when no DOI is present.
- **FR-009**: When a database source fails or is rate-limited during a search, the system MUST still return results from all other sources and clearly indicate which sources were affected.
- **FR-010**: The system MUST support filtering searches by publication year range and, where the source allows, by content type or subject area.

#### Full-Text Retrieval

- **FR-011**: The system MUST attempt full-text PDF retrieval using open-access sources by default before considering any other retrieval method.
- **FR-012**: The system MUST store the retrieved PDF source (open access, direct, or other) against each paper record so its provenance is traceable.
- **FR-013**: SciHub retrieval MUST only be available when explicitly enabled at the server infrastructure level by an operator.
- **FR-014**: SciHub MUST require an explicit per-study opt-in by the researcher, preceded by a legal acknowledgment dialog, before any SciHub retrieval attempt is made.
- **FR-015**: If SciHub retrieval is requested but is not enabled at the server level, the system MUST return a clear error rather than silently failing or falling back.

#### Citation and Reference Lookup

- **FR-016**: The system MUST provide a citation lookup that returns a structured list of papers citing a given paper, identified by DOI.
- **FR-017**: The system MUST provide a reference lookup that returns a structured list of papers referenced by a given paper, identified by DOI.
- **FR-018**: Both citation and reference lookups MUST return normalised paper records (same schema as search results) rather than raw citation strings.

#### Paper Text Conversion

- **FR-019**: The system MUST convert retrieved PDFs to plain structured text and store the result against the paper record for use by downstream agents.
- **FR-020**: The system MUST support OCR-assisted text extraction for papers where standard text extraction yields no usable content.
- **FR-021**: Once converted text is stored for a paper, subsequent text retrieval requests MUST return the stored result without re-running conversion.
- **FR-022**: Downstream AI agents (screening, extraction) MUST use stored plain text when available, falling back to the abstract when no full text is present.

#### Author Search

- **FR-023**: The system MUST support searching for authors by name and optional institution, returning structured author profiles.
- **FR-024**: The system MUST allow retrieval of a full paper list for a specific author by their profile identifier.

#### Credential Management

- **FR-025**: Administrators MUST be able to add, update, and test API credentials for all subscription-gated database integrations from the administration panel without modifying server configuration files.
- **FR-026**: Stored credentials MUST never be returned in plaintext via any interface; only a masked representation is displayed.
- **FR-027**: Each integration MUST have an on-demand connectivity test that runs a lightweight live query and reports success, rate-limit warning, or authentication failure.
- **FR-028**: The system MUST fall back to server environment variables for credentials when no admin-panel credential has been stored, and MUST indicate this in the admin panel.

### Key Entities

- **Study Database Selection**: A per-study configuration record linking a study to its chosen set of database indices, stored with enable/disable flags per index.
- **Paper Record**: A normalised representation of an academic paper, including title, DOI, abstract, authors, year, venue, source database, and open-access status. Shared schema regardless of originating source.
- **Full-Text Content**: The plain-text rendering of a paper's full content, stored against the paper record with provenance (source, conversion method, timestamp).
- **Search Integration Credential**: An encrypted credential record per database integration, used for authentication with subscription-gated services.
- **Author Profile**: A structured record of an academic author including name, affiliations, publication count, and citation metrics, returned from author search.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A researcher can configure database index selection for a study and execute a parallel search across three or more sources, receiving a merged deduplicated result set, within a single workflow session.
- **SC-002**: Search results from any configured index include title, DOI (where available), abstract, authors, year, and venue — completeness verified across a representative set of 50 queries.
- **SC-003**: Open-access full-text retrieval succeeds for at least 40% of accepted papers in a representative computer science or software engineering study.
- **SC-004**: Paper text conversion completes without errors for standard, non-scanned PDFs and the resulting text is stored and accessible to AI agents.
- **SC-005**: Citation and reference lookups return structured results (not empty stubs) for any paper with a known identifier in the citation data source.
- **SC-006**: An administrator can add, test, and update credentials for all subscription-gated integrations from the admin panel without requiring server restarts or environment variable changes.
- **SC-007**: SciHub cannot be invoked unless both the server operator has enabled it at the infrastructure level and the researcher has completed the per-study acknowledgment — verified by attempting retrieval in each missing-condition scenario.
- **SC-008**: When one or more database sources fail during a parallel search, results from the remaining sources are returned within the same response, with affected sources identified.

---

## Assumptions

- All academic database integrations are implemented as services callable from the research automation backend; the researcher interacts with them through the study workflow UI and does not manage database connections directly.
- The Unpaywall service requires a registered institutional email for identification as per its terms of service; this email is configured globally by the administrator.
- Deduplication across database sources is performed by the system before returning results to the researcher; researchers do not need to manually identify duplicates from multi-source searches.
- OCR-assisted text extraction relies on a vision-capable model configured in the system; if no such model is configured, OCR is unavailable but standard text extraction still functions.
- Grey literature retrieval (technical reports, dissertations) is out of scope for the initial implementation but the architecture supports it as a future extension.
- The legal disclaimer for SciHub is shown once per study at the time of opt-in; it does not need to be acknowledged on every retrieval request.
