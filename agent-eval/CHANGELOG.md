# Changelog — sms-agent-eval

All notable changes to this subproject are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — feature/005-models-and-agents

### Added
- **`pipelines/agent_generator_eval.py`**: DeepEval evaluation pipeline for
  `AgentGeneratorAgent`; dataset of 5 representative role/persona inputs; metrics:
  `AnswerRelevancyMetric` (generated message must reference role name) and
  `FaithfulnessMetric` (no hallucinated variable names); minimum threshold 0.8

---

## [Unreleased] — feature/003-project-setup-improvements

### Changed
- Coverage command documented in `CLAUDE.md`:
  `uv run pytest agent-eval/tests/ --cov=agent_eval`
- Mutation testing tool updated to `cosmic-ray` (was `mutmut`); run via manual GitHub
  Actions `workflow_dispatch` workflow
- `pytest` build gate enforced: skip/xfail markers without `reason=` cause the run to fail

---

## [0.2.0] — 2026-03-12 — feature/002-sms-workflow

### Added
- `evaluate` command — runs a JSONL test suite against a named agent with a pass/fail
  threshold; exits `0` (all pass), `1` (cases fail), or `2` (config error)
- `report` command — displays a saved evaluation report in `table`, `markdown`, or `json`
  format; supports `--output` to write to file
- `compare` command — compares two evaluation runs and shows per-metric deltas
- `improve` command — uses LLM feedback to generate candidate prompt revisions written
  to `agents/prompts/{agent}/candidates/`
- `EvalReport` and `TestCaseResult` Pydantic models (`src/agent_eval/models.py`)
- `LiteLLMJudge` — `DeepEvalBaseLLM` wrapper routing judge calls through LiteLLM
- `agent-eval` CLI entry point via `uv run agent-eval`
- Unit tests for CLI help output and model validation

---

## [0.1.0] — 2026-03-11 — feature/001-repo-setup

### Added
- Initial `pyproject.toml` (`sms-agent-eval`) as UV workspace member
- Ruff, MyPy strict, pytest + pytest-asyncio configuration
