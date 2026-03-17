"""Unit tests for backend.jobs.worker.

Covers WorkerSettings class attributes and get_redis_settings method,
and verifies that all required job functions are registered.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch


def test_worker_settings_has_functions_list():
    """WorkerSettings.functions is a non-empty list of job callables.

    All expected ARQ job functions should be registered in the functions list.
    """
    from backend.jobs.worker import WorkerSettings

    assert isinstance(WorkerSettings.functions, list)
    assert len(WorkerSettings.functions) > 0


def test_worker_settings_has_max_jobs():
    """WorkerSettings.max_jobs is a positive integer.

    The max_jobs attribute should be set to a reasonable non-zero value.
    """
    from backend.jobs.worker import WorkerSettings

    assert isinstance(WorkerSettings.max_jobs, int)
    assert WorkerSettings.max_jobs > 0


def test_worker_settings_has_job_timeout():
    """WorkerSettings.job_timeout is a positive integer.

    The job_timeout attribute should be set to a positive number of seconds.
    """
    from backend.jobs.worker import WorkerSettings

    assert isinstance(WorkerSettings.job_timeout, int)
    assert WorkerSettings.job_timeout > 0


def test_worker_settings_functions_include_run_full_search():
    """WorkerSettings.functions includes run_full_search.

    The full search job function should be registered for ARQ to discover.
    """
    from backend.jobs.search_job import run_full_search
    from backend.jobs.worker import WorkerSettings

    assert run_full_search in WorkerSettings.functions


def test_worker_settings_functions_include_run_batch_extraction():
    """WorkerSettings.functions includes run_batch_extraction.

    The batch extraction job should be registered for ARQ to discover.
    """
    from backend.jobs.extraction_job import run_batch_extraction
    from backend.jobs.worker import WorkerSettings

    assert run_batch_extraction in WorkerSettings.functions


def test_worker_settings_functions_include_run_quality_eval():
    """WorkerSettings.functions includes run_quality_eval.

    The quality evaluation job should be registered for ARQ to discover.
    """
    from backend.jobs.quality_job import run_quality_eval
    from backend.jobs.worker import WorkerSettings

    assert run_quality_eval in WorkerSettings.functions


def test_worker_settings_functions_include_run_validity_prefill():
    """WorkerSettings.functions includes run_validity_prefill.

    The validity prefill job should be registered for ARQ to discover.
    """
    from backend.jobs.validity_job import run_validity_prefill
    from backend.jobs.worker import WorkerSettings

    assert run_validity_prefill in WorkerSettings.functions


def test_worker_settings_get_redis_settings_returns_redis_settings():
    """WorkerSettings.get_redis_settings returns a RedisSettings instance.

    The class method should use the application settings to build RedisSettings.
    """
    from arq.connections import RedisSettings

    from backend.jobs.worker import WorkerSettings

    result = WorkerSettings.get_redis_settings()
    assert isinstance(result, RedisSettings)


def test_main_calls_run_worker():
    """main() calls arq.run_worker with WorkerSettings.

    The entry-point function should invoke the ARQ run_worker with the
    correct settings class.
    """
    with patch("backend.jobs.worker.run_worker") as mock_run_worker:
        from backend.jobs.worker import main

        main()

    mock_run_worker.assert_called_once()
