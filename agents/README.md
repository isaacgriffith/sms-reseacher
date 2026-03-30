# sms-agents

LLM-powered research agents for SMS Researcher. Provides `ScreenerAgent`, `ExtractorAgent`, and `SynthesiserAgent` as an importable Python library.

## Setup

```bash
# From repo root
uv sync

# Run tests
uv run --package sms-agents pytest agents/tests/

# Run tests with coverage (minimum 85% line coverage required)
uv run --package sms-agents pytest agents/tests/ --cov=agents --cov-report=term-missing

# Mutation testing (run via GitHub Actions workflow_dispatch, or locally)
uv run cosmic-ray run agents/cosmic-ray.toml

# Lint and type-check
uv run ruff check agents/src
uv run ruff format --check agents/src
uv run mypy agents/src
```

## Agents

| Agent | Purpose |
|-------|---------|
| `ScreenerAgent` | Decides include/exclude for a paper abstract given inclusion/exclusion criteria |
| `ExtractorAgent` | Extracts structured data fields from full paper text |
| `SynthesiserAgent` | Synthesises a research answer from multiple paper summaries |
| `AgentGeneratorAgent` | Generates a Jinja2 system message template given role and persona inputs |
| `LibrarianAgent` | Searches and retrieves relevant literature |
| `ExpertAgent` | Provides domain-expert analysis on research topics |
| `QualityJudgeAgent` | Assesses methodological quality of included papers |
| `DomainModelerAgent` | Models research domain concepts and relationships |
| `ValidityAgent` | Assesses internal and external validity threats |
| `ProtocolReviewerAgent` | Structured review of SLR protocol sections with strengths/weaknesses/recommendations |
| `NarrativeSynthesiserAgent` | Generates narrative draft text for a Rapid Review research question section |

All agents accept an optional `provider_config` parameter to override the default
environment-based LLM settings on a per-call basis.

```python
from agents.services.screener import ScreenerAgent
from agents.core.config import AgentSettings

settings = AgentSettings()
agent = ScreenerAgent(settings)
decision = await agent.run(
    inclusion_criteria="...",
    exclusion_criteria="...",
    abstract="...",
)
```

### Per-Agent Provider Override (`ProviderConfig` Protocol)

```python
from agents.core.provider_config import ProviderConfig
from agents.services.screener import ScreenerAgent
from agents.core.config import AgentSettings

class MyConfig:  # satisfies ProviderConfig Protocol
    model_string = "ollama/llama3"
    api_base = "http://localhost:11434"
    api_key = None

agent = ScreenerAgent(AgentSettings(), provider_config=MyConfig())
```

## Prompt Templates

Each agent has a `prompts/{agent}/` directory with:

- `system.md` — role definition (plain Markdown)
- `user.md.j2` — Jinja2 template with context variables
- `candidates/` — human-reviewed prompt revisions (gitignored on `main`)

```
agents/src/agents/prompts/
├── screener/
│   ├── system.md
│   └── user.md.j2      # {{ inclusion_criteria }}, {{ exclusion_criteria }}, {{ abstract }}
├── extractor/
│   ├── system.md
│   └── user.md.j2      # {{ data_fields }}, {{ paper_text }}
├── synthesiser/
│   ├── system.md
│   └── user.md.j2      # {{ papers_summary }}, {{ research_question }}
└── agent_generator/
    ├── system.md        # instructs model to produce Jinja2 template with standard variables
    └── user.md.j2       # {{ task_type }}, {{ role_name }}, {{ role_description }},
                         # {{ persona_name }}, {{ persona_description }}, {{ model_display_name }}
```

Use `PromptLoader` to render templates:

```python
from agents.core.prompt_loader import PromptLoader

loader = PromptLoader("screener")
system, user = loader.render({"inclusion_criteria": "...", "abstract": "..."})
```

## MCP Client

`MCPClient` connects to `RESEARCHER_MCP_URL` (default `http://localhost:8002/sse`) and exposes discovered tools as LiteLLM function-call schemas:

```python
from agents.core.mcp_client import MCPClient

client = MCPClient(url="http://localhost:8002/sse")
await client.connect()
tools = client.to_litellm_tools()
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `anthropic` | `anthropic`, `openai`, or `ollama` |
| `LLM_MODEL` | `claude-sonnet-4-6` | Model ID |
| `ANTHROPIC_API_KEY` | — | Required when `LLM_PROVIDER=anthropic` |
| `OPENAI_API_KEY` | — | Required when `LLM_PROVIDER=openai` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `RESEARCHER_MCP_URL` | `http://localhost:8002/sse` | MCP server SSE endpoint |

When a `ProviderConfig` is passed directly to an agent, it takes precedence over these environment variables for that specific call.
