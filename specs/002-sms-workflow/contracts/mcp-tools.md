# MCP Tool Contracts: researcher-mcp

**Branch**: `002-sms-workflow` | **Date**: 2026-03-10
**Server**: `researcher-mcp` (FastMCP 2.0, runs on port 8002)

---

## Existing Tools (Unchanged)

### `search_papers`
Search academic databases for papers matching a query string.

**Input**:
```json
{
  "query": "string",
  "databases": ["acm", "ieee", "scopus", "wos", "sciencedirect", "google_scholar"],
  "max_results": 100,
  "year_from": 2011
}
```
**Output**: `[{ "doi": "string|null", "title": "string", "abstract": "string|null", "authors": [...], "year": 2024, "venue": "string", "url": "string" }]`

### `get_paper`
Retrieve full metadata for a single paper by DOI or URL.

**Input**: `{ "doi": "string" }` or `{ "url": "string" }`
**Output**: Single paper metadata object.

### `search_authors`
Search for academic author profiles.

**Input**: `{ "name": "string", "institution": "string|null" }`
**Output**: `[{ "name": "string", "institution": "string", "profile_url": "string", "research_areas": ["string"] }]`

### `get_author`
Retrieve an author's profile and paper list.

**Input**: `{ "profile_url": "string" }` or `{ "name": "string", "institution": "string" }`
**Output**: `{ "name": "string", "papers": [{ "doi": "string", "title": "string", "year": 2024 }] }`

### `fetch_paper_pdf`
Fetch the full text of a paper from an open-access source. SciHub access is opt-in via `SCIHUB_ENABLED=true`.

**Input**: `{ "doi": "string", "url": "string|null" }`
**Output**: `{ "text": "string|null", "available": true, "source": "unpaywall|doaj|scihub" }`

---

## New Tools (Added in this feature)

### `get_references`
Retrieve the reference list of a paper (backward snowball sampling).

**Input**:
```json
{ "doi": "string", "max_results": 200 }
```
**Output**: `[{ "doi": "string|null", "title": "string", "authors": [...], "year": 2024, "venue": "string" }]`
**Error**: `{ "error": "unavailable", "message": "Reference list not available for this paper" }`

### `get_citations`
Retrieve papers that cite a given paper (forward snowball sampling).

**Input**:
```json
{ "doi": "string", "max_results": 200 }
```
**Output**: `[{ "doi": "string|null", "title": "string", "authors": [...], "year": 2024, "venue": "string", "citation_source": "semantic_scholar|crossref|openalex" }]`

### `scrape_journal`
Scrape a journal or conference proceedings page for paper listings within a date range.

**Input**:
```json
{
  "journal_url": "string",
  "year_from": 2015,
  "year_to": 2024,
  "max_results": 500
}
```
**Output**: `[{ "doi": "string|null", "title": "string", "url": "string", "year": 2024 }]`

### `scrape_author_page`
Scrape an author's academic profile page for their paper list.

**Input**:
```json
{ "profile_url": "string", "max_results": 100 }
```
**Output**: `[{ "doi": "string|null", "title": "string", "url": "string", "year": 2024 }]`
