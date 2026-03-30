"""Integration tests for Rapid Review Evidence Briefing routes (feature 008).

Covers:
- GET  /rapid/studies/{id}/briefings             → 200 empty list, 200 with records
- POST /rapid/studies/{id}/briefings             → 422 when synthesis incomplete
- GET  /rapid/studies/{id}/briefings/{bid}       → 200, 404
- POST /rapid/studies/{id}/briefings/{bid}/publish → 200 PUBLISHED
- GET  /rapid/studies/{id}/briefings/{bid}/export → 404 when no pdf/html
- POST /rapid/studies/{id}/briefings/{bid}/share-token → 201, 422 when unpublished
- DELETE /rapid/studies/{id}/briefings/share-token/{token} → 204, 404
- GET  /public/briefings/{token}                 → 200 with published briefing
- GET  /public/briefings/{token}/export          → 404 when no pdf
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return a Bearer token header for the given user id.

    Args:
        user_id: The numeric user ID to embed in the JWT.

    Returns:
        A dict with the ``Authorization`` header value.
    """
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_rr_study(client, db_engine, user) -> int:
    """Create a research group and RAPID study, return study id.

    Args:
        client: The httpx AsyncClient pointed at the test FastAPI app.
        db_engine: The in-memory async SQLite engine.
        user: The test user who owns the study.

    Returns:
        The newly created study ID.
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"RR Briefing Group {user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "RR Briefing Test Study",
            "topic": "Rapid Review",
            "study_type": "Rapid",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _insert_briefing(
    db_engine,
    *,
    study_id: int,
    version_number: int = 1,
    status: str = "draft",
    html_path: str | None = None,
    pdf_path: str | None = None,
) -> int:
    """Insert an EvidenceBriefing directly into the test database.

    Args:
        db_engine: The in-memory async SQLite engine.
        study_id: Study to associate the briefing with.
        version_number: Briefing version number.
        status: Status string (``"draft"`` or ``"published"``).
        html_path: Optional path to the HTML file.
        pdf_path: Optional path to the PDF file.

    Returns:
        The new briefing's primary key.
    """
    from db.models.rapid_review import BriefingStatus, EvidenceBriefing

    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        briefing = EvidenceBriefing(
            study_id=study_id,
            version_number=version_number,
            status=BriefingStatus(status),
            title=f"Evidence Briefing v{version_number}",
            summary="Test summary",
            findings={"0": "Finding text"},
            target_audience="Test audience",
            generated_at=datetime.now(UTC),
            html_path=html_path,
            pdf_path=pdf_path,
        )
        session.add(briefing)
        await session.commit()
        await session.refresh(briefing)
        return briefing.id


async def _insert_share_token(
    db_engine,
    *,
    briefing_id: int,
    study_id: int,
    user_id: int,
    token: str = "test-token-abc",
    revoked: bool = False,
) -> str:
    """Insert an EvidenceBriefingShareToken directly into the test database.

    Args:
        db_engine: The in-memory async SQLite engine.
        briefing_id: Associated briefing ID.
        study_id: Study ID (denormalised).
        user_id: User who created the token.
        token: The raw token string.
        revoked: Whether to set revoked_at.

    Returns:
        The token string.
    """
    from db.models.rapid_review import EvidenceBriefingShareToken

    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        token_record = EvidenceBriefingShareToken(
            briefing_id=briefing_id,
            study_id=study_id,
            created_by_user_id=user_id,
            token=token,
            revoked_at=datetime.now(UTC) if revoked else None,
        )
        session.add(token_record)
        await session.commit()
    return token


# ---------------------------------------------------------------------------
# GET /rapid/studies/{id}/briefings
# ---------------------------------------------------------------------------


class TestListBriefings:
    """GET /rapid/studies/{id}/briefings returns briefing summaries."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_initially(self, client, db_engine, alice) -> None:
        """Returns 200 with empty list when no briefings exist for the study."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)

        resp = await client.get(
            f"/api/v1/rapid/studies/{study_id}/briefings",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_returns_briefing_list(self, client, db_engine, alice) -> None:
        """Returns 200 with the briefing summaries when records exist."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        await _insert_briefing(db_engine, study_id=study_id, version_number=1)
        await _insert_briefing(db_engine, study_id=study_id, version_number=2)

        resp = await client.get(
            f"/api/v1/rapid/studies/{study_id}/briefings",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_returns_401_without_auth(self, client, db_engine, alice) -> None:
        """Returns 401 when no Authorization header is provided."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)

        resp = await client.get(f"/api/v1/rapid/studies/{study_id}/briefings")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /rapid/studies/{id}/briefings
# ---------------------------------------------------------------------------


class TestCreateBriefing:
    """POST /rapid/studies/{id}/briefings enqueues generation."""

    @pytest.mark.asyncio
    async def test_returns_422_when_synthesis_incomplete(
        self, client, db_engine, alice
    ) -> None:
        """Returns 422 when no synthesis sections are complete."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)

        # No synthesis sections → synthesis is not complete
        resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/briefings",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_202_when_synthesis_complete(
        self, client, db_engine, alice
    ) -> None:
        """Returns 202 with job_id when synthesis is complete."""
        from backend.services.narrative_synthesis_service import is_synthesis_complete

        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)

        mock_arq_pool = AsyncMock()
        mock_arq_pool.enqueue_job = AsyncMock()
        mock_arq_pool.close = AsyncMock()

        with (
            patch(
                "backend.api.v1.rapid.briefing.narrative_synthesis_service.is_synthesis_complete",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "backend.api.v1.rapid.briefing.evidence_briefing_service.create_new_version",
                new=AsyncMock(
                    return_value=type(
                        "B",
                        (),
                        {"id": 1, "version_number": 1},
                    )()
                ),
            ),
            patch(
                "backend.api.v1.rapid.briefing.arq.connections.create_pool",
                new=AsyncMock(return_value=mock_arq_pool),
            ),
        ):
            resp = await client.post(
                f"/api/v1/rapid/studies/{study_id}/briefings",
                headers=_bearer(user.id),
            )

        assert resp.status_code == 202
        data = resp.json()
        assert "job_id" in data
        assert data["status"] == "queued"


