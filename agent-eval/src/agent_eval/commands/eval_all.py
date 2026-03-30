"""eval all command: run all deepeval agent pipelines and produce a combined report."""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

console = Console()
err_console = Console(stderr=True)

# Registry: agent name → (run_function, module_path)
_PIPELINE_REGISTRY: list[tuple[str, str]] = [
    ("librarian", "agent_eval.evals.librarian_eval"),
    ("expert", "agent_eval.evals.expert_eval"),
    ("search_builder", "agent_eval.evals.search_builder_eval"),
    ("domain_modeler", "agent_eval.evals.domain_modeler_eval"),
    ("quality_judge", "agent_eval.evals.quality_judge_eval"),
    ("validity", "agent_eval.evals.validity_eval"),
    ("screener", "agent_eval.evals.screener_eval"),
    ("extractor", "agent_eval.evals.extractor_eval"),
    ("synthesiser", "agent_eval.evals.synthesiser_eval"),
]

# Map agent name → run function name in each eval module
_RUN_FN: dict[str, str] = {
    "librarian": "run_librarian_eval",
    "expert": "run_expert_eval",
    "search_builder": "run_search_builder_eval",
    "domain_modeler": "run_domain_modeler_eval",
    "quality_judge": "run_quality_judge_eval",
    "validity": "run_validity_eval",
    "screener": "run_screener_eval",
    "extractor": "run_extractor_eval",
    "synthesiser": "run_synthesiser_eval",
}


def _run_pipeline(agent_name: str, module_path: str, run_agent: bool) -> dict[str, Any]:
    """Import eval module and call its run_*_eval function.

    Args:
        agent_name: Short identifier for the agent (e.g. ``librarian``).
        module_path: Dotted module path (e.g. ``agent_eval.evals.librarian_eval``).
        run_agent: Whether to invoke the live agent (requires LLM credentials).

    Returns:
        Dict with ``{passed, failed, total, errors}`` from the pipeline.

    """
    import importlib

    fn_name = _RUN_FN[agent_name]
    try:
        mod = importlib.import_module(module_path)
        fn = getattr(mod, fn_name)
        return fn(run_agent=run_agent)
    except Exception as exc:  # noqa: BLE001
        return {"passed": 0, "failed": 1, "total": 1, "errors": [str(exc)]}


def run_eval_all(
    run_agent: bool = typer.Option(
        False,
        "--run-agent",
        help="Invoke live agents (requires LLM credentials). Default: stub mode.",
    ),
    output: str = typer.Option(
        "",
        "--output",
        help="Write combined JSON report to this path.",
    ),
) -> None:
    """Run all deepeval agent pipelines in sequence and report combined pass/fail.

    Pipelines: librarian, expert, search_builder, domain_modeler,
    quality_judge, validity, screener, extractor, synthesiser.

    Exit code 0 = all pipelines passed; exit code 1 = one or more failed.
    """
    console.print("[bold]Running all agent evaluation pipelines…[/bold]\n")

    results: list[dict[str, Any]] = []
    any_failed = False

    for agent_name, module_path in _PIPELINE_REGISTRY:
        console.print(f"  ▶ {agent_name}…", end=" ")
        report = _run_pipeline(agent_name, module_path, run_agent=run_agent)
        results.append({"agent": agent_name, **report})

        if report["failed"] > 0:
            any_failed = True
            console.print(f"[red]FAIL ({report['passed']}/{report['total']})[/red]")
        else:
            console.print(f"[green]PASS ({report['passed']}/{report['total']})[/green]")

    # Summary table
    table = Table(title="Combined Eval Report", show_lines=True)
    table.add_column("Agent", style="bold")
    table.add_column("Passed", justify="right")
    table.add_column("Failed", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Status")

    total_passed = total_failed = total_cases = 0
    for r in results:
        status = "[green]✓ PASS[/green]" if r["failed"] == 0 else "[red]✗ FAIL[/red]"
        table.add_row(
            r["agent"],
            str(r["passed"]),
            str(r["failed"]),
            str(r["total"]),
            status,
        )
        total_passed += r["passed"]
        total_failed += r["failed"]
        total_cases += r["total"]

    table.add_section()
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_passed}[/bold]",
        f"[bold]{total_failed}[/bold]",
        f"[bold]{total_cases}[/bold]",
        "[green][bold]PASS[/bold][/green]" if not any_failed else "[red][bold]FAIL[/bold][/red]",
    )

    console.print()
    console.print(table)

    if output:
        combined = {
            "overall": "pass" if not any_failed else "fail",
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_cases": total_cases,
            "pipelines": results,
        }
        with open(output, "w") as f:
            json.dump(combined, f, indent=2)
        console.print(f"\nReport written to: {output}")

    if any_failed:
        raise typer.Exit(code=1)
