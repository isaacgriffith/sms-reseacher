# Changelog — sms-agents

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — feature/003-project-setup-improvements

### Changed
- Coverage command documented in `CLAUDE.md`: `uv run pytest agents/tests/ --cov=agents`
- Mutation testing tool updated to `cosmic-ray` (was `mutmut`); run via manual GitHub
  Actions `workflow_dispatch` workflow
- `pytest` build gate enforced: skip/xfail markers without `reason=` cause the run to fail

---

## [0.2.0] — 2026-03-12 — feature/002-sms-workflow

### Added
- `ScreenerAgent` — include/exclude decision for paper abstracts given criteria
- `ExtractorAgent` — extract structured data fields from full paper text
- `SynthesiserAgent` — synthesise a research answer from multiple paper summaries
- `AgentSettings` — Pydantic Settings for LLM provider, model, and MCP URL
- `PromptLoader` — Jinja2 template rendering for `system.md` / `user.md.j2` prompt pairs
- `MCPClient` — connects to `RESEARCHER_MCP_URL` over SSE; exposes tools as LiteLLM
  function-call schemas
- Prompt template directories for each agent under `src/agents/prompts/`
- `candidates/` subdirectory in each prompt directory for human-reviewed revisions
- Property-based tests using `hypothesis` for metamorphic agent behaviour
- LiteLLM abstraction: all LLM calls go through `LLMClient` in `agents/core/llm_client.py`

---

## [0.1.0] — 2026-03-11 — feature/001-repo-setup

### Added
- Initial `pyproject.toml` (`sms-agents`) as UV workspace member
- Ruff, MyPy strict, pytest + pytest-asyncio configuration
