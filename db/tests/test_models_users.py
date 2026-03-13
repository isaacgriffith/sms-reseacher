"""Unit tests for db.models.users — User, ResearchGroup, GroupMembership."""

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
from db.models.users import GroupMembership, GroupRole, ResearchGroup, User


# ---------------------------------------------------------------------------
# Test database fixture
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def session():
    """Yield an in-memory SQLite session with all users tables created."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Only create the tables defined in this module's models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    await engine.dispose()


# ---------------------------------------------------------------------------
# GroupRole enum
# ---------------------------------------------------------------------------


class TestGroupRoleEnum:
    """GroupRole enum values and string coercion."""

    def test_admin_value(self) -> None:
        """GroupRole.ADMIN has string value 'admin'."""
        assert GroupRole.ADMIN.value == "admin"

    def test_member_value(self) -> None:
        """GroupRole.MEMBER has string value 'member'."""
        assert GroupRole.MEMBER.value == "member"

    @pytest.mark.parametrize("role", list(GroupRole))
    def test_all_enum_values_are_strings(self, role: GroupRole) -> None:
        """All GroupRole values are str subclasses."""
        assert isinstance(role, str)

    def test_invalid_value_raises(self) -> None:
        """Constructing GroupRole with an unknown value raises ValueError."""
        with pytest.raises(ValueError):
            GroupRole("superuser")


# ---------------------------------------------------------------------------
# ResearchGroup
# ---------------------------------------------------------------------------


class TestResearchGroupModel:
    """In-memory attribute tests for ResearchGroup."""

    def test_instantiates_with_name(self) -> None:
        """ResearchGroup can be created with a name."""
        group = ResearchGroup(name="AI Safety Lab")
        assert group.name == "AI Safety Lab"

    def test_repr_contains_name(self) -> None:
        """__repr__ includes the group name."""
        group = ResearchGroup(name="Repr Lab")
        assert "Repr Lab" in repr(group)

    @pytest.mark.asyncio
    async def test_persists_and_gets_id(self, session) -> None:
        """Persisted ResearchGroup receives an auto-incremented id."""
        group = ResearchGroup(name="Persist Lab")
        session.add(group)
        await session.commit()
        assert group.id is not None
        assert group.id > 0

    @pytest.mark.asyncio
    async def test_created_at_is_set_on_persist(self, session) -> None:
        """created_at timestamp is populated after commit (server default)."""
        group = ResearchGroup(name="Timestamp Lab")
        session.add(group)
        await session.commit()
        # SQLite server_default for func.now() may return None at Python level
        # but the column is not nullable, so it must be set after refresh.
        await session.refresh(group)
        assert group.created_at is not None

    @pytest.mark.asyncio
    async def test_name_uniqueness_constraint(self, session) -> None:
        """Two ResearchGroups with the same name violate the UNIQUE constraint."""
        session.add(ResearchGroup(name="Duplicate"))
        await session.commit()
        session.add(ResearchGroup(name="Duplicate"))
        with pytest.raises(IntegrityError):
            await session.commit()


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


class TestUserModel:
    """Attribute and persistence tests for User."""

    def test_instantiates_with_required_fields(self) -> None:
        """User can be created with email, hashed_password, and display_name."""
        user = User(email="a@b.com", hashed_password="hash", display_name="A")
        assert user.email == "a@b.com"
        assert user.display_name == "A"

    def test_last_login_at_defaults_to_none(self) -> None:
        """last_login_at is None before any login."""
        user = User(email="x@y.com", hashed_password="h", display_name="X")
        assert user.last_login_at is None

    def test_repr_contains_email(self) -> None:
        """__repr__ includes the email address."""
        user = User(email="repr@test.com", hashed_password="h", display_name="R")
        assert "repr@test.com" in repr(user)

    @pytest.mark.asyncio
    async def test_persists_and_gets_id(self, session) -> None:
        """Persisted User receives an auto-incremented id."""
        user = User(email="persist@test.com", hashed_password="h", display_name="P")
        session.add(user)
        await session.commit()
        assert user.id is not None
        assert user.id > 0

    @pytest.mark.asyncio
    async def test_email_uniqueness_constraint(self, session) -> None:
        """Two Users with the same email violate the UNIQUE constraint."""
        session.add(User(email="dup@test.com", hashed_password="h", display_name="D1"))
        await session.commit()
        session.add(User(email="dup@test.com", hashed_password="h", display_name="D2"))
        with pytest.raises(IntegrityError):
            await session.commit()

    @pytest.mark.asyncio
    async def test_created_at_is_set_on_persist(self, session) -> None:
        """created_at is populated after commit."""
        user = User(email="ts@test.com", hashed_password="h", display_name="TS")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        assert user.created_at is not None


# ---------------------------------------------------------------------------
# GroupMembership
# ---------------------------------------------------------------------------


class TestGroupMembershipModel:
    """Tests for GroupMembership join table."""

    def test_instantiates_with_required_fields(self) -> None:
        """GroupMembership can be created with group_id, user_id, role."""
        gm = GroupMembership(group_id=1, user_id=2, role=GroupRole.ADMIN)
        assert gm.group_id == 1
        assert gm.user_id == 2
        assert gm.role == GroupRole.ADMIN

    @pytest.mark.asyncio
    async def test_default_role_is_member_after_persist(self, session) -> None:
        """Default role is MEMBER after the row is flushed to the database."""
        group = ResearchGroup(name="Default Role Lab")
        user = User(email="drole@test.com", hashed_password="h", display_name="DR")
        session.add_all([group, user])
        await session.flush()

        gm = GroupMembership(group_id=group.id, user_id=user.id)
        session.add(gm)
        await session.flush()
        assert gm.role == GroupRole.MEMBER

    def test_repr_contains_group_and_user(self) -> None:
        """__repr__ contains group_id and user_id."""
        gm = GroupMembership(group_id=5, user_id=7, role=GroupRole.MEMBER)
        r = repr(gm)
        assert "5" in r
        assert "7" in r

    @pytest.mark.asyncio
    async def test_persists_with_fk_rows(self, session) -> None:
        """GroupMembership persists when referenced group and user exist."""
        group = ResearchGroup(name="FK Lab")
        user = User(email="fk@test.com", hashed_password="h", display_name="FK")
        session.add_all([group, user])
        await session.flush()  # populate group.id and user.id

        gm = GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN)
        session.add(gm)
        await session.commit()
        assert gm.group_id == group.id
        assert gm.user_id == user.id

    @pytest.mark.asyncio
    async def test_unique_constraint_group_user_pair(self, session) -> None:
        """Inserting two memberships for the same (group_id, user_id) raises IntegrityError."""
        group = ResearchGroup(name="Uniq Lab")
        user = User(email="uniq@test.com", hashed_password="h", display_name="U")
        session.add_all([group, user])
        await session.flush()

        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.MEMBER))
        await session.flush()

        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        with pytest.raises(IntegrityError):
            await session.commit()
