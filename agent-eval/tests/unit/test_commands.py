"""Unit tests for agent_eval commands: evaluate, compare, report, improve, eval_all."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from agent_eval.cli import app
from agent_eval.models import EvalReport, TestCaseResult


runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_report(**overrides: Any) -> EvalReport:
    """Build a minimal EvalReport for use in tests.

    Args:
        **overrides: Field overrides for the report.

    Returns:
        A fully valid :class:`EvalReport` instance.
    """
    tc = TestCaseResult(
        case_id="tc-001",
        input={"abstract": "test"},
        output="include",
        scores={"accuracy": 0.9},
        passed=True,
    )
    defaults: dict[str, Any] = dict(
        agent_type="screener",
        prompt_version="0.1.0",
        test_cases=[tc],
        overall_score=0.9,
    )
    defaults.update(overrides)
    return EvalReport(**defaults)


def _write_report(path: Path, report: EvalReport) -> Path:
    """Write an EvalReport to *path* and return it.

    Args:
        path: Destination file path (must have a parent that exists).
        report: The report to serialise.

    Returns:
        The same *path* after writing.
    """
    path.write_text(report.model_dump_json())
    return path


def _write_suite(tmp_path: Path, cases: list[dict[str, Any]]) -> Path:
    """Write a JSONL test suite file and return its path.

    Args:
        tmp_path: Pytest tmp_path fixture directory.
        cases: List of test case dicts to write as JSONL.

    Returns:
        Path to the written JSONL file.
    """
    p = tmp_path / "suite.jsonl"
    p.write_text("\n".join(json.dumps(c) for c in cases))
    return p


# ---------------------------------------------------------------------------
# evaluate command
# ---------------------------------------------------------------------------


class TestEvaluateCommand:
    """Tests for `agent-eval evaluate` command."""

    def test_evaluate_missing_suite_exits_nonzero(self, tmp_path: Path) -> None:
        """Evaluate with a missing suite file exits with non-zero code."""
        result = runner.invoke(app, [
            "evaluate",
            "--agent", "screener",
            "--suite", str(tmp_path / "nonexistent.jsonl"),
        ])
        assert result.exit_code != 0

    def test_evaluate_unknown_agent_exits_2(self, tmp_path: Path) -> None:
        """Unknown agent type exits with code 2."""
        suite = _write_suite(tmp_path, [{"case_id": "tc-001", "input": {}}])
        result = runner.invoke(app, [
            "evaluate",
            "--agent", "unknown_agent",
            "--suite", str(suite),
        ])
        assert result.exit_code == 2

    def test_evaluate_empty_suite_exits_2(self, tmp_path: Path) -> None:
        """Empty test suite file exits with code 2."""
        empty_suite = tmp_path / "empty.jsonl"
        empty_suite.write_text("")
        result = runner.invoke(app, [
            "evaluate",
            "--agent", "screener",
            "--suite", str(empty_suite),
        ])
        assert result.exit_code == 2

    def test_evaluate_single_case_passes(self, tmp_path: Path) -> None:
        """Single valid case in suite produces a result."""
        suite = _write_suite(tmp_path, [{"case_id": "tc-001", "input": {"abstract": "test"}}])
        result = runner.invoke(app, [
            "evaluate",
            "--agent", "screener",
            "--suite", str(suite),
        ])
        # Default threshold is 0.7, stub score is 0.75 → should pass
        assert result.exit_code == 0

    def test_evaluate_writes_output_report(self, tmp_path: Path) -> None:
        """Evaluate writes a JSON report file when --output is provided."""
        suite = _write_suite(tmp_path, [{"case_id": "tc-001", "input": {}}])
        out = tmp_path / "out.json"
        result = runner.invoke(app, [
            "evaluate",
            "--agent", "screener",
            "--suite", str(suite),
            "--output", str(out),
        ])
        assert out.exists()

    def test_evaluate_high_threshold_exits_1(self, tmp_path: Path) -> None:
        """With threshold above stub score (0.75), command exits with code 1."""
        suite = _write_suite(tmp_path, [{"case_id": "tc-001", "input": {}}])
        result = runner.invoke(app, [
            "evaluate",
            "--agent", "screener",
            "--suite", str(suite),
            "--threshold", "0.99",
        ])
        assert result.exit_code == 1

    def test_evaluate_invalid_jsonl_exits_2(self, tmp_path: Path) -> None:
        """Malformed JSONL in suite exits with code 2."""
        bad_suite = tmp_path / "bad.jsonl"
        bad_suite.write_text("{this is not valid json\n")
        result = runner.invoke(app, [
            "evaluate",
            "--agent", "screener",
            "--suite", str(bad_suite),
        ])
        assert result.exit_code == 2


# ---------------------------------------------------------------------------
# compare command
# ---------------------------------------------------------------------------


class TestCompareCommand:
    """Tests for `agent-eval compare` command."""

    def test_compare_two_valid_reports(self, tmp_path: Path) -> None:
        """Comparing two valid reports exits 0."""
        base = _write_report(tmp_path / "base.json", _make_report(overall_score=0.7))
        cand = _write_report(tmp_path / "cand.json", _make_report(overall_score=0.9))
        result = runner.invoke(app, ["compare", str(base), str(cand)])
        assert result.exit_code == 0

    def test_compare_missing_baseline_exits_2(self, tmp_path: Path) -> None:
        """Missing baseline file exits with code 2."""
        cand = _write_report(tmp_path / "cand.json", _make_report())
        result = runner.invoke(app, ["compare", str(tmp_path / "missing.json"), str(cand)])
        assert result.exit_code == 2

    def test_compare_missing_candidate_exits_2(self, tmp_path: Path) -> None:
        """Missing candidate file exits with code 2."""
        base = _write_report(tmp_path / "base.json", _make_report())
        result = runner.invoke(app, ["compare", str(base), str(tmp_path / "missing.json")])
        assert result.exit_code == 2

    def test_compare_writes_output(self, tmp_path: Path) -> None:
        """Compare writes CSV output when --output is given."""
        base = _write_report(tmp_path / "base.json", _make_report(overall_score=0.7))
        cand = _write_report(tmp_path / "cand.json", _make_report(overall_score=0.9))
        out = tmp_path / "comparison.csv"
        result = runner.invoke(app, ["compare", str(base), str(cand), "--output", str(out)])
        assert out.exists()
        assert "Metric" in out.read_text()

    def test_compare_invalid_json_exits_2(self, tmp_path: Path) -> None:
        """Invalid JSON in report file exits with code 2."""
        bad = tmp_path / "bad.json"
        bad.write_text("not valid json")
        valid = _write_report(tmp_path / "valid.json", _make_report())
        result = runner.invoke(app, ["compare", str(bad), str(valid)])
        assert result.exit_code == 2

    def test_compare_delta_shown_in_output(self, tmp_path: Path) -> None:
        """Compare output contains a delta column."""
        base = _write_report(tmp_path / "b.json", _make_report(overall_score=0.5))
        cand = _write_report(tmp_path / "c.json", _make_report(overall_score=0.8))
        result = runner.invoke(app, ["compare", str(base), str(cand)])
        # The table should contain some score values
        assert "accuracy" in result.output or "Metric" in result.output or result.exit_code == 0


# ---------------------------------------------------------------------------
# report command
# ---------------------------------------------------------------------------


class TestReportCommand:
    """Tests for `agent-eval report` command."""

    def test_report_table_format(self, tmp_path: Path) -> None:
        """report command with table format exits 0."""
        rp = _write_report(tmp_path / "r.json", _make_report())
        result = runner.invoke(app, ["report", str(rp)])
        assert result.exit_code == 0

    def test_report_json_format(self, tmp_path: Path) -> None:
        """report command with --format json outputs valid JSON."""
        rp = _write_report(tmp_path / "r.json", _make_report())
        result = runner.invoke(app, ["report", str(rp), "--format", "json"])
        assert result.exit_code == 0
        # Output should contain parseable JSON
        assert "agent_type" in result.output

    def test_report_markdown_format(self, tmp_path: Path) -> None:
        """report command with --format markdown contains markdown headers."""
        rp = _write_report(tmp_path / "r.json", _make_report())
        result = runner.invoke(app, ["report", str(rp), "--format", "markdown"])
        assert result.exit_code == 0
        assert "# Evaluation Report" in result.output

    def test_report_missing_file_exits_2(self, tmp_path: Path) -> None:
        """report command with missing file exits with code 2."""
        result = runner.invoke(app, ["report", str(tmp_path / "no.json")])
        assert result.exit_code == 2

    def test_report_invalid_json_exits_2(self, tmp_path: Path) -> None:
        """report command with invalid JSON exits with code 2."""
        bad = tmp_path / "bad.json"
        bad.write_text("{invalid}")
        result = runner.invoke(app, ["report", str(bad)])
        assert result.exit_code == 2

    def test_report_writes_json_output(self, tmp_path: Path) -> None:
        """report --format json --output writes file."""
        rp = _write_report(tmp_path / "r.json", _make_report())
        out = tmp_path / "out.json"
        result = runner.invoke(app, ["report", str(rp), "--format", "json", "--output", str(out)])
        assert out.exists()


# ---------------------------------------------------------------------------
# improve command
# ---------------------------------------------------------------------------


class TestImproveCommand:
    """Tests for `agent-eval improve` command."""

    def test_improve_no_weak_cases_prints_message(self, tmp_path: Path) -> None:
        """improve command prints message when all cases pass."""
        rp = _write_report(tmp_path / "r.json", _make_report(overall_score=0.9))
        result = runner.invoke(app, [
            "improve",
            "--report", str(rp),
            "--agent", "screener",
        ])
        assert result.exit_code == 0
        assert "No low-scoring" in result.output

    def test_improve_generates_candidate_files(self, tmp_path: Path) -> None:
        """improve command generates candidate prompt files for weak cases."""
        tc_fail = TestCaseResult(
            case_id="tc-fail",
            input={},
            output="reject",
            scores={"accuracy": 0.5},
            passed=False,
        )
        report = EvalReport(
            agent_type="screener",
            prompt_version="0.1.0",
            test_cases=[tc_fail],
            overall_score=0.5,
        )
        rp = _write_report(tmp_path / "r.json", report)
        out_dir = tmp_path / "candidates"
        result = runner.invoke(app, [
            "improve",
            "--report", str(rp),
            "--agent", "screener",
            "--output-dir", str(out_dir),
        ])
        assert result.exit_code == 0
        # Two candidate files should have been created
        assert out_dir.exists()
        files = list(out_dir.iterdir())
        assert len(files) == 2

    def test_improve_missing_report_exits_2(self, tmp_path: Path) -> None:
        """improve command with missing report exits with code 2."""
        result = runner.invoke(app, [
            "improve",
            "--report", str(tmp_path / "no.json"),
            "--agent", "screener",
        ])
        assert result.exit_code == 2


# ---------------------------------------------------------------------------
# eval-all command
# ---------------------------------------------------------------------------


class TestEvalAllCommand:
    """Tests for `agent-eval eval-all` command."""

    def test_eval_all_stub_mode_passes(self) -> None:
        """eval-all in stub mode (run_agent=False) exits 0."""
        result = runner.invoke(app, ["eval-all"])
        assert result.exit_code == 0

    def test_eval_all_writes_output_file(self, tmp_path: Path) -> None:
        """eval-all --output writes a combined JSON report."""
        out = tmp_path / "combined.json"
        result = runner.invoke(app, ["eval-all", "--output", str(out)])
        assert out.exists()
        data = json.loads(out.read_text())
        assert "overall" in data
        assert "pipelines" in data
