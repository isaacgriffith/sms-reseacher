"""Unit tests for backend.services.statistics (feature 007).

Tests cover:
- safe_cohen_kappa: perfect agreement, chance-level, zero-variance (undefined).
- compute_q_test: formula correctness, minimum-study guard.
- fixed_effects_meta_analysis: pooled effect and CI against known values.
- random_effects_meta_analysis: τ²-adjusted pooling with high heterogeneity.
"""

from __future__ import annotations

import math

import pytest

from backend.services.statistics import (
    MetaAnalysisResult,
    QTestResult,
    compute_q_test,
    fixed_effects_meta_analysis,
    random_effects_meta_analysis,
    safe_cohen_kappa,
)


class TestSafeCohenKappa:
    """safe_cohen_kappa returns a float for valid inputs and None for undefined."""

    def test_perfect_agreement(self) -> None:
        """Identical binary decisions yield kappa == 1.0."""
        result = safe_cohen_kappa([0, 1, 0, 1, 1], [0, 1, 0, 1, 1])
        assert result == pytest.approx(1.0)

    def test_chance_agreement(self) -> None:
        """Complete disagreement yields kappa < 0."""
        result = safe_cohen_kappa([0, 0, 1, 1], [1, 1, 0, 0])
        assert result is not None
        assert result < 0.0

    def test_zero_variance_returns_none(self) -> None:
        """All-same decisions from both reviewers is undefined → None."""
        result = safe_cohen_kappa([1, 1, 1, 1], [1, 1, 1, 1])
        # sklearn returns nan for zero-variance; we convert to None
        assert result is None

    def test_string_labels(self) -> None:
        """String decision labels are supported."""
        result = safe_cohen_kappa(
            ["include", "exclude", "include"],
            ["include", "exclude", "include"],
        )
        assert result == pytest.approx(1.0)

    def test_mismatched_lengths_raises(self) -> None:
        """Different-length inputs raise ValueError."""
        with pytest.raises(ValueError, match="equal length"):
            safe_cohen_kappa([0, 1], [0, 1, 0])

    def test_partial_agreement(self) -> None:
        """Partial agreement yields kappa between 0 and 1."""
        result = safe_cohen_kappa([0, 1, 0, 1, 0, 1], [0, 1, 0, 1, 1, 0])
        assert result is not None
        assert 0.0 < result < 1.0


class TestComputeQTest:
    """compute_q_test computes Q statistic, p-value, I², and τ²."""

    def test_homogeneous_studies(self) -> None:
        """Identical effect sizes → Q ≈ 0, large p-value, I² == 0."""
        effect_sizes = [0.5, 0.5, 0.5]
        weights = [4.0, 4.0, 4.0]
        result = compute_q_test(effect_sizes, weights)
        assert isinstance(result, QTestResult)
        assert result.q_statistic == pytest.approx(0.0, abs=1e-10)
        assert result.p_value == pytest.approx(1.0, abs=0.01)
        assert result.i_squared == pytest.approx(0.0, abs=0.01)
        assert result.tau_squared == pytest.approx(0.0, abs=1e-10)

    def test_heterogeneous_studies(self) -> None:
        """Heterogeneous effect sizes → Q > df, small p-value, I² > 0."""
        effect_sizes = [0.1, 0.5, 1.5, 2.0]
        weights = [10.0, 10.0, 10.0, 10.0]
        result = compute_q_test(effect_sizes, weights)
        assert result.q_statistic > result.df
        assert result.p_value < 0.05
        assert result.i_squared > 0.0
        assert result.tau_squared >= 0.0

    def test_df_equals_k_minus_1(self) -> None:
        """Degrees of freedom equals number of studies minus one."""
        result = compute_q_test([0.2, 0.4, 0.6], [5.0, 5.0, 5.0])
        assert result.df == 2

    def test_too_few_studies_raises(self) -> None:
        """Fewer than two studies raises ValueError."""
        with pytest.raises(ValueError, match="At least two"):
            compute_q_test([0.5], [1.0])

    def test_mismatched_lengths_raises(self) -> None:
        """Mismatched effect_sizes / weights raises ValueError."""
        with pytest.raises(ValueError, match="equal length"):
            compute_q_test([0.5, 0.6], [1.0])


