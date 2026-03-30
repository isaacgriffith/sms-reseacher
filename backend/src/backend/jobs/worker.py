"""ARQ worker entrypoint.

Start with::

    python -m backend.jobs.worker

or via Docker Compose ``worker`` service.
"""

from arq import run_worker
from arq.connections import RedisSettings
from arq.typing import WorkerSettingsBase

from backend.core.config import get_settings
from backend.jobs.evidence_briefing_job import run_generate_evidence_briefing
from backend.jobs.extraction_job import run_batch_extraction
from backend.jobs.narrative_synthesis_job import run_narrative_draft
from backend.jobs.protocol_review_job import run_protocol_review
from backend.jobs.quality_job import run_quality_eval
from backend.jobs.results_job import run_export, run_generate_results
from backend.jobs.search_job import (
    run_expert_seed_suggestion,
    run_full_search,
    run_snowball,
    run_test_search,
)
from backend.jobs.synthesis_job import run_synthesis
from backend.jobs.validity_job import run_validity_prefill


def main() -> None:
    """Start the ARQ worker process."""
    settings = get_settings()
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    run_worker(WorkerSettings, redis_settings=redis_settings)


class WorkerSettings(WorkerSettingsBase):
    """ARQ worker configuration.

    Job functions are registered here as they are implemented.
    All job modules are imported at module level so ARQ can discover them.
    """

    functions = [
        run_test_search,
        run_full_search,
        run_snowball,
        run_expert_seed_suggestion,
        run_batch_extraction,
        run_generate_results,
        run_export,
        run_quality_eval,
        run_validity_prefill,
        run_protocol_review,
        run_synthesis,
        # Feature 008: Rapid Review workflow jobs
        run_narrative_draft,
        run_generate_evidence_briefing,
    ]

    max_jobs: int = 10
    job_timeout: int = 3600

    @classmethod
    def get_redis_settings(cls) -> RedisSettings:
        """Return Redis settings from application config."""
        return RedisSettings.from_dsn(get_settings().redis_url)


if __name__ == "__main__":
    main()
