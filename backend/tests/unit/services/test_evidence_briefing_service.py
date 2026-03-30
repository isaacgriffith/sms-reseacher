"""Unit tests for backend.services.evidence_briefing_service (feature 008).

Covers:
- get_briefings_for_study: returns empty list, returns list ordered newest first
- create_new_version: version 1 on first call, increments on subsequent calls,
  populates title from study name, populates findings from narrative sections
- publish_version: marks briefing as published, demotes previous published to draft,
  raises 404 if briefing not found
- generate_html: renders template to file, stores html_path, raises 404 if not found
- generate_pdf: calls weasyprint, stores pdf_path, raises 404 if not found,
  raises 422 if html_path not set
- create_share_token: creates token with correct fields, raises 422 if no published
  briefing, raises 404 if briefing not found, token is 43 chars
- revoke_token: sets revoked_at, raises 404 if token not found
- resolve_token: returns published briefing for valid token, raises 404 for revoked,
  raises 404 for expired, raises 404 if no published briefing
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException


def _make_briefing(
    *,
    briefing_id: int = 1,
    study_id: int = 10,
    version_number: int = 1,
    status_val: str = "draft",
    html_path: str | None = None,
    pdf_path: str | None = None,
) -> MagicMock:
    """Build a minimal EvidenceBriefing mock.

    Args:
        briefing_id: Primary key.
        study_id: Owning study ID.
        version_number: Version number.
        status_val: Status value string.
        html_path: Path to rendered HTML file, or None.
        pdf_path: Path to rendered PDF file, or None.

    Returns:
        A :class:`~unittest.mock.MagicMock` standing in for an
        :class:`~db.models.rapid_review.EvidenceBriefing` instance.
    """
    from db.models.rapid_review import BriefingStatus

    b = MagicMock()
    b.id = briefing_id
    b.study_id = study_id
    b.version_number = version_number
    b.status = BriefingStatus(status_val)
    b.html_path = html_path
    b.pdf_path = pdf_path
    return b


def _make_session(execute_side_effects: list) -> AsyncMock:
    """Build a minimal async session mock with the given execute return values.

    Args:
        execute_side_effects: List of return values for successive
            ``session.execute()`` calls.

    Returns:
        A configured :class:`~unittest.mock.AsyncMock` session.
    """
    session = AsyncMock()
    session.execute.side_effect = execute_side_effects
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    return session


# ---------------------------------------------------------------------------
# get_briefings_for_study
# ---------------------------------------------------------------------------


class TestGetBriefingsForStudy:
    """get_briefings_for_study returns empty list or ordered list."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_none_exist(self) -> None:
        """Returns an empty list when no briefings exist for the study."""
        from backend.services.evidence_briefing_service import get_briefings_for_study

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        session = _make_session([result_mock])

        out = await get_briefings_for_study(study_id=1, db=session)

        assert out == []

    @pytest.mark.asyncio
    async def test_returns_list_of_briefings(self) -> None:
        """Returns the list of briefings (mocked as returned by the DB)."""
        from backend.services.evidence_briefing_service import get_briefings_for_study

        b1 = _make_briefing(version_number=2)
        b2 = _make_briefing(version_number=1)

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [b1, b2]
        session = _make_session([result_mock])

        out = await get_briefings_for_study(study_id=1, db=session)

        assert len(out) == 2
        assert out[0].version_number == 2


# ---------------------------------------------------------------------------
# create_new_version
# ---------------------------------------------------------------------------


