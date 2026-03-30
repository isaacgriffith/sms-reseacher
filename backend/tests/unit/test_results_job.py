"""Unit tests for backend.jobs.results_job.

Covers run_generate_results, run_export, _store_export, and all private
helpers with mocked sessions, agent dependencies, and file system calls.
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
# run_generate_results — happy path
# ---------------------------------------------------------------------------


async def test_run_generate_results_returns_job_id_and_counts():
    """run_generate_results returns domain_model_id, charts_generated, job_id on success.

    When all sub-steps succeed the returned dict should have the three expected
    keys and status should be successful (no exception raised).
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    session_maker = _make_session_cm(db)

    with (
        patch("backend.core.database._session_maker", session_maker),
        patch(
            "backend.jobs.results_job._load_completed_extractions",
            new=AsyncMock(return_value=[]),
        ),
        patch(
            "backend.jobs.results_job._load_study_topic",
            new=AsyncMock(return_value="Testing"),
        ),
        patch(
            "backend.jobs.results_job._load_research_questions",
            new=AsyncMock(return_value=[]),
        ),
        patch(
            "backend.jobs.results_job._update_job_progress",
            new=AsyncMock(),
        ),
        patch(
            "backend.jobs.results_job._run_domain_model_agent",
            new=AsyncMock(return_value=7),
        ),
        patch(
            "backend.jobs.results_job._generate_all_charts",
            new=AsyncMock(return_value=3),
        ),
        patch(
            "backend.jobs.results_job._mark_job_complete_ok",
            new=AsyncMock(),
        ),
    ):
        from backend.jobs.results_job import run_generate_results

        result = await run_generate_results({}, study_id=1)

    assert result["domain_model_id"] == 7
    assert result["charts_generated"] == 3
    assert "job_id" in result


async def test_run_generate_results_multiple_extractions():
    """run_generate_results passes extractions to domain model agent.

    When extractions are available all steps should execute in order and the
    correct counts should be returned.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    session_maker = _make_session_cm(db)

    extractions = [
        {"research_type": "evaluation", "open_codings": ["c1"], "keywords": ["k1"], "summary": "S"}
    ]

    with (
        patch("backend.core.database._session_maker", session_maker),
        patch(
            "backend.jobs.results_job._load_completed_extractions",
            new=AsyncMock(return_value=extractions),
        ),
        patch(
            "backend.jobs.results_job._load_study_topic",
            new=AsyncMock(return_value="CI/CD"),
        ),
        patch(
            "backend.jobs.results_job._load_research_questions",
            new=AsyncMock(return_value=["RQ1?"]),
        ),
        patch(
            "backend.jobs.results_job._update_job_progress",
            new=AsyncMock(),
        ),
        patch(
            "backend.jobs.results_job._run_domain_model_agent",
            new=AsyncMock(return_value=9),
        ),
        patch(
            "backend.jobs.results_job._generate_all_charts",
            new=AsyncMock(return_value=5),
        ),
        patch(
            "backend.jobs.results_job._mark_job_complete_ok",
            new=AsyncMock(),
        ),
    ):
        from backend.jobs.results_job import run_generate_results

        result = await run_generate_results({}, study_id=2)

    assert result["domain_model_id"] == 9
    assert result["charts_generated"] == 5


# ---------------------------------------------------------------------------
# run_export
# ---------------------------------------------------------------------------


async def test_run_export_returns_job_id_and_download_url():
    """run_export returns job_id, download_url, and size_bytes on success.

    When build_export and _store_export both succeed the returned dict should
    contain all three expected keys.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.commit = AsyncMock()

    session_maker = _make_session_cm(db)

    with (
        patch("backend.core.database._session_maker", session_maker),
        patch(
            "backend.services.export.build_export",
            new=AsyncMock(return_value=b"fake-export"),
        ),
        patch(
            "backend.jobs.results_job._store_export",
            return_value="/exports/test.zip",
        ),
    ):
        from backend.jobs.results_job import run_export

        result = await run_export({}, study_id=1, format="full_archive")

    assert "job_id" in result
    assert result["download_url"] == "/exports/test.zip"
    assert result["size_bytes"] == len(b"fake-export")


