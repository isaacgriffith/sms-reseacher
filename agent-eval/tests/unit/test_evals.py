"""Unit tests for agent_eval.evals.* evaluation pipelines.

All tests run in stub mode (run_agent=False) to avoid requiring live LLM
credentials.  Tests verify that:
- build_test_cases returns correctly shaped LLMTestCase objects
- run_*_eval returns a valid {passed, failed, total, errors} dict
- pass/fail counts are correct for the stub outputs
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# screener_eval
# ---------------------------------------------------------------------------


class TestScreenerEval:
    """Tests for agent_eval.evals.screener_eval."""

    def test_build_test_cases_returns_list(self) -> None:
        """build_test_cases returns a non-empty list."""
        from agent_eval.evals.screener_eval import build_test_cases

        cases = build_test_cases(run_agent=False)
        assert isinstance(cases, list)
        assert len(cases) > 0

    def test_build_test_cases_have_input_and_output(self) -> None:
        """Each LLMTestCase has non-empty input and actual_output."""
        from agent_eval.evals.screener_eval import build_test_cases

        for case in build_test_cases(run_agent=False):
            assert case.input
            assert case.actual_output

    def test_run_screener_eval_stub_all_pass(self) -> None:
        """Stub mode should produce all passed cases."""
        from agent_eval.evals.screener_eval import run_screener_eval

        result = run_screener_eval(run_agent=False)
        assert result["failed"] == 0
        assert result["passed"] == result["total"]
        assert result["total"] > 0

    def test_run_screener_eval_returns_correct_keys(self) -> None:
        """run_screener_eval returns a dict with expected keys."""
        from agent_eval.evals.screener_eval import run_screener_eval

        result = run_screener_eval(run_agent=False)
        assert set(result.keys()) >= {"passed", "failed", "total", "errors"}

    def test_assert_valid_decision_accepts_valid(self) -> None:
        """_assert_valid_decision accepts accepted/rejected/duplicate."""
        import json

        from agent_eval.evals.screener_eval import _assert_valid_decision

        for decision in ("accepted", "rejected", "duplicate"):
            _assert_valid_decision(json.dumps({"decision": decision}))

    def test_assert_valid_decision_raises_on_invalid(self) -> None:
        """_assert_valid_decision raises on unknown decision."""
        import json

        from agent_eval.evals.screener_eval import _assert_valid_decision

        with pytest.raises(AssertionError):
            _assert_valid_decision(json.dumps({"decision": "maybe"}))

    def test_assert_rationale_present_passes(self) -> None:
        """_assert_rationale_present accepts a non-trivial rationale."""
        import json

        from agent_eval.evals.screener_eval import _assert_rationale_present

        _assert_rationale_present(
            json.dumps(
                {
                    "decision": "accepted",
                    "rationale": "This is a valid empirical study.",
                }
            )
        )

    def test_assert_rationale_present_raises_on_empty(self) -> None:
        """_assert_rationale_present raises when rationale is missing."""
        import json

        from agent_eval.evals.screener_eval import _assert_rationale_present

        with pytest.raises(AssertionError):
            _assert_rationale_present(json.dumps({"decision": "accepted", "rationale": ""}))


# ---------------------------------------------------------------------------
# extractor_eval
# ---------------------------------------------------------------------------


class TestExtractorEval:
    """Tests for agent_eval.evals.extractor_eval."""

    def test_build_test_cases_returns_nonempty_list(self) -> None:
        """build_test_cases returns a non-empty list."""
        from agent_eval.evals.extractor_eval import build_test_cases

        cases = build_test_cases(run_agent=False)
        assert len(cases) > 0

    def test_run_extractor_eval_stub_all_pass(self) -> None:
        """Stub mode all cases should pass."""
        from agent_eval.evals.extractor_eval import run_extractor_eval

        result = run_extractor_eval(run_agent=False)
        assert result["failed"] == 0
        assert result["passed"] == result["total"]

    def test_assert_non_empty_fields_passes(self) -> None:
        """_assert_non_empty_fields passes when all fields have values."""
        import json

        from agent_eval.evals.extractor_eval import _assert_non_empty_fields

        _assert_non_empty_fields(
            json.dumps({"study_design": "RCT", "sample_size": "42"}),
            ["study_design", "sample_size"],
        )

    def test_assert_non_empty_fields_raises_on_missing(self) -> None:
        """_assert_non_empty_fields raises when a field is missing."""
        import json

        from agent_eval.evals.extractor_eval import _assert_non_empty_fields

        with pytest.raises(AssertionError):
            _assert_non_empty_fields(json.dumps({"study_design": "RCT"}), ["sample_size"])

    def test_assert_no_none_values_raises_on_null(self) -> None:
        """_assert_no_none_values_for_required_fields raises when field is null."""
        import json

        from agent_eval.evals.extractor_eval import _assert_no_none_values_for_required_fields

        with pytest.raises(AssertionError):
            _assert_no_none_values_for_required_fields(
                json.dumps({"study_design": None}),
                ["study_design"],
            )


# ---------------------------------------------------------------------------
# synthesiser_eval
# ---------------------------------------------------------------------------


class TestSynthesiserEval:
    """Tests for agent_eval.evals.synthesiser_eval."""

    def test_run_synthesiser_eval_stub_passes(self) -> None:
        """Stub mode for synthesiser_eval exits without failure."""
        from agent_eval.evals.synthesiser_eval import run_synthesiser_eval

        result = run_synthesiser_eval(run_agent=False)
        assert "passed" in result
        assert "failed" in result

    def test_build_test_cases_nonempty(self) -> None:
        """build_test_cases for synthesiser returns at least one case."""
        from agent_eval.evals.synthesiser_eval import build_test_cases

        cases = build_test_cases(run_agent=False)
        assert len(cases) > 0


# ---------------------------------------------------------------------------
# librarian_eval
# ---------------------------------------------------------------------------


class TestLibrarianEval:
    """Tests for agent_eval.evals.librarian_eval."""

    def test_run_librarian_eval_returns_dict(self) -> None:
        """run_librarian_eval returns a dict with expected keys."""
        from agent_eval.evals.librarian_eval import run_librarian_eval

        result = run_librarian_eval(run_agent=False)
        assert set(result.keys()) >= {"passed", "failed", "total", "errors"}

    def test_run_librarian_eval_stub_passes(self) -> None:
        """Stub mode should not fail."""
        from agent_eval.evals.librarian_eval import run_librarian_eval

        result = run_librarian_eval(run_agent=False)
        assert result["failed"] == 0


# ---------------------------------------------------------------------------
# expert_eval
# ---------------------------------------------------------------------------


class TestExpertEval:
    """Tests for agent_eval.evals.expert_eval."""

    def test_run_expert_eval_returns_dict(self) -> None:
        """run_expert_eval returns a dict with expected keys."""
        from agent_eval.evals.expert_eval import run_expert_eval

        result = run_expert_eval(run_agent=False)
        assert set(result.keys()) >= {"passed", "failed", "total", "errors"}

    def test_run_expert_eval_stub_passes(self) -> None:
        """Stub mode should not fail."""
        from agent_eval.evals.expert_eval import run_expert_eval

        result = run_expert_eval(run_agent=False)
        assert result["failed"] == 0


# ---------------------------------------------------------------------------
# search_builder_eval
# ---------------------------------------------------------------------------


class TestSearchBuilderEval:
    """Tests for agent_eval.evals.search_builder_eval."""

    def test_run_search_builder_eval_returns_dict(self) -> None:
        """run_search_builder_eval returns a dict with expected keys."""
        from agent_eval.evals.search_builder_eval import run_search_builder_eval

        result = run_search_builder_eval(run_agent=False)
        assert "passed" in result

    def test_run_search_builder_eval_stub_passes(self) -> None:
        """Stub mode should not fail."""
        from agent_eval.evals.search_builder_eval import run_search_builder_eval

        result = run_search_builder_eval(run_agent=False)
        assert result["failed"] == 0


# ---------------------------------------------------------------------------
# domain_modeler_eval
# ---------------------------------------------------------------------------


class TestDomainModelerEval:
    """Tests for agent_eval.evals.domain_modeler_eval."""

    def test_run_domain_modeler_eval_returns_dict(self) -> None:
        """run_domain_modeler_eval returns the expected result shape."""
        from agent_eval.evals.domain_modeler_eval import run_domain_modeler_eval

        result = run_domain_modeler_eval(run_agent=False)
        assert "passed" in result

    def test_run_domain_modeler_eval_stub_passes(self) -> None:
        """Stub mode should not fail."""
        from agent_eval.evals.domain_modeler_eval import run_domain_modeler_eval

        result = run_domain_modeler_eval(run_agent=False)
        assert result["failed"] == 0


# ---------------------------------------------------------------------------
# quality_judge_eval
# ---------------------------------------------------------------------------


class TestQualityJudgeEval:
    """Tests for agent_eval.evals.quality_judge_eval."""

    def test_run_quality_judge_eval_returns_dict(self) -> None:
        """run_quality_judge_eval returns expected keys."""
        from agent_eval.evals.quality_judge_eval import run_quality_judge_eval

        result = run_quality_judge_eval(run_agent=False)
        assert "passed" in result

    def test_run_quality_judge_eval_stub_passes(self) -> None:
        """Stub mode should not fail."""
        from agent_eval.evals.quality_judge_eval import run_quality_judge_eval

        result = run_quality_judge_eval(run_agent=False)
        assert result["failed"] == 0


# ---------------------------------------------------------------------------
# validity_eval
# ---------------------------------------------------------------------------


class TestValidityEval:
    """Tests for agent_eval.evals.validity_eval."""

    def test_run_validity_eval_returns_dict(self) -> None:
        """run_validity_eval returns expected keys."""
        from agent_eval.evals.validity_eval import run_validity_eval

        result = run_validity_eval(run_agent=False)
        assert "passed" in result

    def test_run_validity_eval_stub_passes(self) -> None:
        """Stub mode should not fail."""
        from agent_eval.evals.validity_eval import run_validity_eval

        result = run_validity_eval(run_agent=False)
        assert result["failed"] == 0


# ---------------------------------------------------------------------------
# protocol_reviewer_eval
# ---------------------------------------------------------------------------


class TestProtocolReviewerEval:
    """Tests for agent_eval.evals.protocol_reviewer_eval."""

    def test_build_test_cases_returns_nonempty_list(self) -> None:
        """build_test_cases returns a non-empty list of LLMTestCase."""
        from agent_eval.evals.protocol_reviewer_eval import build_test_cases

        cases = build_test_cases(run_agent=False)
        assert isinstance(cases, list)
        assert len(cases) > 0

    def test_build_test_cases_have_input_and_output(self) -> None:
        """Each test case has non-empty input and actual_output."""
        from agent_eval.evals.protocol_reviewer_eval import build_test_cases

        for case in build_test_cases(run_agent=False):
            assert case.input
            assert case.actual_output

    def test_run_protocol_reviewer_eval_returns_correct_keys(self) -> None:
        """run_protocol_reviewer_eval returns a dict with expected keys."""
        from agent_eval.evals.protocol_reviewer_eval import run_protocol_reviewer_eval

        result = run_protocol_reviewer_eval(run_agent=False)
        assert set(result.keys()) >= {
            "passed",
            "failed",
            "total",
            "errors",
            "pass_rate",
            "threshold",
            "threshold_met",
        }

    def test_run_protocol_reviewer_eval_stub_all_pass(self) -> None:
        """Stub mode should produce all passed cases."""
        from agent_eval.evals.protocol_reviewer_eval import run_protocol_reviewer_eval

        result = run_protocol_reviewer_eval(run_agent=False)
        assert result["failed"] == 0
        assert result["passed"] == result["total"]
        assert result["total"] > 0
        assert result["threshold_met"] is True

    def test_assert_valid_structure_accepts_valid(self) -> None:
        """_assert_valid_structure accepts valid JSON."""
        import json

        from agent_eval.evals.protocol_reviewer_eval import _assert_valid_structure

        valid = json.dumps(
            {
                "issues": [
                    {
                        "section": "search_strategy",
                        "severity": "critical",
                        "description": "Missing.",
                        "suggestion": "Add it.",
                    }
                ],
                "overall_assessment": "Needs work.",
            }
        )
        _assert_valid_structure(valid)

    def test_assert_valid_structure_raises_on_missing_issues(self) -> None:
        """_assert_valid_structure raises when 'issues' is missing."""
        import json

        from agent_eval.evals.protocol_reviewer_eval import _assert_valid_structure

        with pytest.raises(AssertionError, match="Missing 'issues'"):
            _assert_valid_structure(json.dumps({"overall_assessment": "ok"}))

    def test_assert_valid_structure_raises_on_missing_assessment(self) -> None:
        """_assert_valid_structure raises when 'overall_assessment' is missing."""
        import json

        from agent_eval.evals.protocol_reviewer_eval import _assert_valid_structure

        with pytest.raises(AssertionError, match="Missing 'overall_assessment'"):
            _assert_valid_structure(json.dumps({"issues": []}))

    def test_assert_valid_structure_raises_on_bad_severity(self) -> None:
        """_assert_valid_structure raises when severity is invalid."""
        import json

        from agent_eval.evals.protocol_reviewer_eval import _assert_valid_structure

        bad = json.dumps(
            {
                "issues": [
                    {
                        "section": "x",
                        "severity": "low",
                        "description": "d",
                        "suggestion": "s",
                    }
                ],
                "overall_assessment": "ok",
            }
        )
        with pytest.raises(AssertionError, match="severity must be"):
            _assert_valid_structure(bad)

    def test_assert_valid_structure_raises_on_empty_assessment(self) -> None:
        """_assert_valid_structure raises when overall_assessment is empty string."""
        import json

        from agent_eval.evals.protocol_reviewer_eval import _assert_valid_structure

        with pytest.raises(AssertionError, match="non-empty"):
            _assert_valid_structure(json.dumps({"issues": [], "overall_assessment": ""}))

    def test_assert_faithfulness_passes_no_known_issues(self) -> None:
        """_assert_faithfulness passes when no known issues."""
        import json

        from agent_eval.evals.protocol_reviewer_eval import _assert_faithfulness

        _assert_faithfulness(
            json.dumps({"issues": [], "overall_assessment": "ok"}),
            {"known_issues": []},
        )

    def test_assert_faithfulness_passes_when_known_flagged(self) -> None:
        """_assert_faithfulness passes when known sections are flagged."""
        import json

        from agent_eval.evals.protocol_reviewer_eval import _assert_faithfulness

        output = json.dumps(
            {
                "issues": [
                    {
                        "section": "search_strategy",
                        "severity": "critical",
                        "description": "d",
                        "suggestion": "s",
                    }
                ],
                "overall_assessment": "ok",
            }
        )
        _assert_faithfulness(output, {"known_issues": ["search_strategy"]})

    def test_assert_faithfulness_raises_when_known_not_flagged(self) -> None:
        """_assert_faithfulness raises when known section missing from output."""
        import json

        from agent_eval.evals.protocol_reviewer_eval import _assert_faithfulness

        output = json.dumps({"issues": [], "overall_assessment": "ok"})
        with pytest.raises(AssertionError, match="Expected issue in section"):
            _assert_faithfulness(output, {"known_issues": ["search_strategy"]})

    def test_protocol_test_inputs_length(self) -> None:
        """PROTOCOL_TEST_INPUTS has the expected 6 entries."""
        from agent_eval.evals.protocol_reviewer_eval import PROTOCOL_TEST_INPUTS

        assert len(PROTOCOL_TEST_INPUTS) == 6

    def test_run_protocol_reviewer_eval_custom_threshold(self) -> None:
        """Custom threshold is reflected in the result."""
        from agent_eval.evals.protocol_reviewer_eval import run_protocol_reviewer_eval

        result = run_protocol_reviewer_eval(run_agent=False, threshold=1.0)
        assert result["threshold"] == 1.0
        assert result["threshold_met"] is True


# ---------------------------------------------------------------------------
# eval_all._run_pipeline
# ---------------------------------------------------------------------------


class TestRunPipeline:
    """Tests for agent_eval.commands.eval_all._run_pipeline."""

    def test_run_pipeline_known_agent(self) -> None:
        """_run_pipeline runs screener_eval in stub mode and returns a dict."""
        from agent_eval.commands.eval_all import _run_pipeline

        result = _run_pipeline("screener", "agent_eval.evals.screener_eval", run_agent=False)
        assert "passed" in result

    def test_run_pipeline_unknown_module_returns_error_dict(self) -> None:
        """_run_pipeline returns a failure dict when module doesn't exist."""
        from agent_eval.commands.eval_all import _run_pipeline

        result = _run_pipeline("screener", "agent_eval.evals.no_such_module", run_agent=False)
        assert result["failed"] == 1
        assert len(result["errors"]) > 0
