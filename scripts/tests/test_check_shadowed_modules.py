"""Unit tests for scripts/check_shadowed_modules.py.

The check is a commit gate, so both directions matter: it must catch a module a
package shadows, and must stay silent on the ordinary layouts that fill this
repository — a package with no same-named sibling, and a plain module with no
same-named package.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).resolve().parent.parent / "check_shadowed_modules.py"
_spec = importlib.util.spec_from_file_location("check_shadowed_modules", _MODULE_PATH)
assert _spec is not None and _spec.loader is not None
csm = importlib.util.module_from_spec(_spec)
sys.modules["check_shadowed_modules"] = csm
_spec.loader.exec_module(csm)


def _root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    """Point the checker at tmp_path and return the relative root name."""
    monkeypatch.setattr(csm, "REPO_ROOT", tmp_path)
    (tmp_path / "src").mkdir()
    return "src"


def test_detects_a_module_shadowed_by_a_package(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A file X.py beside a package X/ is reported."""
    # Arrange
    root = _root(tmp_path, monkeypatch)
    src = tmp_path / root
    (src / "admin").mkdir()
    (src / "admin" / "__init__.py").write_text("router = 1\n")
    (src / "admin.py").write_text("router = 2\n")

    # Act
    findings = csm.find_shadowed_modules([root])

    # Assert
    assert [(d.name, i.parent.name) for d, i in findings] == [("admin.py", "admin")]


def test_package_without_a_twin_module_is_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The ordinary layout — a package and no same-named sibling — passes."""
    # Arrange
    root = _root(tmp_path, monkeypatch)
    src = tmp_path / root
    (src / "services").mkdir()
    (src / "services" / "__init__.py").write_text("")
    (src / "services" / "audit.py").write_text("def record(): ...\n")

    # Act
    findings = csm.find_shadowed_modules([root])

    # Assert
    assert findings == []


def test_module_without_a_twin_package_is_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sibling modules with similar names do not shadow each other.

    `audit.py` and `audit_service.py` coexist in this repository and are
    distinct live modules; neither shadows the other.
    """
    # Arrange
    root = _root(tmp_path, monkeypatch)
    src = tmp_path / root
    (src / "audit.py").write_text("def record(): ...\n")
    (src / "audit_service.py").write_text("def log(): ...\n")

    # Act
    findings = csm.find_shadowed_modules([root])

    # Assert
    assert findings == []


def test_directory_without_init_does_not_shadow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A plain directory is not a package, so it shadows nothing."""
    # Arrange
    root = _root(tmp_path, monkeypatch)
    src = tmp_path / root
    (src / "fixtures").mkdir()
    (src / "fixtures" / "data.json").write_text("{}")
    (src / "fixtures.py").write_text("PATH = 'fixtures'\n")

    # Act
    findings = csm.find_shadowed_modules([root])

    # Assert
    assert findings == []


def test_finds_shadowing_nested_deep_in_a_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Detection is not limited to the top level of a source root."""
    # Arrange
    root = _root(tmp_path, monkeypatch)
    deep = tmp_path / root / "backend" / "api" / "v1"
    deep.mkdir(parents=True)
    (deep / "admin").mkdir()
    (deep / "admin" / "__init__.py").write_text("")
    (deep / "admin.py").write_text("")

    # Act
    findings = csm.find_shadowed_modules([root])

    # Assert
    assert len(findings) == 1
    assert findings[0][0] == deep / "admin.py"


def test_missing_root_is_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A configured root that does not exist is not an error."""
    # Arrange
    monkeypatch.setattr(csm, "REPO_ROOT", tmp_path)

    # Act
    findings = csm.find_shadowed_modules(["does-not-exist"])

    # Assert
    assert findings == []


def test_main_returns_zero_on_a_clean_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A clean tree exits 0 so the commit proceeds."""
    # Arrange
    root = _root(tmp_path, monkeypatch)
    (tmp_path / root / "module.py").write_text("")

    # Act
    code = csm.main([root])

    # Assert
    assert code == 0


def test_main_returns_one_when_a_module_is_shadowed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A shadowed module exits non-zero so the commit is blocked."""
    # Arrange
    root = _root(tmp_path, monkeypatch)
    src = tmp_path / root
    (src / "models").mkdir()
    (src / "models" / "__init__.py").write_text("")
    (src / "models.py").write_text("")

    # Act
    code = csm.main([root])

    # Assert
    assert code == 1


def test_repository_itself_has_no_shadowed_modules() -> None:
    """Regression guard: the real tree stays clean after the 2026-08-06 deletions."""
    # Act
    findings = csm.find_shadowed_modules(csm.SOURCE_ROOTS)

    # Assert
    assert findings == [], f"shadowed modules reappeared: {findings}"