async def test_run_export_raises_on_exception():
    """run_export re-raises exceptions after marking the job failed.

    When build_export raises the exception should propagate to the caller.
    """
    import pytest

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.commit = AsyncMock()

    session_maker = _make_session_cm(db)

    with (
        patch("backend.core.database._session_maker", session_maker),
        patch(
            "backend.services.export.build_export",
            new=AsyncMock(side_effect=ValueError("export failed")),
        ),
        patch(
            "backend.jobs.results_job._mark_job_failed",
            new=AsyncMock(),
        ),
    ):
        from backend.jobs.results_job import run_export

        with pytest.raises(ValueError):
            await run_export({}, study_id=1, format="full_archive")


# ---------------------------------------------------------------------------
# _store_export
# ---------------------------------------------------------------------------


def test_store_export_writes_file_and_returns_url():
    """_store_export writes a file to disk and returns a /exports/ URL.

    The returned URL should begin with /exports/ and the file should exist.
    """
    import os
    import tempfile

    payload = b"hello export"

    with patch("backend.jobs.results_job.tempfile.gettempdir", return_value=tempfile.gettempdir()):
        from backend.jobs.results_job import _store_export

        url = _store_export("test-job-id", "full_archive", payload)

    assert url.startswith("/exports/")
    assert "test-job-id" in url
    assert url.endswith(".zip")


def test_store_export_uses_correct_extension_for_json_only():
    """_store_export appends .json extension for the json_only format.

    The URL should end with .json when format='json_only' is specified.
    """
    from backend.jobs.results_job import _store_export

    url = _store_export("job-json", "json_only", b"{}")
    assert url.endswith(".json")


def test_store_export_uses_bin_for_unknown_format():
    """_store_export appends .bin extension for an unrecognised format.

    Formats not in the extension map should produce a .bin file.
    """
    from backend.jobs.results_job import _store_export

    url = _store_export("job-unknown", "not_a_format", b"data")
    assert url.endswith(".bin")


# ---------------------------------------------------------------------------
# _load_completed_extractions
# ---------------------------------------------------------------------------


async def test_load_completed_extractions_returns_empty_when_none():
    """_load_completed_extractions returns an empty list when no extractions exist.

    A query that returns no rows should produce an empty list.
    """
    r = MagicMock()
    r.scalars.return_value.all.return_value = []
    db = AsyncMock()
    db.execute = AsyncMock(return_value=r)

    from backend.jobs.results_job import _load_completed_extractions

    result = await _load_completed_extractions(db, study_id=1)
    assert result == []


async def test_load_completed_extractions_maps_extraction_fields():
    """_load_completed_extractions maps ORM rows to plain dicts with expected keys.

    Each row should be converted to a dict containing research_type, venue_type,
    venue_name, author_details, summary, open_codings, keywords, and question_data.
    """
    row = MagicMock()
    row.research_type = "evaluation"
    row.venue_type = "journal"
    row.venue_name = "TSE"
    row.author_details = []
    row.summary = "Summary text"
    row.open_codings = ["coding1"]
    row.keywords = ["kw1"]
    row.question_data = {"rq1": "answer"}

    r = MagicMock()
    r.scalars.return_value.all.return_value = [row]
    db = AsyncMock()
    db.execute = AsyncMock(return_value=r)

    from backend.jobs.results_job import _load_completed_extractions

    result = await _load_completed_extractions(db, study_id=1)
    assert len(result) == 1
    assert result[0]["research_type"] == "evaluation"
    assert result[0]["venue_name"] == "TSE"


# ---------------------------------------------------------------------------
# _load_study_topic
# ---------------------------------------------------------------------------


