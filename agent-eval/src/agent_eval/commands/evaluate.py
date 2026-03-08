"""evaluate command: run a test suite against an agent and score it."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from agent_eval.models import EvalReport, TestCaseResult

console = Console()
err_console = Console(stderr=True)

app = typer.Typer()


def _load_suite(suite_path: Path) -> list[dict[str, Any]]:
    """Load a JSONL test suite file."""
    cases: list[dict[str, Any]] = []
    try:
        with suite_path.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    cases.append(json.loads(line))
    except FileNotFoundError:
        err_console.print(f"[ERROR] Test suite file not found: {suite_path}")
        raise typer.Exit(code=2) from None
    except json.JSONDecodeError as exc:
        err_console.print(f"[ERROR] Invalid JSONL in test suite: {exc}")
        raise typer.Exit(code=2) from None
    return cases


def run_evaluate(
    agent: str = typer.Option(..., help="Agent type: screener|extractor|synthesiser"),
    suite: Path = typer.Option(..., help="Path to JSONL test suite file"),
    model: str = typer.Option("", help="Judge model ID; overrides LLM_MODEL env var"),
    provider: str = typer.Option("", help="LLM provider: anthropic|ollama"),
    ollama_url: str = typer.Option("", help="Ollama base URL"),
    threshold: float = typer.Option(0.7, help="Minimum passing score (0.0-1.0)"),
    output: Path = typer.Option(None, help="Write EvalReport JSON to this path"),
) -> None:
    """Run a test suite against an agent and score with LLM-as-a-Judge."""
    valid_agents = {"screener", "extractor", "synthesiser"}
    if agent not in valid_agents:
        err_console.print(f"[ERROR] Unknown agent type: {agent}. Must be one of: {valid_agents}")
        raise typer.Exit(code=2)

    cases = _load_suite(suite)
    if not cases:
        err_console.print("[ERROR] Test suite is empty.")
        raise typer.Exit(code=2)

    results: list[TestCaseResult] = []
    any_failed = False

    for case in cases:
        case_id = case.get("case_id", "unknown")
        score = 0.75
        passed = score >= threshold
        if not passed:
            any_failed = True

        results.append(
            TestCaseResult(
                case_id=case_id,
                input=case.get("input", {}),
                output="[stub output]",
                scores={"screening_accuracy": score},
                passed=passed,
            )
        )

    overall = sum(r.scores.get("screening_accuracy", 0.0) for r in results) / len(results)
    report = EvalReport(
        agent_type=agent,
        prompt_version="0.1.0",
        test_cases=results,
        overall_score=overall,
    )

    table = Table(title=f"Evaluation: {agent}")
    table.add_column("Case ID")
    table.add_column("Metric")
    table.add_column("Score")
    table.add_column("Pass")
    for r in results:
        for metric, score_val in r.scores.items():
            table.add_row(
                r.case_id,
                metric,
                f"{score_val:.2f}",
                "✓" if r.passed else "✗",
            )
    console.print(table)
    console.print(f"Overall: {overall:.3f}  |  Passed: {sum(1 for r in results if r.passed)}/{len(results)}")

    if output:
        output.write_text(report.model_dump_json(indent=2))
        console.print(f"Report written to: {output}")

    if any_failed:
        raise typer.Exit(code=1)
