# Contract: `researcher-mcp` MCP Tools

**Sub-project**: `researcher-mcp` | **Date**: 2026-03-08

The `researcher-mcp` FastMCP server exposes research tools via the Model Context Protocol (MCP) over HTTP/SSE on port 8002. All tools follow the MCP tool-call pattern: JSON input schema, JSON output, structured errors.

All search responses include a `source` field (string) indicating which upstream API served the result, and an optional `warnings` list when a cascade fallback occurred or rate limiting was approached.

---

## Tool: `search_papers`

Search for academic papers across configured sources (Semantic Scholar → OpenAlex cascade).

**Input schema**:
```json
{
  "query":   { "type": "string",  "description": "Free-text search query", "required": true },
  "limit":   { "type": "integer", "description": "Max results (1–100)", "default": 10 },
  "year_from": { "type": "integer", "description": "Earliest publication year", "required": false },
  "year_to":   { "type": "integer", "description": "Latest publication year",  "required": false },
  "fields":  { "type": "array", "items": "string",
               "description": "Fields to return: title, abstract, doi, authors, year, venue, citations",
               "default": ["title", "doi", "year", "authors"] }
}
```

**Output schema**:
```json
{
  "results": [
    {
      "title":    "string",
      "doi":      "string | null",
      "year":     "integer | null",
      "abstract": "string | null",
      "authors":  [{"name": "string", "author_id": "string | null"}],
      "venue":    "string | null",
      "citations": "integer | null",
      "paper_id": "string"
    }
  ],
  "total":    "integer",
  "source":   "semantic_scholar | open_alex",
  "warnings": ["string"]
}
```

**Cascade behaviour**: Tries Semantic Scholar first; on 5xx, timeout, or network error falls back to OpenAlex. If both fail, raises MCP error code `UPSTREAM_UNAVAILABLE`.

---

## Tool: `get_paper`

Retrieve full metadata for a single paper by its ID or DOI.

**Input schema**:
```json
{
  "paper_id": { "type": "string", "description": "Semantic Scholar paper ID or DOI (prefix with 'DOI:')", "required": true },
  "fields":   { "type": "array", "items": "string", "default": ["title", "abstract", "doi", "authors", "year", "venue", "references"] }
}
```

**Output schema**:
```json
{
  "paper_id":  "string",
  "title":     "string",
  "abstract":  "string | null",
  "doi":       "string | null",
  "year":      "integer | null",
  "authors":   [{"name": "string", "author_id": "string | null"}],
  "venue":     "string | null",
  "citations": "integer | null",
  "references": [{"title": "string", "doi": "string | null"}],
  "source":    "semantic_scholar | open_alex | crossref",
  "warnings":  ["string"]
}
```

**DOI resolution**: When `paper_id` is prefixed `DOI:`, CrossRef is queried first to resolve metadata; result is supplemented with Semantic Scholar / OpenAlex data if available.

---

## Tool: `search_authors`

Search for academic authors by name.

**Input schema**:
```json
{
  "query": { "type": "string", "description": "Author name query", "required": true },
  "limit": { "type": "integer", "default": 10 }
}
```

**Output schema**:
```json
{
  "results": [
    {
      "author_id":    "string",
      "name":         "string",
      "affiliations": ["string"],
      "paper_count":  "integer | null",
      "h_index":      "integer | null"
    }
  ],
  "source":   "semantic_scholar",
  "warnings": ["string"]
}
```

---

## Tool: `get_author`

Retrieve full profile and publication list for a single author.

**Input schema**:
```json
{
  "author_id": { "type": "string", "description": "Semantic Scholar author ID", "required": true },
  "limit":     { "type": "integer", "description": "Max papers to return", "default": 50 }
}
```

**Output schema**:
```json
{
  "author_id":    "string",
  "name":         "string",
  "affiliations": ["string"],
  "paper_count":  "integer | null",
  "h_index":      "integer | null",
  "papers": [
    {
      "paper_id": "string",
      "title":    "string",
      "year":     "integer | null",
      "doi":      "string | null",
      "citations": "integer | null"
    }
  ],
  "source":   "semantic_scholar",
  "warnings": ["string"]
}
```

---

## Tool: `fetch_paper_pdf`

Attempt to fetch a paper's PDF from open-access sources.

**Input schema**:
```json
{
  "doi":         { "type": "string", "description": "Paper DOI",          "required": true },
  "output_path": { "type": "string", "description": "Local path to save the PDF", "required": true }
}
```

**Output schema**:
```json
{
  "success":     "boolean",
  "output_path": "string | null",
  "source":      "unpaywall | arxiv | scihub | null",
  "url":         "string | null",
  "warnings":    ["string"]
}
```

**Fetch cascade** (in order):
1. **Unpaywall** — queries `api.unpaywall.org/{doi}?email={UNPAYWALL_EMAIL}` for open-access PDF URL; downloads if found.
2. **arXiv** — attempts `arxiv.org/pdf/{arxiv_id}` lookup via DOI cross-reference.
3. **SciHub** — attempted **only** if `SCIHUB_ENABLED=true`; raises `SCIHUB_DISABLED` MCP error if env var is false.

**Legal warning** (documented in README and server startup log):
> SciHub access is opt-in only (`SCIHUB_ENABLED=true`). Users are solely responsible for compliance with applicable copyright law in their jurisdiction.

**Exit conditions**:
- All sources exhausted with no PDF found → `success: false`, `source: null`
- `SCIHUB_ENABLED=false` and Unpaywall + arXiv both fail → `success: false`, warning includes `"SciHub disabled; set SCIHUB_ENABLED=true to attempt SciHub"`

---

## Error Format

MCP errors use standard error codes:

| Code | Meaning |
|------|---------|
| `UPSTREAM_UNAVAILABLE` | All configured sources failed after retries |
| `INVALID_INPUT` | Input validation failed (missing required field, out-of-range value) |
| `RATE_LIMITED` | Per-source rate limit reached (after internal retry exhausted) |
| `SCIHUB_DISABLED` | SciHub was requested but `SCIHUB_ENABLED=false` |
| `PDF_NOT_FOUND` | No open-access PDF located from any enabled source |

---

## Retry & Rate Limiting Policy

Applies to all outbound HTTP calls within every tool:

- **Retry**: `tenacity` — max 3 attempts, exponential backoff with full jitter, retry on HTTP 5xx + `httpx.TimeoutException` + `httpx.NetworkError`.
- **Rate limiting**: Per-source request-per-minute cap enforced via token-bucket; configurable via env vars:
  - `SEMANTIC_SCHOLAR_RPM` (default: `100` — matches unauthenticated API limit)
  - `OPEN_ALEX_RPM` (default: `300`)
- **Cascade trigger**: Retry exhaustion on primary source triggers cascade to secondary (not an error).

---

## LiteLLM Function-Call Conversion

The `agents/core/mcp_client.py` discovers tools via MCP introspection and converts them to LiteLLM `tools` parameter format:

```python
{
  "type": "function",
  "function": {
    "name":        "search_papers",
    "description": "Search for academic papers across configured sources.",
    "parameters":  { ...JSON schema from MCP tool definition... }
  }
}
```

All five tools are converted and passed to every agent LLM call as the `tools` list, enabling function-calling-capable models to invoke MCP tools directly.
