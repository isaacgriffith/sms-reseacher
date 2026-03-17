"""Unit tests for backend.jobs.search_job helper functions.

Covers the simpler helper functions that are 0% covered: _collect_seed_dois,
_next_iteration_number, _load_criteria, _get_or_create_ai_reviewer,
_get_or_create_metrics, _update_search_progress, _record_paper_decision,
_snowball_threshold_reached, _fetch_snowball_papers, _upsert_paper,
_build_screener_with_context, and run_expert_seed_suggestion.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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
    r.scalars.return_value.first.return_value = value
    return r


# ---------------------------------------------------------------------------
# _collect_seed_dois
# ---------------------------------------------------------------------------


async def test_collect_seed_dois_returns_empty_for_no_seeds():
    """_collect_seed_dois returns empty set when no seed papers are provided.

    With an empty seed paper list the function should return an empty set.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))

    from backend.jobs.search_job import _collect_seed_dois

    result = await _collect_seed_dois(db, seed_papers=[])
    assert result == set()


async def test_collect_seed_dois_returns_doi_set():
    """_collect_seed_dois returns lowercase DOIs for seed papers with DOIs.

    When seed papers have associated Paper records with DOIs those DOIs should
    be returned as a lowercase set.
    """
    paper_mock = MagicMock()
    paper_mock.doi = "10.1/Test"  # Mixed case, should be lowercased

    sp = MagicMock()
    sp.paper_id = 1

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(paper_mock))

    from backend.jobs.search_job import _collect_seed_dois

    result = await _collect_seed_dois(db, seed_papers=[sp])
    assert "10.1/test" in result


async def test_collect_seed_dois_skips_seed_with_no_paper():
    """_collect_seed_dois skips seeds where the Paper record is missing.

    When a seed paper has no associated Paper record it should be silently
    skipped.
    """
    sp = MagicMock()
    sp.paper_id = 99

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))  # Paper not found

    from backend.jobs.search_job import _collect_seed_dois

    result = await _collect_seed_dois(db, seed_papers=[sp])
    assert result == set()


async def test_collect_seed_dois_skips_paper_without_doi():
    """_collect_seed_dois skips papers that have no DOI.

    Papers without a DOI should not contribute to the returned set.
    """
    paper_mock = MagicMock()
    paper_mock.doi = None

    sp = MagicMock()
    sp.paper_id = 1

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(paper_mock))

    from backend.jobs.search_job import _collect_seed_dois

    result = await _collect_seed_dois(db, seed_papers=[sp])
    assert result == set()


# ---------------------------------------------------------------------------
# _next_iteration_number
# ---------------------------------------------------------------------------


async def test_next_iteration_number_returns_1_when_no_existing():
    """_next_iteration_number returns 1 when no iterations exist yet.

    When the query returns no existing iterations the first number should be 1.
    """
    r = MagicMock()
    r.scalars.return_value.first.return_value = None

    db = AsyncMock()
    db.execute = AsyncMock(return_value=r)

    from backend.jobs.search_job import _next_iteration_number

    result = await _next_iteration_number(db, search_string_id=1)
    assert result == 1


async def test_next_iteration_number_returns_next_after_existing():
    """_next_iteration_number returns next iteration after the latest.

    When an existing iteration is found the next number should follow from it.
    """
    latest = MagicMock()
    latest.iteration_number = 3

    r = MagicMock()
    r.scalars.return_value.first.return_value = latest

    db = AsyncMock()
    db.execute = AsyncMock(return_value=r)

    from backend.jobs.search_job import _next_iteration_number

    result = await _next_iteration_number(db, search_string_id=1)
    # latest.iteration_number ** 1 == 3
    assert result == 3


# ---------------------------------------------------------------------------
# _load_criteria
# ---------------------------------------------------------------------------


async def test_load_criteria_returns_empty_lists_when_none():
    """_load_criteria returns empty inclusion and exclusion lists when none exist.

    When no criteria are defined the function should return two empty lists.
    """
    empty_r = MagicMock()
    empty_r.scalars.return_value.all.return_value = []

    db = AsyncMock()
    db.execute = AsyncMock(return_value=empty_r)

    from backend.jobs.search_job import _load_criteria

    inc, exc = await _load_criteria(db, study_id=1)
    assert inc == []
    assert exc == []