class TestCreateNewVersion:
    """create_new_version creates a briefing and auto-populates fields."""

    @pytest.mark.asyncio
    async def test_creates_version_1_on_first_call(self) -> None:
        """When no versions exist yet, the new briefing has version_number=1."""
        from backend.services.evidence_briefing_service import create_new_version

        # max_version query → None
        max_ver_result = MagicMock()
        max_ver_result.scalar_one_or_none.return_value = None

        # study query
        mock_study = MagicMock()
        mock_study.name = "My Study"
        study_result = MagicMock()
        study_result.scalar_one_or_none.return_value = mock_study

        session = AsyncMock()
        session.execute.side_effect = [max_ver_result, study_result]
        session.add = MagicMock()  # sync mock so side_effect captures work
        session.commit = AsyncMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()

        mock_protocol = MagicMock()
        mock_protocol.practical_problem = "practitioners"
        mock_protocol.research_questions = []

        mock_section = MagicMock()
        mock_section.is_complete = True
        mock_section.narrative_text = "Finding text"
        mock_section.rq_index = 0

        captured = []
        session.add.side_effect = lambda obj: captured.append(obj)

        with (
            patch(
                "backend.services.evidence_briefing_service.rr_protocol_service.get_or_create_protocol",
                new=AsyncMock(return_value=mock_protocol),
            ),
            patch(
                "backend.services.evidence_briefing_service.narrative_synthesis_service.get_or_create_sections",
                new=AsyncMock(return_value=[mock_section]),
            ),
        ):
            await create_new_version(study_id=1, db=session)

        assert len(captured) == 1
        briefing_obj = captured[0]
        assert briefing_obj.version_number == 1

    @pytest.mark.asyncio
    async def test_increments_version_number(self) -> None:
        """When max_version=2 exists, the new briefing is version 3."""
        from backend.services.evidence_briefing_service import create_new_version

        max_ver_result = MagicMock()
        max_ver_result.scalar_one_or_none.return_value = 2

        mock_study = MagicMock()
        mock_study.name = "Study"
        study_result = MagicMock()
        study_result.scalar_one_or_none.return_value = mock_study

        session = AsyncMock()
        session.execute.side_effect = [max_ver_result, study_result]
        session.add = MagicMock()  # sync mock so side_effect captures work
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        mock_protocol = MagicMock()
        mock_protocol.practical_problem = None
        mock_protocol.research_questions = []

        captured = []
        session.add.side_effect = lambda obj: captured.append(obj)

        with (
            patch(
                "backend.services.evidence_briefing_service.rr_protocol_service.get_or_create_protocol",
                new=AsyncMock(return_value=mock_protocol),
            ),
            patch(
                "backend.services.evidence_briefing_service.narrative_synthesis_service.get_or_create_sections",
                new=AsyncMock(return_value=[]),
            ),
        ):
            await create_new_version(study_id=1, db=session)

        assert captured[0].version_number == 3

    @pytest.mark.asyncio
    async def test_populates_title_from_study_name(self) -> None:
        """The briefing title includes the study name."""
        from backend.services.evidence_briefing_service import create_new_version

        max_ver_result = MagicMock()
        max_ver_result.scalar_one_or_none.return_value = None

        mock_study = MagicMock()
        mock_study.name = "Protocol Study XYZ"
        study_result = MagicMock()
        study_result.scalar_one_or_none.return_value = mock_study

        session = AsyncMock()
        session.execute.side_effect = [max_ver_result, study_result]
        session.add = MagicMock()  # sync mock so side_effect captures work
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        mock_protocol = MagicMock()
        mock_protocol.practical_problem = None
        mock_protocol.research_questions = []

        captured = []
        session.add.side_effect = lambda obj: captured.append(obj)

        with (
            patch(
                "backend.services.evidence_briefing_service.rr_protocol_service.get_or_create_protocol",
                new=AsyncMock(return_value=mock_protocol),
            ),
            patch(
                "backend.services.evidence_briefing_service.narrative_synthesis_service.get_or_create_sections",
                new=AsyncMock(return_value=[]),
            ),
        ):
            await create_new_version(study_id=1, db=session)

        assert "Protocol Study XYZ" in captured[0].title

    @pytest.mark.asyncio
    async def test_populates_findings_from_sections(self) -> None:
        """Findings dict is populated with one entry per narrative section."""
        from backend.services.evidence_briefing_service import create_new_version

        max_ver_result = MagicMock()
        max_ver_result.scalar_one_or_none.return_value = None

        mock_study = MagicMock()
        mock_study.name = "Study"
        study_result = MagicMock()
        study_result.scalar_one_or_none.return_value = mock_study

        session = AsyncMock()
        session.execute.side_effect = [max_ver_result, study_result]
        session.add = MagicMock()  # sync mock so side_effect captures work
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        mock_protocol = MagicMock()
        mock_protocol.practical_problem = None
        mock_protocol.research_questions = ["RQ1", "RQ2"]

        section0 = MagicMock()
        section0.is_complete = True
        section0.narrative_text = "Finding for RQ0"
        section0.rq_index = 0

        section1 = MagicMock()
        section1.is_complete = False
        section1.narrative_text = "Incomplete finding"
        section1.rq_index = 1

        captured = []
        session.add.side_effect = lambda obj: captured.append(obj)

        with (
            patch(
                "backend.services.evidence_briefing_service.rr_protocol_service.get_or_create_protocol",
                new=AsyncMock(return_value=mock_protocol),
            ),
            patch(
                "backend.services.evidence_briefing_service.narrative_synthesis_service.get_or_create_sections",
                new=AsyncMock(return_value=[section0, section1]),
            ),
        ):
            await create_new_version(study_id=1, db=session)

        findings = captured[0].findings
        assert "0" in findings
        assert "1" in findings
        assert findings["0"] == "Finding for RQ0"

    @pytest.mark.asyncio
    async def test_fallback_study_name_when_study_not_found(self) -> None:
        """Falls back to 'Study {study_id}' when the study row does not exist."""
        from backend.services.evidence_briefing_service import create_new_version

        max_ver_result = MagicMock()
        max_ver_result.scalar_one_or_none.return_value = None

        study_result = MagicMock()
        study_result.scalar_one_or_none.return_value = None  # study missing

        session = AsyncMock()
        session.execute.side_effect = [max_ver_result, study_result]
        session.add = MagicMock()  # sync mock so side_effect captures work
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        mock_protocol = MagicMock()
        mock_protocol.practical_problem = None
        mock_protocol.research_questions = []

        captured = []
        session.add.side_effect = lambda obj: captured.append(obj)

        with (
            patch(
                "backend.services.evidence_briefing_service.rr_protocol_service.get_or_create_protocol",
                new=AsyncMock(return_value=mock_protocol),
            ),
            patch(
                "backend.services.evidence_briefing_service.narrative_synthesis_service.get_or_create_sections",
                new=AsyncMock(return_value=[]),
            ),
        ):
            await create_new_version(study_id=99, db=session)

        assert "99" in captured[0].title

    @pytest.mark.asyncio
    async def test_summary_falls_back_when_no_complete_sections(self) -> None:
        """Summary defaults to generic text when no section is complete."""
        from backend.services.evidence_briefing_service import create_new_version

        max_ver_result = MagicMock()
        max_ver_result.scalar_one_or_none.return_value = None

        mock_study = MagicMock()
        mock_study.name = "Study"
        study_result = MagicMock()
        study_result.scalar_one_or_none.return_value = mock_study

        session = AsyncMock()
        session.execute.side_effect = [max_ver_result, study_result]
        session.add = MagicMock()  # sync mock so side_effect captures work
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        mock_protocol = MagicMock()
        mock_protocol.practical_problem = None
        mock_protocol.research_questions = []

        captured = []
        session.add.side_effect = lambda obj: captured.append(obj)

        with (
            patch(
                "backend.services.evidence_briefing_service.rr_protocol_service.get_or_create_protocol",
                new=AsyncMock(return_value=mock_protocol),
            ),
            patch(
                "backend.services.evidence_briefing_service.narrative_synthesis_service.get_or_create_sections",
                new=AsyncMock(return_value=[]),
            ),
        ):
            await create_new_version(study_id=1, db=session)

        assert "evidence briefing" in captured[0].summary.lower()


