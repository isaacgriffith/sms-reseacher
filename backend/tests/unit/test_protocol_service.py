"""Unit tests for protocol_service graph validation helpers (feature 010).

Tests cover T019 (gate config parsing), T020 (task type allowlist), and T021
(graph structural validation helpers).

All tests are synchronous and require no database connection.
"""

from __future__ import annotations

import pytest
from db.models.protocols import ProtocolTaskType

from backend.services.protocol_service import (
    VALID_TASK_TYPES_BY_STUDY_TYPE,
    CompletionCheckConfig,
    HumanSignOffConfig,
    MetricThresholdConfig,
    ProtocolGraphError,
    detect_cycle,
    parse_gate_config,
    validate_graph,
    validate_required_input_coverage,
    validate_task_type,
)

# ---------------------------------------------------------------------------
# T019 — Gate config parsing tests
# ---------------------------------------------------------------------------


class TestParseGateConfig:
    """Tests for :func:`parse_gate_config` discriminated union parsing."""

    def test_metric_threshold_valid(self) -> None:
        """Parses a valid metric_threshold gate config into MetricThresholdConfig."""
        cfg = parse_gate_config(
            {
                "gate_type": "metric_threshold",
                "metric_name": "kappa",
                "operator": "gte",
                "threshold": 0.6,
            }
        )
        assert isinstance(cfg, MetricThresholdConfig)
        assert cfg.threshold == 0.6

    def test_completion_check_valid(self) -> None:
        """Parses a valid completion_check gate config into CompletionCheckConfig."""
        cfg = parse_gate_config(
            {"gate_type": "completion_check", "description": "All papers extracted."}
        )
        assert isinstance(cfg, CompletionCheckConfig)
        assert cfg.description == "All papers extracted."

    def test_human_sign_off_valid(self) -> None:
        """Parses a valid human_sign_off gate config into HumanSignOffConfig."""
        cfg = parse_gate_config(
            {
                "gate_type": "human_sign_off",
                "required_role": "study_admin",
                "prompt": "Please review.",
            }
        )
        assert isinstance(cfg, HumanSignOffConfig)
        assert cfg.required_role == "study_admin"

    def test_unknown_gate_type_raises(self) -> None:
        """Raises ValidationError when gate_type is not a recognised discriminator value."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            parse_gate_config({"gate_type": "nonexistent_type", "description": "x"})

    def test_metric_threshold_missing_field_raises(self) -> None:
        """Raises ValidationError when a required field is absent from the payload."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            # Missing 'threshold'
            parse_gate_config(
                {"gate_type": "metric_threshold", "metric_name": "k", "operator": "gte"}
            )

    def test_completion_check_empty_description_raises(self) -> None:
        """Raises ValidationError when the completion_check description is an empty string."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            parse_gate_config({"gate_type": "completion_check", "description": ""})


# ---------------------------------------------------------------------------
# T020 — Task type allowlist tests
# ---------------------------------------------------------------------------


class TestValidTaskTypesByStudyType:
    """Tests for :data:`VALID_TASK_TYPES_BY_STUDY_TYPE` and :func:`validate_task_type`."""

    def test_all_study_types_present(self) -> None:
        """The allowlist map contains exactly the four expected study type keys."""
        assert set(VALID_TASK_TYPES_BY_STUDY_TYPE.keys()) == {"SMS", "SLR", "Rapid", "Tertiary"}

    def test_sms_allows_define_pico(self) -> None:
        """DEFINE_PICO is a valid task type for SMS studies."""
        validate_task_type("SMS", ProtocolTaskType.DEFINE_PICO)  # no exception

    def test_sms_rejects_define_protocol(self) -> None:
        """DEFINE_PROTOCOL is not valid for SMS studies and raises ValueError."""
        with pytest.raises(ValueError, match="not valid for study type"):
            validate_task_type("SMS", ProtocolTaskType.DEFINE_PROTOCOL)

    def test_slr_allows_assess_quality(self) -> None:
        """ASSESS_QUALITY is a valid task type for SLR studies."""
        validate_task_type("SLR", ProtocolTaskType.ASSESS_QUALITY)

    def test_slr_rejects_define_pico(self) -> None:
        """DEFINE_PICO is not valid for SLR studies and raises ValueError."""
        with pytest.raises(ValueError):
            validate_task_type("SLR", ProtocolTaskType.DEFINE_PICO)

    def test_rapid_allows_produce_briefing(self) -> None:
        """PRODUCE_BRIEFING is a valid task type for Rapid studies."""
        validate_task_type("Rapid", ProtocolTaskType.PRODUCE_BRIEFING)

    def test_rapid_rejects_assess_quality(self) -> None:
        """ASSESS_QUALITY is not valid for Rapid studies and raises ValueError."""
        with pytest.raises(ValueError):
            validate_task_type("Rapid", ProtocolTaskType.ASSESS_QUALITY)

    def test_tertiary_allows_import_seed_studies(self) -> None:
        """IMPORT_SEED_STUDIES is a valid task type for Tertiary studies."""
        validate_task_type("Tertiary", ProtocolTaskType.IMPORT_SEED_STUDIES)

    def test_tertiary_rejects_produce_briefing(self) -> None:
        """PRODUCE_BRIEFING is not valid for Tertiary studies and raises ValueError."""
        with pytest.raises(ValueError):
            validate_task_type("Tertiary", ProtocolTaskType.PRODUCE_BRIEFING)

    def test_unknown_study_type_raises(self) -> None:
        """Raises ValueError with 'Unknown study_type' for an unrecognised study type string."""
        with pytest.raises(ValueError, match="Unknown study_type"):
            validate_task_type("Unknown", ProtocolTaskType.DEFINE_PICO)

    def test_all_types_covered_in_at_least_one_study_type(self) -> None:
        """Every ProtocolTaskType value appears in at least one study type allowlist."""
        all_allowed = set().union(*VALID_TASK_TYPES_BY_STUDY_TYPE.values())
        for task_type in ProtocolTaskType:
            assert task_type in all_allowed, f"{task_type.value} not in any allowlist"


# ---------------------------------------------------------------------------
# T021a — detect_cycle tests
# ---------------------------------------------------------------------------


class TestDetectCycle:
    """Tests for :func:`detect_cycle`."""

    def test_empty_graph_no_cycle(self) -> None:
        """An empty graph with no nodes or edges has no cycle."""
        assert detect_cycle([], []) is False

    def test_single_node_no_cycle(self) -> None:
        """A single isolated node has no cycle."""
        assert detect_cycle(["a"], []) is False

    def test_linear_chain_no_cycle(self) -> None:
        """A simple linear chain a→b→c is acyclic."""
        assert detect_cycle(["a", "b", "c"], [("a", "b"), ("b", "c")]) is False

    def test_simple_cycle(self) -> None:
        """A three-node ring a→b→c→a is detected as a cycle."""
        assert detect_cycle(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")]) is True

    def test_diamond_dag_no_cycle(self) -> None:
        """A diamond-shaped DAG (a→b, a→c, b→d, c→d) is acyclic."""
        # a → b, a → c, b → d, c → d
        nodes = ["a", "b", "c", "d"]
        edges = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
        assert detect_cycle(nodes, edges) is False

    def test_two_node_cycle(self) -> None:
        """A two-node mutual edge a→b, b→a is detected as a cycle."""
        assert detect_cycle(["a", "b"], [("a", "b"), ("b", "a")]) is True

    def test_isolated_node_plus_chain(self) -> None:
        """An isolated node alongside an acyclic chain produces no cycle."""
        # "z" is isolated; "a" → "b" → "c"
        assert detect_cycle(["a", "b", "c", "z"], [("a", "b"), ("b", "c")]) is False

    def test_disconnected_cycle(self) -> None:
        """A cycle in one connected component is detected even when another is acyclic."""
        # Two components: a→b (no cycle), x→y→x (cycle)
        nodes = ["a", "b", "x", "y"]
        edges = [("a", "b"), ("x", "y"), ("y", "x")]
        assert detect_cycle(nodes, edges) is True


# ---------------------------------------------------------------------------
# T021b — validate_graph tests
# ---------------------------------------------------------------------------


class TestValidateGraph:
    """Tests for :func:`validate_graph`."""

    def _sms_node(self, task_id: str, task_type: str = "DefinePICO") -> dict:
        """Return a minimal SMS node dict for use in graph validation tests."""
        return {"task_id": task_id, "task_type": task_type}

    def test_single_valid_node_passes(self) -> None:
        """A graph with one valid SMS node and no edges passes validation."""
        validate_graph("SMS", [self._sms_node("n1")], [])

    def test_empty_nodes_raises(self) -> None:
        """A graph with zero nodes raises ProtocolGraphError."""
        with pytest.raises(ProtocolGraphError, match="at least one node"):
            validate_graph("SMS", [], [])

    def test_duplicate_task_ids_raises(self) -> None:
        """Duplicate task_id values in the node list raise ProtocolGraphError."""
        with pytest.raises(ProtocolGraphError, match="duplicate task_id"):
            validate_graph("SMS", [self._sms_node("n1"), self._sms_node("n1")], [])

    def test_invalid_task_type_raises(self) -> None:
        """An unrecognised task_type string raises ProtocolGraphError."""
        with pytest.raises(ProtocolGraphError, match="Unknown task_type"):
            validate_graph("SMS", [{"task_id": "n1", "task_type": "NotARealType"}], [])

    def test_wrong_study_type_task_raises(self) -> None:
        """A task type that belongs to a different study type raises an error."""
        # DefineProtocol is SLR-only; should fail for SMS
        with pytest.raises((ProtocolGraphError, ValueError)):
            validate_graph("SMS", [{"task_id": "n1", "task_type": "DefineProtocol"}], [])

    def test_edge_unknown_source_raises(self) -> None:
        """An edge whose source task_id does not exist raises ProtocolGraphError."""
        with pytest.raises(ProtocolGraphError, match="unknown source"):
            validate_graph(
                "SMS",
                [self._sms_node("n1")],
                [{"source_task_id": "nonexistent", "target_task_id": "n1"}],
            )

    def test_edge_unknown_target_raises(self) -> None:
        """An edge whose target task_id does not exist raises ProtocolGraphError."""
        with pytest.raises(ProtocolGraphError, match="unknown target"):
            validate_graph(
                "SMS",
                [self._sms_node("n1")],
                [{"source_task_id": "n1", "target_task_id": "nonexistent"}],
            )

    def test_self_loop_raises(self) -> None:
        """An edge from a node to itself raises ProtocolGraphError."""
        with pytest.raises(ProtocolGraphError, match="Self-loop"):
            validate_graph(
                "SMS",
                [self._sms_node("n1")],
                [{"source_task_id": "n1", "target_task_id": "n1"}],
            )

    def test_cycle_raises(self) -> None:
        """A cyclic edge set raises ProtocolGraphError with 'cycle' in the message."""
        nodes = [
            self._sms_node("a"),
            {"task_id": "b", "task_type": "BuildSearchString"},
        ]
        edges = [
            {"source_task_id": "a", "target_task_id": "b"},
            {"source_task_id": "b", "target_task_id": "a"},
        ]
        with pytest.raises(ProtocolGraphError, match="cycle"):
            validate_graph("SMS", nodes, edges)

    def test_valid_two_node_dag_passes(self) -> None:
        """A two-node DAG with a single directed edge passes validation."""
        nodes = [
            self._sms_node("a"),
            {"task_id": "b", "task_type": "BuildSearchString"},
        ]
        edges = [{"source_task_id": "a", "target_task_id": "b"}]
        validate_graph("SMS", nodes, edges)  # should not raise


# ---------------------------------------------------------------------------
# T021c — validate_required_input_coverage tests
# ---------------------------------------------------------------------------


class TestValidateRequiredInputCoverage:
    """Tests for :func:`validate_required_input_coverage`."""

    def test_no_nodes_passes(self) -> None:
        """An empty node list with no edges passes input coverage validation."""
        validate_required_input_coverage([], [])

    def test_node_with_no_inputs_passes(self) -> None:
        """A node declaring no inputs passes input coverage validation."""
        validate_required_input_coverage([{"task_id": "n1", "inputs": []}], [])

    def test_required_input_covered_passes(self) -> None:
        """A required input that has a matching incoming edge passes validation."""
        nodes = [{"task_id": "n1", "inputs": [{"name": "papers", "is_required": True}]}]
        edges = [{"target_task_id": "n1", "target_input_name": "papers"}]
        validate_required_input_coverage(nodes, edges)

    def test_optional_input_uncovered_passes(self) -> None:
        """An optional input with no incoming edge does not raise an error."""
        nodes = [{"task_id": "n1", "inputs": [{"name": "papers", "is_required": False}]}]
        validate_required_input_coverage(nodes, [])

    def test_required_input_uncovered_raises(self) -> None:
        """A required input with no incoming edge raises ProtocolGraphError naming the input."""
        nodes = [{"task_id": "n1", "inputs": [{"name": "papers", "is_required": True}]}]
        with pytest.raises(ProtocolGraphError, match="n1.papers"):
            validate_required_input_coverage(nodes, [])

    def test_multiple_uncovered_inputs_listed(self) -> None:
        """All uncovered required inputs are listed together in the ProtocolGraphError."""
        nodes = [
            {"task_id": "n1", "inputs": [
                {"name": "x", "is_required": True},
                {"name": "y", "is_required": True},
            ]}
        ]
        with pytest.raises(ProtocolGraphError) as exc:
            validate_required_input_coverage(nodes, [])
        assert "n1.x" in str(exc.value)
        assert "n1.y" in str(exc.value)