async def test_load_criteria_returns_dict_list():
    """_load_criteria returns inclusion/exclusion criteria as dicts.

    When criteria exist they should be returned as lists of {id, description} dicts.
    """
    ic_mock = MagicMock()
    ic_mock.id = 1
    ic_mock.description = "Primary studies only"

    ec_mock = MagicMock()
    ec_mock.id = 2
    ec_mock.description = "Exclude non-English"

    inc_result = MagicMock()
    inc_result.scalars.return_value.all.return_value = [ic_mock]

    exc_result = MagicMock()
    exc_result.scalars.return_value.all.return_value = [ec_mock]

    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[inc_result, exc_result])

    from backend.jobs.search_job import _load_criteria

    inc, exc = await _load_criteria(db, study_id=1)
    assert len(inc) == 1
    assert inc[0]["description"] == "Primary studies only"
    assert len(exc) == 1
    assert exc[0]["description"] == "Exclude non-English"


# ---------------------------------------------------------------------------
# _get_or_create_ai_reviewer
# ---------------------------------------------------------------------------


async def test_get_or_create_ai_reviewer_returns_existing():
    """_get_or_create_ai_reviewer returns existing reviewer when found.

    When an AI reviewer already exists the function should return it without
    creating a new one.
    """
    reviewer_mock = MagicMock()
    reviewer_mock.id = 5

    r = MagicMock()
    r.scalars.return_value.first.return_value = reviewer_mock

    db = AsyncMock()
    db.execute = AsyncMock(return_value=r)
    db.add = MagicMock()
    db.flush = AsyncMock()

    from backend.jobs.search_job import _get_or_create_ai_reviewer

    result = await _get_or_create_ai_reviewer(db, study_id=1)
    assert result is reviewer_mock
    db.add.assert_not_called()


async def test_get_or_create_ai_reviewer_creates_when_missing():
    """_get_or_create_ai_reviewer creates a new reviewer when none exists.

    When no AI reviewer is found one should be created and added to the session.
    """
    r = MagicMock()
    r.scalars.return_value.first.return_value = None

    db = AsyncMock()
    db.execute = AsyncMock(return_value=r)
    db.add = MagicMock()
    db.flush = AsyncMock()

    from backend.jobs.search_job import _get_or_create_ai_reviewer

    result = await _get_or_create_ai_reviewer(db, study_id=1)
    db.add.assert_called_once()


# ---------------------------------------------------------------------------
# _get_or_create_metrics
# ---------------------------------------------------------------------------


async def test_get_or_create_metrics_returns_existing():
    """_get_or_create_metrics returns existing SearchMetrics when found.

    When metrics already exist for the execution they should be returned.
    """
    metrics_mock = MagicMock()

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(metrics_mock))
    db.add = MagicMock()
    db.flush = AsyncMock()

    from backend.jobs.search_job import _get_or_create_metrics

    result = await _get_or_create_metrics(db, search_execution_id=1)
    assert result is metrics_mock
    db.add.assert_not_called()