class TestFixedEffectsMetaAnalysis:
    """fixed_effects_meta_analysis pools effect sizes under fixed-effects model."""

    def test_symmetric_two_studies(self) -> None:
        """Two studies with equal SE produce pooled == mean and pooled SE < individual SE."""
        result = fixed_effects_meta_analysis([0.5, 0.5], [0.1, 0.1])
        assert isinstance(result, MetaAnalysisResult)
        assert result.pooled_effect == pytest.approx(0.5)
        assert result.se < 0.1  # pooling reduces SE
        assert result.model == "fixed"

    def test_ci_contains_pooled(self) -> None:
        """Confidence interval contains the pooled estimate."""
        result = fixed_effects_meta_analysis([0.3, 0.7], [0.2, 0.2])
        assert result.ci_lower < result.pooled_effect < result.ci_upper

    def test_pooled_effect_known_value(self) -> None:
        """Verify pooled effect against manually computed value.

        Two studies: effect=[0.0, 1.0], se=[1.0, 1.0].
        Weights = [1, 1], pooled = (0*1 + 1*1) / 2 = 0.5.
        """
        result = fixed_effects_meta_analysis([0.0, 1.0], [1.0, 1.0])
        assert result.pooled_effect == pytest.approx(0.5)

    def test_95_ci_width_known_value(self) -> None:
        """Verify 95% CI width for two studies with known SE.

        se=[1, 1] → pooled_se = 1/sqrt(2) ≈ 0.707.
        95% CI half-width = 1.96 × 0.707 ≈ 1.386.
        """
        result = fixed_effects_meta_analysis([0.0, 1.0], [1.0, 1.0])
        half_width = (result.ci_upper - result.ci_lower) / 2.0
        assert half_width == pytest.approx(1.96 / math.sqrt(2.0), rel=0.01)

    def test_mismatched_lengths_raises(self) -> None:
        """Mismatched effect_sizes / ses raises ValueError."""
        with pytest.raises(ValueError, match="equal length"):
            fixed_effects_meta_analysis([0.5], [0.1, 0.1])

    def test_too_few_studies_raises(self) -> None:
        """Single study raises ValueError."""
        with pytest.raises(ValueError, match="At least two"):
            fixed_effects_meta_analysis([0.5], [0.1])

    def test_q_test_embedded(self) -> None:
        """Result includes a QTestResult."""
        result = fixed_effects_meta_analysis([0.4, 0.6], [0.2, 0.2])
        assert isinstance(result.q_test, QTestResult)


class TestRandomEffectsMetaAnalysis:
    """random_effects_meta_analysis pools effect sizes under DerSimonian-Laird model."""

    def test_model_label(self) -> None:
        """Result model field is 'random'."""
        result = random_effects_meta_analysis([0.5, 0.5], [0.1, 0.1])
        assert result.model == "random"

    def test_homogeneous_matches_fixed(self) -> None:
        """With zero heterogeneity random-effects ≈ fixed-effects."""
        fixed = fixed_effects_meta_analysis([0.5, 0.5], [0.2, 0.2])
        random = random_effects_meta_analysis([0.5, 0.5], [0.2, 0.2])
        assert random.pooled_effect == pytest.approx(fixed.pooled_effect, rel=0.01)

    def test_heterogeneous_wider_ci(self) -> None:
        """With high heterogeneity random-effects CI is wider than fixed-effects CI."""
        effects = [0.1, 0.5, 1.5, 2.5]
        ses = [0.1, 0.1, 0.1, 0.1]
        fixed = fixed_effects_meta_analysis(effects, ses)
        random = random_effects_meta_analysis(effects, ses)
        fixed_width = fixed.ci_upper - fixed.ci_lower
        random_width = random.ci_upper - random.ci_lower
        assert random_width > fixed_width

    def test_ci_contains_pooled(self) -> None:
        """Confidence interval contains the pooled estimate."""
        result = random_effects_meta_analysis([0.3, 0.7, 1.2], [0.3, 0.3, 0.3])
        assert result.ci_lower < result.pooled_effect < result.ci_upper

    def test_mismatched_lengths_raises(self) -> None:
        """Mismatched inputs raise ValueError."""
        with pytest.raises(ValueError, match="equal length"):
            random_effects_meta_analysis([0.5, 0.6], [0.1])

    def test_too_few_studies_raises(self) -> None:
        """Single study raises ValueError."""
        with pytest.raises(ValueError, match="At least two"):
            random_effects_meta_analysis([0.5], [0.1])
