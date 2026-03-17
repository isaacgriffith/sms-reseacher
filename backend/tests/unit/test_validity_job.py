"""Unit tests for backend.jobs.validity_job.

Covers run_validity_prefill and all private helpers with mocked sessions
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
# run_validity_prefill — happy path
# ---------------------------------------------------------------------------


async def test_run_validity_prefill_returns_completed_status():
    """run_validity_prefill returns {'status': 'completed'} on a successful run.

    When the snapshot and agent run both succeed the job should be marked
    complete and the returned dict should contain status='completed'.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    session_maker = _make_session_cm(db)

    snapshot = {"study_id": 1, "study_name": "Test"}

    with (
        patch("backend.core.database._session_maker", session_maker),
        patch(
            "backend.jobs.validity_job._build_validity_snapshot",
            new=AsyncMock(return_value=snapshot),
        ),
        patch(
            "backend.jobs.validity_job._run_and_persist_validity",
            new=AsyncMock(),
        ),
        patch(
            "backend.jobs.validity_job._mark_job_done",
            new=AsyncMock(),
        ),
    ):
        from backend.jobs.validity_job import run_validity_prefill

        result = await run_validity_prefill({}, study_id=1)

    assert result["status"] == "completed"
    assert "job_id" in result


async def test_run_validity_prefill_returns_failed_status_on_exception():
    """run_validity_prefill returns {'status': 'failed'} when an exception is raised.

    Exceptions from _build_validity_snapshot should be caught and the job
    should be marked failed without re-raising.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.commit = AsyncMock()

    session_maker = _make_session_cm(db)

    with (
        patch("backend.core.database._session_maker", session_maker),
        patch(
            "backend.jobs.validity_job._build_validity_snapshot",
            new=AsyncMock(side_effect=ValueError("study not found")),
        ),
        patch(
            "backend.jobs.validity_job._mark_job_done",
            new=AsyncMock(),
        ),
    ):
        from backend.jobs.validity_job import run_validity_prefill

        result = await run_validity_prefill({}, study_id=999)

    assert result["status"] == "failed"
    assert "job_id" in result


# ---------------------------------------------------------------------------
# _build_validity_snapshot
# ---------------------------------------------------------------------------


async def test_build_validity_snapshot_raises_when_study_not_found():
    """_build_validity_snapshot raises ValueError when the study is missing.

    A None result from the Study query should raise ValueError so the caller
    can handle it gracefully.
    """
    import pytest

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))

    from backend.jobs.validity_job import _build_validity_snapshot

    with pytest.raises(ValueError, match="not found"):
        await _build_validity_snapshot(db, study_id=999)


async def test_build_validity_snapshot_returns_dict_with_expected_keys():
    """_build_validity_snapshot returns a dict containing all required keys.

    The snapshot dict must contain study_id, study_name, study_type,
    current_phase, pico_components, search_strategies, databases,
    test_retest_done, reviewers, inclusion_criteria, exclusion_criteria, and
    extraction_summary.
    """
    study_mock = MagicMock()
    study_mock.name = "My Study"
    study_mock.study_type = MagicMock()
    study_mock.study_type.value = "SMS"
    study_mock.current_phase = "extraction"
    study_mock.pico_saved_at = None
    study_mock.validity = {}

    empty_result = MagicMock()
    empty_result.scalar_one_or_none.return_value = None
    empty_result.scalars.return_value.all.return_value = []

    db = AsyncMock()
    # First call: Study lookup returns study_mock
    db.execute = AsyncMock(
        side_effect=[
            _scalar_result(study_mock),  # Study
            _scalar_result(None),         # PICOComponent
            empty_result,                 # SearchString
            empty_result,                 # SearchExecution
            empty_result,                 # Reviewer
            empty_result,                 # InclusionCriterion
            empty_result,                 # ExclusionCriterion
            empty_result,                 # DataExtraction
        ]
    )

    from backend.jobs.validity_job import _build_validity_snapshot

    snapshot = await _build_validity_snapshot(db, study_id=1)

    required_keys = {
        "study_id",
        "study_name",
        "study_type",
        "current_phase",
        "pico_components",
        "search_strategies",
        "databases",
        "test_retest_done",
        "reviewers",
        "inclusion_criteria",
        "exclusion_criteria",
        "extraction_summary",
    }
    assert required_keys <= set(snapshot.keys())


# ---------------------------------------------------------------------------
# _run_and_persist_validity
# ---------------------------------------------------------------------------


async def test_run_and_persist_validity_calls_commit():
    """_run_and_persist_validity calls db.commit after persisting validity data.

    The function should call agent.run and then update study.validity and commit.
    """
    validity_result = MagicMock()
    validity_result.model_dump.return_value = {"descriptive": "Good"}

    agent_mock = MagicMock()
    agent_mock.run = AsyncMock(return_value=validity_result)

    study_mock = MagicMock()
    study_mock.validity = {}

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(study_mock))
    db.commit = AsyncMock()

    snapshot = {
        "study_id": 1,
        "study_name": "Test",
        "study_type": "SMS",
        "current_phase": "validity",
        "pico_components": [],
        "search_strategies": [],
        "databases": None,
        "test_retest_done": False,
        "reviewers": [],
        "inclusion_criteria": [],
        "exclusion_criteria": [],
        "extraction_summary": None,
    }

    with patch(
        "backend.jobs.validity_job._build_validity_agent_with_context",
        new=AsyncMock(return_value=agent_mock),
    ):
        from backend.jobs.validity_job import _run_and_persist_validity

        await _run_and_persist_validity(db, study_id=1, snapshot=snapshot)

    db.commit.assert_awaited()


# ---------------------------------------------------------------------------
# _build_validity_agent_with_context
# ---------------------------------------------------------------------------


async def test_build_validity_agent_with_context_returns_plain_agent_when_none():
    """_build_validity_agent_with_context returns plain ValidityAgent when no active agent.

    When the Agent query returns None the function should instantiate and
    return a default ValidityAgent().
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))

    with patch("agents.services.validity.ValidityAgent") as MockValidity:
        MockValidity.return_value = MagicMock()

        from backend.jobs.validity_job import _build_validity_agent_with_context

        result = await _build_validity_agent_with_context(db, study_id=1)

    assert result is not None