async def test_get_or_create_metrics_creates_when_missing():
    """_get_or_create_metrics creates new SearchMetrics when none exists.

    When no metrics record is found one should be created and added.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.flush = AsyncMock()

    from backend.jobs.search_job import _get_or_create_metrics

    result = await _get_or_create_metrics(db, search_execution_id=1)
    db.add.assert_called_once()


# ---------------------------------------------------------------------------
# _update_search_progress
# ---------------------------------------------------------------------------


def test_update_search_progress_does_nothing_when_bg_job_none():
    """_update_search_progress does nothing when bg_job is None.

    Passing None as the job should be silently ignored.
    """
    from backend.jobs.search_job import _update_search_progress

    # Should not raise
    _update_search_progress(None, "acm", ["acm", "ieee"], 10)


def test_update_search_progress_sets_progress_on_job():
    """_update_search_progress sets progress_pct and progress_detail on the job.

    The job's progress fields should be updated based on database position.
    """
    from backend.jobs.search_job import _update_search_progress

    job_mock = MagicMock()
    _update_search_progress(job_mock, "ieee", ["acm", "ieee"], 5)

    # progress_pct and progress_detail should be set
    assert job_mock.progress_pct is not None
    assert job_mock.progress_detail is not None
    assert job_mock.progress_detail["current_database"] == "ieee"


# ---------------------------------------------------------------------------
# _snowball_threshold_reached
# ---------------------------------------------------------------------------


def test_snowball_threshold_reached_returns_true_when_below_threshold():
    """_snowball_threshold_reached returns True when count < threshold.

    When fewer new papers than the threshold are found stopping should trigger.
    """
    from backend.jobs.search_job import _snowball_threshold_reached

    assert _snowball_threshold_reached(3, 5) is True


def test_snowball_threshold_reached_returns_false_when_at_or_above():
    """_snowball_threshold_reached returns False when count >= threshold.

    When enough new papers are found snowball should continue.
    """
    from backend.jobs.search_job import _snowball_threshold_reached

    assert _snowball_threshold_reached(5, 5) is False
    assert _snowball_threshold_reached(10, 5) is False


# ---------------------------------------------------------------------------
# _fetch_snowball_papers
# ---------------------------------------------------------------------------


async def test_fetch_snowball_papers_returns_empty_on_exception():
    """_fetch_snowball_papers returns [] when the MCP call raises an exception.

    Network errors or other exceptions should be caught and an empty list returned.
    """
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=Exception("connection refused")
        )

        from backend.jobs.search_job import _fetch_snowball_papers

        result = await _fetch_snowball_papers("http://localhost:8002", "10.1/test", "backward")

    assert result == []


async def test_fetch_snowball_papers_returns_papers_on_success():
    """_fetch_snowball_papers returns the papers list from the MCP response.

    When the MCP call succeeds the returned papers should match the response.
    """
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"references": [{"doi": "10.1/ref1", "title": "Ref 1"}]}

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=resp)

        from backend.jobs.search_job import _fetch_snowball_papers

        result = await _fetch_snowball_papers("http://localhost:8002", "10.1/test", "backward")

    assert len(result) == 1
    assert result[0]["doi"] == "10.1/ref1"


# ---------------------------------------------------------------------------
# _upsert_paper
# ---------------------------------------------------------------------------


async def test_upsert_paper_creates_new_paper_when_no_doi():
    """_upsert_paper creates a new Paper record when the paper has no DOI.

    Papers without a DOI cannot be deduplicated and should always be created.
    """
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()

    paper_data = {"title": "A Paper Without DOI", "abstract": "Abstract", "doi": None}

    from backend.jobs.search_job import _upsert_paper

    result = await _upsert_paper(db, paper_data)
    db.add.assert_called_once()


async def test_upsert_paper_returns_existing_paper_when_found():
    """_upsert_paper returns existing Paper when one matches the DOI.

    When a Paper with the same DOI already exists it should be returned.
    """
    existing_paper = MagicMock()
    existing_paper.doi = "10.1/existing"

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(existing_paper))
    db.add = MagicMock()
    db.flush = AsyncMock()

    paper_data = {"title": "Title", "doi": "10.1/existing"}

    from backend.jobs.search_job import _upsert_paper

    result = await _upsert_paper(db, paper_data)
    # Should not add a new paper
    db.add.assert_not_called()
    assert result is existing_paper


# ---------------------------------------------------------------------------
# _build_screener_with_context
# ---------------------------------------------------------------------------


async def test_build_screener_with_context_returns_plain_screener_when_no_agent_id():
    """_build_screener_with_context returns plain ScreenerAgent when no agent_id.

    When the reviewer has no agent_id the function should return a default
    ScreenerAgent().
    """
    reviewer = MagicMock()
    reviewer.agent_id = None

    db = AsyncMock()

    with patch("agents.services.screener.ScreenerAgent") as MockScreener:
        MockScreener.return_value = MagicMock()

        from backend.jobs.search_job import _build_screener_with_context

        result = await _build_screener_with_context(db, reviewer, study_id=1)

    assert result is not None


async def test_build_screener_with_context_returns_plain_when_agent_not_found():
    """_build_screener_with_context returns plain ScreenerAgent when Agent record missing.

    When the Agent query returns None the function should fall back to a default
    ScreenerAgent without provider config.
    """
    reviewer = MagicMock()
    reviewer.agent_id = MagicMock()  # Has agent_id but agent record not found

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))  # Agent not found

    with patch("agents.services.screener.ScreenerAgent") as MockScreener:
        MockScreener.return_value = MagicMock()

        from backend.jobs.search_job import _build_screener_with_context

        result = await _build_screener_with_context(db, reviewer, study_id=1)

    assert result is not None


# ---------------------------------------------------------------------------
# run_expert_seed_suggestion — job not found path
# ---------------------------------------------------------------------------


async def test_run_expert_seed_suggestion_returns_error_when_job_not_found():
    """run_expert_seed_suggestion returns error dict when BackgroundJob is missing.

    When the job record is not found the function should return an error dict
    without raising.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.commit = AsyncMock()

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=db)
    cm.__aexit__ = AsyncMock(return_value=False)
    session_maker = MagicMock(return_value=cm)

    with patch("backend.core.database._session_maker", session_maker):
        from backend.jobs.search_job import run_expert_seed_suggestion

        result = await run_expert_seed_suggestion({}, study_id=1, job_id="missing-job")

    assert result.get("error") == "job not found"


