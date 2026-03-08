# sms-agent-eval

Typer CLI for evaluating SMS Researcher agents using LLM-as-a-Judge (via DeepEval + LiteLLM).

## Setup

```bash
# From repo root
uv sync

# Verify CLI is available
uv run agent-eval --help
```

## Commands

### `evaluate` — Run a test suite against an agent

```bash
uv run agent-eval evaluate \
  --agent screener \
  --suite agent-eval/test-suites/screener.jsonl \
  --threshold 0.7 \
  --output /tmp/eval-report.json
```

Test suite format (JSONL, one case per line):
```json
{"case_id": "tc-001", "input": {"inclusion_criteria": "...", "abstract": "..."}, "expected_decision": "include"}
```

**Exit codes**: `0` = all passed, `1` = cases failed, `2` = config error

### `report` — Display a saved evaluation report

```bash
uv run agent-eval report /tmp/eval-report.json
uv run agent-eval report /tmp/eval-report.json --format markdown
uv run agent-eval report /tmp/eval-report.json --format json --output report.json
```

### `compare` — Compare two evaluation runs

```bash
uv run agent-eval compare baseline.json candidate.json
```

Output:
```
Metric                 Baseline   Candidate   Delta
─────────────────────────────────────────────────────
Screening Accuracy     0.72       0.85        +0.13 ↑
```

### `improve` — Generate candidate prompt revisions

```bash
uv run agent-eval improve \
  --report /tmp/eval-report.json \
  --agent screener \
  --threshold 0.7
```

Writes `system_candidate_{timestamp}.md` and `user_candidate_{timestamp}.md.j2` to `agents/prompts/screener/candidates/` for human review.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `anthropic` | `anthropic` or `ollama` |
| `LLM_MODEL` | `claude-sonnet-4-6` | Judge model ID |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama URL (when `LLM_PROVIDER=ollama`) |
| `ANTHROPIC_API_KEY` | — | Required for Anthropic provider |

## Project Structure

```
agent-eval/
├── pyproject.toml
├── src/agent_eval/
│   ├── cli.py              # Typer app; wires evaluate/report/compare/improve
│   ├── models.py           # EvalReport, TestCaseResult Pydantic models
│   ├── commands/
│   │   ├── evaluate.py
│   │   ├── report.py
│   │   ├── compare.py
│   │   └── improve.py
│   └── judge/
│       └── litellm_judge.py  # DeepEvalBaseLLM wrapper over LiteLLM
└── tests/unit/
    ├── test_cli_help.py
    └── test_models.py
```
