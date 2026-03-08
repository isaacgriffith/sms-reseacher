"""SMS Researcher — Agent Evaluation CLI."""

from __future__ import annotations

import typer

from agent_eval.commands.compare import run_compare
from agent_eval.commands.evaluate import run_evaluate
from agent_eval.commands.improve import run_improve
from agent_eval.commands.report import run_report

app = typer.Typer(
    name="agent-eval",
    help="SMS Researcher — Agent Evaluation CLI",
    no_args_is_help=True,
)

app.command("evaluate")(run_evaluate)
app.command("report")(run_report)
app.command("compare")(run_compare)
app.command("improve")(run_improve)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo("agent-eval 0.1.0")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """SMS Researcher — Agent Evaluation CLI."""