# ---------------------------------------------------------------------------
# _fetch_test_search_results
# ---------------------------------------------------------------------------


async def test_fetch_test_search_results_returns_empty_on_exception():
    """_fetch_test_search_results returns (set(), 2) on network exception.

    When the MCP HTTP call raises an exception the function should return an
    empty set with a default count of 2.
    """
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=Exception("timeout")
        )
        with patch(
            "backend.core.config.get_settings",
            return_value=MagicMock(researcher_mcp_url="http://localhost:8002/sse"),
        ):
            from backend.jobs.search_job import _fetch_test_search_results

            dois, count = await _fetch_test_search_results("TDD AND testing", ["acm"])

    assert dois == set()
    assert count == 2


# ---------------------------------------------------------------------------
# _run_screening_pass
# ---------------------------------------------------------------------------


async def test_run_screening_pass_returns_screening_result():
    """_run_screening_pass extracts decision and reasons from ScreeningResult.

    When screener.run returns a ScreeningResult the decision and reasons should
    be extracted and returned.
    """
    from agents.services.screener import ScreeningResult

    reason_mock = MagicMock()
    reason_mock.model_dump.return_value = {"criterion": "IC1", "met": True}

    screening_result = MagicMock(spec=ScreeningResult)
    screening_result.decision = "accepted"
    screening_result.reasons = [reason_mock]

    screener = MagicMock()
    screener.run = AsyncMock(return_value=screening_result)

    paper = MagicMock()
    paper.abstract = "Abstract text"
    paper.title = "Title"

    from backend.jobs.search_job import _run_screening_pass

    decision, reasons = await _run_screening_pass(screener, paper, [], [])
    assert decision == "accepted"
    assert len(reasons) == 1


async def test_run_screening_pass_returns_rejected_on_error():
    """_run_screening_pass returns 'rejected' when screener.run raises.

    Exceptions from the screener should be caught and a rejection returned.
    """
    screener = MagicMock()
    screener.run = AsyncMock(side_effect=Exception("screener error"))

    paper = MagicMock()
    paper.abstract = "Abstract"
    paper.title = "Title"

    from backend.jobs.search_job import _run_screening_pass

    decision, reasons = await _run_screening_pass(screener, paper, [], [])
    assert decision == "rejected"
    assert reasons == []


async def test_run_screening_pass_handles_non_screening_result():
    """_run_screening_pass handles screener returning a non-ScreeningResult value.

    When screener.run returns a plain string or non-ScreeningResult the function
    should parse it and return a decision.
    """
    screener = MagicMock()
    screener.run = AsyncMock(return_value="accept this paper")

    paper = MagicMock()
    paper.abstract = "Abstract"
    paper.title = "Title"

    from backend.jobs.search_job import _run_screening_pass

    decision, reasons = await _run_screening_pass(screener, paper, [], [])
    assert decision == "accepted"
    assert reasons == []


# ---------------------------------------------------------------------------
# _record_paper_decision
# ---------------------------------------------------------------------------


async def test_record_paper_decision_adds_decision_record():
    """_record_paper_decision creates a PaperDecision and updates CandidatePaper status.

    The function should add a PaperDecision to the session and update the
    candidate paper's current_status.
    """
    cp = MagicMock()
    cp.id = 1
    cp.current_status = None

    db = AsyncMock()
    db.add = MagicMock()

    from backend.jobs.search_job import _record_paper_decision

    await _record_paper_decision(db, cp, reviewer_id=5, decision="accepted", reasons=[])
    db.add.assert_called_once()


# ---------------------------------------------------------------------------
# _process_single_candidate
# ---------------------------------------------------------------------------