# ---------------------------------------------------------------------------
# _mark_job_done
# ---------------------------------------------------------------------------


async def test_mark_job_done_sets_status_and_commits():
    """_mark_job_done updates job.status and calls db.commit().

    The job record's status field should be updated and the session committed.
    """
    from db.models.jobs import JobStatus

    job_mock = MagicMock()
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(job_mock))
    db.commit = AsyncMock()

    from backend.jobs.validity_job import _mark_job_done

    await _mark_job_done(db, "job-1", JobStatus.COMPLETED)

    assert job_mock.status == JobStatus.COMPLETED
    db.commit.assert_awaited()


async def test_mark_job_done_sets_error_message_when_provided():
    """_mark_job_done sets error_message when error param is not None.

    When an error string is passed it should be stored on the job record.
    """
    from db.models.jobs import JobStatus

    job_mock = MagicMock()
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(job_mock))
    db.commit = AsyncMock()

    from backend.jobs.validity_job import _mark_job_done

    await _mark_job_done(db, "job-1", JobStatus.FAILED, error="Something went wrong")

    assert job_mock.error_message == "Something went wrong"
    db.commit.assert_awaited()


async def test_mark_job_done_does_nothing_when_job_not_found():
    """_mark_job_done does not raise when the job record is missing.

    A None result from the job query should be silently ignored.
    """
    from db.models.jobs import JobStatus

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.commit = AsyncMock()

    from backend.jobs.validity_job import _mark_job_done

    # Should not raise
    await _mark_job_done(db, "missing", JobStatus.COMPLETED)
    db.commit.assert_not_awaited()


# ---------------------------------------------------------------------------
# Additional coverage: _build_validity_snapshot with pico and databases
# ---------------------------------------------------------------------------


async def test_build_validity_snapshot_populates_pico_components():
    """_build_validity_snapshot populates pico_components when PICOComponent found.

    When a PICOComponent row is found and has non-None fields those fields should
    be included in pico_components as {type, content} dicts.
    """
    study_mock = MagicMock()
    study_mock.name = "PICO Study"
    study_mock.study_type = MagicMock()
    study_mock.study_type.value = "SMS"
    study_mock.current_phase = "screening"
    study_mock.pico_saved_at = None
    study_mock.validity = {}

    pico_mock = MagicMock()
    pico_mock.population = "Software developers"
    pico_mock.intervention = "TDD"
    pico_mock.comparison = None
    pico_mock.outcome = "Code quality"
    pico_mock.context = None

    empty_result = MagicMock()
    empty_result.scalar_one_or_none.return_value = None
    empty_result.scalars.return_value.all.return_value = []

    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            _scalar_result(study_mock),    # Study
            _scalar_result(pico_mock),     # PICOComponent
            empty_result,                   # SearchString
            empty_result,                   # SearchExecution
            empty_result,                   # Reviewer
            empty_result,                   # InclusionCriterion
            empty_result,                   # ExclusionCriterion
            empty_result,                   # DataExtraction
        ]
    )

    from backend.jobs.validity_job import _build_validity_snapshot

    snapshot = await _build_validity_snapshot(db, study_id=1)

    # pico_components should have entries for non-None fields
    types_in_pico = [pc["type"] for pc in snapshot["pico_components"]]
    assert "population" in types_in_pico
    assert "intervention" in types_in_pico
    assert "outcome" in types_in_pico
    # None fields should not appear
    assert "comparison" not in types_in_pico
    assert "context" not in types_in_pico