# ---------------------------------------------------------------------------
# publish_version
# ---------------------------------------------------------------------------


class TestPublishVersion:
    """publish_version atomically promotes a briefing to PUBLISHED."""

    @pytest.mark.asyncio
    async def test_marks_briefing_as_published(self) -> None:
        """Sets status to PUBLISHED on the returned briefing."""
        from db.models.rapid_review import BriefingStatus
        from backend.services.evidence_briefing_service import publish_version

        mock_briefing = _make_briefing(status_val="draft", study_id=10)

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_briefing

        session = AsyncMock()
        # First execute: fetch briefing; second execute: demote update
        session.execute.side_effect = [fetch_result, MagicMock()]
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        await publish_version(briefing_id=1, db=session)

        assert mock_briefing.status == BriefingStatus.PUBLISHED

    @pytest.mark.asyncio
    async def test_raises_404_if_briefing_not_found(self) -> None:
        """Raises HTTP 404 when the briefing does not exist."""
        from backend.services.evidence_briefing_service import publish_version

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = None

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        with pytest.raises(HTTPException) as exc_info:
            await publish_version(briefing_id=999, db=session)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_executes_demote_update_for_previously_published(self) -> None:
        """Calls a second db.execute to demote previously published version."""
        from backend.services.evidence_briefing_service import publish_version

        mock_briefing = _make_briefing(status_val="draft", study_id=10)
        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_briefing

        demote_result = MagicMock()

        session = AsyncMock()
        session.execute.side_effect = [fetch_result, demote_result]
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        await publish_version(briefing_id=1, db=session)

        # Verify two execute calls were made: fetch + update
        assert session.execute.call_count == 2


