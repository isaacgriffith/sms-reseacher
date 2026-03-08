"""Unit tests covering current behavior of search_job functions (TREF1).

These tests must pass both before and after TREF2/TREF3 decomposition.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_db_mock(scalar_returns: list):
    """Build an AsyncMock DB session that returns scalar_returns in order."""
    db = AsyncMock()
    results = []
    for val in scalar_returns:
        r = MagicMock()
        r.scalar_one_or_none.return_value = val
        r.scalars.return_value.first.return_value = val
        r.scalars.return_value.all.return_value = [] if val is None else [val]
        results.append(r)
    db.execute = AsyncMock(side_effect=results)
    return db


def _make_session_cm(db_mock):
    """Wrap db_mock in a context-manager mock for _session_maker()."""
    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=db_mock)
    cm.__aexit__ = AsyncMock(return_value=False)
    session_maker = MagicMock(return_value=cm)
    return session_maker


# ---------------------------------------------------------------------------
# run_full_search — error paths
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_full_search_returns_error_when_execution_not_found():
    """SearchExecution not found → error dict returned."""
    db = _make_db_mock([None])  # first execute returns None
    session_maker = _make_session_cm(db)

    with patch("backend.core.database._session_maker", session_maker):
        from backend.jobs.search_job import run_full_search

        result = await run_full_search({}, study_id=1, search_execution_id=999)

    assert result.get("error") == "search_execution not found"


@pytest.mark.asyncio
async def test_run_full_search_returns_error_when_search_string_missing():
    """Active SearchString not found → error dict returned."""
    # First execute: SearchExecution found
    exec_mock = MagicMock()
    exec_mock.status = "queued"
    exec_mock.databases_queried = []
    exec_mock.phase_tag = "initial-search"
    exec_mock.search_string_id = 1

    # Second execute: BackgroundJob lookup
    bg_result = MagicMock()
    bg_result.scalars.return_value.first.return_value = None

    # Third execute: SearchString → None
    ss_result = MagicMock()
    ss_result.scalar_one_or_none.return_value = None

    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            _r(exec_mock),  # SearchExecution found
            bg_result,       # BackgroundJob
            ss_result,       # SearchString not found
        ]
    )

    session_maker = _make_session_cm(db)
    with patch("backend.core.database._session_maker", session_maker):
        from backend.jobs.search_job import run_full_search

        result = await run_full_search({}, study_id=1, search_execution_id=1)

    assert result.get("error") == "search_string not found"


def _r(val):
    """Build a scalar result mock returning val."""
    r = MagicMock()
    r.scalar_one_or_none.return_value = val
    r.scalars.return_value.first.return_value = val
    r.scalars.return_value.all.return_value = [] if val is None else [val]
    return r


# ---------------------------------------------------------------------------
# run_snowball — error paths
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_snowball_returns_error_when_study_not_found():
    """Study not found → error dict returned."""
    db = _make_db_mock([None])
    session_maker = _make_session_cm(db)

    with patch("backend.core.database._session_maker", session_maker):
        from backend.jobs.search_job import run_snowball

        result = await run_snowball(
            {},
            study_id=999,
            phase_tag="backward-search-1",
            paper_dois=["10.1/test"],
            direction="backward",
            search_execution_id=1,
        )

    assert result.get("error") == "study not found"


@pytest.mark.asyncio
async def test_run_snowball_stopped_early_when_below_threshold():
    """Snowball with 0 new papers → stopped_early=True."""
    study_mock = MagicMock()
    study_mock.snowball_threshold = 5

    reviewer_mock = MagicMock()
    reviewer_mock.id = 7

    inc_result = MagicMock()
    inc_result.scalars.return_value.all.return_value = []

    exc_result = MagicMock()
    exc_result.scalars.return_value.all.return_value = []

    metrics_mock = MagicMock()
    metrics_mock.total_identified = 0
    metrics_mock.accepted = 0
    metrics_mock.rejected = 0
    metrics_mock.duplicates = 0

    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            _r(study_mock),     # Study
            _r(reviewer_mock),  # Reviewer
            inc_result,         # InclusionCriteria
            exc_result,         # ExclusionCriteria
            _r(metrics_mock),   # SearchMetrics
        ]
    )

    session_maker = _make_session_cm(db)
    with (
        patch("backend.core.database._session_maker", session_maker),
        patch("backend.core.config.get_settings") as mock_settings,
        patch("httpx.AsyncClient") as mock_client,
    ):
        settings = MagicMock()
        settings.researcher_mcp_url = "http://localhost:8002/sse"
        mock_settings.return_value = settings

        # httpx returns empty citations list
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"citations": []}
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=resp)

        from backend.jobs.search_job import run_snowball

        result = await run_snowball(
            {},
            study_id=1,
            phase_tag="forward-search-1",
            paper_dois=["10.1/test"],
            direction="forward",
            search_execution_id=1,
        )

    assert result["stopped_early"] is True
    assert result["new_non_duplicate_count"] == 0


# ---------------------------------------------------------------------------
# run_test_search — error path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_test_search_returns_error_when_search_string_not_found():
    db = _make_db_mock([None])
    session_maker = _make_session_cm(db)

    with patch("backend.core.database._session_maker", session_maker):
        from backend.jobs.search_job import run_test_search

        result = await run_test_search({}, study_id=1, search_string_id=999, databases=[])

    assert result.get("error") == "search_string not found"
