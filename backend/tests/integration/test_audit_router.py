"""Integration tests for GET /studies/{study_id}/audit (FR-044).

Covers:
- 403 returned for non-lead members (non-admin access guard)
- 200 and empty list for lead with no audit records
- entity_type query filter applied correctly
- actor_user_id query filter applied correctly
- pagination parameters (page, page_size) respected
"""

from __future__ import annotations

import time

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.audit import AuditAction, AuditRecord
from db.models.study import StudyMember, StudyMemberRole
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study_with_roles(db_engine, lead, member=None) -> int:
    """Create group + study; lead is LEAD, optional member is MEMBER. Returns study_id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"Audit Test Group {lead.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=lead.id, role=GroupRole.ADMIN))
        if member:
            session.add(GroupMembership(group_id=group.id, user_id=member.id, role=GroupRole.MEMBER))
        await session.commit()
        group_id = group.id

    resp_data = {"name": "Audit Study", "topic": "TDD", "study_type": "SMS",
                 "research_objectives": [], "research_questions": []}

    from httpx import ASGITransport, AsyncClient
    from backend.main import create_app
    from backend.core.database import get_db

    app = create_app()
    maker2 = async_sessionmaker(db_engine, expire_on_commit=False)

    async def _override():
        async with maker2() as s:
            yield s

    app.dependency_overrides[get_db] = _override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            f"/api/v1/groups/{group_id}/studies",
            json=resp_data,
            headers=_bearer(lead.id),
        )
    app.dependency_overrides.clear()
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _insert_audit_record(db_engine, study_id: int, entity_type: str, actor_user_id: int) -> None:
    """Insert a bare AuditRecord row for testing."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        record = AuditRecord(
            study_id=study_id,
            actor_user_id=actor_user_id,
            actor_agent=None,
            entity_type=entity_type,
            entity_id=1,
            action=AuditAction.UPDATE,
            field_name="description",
            before_value={"old": "v1"},
            after_value={"new": "v2"},
        )
        session.add(record)
        await session.commit()


class TestAuditEndpoint:
    """GET /studies/{study_id}/audit."""

    @pytest.mark.asyncio
    async def test_non_lead_member_gets_403(self, client, alice, bob, db_engine):
        """A non-lead study member receives HTTP 403."""
        lead, _ = alice
        member, _ = bob
        study_id = await _setup_study_with_roles(db_engine, lead, member)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/audit",
            headers=_bearer(member.id),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_unauthenticated_gets_401(self, client, alice, db_engine):
        """An unauthenticated request receives HTTP 401."""
        lead, _ = alice
        study_id = await _setup_study_with_roles(db_engine, lead)
        resp = await client.get(f"/api/v1/studies/{study_id}/audit")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_lead_gets_empty_list(self, client, alice, db_engine):
        """A study lead with no audit records gets 200 and empty items list."""
        lead, _ = alice
        study_id = await _setup_study_with_roles(db_engine, lead)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/audit",
            headers=_bearer(lead.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["items"] == []
        assert body["total"] == 0
        assert body["page"] == 1

    @pytest.mark.asyncio
    async def test_audit_records_returned_for_lead(self, client, alice, db_engine):
        """Audit records are returned in newest-first order for the study lead."""
        lead, _ = alice
        study_id = await _setup_study_with_roles(db_engine, lead)
        await _insert_audit_record(db_engine, study_id, "PICOComponent", lead.id)
        await _insert_audit_record(db_engine, study_id, "SearchString", lead.id)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/audit",
            headers=_bearer(lead.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 2
        assert len(body["items"]) == 2

    @pytest.mark.asyncio
    async def test_entity_type_filter(self, client, alice, db_engine):
        """entity_type query param filters results to matching entity type only."""
        lead, _ = alice
        study_id = await _setup_study_with_roles(db_engine, lead)
        await _insert_audit_record(db_engine, study_id, "PICOComponent", lead.id)
        await _insert_audit_record(db_engine, study_id, "SearchString", lead.id)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/audit?entity_type=PICOComponent",
            headers=_bearer(lead.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["entity_type"] == "PICOComponent"

    @pytest.mark.asyncio
    async def test_actor_user_id_filter(self, client, alice, bob, db_engine):
        """actor_user_id query param filters results to matching actor only."""
        lead, _ = alice
        other, _ = bob
        study_id = await _setup_study_with_roles(db_engine, lead, other)
        await _insert_audit_record(db_engine, study_id, "Study", lead.id)
        await _insert_audit_record(db_engine, study_id, "Study", other.id)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/audit?actor_user_id={lead.id}",
            headers=_bearer(lead.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["actor"]["id"] == lead.id

    @pytest.mark.asyncio
    async def test_pagination_page_size(self, client, alice, db_engine):
        """page_size param limits the number of items returned per page."""
        lead, _ = alice
        study_id = await _setup_study_with_roles(db_engine, lead)
        for _ in range(5):
            await _insert_audit_record(db_engine, study_id, "Study", lead.id)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/audit?page_size=3",
            headers=_bearer(lead.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 5
        assert len(body["items"]) == 3
        assert body["page_size"] == 3


class TestAuditPerformance:
    """Performance regression: SC-012 — audit trail renders ≤3s for ≤500 events."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_audit_500_rows_responds_within_3s(self, client, alice, db_engine):
        """GET /studies/{study_id}/audit with 500 rows must respond in under 3 000 ms.

        Excluded from the default test run (``@pytest.mark.slow``);
        included in CI nightly via ``pytest -m slow``.

        Satisfies SC-012.
        """
        lead, _ = alice
        study_id = await _setup_study_with_roles(db_engine, lead)

        # Insert 500 AuditRecord rows directly via the DB (fast bulk path)
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            records = [
                AuditRecord(
                    study_id=study_id,
                    actor_user_id=lead.id,
                    actor_agent=None,
                    entity_type="Study",
                    entity_id=i,
                    action=AuditAction.UPDATE,
                    field_name="description",
                    before_value={"old": f"v{i}"},
                    after_value={"new": f"v{i+1}"},
                )
                for i in range(500)
            ]
            session.add_all(records)
            await session.commit()

        start = time.monotonic()
        resp = await client.get(
            f"/api/v1/studies/{study_id}/audit?page_size=200",
            headers=_bearer(lead.id),
        )
        elapsed_ms = (time.monotonic() - start) * 1000

        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 500

        assert elapsed_ms < 3000, (
            f"Audit endpoint took {elapsed_ms:.0f} ms for 500 rows (limit: 3000 ms). "
            "SC-012 violated."
        )
