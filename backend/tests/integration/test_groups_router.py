"""Integration tests for the /api/v1/groups router.

Covers all group CRUD endpoints and member management including 401/403 error paths.
"""

import pytest

from backend.core.auth import create_access_token

BASE = "/api/v1/groups"


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for the given user_id.

    Args:
        user_id: The user to sign a token for.

    Returns:
        A dict suitable for use as ``headers=`` in an httpx request.
    """
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


class TestListGroups:
    """GET /groups — list current user's groups."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client):
        """No token → 401 Unauthorized."""
        resp = await client.get(BASE)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_memberships(self, client, alice):
        """User with no group memberships gets an empty list."""
        user, _ = alice
        resp = await client.get(BASE, headers=_bearer(user.id))
        assert resp.status_code == 200
        assert resp.json() == []


class TestCreateGroup:
    """POST /groups — create a new research group."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client):
        """No token → 401 Unauthorized."""
        resp = await client.post(BASE, json={"name": "Lab"})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_creates_group_and_returns_201(self, client, alice):
        """Authenticated user creates a group; becomes admin; 201 returned."""
        user, _ = alice
        resp = await client.post(BASE, json={"name": "Alpha Lab"}, headers=_bearer(user.id))
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Alpha Lab"
        assert "id" in body

    @pytest.mark.asyncio
    async def test_creator_appears_in_member_list(self, client, alice):
        """After creation, creator is listed as admin member."""
        user, _ = alice
        create_resp = await client.post(
            BASE, json={"name": "Beta Lab"}, headers=_bearer(user.id)
        )
        group_id = create_resp.json()["id"]

        members_resp = await client.get(
            f"{BASE}/{group_id}/members", headers=_bearer(user.id)
        )
        assert members_resp.status_code == 200
        members = members_resp.json()
        assert len(members) == 1
        assert members[0]["user_id"] == user.id
        assert members[0]["role"] == "admin"

    @pytest.mark.asyncio
    async def test_group_appears_in_list_after_creation(self, client, alice):
        """Newly created group shows up in GET /groups with study_count=0."""
        user, _ = alice
        await client.post(BASE, json={"name": "Gamma Lab"}, headers=_bearer(user.id))
        list_resp = await client.get(BASE, headers=_bearer(user.id))
        assert list_resp.status_code == 200
        groups = list_resp.json()
        assert len(groups) == 1
        assert groups[0]["name"] == "Gamma Lab"
        assert groups[0]["study_count"] == 0

    @pytest.mark.asyncio
    async def test_duplicate_name_returns_409(self, client, alice):
        """Creating a group with a name that already exists → 409 Conflict."""
        user, _ = alice
        headers = _bearer(user.id)
        await client.post(BASE, json={"name": "Unique Lab"}, headers=headers)
        resp2 = await client.post(BASE, json={"name": "Unique Lab"}, headers=headers)
        assert resp2.status_code == 409

    @pytest.mark.asyncio
    async def test_blank_name_returns_422(self, client, alice):
        """Blank (whitespace-only) name → 422 Unprocessable Entity."""
        user, _ = alice
        resp = await client.post(BASE, json={"name": "   "}, headers=_bearer(user.id))
        assert resp.status_code == 422


class TestListMembers:
    """GET /groups/{group_id}/members."""

    @pytest.mark.asyncio
    async def test_non_member_returns_404(self, client, alice, bob):
        """Non-member requesting member list for a group they don't belong to → 404."""
        alice_user, _ = alice
        bob_user, _ = bob

        # Alice creates a group; Bob is not a member
        create_resp = await client.post(
            BASE, json={"name": "Alice's Lab"}, headers=_bearer(alice_user.id)
        )
        group_id = create_resp.json()["id"]

        resp = await client.get(f"{BASE}/{group_id}/members", headers=_bearer(bob_user.id))
        assert resp.status_code == 404


