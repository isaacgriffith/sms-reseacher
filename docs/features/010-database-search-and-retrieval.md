# Feature: Database Search, Retrieval & Paper Processing

**Feature ID**: 010-database-search-and-retrieval
**Depends On**: 001-repo-setup, 002-sms-workflow, 008-models-and-agents
**Reference**: `docs/systematic-mapping-studies.md`, `docs/systematic-literature-reviews.md`, `docs/rapid-reviews.md`, `specs/002-sms-workflow/contracts/mcp-tools.md`

---

## Overview

The existing `researcher-mcp` service defines stub MCP tools for `search_papers`, `get_paper`, `get_citations`, `get_references`, and `fetch_paper_pdf` but lacks real implementations behind those stubs. This feature delivers:

1. **Real, working backend integrations** in `researcher-mcp` for each supported academic database and retrieval service.
2. **Semantic Scholar integration** for paper metadata, author information, and citation/reference graphs.
3. **Full-text retrieval** via Unpaywall (open access) and SciHub (opt-in, user-acknowledged).
4. **Paper-to-Markdown conversion** using MarkItDown for downstream study selection, data extraction, and synthesis.
5. **Per-study UI for selecting which database indices to search**, replacing the implicit "all databases" behaviour.
6. **API key and credential management** for subscription-gated services, integrated with the provider management system from feature 008.

---

## Part 1: UI — Database Index Selection

### Study-Level Index Configuration

During study creation (New Study Wizard, Phase 2 — Study Identification) and in the study's settings, researchers can select which database indices to include in the study's search strategy. Index selection is persisted as part of the study configuration.

- Each index appears as a toggleable option with its display name, logo, and current connectivity status (configured / not configured / unreachable).
- Indices that require an API key show a warning badge if the key has not been configured in the administration panel.
- The selection UI groups indices into three categories:
  - **Primary CS/SE Databases** (recommended): IEEExplore, ACM Digital Library, Scopus, Web of Science
  - **General Indices**: Inspec/Compendex, ScienceDirect, SpringerLink
  - **Supplementary**: Google Scholar, Semantic Scholar

Alongside the database selection, researchers can enable the following supplementary search modes:
- **Snowball Sampling** (backward/forward) — always available; uses Semantic Scholar and CrossRef for citation/reference data
- **Grey Literature** (for SLR/Tertiary studies) — enables scraping of author pages and journal proceedings pages

### Full-Text Retrieval Configuration (Per Study)

A separate section in the study settings controls how the system attempts to retrieve full-text papers for data extraction:

- **Unpaywall** (enabled by default): Retrieves open-access PDFs using the Unpaywall API. Requires an institutional email address configured globally in the admin settings.
- **SciHub** (disabled by default, opt-in): Retrieves PDFs from SciHub for papers unavailable through open-access channels. This option is gated behind an explicit acknowledgment:

  > *"SciHub distributes papers that may be subject to copyright restrictions. By enabling this option, you acknowledge that access to SciHub content may be legally restricted in your jurisdiction and that you take responsibility for compliance with applicable laws and your institution's policies. The system administrators are not liable for misuse."*

  SciHub can only be enabled if `SCIHUB_ENABLED=true` is set in the server environment (operator opt-in at the infrastructure level).

---

## Part 2: `researcher-mcp` — Database Search Integrations

All integrations are implemented as MCP tools within `researcher-mcp` (FastMCP 2.0). Each tool is independent and returns a normalised `PaperRecord` schema regardless of source.

### Normalised PaperRecord Schema

```json
{
  "doi": "string | null",
  "title": "string",
  "abstract": "string | null",
  "authors": [{ "name": "string", "institution": "string | null", "orcid": "string | null" }],
  "year": 2024,
  "venue": "string | null",
  "venue_type": "journal | conference | book | preprint | report | other | null",
  "url": "string | null",
  "open_access": true,
  "source_database": "string",
  "raw_id": "string | null"
}
```

---

### 2.1 IEEExplore

**Access**: Official IEEE Xplore API — free registration, API key required. Covers journals, conference proceedings, books, and standards.

**Library**: Official IEEE Python SDK (`xplore` / `xploreapi`) from `developer.ieee.org`.

**MCP Tool: `search_ieee`**
```json
Input:  { "query": "string", "max_results": 100, "year_from": 2010, "year_to": 2025, "content_type": ["Journals","Conference Publications","Books","Standards"] | null }
Output: [PaperRecord]
```