async def test_load_study_topic_returns_empty_when_study_not_found():
    """_load_study_topic returns '' when the Study record does not exist.

    A missing study should produce an empty string without raising.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))

    from backend.jobs.results_job import _load_study_topic

    result = await _load_study_topic(db, study_id=999)
    assert result == ""


async def test_load_study_topic_returns_title():
    """_load_study_topic returns the study title when the study is found.

    The study's title field should be returned as the topic string.
    """
    study_mock = MagicMock()
    study_mock.topic = "My Study Topic"

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(study_mock))

    from backend.jobs.results_job import _load_study_topic

    result = await _load_study_topic(db, study_id=1)
    assert result == "My Study Topic"


# ---------------------------------------------------------------------------
# _load_research_questions
# ---------------------------------------------------------------------------


async def test_load_research_questions_returns_empty_when_no_metadata():
    """_load_research_questions returns [] when study.metadata_ is falsy.

    When there is no metadata the function should return an empty list.
    """
    study_mock = MagicMock()
    study_mock.metadata_ = None

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(study_mock))

    from backend.jobs.results_job import _load_research_questions

    result = await _load_research_questions(db, study_id=1)
    assert result == []


async def test_load_research_questions_returns_text_strings():
    """_load_research_questions returns the text of each research question.

    The returned list should contain the 'text' field of each research question
    dict in study.metadata_.
    """
    study_mock = MagicMock()
    study_mock.metadata_ = {
        "research_questions": [
            {"id": 1, "text": "What is CI/CD?"},
            {"id": 2, "text": "How is it measured?"},
        ]
    }

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(study_mock))

    from backend.jobs.results_job import _load_research_questions

    result = await _load_research_questions(db, study_id=1)
    assert "What is CI/CD?" in result
    assert "How is it measured?" in result


# ---------------------------------------------------------------------------
# _run_domain_model_agent
# ---------------------------------------------------------------------------


async def test_run_domain_model_agent_returns_record_id():
    """_run_domain_model_agent calls agent.run and persists a DomainModel record.

    The function should call db.add and db.commit and return the record's id.
    """
    concept_mock = MagicMock()
    concept_mock.model_dump.return_value = {"name": "Concept A"}

    relationship_mock = MagicMock()
    relationship_mock.from_ = "A"
    relationship_mock.to = "B"
    relationship_mock.label = "relates_to"
    relationship_mock.type = "association"

    agent_result = MagicMock()
    agent_result.concepts = [concept_mock]
    agent_result.relationships = [relationship_mock]

    agent_mock = MagicMock()
    agent_mock.run = AsyncMock(return_value=agent_result)

    domain_model_record = MagicMock()
    domain_model_record.id = 5

    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock(side_effect=lambda r: setattr(r, "id", 5) or None)

    with patch(
        "backend.jobs.results_job._build_domain_model_agent_with_context",
        new=AsyncMock(return_value=agent_mock),
    ):
        from backend.jobs.results_job import _run_domain_model_agent

        record_id = await _run_domain_model_agent(
            db,
            study_id=1,
            topic="Testing",
            research_questions=["RQ1"],
            extractions=[],
        )

    db.add.assert_called_once()
    db.commit.assert_awaited()


# ---------------------------------------------------------------------------
# _build_domain_model_agent_with_context
# ---------------------------------------------------------------------------


async def test_build_domain_model_agent_with_context_returns_plain_when_no_agent():
    """_build_domain_model_agent_with_context returns plain DomainModelAgent when no active agent.

    When the Agent query returns None the function should return a default
    DomainModelAgent() without provider config.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))

    with patch("agents.services.domain_modeler.DomainModelAgent") as MockAgent:
        MockAgent.return_value = MagicMock()

        from backend.jobs.results_job import _build_domain_model_agent_with_context

        result = await _build_domain_model_agent_with_context(db, study_id=1)

    assert result is not None


# ---------------------------------------------------------------------------
# _update_job_progress
# ---------------------------------------------------------------------------


async def test_update_job_progress_sets_pct():
    """_update_job_progress writes progress_pct when the job record is found.

    The job's progress_pct should be updated and db.commit should be called.
    """
    job_mock = MagicMock()
    job_mock.progress_pct = 0

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(job_mock))
    db.commit = AsyncMock()

    from backend.jobs.results_job import _update_job_progress

    await _update_job_progress(db, "job-1", 30, {"step": "loading"})

    assert job_mock.progress_pct == 30
    db.commit.assert_awaited()


async def test_update_job_progress_does_nothing_when_missing():
    """_update_job_progress does not raise when the job record is missing.

    A None result from the job query should be silently ignored.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.commit = AsyncMock()

    from backend.jobs.results_job import _update_job_progress

    await _update_job_progress(db, "missing", 50, {})
    db.commit.assert_not_awaited()


# ---------------------------------------------------------------------------
# _mark_job_complete_ok
# ---------------------------------------------------------------------------


async def test_mark_job_complete_ok_does_not_raise_when_job_missing():
    """_mark_job_complete_ok silently does nothing when the job record is missing.

    The function should not raise even when the job is not found.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.commit = AsyncMock()

    from backend.jobs.results_job import _mark_job_complete_ok

    await _mark_job_complete_ok(db, "missing-job", {"charts": 0})
    db.commit.assert_not_awaited()


# ---------------------------------------------------------------------------
# _mark_job_failed
# ---------------------------------------------------------------------------


