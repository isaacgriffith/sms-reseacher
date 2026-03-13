"""Metamorphic tests for ScreenerAgent.

Metamorphic Relations
---------------------
MR-S1: Decision Stability Under Abstract Paraphrase
    Paraphrasing an abstract without changing its meaning must not change
    the inclusion/exclusion decision.  Under a deterministic stub this
    verifies the structural MR wiring; live semantic equivalence is validated
    in integration evals.

MR-S2: Consistent Rejection When Criteria Unmet
    When an abstract clearly does not meet any inclusion criterion, the
    decision must always be ``rejected`` regardless of how the abstract
    is phrased.  Under a deterministic stub every call returns the same
    rejected decision, confirming the MR is correctly wired.

Tests use a stubbed ``LLMClient`` for deterministic, offline verification.

See conftest.py for hypothesis profile configuration.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.screener import ScreenerAgent, ScreeningResult

# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

_STUB_ACCEPTED = json.dumps({
    "decision": "accepted",
    "reasons": [
        {"criterion_type": "inclusion", "text": "empirical study on TDD"}
    ],
})

_STUB_REJECTED = json.dumps({
    "decision": "rejected",
    "reasons": [
        {"criterion_type": "exclusion", "text": "not peer-reviewed"}
    ],
})

_INCLUSION = [{"id": 1, "description": "Empirical studies on automated testing"}]
_EXCLUSION = [{"id": 1, "description": "Opinion pieces or grey literature"}]

_ABSTRACT_INCLUDE = (
    "We present a controlled experiment evaluating TDD in software projects. "
    "Defect density was reduced by 40% using test-first methods."
)

_ABSTRACT_INCLUDE_PARAPHRASE = (
    "A controlled study assessed test-driven development in software contexts. "
    "The defect rate dropped 40% when tests were written before implementation."
)

_ABSTRACT_REJECT = (
    "This blog post argues that unit tests slow down development "
    "and developers should rely on manual testing instead."
)

_ABSTRACT_REJECT_PARAPHRASE = (
    "An opinion column claims automated testing impedes developer productivity "
    "and manual verification is preferable."
)


def make_stub_agent(decision: str = "accepted") -> ScreenerAgent:
    """Return a ScreenerAgent backed by a deterministic stub LLMClient.

    Args:
        decision: The decision string the stub will always return.

    Returns:
        :class:`ScreenerAgent` with mocked LLM client.
    """
    stub_response = json.dumps({
        "decision": decision,
        "reasons": [{"criterion_type": "inclusion", "text": f"Stub: {decision}"}],
    })
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=stub_response)
    return ScreenerAgent(llm_client=stub_client)


def _decision(result: str | ScreeningResult) -> str:
    """Extract the decision string from a screener result.

    Args:
        result: Raw string or :class:`ScreeningResult` from the agent.

    Returns:
        Decision string: ``'accepted'``, ``'rejected'``, or ``'duplicate'``.
    """
    if isinstance(result, ScreeningResult):
        return result.decision
    try:
        return json.loads(result).get("decision", "")
    except (json.JSONDecodeError, AttributeError):
        lower = str(result).lower()
        if "accept" in lower:
            return "accepted"
        if "duplicate" in lower:
            return "duplicate"
        return "rejected"


# ---------------------------------------------------------------------------
# MR-S1: Decision Stability Under Abstract Paraphrase
# ---------------------------------------------------------------------------


class TestScreenerMRS1DecisionStabilityUnderParaphrase:
    """MR-S1: paraphrasing the abstract must not change the inclusion decision."""

    async def test_include_paraphrase_same_decision(self) -> None:
        """Original and paraphrased include-abstract produce the same decision.

        Both calls use the same stub, confirming structural MR wiring.
        """
        agent = make_stub_agent("accepted")

        result_orig = await agent.run(
            inclusion_criteria=_INCLUSION,
            exclusion_criteria=_EXCLUSION,
            abstract=_ABSTRACT_INCLUDE,
        )
        result_para = await agent.run(
            inclusion_criteria=_INCLUSION,
            exclusion_criteria=_EXCLUSION,
            abstract=_ABSTRACT_INCLUDE_PARAPHRASE,
        )

        assert _decision(result_orig) == _decision(result_para), (
            "MR-S1: paraphrase of includable abstract must not change decision. "
            f"Original: {_decision(result_orig)!r}, Paraphrase: {_decision(result_para)!r}"
        )

    async def test_reject_paraphrase_same_decision(self) -> None:
        """Original and paraphrased reject-abstract produce the same decision."""
        agent = make_stub_agent("rejected")

        result_orig = await agent.run(
            inclusion_criteria=_INCLUSION,
            exclusion_criteria=_EXCLUSION,
            abstract=_ABSTRACT_REJECT,
        )
        result_para = await agent.run(
            inclusion_criteria=_INCLUSION,
            exclusion_criteria=_EXCLUSION,
            abstract=_ABSTRACT_REJECT_PARAPHRASE,
        )

        assert _decision(result_orig) == _decision(result_para), (
            "MR-S1: paraphrase of rejected abstract must not change decision"
        )

    async def test_decision_always_valid_enum(self) -> None:
        """Every decision must be one of: accepted, rejected, duplicate."""
        for decision_val in ("accepted", "rejected", "duplicate"):
            agent = make_stub_agent(decision_val)
            result = await agent.run(
                inclusion_criteria=_INCLUSION,
                exclusion_criteria=_EXCLUSION,
                abstract=_ABSTRACT_INCLUDE,
            )
            assert _decision(result) in {"accepted", "rejected", "duplicate"}, (
                f"MR-S1: decision {_decision(result)!r} is not a valid enum value"
            )

    @given(
        abstract_a=st.sampled_from([_ABSTRACT_INCLUDE, _ABSTRACT_INCLUDE_PARAPHRASE]),
        abstract_b=st.sampled_from([_ABSTRACT_INCLUDE, _ABSTRACT_INCLUDE_PARAPHRASE]),
    )
    async def test_any_paraphrase_pair_same_decision(
        self, abstract_a: str, abstract_b: str
    ) -> None:
        """Hypothesis: any include-abstract paraphrase pair produces same decision."""
        agent = make_stub_agent("accepted")

        result_a = await agent.run(
            inclusion_criteria=_INCLUSION,
            exclusion_criteria=_EXCLUSION,
            abstract=abstract_a,
        )
        result_b = await agent.run(
            inclusion_criteria=_INCLUSION,
            exclusion_criteria=_EXCLUSION,
            abstract=abstract_b,
        )

        assert _decision(result_a) == _decision(result_b), (
            "MR-S1: paraphrase pair produced different decisions"
        )


# ---------------------------------------------------------------------------
# MR-S2: Consistent Rejection When Criteria Unmet
# ---------------------------------------------------------------------------


class TestScreenerMRS2ConsistentRejectionWhenCriteriaUnmet:
    """MR-S2: abstracts that clearly fail all inclusion criteria must be rejected."""

    async def test_opinion_piece_always_rejected(self) -> None:
        """An opinion blog post must always be rejected under consistent stub."""
        agent = make_stub_agent("rejected")

        result = await agent.run(
            inclusion_criteria=_INCLUSION,
            exclusion_criteria=_EXCLUSION,
            abstract=_ABSTRACT_REJECT,
        )

        assert _decision(result) == "rejected", (
            "MR-S2: opinion piece must be rejected when inclusion criteria require empirical work. "
            f"Got: {_decision(result)!r}"
        )

    async def test_paraphrase_of_rejection_also_rejected(self) -> None:
        """Paraphrased rejection abstract must also be rejected."""
        agent = make_stub_agent("rejected")

        result = await agent.run(
            inclusion_criteria=_INCLUSION,
            exclusion_criteria=_EXCLUSION,
            abstract=_ABSTRACT_REJECT_PARAPHRASE,
        )

        assert _decision(result) == "rejected", (
            "MR-S2: paraphrase of rejected abstract must remain rejected"
        )

    async def test_rejection_consistent_across_multiple_calls(self) -> None:
        """Calling the agent twice on the same reject-abstract produces the same result."""
        agent = make_stub_agent("rejected")

        result_1 = await agent.run(
            inclusion_criteria=_INCLUSION,
            exclusion_criteria=_EXCLUSION,
            abstract=_ABSTRACT_REJECT,
        )
        result_2 = await agent.run(
            inclusion_criteria=_INCLUSION,
            exclusion_criteria=_EXCLUSION,
            abstract=_ABSTRACT_REJECT,
        )

        assert _decision(result_1) == _decision(result_2), (
            "MR-S2: identical reject-abstract must produce identical decisions across calls"
        )

    @given(
        reject_abstract=st.sampled_from([_ABSTRACT_REJECT, _ABSTRACT_REJECT_PARAPHRASE])
    )
    async def test_any_reject_abstract_always_rejected(
        self, reject_abstract: str
    ) -> None:
        """Hypothesis: any reject-class abstract must produce 'rejected' under stub."""
        agent = make_stub_agent("rejected")

        result = await agent.run(
            inclusion_criteria=_INCLUSION,
            exclusion_criteria=_EXCLUSION,
            abstract=reject_abstract,
        )

        assert _decision(result) == "rejected", (
            f"MR-S2: expected 'rejected' for reject-class abstract, got {_decision(result)!r}"
        )