**MCP Tool: `get_ieee_paper`**
```json
Input:  { "article_number": "string" }
Output: PaperRecord
```

**API Key Storage**: `IEEE_XPLORE_API_KEY` environment variable, displayed as masked in the admin panel.

---

### 2.2 ACM Digital Library

**Access**: No official public API. Implemented via structured web scraping of the ACM DL search interface with respectful rate limiting and robots.txt compliance.

**Approach**: Custom scraper using `httpx` and `BeautifulSoup`. Metadata (title, abstract, DOI, authors, venue) is extracted from ACM DL search result pages. Where institutional access is not available, abstract-only records are returned.

**MCP Tool: `search_acm`**
```json
Input:  { "query": "string", "max_results": 100, "year_from": 2010, "year_to": 2025 }
Output: [PaperRecord]
```

**Notes**: ACM scraping is subject to IP-based rate limiting. The tool implements exponential backoff and will return a partial result set with a `truncated: true` flag if rate limiting is encountered. No API key required; institutional network access improves metadata coverage. Explicit disclaimer in admin UI: *"ACM Digital Library access is provided via web scraping as no official API is available. Use in accordance with ACM's Terms of Service."*

---

### 2.3 Google Scholar

**Access**: No official API. Implemented via the `scholarly` Python library (PyPI: `scholarly`), which uses unofficial scraping. Proxy configuration is strongly recommended for production use to avoid CAPTCHA blocks.

**Library**: `scholarly`

**MCP Tool: `search_google_scholar`**
```json
Input:  { "query": "string", "max_results": 100, "year_from": 2010, "year_to": 2025, "citations": false }
Output: [PaperRecord]
```

**Proxy Configuration**: `SCHOLARLY_PROXY_URL` environment variable (optional). If not configured, the tool operates without a proxy and may encounter CAPTCHAs after moderate query volumes. The admin panel displays a warning when Google Scholar is enabled without proxy configuration.

**Notes**: Explicit disclaimer in admin UI: *"Google Scholar access relies on unofficial methods. Results may be incomplete or temporarily unavailable due to rate limiting. Use in accordance with Google's Terms of Service."*

---

### 2.4 Inspec/Compendex (Engineering Village)

**Access**: Elsevier Engineering Village API. Requires institutional subscription and API key from `dev.elsevier.com`. No publicly maintained Python wrapper exists; implemented via direct REST calls to the Engineering Village API.

**Library**: Direct `httpx` REST integration against the Elsevier Engineering Village API.

**MCP Tool: `search_inspec`**
```json
Input:  { "query": "string", "max_results": 100, "year_from": 2010, "year_to": 2025, "databases": ["INS", "CPX"] }
Output: [PaperRecord]
```

**API Key Storage**: `ELSEVIER_API_KEY` and `ELSEVIER_INST_TOKEN` environment variables (shared with Scopus and ScienceDirect).

**Notes**: If institutional access is not available, the tool returns a structured `AccessDenied` error rather than silently returning empty results. The admin panel shows a connectivity test result for Engineering Village separately from Scopus.

---

### 2.5 Scopus (Elsevier)

**Access**: Official Elsevier Scopus API. Free API key for institutional users at `dev.elsevier.com`.

**Library**: `pybliometrics` (PyPI: `pybliometrics`) — the most feature-complete and actively maintained Python wrapper for the Scopus and ScienceDirect APIs.

**MCP Tool: `search_scopus`**
```json
Input:  { "query": "string", "max_results": 100, "year_from": 2010, "year_to": 2025, "subject_areas": ["COMP","ENGI"] | null }
Output: [PaperRecord]
```

**MCP Tool: `get_scopus_paper`**
```json
Input:  { "doi": "string" } | { "eid": "string" }
Output: PaperRecord
```

**API Key Storage**: `ELSEVIER_API_KEY` (shared with ScienceDirect/Inspec), `ELSEVIER_INST_TOKEN`.

---

### 2.6 Web of Science (Clarivate)

**Access**: Clarivate Web of Science Starter API and API Expanded. Requires institutional access and individual API key.

**Library**: Official Clarivate Python client `wosstarter_python_client` (GitHub: `clarivate/wosstarter_python_client`).

**MCP Tool: `search_wos`**
```json
Input:  { "query": "string", "max_results": 100, "year_from": 2010, "year_to": 2025, "edition": "WOS" | "MEDLINE" | "BIOSIS" | null }
Output: [PaperRecord]
```

