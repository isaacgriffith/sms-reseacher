"""Report frontend modules that nothing can reach from the application entry point.

A component can compile, pass its unit tests, and call a working endpoint while
being unreachable by any user — because no route registers it and no rendered
component imports it. Five defects of that shape were found on 2026-08-06 (see
docs/feature-gaps.md, "Built-but-never-wired audit"), which is why this exists.

The check is a reachability walk over the static import graph of ``frontend/src``
starting at ``main.tsx``. Test files are excluded from the graph: a module
imported only by its own test is still dead.

Exits non-zero when unreachable modules are found, so it can gate CI.

Usage::

    python3 scripts/audit_unreachable_frontend.py [--src frontend/src]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

#: Modules that are entry points in their own right and so are never "dead".
ENTRY_POINTS = ("main.tsx", "App.tsx")

#: Tooling entry points that nothing in the app imports by design.
ALLOWED_ORPHANS = ("test-setup.ts",)

_SOURCE_SUFFIXES = (".ts", ".tsx")

#: ``from './x'`` and ``import('./x')``, relative specifiers only — a package
#: import cannot point back into src.
_IMPORT_RE = re.compile(r"""(?:from|import)\s*\(?\s*['"](\.[^'"]+)['"]""")


def is_source(path: Path) -> bool:
    """Return True if *path* is an app source file rather than a test or typing stub.

    Args:
        path: Candidate file.

    Returns:
        True when the file participates in the app's import graph.

    """
    text = str(path)
    return (
        path.suffix in _SOURCE_SUFFIXES
        and "__tests__" not in text
        and ".test." not in text
        and not text.endswith(".d.ts")
    )


def resolve(importer: Path, spec: str) -> Path | None:
    """Resolve a relative import *spec* written in *importer* to a file on disk.

    Mirrors the resolution order bundlers use: exact file, then ``.ts`` /
    ``.tsx``, then a directory's ``index`` module.

    Args:
        importer: File containing the import statement.
        spec: The relative specifier, e.g. ``"../components/Foo"``.

    Returns:
        The resolved path, or None when nothing matches (an external package, a
        CSS import, or a broken specifier).

    """
    base = importer.parent / spec
    candidates = (
        base,
        base.with_suffix(".ts"),
        base.with_suffix(".tsx"),
        base / "index.ts",
        base / "index.tsx",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def build_graph(src: Path) -> dict[Path, set[Path]]:
    """Return a map of source file to the source files it imports.

    Args:
        src: The ``frontend/src`` directory.

    Returns:
        Adjacency mapping keyed by resolved path.

    """
    graph: dict[Path, set[Path]] = {}
    for path in src.rglob("*"):
        if not is_source(path):
            continue
        deps: set[Path] = set()
        for spec in _IMPORT_RE.findall(path.read_text()):
            resolved = resolve(path, spec)
            if resolved is not None:
                deps.add(resolved)
        graph[path.resolve()] = deps
    return graph


def find_unreachable(src: Path) -> list[Path]:
    """Return source modules unreachable from the entry points, sorted by path.

    Args:
        src: The ``frontend/src`` directory.

    Returns:
        Unreachable modules, excluding entry points and known tooling orphans.

    """
    graph = build_graph(src)

    stack = [(src / name).resolve() for name in ENTRY_POINTS if (src / name).is_file()]
    reachable = set(stack)
    while stack:
        for dep in graph.get(stack.pop(), ()):
            if dep not in reachable:
                reachable.add(dep)
                stack.append(dep)

    return sorted(
        path
        for path in graph
        if path not in reachable and path.name not in ALLOWED_ORPHANS
    )


def main() -> int:
    """Print unreachable modules and return a process exit code.

    Returns:
        1 when unreachable modules were found, else 0.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--src",
        type=Path,
        default=Path("frontend/src"),
        help="Path to the frontend source root (default: frontend/src)",
    )
    args = parser.parse_args()

    if not args.src.is_dir():
        print(f"not a directory: {args.src}", file=sys.stderr)
        return 2

    unreachable = find_unreachable(args.src)
    if not unreachable:
        print("No unreachable frontend modules.")
        return 0

    print(f"{len(unreachable)} modules unreachable from {' / '.join(ENTRY_POINTS)}:\n")
    cwd = Path.cwd()
    for path in unreachable:
        shown = path.relative_to(cwd) if path.is_relative_to(cwd) else path
        print(f"  {shown}")
    print("\nSee docs/feature-gaps.md — 'Built-but-never-wired audit'.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
