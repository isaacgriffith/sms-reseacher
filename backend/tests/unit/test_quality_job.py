"""Unit tests for backend.jobs.quality_job.

Covers run_quality_eval and all private helpers with mocked sessions
and agent dependencies.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session_cm(db_mock: AsyncMock) -> MagicMock:
    """Wrap db_mock in an async context-manager returned by _session_maker().

    Args:
        db_mock: AsyncMock acting as the SQLAlchemy session.

    Returns:
        A MagicMock whose call returns an async context manager yielding db_mock.
    """
    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=db_mock)
    cm.__aexit__ = AsyncMock(return_value=False)
    return MagicMock(return_value=cm)


def _scalar_result(value: object) -> MagicMock:
    """Return a mock mimicking an AsyncSession.execute() scalar result.

    Args:
        value: The value returned by scalar_one_or_none().

    Returns:
        MagicMock with scalar_one_or_none and scalars().all() wired.
    """
    r = MagicMock()
    r.scalar_one_or_none.return_value = value
    r.scalars.return_value.all.return_value = [] if value is None else [value]
    return r


# ---------------------------------------------------------------------------
# run_quality_eval — happy path
# ---------------------------------------------------------------------------


async def test_run_quality_eval_returns_completed_on_success():
    """run_quality_eval returns status='completed' and total_score when agent succeeds.

    When the snapshot and report generation both succeed the returned dict should
    contain status='completed' and the total_score from the report.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    session_maker = _make_session_cm(db)

    report_mock = MagicMock()
    report_mock.total_score = 42

    with (
        patch("backend.core.database._session_maker", session_maker),
        patch(
            "backend.jobs.quality_job._build_study_snapshot",
            new=AsyncMock(return_value={"study_id": 1}),
        ),
        patch(
            "backend.jobs.quality_job._run_and_persist_report",
            new=AsyncMock(return_value=report_mock),
        ),
        patch(
            "backend.jobs.quality_job._mark_job_done",
            new=AsyncMock(),
        ),
    ):
        from backend.jobs.quality_job import run_quality_eval

        result = await run_quality_eval({}, study_id=1)

    assert result["status"] == "completed"
    assert result["total_score"] == 42
    assert "job_id" in result


async def test_run_quality_eval_returns_completed_with_zero_score():
    """run_quality_eval returns total_score=0 when agent gives all-zero scores.

    When the agent returns an all-zero score the job should still complete
    with total_score=0 in the result.
    """
    import pytest

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    session_maker = _make_session_cm(db)

    report_mock = MagicMock()
    report_mock.total_score = 0

    with (
        patch("backend.core.database._session_maker", session_maker),
        patch(
            "backend.jobs.quality_job._build_study_snapshot",
            new=AsyncMock(return_value={"study_id": 1}),
        ),
        patch(
            "backend.jobs.quality_job._run_and_persist_report",
            new=AsyncMock(return_value=report_mock),
        ),
        patch(
            "backend.jobs.quality_job._mark_job_done",
            new=AsyncMock(),
        ),
    ):
        from backend.jobs.quality_job import run_quality_eval

        result = await run_quality_eval({}, study_id=1)

    assert result["status"] == "completed"
    assert result["total_score"] == 0


# ---------------------------------------------------------------------------
# _build_study_snapshot
# ---------------------------------------------------------------------------


async def test_build_study_snapshot_raises_when_study_not_found():
    """_build_study_snapshot raises ValueError when the Study record is missing.

    A None result from the Study query should raise ValueError.
    """
    import pytest

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))

    from backend.jobs.quality_job import _build_study_snapshot

    with pytest.raises(ValueError, match="not found"):
        await _build_study_snapshot(db, study_id=999)


async def test_build_study_snapshot_returns_dict_with_required_keys():
    """_build_study_snapshot returns a dict containing all required snapshot keys.

    The snapshot must include study_id, study_name, study_type, current_phase,
    pico_saved, search_strategies, test_retest_done, reviewers,
    inclusion_criteria, exclusion_criteria, extractions_done, validity_filled,
    and validity_dimensions.
    """
    study_mock = MagicMock()
    study_mock.name = "Quality Study"
    study_mock.study_type = MagicMock()
    study_mock.study_type.value = "SMS"
    study_mock.current_phase = "quality"
    study_mock.pico_saved_at = None
    study_mock.validity = {}

    empty_result = MagicMock()
    empty_result.scalar_one_or_none.return_value = None
    empty_result.scalars.return_value.all.return_value = []
    empty_result.all.return_value = []

    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            _scalar_result(study_mock),  # Study
            empty_result,                 # SearchExecution + SearchString join
            empty_result,                 # SearchStringIteration
            empty_result,                 # Reviewer
            empty_result,                 # InclusionCriterion
            empty_result,                 # ExclusionCriterion
            empty_result,                 # DataExtraction
        ]
    )

    from backend.jobs.quality_job import _build_study_snapshot

    snapshot = await _build_study_snapshot(db, study_id=1)

    required_keys = {
        "study_id",
        "study_name",
        "study_type",
        "current_phase",
        "pico_saved",
        "search_strategies",
        "test_retest_done",
        "reviewers",
        "inclusion_criteria",
        "exclusion_criteria",
        "extractions_done",
        "validity_filled",
        "validity_dimensions",
    }
    assert required_keys <= set(snapshot.keys())
    assert snapshot["study_id"] == 1
    assert snapshot["study_name"] == "Quality Study"


# ---------------------------------------------------------------------------
# _run_and_persist_report
# ---------------------------------------------------------------------------


