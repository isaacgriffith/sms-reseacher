"""Unit tests for scripts/check_mutation_artifacts.py.

This scanner blocks commits, so its precision matters as much as its recall: a
check that flags legitimate code gets switched off, and then it protects
nothing. The false-positive cases below are therefore as load-bearing as the
detection cases.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).resolve().parent.parent / "check_mutation_artifacts.py"
_spec = importlib.util.spec_from_file_location("check_mutation_artifacts", _MODULE_PATH)
assert _spec is not None and _spec.loader is not None
cma = importlib.util.module_from_spec(_spec)
sys.modules["check_mutation_artifacts"] = cma
_spec.loader.exec_module(cma)


def _write(tmp_path: Path, source: str) -> Path:
    """Write a synthetic module and return its path."""
    target = tmp_path / "sample.py"
    target.write_text(source, encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# Detection — each signature the scanner claims to catch
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "source"),
    [
        (
            "cosmic-ray exception class",
            "try:\n    go()\nexcept CosmicRayTestingException as exc:\n    pass\n",
        ),
        ("double negation", "if not not ready:\n    go()\n"),
        ("loop over an empty literal", "for chart in []:\n    draw(chart)\n"),
        (
            "identity comparison against a value",
            "q = select(Study).where(Study.id is study_id)\n",
        ),
        (
            "ordering comparison on an identity column",
            "q = select(Paper).where(Paper.doi > doi)\n",
        ),
    ],
)
def test_detects_each_signature(tmp_path: Path, name: str, source: str) -> None:
    """Every declared signature is found in code that exhibits it."""
    # Arrange
    target = _write(tmp_path, source)

    # Act
    findings = cma.scan_file(target)

    # Assert
    assert [f[1] for f in findings] == [name]


def test_reports_line_number_and_source_line(tmp_path: Path) -> None:
    """A finding carries the 1-indexed line and the original source text."""
    # Arrange
    target = _write(tmp_path, "x = 1\n\nq = select(Paper).where(Paper.doi > doi)\n")

    # Act
    findings = cma.scan_file(target)

    # Assert
    assert len(findings) == 1
    lineno, _name, _why, line = findings[0]
    assert lineno == 3
    assert line == "q = select(Paper).where(Paper.doi > doi)"


# ---------------------------------------------------------------------------
# Precision — the cases that would make the gate untrustworthy
# ---------------------------------------------------------------------------


def test_ignores_prose_in_docstrings(tmp_path: Path) -> None:
    """Prose describing an attribute is not an identity comparison.

    A docstring reading "WorkerSettings.functions is a non-empty list" matches
    the identity pattern textually. Flagging it produced four false positives on
    an otherwise clean tree, which is exactly how a commit gate loses its
    credibility.
    """
    # Arrange
    target = _write(
        tmp_path,
        '"""WorkerSettings.functions is a non-empty list of job callables."""\n'
        "\n"
        "def f():\n"
        '    """TemplateRenderError.variable_name is populated with the name."""\n'
        "    return 1\n",
    )

    # Act
    findings = cma.scan_file(target)

    # Assert
    assert findings == []


def test_ignores_signatures_inside_string_literals(tmp_path: Path) -> None:
    """A signature quoted in a string is data, not code."""
    # Arrange
    target = _write(tmp_path, 'MESSAGE = "raises CosmicRayTestingException on failure"\n')

    # Act
    findings = cma.scan_file(target)

    # Assert
    assert findings == []


def test_ignores_comment_lines(tmp_path: Path) -> None:
    """A signature written in a comment is not executable code."""
    # Arrange
    target = _write(tmp_path, "# for chart in []:  historical note\nvalue = 1\n")

    # Act
    findings = cma.scan_file(target)

    # Assert
    assert findings == []


def test_allow_marker_suppresses_a_finding(tmp_path: Path) -> None:
    """An explicit, justified exemption is honoured."""
    # Arrange
    target = _write(
        tmp_path,
        "rows = select(Paper).where(Paper.id > cursor)  # cosmic-ray-ok: keyset pagination\n",
    )

    # Act
    findings = cma.scan_file(target)

    # Assert
    assert findings == []


def test_equality_comparisons_are_never_flagged(tmp_path: Path) -> None:
    """The idiomatic form the scanner steers towards must pass cleanly."""
    # Arrange
    target = _write(
        tmp_path,
        "q = select(Paper).where(Paper.doi == doi)\n"
        "r = select(Study).where(Study.id == study_id)\n"
        "if value is None:\n"
        "    value = fetch()\n"
        "if other is not None:\n"
        "    use(other)\n",
    )

    # Act
    findings = cma.scan_file(target)

    # Assert
    assert findings == []


def test_unparseable_source_does_not_crash(tmp_path: Path) -> None:
    """A syntactically invalid file degrades to raw-line scanning."""
    # Arrange
    target = _write(tmp_path, "def broken(:\n    q = select(Paper).where(Paper.doi > doi)\n")

    # Act
    findings = cma.scan_file(target)

    # Assert — still detected, via the raw-line fallback
    assert [f[1] for f in findings] == ["ordering comparison on an identity column"]


def test_unreadable_file_returns_no_findings(tmp_path: Path) -> None:
    """A path that cannot be decoded is skipped rather than raising."""
    # Arrange
    target = tmp_path / "binary.py"
    target.write_bytes(b"\xff\xfe\x00binary")

    # Act
    findings = cma.scan_file(target)

    # Assert
    assert findings == []


# ---------------------------------------------------------------------------
# CLI contract
# ---------------------------------------------------------------------------


def test_main_returns_zero_for_clean_file(tmp_path: Path) -> None:
    """A clean tree exits 0 so the commit proceeds."""
    # Arrange
    target = _write(tmp_path, "q = select(Paper).where(Paper.doi == doi)\n")

    # Act
    code = cma.main([str(target)])

    # Assert
    assert code == 0


def test_main_returns_one_when_an_artifact_is_present(tmp_path: Path) -> None:
    """An artifact exits non-zero so the commit is blocked."""
    # Arrange
    target = _write(tmp_path, "q = select(Paper).where(Paper.doi > doi)\n")

    # Act
    code = cma.main([str(target)])

    # Assert
    assert code == 1


def test_main_ignores_non_python_arguments(tmp_path: Path) -> None:
    """pre-commit may pass paths this scanner does not handle."""
    # Arrange
    other = tmp_path / "notes.md"
    other.write_text("Paper.doi > doi\n", encoding="utf-8")

    # Act
    code = cma.main([str(other)])

    # Assert
    assert code == 0