# ---------------------------------------------------------------------------
# generate_html
# ---------------------------------------------------------------------------


class TestGenerateHtml:
    """generate_html renders a Jinja2 template and stores html_path."""

    @pytest.mark.asyncio
    async def test_raises_404_if_briefing_not_found(self) -> None:
        """Raises HTTP 404 when the briefing ID does not exist."""
        from backend.services.evidence_briefing_service import generate_html

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = None

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        with pytest.raises(HTTPException) as exc_info:
            await generate_html(briefing_id=999, db=session)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_stores_html_path_and_commits(self) -> None:
        """Sets html_path on the briefing and calls db.commit."""
        import tempfile
        import os
        from backend.services.evidence_briefing_service import generate_html

        mock_briefing = _make_briefing(study_id=5)
        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_briefing

        threats_result = MagicMock()
        threats_result.scalars.return_value.all.return_value = []

        session = AsyncMock()
        session.execute.side_effect = [fetch_result, threats_result]
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        mock_protocol = MagicMock()
        mock_protocol.research_questions = ["RQ1"]

        mock_template = MagicMock()
        mock_template.render.return_value = "<html>content</html>"

        with (
            patch(
                "backend.services.evidence_briefing_service.rr_protocol_service.get_or_create_protocol",
                new=AsyncMock(return_value=mock_protocol),
            ),
            patch(
                "backend.services.evidence_briefing_service._jinja_env"
            ) as mock_env,
        ):
            mock_env.get_template.return_value = mock_template

            await generate_html(briefing_id=1, db=session)

        assert mock_briefing.html_path is not None
        assert mock_briefing.html_path.endswith(".html")
        session.commit.assert_awaited()


# ---------------------------------------------------------------------------
# generate_pdf
# ---------------------------------------------------------------------------


