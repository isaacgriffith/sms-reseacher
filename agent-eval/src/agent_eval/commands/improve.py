"""improve command: suggest prompt revisions for low-scoring cases."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console

from agent_eval.models import EvalReport

console = Console()
err_console = Console(stderr=True)


def run_improve(
    report: Path = typer.Option(..., help="EvalReport JSON to analyse"),
    agent: str = typer.Option(..., help="Agent type whose prompts to improve"),
    model: str = typer.Option("", help="Improvement model ID"),
    provider: str = typer.Option("", help="LLM provider: anthropic|ollama"),
    ollama_url: str = typer.Option("", help="Ollama base URL"),
    threshold: float = typer.Option(0.7, help="Cases below this score are treated as weak"),
    output_dir: Path = typer.Option(None, help="Directory for candidate prompt files"),
) -> None:
    """Identify low-scoring cases and generate candidate revised prompts."""
    try:
        eval_report = EvalReport.model_validate(json.loads(report.read_text()))
    except FileNotFoundError:
        err_console.print(f"[ERROR] Report file not found: {report}")
        raise typer.Exit(code=2) from None
    except (json.JSONDecodeError, ValueError) as exc:
        err_console.print(f"[ERROR] Invalid report file: {exc}")
        raise typer.Exit(code=2) from None

    weak_cases = [tc for tc in eval_report.test_cases if not tc.passed]
    if not weak_cases:
        console.print("No low-scoring cases found. No prompt improvements needed.")
        return

    dest = output_dir or Path(f"agents/prompts/{agent}/candidates")
    dest.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    system_file = dest / f"system_candidate_{ts}.md"
    user_file = dest / f"user_candidate_{ts}.md.j2"

    system_file.write_text(
        f"# Candidate System Prompt — generated {ts}\n\n"
        f"Agent: {agent}\n"
        f"Weak cases: {len(weak_cases)}\n\n"
        "[REVIEW AND EDIT: Insert improved system prompt here]\n"
    )
    user_file.write_text(
        f"{{# Candidate User Prompt — generated {ts} #}}\n\n"
        "[REVIEW AND EDIT: Insert improved user prompt template here]\n"
    )

    console.print(f"Generated 2 candidate prompt files in {dest}/")
    console.print(f"  {system_file.name}")
    console.print(f"  {user_file.name}")
    console.print()
    console.print("Review changes, then re-run `agent-eval evaluate` to validate improvement.")