**API Key Storage**: `WOS_API_KEY` environment variable.

---

### 2.7 ScienceDirect (Elsevier)

**Access**: Official Elsevier ScienceDirect API. Same API key infrastructure as Scopus.

**Library**: `pybliometrics` or `elsapy` (GitHub: `ElsevierDev/elsapy`). Use `pybliometrics` as the primary implementation since it is already used for Scopus; fall back to `elsapy` if ScienceDirect-specific endpoints are needed.

**MCP Tool: `search_sciencedirect`**
```json
Input:  { "query": "string", "max_results": 100, "year_from": 2010, "year_to": 2025, "open_access_only": false }
Output: [PaperRecord]
```

**API Key Storage**: `ELSEVIER_API_KEY` (shared with Scopus/Inspec).

---

### 2.8 SpringerLink (Springer Nature)

**Access**: Official Springer Nature Metadata API and Open Access API. Free API key for non-commercial use at `dev.springernature.com`. Covers ~12 million documents.

**Library**: Official `springernature_api_client` (GitHub: `springernature/springernature_api_client`, requires Python 3.9+).

**MCP Tool: `search_springer`**
```json
Input:  { "query": "string", "max_results": 100, "year_from": 2010, "year_to": 2025, "open_access_only": false }
Output: [PaperRecord]
```

**API Key Storage**: `SPRINGER_API_KEY` environment variable.

---

## Part 3: `researcher-mcp` — Semantic Scholar Integration

Semantic Scholar provides a public Academic Graph API covering ~220 million papers, with rich citation/reference data, author profiles, and semantic embeddings. An optional API key increases rate limits. An existing community FastMCP server (`semantic-scholar-fastmcp-mcp-server`) exists and should be evaluated for adoption or as a reference implementation.

**Library**: `semanticscholar` (PyPI: `semanticscholar`) — most feature-complete Python client with async support.

**API Key Storage**: `SEMANTIC_SCHOLAR_API_KEY` environment variable (optional; increases rate limits from shared to per-key).

### Updated MCP Tool: `search_semantic_scholar`
```json
Input:  { "query": "string", "max_results": 100, "year_from": 2010, "year_to": 2025, "fields_of_study": ["Computer Science","Artificial Intelligence"] | null, "open_access_only": false }
Output: [PaperRecord]
```

### Updated MCP Tool: `get_references` (upgrade existing stub)
Uses Semantic Scholar as the primary data source for reference lists, falling back to CrossRef.
```json
Input:  { "doi": "string", "max_results": 200 }
Output: [PaperRecord + { "intent": "methodology|background|result|unknown" }]
```

### Updated MCP Tool: `get_citations` (upgrade existing stub)
Uses Semantic Scholar as the primary data source for citation lists.
```json
Input:  { "doi": "string", "max_results": 200 }
Output: [PaperRecord + { "citation_source": "semantic_scholar" }]
```

### New MCP Tool: `search_author_semantic_scholar`
```json
Input:  { "name": "string", "institution": "string | null", "limit": 10 }
Output: [{ "author_id": "string", "name": "string", "affiliations": ["string"], "paper_count": 42, "citation_count": 1234, "h_index": 12, "profile_url": "string", "fields_of_study": ["string"] }]
```

### New MCP Tool: `get_author_semantic_scholar`
```json
Input:  { "author_id": "string" }
Output: { "author_id": "string", "name": "string", "affiliations": ["string"], "papers": [PaperRecord] }
```

### New MCP Tool: `get_paper_semantic_scholar`
Retrieves full metadata for a single paper including abstract, TLDRs, embedding vectors, and influential citation count.
```json
Input:  { "doi": "string" } | { "semantic_scholar_id": "string" }
Output: PaperRecord + { "tldr": "string | null", "influential_citation_count": 12, "is_open_access": true, "fields_of_study": ["string"] }
```

---

## Part 4: `researcher-mcp` — Full-Text Retrieval

### Updated MCP Tool: `fetch_paper_pdf` (upgrade existing stub)

The existing stub is upgraded to a real implementation with a priority waterfall:

1. **Unpaywall**: Query the Unpaywall API (`unpywall` library) using the paper's DOI. Returns the best open-access PDF URL.
2. **Direct URL**: If the paper's `url` points to a PDF or a known open-access publisher, attempt direct retrieval.
3. **SciHub** (opt-in only): If `SCIHUB_ENABLED=true` in the server environment AND the study has SciHub enabled, attempt retrieval via SciHub. Uses `scidownl` (PyPI: `scidownl`) or the `scihub.py` library.

