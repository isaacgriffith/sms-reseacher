"""Integration tests for POST /api/v1/studies/{study_id}/snowball.

Closes G22: ``run_snowball`` was a complete, registered ARQ job that nothing
could start. It appeared in ``WorkerSettings.functions`` and nowhere else — no
endpoint enqueued it, no service called it, no control reached it — so
backward and forward snowballing had never run for a user.

Covers the seed sources, the in-flight guard FR-026 requires, and the rows the
job needs to exist before it starts.
"""

from __future__ import annotations

import pytest
from db.models import Paper
from db.models.candidate import CandidatePaper, CandidatePaperStatus
from db.models.jobs import BackgroundJob, JobStatus, JobType
from db.models.search import SearchString
from db.models.search_exec import SearchExecution
from db.models.users import GroupMembership, GroupRole, ResearchGroup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create a group + membership + study; return the study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Snowball Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Snowball Study",
            "topic": "TDD",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _add_search_string(db_engine, study_id: int) -> int:
    """Insert an active SearchString and return its id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        ss = SearchString(
            study_id=study_id, version=1, string_text="TDD AND testing", is_active=True
        )
        session.add(ss)
        await session.commit()
        return ss.id


async def _add_accepted_candidate(
    db_engine, study_id: int, search_string_id: int, doi: str
) -> None:
    """Insert an accepted CandidatePaper whose Paper carries *doi*."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        execution = SearchExecution(
            study_id=study_id,
            search_string_id=search_string_id,
            phase_tag="initial-search",
        )
        paper = Paper(title=f"Paper {doi}", doi=doi)
        session.add_all([execution, paper])
        await session.flush()
        session.add(
            CandidatePaper(
                study_id=study_id,
                paper=paper,
                search_execution_id=execution.id,
                phase_tag="initial-search",
                current_status=CandidatePaperStatus.ACCEPTED,
            )
        )
        await session.commit()


