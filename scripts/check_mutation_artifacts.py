#!/usr/bin/env python3
"""Block mutation-testing artifacts from entering the source tree.

Mutation testing rewrites source in place. If a run is interrupted — or is
invoked outside ``scripts/run-mutation-safe.sh`` — the mutated files stay in the
working tree and can be committed.

That failure is uniquely dangerous, because a *surviving* mutant is by
definition one the test suite cannot detect. Committing survivors produces a
codebase that is green and broken at the same time. It happened here: commit
``ecc32de`` — which introduced cosmic-ray, before the isolation wrapper existed
— carried 60+ mutants into ``backend/src``, where they sat undetected through
five feature releases while 1104 tests passed.

This scanner looks for constructs cosmic-ray emits that a person is very
unlikely to write deliberately. It is intentionally high-precision rather than
exhaustive: a commit-blocking check that cries wolf gets disabled.

Usage:
    python3 scripts/check_mutation_artifacts.py [PATH ...]

With no arguments every tracked source root is scanned. pre-commit passes the
staged filenames. Exits non-zero when an artifact is found.

Escape hatch: append ``# cosmic-ray-ok: <reason>`` to a line that legitimately
matches. The reason is required so the exemption is reviewable.
"""

from __future__ import annotations

import io
import re
import sys
import tokenize
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_ROOTS = (
    "backend/src",
    "backend/tests",
    "db/src",
    "agents/src",
    "agent-eval/src",
    "researcher-mcp/src",
)

ALLOW_MARKER = "cosmic-ray-ok:"

# Each signature is (name, compiled pattern, why it matters).
#
# Ordering is by confidence: the first three cannot plausibly be hand-written;
# the last two are idiom violations that are overwhelmingly mutation-caused in
# a SQLAlchemy codebase.
SIGNATURES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "cosmic-ray exception class",
        re.compile(r"\bCosmicRayTestingException\b"),
        "cosmic-ray's internal exception type; the name is undefined at runtime, "
        "so the handler raises NameError and masks the real error",
    ),
    (
        "double negation",
        re.compile(r"\bnot\s+not\b"),
        "cosmic-ray negates a condition by prefixing 'not'; two of them mean a "
        "mutant landed on an already-negated expression",
    ),
    (
        "loop over an empty literal",
        re.compile(r"\bfor\s+\w+\s+in\s+\[\]\s*:"),
        "the loop body is unreachable — cosmic-ray blanks an iterable to prove "
        "the loop is untested",
    ),
    (
        "identity comparison against a value",
        re.compile(r"\b[A-Z]\w*\.\w+\s+is(?:\s+not)?\s+(?!None\b|True\b|False\b)[a-z_]\w*"),
        "'is' compares object identity; on a SQLAlchemy column it yields a plain "
        "bool instead of a SQL clause, silently matching every row or none",
    ),
    (
        "ordering comparison on an identity column",
        re.compile(
            r"\b[A-Z]\w*\.(?:id|\w+_id|doi|uuid|token|role|email|username)\s*"
            r"(?:>=|<=|(?<![<>=!])>(?!=)|(?<![<>=!])<(?!=))\s"
        ),
        "identity columns are matched with '==', never ordered; an inequality "
        "here selects the wrong rows and can raise MultipleResultsFound",
    ),
)

SOURCE_SUFFIXES = {".py"}


def _code_only_lines(text: str) -> list[str]:
    """Blank out string literals and comments, keeping line and column numbers.

    Docstrings describing an attribute — "TemplateRenderError.variable_name is
    populated with…" — read exactly like an identity comparison. Matching prose
    would make this check cry wolf, and a commit-blocking check that cries wolf
    gets disabled. So the patterns only ever see executable code.

    Args:
        text: Full source of a Python file.

    Returns:
        The file's lines with every STRING and COMMENT token replaced by spaces.
        Falls back to the raw lines if the file does not tokenize.

    """
    lines = text.splitlines()
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return lines

    grid = [list(line) for line in lines]
    for tok in tokens:
        if tok.type not in (tokenize.STRING, tokenize.COMMENT):
            continue
        (srow, scol), (erow, ecol) = tok.start, tok.end
        for row in range(srow, erow + 1):
            if not 1 <= row <= len(grid):
                continue
            cells = grid[row - 1]
            begin = scol if row == srow else 0
            finish = ecol if row == erow else len(cells)
            for col in range(begin, min(finish, len(cells))):
                cells[col] = " "
    return ["".join(cells) for cells in grid]


def scan_file(path: Path) -> list[tuple[int, str, str, str]]:
    """Scan one file for mutation artifacts.

    Args:
        path: Source file to read.

    Returns:
        One ``(line_number, signature_name, explanation, source_line)`` tuple
        per finding. Lines carrying the ``cosmic-ray-ok:`` marker are skipped.

    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    raw = text.splitlines()
    code = _code_only_lines(text)

    findings: list[tuple[int, str, str, str]] = []
    for lineno, code_line in enumerate(code, start=1):
        original = raw[lineno - 1] if lineno <= len(raw) else ""
        if ALLOW_MARKER in original:
            continue
        for name, pattern, why in SIGNATURES:
            if pattern.search(code_line):
                findings.append((lineno, name, why, original.strip()))
                break
    return findings


def _candidate_files(argv: list[str]) -> list[Path]:
    """Resolve the files to scan from CLI arguments, or from the default roots."""
    if argv:
        return [Path(a) for a in argv if Path(a).suffix in SOURCE_SUFFIXES and Path(a).is_file()]
    files: list[Path] = []
    for root in DEFAULT_ROOTS:
        base = REPO_ROOT / root
        if base.is_dir():
            files.extend(sorted(base.rglob("*.py")))
    return files


def main(argv: list[str]) -> int:
    """Scan the requested files and report any artifacts found.

    Args:
        argv: Explicit paths to scan; empty means scan every default root.

    Returns:
        0 when the tree is clean, 1 when at least one artifact is present.

    """
    files = _candidate_files(argv)
    total = 0

    for path in files:
        for lineno, name, why, line in scan_file(path):
            if total == 0:
                print("Mutation-testing artifacts found in source:\n", file=sys.stderr)
            total += 1
            try:
                shown: Path = path.relative_to(REPO_ROOT)
            except ValueError:
                shown = path
            print(f"  {shown}:{lineno}  [{name}]", file=sys.stderr)
            print(f"      {line}", file=sys.stderr)
            print(f"      why: {why}\n", file=sys.stderr)

    if total:
        print(
            f"{total} artifact(s) found across {len(files)} scanned file(s).\n\n"
            "Mutation testing must never run against the real working tree. Use:\n"
            "    ./scripts/run-mutation-safe.sh <package>\n"
            "which applies mutations inside a throwaway git worktree.\n\n"
            "To recover a tree that was mutated in place:\n"
            "    git diff            # review every change before discarding\n"
            "    git checkout -- <file>\n\n"
            "If a flagged line is genuinely intended, append a justification:\n"
            f"    # {ALLOW_MARKER} <reason>",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
