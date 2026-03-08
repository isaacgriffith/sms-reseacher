"""Unit tests for EvalReport and TestCaseResult models."""

import json
import uuid
from datetime import datetime

from agent_eval.models import EvalReport, TestCaseResult


class TestTestCaseResult:
    """Tests for TestCaseResult model."""

    def test_instantiation(self) -> None:
        """TestCaseResult instantiates with required fields."""
        tc = TestCaseResult(
            case_id="tc-001",
            input={"abstract": "A test abstract"},
            output="include",
            scores={"accuracy": 0.9},
            passed=True,
        )
        assert tc.case_id == "tc-001"
        assert tc.passed is True

    def test_json_round_trip(self) -> None:
        """TestCaseResult survives JSON serialisation and deserialisation."""
        tc = TestCaseResult(
            case_id="tc-002",
            input={"key": "value"},
            output="exclude",
            scores={"accuracy": 0.5},
            passed=False,
        )
        serialised = tc.model_dump_json()
        restored = TestCaseResult.model_validate_json(serialised)
        assert restored.case_id == tc.case_id
        assert restored.passed == tc.passed


class TestEvalReport:
    """Tests for EvalReport model."""

    def test_instantiation_defaults(self) -> None:
        """EvalReport auto-generates run_id and timestamp."""
        report = EvalReport(
            agent_type="screener",
            prompt_version="0.1.0",
            test_cases=[],
            overall_score=0.0,
        )
        assert isinstance(report.run_id, uuid.UUID)
        assert isinstance(report.timestamp, datetime)

    def test_instantiation_with_cases(self) -> None:
        """EvalReport holds test cases correctly."""
        tc = TestCaseResult(
            case_id="tc-001",
            input={},
            output="include",
            scores={"accuracy": 1.0},
            passed=True,
        )
        report = EvalReport(
            agent_type="screener",
            prompt_version="1.0.0",
            test_cases=[tc],
            overall_score=1.0,
        )
        assert len(report.test_cases) == 1
        assert report.test_cases[0].case_id == "tc-001"

    def test_json_round_trip(self) -> None:
        """EvalReport survives JSON round-trip."""
        report = EvalReport(
            agent_type="extractor",
            prompt_version="0.2.0",
            test_cases=[],
            overall_score=0.85,
        )
        serialised = report.model_dump_json()
        data = json.loads(serialised)
        restored = EvalReport.model_validate(data)
        assert restored.run_id == report.run_id
        assert restored.overall_score == report.overall_score
        assert restored.agent_type == report.agent_type
