# MCP Tool Contracts: Database Search, Retrieval & Paper Processing

**Branch**: `006-database-search-and-retrieval`
**Date**: 2026-03-17
**Server**: `researcher-mcp` (FastMCP 3.x, `@mcp.tool` decorator)

All tools return structured Pydantic models. Tool functions are `async def`. Synchronous third-party library calls are offloaded via `asyncio.to_thread()`.

---

## Shared Schema: `PaperRecord`

```python
class PaperRecord(BaseModel):
    doi: str | None
    title: str
    abstract: str | None
    authors: list[AuthorInfo]
    year: int | None
    venue: str | None
    venue_type: Literal["journal","conference","book","preprint","report","other"] | None
    url: str | None
    open_access: bool
    source_database: str          # e.g., "ieee_xplore", "scopus", "semantic_scholar"
    raw_id: str | None            # Source-native identifier

class AuthorInfo(BaseModel):
    name: str
    institution: str | None
    orcid: str | None
```

---

## Upgraded Tool: `search_papers`

Fan-out across all study-selected indices (or an explicit list). Results are merged and deduplicated (DOI primary key; normalised title+first-author fallback).

```python
@mcp.tool
async def search_papers(
    query: str,
    indices: list[str] | None = None,   # DatabaseIndex values; None = all configured
    max_results: int = 100,
    year_from: int | None = None,
    year_to: int | None = None,
) -> SearchPapersResult:
    ...

class SearchPapersResult(BaseModel):
    papers: list[PaperRecord]
    total_found: int
    sources_queried: list[str]
    sources_failed: list[SourceFailure]
    truncated: bool

class SourceFailure(BaseModel):
    source: str
    reason: str   # "rate_limited" | "auth_failed" | "unreachable" | "not_configured"
```

---

## New Tool: `search_ieee`

```python
@mcp.tool
async def search_ieee(
    query: str,
    max_results: int = 100,
    year_from: int | None = None,
    year_to: int | None = None,
    content_type: list[str] | None = None,  # ["Journals","Conference Publications","Books","Standards"]
) -> list[PaperRecord]:
    ...
```

---

## New Tool: `get_ieee_paper`

```python
@mcp.tool
async def get_ieee_paper(article_number: str) -> PaperRecord:
    ...
```

---

## New Tool: `search_acm`

```python
@mcp.tool
async def search_acm(
    query: str,
    max_results: int = 100,
    year_from: int | None = None,
    year_to: int | None = None,
) -> AcmSearchResult:
    ...

class AcmSearchResult(BaseModel):
    papers: list[PaperRecord]
    truncated: bool   # True if rate limiting cut the result set short
```

---

## New Tool: `search_google_scholar`

```python
@mcp.tool
async def search_google_scholar(
    query: str,
    max_results: int = 100,
    year_from: int | None = None,
    year_to: int | None = None,
) -> list[PaperRecord]:
    ...
```

---

## New Tool: `search_inspec`

```python
@mcp.tool
async def search_inspec(
    query: str,
    max_results: int = 100,
    year_from: int | None = None,
    year_to: int | None = None,
    databases: list[str] = ["INS", "CPX"],
) -> list[PaperRecord]:
    ...
```

---

## New Tool: `search_scopus`

```python
@mcp.tool
async def search_scopus(
    query: str,
    max_results: int = 100,
    year_from: int | None = None,
    year_to: int | None = None,
    subject_areas: list[str] | None = None,
) -> list[PaperRecord]:
    ...
```

---

## New Tool: `get_scopus_paper`

```python
@mcp.tool
async def get_scopus_paper(
    doi: str | None = None,
    eid: str | None = None,
) -> PaperRecord:
    ...
```

---

## New Tool: `search_wos`

```python
@mcp.tool
async def search_wos(
    query: str,
    max_results: int = 100,
    year_from: int | None = None,
    year_to: int | None = None,
    edition: str | None = None,   # "WOS" | "MEDLINE" | "BIOSIS"
) -> list[PaperRecord]:
    ...
```

---

## New Tool: `search_sciencedirect`

```python
@mcp.tool
async def search_sciencedirect(
    query: str,
    max_results: int = 100,
    year_from: int | None = None,
    year_to: int | None = None,
    open_access_only: bool = False,
) -> list[PaperRecord]:
    ...
```

---

## New Tool: `search_springer`

