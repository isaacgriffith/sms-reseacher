"""compare command: compare scores between two evaluation runs."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from agent_eval.models import EvalReport

console = Console()
err_console = Console(stderr=True)


def _load_report(path: Path) -> EvalReport:
    """Load an EvalReport from a JSON file."""
    try:
        return EvalReport.model_validate(json.loads(path.read_text()))
    except FileNotFoundError:
        err_console.print(f"[ERROR] Report file not found: {path}")
        raise typer.Exit(code=2) from None
    except (json.JSONDecodeError, ValueError) as exc:
        err_console.print(f"[ERROR] Invalid report file {path}: {exc}")
        raise typer.Exit(code=2) from None


def run_compare(
    baseline: Path = typer.Argument(..., help="Path to baseline EvalReport JSON"),
    candidate: Path = typer.Argument(..., help="Path to candidate EvalReport JSON"),
    output: Path = typer.Option(None, help="Write comparison table to file"),
) -> None:
    """Compare scores between two evaluation runs or prompt variants."""
    base_report = _load_report(baseline)
    cand_report = _load_report(candidate)

    base_scores: dict[str, float] = {}
    for tc in base_report.test_cases:
        for metric, score in tc.scores.items():
            base_scores.setdefault(metric, 0.0)
            base_scores[metric] += score
    if base_report.test_cases:
        for k in base_scores:
            base_scores[k] /= len(base_report.test_cases)

    cand_scores: dict[str, float] = {}
    for tc in cand_report.test_cases:
        for metric, score in tc.scores.items():
            cand_scores.setdefault(metric, 0.0)
            cand_scores[metric] += score
    if cand_report.test_cases:
        for k in cand_scores:
            cand_scores[k] /= len(cand_report.test_cases)

    all_metrics = sorted(set(base_scores) | set(cand_scores))

    table = Table(title="Comparison: Baseline vs Candidate")
    table.add_column("Metric")
    table.add_column("Baseline")
    table.add_column("Candidate")
    table.add_column("Delta")

    for metric in all_metrics:
        b = base_scores.get(metric, 0.0)
        c = cand_scores.get(metric, 0.0)
        delta = c - b
        arrow = "↑" if delta >= 0 else "↓"
        sign = "+" if delta >= 0 else ""
        table.add_row(metric, f"{b:.2f}", f"{c:.2f}", f"{sign}{delta:.2f} {arrow}")

    console.print(table)

    if output:
        lines = ["Metric,Baseline,Candidate,Delta"]
        for metric in all_metrics:
            b = base_scores.get(metric, 0.0)
            c = cand_scores.get(metric, 0.0)
            delta = c - b
            sign = "+" if delta >= 0 else ""
            lines.append(f"{metric},{b:.2f},{c:.2f},{sign}{delta:.2f}")
        output.write_text("\n".join(lines))
        console.print(f"Comparison written to: {output}")
