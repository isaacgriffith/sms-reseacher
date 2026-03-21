"""Unit tests for backend.services.synthesis_strategies (feature 007, T068).

Tests cover:
- MetaAnalysisSynthesizer: 3 papers → SynthesisOutput with funnel_plot_svg.
- Auto model selection picks random when Q-test p_value < heterogeneity_threshold.
- Auto model selection picks fixed when Q-test p_value >= heterogeneity_threshold.
- DescriptiveSynthesizer: 3 papers → SynthesisOutput with forest_plot_svg.
- DescriptiveSynthesizer raises ValueError with 2 papers (< slr_min_synthesis_papers).
- QualitativeSynthesizer returns qualitative_themes.
- Sensitivity analysis populated when subsets/exclude_paper_ids provided.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.synthesis_strategies import (
    DescriptiveSynthesizer,
    MetaAnalysisSynthesizer,
    QualitativeSynthesizer,
    SynthesisOutput,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_PAPERS_3 = [
    {"label": "Smith 2020", "effect_size": 0.4, "se": 0.1, "ci_lower": 0.2, "ci_upper": 0.6, "weight": 1.0},
    {"label": "Jones 2021", "effect_size": 0.5, "se": 0.12, "ci_lower": 0.26, "ci_upper": 0.74, "weight": 1.0},
    {"label": "Brown 2022", "effect_size": 0.3, "se": 0.09, "ci_lower": 0.12, "ci_upper": 0.48, "weight": 1.0},
]

_DESCRIPTIVE_PAPERS_3 = [
    {"label": "A", "effect_size": 0.4, "ci_lower": 0.2, "ci_upper": 0.6, "weight": 1.0, "sample_size": 50, "unit": "SMD"},
    {"label": "B", "effect_size": 0.5, "ci_lower": 0.3, "ci_upper": 0.7, "weight": 1.0, "sample_size": 80, "unit": "SMD"},
    {"label": "C", "effect_size": 0.3, "ci_lower": 0.1, "ci_upper": 0.5, "weight": 1.0, "sample_size": 60, "unit": "SMD"},
]

_FAKE_FUNNEL_SVG = "<svg>funnel</svg>"
_FAKE_FOREST_SVG = "<svg>forest</svg>"


def _make_db():
    """Return a minimal async mock database session."""
    return AsyncMock()


# ---------------------------------------------------------------------------
# MetaAnalysisSynthesizer
# ---------------------------------------------------------------------------


class TestMetaAnalysisSynthesizer:
    """Tests for MetaAnalysisSynthesizer.run."""

    @pytest.mark.asyncio
    async def test_run_3_papers_returns_funnel_plot_svg(self) -> None:
        """3 papers returns SynthesisOutput with funnel_plot_svg set."""
        from backend.services import statistics, visualization

        with (
            patch.object(
                statistics,
                "fixed_effects_meta_analysis",
                return_value=_fake_meta_result("fixed"),
            ) as mock_fixed,
            patch.object(
                statistics,
                "compute_q_test",
                return_value=_fake_q_result(p_value=0.5),
            ),
            patch.object(
                visualization,
                "generate_funnel_plot",
                return_value=_FAKE_FUNNEL_SVG,
            ) as mock_funnel,
        ):
            synthesizer = MetaAnalysisSynthesizer()
            output = await synthesizer.run(
                1,
                {"papers": _PAPERS_3, "model_type": "fixed"},
                _make_db(),
            )

        assert isinstance(output, SynthesisOutput)
        assert output.funnel_plot_svg == _FAKE_FUNNEL_SVG
        assert output.computed_statistics is not None
        assert output.forest_plot_svg is None
        mock_fixed.assert_called_once()
        mock_funnel.assert_called_once()

    @pytest.mark.asyncio
    async def test_auto_selects_random_when_high_heterogeneity(self) -> None:
        """Auto model picks random when Q p_value < heterogeneity_threshold."""
        from backend.services import statistics, visualization

        with (
            patch.object(
                statistics,
                "compute_q_test",
                return_value=_fake_q_result(p_value=0.01),  # < 0.1 threshold
            ),
            patch.object(
                statistics,
                "random_effects_meta_analysis",
                return_value=_fake_meta_result("random"),
            ) as mock_random,
            patch.object(
                statistics,
                "fixed_effects_meta_analysis",
                return_value=_fake_meta_result("fixed"),
            ) as mock_fixed,
            patch.object(
                visualization,
                "generate_funnel_plot",
                return_value=_FAKE_FUNNEL_SVG,
            ),
        ):
            synthesizer = MetaAnalysisSynthesizer()
            output = await synthesizer.run(
                1,
                {"papers": _PAPERS_3, "model_type": "auto", "heterogeneity_threshold": 0.1},
                _make_db(),
            )

        mock_random.assert_called_once()
        mock_fixed.assert_not_called()
        assert output.computed_statistics["model"] == "random"

    @pytest.mark.asyncio
    async def test_auto_selects_fixed_when_low_heterogeneity(self) -> None:
        """Auto model picks fixed when Q p_value >= heterogeneity_threshold."""
        from backend.services import statistics, visualization

        with (
            patch.object(
                statistics,
                "compute_q_test",
                return_value=_fake_q_result(p_value=0.8),  # >= 0.1 threshold
            ),
            patch.object(
                statistics,
                "fixed_effects_meta_analysis",
                return_value=_fake_meta_result("fixed"),
            ) as mock_fixed,
            patch.object(
                statistics,
                "random_effects_meta_analysis",
                return_value=_fake_meta_result("random"),
            ) as mock_random,
            patch.object(
                visualization,
                "generate_funnel_plot",
                return_value=_FAKE_FUNNEL_SVG,
            ),
        ):
            synthesizer = MetaAnalysisSynthesizer()
            output = await synthesizer.run(
                1,
                {"papers": _PAPERS_3, "model_type": "auto", "heterogeneity_threshold": 0.1},
                _make_db(),
            )

        mock_fixed.assert_called_once()
        mock_random.assert_not_called()
        assert output.computed_statistics["model"] == "fixed"

    @pytest.mark.asyncio
    async def test_sensitivity_analysis_populated_with_subsets(self) -> None:
        """sensitivity_analysis dict is populated when subsets are provided."""
        from backend.services import statistics, visualization

        with (
            patch.object(
                statistics,
                "compute_q_test",
                return_value=_fake_q_result(p_value=0.5),
            ),
            patch.object(
                statistics,
                "fixed_effects_meta_analysis",
                return_value=_fake_meta_result("fixed"),
            ),
            patch.object(
                visualization,
                "generate_funnel_plot",
                return_value=_FAKE_FUNNEL_SVG,
            ),
        ):
            synthesizer = MetaAnalysisSynthesizer()
            output = await synthesizer.run(
                1,
                {
                    "papers": _PAPERS_3,
                    "model_type": "auto",
                    "subsets": [{"name": "Sub1", "paper_indices": [0, 1]}],
                },
                _make_db(),
            )

        assert output.sensitivity_analysis is not None
        assert "Sub1" in output.sensitivity_analysis


# ---------------------------------------------------------------------------
# DescriptiveSynthesizer
# ---------------------------------------------------------------------------


class TestDescriptiveSynthesizer:
    """Tests for DescriptiveSynthesizer.run."""

    @pytest.mark.asyncio
    async def test_run_3_papers_returns_forest_plot_svg(self) -> None:
        """3 papers returns SynthesisOutput with forest_plot_svg set."""
        from backend.services import visualization

        with patch.object(
            visualization,
            "generate_forest_plot",
            return_value=_FAKE_FOREST_SVG,
        ) as mock_forest:
            synthesizer = DescriptiveSynthesizer()
            output = await synthesizer.run(
                1,
                {"papers": _DESCRIPTIVE_PAPERS_3},
                _make_db(),
            )

        assert isinstance(output, SynthesisOutput)
        assert output.forest_plot_svg == _FAKE_FOREST_SVG
        assert output.computed_statistics is not None
        assert output.funnel_plot_svg is None
        mock_forest.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_2_papers_raises_value_error(self) -> None:
        """Fewer than slr_min_synthesis_papers raises ValueError."""
        two_papers = _DESCRIPTIVE_PAPERS_3[:2]
        with patch("backend.services.synthesis_strategies.get_settings") as mock_s:
            mock_s.return_value.slr_min_synthesis_papers = 3
            synthesizer = DescriptiveSynthesizer()
            with pytest.raises(ValueError, match="Forest plot requires at least"):
                await synthesizer.run(1, {"papers": two_papers}, _make_db())

    @pytest.mark.asyncio
    async def test_computed_statistics_contains_n_papers(self) -> None:
        """computed_statistics includes n_papers count."""
        from backend.services import visualization

        with patch.object(
            visualization,
            "generate_forest_plot",
            return_value=_FAKE_FOREST_SVG,
        ):
            synthesizer = DescriptiveSynthesizer()
            output = await synthesizer.run(
                1,
                {"papers": _DESCRIPTIVE_PAPERS_3},
                _make_db(),
            )

        assert output.computed_statistics["n_papers"] == 3

    @pytest.mark.asyncio
    async def test_sensitivity_analysis_populated_with_subsets(self) -> None:
        """sensitivity_analysis is populated when subsets are provided."""
        from backend.services import visualization

        with patch.object(
            visualization,
            "generate_forest_plot",
            return_value=_FAKE_FOREST_SVG,
        ):
            synthesizer = DescriptiveSynthesizer()
            output = await synthesizer.run(
                1,
                {
                    "papers": _DESCRIPTIVE_PAPERS_3,
                    "subsets": [{"name": "RCT", "paper_indices": [0, 1]}],
                },
                _make_db(),
            )

        assert output.sensitivity_analysis is not None
        assert "RCT" in output.sensitivity_analysis


# ---------------------------------------------------------------------------
# QualitativeSynthesizer
# ---------------------------------------------------------------------------


class TestQualitativeSynthesizer:
    """Tests for QualitativeSynthesizer.run."""

    @pytest.mark.asyncio
    async def test_run_returns_qualitative_themes(self) -> None:
        """run returns SynthesisOutput with qualitative_themes."""
        themes = [
            {"theme_name": "Usability", "paper_ids": [1, 3, 5]},
            {"theme_name": "Performance", "paper_ids": [2, 4]},
        ]
        synthesizer = QualitativeSynthesizer()
        output = await synthesizer.run(
            1, {"themes": themes}, _make_db()
        )

        assert isinstance(output, SynthesisOutput)
        assert output.qualitative_themes is not None
        assert "Usability" in output.qualitative_themes["themes"]
        assert "Performance" in output.qualitative_themes["themes"]
        assert output.qualitative_themes["themes"]["Usability"] == [1, 3, 5]

    @pytest.mark.asyncio
    async def test_no_plots_generated(self) -> None:
        """forest_plot_svg and funnel_plot_svg are None."""
        synthesizer = QualitativeSynthesizer()
        output = await synthesizer.run(
            1,
            {"themes": [{"theme_name": "T1", "paper_ids": [1]}]},
            _make_db(),
        )

        assert output.forest_plot_svg is None
        assert output.funnel_plot_svg is None

    @pytest.mark.asyncio
    async def test_sensitivity_populated_with_exclude_paper_ids(self) -> None:
        """sensitivity_analysis remaps themes excluding excluded paper IDs."""
        themes = [
            {"theme_name": "Usability", "paper_ids": [1, 3, 5]},
            {"theme_name": "Performance", "paper_ids": [2, 4, 5]},
        ]
        synthesizer = QualitativeSynthesizer()
        output = await synthesizer.run(
            1,
            {"themes": themes, "exclude_paper_ids": [5]},
            _make_db(),
        )

        assert output.sensitivity_analysis is not None
        assert 5 not in output.sensitivity_analysis["themes"]["Usability"]
        assert 5 not in output.sensitivity_analysis["themes"]["Performance"]
        assert output.sensitivity_analysis["excluded_paper_ids"] == [5]

    @pytest.mark.asyncio
    async def test_sensitivity_none_when_no_exclude(self) -> None:
        """sensitivity_analysis is None when exclude_paper_ids is not provided."""
        synthesizer = QualitativeSynthesizer()
        output = await synthesizer.run(
            1,
            {"themes": [{"theme_name": "T1", "paper_ids": [1, 2]}]},
            _make_db(),
        )

        assert output.sensitivity_analysis is None


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _fake_meta_result(model: str):
    """Return a minimal MetaAnalysisResult-like object."""
    from backend.services.statistics import MetaAnalysisResult, QTestResult

    return MetaAnalysisResult(
        pooled_effect=0.4,
        se=0.06,
        ci_lower=0.28,
        ci_upper=0.52,
        z_score=6.67,
        p_value=0.001,
        model=model,
        q_test=QTestResult(
            q_statistic=2.1,
            df=2,
            p_value=0.35,
            i_squared=4.8,
            tau_squared=0.0,
        ),
    )


def _fake_q_result(p_value: float):
    """Return a minimal QTestResult-like object with given p_value."""
    from backend.services.statistics import QTestResult

    return QTestResult(
        q_statistic=2.1,
        df=2,
        p_value=p_value,
        i_squared=4.8,
        tau_squared=0.0,
    )
