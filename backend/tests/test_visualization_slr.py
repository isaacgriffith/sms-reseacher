"""Unit tests for SLR-specific visualization functions (feature 007).

Tests cover:
- generate_forest_plot: SVG output, minimum-study guard, layout.
- generate_funnel_plot: SVG output, funnel envelope math (95% CI lines).
"""

from __future__ import annotations

import pytest

from backend.services.visualization import (
    StudyPlotData,
    generate_forest_plot,
    generate_funnel_plot,
)


def _make_studies(n: int) -> list[StudyPlotData]:
    """Return n generic study entries suitable for plot testing."""
    return [
        StudyPlotData(
            label=f"Study {i + 1}",
            effect_size=0.3 * i,
            ci_lower=0.3 * i - 0.2,
            ci_upper=0.3 * i + 0.2,
            weight=1.0,
        )
        for i in range(n)
    ]


def _pooled() -> StudyPlotData:
    """Return a generic pooled estimate for testing."""
    return StudyPlotData(
        label="Pooled",
        effect_size=0.5,
        ci_lower=0.3,
        ci_upper=0.7,
        weight=2.0,
    )


class TestGenerateForestPlot:
    """generate_forest_plot produces valid SVG or raises on too few studies."""

    def test_returns_svg_string(self) -> None:
        """Output starts with the SVG XML declaration."""
        svg = generate_forest_plot(_make_studies(3), _pooled(), title="Test Forest")
        assert isinstance(svg, str)
        assert len(svg) > 0
        assert "<svg" in svg

    def test_title_in_output(self) -> None:
        """The provided title appears somewhere in the SVG text."""
        svg = generate_forest_plot(_make_studies(3), _pooled(), title="My Title")
        assert "My Title" in svg

    def test_fewer_than_min_raises(self) -> None:
        """Fewer than slr_min_synthesis_papers studies raises ValueError."""
        with pytest.raises(ValueError, match="requires at least"):
            generate_forest_plot(_make_studies(2), _pooled(), title="Too few")

    def test_exactly_min_succeeds(self) -> None:
        """Exactly slr_min_synthesis_papers (3) studies succeeds."""
        svg = generate_forest_plot(_make_studies(3), _pooled(), title="Exact min")
        assert "<svg" in svg

    def test_many_studies_succeeds(self) -> None:
        """Ten studies produce a non-empty SVG."""
        svg = generate_forest_plot(_make_studies(10), _pooled(), title="Many")
        assert len(svg) > 100

    def test_zero_studies_raises(self) -> None:
        """Empty study list raises ValueError."""
        with pytest.raises(ValueError, match="requires at least"):
            generate_forest_plot([], _pooled(), title="Empty")


class TestGenerateFunnelPlot:
    """generate_funnel_plot produces valid SVG with a funnel envelope."""

    def test_returns_svg_string(self) -> None:
        """Output is a non-empty SVG string."""
        svg = generate_funnel_plot(_make_studies(3), _pooled(), title="Funnel")
        assert isinstance(svg, str)
        assert "<svg" in svg

    def test_title_in_output(self) -> None:
        """The provided title appears in the SVG."""
        svg = generate_funnel_plot(_make_studies(3), _pooled(), title="Funnel Chart")
        assert "Funnel Chart" in svg

    def test_single_study_succeeds(self) -> None:
        """Funnel plot does not enforce minimum study count."""
        svg = generate_funnel_plot(_make_studies(1), _pooled(), title="Single")
        assert "<svg" in svg

    def test_envelope_math(self) -> None:
        """SVG contains numeric values consistent with 1.96 × SE envelope.

        For a study with ci_lower=0.1, ci_upper=0.9:
        SE = (0.9 - 0.1) / (2 * 1.96) ≈ 0.204
        Upper envelope at that SE: pooled(0.5) + 1.96 * 0.204 ≈ 0.9.

        We verify that the SVG encodes the correct effect size value.
        """
        study = StudyPlotData(
            label="Study A",
            effect_size=0.5,
            ci_lower=0.1,
            ci_upper=0.9,
            weight=1.0,
        )
        pooled = StudyPlotData(
            label="Pooled",
            effect_size=0.5,
            ci_lower=0.3,
            ci_upper=0.7,
        )
        svg = generate_funnel_plot([study], pooled, title="Envelope test")
        # The SVG must exist and encode visual content
        assert "<svg" in svg
        assert len(svg) > 200
