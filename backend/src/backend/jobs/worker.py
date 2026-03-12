"""ARQ worker entrypoint.

Start with::

    python -m backend.jobs.worker

or via Docker Compose ``worker`` service.
"""

from arq import run_worker
from arq.connections import RedisSettings

from backend.core.config import get_settings


def main() -> None:
    """Start the ARQ worker process."""
    settings = get_settings()
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    run_worker(WorkerSettings, redis_settings=redis_settings)


class WorkerSettings:
    """ARQ worker configuration.

    Job functions are registered here as they are implemented.
    Import each job module so ARQ can discover the decorated functions.
    """

    from backend.jobs.search_job import run_full_search, run_snowball, run_test_search

    functions = [run_test_search, run_full_search, run_snowball]

    max_jobs: int = 10
    job_timeout: int = 3600

    @classmethod
    def get_redis_settings(cls) -> RedisSettings:
        """Return Redis settings from application config."""
        return RedisSettings.from_dsn(get_settings().redis_url)


if __name__ == "__main__":
    main()