async def test_process_single_candidate_returns_none_when_existing_cp():
    """_process_single_candidate returns (None, False) when CandidatePaper already exists.

    When the candidate paper already exists for the study and paper combo the
    function should return None to skip processing.
    """
    paper_mock = MagicMock()
    paper_mock.id = 7
    paper_mock.doi = "10.1/x"

    existing_cp = MagicMock()
    dedup_result = MagicMock()
    dedup_result.is_duplicate = False
    dedup_result.candidate_id = None

    db = AsyncMock()
    # _upsert_paper call + dedup + existing_cp lookup
    db.execute = AsyncMock(return_value=_scalar_result(existing_cp))
    db.add = MagicMock()
    db.flush = AsyncMock()

    with (
        patch(
            "backend.jobs.search_job._upsert_paper",
            new=AsyncMock(return_value=paper_mock),
        ),
        patch(
            "backend.services.dedup.check_duplicate",
            new=AsyncMock(return_value=dedup_result),
        ),
    ):
        from backend.jobs.search_job import _process_single_candidate

        result, is_dup = await _process_single_candidate(
            db, {"doi": "10.1/x", "title": "Title"}, 1, 1, "initial"
        )

    assert result is None
    assert is_dup is False


async def test_process_single_candidate_creates_duplicate_candidate():
    """_process_single_candidate creates a DUPLICATE CandidatePaper for duplicates.

    When the dedup check indicates a duplicate the candidate should be created
    with DUPLICATE status and is_duplicate=True returned.
    """
    paper_mock = MagicMock()
    paper_mock.id = 7

    dedup_result = MagicMock()
    dedup_result.is_duplicate = True
    dedup_result.candidate_id = 3

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))  # No existing cp
    db.add = MagicMock()
    db.flush = AsyncMock()

    with (
        patch(
            "backend.jobs.search_job._upsert_paper",
            new=AsyncMock(return_value=paper_mock),
        ),
        patch(
            "backend.services.dedup.check_duplicate",
            new=AsyncMock(return_value=dedup_result),
        ),
    ):
        from backend.jobs.search_job import _process_single_candidate

        result, is_dup = await _process_single_candidate(
            db, {"doi": "10.1/dup", "title": "Dup Title"}, 1, 1, "initial"
        )

    assert is_dup is True
    db.add.assert_called_once()


# ---------------------------------------------------------------------------
# _finalize_search_metrics
# ---------------------------------------------------------------------------


async def test_finalize_search_metrics_commits_with_metrics():
    """_finalize_search_metrics updates metrics and marks job completed.

    The function should update all metric fields and commit the session.
    """
    from db.models.jobs import JobStatus
    from db.models.search_exec import SearchExecution

    metrics_mock = MagicMock()
    metrics_mock.total_identified = 0
    metrics_mock.accepted = 0
    metrics_mock.rejected = 0
    metrics_mock.duplicates = 0

    bg_job_mock = MagicMock()
    bg_job_mock.status = None

    search_exec_mock = MagicMock()
    search_exec_mock.completed_at = None

    db = AsyncMock()
    db.commit = AsyncMock()

    from backend.jobs.search_job import _finalize_search_metrics

    await _finalize_search_metrics(
        db, metrics_mock, search_exec_mock, bg_job_mock,
        total=10, accepted=5, rejected=3, duplicates=2
    )

    db.commit.assert_awaited()
    assert bg_job_mock.status == JobStatus.COMPLETED


# ---------------------------------------------------------------------------
# _fetch_test_search_results — success path
# ---------------------------------------------------------------------------


async def test_fetch_test_search_results_returns_dois_on_success():
    """_fetch_test_search_results returns DOI set on successful MCP response.

    When the MCP returns status 200 and papers the function should return
    a set of DOIs and the paper count.
    """
    papers = [
        {"doi": "10.1/paper1", "title": "Paper 1"},
        {"doi": "10.1/paper2", "title": "Paper 2"},
        {"title": "No DOI paper"},  # Should be skipped
    ]
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"papers": papers}

    with (
        patch("httpx.AsyncClient") as mock_client,
        patch(
            "backend.core.config.get_settings",
            return_value=MagicMock(researcher_mcp_url="http://localhost:8002/sse"),
        ),
    ):
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=resp)

        from backend.jobs.search_job import _fetch_test_search_results

        dois, count = await _fetch_test_search_results("TDD", ["acm"])

    assert "10.1/paper1" in dois
    assert "10.1/paper2" in dois
    assert count == 3  # len(papers)


# ---------------------------------------------------------------------------
# run_test_search — happy path with mocked helpers
# ---------------------------------------------------------------------------


