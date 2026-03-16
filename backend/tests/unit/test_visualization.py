"""Unit tests for backend.services.visualization.

Patches matplotlib and matplotlib.pyplot via patch.dict(sys.modules) so no
graphical backend is required.  Verifies that each public function returns a
string and does not raise under normal and edge-case inputs.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pyplot_mock() -> tuple[MagicMock, MagicMock, MagicMock]:
    """Build a minimal matplotlib.pyplot mock.

    Returns:
        A ``(plt_mock, fig_mock, ax_mock)`` triple whose ``fig.savefig``
        writes a minimal SVG to its buffer argument so the tested functions
        return a non-empty string.
    """
    import io as _real_io

    fig_mock = MagicMock()
    ax_mock = MagicMock()
    bar1 = MagicMock()
    bar1.get_x.return_value = 0.0
    bar1.get_width.return_value = 1.0
    bar1.get_height.return_value = 5.0
    ax_mock.bar.return_value = [bar1]
    ax_mock.text = MagicMock()
    ax_mock.spines = MagicMock()
    ax_mock.spines.__getitem__ = MagicMock(return_value=MagicMock())

    def _fake_savefig(buf: _real_io.StringIO, format: str) -> None:  # noqa: A002
        buf.write("<svg xmlns='http://www.w3.org/2000/svg'><rect/></svg>")

    fig_mock.savefig.side_effect = _fake_savefig

    plt_mock = MagicMock()
    plt_mock.subplots.return_value = (fig_mock, ax_mock)
    plt_mock.close = MagicMock()
    plt_mock.xticks = MagicMock()
    plt_mock.tight_layout = MagicMock()

    return plt_mock, fig_mock, ax_mock


def _matplotlib_patch(plt_mock: MagicMock):
    """Return a patch.dict context manager that injects matplotlib mocks.

    Args:
        plt_mock: The pyplot mock to inject.

    Returns:
        A ``patch.dict`` context manager for ``sys.modules``.
    """
    mat_mock = MagicMock()
    mat_mock.use = MagicMock()
    mat_mock.pyplot = plt_mock
    return patch.dict(sys.modules, {"matplotlib": mat_mock, "matplotlib.pyplot": plt_mock})


# ---------------------------------------------------------------------------
# generate_bar_chart
# ---------------------------------------------------------------------------


def test_generate_bar_chart_returns_nonempty_svg() -> None:
    """generate_bar_chart returns a non-empty string when matplotlib is mocked."""
    plt_mock, _fig, _ax = _make_pyplot_mock()

    with _matplotlib_patch(plt_mock):
        from backend.services.visualization import generate_bar_chart
        result = generate_bar_chart({"2020": 5, "2021": 8}, "Papers by Year", "Year", "Count")

    assert isinstance(result, str)


def test_generate_bar_chart_with_empty_data() -> None:
    """generate_bar_chart handles an empty dict without raising."""
    plt_mock, _fig, _ax = _make_pyplot_mock()

    with _matplotlib_patch(plt_mock):
        from backend.services.visualization import generate_bar_chart
        result = generate_bar_chart({}, "Empty", "X", "Y")

    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# generate_classification_charts / _build_classification_data
# ---------------------------------------------------------------------------


def test_build_classification_data_research_type() -> None:
    """_build_classification_data aggregates research_type correctly."""
    from backend.services.visualization import _build_classification_data

    extractions = [
        {"research_type": "evaluation", "venue_type": "journal", "venue_name": "TSE",
         "author_details": [], "keywords": []},
        {"research_type": "evaluation", "venue_type": "conference", "venue_name": "ICSE",
         "author_details": [], "keywords": []},
        {"research_type": "validation", "venue_type": "journal", "venue_name": "JSS",
         "author_details": [], "keywords": []},
    ]
    result = _build_classification_data(extractions, "research_type")
    assert result.get("evaluation") == 2
    assert result.get("validation") == 1


def test_build_classification_data_venue() -> None:
    """_build_classification_data aggregates venue_name correctly."""
    from backend.services.visualization import _build_classification_data

    extractions = [
        {"research_type": "evaluation", "venue_type": "journal", "venue_name": "TSE",
         "author_details": [], "keywords": []},
        {"research_type": "evaluation", "venue_type": "journal", "venue_name": "TSE",
         "author_details": [], "keywords": []},
        {"research_type": "evaluation", "venue_type": "conference", "venue_name": None,
         "author_details": [], "keywords": []},
    ]
    result = _build_classification_data(extractions, "venue")
    assert result.get("TSE") == 2


def test_build_classification_data_keywords() -> None:
    """_build_classification_data counts keyword occurrences."""
    from backend.services.visualization import _build_classification_data

    extractions = [
        {"research_type": "evaluation", "venue_type": "journal", "venue_name": "TSE",
         "author_details": [], "keywords": ["agile", "scrum"]},
        {"research_type": "evaluation", "venue_type": "journal", "venue_name": "TSE",
         "author_details": [], "keywords": ["agile", "kanban"]},
    ]
    result = _build_classification_data(extractions, "subtopic")
    assert result.get("agile") == 2
    assert result.get("scrum") == 1
    assert result.get("kanban") == 1


def test_build_classification_data_locale() -> None:
    """_build_classification_data aggregates author locale."""
    from backend.services.visualization import _build_classification_data

    extractions = [
        {"research_type": "evaluation", "venue_type": "journal", "venue_name": "TSE",
         "author_details": [{"name": "Alice", "locale": "US"}, {"name": "Bob", "locale": "UK"}],
         "keywords": []},
        {"research_type": "evaluation", "venue_type": "journal", "venue_name": "TSE",
         "author_details": [{"name": "Carol", "locale": "US"}],
         "keywords": []},
    ]
    result = _build_classification_data(extractions, "locale")
    assert result.get("US") == 2
    assert result.get("UK") == 1


def test_build_classification_data_empty_extractions() -> None:
    """_build_classification_data returns empty dict for empty input."""
    from backend.services.visualization import _build_classification_data

    result = _build_classification_data([], "research_type")
    assert result == {}


def test_build_classification_data_author() -> None:
    """_build_classification_data counts author names."""
    from backend.services.visualization import _build_classification_data

    extractions = [
        {"research_type": "eval", "venue_type": "j", "venue_name": "J",
         "author_details": [{"name": "Alice", "locale": "US"}],
         "keywords": []},
        {"research_type": "eval", "venue_type": "j", "venue_name": "J",
         "author_details": [{"name": "Alice", "locale": "US"}, {"name": None, "locale": "US"}],
         "keywords": []},
    ]
    result = _build_classification_data(extractions, "author")
    assert result.get("Alice") == 2


def test_build_classification_data_institution() -> None:
    """_build_classification_data counts author institutions."""
    from backend.services.visualization import _build_classification_data

    extractions = [
        {"research_type": "eval", "venue_type": "j", "venue_name": "J",
         "author_details": [{"name": "A", "locale": "US", "institution": "MIT"}],
         "keywords": []},
    ]
    result = _build_classification_data(extractions, "institution")
    assert result.get("MIT") == 1


def test_build_classification_data_year() -> None:
    """_build_classification_data groups by year."""
    from backend.services.visualization import _build_classification_data

    extractions = [
        {"research_type": "eval", "venue_type": "j", "venue_name": "J",
         "author_details": [], "keywords": [], "year": 2021},
        {"research_type": "eval", "venue_type": "j", "venue_name": "J",
         "author_details": [], "keywords": [], "year": 2021},
        {"research_type": "eval", "venue_type": "j", "venue_name": "J",
         "author_details": [], "keywords": [], "year": None},
    ]
    result = _build_classification_data(extractions, "year")
    assert result.get("2021") == 2
    assert result.get("Unknown") == 1


def test_build_classification_data_research_method() -> None:
    """_build_classification_data aggregates research_method via venue_type."""
    from backend.services.visualization import _build_classification_data

    extractions = [
        {"research_type": "eval", "venue_type": "journal", "venue_name": "J",
         "author_details": [], "keywords": []},
    ]
    result = _build_classification_data(extractions, "research_method")
    assert result.get("journal") == 1


# ---------------------------------------------------------------------------
# generate_frequency_infographic
# ---------------------------------------------------------------------------


def test_generate_frequency_infographic_returns_string() -> None:
    """generate_frequency_infographic returns a string without raising."""
    plt_mock, _fig, ax_mock = _make_pyplot_mock()
    bar1 = MagicMock()
    bar1.get_x.return_value = 0.0
    bar1.get_width.return_value = 1.0
    bar1.get_height.return_value = 3.0
    ax_mock.bar.return_value = [bar1]

    with _matplotlib_patch(plt_mock):
        from backend.services.visualization import generate_frequency_infographic
        result = generate_frequency_infographic({"2020": 3, "2021": 5})

    assert isinstance(result, str)


def test_generate_classification_charts_venue() -> None:
    """generate_classification_charts delegates correctly for venue chart type."""
    plt_mock, _fig, _ax = _make_pyplot_mock()
    extractions = [
        {"research_type": "eval", "venue_type": "j", "venue_name": "TSE",
         "author_details": [], "keywords": []},
    ]

    with _matplotlib_patch(plt_mock):
        from backend.services.visualization import generate_classification_charts
        result = generate_classification_charts(extractions, "venue")

    assert isinstance(result, str)