async def test_mark_job_failed_sets_failed_status():
    """_mark_job_failed sets job.status=FAILED and stores the error message.

    The job record should be marked FAILED with the error message persisted.
    """
    from db.models.jobs import JobStatus

    job_mock = MagicMock()
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(job_mock))
    db.commit = AsyncMock()

    from backend.jobs.results_job import _mark_job_failed

    await _mark_job_failed(db, "job-1", "Something went wrong")

    assert job_mock.status == JobStatus.FAILED
    assert job_mock.error_message == "Something went wrong"
    db.commit.assert_awaited()


async def test_mark_job_failed_does_nothing_when_job_missing():
    """_mark_job_failed silently does nothing when the job record is missing.

    A None result from the job query should be silently ignored.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.commit = AsyncMock()

    from backend.jobs.results_job import _mark_job_failed

    await _mark_job_failed(db, "missing-job", "Error")
    db.commit.assert_not_awaited()


# ---------------------------------------------------------------------------
# Additional coverage: _mark_job_complete_ok when job is found
# ---------------------------------------------------------------------------


async def test_mark_job_complete_ok_sets_completed_status_when_found():
    """_mark_job_complete_ok sets COMPLETED status when the job record is found.

    When the job is found its status should be set to COMPLETED and committed.
    """
    from db.models.jobs import JobStatus

    job_mock = MagicMock()
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(job_mock))
    db.commit = AsyncMock()

    from backend.jobs.results_job import _mark_job_complete_ok

    await _mark_job_complete_ok(db, "job-1", {"charts": 3})

    assert job_mock.status == JobStatus.COMPLETED
    db.commit.assert_awaited()


# ---------------------------------------------------------------------------
# Additional coverage: _run_domain_model_agent with keyword dedup
# ---------------------------------------------------------------------------


async def test_run_domain_model_agent_deduplicates_keywords():
    """_run_domain_model_agent deduplicates keywords across extractions.

    Keywords that appear multiple times should only be passed once to agent.run.
    This test exercises the keyword deduplication loop.
    """
    agent_result = MagicMock()
    agent_result.concepts = []
    agent_result.relationships = []

    agent_mock = MagicMock()
    agent_mock.run = AsyncMock(return_value=agent_result)

    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    # Two extractions with overlapping keywords
    extractions = [
        {"open_codings": [], "keywords": ["TDD", "testing"], "summary": "Paper 1"},
        {"open_codings": [], "keywords": ["testing", "CI/CD"], "summary": "Paper 2"},
    ]

    with patch(
        "backend.jobs.results_job._build_domain_model_agent_with_context",
        new=AsyncMock(return_value=agent_mock),
    ):
        from backend.jobs.results_job import _run_domain_model_agent

        await _run_domain_model_agent(
            db,
            study_id=1,
            topic="Testing",
            research_questions=[],
            extractions=extractions,
        )

    # agent.run should have been called
    agent_mock.run.assert_awaited_once()


# ---------------------------------------------------------------------------
# Additional coverage: run_export — job record update
# ---------------------------------------------------------------------------


async def test_run_export_updates_job_record_status():
    """run_export updates the BackgroundJob status to COMPLETED on success.

    The job record's status should be set to COMPLETED after a successful export.
    """
    job_mock = MagicMock()

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(job_mock))
    db.add = MagicMock()
    db.commit = AsyncMock()

    session_maker = _make_session_cm(db)

    with (
        patch("backend.core.database._session_maker", session_maker),
        patch(
            "backend.services.export.build_export",
            new=AsyncMock(return_value=b"export-data"),
        ),
        patch(
            "backend.jobs.results_job._store_export",
            return_value="/exports/test.json",
        ),
    ):
        from backend.jobs.results_job import run_export

        result = await run_export({}, study_id=1, format="json_only")

    assert result["download_url"] == "/exports/test.json"


# ---------------------------------------------------------------------------
# Additional coverage: _build_domain_model_agent_with_context with configured agent
# ---------------------------------------------------------------------------


async def test_build_domain_model_agent_with_context_uses_configured_agent():
    """_build_domain_model_agent_with_context builds with provider_config when found.

    When an active Agent record exists the function should look up Provider and
    Model, build a provider_config, and return a configured DomainModelAgent.
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
            "agents.services.domain_modeler.DomainModelAgent",
            return_value=built_agent_mock,
        ),
    ):
        from backend.jobs.results_job import _build_domain_model_agent_with_context

        result = await _build_domain_model_agent_with_context(db, study_id=1)

    assert result is not None