async def _add_job(db_engine, study_id: int, job_type: JobType, job_status: JobStatus) -> None:
    """Insert a BackgroundJob for *study_id*."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        session.add(
            BackgroundJob(
                id=f"job-{job_type.value}-{job_status.value}",
                study_id=study_id,
                job_type=job_type,
                status=job_status,
            )
        )
        await session.commit()


class TestStartSnowball:
    """POST /studies/{study_id}/snowball — enqueue the snowball job."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token → 401."""
        resp = await client.post("/api/v1/studies/1/snowball", json={"direction": "backward"})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_non_member_returns_403(self, client, alice, bob, db_engine) -> None:
        """A user outside the study cannot start a snowball run.

        Snowballing spends provider calls against another group's study, so the
        guard is the same one the full search uses rather than a weaker check.
        """
        user, _ = alice
        other, _ = bob
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/snowball",
            json={"direction": "backward"},
            headers=_bearer(other.id),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_no_search_string_returns_422(self, client, alice, db_engine) -> None:
        """No search string → 422.

        Every SearchExecution requires one, so the run cannot be recorded
        without it even though snowballing does not query with it.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/snowball",
            json={"direction": "backward", "paper_dois": ["10.1/seed"]},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_no_seed_dois_returns_422(self, client, alice, db_engine) -> None:
        """Nothing to snowball from → 422, rather than an empty run.

        A run over zero seeds would complete instantly and report zero new
        papers, which reads exactly like a search that found nothing.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/snowball",
            json={"direction": "backward"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422
        assert "seed" in str(resp.json()["detail"]).lower()

    @pytest.mark.asyncio
    async def test_explicit_dois_return_202(self, client, alice, db_engine) -> None:
        """Caller-supplied seeds → 202 with the ids the UI needs to poll."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/snowball",
            json={"direction": "backward", "paper_dois": ["10.1/seed"]},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 202
        body = resp.json()
        assert isinstance(body["job_id"], str)
        assert isinstance(body["search_execution_id"], int)
        assert body["seed_count"] == 1

    @pytest.mark.asyncio
    async def test_seeds_default_to_the_studys_accepted_papers(
        self, client, alice, db_engine
    ) -> None:
        """Omitting the seeds snowballs from what the study has accepted.

        That is what snowballing means in a mapping study — walk citations from
        the papers that survived screening — and it is the only default a
        reviewer could not get wrong.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        ss_id = await _add_search_string(db_engine, study_id)
        await _add_accepted_candidate(db_engine, study_id, ss_id, "10.1/accepted-a")
        await _add_accepted_candidate(db_engine, study_id, ss_id, "10.1/accepted-b")

        resp = await client.post(
            f"/api/v1/studies/{study_id}/snowball",
            json={"direction": "forward"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 202
        assert resp.json()["seed_count"] == 2

    @pytest.mark.asyncio
    async def test_creates_the_rows_the_job_expects(self, client, alice, db_engine) -> None:
        """A SearchExecution and a SNOWBALL_SEARCH job exist before the job runs.

        ``run_snowball`` looks both up by study and type; without them it runs
        with no way to report progress or failure.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/snowball",
            json={"direction": "backward", "paper_dois": ["10.1/seed"]},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 202

        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            execution = (
                (
                    await session.execute(
                        select(SearchExecution).where(SearchExecution.study_id == study_id)
                    )
                )
                .scalars()
                .one()
            )
            job = (
                (
                    await session.execute(
                        select(BackgroundJob).where(BackgroundJob.id == resp.json()["job_id"])
                    )
                )
                .scalars()
                .one()
            )

        assert execution.phase_tag == "backward-search"
        assert job.job_type is JobType.SNOWBALL_SEARCH
        assert job.status is JobStatus.QUEUED

    @pytest.mark.asyncio
    async def test_phase_tag_follows_the_direction(self, client, alice, db_engine) -> None:
        """A forward run is tagged forward, so the two are distinguishable.

        ``phase_tag`` is what separates candidates by how they were found; one
        tag for both directions would merge them in the PRISMA funnel.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)

        await client.post(
            f"/api/v1/studies/{study_id}/snowball",
            json={"direction": "forward", "paper_dois": ["10.1/seed"]},
            headers=_bearer(user.id),
        )

        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            execution = (
                (
                    await session.execute(
                        select(SearchExecution).where(SearchExecution.study_id == study_id)
                    )
                )
                .scalars()
                .one()
            )
        assert execution.phase_tag == "forward-search"

    @pytest.mark.asyncio
    async def test_rejects_an_unknown_direction(self, client, alice, db_engine) -> None:
        """Only backward and forward exist; anything else is refused at the boundary."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/snowball",
            json={"direction": "sideways", "paper_dois": ["10.1/seed"]},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422


class TestSnowballInFlightGuard:
    """FR-026 — refuse a second automated pass over the same papers."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("blocking_type", [JobType.FULL_SEARCH, JobType.SNOWBALL_SEARCH])
    @pytest.mark.parametrize("blocking_status", [JobStatus.QUEUED, JobStatus.RUNNING])
    async def test_refuses_while_another_pass_is_in_flight(
        self, client, alice, db_engine, blocking_type, blocking_status
    ) -> None:
        """409 while any non-terminal automated pass is running for the study.

        Snowballing screens every candidate it finds, so two passes would
        interleave over the same papers and each would see a moving target.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)
        await _add_job(db_engine, study_id, blocking_type, blocking_status)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/snowball",
            json={"direction": "backward", "paper_dois": ["10.1/seed"]},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_names_the_run_that_blocked_it(self, client, alice, db_engine) -> None:
        """The 409 payload identifies the blocking run.

        The UI has to say which run is in the way; without the id and type it
        can only report that something is, which is not actionable.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)
        await _add_job(db_engine, study_id, JobType.FULL_SEARCH, JobStatus.RUNNING)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/snowball",
            json={"direction": "backward", "paper_dois": ["10.1/seed"]},
            headers=_bearer(user.id),
        )
        detail = resp.json()["detail"]
        assert detail["blocking_job_type"] == "full_search"
        assert detail["blocking_job_id"] == "job-full_search-running"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("terminal_status", [JobStatus.COMPLETED, JobStatus.FAILED])
    async def test_ignores_finished_runs(self, client, alice, db_engine, terminal_status) -> None:
        """A finished run does not block a new one.

        Terminal states must be ignored, or the first search a study ever runs
        would block every snowball afterwards.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)
        await _add_job(db_engine, study_id, JobType.FULL_SEARCH, terminal_status)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/snowball",
            json={"direction": "backward", "paper_dois": ["10.1/seed"]},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 202