class TestGeneratePdf:
    """generate_pdf converts HTML to PDF via WeasyPrint."""

    @pytest.mark.asyncio
    async def test_raises_404_if_briefing_not_found(self) -> None:
        """Raises HTTP 404 when the briefing ID does not exist."""
        from backend.services.evidence_briefing_service import generate_pdf

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = None

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        with pytest.raises(HTTPException) as exc_info:
            await generate_pdf(briefing_id=999, db=session)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_raises_422_if_html_path_not_set(self) -> None:
        """Raises HTTP 422 when html_path is not set on the briefing."""
        from backend.services.evidence_briefing_service import generate_pdf

        mock_briefing = _make_briefing(html_path=None)
        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_briefing

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        with pytest.raises(HTTPException) as exc_info:
            await generate_pdf(briefing_id=1, db=session)

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_calls_weasyprint_and_stores_pdf_path(self) -> None:
        """Calls weasyprint.HTML and sets pdf_path on the briefing."""
        from backend.services.evidence_briefing_service import generate_pdf

        mock_briefing = _make_briefing(html_path="/tmp/briefings/1/evidence_briefing.html")
        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_briefing

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        mock_wp_html_instance = MagicMock()
        mock_wp_html_cls = MagicMock(return_value=mock_wp_html_instance)

        with patch.dict("sys.modules", {"weasyprint": MagicMock(HTML=mock_wp_html_cls)}):
            await generate_pdf(briefing_id=1, db=session)

        mock_wp_html_cls.assert_called_once()
        mock_wp_html_instance.write_pdf.assert_called_once()
        assert mock_briefing.pdf_path is not None
        assert mock_briefing.pdf_path.endswith(".pdf")


# ---------------------------------------------------------------------------
# create_share_token
# ---------------------------------------------------------------------------


class TestCreateShareToken:
    """create_share_token creates an opaque share token."""

    @pytest.mark.asyncio
    async def test_raises_404_if_briefing_not_found(self) -> None:
        """Raises HTTP 404 when the briefing does not exist."""
        from backend.services.evidence_briefing_service import create_share_token

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = None

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        with pytest.raises(HTTPException) as exc_info:
            await create_share_token(briefing_id=999, created_by_user_id=1, db=session)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_raises_422_if_no_published_briefing(self) -> None:
        """Raises HTTP 422 when no published version exists for the study."""
        from backend.services.evidence_briefing_service import create_share_token

        mock_briefing = _make_briefing(status_val="draft", study_id=10)
        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_briefing

        published_result = MagicMock()
        published_result.scalar_one_or_none.return_value = None  # no published version

        session = AsyncMock()
        session.execute.side_effect = [fetch_result, published_result]

        with pytest.raises(HTTPException) as exc_info:
            await create_share_token(briefing_id=1, created_by_user_id=1, db=session)

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_creates_token_with_correct_fields(self) -> None:
        """Creates a share token with the correct briefing_id and study_id."""
        from backend.services.evidence_briefing_service import create_share_token

        mock_briefing = _make_briefing(status_val="published", study_id=10)
        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_briefing

        published_result = MagicMock()
        published_result.scalar_one_or_none.return_value = mock_briefing  # has published version

        session = AsyncMock()
        session.execute.side_effect = [fetch_result, published_result]
        session.add = MagicMock()  # sync mock so side_effect captures work
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        captured = []
        session.add.side_effect = lambda obj: captured.append(obj)

        await create_share_token(briefing_id=1, created_by_user_id=42, db=session)

        assert len(captured) == 1
        token_obj = captured[0]
        assert token_obj.briefing_id == 1
        assert token_obj.study_id == 10
        assert token_obj.created_by_user_id == 42

    @pytest.mark.asyncio
    async def test_token_is_url_safe_string(self) -> None:
        """The generated token is a non-empty URL-safe string."""
        from backend.services.evidence_briefing_service import create_share_token

        mock_briefing = _make_briefing(status_val="published", study_id=10)
        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_briefing

        published_result = MagicMock()
        published_result.scalar_one_or_none.return_value = mock_briefing

        session = AsyncMock()
        session.execute.side_effect = [fetch_result, published_result]
        session.add = MagicMock()  # sync mock so side_effect captures work
        session.commit = AsyncMock()
        session.refresh = AsyncMock()

        captured = []
        session.add.side_effect = lambda obj: captured.append(obj)

        await create_share_token(briefing_id=1, created_by_user_id=1, db=session)

        token_str = captured[0].token
        assert isinstance(token_str, str)
        assert len(token_str) > 0
        # secrets.token_urlsafe(32) produces 43-char strings
        assert len(token_str) == 43


