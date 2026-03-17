"""Quality Judge agent: evaluates a study against five quality rubrics."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, field_validator

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader
from agents.core.provider_config import ProviderConfig

_RUBRIC_NAMES = frozenset(
    {
        "need_for_review",
        "search_strategy",
        "search_evaluation",
        "extraction_classification",
        "study_validity",
    }
)

_RUBRIC_MAX = {
    "need_for_review": 2,
    "search_strategy": 2,
    "search_evaluation": 3,
    "extraction_classification": 3,
    "study_validity": 1,
}


class RubricDetail(BaseModel):
    """Score and justification for one quality rubric."""

    score: int
    justification: str


class Recommendation(BaseModel):
    """Prioritised improvement recommendation targeting a rubric."""

    priority: int
    action: str
    target_rubric: str


class QualityJudgeResult(BaseModel):
    """Structured output from the QualityJudgeAgent.

    Scores are validated against per-rubric maximums.  Any score exceeding
    the rubric maximum is clamped to the maximum.
    """

    scores: dict[str, int]
    rubric_details: dict[str, RubricDetail]
    recommendations: list[Recommendation]

    @field_validator("scores")
    @classmethod
    def clamp_scores(cls, v: dict[str, int]) -> dict[str, int]:
        """Clamp each rubric score to its valid 0–max range.

        Args:
            v: Raw scores dict from the LLM response.

        Returns:
            Scores dict with each value clamped to [0, max].
        """
        return {
            rubric: max(0, min(score, _RUBRIC_MAX.get(rubric, score)))
            for rubric, score in v.items()
        }


def _extract_json(raw: str) -> dict[str, Any]:
    """Strip markdown fences and parse JSON from the LLM response.

    Args:
        raw: The raw string returned by the LLM.

    Returns:
        The parsed JSON object.

    Raises:
        ValueError: If no valid JSON object can be found in the response.
    """
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"No valid JSON found in quality judge response: {raw[:200]!r}")


def _build_snapshot(
    *,
    study_id: int,
    study_name: str | None,
    study_type: str | None,
    current_phase: int,
    pico_saved: bool,
    search_strategies: list[dict[str, Any]],
    test_retest_done: bool,
    reviewers: list[dict[str, Any]],
    inclusion_criteria: list[str],
    exclusion_criteria: list[str],
    extractions_done: bool,
    validity_filled: bool,
    validity_dimensions: dict[str, str],
) -> dict[str, Any]:
    """Assemble the Jinja2 template context from keyword arguments.

    Args:
        study_id: Study primary key.
        study_name: Human-readable study name.
        study_type: Study type enum value string.
        current_phase: Current SMS workflow phase (1–5).
        pico_saved: Whether PICO components have been saved.
        search_strategies: List of search string dicts with query_string/result_count.
        test_retest_done: Whether a test-retest search validation was performed.
        reviewers: List of reviewer config dicts (reviewer_type, agent_name, user_id).
        inclusion_criteria: List of inclusion criterion description strings.
        exclusion_criteria: List of exclusion criterion description strings.
        extractions_done: Whether data extractions exist for accepted papers.
        validity_filled: Whether the validity discussion section is populated.
        validity_dimensions: Dict mapping dimension name → filled text.

    Returns:
        Context dict for the Jinja2 prompt template.
    """
    return {
        "study_id": study_id,
        "study_name": study_name,
        "study_type": study_type,
        "current_phase": current_phase,
        "pico_saved": pico_saved,
        "search_strategies": search_strategies,
        "test_retest_done": test_retest_done,
        "reviewers": reviewers,
        "inclusion_criteria": inclusion_criteria,
        "exclusion_criteria": exclusion_criteria,
        "extractions_done": extractions_done,
        "validity_filled": validity_filled,
        "validity_dimensions": validity_dimensions,
    }


class QualityJudgeAgent:
    """Agent that evaluates a study against five SMS quality rubrics.

    Produces a :class:`QualityJudgeResult` with per-rubric scores (0–11 total),
    justification text, and prioritised improvement recommendations.

    When ``provider_config`` is supplied, all LLM calls are routed through
    the database-backed model configuration rather than environment variables.

    Args:
        llm_client: Optional :class:`LLMClient` override for testing.
        provider_config: Optional :class:`ProviderConfig` for database-backed
            model routing.  When ``None``, falls back to environment settings.
    """

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        provider_config: ProviderConfig | None = None,
        system_message_override: str | None = None,
    ) -> None:
        """Initialise the quality judge agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
            provider_config: Optional database-resolved provider configuration.
                Passed through to each :meth:`LLMClient.complete` call.
            system_message_override: Optional rendered system message to use
                instead of the default prompt-file system message.
        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("quality_judge")
        self._provider_config = provider_config
        self._system_message_override = system_message_override

    async def run(
        self,
        *,
        study_id: int,
        study_name: str | None = None,
        study_type: str | None = None,
        current_phase: int = 1,
        pico_saved: bool = False,
        search_strategies: list[dict[str, Any]] | None = None,
        test_retest_done: bool = False,
        reviewers: list[dict[str, Any]] | None = None,
        inclusion_criteria: list[str] | None = None,
        exclusion_criteria: list[str] | None = None,
        extractions_done: bool = False,
        validity_filled: bool = False,
        validity_dimensions: dict[str, str] | None = None,
    ) -> QualityJudgeResult:
        """Evaluate a study against all five quality rubrics.

        Args:
            study_id: Study primary key.
            study_name: Human-readable study name.
            study_type: Study type enum value string.
            current_phase: Current SMS workflow phase (1–5).
            pico_saved: Whether PICO components have been saved.
            search_strategies: List of search string dicts with
                ``query_string`` and ``result_count`` keys.
            test_retest_done: Whether a test-retest search validation was
                performed.
            reviewers: List of reviewer config dicts.
            inclusion_criteria: List of inclusion criterion descriptions.
            exclusion_criteria: List of exclusion criterion descriptions.
            extractions_done: Whether data extractions exist.
            validity_filled: Whether the validity section is populated.
            validity_dimensions: Dict mapping dimension name → filled text.

        Returns:
            A :class:`QualityJudgeResult` with scores, details, and
            recommendations.

        Raises:
            ValueError: If the LLM response cannot be parsed as valid JSON.
        """
        context = _build_snapshot(
            study_id=study_id,
            study_name=study_name,
            study_type=study_type,
            current_phase=current_phase,
            pico_saved=pico_saved,
            search_strategies=search_strategies or [],
            test_retest_done=test_retest_done,
            reviewers=reviewers or [],
            inclusion_criteria=inclusion_criteria or [],
            exclusion_criteria=exclusion_criteria or [],
            extractions_done=extractions_done,
            validity_filled=validity_filled,
            validity_dimensions=validity_dimensions or {},
        )
        messages = self._loader.load_messages(context)

        # Apply system message override if provided (Feature 005 / T063)
        if self._system_message_override is not None:
            messages = list(messages)
            for i, msg in enumerate(messages):
                if msg.get("role") == "system":
                    messages[i] = {"role": "system", "content": self._system_message_override}
                    break

        raw = await self._client.complete(
            messages, max_tokens=2048, provider_config=self._provider_config
        )
        data = _extract_json(raw)

        scores = data.get("scores", {})
        raw_details = data.get("rubric_details", {})
        rubric_details = {
            rubric: RubricDetail(
                score=detail.get("score", 0),
                justification=detail.get("justification", ""),
            )
            for rubric, detail in raw_details.items()
        }
        recommendations = [
            Recommendation(
                priority=rec.get("priority", i + 1),
                action=rec.get("action", ""),
                target_rubric=rec.get("target_rubric", ""),
            )
            for i, rec in enumerate(data.get("recommendations", []))
        ]

        return QualityJudgeResult(
            scores=scores,
            rubric_details=rubric_details,
            recommendations=recommendations,
        )