async def test_build_validity_snapshot_populates_databases_from_search_executions():
    """_build_validity_snapshot extracts database names from SearchExecution rows.

    When SearchExecution rows have databases_queried the names should be
    deduplicated and joined into the databases field.
    """
    study_mock = MagicMock()
    study_mock.name = "DB Study"
    study_mock.study_type = MagicMock()
    study_mock.study_type.value = "SMS"
    study_mock.current_phase = "search"
    study_mock.pico_saved_at = None
    study_mock.validity = {}

    exec_mock = MagicMock()
    exec_mock.databases_queried = ["IEEE", "ACM", "IEEE"]  # duplicates

    empty_result = MagicMock()
    empty_result.scalar_one_or_none.return_value = None
    empty_result.scalars.return_value.all.return_value = []

    exec_result = MagicMock()
    exec_result.scalars.return_value.all.return_value = [exec_mock]

    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            _scalar_result(study_mock),    # Study
            _scalar_result(None),           # PICOComponent
            empty_result,                   # SearchString
            exec_result,                    # SearchExecution
            empty_result,                   # Reviewer
            empty_result,                   # InclusionCriterion
            empty_result,                   # ExclusionCriterion
            empty_result,                   # DataExtraction
        ]
    )

    from backend.jobs.validity_job import _build_validity_snapshot

    snapshot = await _build_validity_snapshot(db, study_id=1)

    # databases should be a comma-joined string of deduplicated names
    assert snapshot["databases"] is not None
    assert "ACM" in snapshot["databases"]
    assert "IEEE" in snapshot["databases"]


async def test_build_validity_snapshot_sets_extraction_summary_when_extractions_found():
    """_build_validity_snapshot sets extraction_summary when done extractions exist.

    When DataExtraction rows are found the extraction_summary should describe
    the count of extracted papers.
    """
    study_mock = MagicMock()
    study_mock.name = "Extraction Study"
    study_mock.study_type = MagicMock()
    study_mock.study_type.value = "SMS"
    study_mock.current_phase = "extraction"
    study_mock.pico_saved_at = None
    study_mock.validity = {}

    extraction_mock = MagicMock()
    extraction_result = MagicMock()
    extraction_result.scalars.return_value.all.return_value = [extraction_mock, extraction_mock]

    empty_result = MagicMock()
    empty_result.scalar_one_or_none.return_value = None
    empty_result.scalars.return_value.all.return_value = []

    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            _scalar_result(study_mock),    # Study
            _scalar_result(None),           # PICOComponent
            empty_result,                   # SearchString
            empty_result,                   # SearchExecution
            empty_result,                   # Reviewer
            empty_result,                   # InclusionCriterion
            empty_result,                   # ExclusionCriterion
            extraction_result,              # DataExtraction
        ]
    )

    from backend.jobs.validity_job import _build_validity_snapshot

    snapshot = await _build_validity_snapshot(db, study_id=1)

    assert snapshot["extraction_summary"] is not None
    assert "2" in snapshot["extraction_summary"]


async def test_run_and_persist_validity_raises_when_study_not_found():
    """_run_and_persist_validity raises ValueError when Study is not found post-agent.

    If the Study query returns None after the agent has run the function should
    raise ValueError.
    """
    import pytest

    validity_result = MagicMock()
    validity_result.model_dump.return_value = {"descriptive": "Good"}

    agent_mock = MagicMock()
    agent_mock.run = AsyncMock(return_value=validity_result)

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))  # Study not found
    db.commit = AsyncMock()

    snapshot = {
        "study_id": 1,
        "study_name": "Test",
        "study_type": "SMS",
        "current_phase": "validity",
        "pico_components": [],
        "search_strategies": [],
        "databases": None,
        "test_retest_done": False,
        "reviewers": [],
        "inclusion_criteria": [],
        "exclusion_criteria": [],
        "extraction_summary": None,
    }

    with patch(
        "backend.jobs.validity_job._build_validity_agent_with_context",
        new=AsyncMock(return_value=agent_mock),
    ):
        from backend.jobs.validity_job import _run_and_persist_validity

        with pytest.raises(ValueError, match="not found when persisting"):
            await _run_and_persist_validity(db, study_id=1, snapshot=snapshot)


async def test_build_validity_agent_with_context_uses_configured_agent():
    """_build_validity_agent_with_context builds agent with provider_config when found.

    When an active Agent record exists the function should look up Provider and
    Model, build a provider_config, and return a configured ValidityAgent.
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
            "agents.services.validity.ValidityAgent",
            return_value=built_agent_mock,
        ),
    ):
        from backend.jobs.validity_job import _build_validity_agent_with_context

        result = await _build_validity_agent_with_context(db, study_id=1)

    assert result is not None