# ---------------------------------------------------------------------------
# revoke_token
# ---------------------------------------------------------------------------


class TestRevokeToken:
    """revoke_token sets revoked_at on the token record."""

    @pytest.mark.asyncio
    async def test_raises_404_if_token_not_found(self) -> None:
        """Raises HTTP 404 when the token string is not in the database."""
        from backend.services.evidence_briefing_service import revoke_token

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = None

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        with pytest.raises(HTTPException) as exc_info:
            await revoke_token(token="nonexistent", db=session)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_sets_revoked_at(self) -> None:
        """Sets revoked_at to a non-None datetime on the token record."""
        from backend.services.evidence_briefing_service import revoke_token

        mock_token = MagicMock()
        mock_token.id = 7
        mock_token.revoked_at = None

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_token

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]
        session.commit = AsyncMock()

        await revoke_token(token="valid-token", db=session)

        assert mock_token.revoked_at is not None
        session.commit.assert_awaited()


# ---------------------------------------------------------------------------
# resolve_token
# ---------------------------------------------------------------------------


class TestResolveToken:
    """resolve_token validates a share token and returns the published briefing."""

    @pytest.mark.asyncio
    async def test_raises_404_for_revoked_or_missing_token(self) -> None:
        """Raises HTTP 404 when the token is not found (revoked or missing)."""
        from backend.services.evidence_briefing_service import resolve_token

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = None

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        with pytest.raises(HTTPException) as exc_info:
            await resolve_token(token="bad-token", db=session)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_raises_404_for_expired_token(self) -> None:
        """Raises HTTP 404 when the token's expires_at is in the past."""
        from backend.services.evidence_briefing_service import resolve_token

        mock_token = MagicMock()
        mock_token.expires_at = datetime.now(UTC) - timedelta(hours=1)  # expired
        mock_token.study_id = 10

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_token

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        with pytest.raises(HTTPException) as exc_info:
            await resolve_token(token="expired-token", db=session)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_raises_404_if_no_published_briefing(self) -> None:
        """Raises HTTP 404 when no published briefing exists for the study."""
        from backend.services.evidence_briefing_service import resolve_token

        mock_token = MagicMock()
        mock_token.expires_at = None  # no expiry
        mock_token.study_id = 10

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_token

        briefing_result = MagicMock()
        briefing_result.scalar_one_or_none.return_value = None  # no published briefing

        session = AsyncMock()
        session.execute.side_effect = [fetch_result, briefing_result]

        with pytest.raises(HTTPException) as exc_info:
            await resolve_token(token="valid-token", db=session)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_published_briefing_for_valid_token(self) -> None:
        """Returns the published briefing when the token is valid and not expired."""
        from backend.services.evidence_briefing_service import resolve_token

        mock_token = MagicMock()
        mock_token.expires_at = None  # no expiry
        mock_token.study_id = 10

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_token

        mock_briefing = _make_briefing(status_val="published", study_id=10)
        briefing_result = MagicMock()
        briefing_result.scalar_one_or_none.return_value = mock_briefing

        session = AsyncMock()
        session.execute.side_effect = [fetch_result, briefing_result]

        result = await resolve_token(token="valid-token", db=session)

        assert result is mock_briefing

    @pytest.mark.asyncio
    async def test_accepts_non_expired_token(self) -> None:
        """Returns briefing when token has a future expires_at."""
        from backend.services.evidence_briefing_service import resolve_token

        mock_token = MagicMock()
        mock_token.expires_at = datetime.now(UTC) + timedelta(days=7)  # future
        mock_token.study_id = 10

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_token

        mock_briefing = _make_briefing(status_val="published", study_id=10)
        briefing_result = MagicMock()
        briefing_result.scalar_one_or_none.return_value = mock_briefing

        session = AsyncMock()
        session.execute.side_effect = [fetch_result, briefing_result]

        result = await resolve_token(token="valid-token", db=session)

        assert result is mock_briefing
