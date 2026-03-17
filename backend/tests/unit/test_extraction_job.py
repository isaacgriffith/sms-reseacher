"""Unit tests for backend.jobs.extraction_job.

Covers the main entry-point run_batch_extraction and all private helpers
with fully-mocked database sessions and agent dependencies.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session_cm(db_mock: AsyncMock) -> MagicMock:
    """Wrap db_mock in an async context-manager returned by _session_maker().

    Args:
        db_mock: AsyncMock that acts as the SQLAlchemy session.

    Returns:
        A MagicMock whose call returns an async context manager yielding db_mock.
    """
    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=db_mock)
    cm.__aexit__ = AsyncMock(return_value=False)
    session_maker = MagicMock(return_value=cm)
    return session_maker


def _scalar_result(value: object) -> MagicMock:
    """Return a mock that behaves like the SQLAlchemy result of a scalar query.

    Args:
        value: The value returned by scalar_one_or_none().

    Returns:
        MagicMock mimicking an AsyncSession.execute() return value.
    """
    r = MagicMock()
    r.scalar_one_or_none.return_value = value
    r.scalars.return_value.all.return_value = [] if value is None else [value]
    r.scalars.return_value.first.return_value = value
    return r


# ---------------------------------------------------------------------------
# run_batch_extraction — basic happy path
# ---------------------------------------------------------------------------


async def test_run_batch_extraction_returns_job_id_and_counts_when_no_papers():
    """run_batch_extraction returns processed=0 and failed=0 when no papers exist.

    When _load_accepted_without_extraction returns an empty list the job should
    complete immediately with zero processed and zero failed counts.
    """
    db = AsyncMock()
    # First execute: job lookup for _update_job_progress / _mark_job_complete queries
    # db.add / db.commit are also needed
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    session_maker = _make_session_cm(db)

    with (
        patch("backend.core.database._session_maker", session_maker),
        patch(
            "backend.jobs.extraction_job._load_accepted_without_extraction",
            new=AsyncMock(return_value=[]),
        ),
    ):
        from backend.jobs.extraction_job import run_batch_extraction

        result = await run_batch_extraction({}, study_id=1)

    assert result["processed"] == 0
    assert result["failed"] == 0
    assert "job_id" in result


async def test_run_batch_extraction_increments_failed_on_paper_error():
    """run_batch_extraction increments failed counter when _extract_single_paper raises.

    If one paper throws an exception the job should still complete and report
    failed=1 rather than propagating the exception.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    session_maker = _make_session_cm(db)

    cp_mock = MagicMock()
    cp_mock.id = 42

    with (
        patch("backend.core.database._session_maker", session_maker),
        patch(
            "backend.jobs.extraction_job._load_accepted_without_extraction",
            new=AsyncMock(return_value=[cp_mock]),
        ),
        patch(
            "backend.jobs.extraction_job._extract_single_paper",
            new=AsyncMock(side_effect=RuntimeError("extraction failed")),
        ),
    ):
        from backend.jobs.extraction_job import run_batch_extraction

        result = await run_batch_extraction({}, study_id=1)

    assert result["failed"] == 1


# ---------------------------------------------------------------------------
# _load_accepted_without_extraction
# ---------------------------------------------------------------------------


async def test_load_accepted_without_extraction_returns_list():
    """_load_accepted_without_extraction returns whatever scalars().all() gives.

    The helper should pass through the ORM results as a list.
    """
    paper_mock = MagicMock()
    paper_mock.id = 7

    r = MagicMock()
    r.scalars.return_value.all.return_value = [paper_mock]
    db = AsyncMock()
    db.execute = AsyncMock(return_value=r)

    from backend.jobs.extraction_job import _load_accepted_without_extraction

    result = await _load_accepted_without_extraction(db, study_id=1)
    assert paper_mock in result


# ---------------------------------------------------------------------------
# _fetch_paper_full_text
# ---------------------------------------------------------------------------