class TestAddMember:
    """POST /groups/{group_id}/members — invite a user by email."""

    @pytest.mark.asyncio
    async def test_admin_can_invite_member(self, client, alice, bob):
        """Admin invites Bob; membership created with role 'member'."""
        alice_user, _ = alice
        bob_user, _ = bob

        create_resp = await client.post(
            BASE, json={"name": "Invite Lab"}, headers=_bearer(alice_user.id)
        )
        group_id = create_resp.json()["id"]

        invite_resp = await client.post(
            f"{BASE}/{group_id}/members",
            json={"email": bob_user.email, "role": "member"},
            headers=_bearer(alice_user.id),
        )
        assert invite_resp.status_code == 201
        body = invite_resp.json()
        assert body["user_id"] == bob_user.id
        assert body["role"] == "member"

    @pytest.mark.asyncio
    async def test_non_admin_cannot_invite_returns_403(self, client, alice, bob):
        """Non-admin member cannot invite others → 403 Forbidden."""
        alice_user, _ = alice
        bob_user, _ = bob

        # Alice creates group, invites Bob as member
        create_resp = await client.post(
            BASE, json={"name": "Perm Lab"}, headers=_bearer(alice_user.id)
        )
        group_id = create_resp.json()["id"]
        await client.post(
            f"{BASE}/{group_id}/members",
            json={"email": bob_user.email, "role": "member"},
            headers=_bearer(alice_user.id),
        )

        # Bob (member, not admin) tries to invite someone → 403
        resp = await client.post(
            f"{BASE}/{group_id}/members",
            json={"email": "newperson@example.com", "role": "member"},
            headers=_bearer(bob_user.id),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_invite_nonexistent_user_returns_404(self, client, alice):
        """Inviting an email with no matching User row → 404 Not Found."""
        user, _ = alice
        create_resp = await client.post(
            BASE, json={"name": "Ghost Lab"}, headers=_bearer(user.id)
        )
        group_id = create_resp.json()["id"]

        resp = await client.post(
            f"{BASE}/{group_id}/members",
            json={"email": "nobody@nowhere.com", "role": "member"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_invite_duplicate_member_returns_409(self, client, alice, bob):
        """Inviting a user who is already a member → 409 Conflict."""
        alice_user, _ = alice
        bob_user, _ = bob

        create_resp = await client.post(
            BASE, json={"name": "Dup Lab"}, headers=_bearer(alice_user.id)
        )
        group_id = create_resp.json()["id"]

        await client.post(
            f"{BASE}/{group_id}/members",
            json={"email": bob_user.email, "role": "member"},
            headers=_bearer(alice_user.id),
        )
        resp2 = await client.post(
            f"{BASE}/{group_id}/members",
            json={"email": bob_user.email, "role": "member"},
            headers=_bearer(alice_user.id),
        )
        assert resp2.status_code == 409


class TestRemoveMember:
    """DELETE /groups/{group_id}/members/{user_id}."""

    @pytest.mark.asyncio
    async def test_admin_can_remove_member(self, client, alice, bob):
        """Admin removes Bob; 204 No Content returned."""
        alice_user, _ = alice
        bob_user, _ = bob

        create_resp = await client.post(
            BASE, json={"name": "Remove Lab"}, headers=_bearer(alice_user.id)
        )
        group_id = create_resp.json()["id"]
        await client.post(
            f"{BASE}/{group_id}/members",
            json={"email": bob_user.email, "role": "member"},
            headers=_bearer(alice_user.id),
        )

        del_resp = await client.delete(
            f"{BASE}/{group_id}/members/{bob_user.id}",
            headers=_bearer(alice_user.id),
        )
        assert del_resp.status_code == 204

    @pytest.mark.asyncio
    async def test_remove_last_admin_returns_409(self, client, alice):
        """Removing the only admin → 409 Conflict."""
        user, _ = alice
        create_resp = await client.post(
            BASE, json={"name": "Solo Lab"}, headers=_bearer(user.id)
        )
        group_id = create_resp.json()["id"]

        resp = await client.delete(
            f"{BASE}/{group_id}/members/{user.id}",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_non_admin_cannot_remove_member_returns_403(self, client, alice, bob):
        """Non-admin trying to remove a member → 403 Forbidden."""
        alice_user, _ = alice
        bob_user, _ = bob

        create_resp = await client.post(
            BASE, json={"name": "NoPerm Lab"}, headers=_bearer(alice_user.id)
        )
        group_id = create_resp.json()["id"]
        await client.post(
            f"{BASE}/{group_id}/members",
            json={"email": bob_user.email, "role": "member"},
            headers=_bearer(alice_user.id),
        )

        # Bob (member) tries to remove Alice (admin) → 403
        resp = await client.delete(
            f"{BASE}/{group_id}/members/{alice_user.id}",
            headers=_bearer(bob_user.id),
        )
        assert resp.status_code == 403