```json
Input:  { "doi": "string", "url": "string | null", "allow_scihub": false }
Output: { "pdf_bytes_b64": "string | null", "available": true, "source": "unpaywall | direct | scihub | unavailable", "open_access_url": "string | null" }
```

**Unpaywall Configuration**: `UNPAYWALL_EMAIL` environment variable (required; Unpaywall's terms of service require an institutional email for identification).

**SciHub guard**: `allow_scihub` in the tool input is only respected when `SCIHUB_ENABLED=true` in the server environment. If `SCIHUB_ENABLED` is not set or is `false`, passing `allow_scihub: true` returns a `SciHubDisabled` error rather than silently falling back.

---

## Part 5: `researcher-mcp` — Paper-to-Markdown Conversion

Downloaded PDFs (and any other document formats) must be converted to Markdown before being passed to AI agents for study selection, data extraction, or synthesis. MarkItDown (Microsoft, PyPI: `markitdown[all]`) handles this conversion locally.

**Library**: `markitdown[all]` (requires Python 3.10+). Supports PDF, DOCX, PPTX, XLSX, HTML, and more. Optional OCR support via `markitdown-ocr` plugin for scanned PDFs.

### New MCP Tool: `convert_paper_to_markdown`

```json
Input:  {
  "pdf_bytes_b64": "string | null",
  "url": "string | null",
  "doi": "string | null",
  "enable_ocr": false
}
Output: {
  "markdown": "string",
  "title": "string | null",
  "page_count": 12,
  "word_count": 8430,
  "conversion_method": "markitdown | markitdown-ocr",
  "warnings": ["string"]
}
```

**Input priority**: `pdf_bytes_b64` is used first if provided. If not, `url` is fetched and converted. If only `doi` is provided, the tool calls `fetch_paper_pdf` internally to obtain the PDF before conversion.

**OCR**: When `enable_ocr: true`, the tool uses the `markitdown-ocr` plugin, which invokes an LLM vision model to extract text from scanned or image-heavy PDFs. The LLM used for OCR is configurable via the `MARKITDOWN_OCR_MODEL` environment variable.

**Storage**: Converted Markdown is stored against the `CandidatePaper` record in the database (as `full_text_markdown`) and is used by all downstream agents (Screener, Extractor) in preference to raw PDF content.

### New MCP Tool: `get_paper_markdown`

Retrieves the stored Markdown for a paper that has already been converted, without re-running conversion.

```json
Input:  { "doi": "string" } | { "paper_id": "string" }
Output: { "markdown": "string | null", "converted_at": "ISO8601 | null", "available": true }
```

---

## Part 6: Administration Panel — API Key & Credential Management

The credential management for all database integrations is centralised in the administration panel's **Search Integrations** section (separate from but visually adjacent to the Models & Providers section from feature 008).

For each database integration, the admin panel shows:

| Column | Content |
|---|---|
| Database | Name and logo |
| Status | `configured` / `not configured` / `unreachable` |
| Access Type | Official API / Unofficial scraping / Subscription required |
| API Key | Masked display of stored key; edit button |
| Last Tested | Timestamp of last connectivity test |
| Test Now | Button to run a lightweight probe (e.g., one-paper search) |

API keys are stored encrypted in the database. They are never returned in plaintext via any API response. The connectivity test for each integration runs a minimal query and reports success, rate-limit warning, or authentication failure.

**Environment variable fallback**: If an API key is not stored in the database but the corresponding environment variable is set (e.g., `ELSEVIER_API_KEY`), the system uses the environment variable and displays "Configured via environment" in the admin panel.

---

## New and Updated MCP Tool Contracts Summary

| Tool | Status | Primary Source |
|---|---|---|
| `search_ieee` | New | IEEE Xplore API (`xplore`/`xploreapi`) |
| `get_ieee_paper` | New | IEEE Xplore API |
| `search_acm` | New | Custom scraper (`httpx` + `BeautifulSoup`) |
| `search_google_scholar` | New | `scholarly` |
| `search_inspec` | New | Elsevier Engineering Village REST API |
| `search_scopus` | New | `pybliometrics` |
| `get_scopus_paper` | New | `pybliometrics` |
| `search_wos` | New | `wosstarter_python_client` |
| `search_sciencedirect` | New | `pybliometrics` / `elsapy` |
| `search_springer` | New | `springernature_api_client` |
| `search_semantic_scholar` | New | `semanticscholar` |
| `search_author_semantic_scholar` | New | `semanticscholar` |
| `get_author_semantic_scholar` | New | `semanticscholar` |
| `get_paper_semantic_scholar` | New | `semanticscholar` |
| `get_references` | Upgraded (was stub) | `semanticscholar` + CrossRef fallback |
| `get_citations` | Upgraded (was stub) | `semanticscholar` + CrossRef fallback |
| `fetch_paper_pdf` | Upgraded (was stub) | `unpywall` → direct → `scidownl` (opt-in) |
| `convert_paper_to_markdown` | New | `markitdown[all]` (local) |
| `get_paper_markdown` | New | Database cache |
| `search_papers` | Upgraded | Fan-out across selected per-study indices |

The existing `search_papers` tool is updated to fan out to all per-study selected indices in parallel, merging and deduplicating results before returning.

---

## New Data Model Additions

- `StudyDatabaseSelection`: join table linking a `Study` to its set of selected database indices (stored as index identifiers + enabled flag).
- `SearchIntegrationCredential`: encrypted API key storage per integration type (one row per provider).
- `CandidatePaper.full_text_markdown`: nullable text column storing MarkItDown-converted paper content.
- `CandidatePaper.full_text_source`: enum (`unpaywall | direct | scihub | unavailable | pending`).
- `CandidatePaper.full_text_converted_at`: timestamp of last successful MarkItDown conversion.

---

## Integration Points

- **Feature 008 (Models & Agents)**: The admin panel Search Integrations section shares the same design language as the Models & Providers section. Both are part of the Administration view.
- **Feature 002 (SMS Workflow)**: `FR-017` and `FR-028` in the SMS spec are satisfied by this feature's real implementations. The existing `search_papers` fan-out, `fetch_paper_pdf`, `get_references`, and `get_citations` stub contracts are backward-compatible; upgrading to real implementations requires no changes to the calling code.
- **Feature 003 (SLR Workflow)**: Grey literature retrieval (technical reports, dissertations) can leverage the Semantic Scholar API and Unpaywall for open-access grey literature.
- **Feature 009 (Research Protocol)**: Search task nodes in protocol graphs reference the configured index selection and full-text retrieval preferences stored in the study.

---

## Dependencies and Installation Requirements

```
# researcher-mcp/requirements additions
xploreapi>=0.2.0          # IEEE Xplore
scholarly>=1.7.11         # Google Scholar (unofficial)
pybliometrics>=4.0.0      # Scopus + ScienceDirect
elsapy>=0.5.1             # Elsevier fallback
wosstarter_python_client  # Web of Science
springernature_api_client # Springer Nature
semanticscholar>=0.8.4    # Semantic Scholar
unpywall>=0.3.0           # Unpaywall
scidownl>=1.0.2           # SciHub (conditional import, only if SCIHUB_ENABLED=true)
markitdown[all]>=0.1.0    # PDF/DOCX to Markdown (requires Python 3.10+)
httpx>=0.27.0             # ACM/Inspec HTTP client
beautifulsoup4>=4.12.0    # ACM HTML parsing
```

Python version requirement for `researcher-mcp` rises from 3.12 to **3.14** to satisfy `markitdown[all]` (requires ≥3.10) and `springernature_api_client` (requires ≥3.9). Both requirements are already satisfied by the project's declared runtime.

---

## Success Criteria

- A study configured to search IEEExplore, Scopus, and Semantic Scholar executes a parallel search across all three and returns a deduplicated merged result set.
- Each database integration returns a normalised `PaperRecord` with at least title, DOI (where available), abstract, authors, year, and venue.
- The Unpaywall integration successfully retrieves an open-access PDF for at least 40% of accepted papers in a representative CS/SE study.
- `convert_paper_to_markdown` successfully converts a standard PDF to Markdown with no tool errors; output is stored in `CandidatePaper.full_text_markdown`.
- Downstream AI agents (Screener, Extractor) use `full_text_markdown` when available and fall back to abstract-only when not.
- An administrator can add, test, and update API keys for all subscription-gated integrations from the admin panel without touching environment variables.
- SciHub cannot be invoked unless both `SCIHUB_ENABLED=true` is set in the server environment and the researcher has acknowledged the disclaimer at the study level.
- The `get_references` and `get_citations` tools return structured citation data (not stubs) for any paper with a DOI present in Semantic Scholar.
