"""report command: display or export a saved EvalReport."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from agent_eval.models import EvalReport

console = Console()
err_console = Console(stderr=True)


def run_report(
    report_path: Path = typer.Argument(..., help="Path to EvalReport JSON file"),
    format: str = typer.Option("table", help="Output format: table|json|markdown"),
    output: Path = typer.Option(None, help="Write formatted report to file"),
) -> None:
    """Display or export results from a previous evaluation run."""
    try:
        data = json.loads(report_path.read_text())
        report = EvalReport.model_validate(data)
    except FileNotFoundError:
        err_console.print(f"[ERROR] Report file not found: {report_path}")
        raise typer.Exit(code=2) from None
    except (json.JSONDecodeError, ValueError) as exc:
        err_console.print(f"[ERROR] Invalid report file: {exc}")
        raise typer.Exit(code=2) from None

    if format == "json":
        rendered = report.model_dump_json(indent=2)
    elif format == "markdown":
        lines = [
            f"# Evaluation Report: {report.agent_type}",
            f"**Run ID**: {report.run_id}",
            f"**Overall Score**: {report.overall_score:.3f}",
            "",
            "| Case ID | Score | Passed |",
            "|---------|-------|--------|",
        ]
        for tc in report.test_cases:
            scores_str = ", ".join(f"{k}={v:.2f}" for k, v in tc.scores.items())
            lines.append(f"| {tc.case_id} | {scores_str} | {'✓' if tc.passed else '✗'} |")
        rendered = "\n".join(lines)
    else:
        table = Table(title=f"Report: {report.agent_type} (run {report.run_id})")
        table.add_column("Case ID")
        table.add_column("Score")
        table.add_column("Passed")
        for tc in report.test_cases:
            scores_str = ", ".join(f"{k}={v:.2f}" for k, v in tc.scores.items())
            table.add_row(tc.case_id, scores_str, "✓" if tc.passed else "✗")
        console.print(table)
        console.print(f"Overall: {report.overall_score:.3f}")
        if output:
            tmp_console = Console(file=output.open("w"))
            tmp_console.print(table)
        return

    if output:
        output.write_text(rendered)
        console.print(f"Report written to: {output}")
    else:
        console.print(rendered)