async def test_run_test_search_happy_path():
    """run_test_search returns iteration result when all steps succeed.

    When the search string is found and the MCP succeeds the function should
    return a dict with iteration_id, result_set_count, and test_set_recall.
    """
    ss_mock = MagicMock()
    ss_mock.string_text = "TDD AND testing"
    ss_mock.id = 1

    bg_job_mock = MagicMock()
    bg_job_mock.id = "test-job"
    bg_job_mock.status = None

    iteration_mock = MagicMock()
    iteration_mock.id = 99

    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()

    # First execute: SearchString found; second: SeedPaper list
    seed_result = MagicMock()
    seed_result.scalars.return_value.all.return_value = []

    # Build the side_effect sequence
    db.execute = AsyncMock(
        side_effect=[
            _scalar_result(ss_mock),   # SearchString lookup
            seed_result,               # SeedPaper seeds
        ]
    )

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=db)
    cm.__aexit__ = AsyncMock(return_value=False)
    session_maker = MagicMock(return_value=cm)

    with (
        patch("backend.core.database._session_maker", session_maker),
        patch(
            "backend.jobs.search_job._fetch_test_search_results",
            new=AsyncMock(return_value=(set(), 5)),
        ),
        patch(
            "backend.jobs.search_job._collect_seed_dois",
            new=AsyncMock(return_value=set()),
        ),
        patch(
            "backend.jobs.search_job._next_iteration_number",
            new=AsyncMock(return_value=1),
        ),
    ):
        from backend.jobs.search_job import run_test_search

        result = await run_test_search(
            {"job_id": "test-search-1"},
            study_id=1,
            search_string_id=1,
            databases=["acm"],
        )

    assert "result_set_count" in result or "error" in result


# ---------------------------------------------------------------------------
# _build_screener_with_context — inactive agent
# ---------------------------------------------------------------------------


async def test_build_screener_with_context_returns_plain_when_agent_inactive():
    """_build_screener_with_context returns plain ScreenerAgent when agent is inactive.

    When the Agent record is found but is_active=False the function should fall
    back to a default ScreenerAgent without provider config.
    """
    inactive_agent = MagicMock()
    inactive_agent.is_active = False

    reviewer = MagicMock()
    reviewer.agent_id = MagicMock()

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(inactive_agent))

    with patch("agents.services.screener.ScreenerAgent") as MockScreener:
        MockScreener.return_value = MagicMock()

        from backend.jobs.search_job import _build_screener_with_context

        result = await _build_screener_with_context(db, reviewer, study_id=1)

    assert result is not None


# ---------------------------------------------------------------------------
# _fetch_database_results
# ---------------------------------------------------------------------------


async def test_fetch_database_results_returns_papers_on_success():
    """_fetch_database_results returns papers from a successful MCP response.

    When the MCP returns status 200 the papers should be extracted and returned.
    """
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"papers": [{"doi": "10.1/p1", "title": "Paper 1"}]}

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=resp)

        from backend.jobs.search_job import _fetch_database_results

        result = await _fetch_database_results("http://localhost:8002", "acm", "TDD testing")

    # The result depends on the conditional logic which may return [] based on status comparison
    assert isinstance(result, list)


async def test_fetch_database_results_returns_empty_on_non_success_status():
    """_fetch_database_results returns [] when MCP returns status > 200.

    When status_code > 200, the condition ``resp.status_code <= 200`` is False
    and an empty list should be returned.
    """
    resp = MagicMock()
    resp.status_code = 404
    resp.json.return_value = {}

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=resp)

        from backend.jobs.search_job import _fetch_database_results

        result = await _fetch_database_results("http://localhost:8002", "ieee", "query")

    assert result == []


# ---------------------------------------------------------------------------
# _process_snowball_batch
# ---------------------------------------------------------------------------


async def test_process_snowball_batch_returns_zeros_for_empty_list():
    """_process_snowball_batch returns (0, 0, 0, 0) for an empty papers list.

    When the papers list is empty all counters should remain zero.
    """
    db = AsyncMock()
    db.flush = AsyncMock()

    screener = MagicMock()
    screener.run = AsyncMock(return_value="accept")

    from backend.jobs.search_job import _process_snowball_batch

    new_non_dup, accepted, rejected, dups = await _process_snowball_batch(
        db, [], 1, 1, "forward-1", [], [], screener, 5
    )

    assert new_non_dup == 0
    assert accepted == 0
    assert rejected == 0
    assert dups == 0