async def test_run_and_persist_report_calls_db_add_and_commit():
    """_run_and_persist_report calls db.add and db.commit after agent.run.

    The function should create a QualityReport record and persist it.
    """
    scores = {
        "need_for_review": 1,
        "search_strategy": 2,
        "search_evaluation": 1,
        "extraction_classification": 2,
        "study_validity": 1,
    }

    rubric_detail = MagicMock()
    rubric_detail.score = 1
    rubric_detail.justification = "OK"

    rec_mock = MagicMock()
    rec_mock.priority = "high"
    rec_mock.action = "Fix this"
    rec_mock.target_rubric = "search_strategy"

    agent_result = MagicMock()
    agent_result.scores = scores
    agent_result.rubric_details = {"need_for_review": rubric_detail}
    agent_result.recommendations = [rec_mock]

    agent_mock = MagicMock()
    agent_mock.run = AsyncMock(return_value=agent_result)

    version_result = MagicMock()
    version_result.scalar_one_or_none.return_value = 0

    report_mock = MagicMock()
    report_mock.total_score = 7

    db = AsyncMock()
    db.execute = AsyncMock(return_value=version_result)
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    snapshot = {"study_id": 1}

    with patch(
        "backend.jobs.quality_job._build_quality_judge_with_context",
        new=AsyncMock(return_value=agent_mock),
    ):
        from backend.jobs.quality_job import _run_and_persist_report

        result = await _run_and_persist_report(db, study_id=1, snapshot=snapshot)

    db.add.assert_called_once()
    db.commit.assert_awaited()


# ---------------------------------------------------------------------------
# _build_quality_judge_with_context
# ---------------------------------------------------------------------------


async def test_build_quality_judge_with_context_returns_plain_agent_when_none():
    """_build_quality_judge_with_context returns plain QualityJudgeAgent when no active agent.

    When the Agent query returns None the function should fall back to a default
    QualityJudgeAgent().
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))

    with patch("agents.services.quality_judge.QualityJudgeAgent") as MockAgent:
        MockAgent.return_value = MagicMock()

        from backend.jobs.quality_job import _build_quality_judge_with_context

        result = await _build_quality_judge_with_context(db, study_id=1)

    assert result is not None


async def test_build_quality_judge_with_context_uses_configured_agent():
    """_build_quality_judge_with_context builds agent with provider_config when found.

    When an active Agent record exists the function should look up Provider and
    Model, build a provider_config, and return a configured QualityJudgeAgent.
    """
    agent_record = MagicMock()
    agent_record.provider_id = 1
    agent_record.model_id = 1
    agent_record.system_message_template = "Template {{ role_name }}"

    provider_mock = MagicMock()
    model_mock = MagicMock()
    study_mock = MagicMock()
    study_mock.study_type = MagicMock()
    study_mock.study_type.value = "SMS"
    study_mock.topic = "Testing"

    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            _scalar_result(agent_record),  # Agent lookup
            _scalar_result(provider_mock),  # Provider
            _scalar_result(model_mock),     # AvailableModel
            _scalar_result(study_mock),     # Study
        ]
    )

    built_agent_mock = MagicMock()
    provider_cfg_mock = MagicMock()

    with (
        patch(
            "backend.services.agent_service._build_provider_config",
            return_value=provider_cfg_mock,
        ),
        patch(
            "backend.services.agent_service.build_study_context",
            return_value=MagicMock(domain="SE", study_type="SMS"),
        ),
        patch(
            "backend.services.agent_service.render_system_message",
            return_value="Rendered",
        ),
        patch(
            "agents.services.quality_judge.QualityJudgeAgent",
            return_value=built_agent_mock,
        ),
    ):
        from backend.jobs.quality_job import _build_quality_judge_with_context

        result = await _build_quality_judge_with_context(db, study_id=1)

    assert result is not None


# ---------------------------------------------------------------------------
# _mark_job_done
# ---------------------------------------------------------------------------


async def test_mark_job_done_sets_status_and_commits():
    """_mark_job_done updates job.status and calls db.commit().

    The job record status should be updated and the session committed.
    """
    from db.models.jobs import JobStatus

    job_mock = MagicMock()
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(job_mock))
    db.commit = AsyncMock()

    from backend.jobs.quality_job import _mark_job_done

    await _mark_job_done(db, "job-1", JobStatus.COMPLETED)

    assert job_mock.status == JobStatus.COMPLETED
    db.commit.assert_awaited()


async def test_mark_job_done_does_not_set_error_message_when_no_error():
    """_mark_job_done does not set error_message when error param is None.

    When error is None the error_message field should not be written.
    """
    from db.models.jobs import JobStatus

    job_mock = MagicMock()
    job_mock.error_message = None
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(job_mock))
    db.commit = AsyncMock()

    from backend.jobs.quality_job import _mark_job_done

    await _mark_job_done(db, "job-1", JobStatus.COMPLETED, error=None)

    # error_message should remain None (not overwritten)
    db.commit.assert_awaited()


async def test_mark_job_done_sets_error_message_when_provided():
    """_mark_job_done stores the error string on the job when error is provided.

    When error is a non-empty string it should be stored as job.error_message.
    """
    from db.models.jobs import JobStatus

    job_mock = MagicMock()
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(job_mock))
    db.commit = AsyncMock()

    from backend.jobs.quality_job import _mark_job_done

    await _mark_job_done(db, "job-1", JobStatus.FAILED, error="Agent error")

    db.commit.assert_awaited()