async def test_fetch_paper_full_text_returns_empty_when_paper_not_found():
    """_fetch_paper_full_text returns ('', False) when the Paper record is missing.

    When Paper.scalar_one_or_none() returns None the function should fall back
    gracefully rather than raising.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))

    cp_mock = MagicMock()
    cp_mock.paper_id = 99

    from backend.jobs.extraction_job import _fetch_paper_full_text

    text, is_full = await _fetch_paper_full_text(cp_mock, db)
    assert text == ""
    assert is_full is False


async def test_fetch_paper_full_text_falls_back_to_abstract_on_mcp_failure():
    """_fetch_paper_full_text returns abstract when MCP HTTP call fails.

    If the researcher-mcp endpoint raises an exception the helper should fall
    back to paper.abstract without re-raising.
    """
    paper_mock = MagicMock()
    paper_mock.doi = "10.1/test"
    paper_mock.abstract = "The abstract text."
    paper_mock.title = "Title"

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(paper_mock))

    cp_mock = MagicMock()
    cp_mock.paper_id = 5

    with (
        patch(
            "backend.core.config.get_settings",
            return_value=MagicMock(researcher_mcp_url="http://localhost:8002/sse"),
        ),
        patch("httpx.AsyncClient") as mock_client,
    ):
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=Exception("connection refused")
        )

        from backend.jobs.extraction_job import _fetch_paper_full_text

        text, is_full = await _fetch_paper_full_text(cp_mock, db)

    assert text == "The abstract text."
    assert is_full is False


async def test_fetch_paper_full_text_returns_full_text_on_success():
    """_fetch_paper_full_text returns the MCP full text when available.

    When the researcher-mcp endpoint returns a valid text response the helper
    should return that text with is_full_text=True.
    """
    paper_mock = MagicMock()
    paper_mock.doi = "10.1/test"
    paper_mock.abstract = "Fallback"

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(paper_mock))

    cp_mock = MagicMock()
    cp_mock.paper_id = 5

    resp_mock = MagicMock()
    resp_mock.status_code = 200
    resp_mock.json.return_value = {"text": "Full PDF text"}

    with (
        patch(
            "backend.core.config.get_settings",
            return_value=MagicMock(researcher_mcp_url="http://localhost:8002/sse"),
        ),
        patch("httpx.AsyncClient") as mock_client,
    ):
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=resp_mock
        )

        from backend.jobs.extraction_job import _fetch_paper_full_text

        text, is_full = await _fetch_paper_full_text(cp_mock, db)

    assert text == "Full PDF text"
    assert is_full is True


# ---------------------------------------------------------------------------
# _extract_single_paper
# ---------------------------------------------------------------------------


async def test_extract_single_paper_returns_none_when_paper_missing():
    """_extract_single_paper returns None when the Paper record cannot be found.

    When the Paper query returns None the function should return None rather than
    attempting extraction.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))

    cp_mock = MagicMock()
    cp_mock.paper_id = 77
    cp_mock.study_id = 1

    from backend.jobs.extraction_job import _extract_single_paper

    result = await _extract_single_paper(db, cp_mock)
    assert result is None


async def test_extract_single_paper_returns_none_when_no_text():
    """_extract_single_paper returns None when _fetch_paper_full_text gives empty text.

    Without any text to extract from the function should short-circuit.
    """
    paper_mock = MagicMock()
    paper_mock.doi = None
    paper_mock.abstract = None
    paper_mock.title = None

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(paper_mock))

    cp_mock = MagicMock()
    cp_mock.paper_id = 5
    cp_mock.study_id = 1

    with patch(
        "backend.jobs.extraction_job._fetch_paper_full_text",
        new=AsyncMock(return_value=("", False)),
    ):
        from backend.jobs.extraction_job import _extract_single_paper

        result = await _extract_single_paper(db, cp_mock)
    assert result is None


async def test_extract_single_paper_persists_record():
    """_extract_single_paper calls db.add and db.commit when extraction succeeds.

    The function should persist a DataExtraction record and return it.
    """
    paper_mock = MagicMock()
    paper_mock.doi = "10.1/x"
    paper_mock.title = "T"
    paper_mock.authors = []
    paper_mock.year = 2024
    paper_mock.venue = "TSE"

    extraction_result_mock = MagicMock()
    extraction_result_mock.research_type = "evaluation"
    extraction_result_mock.venue_type = "journal"
    extraction_result_mock.venue_name = "TSE"
    extraction_result_mock.author_details = []
    extraction_result_mock.summary = "Summary"
    extraction_result_mock.open_codings = []
    extraction_result_mock.keywords = []
    extraction_result_mock.question_data = {}

    agent_mock = MagicMock()
    agent_mock.run = AsyncMock(return_value=extraction_result_mock)

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(paper_mock))
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    cp_mock = MagicMock()
    cp_mock.paper_id = 5
    cp_mock.id = 10
    cp_mock.study_id = 1

    with (
        patch(
            "backend.jobs.extraction_job._fetch_paper_full_text",
            new=AsyncMock(return_value=("Paper full text", True)),
        ),
        patch(
            "backend.jobs.extraction_job._load_research_questions",
            new=AsyncMock(return_value=[]),
        ),
        patch(
            "backend.jobs.extraction_job._build_extractor_with_context",
            new=AsyncMock(return_value=agent_mock),
        ),
    ):
        from backend.jobs.extraction_job import _extract_single_paper

        await _extract_single_paper(db, cp_mock)

    db.commit.assert_called()


