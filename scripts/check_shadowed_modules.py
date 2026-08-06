#!/usr/bin/env python3
"""Fail when a Python module is shadowed by a same-named package.

A file ``X.py`` sitting beside a directory ``X/`` that contains ``__init__.py``
is dead code. Python's import system resolves ``import X`` to the package every
time, so nothing in ``X.py`` ever runs.

This is nastier than an unimported frontend component, which at least *looks*
disconnected. A shadowed module sits at the path your editor opens, imports
cleanly on its own, type-checks, passes lint, and can even be unit-tested by
file path — while contributing nothing to the running system. Edits land in a
file that executes nowhere, and no tool complains.

Two existed here, both left by incomplete refactors:

- ``backend/src/backend/api/v1/admin.py`` — feature 005 converted the module
  into a package and left the original behind, declaring its own APIRouter that
  nothing could reach.
- ``db/src/db/models.py`` — created in the same commit as the package that
  shadows it, so it was never once imported.

Both were removed on 2026-08-06. This check exists so the next one fails CI
instead of surviving five releases. See docs/feature-gaps.md, G21.

The frontend has an equivalent oracle in ``scripts/audit_unreachable_frontend.py``;
this is the Python-side counterpart, kept separate because the mechanism differs
— import-system resolution rather than an unreferenced module.

Usage:
    python3 scripts/check_shadowed_modules.py [ROOT ...]

Exits non-zero when a shadowed module is found.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SOURCE_ROOTS = (
    "backend/src",
    "db/src",
    "agents/src",
    "agent-eval/src",
    "researcher-mcp/src",
    "scripts",
)


def find_shadowed_modules(
    roots: tuple[str, ...] | list[str],
) -> list[tuple[Path, Path]]:
    """Find every module shadowed by a same-named package.

    Args:
        roots: Repository-relative directories to search.

    Returns:
        One ``(dead_module, shadowing_package_init)`` pair per finding, sorted
        by the dead module's path.

    """
    findings: list[tuple[Path, Path]] = []
    for root in roots:
        base = REPO_ROOT / root
        if not base.is_dir():
            continue
        for init in base.rglob("__init__.py"):
            package = init.parent
            twin = package.with_suffix(".py")
            if twin.is_file():
                findings.append((twin, init))
    return sorted(findings)


def main(argv: list[str]) -> int:
    """Report any shadowed modules found.

    Args:
        argv: Roots to scan; empty means every default source root.

    Returns:
        0 when no module is shadowed, 1 otherwise.

    """
    roots = tuple(argv) if argv else SOURCE_ROOTS
    findings = find_shadowed_modules(roots)

    if not findings:
        return 0

    print(
        "Shadowed Python modules found — these files never execute:\n", file=sys.stderr
    )
    for dead, init in findings:
        rel_dead = dead.relative_to(REPO_ROOT)
        rel_init = init.relative_to(REPO_ROOT)
        size = dead.stat().st_size
        print(f"  {rel_dead}  ({size:,} bytes)", file=sys.stderr)
        print(f"      shadowed by  {rel_init}", file=sys.stderr)
        print(
            "      the import resolves to the package, never this file\n",
            file=sys.stderr,
        )

    print(
        f"{len(findings)} shadowed module(s).\n\n"
        "A module beside a same-named package is dead: Python resolves the import\n"
        "to the package every time. Confirm the package is a superset, then delete\n"
        "the file:\n\n"
        "    diff <(grep -oE '^(async def|def|class) \\w+' DEAD    | sort) \\\\\n"
        "         <(grep -oE '^(async def|def|class) \\w+' PACKAGE | sort)\n"
        "    git rm DEAD\n\n"
        "If the file holds work the package lacks, move it into the package rather\n"
        "than leaving both in place.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