```python
@mcp.tool
async def search_springer(
    query: str,
    max_results: int = 100,
    year_from: int | None = None,
    year_to: int | None = None,
    open_access_only: bool = False,
) -> list[PaperRecord]:
    ...
```

---

## Upgraded Tool: `search_semantic_scholar`

Replaces the existing `search_papers` Semantic Scholar path with a dedicated tool.

```python
@mcp.tool
async def search_semantic_scholar(
    query: str,
    max_results: int = 100,
    year_from: int | None = None,
    year_to: int | None = None,
    fields_of_study: list[str] | None = None,
    open_access_only: bool = False,
) -> list[PaperRecord]:
    ...
```

---

## New Tool: `get_paper_semantic_scholar`

```python
@mcp.tool
async def get_paper_semantic_scholar(
    doi: str | None = None,
    semantic_scholar_id: str | None = None,
) -> SemanticScholarPaperDetail:
    ...

class SemanticScholarPaperDetail(PaperRecord):
    tldr: str | None
    influential_citation_count: int
    is_open_access: bool
    fields_of_study: list[str]
```

---

## New Tool: `search_author_semantic_scholar`

```python
@mcp.tool
async def search_author_semantic_scholar(
    name: str,
    institution: str | None = None,
    limit: int = 10,
) -> list[AuthorProfile]:
    ...

class AuthorProfile(BaseModel):
    author_id: str
    name: str
    affiliations: list[str]
    paper_count: int
    citation_count: int
    h_index: int
    profile_url: str
    fields_of_study: list[str]
```

---

## New Tool: `get_author_semantic_scholar`

```python
@mcp.tool
async def get_author_semantic_scholar(author_id: str) -> AuthorDetail:
    ...

class AuthorDetail(AuthorProfile):
    papers: list[PaperRecord]
```

---

## Upgraded Tool: `get_references`

Primary source: `AsyncSemanticScholar.get_paper_references(doi)`. Falls back to CrossRef.

```python
@mcp.tool
async def get_references(doi: str, max_results: int = 200) -> list[ReferenceRecord]:
    ...

class ReferenceRecord(PaperRecord):
    intent: Literal["methodology","background","result","unknown"]
```

---

## Upgraded Tool: `get_citations`

Primary source: `AsyncSemanticScholar.get_paper_citations(doi)`. Falls back to CrossRef.

```python
@mcp.tool
async def get_citations(doi: str, max_results: int = 200) -> list[CitationRecord]:
    ...

class CitationRecord(PaperRecord):
    citation_source: str   # "semantic_scholar" | "crossref"
```

---

## Upgraded Tool: `fetch_paper_pdf`

Priority waterfall: Unpaywall → direct URL → SciHub (opt-in only).

```python
@mcp.tool
async def fetch_paper_pdf(
    doi: str,
    url: str | None = None,
    allow_scihub: bool = False,
) -> PdfFetchResult:
    ...

class PdfFetchResult(BaseModel):
    pdf_bytes_b64: str | None
    available: bool
    source: Literal["unpaywall","direct","scihub","unavailable"]
    open_access_url: str | None
```

`allow_scihub=True` is only honoured when `SCIHUB_ENABLED=true` in the server environment. Otherwise returns `MCPError("SciHubDisabled")`.

---

## New Tool: `convert_paper_to_markdown`

```python
@mcp.tool
async def convert_paper_to_markdown(
    pdf_bytes_b64: str | None = None,
    url: str | None = None,
    doi: str | None = None,
    enable_ocr: bool = False,
) -> MarkdownConversionResult:
    ...

class MarkdownConversionResult(BaseModel):
    markdown: str
    title: str | None
    page_count: int | None
    word_count: int
    conversion_method: Literal["markitdown","markitdown-ocr"]
    warnings: list[str]
```

Input priority: `pdf_bytes_b64` → `url` → `doi` (triggers `fetch_paper_pdf` internally).

---

## New Tool: `get_paper_markdown`

Returns stored Markdown for a paper already converted. Does not re-run conversion.

```python
@mcp.tool
async def get_paper_markdown(
    doi: str | None = None,
    paper_id: str | None = None,
) -> StoredMarkdownResult:
    ...

class StoredMarkdownResult(BaseModel):
    markdown: str | None
    converted_at: str | None   # ISO8601
    available: bool
```