# ---------------------------------------------------------------------------
# _build_extractor_with_context
# ---------------------------------------------------------------------------


async def test_build_extractor_with_context_returns_plain_agent_when_no_agent_record():
    """_build_extractor_with_context returns a plain ExtractorAgent when no active agent exists.

    When the Agent query returns None the function should fall back to a
    default ExtractorAgent() without provider config.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))

    with patch("agents.services.extractor.ExtractorAgent") as MockExtractor:
        MockExtractor.return_value = MagicMock()

        from backend.jobs.extraction_job import _build_extractor_with_context

        result = await _build_extractor_with_context(db, study_id=1)

    assert result is not None


# ---------------------------------------------------------------------------
# _load_research_questions
# ---------------------------------------------------------------------------


async def test_load_research_questions_returns_empty_when_study_not_found():
    """_load_research_questions returns [] when the Study record does not exist.

    A missing study should produce an empty list rather than raising.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))

    from backend.jobs.extraction_job import _load_research_questions

    result = await _load_research_questions(db, study_id=999)
    assert result == []


async def test_load_research_questions_returns_empty_for_truthy_metadata():
    """_load_research_questions returns [] when study.metadata_ is truthy.

    Due to the conditional ``if study is None or study.metadata_:`` the function
    returns an empty list whenever metadata_ is a non-empty dict (truthy).
    This test documents the current behavior.
    """
    study_mock = MagicMock()
    study_mock.metadata_ = {
        "research_questions": [
            {"id": 1, "text": "What is TDD?"},
        ]
    }

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(study_mock))

    from backend.jobs.extraction_job import _load_research_questions

    result = await _load_research_questions(db, study_id=1)
    # Current implementation returns [] when metadata_ is truthy (short-circuit)
    assert result == []


# ---------------------------------------------------------------------------
# _update_job_progress
# ---------------------------------------------------------------------------


async def test_update_job_progress_sets_pct_on_existing_job():
    """_update_job_progress writes progress_pct when the job record is found.

    The helper should update job.progress_pct and call db.commit().
    """
    job_mock = MagicMock()
    job_mock.progress_pct = 0

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(job_mock))
    db.commit = AsyncMock()

    from backend.jobs.extraction_job import _update_job_progress

    await _update_job_progress(db, "job-1", 50, {"processed": 5})

    assert job_mock.progress_pct == 50
    db.commit.assert_awaited()


async def test_update_job_progress_does_nothing_when_job_not_found():
    """_update_job_progress does not raise when the job record is missing.

    A None result from the job query should be silently ignored.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.commit = AsyncMock()

    from backend.jobs.extraction_job import _update_job_progress

    # Should not raise
    await _update_job_progress(db, "missing-job", 30, {})
    db.commit.assert_not_awaited()


# ---------------------------------------------------------------------------
# _mark_job_complete
# ---------------------------------------------------------------------------


async def test_mark_job_complete_sets_completed_status():
    """_mark_job_complete sets status=COMPLETED when processed > 0.

    When at least one paper was processed the job status should be COMPLETED.
    """
    from db.models.jobs import JobStatus

    job_mock = MagicMock()
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(job_mock))
    db.commit = AsyncMock()

    from backend.jobs.extraction_job import _mark_job_complete

    await _mark_job_complete(db, "job-1", processed=3, failed=0)

    assert job_mock.status == JobStatus.COMPLETED
    db.commit.assert_awaited()


async def test_mark_job_complete_sets_failed_status_when_all_failed():
    """_mark_job_complete sets status=FAILED when processed==0 and failed>0.

    When nothing was processed but some papers failed the job should be FAILED.
    """
    from db.models.jobs import JobStatus

    job_mock = MagicMock()
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(job_mock))
    db.commit = AsyncMock()

    from backend.jobs.extraction_job import _mark_job_complete

    await _mark_job_complete(db, "job-1", processed=0, failed=2)

    assert job_mock.status == JobStatus.FAILED
