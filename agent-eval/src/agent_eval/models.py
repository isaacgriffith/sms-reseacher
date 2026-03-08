"""Pydantic models for agent evaluation results."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TestCaseResult(BaseModel):
    """Result for a single evaluation test case."""

    case_id: str
    input: dict[str, Any]
    output: str
    scores: dict[str, float]
    passed: bool


class EvalReport(BaseModel):
    """Full evaluation report for an agent run."""

    run_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    agent_type: str
    prompt_version: str
    test_cases: list[TestCaseResult]
    overall_score: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def model_dump_json(self, **kwargs: Any) -> str:
        """Serialize to JSON string."""
        return super().model_dump_json(**kwargs)
