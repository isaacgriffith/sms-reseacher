# Changelog — sms-agents

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.8.0] — 2026-03-29 — feature/008-rapid-review-workflow

### Added
- **`NarrativeSynthesiserAgent`** (`narrative_synthesiser_agent.py`): LLM-powered narrative
  draft generation for a single Rapid Review research question; accepts `section_text` (prior
  content, may be empty), `rq_text`, and a list of included paper summaries; returns a
  `NarrativeDraftResult` with `narrative_text` and `confidence`
- **Prompt templates** (`prompts/narrative_synthesiser/`): Jinja2 `system.md` and `user.md.j2`
  templates for narrative synthesis agent

## [0.7.0] — 2026-03-21 — feature/007-slr-workflow

### Added
- **`ProtocolReviewerAgent`** (`services/protocol_reviewer.py`): LLM-powered structured review of
  SLR protocol sections; returns `ProtocolReviewResult` with per-section strengths, weaknesses,
  and actionable recommendations
- **Prompt templates** (`prompts/protocol_reviewer/`): Jinja2 system and user prompt templates
  for the protocol reviewer agent

## [0.5.0] — 2026-03-17 — feature/005-models-and-agents

### Added
- **`ProviderConfig` Protocol** (`core/provider_config.py`): runtime-checkable `typing.Protocol`
  with `model_string: str`, `api_base: str | None`, `api_key: str | None`; used to override
  env-based LLM settings per call without subclassing
- **`AgentGeneratorAgent`** (`agent_generator.py`): generates Jinja2 system message templates
  for given `task_type`, `role_name`, `role_description`, `persona_name`,
  `persona_description`, and `model_display_name` inputs; loads prompts from
  `prompts/agent_generator/`
- **`prompts/agent_generator/system.md`**: static prompt instructing the LLM to produce a
  Jinja2 template with `{{ role_name }}`, `{{ persona_name }}`, `{{ domain }}`, and
  `{{ study_type }}` placeholders
- **`prompts/agent_generator/user.md.j2`**: user prompt template for system-message generation
- Metamorphic tests for `AgentGeneratorAgent` (`tests/metamorphic/test_agent_generator.py`):
  `hypothesis`-based property tests verifying required Jinja2 placeholders are preserved when
  role description is paraphrased
- Unit tests for `ProviderConfig` Protocol and `LLMClient` override behaviour

### Changed
- **`LLMClient.complete()`** (`core/llm_client.py`): accepts optional
  `provider_config: ProviderConfig | None = None`; when provided, overrides `model_string`,
  `api_base`, and `api_key`; existing env-based behavior unchanged when `None`
- **All agent classes** (`ScreenerAgent`, `ExtractorAgent`, `LibrarianAgent`, `ExpertAgent`,
  `QualityJudgeAgent`, `DomainModelerAgent`, `SynthesiserAgent`, `ValidityAgent`): accept
  optional `provider_config: ProviderConfig | None = None` in `__init__`; pass it through
  to `LLMClient.complete()` calls

---

## [0.3.0] — 2026-03-16 — feature/003-project-setup-improvements

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
