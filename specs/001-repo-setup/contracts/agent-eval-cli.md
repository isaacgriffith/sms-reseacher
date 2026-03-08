# Contract: `agent-eval` CLI

**Sub-project**: `agent-eval` | **Date**: 2026-03-08

The `agent-eval` Typer CLI is invoked as `uv run agent-eval <command> [OPTIONS]`. All commands write structured JSON results to `--output` when specified, and render rich terminal output by default.

---

## Top-level

```
Usage: agent-eval [OPTIONS] COMMAND [ARGS]...

  SMS Researcher — Agent Evaluation CLI

Options:
  --version   Show version and exit.
  --help      Show this message and exit.

Commands:
  evaluate  Run a test suite against an agent and score with LLM-as-a-Judge.
  report    Display or export results from a previous evaluation run.
  compare   Compare scores between two evaluation runs or prompt variants.
  improve   Suggest prompt revisions based on low-scoring cases.
```

---

## `evaluate`

Run a labelled test suite through a specified agent type and score each case.

```
Usage: agent-eval evaluate [OPTIONS]

Options:
  --agent TEXT        Agent type to evaluate (screener|extractor|synthesiser)  [required]
  --suite PATH        Path to JSONL test suite file  [required]
  --model TEXT        Judge model ID; overrides LLM_MODEL env var.
                      Anthropic: "claude-sonnet-4-6"
                      Ollama:    "ollama/llama3.2:3b"  [default: env LLM_MODEL]
  --provider TEXT     LLM provider: anthropic|ollama  [default: env LLM_PROVIDER]
  --ollama-url TEXT   Ollama base URL  [default: env OLLAMA_BASE_URL or http://localhost:11434]
  --threshold FLOAT   Minimum passing score per metric (0.0–1.0)  [default: 0.7]
  --output PATH       Write EvalReport JSON to this path
  --help
```

**Test suite file format** (JSONL, one case per line):
```json
{"case_id": "tc-001", "input": {"inclusion_criteria": "...", "abstract": "..."}, "expected_decision": "include"}
```

**Exit codes**:
- `0` — all cases passed (score ≥ threshold)
- `1` — one or more cases failed
- `2` — configuration / input error

**stdout (rich table excerpt)**:
```
┌──────────┬───────────────────┬───────────┬────────┐
│ Case ID  │ Metric            │ Score     │ Pass   │
├──────────┼───────────────────┼───────────┼────────┤
│ tc-001   │ Screening Accuracy│ 0.92      │ ✓      │
│ tc-002   │ Screening Accuracy│ 0.61      │ ✗      │
└──────────┴───────────────────┴───────────┴────────┘
Overall: 0.765  |  Passed: 1/2
```

---

## `report`

Display or export a previously saved EvalReport JSON.

```
Usage: agent-eval report [OPTIONS] REPORT_PATH

Arguments:
  REPORT_PATH  Path to EvalReport JSON file  [required]

Options:
  --format TEXT   Output format: table|json|markdown  [default: table]
  --output PATH   Write formatted report to file instead of stdout
  --help
```

---

## `compare`

Compare two EvalReport files and show metric deltas.

```
Usage: agent-eval compare [OPTIONS] BASELINE CANDIDATE

Arguments:
  BASELINE   Path to baseline EvalReport JSON
  CANDIDATE  Path to candidate EvalReport JSON

Options:
  --output PATH   Write comparison table to file
  --help
```

**stdout excerpt**:
```
Metric                 Baseline   Candidate   Delta
─────────────────────────────────────────────────────
Screening Accuracy     0.72       0.85        +0.13 ↑
Hallucination          0.05       0.03        -0.02 ↑
```

---

## `improve`

Identify low-scoring cases and generate candidate revised prompts.

```
Usage: agent-eval improve [OPTIONS]

Options:
  --report PATH       EvalReport JSON to analyse  [required]
  --agent TEXT        Agent type whose prompts to improve  [required]
  --model TEXT        Improvement model ID  [default: env LLM_MODEL]
  --provider TEXT     LLM provider: anthropic|ollama  [default: env LLM_PROVIDER]
  --ollama-url TEXT   Ollama base URL  [default: env OLLAMA_BASE_URL]
  --threshold FLOAT   Cases below this score are treated as weak  [default: 0.7]
  --output-dir PATH   Directory for candidate prompt files
                      [default: agents/prompts/{agent}/candidates/]
  --help
```

**Behaviour**:
1. Reads failing/low-scoring cases from `--report`.
2. Calls Anthropic API with the current system/user prompt + failure context.
3. Writes `system_candidate_{timestamp}.md` and `user_candidate_{timestamp}.md.j2` to `--output-dir`.
4. Prints a diff-style summary of proposed changes to stdout.

**stdout**:
```
Generated 2 candidate prompt files in agents/prompts/screener/candidates/
  system_candidate_20260308T120000.md
  user_candidate_20260308T120000.md.j2

Review changes, then re-run `agent-eval evaluate` to validate improvement.
```

---

## Error format

All errors print to stderr with a `[ERROR]` prefix and exit with a non-zero code:

```
[ERROR] Test suite file not found: /path/to/suite.jsonl
```