# ---------------------------------------------------------------------------
# GET /rapid/studies/{id}/briefings/{bid}
# ---------------------------------------------------------------------------


class TestGetBriefing:
    """GET /rapid/studies/{id}/briefings/{bid} returns a specific briefing."""

    @pytest.mark.asyncio
    async def test_returns_200_with_briefing(self, client, db_engine, alice) -> None:
        """Returns 200 with full briefing details."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(db_engine, study_id=study_id)

        resp = await client.get(
            f"/api/v1/rapid/studies/{study_id}/briefings/{bid}",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == bid
        assert data["study_id"] == study_id

    @pytest.mark.asyncio
    async def test_returns_404_for_wrong_study(self, client, db_engine, alice) -> None:
        """Returns 404 when the briefing belongs to a different study."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(db_engine, study_id=study_id)

        # Different study_id in path
        resp = await client.get(
            f"/api/v1/rapid/studies/9999/briefings/{bid}",
            headers=_bearer(user.id),
        )
        assert resp.status_code in (403, 404)

    @pytest.mark.asyncio
    async def test_returns_404_for_missing_briefing(self, client, db_engine, alice) -> None:
        """Returns 404 when the briefing ID does not exist."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)

        resp = await client.get(
            f"/api/v1/rapid/studies/{study_id}/briefings/9999",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /rapid/studies/{id}/briefings/{bid}/publish
# ---------------------------------------------------------------------------


class TestPublishBriefing:
    """POST /rapid/studies/{id}/briefings/{bid}/publish promotes to PUBLISHED."""

    @pytest.mark.asyncio
    async def test_returns_200_with_published_status(
        self, client, db_engine, alice
    ) -> None:
        """Returns 200 with status='published' after promoting the briefing."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(db_engine, study_id=study_id, status="draft")

        resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/briefings/{bid}/publish",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "published"

    @pytest.mark.asyncio
    async def test_returns_404_for_missing_briefing(
        self, client, db_engine, alice
    ) -> None:
        """Returns 404 when trying to publish a non-existent briefing."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)

        resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/briefings/9999/publish",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /rapid/studies/{id}/briefings/{bid}/export
# ---------------------------------------------------------------------------


class TestExportBriefing:
    """GET /rapid/studies/{id}/briefings/{bid}/export downloads the file."""

    @pytest.mark.asyncio
    async def test_returns_404_when_pdf_not_generated(
        self, client, db_engine, alice
    ) -> None:
        """Returns 404 when requesting PDF export but pdf_path is not set."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(db_engine, study_id=study_id, pdf_path=None)

        resp = await client.get(
            f"/api/v1/rapid/studies/{study_id}/briefings/{bid}/export?format=pdf",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_404_when_html_not_generated(
        self, client, db_engine, alice
    ) -> None:
        """Returns 404 when requesting HTML export but html_path is not set."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(db_engine, study_id=study_id, html_path=None)

        resp = await client.get(
            f"/api/v1/rapid/studies/{study_id}/briefings/{bid}/export?format=html",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /rapid/studies/{id}/briefings/{bid}/share-token
# ---------------------------------------------------------------------------


class TestCreateShareToken:
    """POST /rapid/studies/{id}/briefings/{bid}/share-token creates a token."""

    @pytest.mark.asyncio
    async def test_returns_422_when_no_published_briefing(
        self, client, db_engine, alice
    ) -> None:
        """Returns 422 when the briefing exists but no published version exists."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(db_engine, study_id=study_id, status="draft")

        resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/briefings/{bid}/share-token",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_201_with_token(self, client, db_engine, alice) -> None:
        """Returns 201 with token details when a published briefing exists."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(db_engine, study_id=study_id, status="published")

        resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/briefings/{bid}/share-token",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "token" in data
        assert len(data["token"]) > 0
        assert "share_url" in data

    @pytest.mark.asyncio
    async def test_returns_404_for_nonexistent_briefing(
        self, client, db_engine, alice
    ) -> None:
        """Returns 404 when the briefing_id does not exist."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)

        resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/briefings/9999/share-token",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /rapid/studies/{id}/briefings/share-token/{token}
# ---------------------------------------------------------------------------


class TestRevokeShareToken:
    """DELETE /rapid/studies/{id}/briefings/share-token/{token} revokes a token."""

    @pytest.mark.asyncio
    async def test_returns_204_on_revoke(self, client, db_engine, alice) -> None:
        """Returns 204 when revoking a valid share token."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(db_engine, study_id=study_id, status="published")
        token = await _insert_share_token(
            db_engine, briefing_id=bid, study_id=study_id, user_id=user.id,
            token="rev-token-xyz-001",
        )

        resp = await client.delete(
            f"/api/v1/rapid/studies/{study_id}/briefings/share-token/{token}",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_returns_404_for_missing_token(self, client, db_engine, alice) -> None:
        """Returns 404 when the token string does not exist."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)

        resp = await client.delete(
            f"/api/v1/rapid/studies/{study_id}/briefings/share-token/nonexistent",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /public/briefings/{token}
# ---------------------------------------------------------------------------


class TestGetPublicBriefing:
    """GET /public/briefings/{token} serves published briefings without auth."""

    @pytest.mark.asyncio
    async def test_returns_200_for_valid_token(self, client, db_engine, alice) -> None:
        """Returns 200 with briefing content for a valid, active share token."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(db_engine, study_id=study_id, status="published")
        token = await _insert_share_token(
            db_engine, briefing_id=bid, study_id=study_id, user_id=user.id,
            token="pub-token-valid-001",
        )

        resp = await client.get(f"/api/v1/public/briefings/{token}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["study_id"] == study_id
        assert data["status"] == "published"
        assert "threats" in data

    @pytest.mark.asyncio
    async def test_returns_404_for_revoked_token(self, client, db_engine, alice) -> None:
        """Returns 404 when the share token has been revoked."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(db_engine, study_id=study_id, status="published")
        token = await _insert_share_token(
            db_engine, briefing_id=bid, study_id=study_id, user_id=user.id,
            token="pub-token-revoked-001", revoked=True,
        )

        resp = await client.get(f"/api/v1/public/briefings/{token}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_404_for_unknown_token(self, client, db_engine, alice) -> None:
        """Returns 404 for a token string that does not exist in the database."""
        resp = await client.get("/api/v1/public/briefings/this-token-does-not-exist")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_no_auth_required(self, client, db_engine, alice) -> None:
        """The public endpoint does not require an Authorization header."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(db_engine, study_id=study_id, status="published")
        token = await _insert_share_token(
            db_engine, briefing_id=bid, study_id=study_id, user_id=user.id,
            token="pub-noauth-token-001",
        )

        # No Authorization header
        resp = await client.get(f"/api/v1/public/briefings/{token}")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /public/briefings/{token}/export
# ---------------------------------------------------------------------------


class TestExportPublicBriefing:
    """GET /public/briefings/{token}/export downloads file without auth."""

    @pytest.mark.asyncio
    async def test_returns_404_when_pdf_not_generated(
        self, client, db_engine, alice
    ) -> None:
        """Returns 404 when the published briefing has no PDF path."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(
            db_engine, study_id=study_id, status="published", pdf_path=None
        )
        token = await _insert_share_token(
            db_engine, briefing_id=bid, study_id=study_id, user_id=user.id,
            token="export-pdf-token-001",
        )

        resp = await client.get(
            f"/api/v1/public/briefings/{token}/export?format=pdf"
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_404_when_html_not_generated(
        self, client, db_engine, alice
    ) -> None:
        """Returns 404 when the published briefing has no HTML path."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user)
        bid = await _insert_briefing(
            db_engine, study_id=study_id, status="published", html_path=None
        )
        token = await _insert_share_token(
            db_engine, briefing_id=bid, study_id=study_id, user_id=user.id,
            token="export-html-token-001",
        )

        resp = await client.get(
            f"/api/v1/public/briefings/{token}/export?format=html"
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_404_for_invalid_token(self, client) -> None:
        """Returns 404 for an export request with an unknown token."""
        resp = await client.get(
            "/api/v1/public/briefings/nonexistent-token/export?format=pdf"
        )
        assert resp.status_code == 404
