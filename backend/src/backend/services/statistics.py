"""Statistical computation service for SLR workflow (feature 007).

Provides Cohen's Kappa inter-rater agreement, Q-test for heterogeneity,
and fixed/random-effects meta-analysis pooling.  All functions use
industry-standard scipy and scikit-learn implementations.

All numeric inputs/outputs are typed via Pydantic models so callers can
rely on structured, validated data rather than bare dicts.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from pydantic import BaseModel, Field


class QTestResult(BaseModel):
    """Result of Cochran's Q heterogeneity test.

    Attributes:
        q_statistic: The Q test statistic (sum of weighted squared deviations).
        df: Degrees of freedom (number of studies minus one).
        p_value: Two-tailed p-value from a chi-squared distribution.
        i_squared: I² statistic (percentage of variation due to heterogeneity).
        tau_squared: DerSimonian-Laird estimate of between-study variance τ².

    """

    q_statistic: float
    df: int
    p_value: float
    i_squared: float
    tau_squared: float


class MetaAnalysisResult(BaseModel):
    """Result of a fixed- or random-effects meta-analysis.

    Attributes:
        pooled_effect: Weighted pooled effect size estimate.
        se: Standard error of the pooled effect.
        ci_lower: Lower bound of the confidence interval.
        ci_upper: Upper bound of the confidence interval.
        z_score: Z-score for the pooled estimate.
        p_value: Two-tailed p-value for the pooled estimate.
        model: ``"fixed"`` or ``"random"``.
        q_test: Heterogeneity test result (always computed).

    """

    pooled_effect: float
    se: float
    ci_lower: float
    ci_upper: float
    z_score: float
    p_value: float
    model: str = Field(pattern=r"^(fixed|random)$")
    q_test: QTestResult


def safe_cohen_kappa(
    decisions_a: Sequence[int | str],
    decisions_b: Sequence[int | str],
) -> float | None:
    """Compute Cohen's Kappa between two reviewers' decisions.

    Uses ``sklearn.metrics.cohen_kappa_score``.  Returns ``None`` when
    the computation is undefined — typically because one reviewer made
    the same decision for every paper (zero-variance input), which would
    produce a division-by-zero in the kappa formula.

    Args:
        decisions_a: Ordered list of decisions from reviewer A.  Each
            element must be a label comparable to the corresponding
            element in ``decisions_b`` (e.g., 0/1 integers or string
            labels like ``"include"``/``"exclude"``).
        decisions_b: Ordered list of decisions from reviewer B.  Must
            have the same length as ``decisions_a``.

    Returns:
        Cohen's Kappa as a float in the range [-1, 1], or ``None`` if the
        score is undefined.

    Raises:
        ValueError: If ``decisions_a`` and ``decisions_b`` have different
            lengths.

    """
    if len(decisions_a) != len(decisions_b):
        raise ValueError(
            f"decisions_a and decisions_b must have equal length; "
            f"got {len(decisions_a)} and {len(decisions_b)}"
        )
    import math

    from sklearn.metrics import cohen_kappa_score  # type: ignore[import-untyped]

    try:
        result = cohen_kappa_score(decisions_a, decisions_b)
        if math.isnan(result):
            return None
        return float(result)
    except ValueError, ZeroDivisionError:
        return None


def _compute_weights(ses: list[float], tau_squared: float = 0.0) -> list[float]:
    """Compute inverse-variance weights for each study.

    Args:
        ses: Standard errors for each study effect size.
        tau_squared: Between-study variance estimate (0.0 for fixed effects).

    Returns:
        List of weights (1 / (se² + τ²)) for each study.

    """
    return [1.0 / (se**2 + tau_squared) for se in ses]


def _compute_q(effect_sizes: list[float], weights: list[float]) -> float:
    """Compute Cochran's Q statistic.

    Args:
        effect_sizes: Effect size estimates for each study.
        weights: Inverse-variance weights for each study.

    Returns:
        The Q test statistic.

    """
    weighted_sum = sum(w * e for w, e in zip(weights, effect_sizes, strict=True))
    total_weight = sum(weights)
    pooled = weighted_sum / total_weight
    return sum(w * (e - pooled) ** 2 for w, e in zip(weights, effect_sizes, strict=True))


def _pool_effect(effect_sizes: list[float], weights: list[float]) -> float:
    """Compute the weighted pooled effect size.

    Args:
        effect_sizes: Effect size estimates for each study.
        weights: Inverse-variance weights.

    Returns:
        Weighted mean effect size.

    """
    return sum(w * e for w, e in zip(weights, effect_sizes, strict=True)) / sum(weights)


def _build_ci(pooled: float, se: float, ci: float) -> tuple[float, float]:
    """Compute a symmetric confidence interval for the pooled estimate.

    Args:
        pooled: Pooled effect size estimate.
        se: Standard error of the pooled estimate.
        ci: Confidence level as a proportion (e.g., 0.95 for 95% CI).

    Returns:
        Tuple of ``(lower, upper)`` confidence interval bounds.

    """
    from scipy.stats import norm  # type: ignore[import-untyped]

    z = norm.ppf(1.0 - (1.0 - ci) / 2.0)
    return pooled - z * se, pooled + z * se


def compute_q_test(
    effect_sizes: list[float],
    weights: list[float],
) -> QTestResult:
    """Compute Cochran's Q test for heterogeneity.

    Computes the Q statistic, its p-value from a chi-squared distribution
    with (k-1) degrees of freedom, I² (percentage of variability due to
    heterogeneity), and the DerSimonian-Laird τ² estimate.

    Args:
        effect_sizes: Effect size estimate for each study.
        weights: Inverse-variance weight for each study (1/SE²).

    Returns:
        A :class:`QTestResult` with Q, df, p-value, I², and τ².

    Raises:
        ValueError: If ``effect_sizes`` and ``weights`` have different
            lengths or if fewer than two studies are provided.

    """
    if len(effect_sizes) != len(weights):
        raise ValueError("effect_sizes and weights must have equal length")
    k = len(effect_sizes)
    if k < 2:
        raise ValueError("At least two studies are required for the Q test")

    from scipy.stats import chi2  # type: ignore[import-untyped]

    df = k - 1
    q = _compute_q(effect_sizes, weights)
    p_value = float(chi2.sf(q, df))

    # I² = max(0, (Q - df) / Q * 100)
    i_squared = max(0.0, (q - df) / q * 100.0) if q > 0 else 0.0

    # DerSimonian-Laird τ² estimate
    c = sum(weights) - sum(w**2 for w in weights) / sum(weights)
    tau_squared = max(0.0, (q - df) / c) if c > 0 else 0.0

    return QTestResult(
        q_statistic=q,
        df=df,
        p_value=p_value,
        i_squared=i_squared,
        tau_squared=tau_squared,
    )


def fixed_effects_meta_analysis(
    effect_sizes: list[float],
    ses: list[float],
    ci: float = 0.95,
) -> MetaAnalysisResult:
    """Pool effect sizes using a fixed-effects inverse-variance model.

    Under the fixed-effects assumption all studies estimate a common true
    effect; differences between studies are attributed to sampling error
    only.  Weights are ``1/SE²``.

    Args:
        effect_sizes: Effect size estimate (e.g., log OR, SMD) per study.
        ses: Standard error of the effect size estimate per study.
        ci: Confidence level for the interval (default 0.95 → 95% CI).

    Returns:
        A :class:`MetaAnalysisResult` with the pooled estimate and
        heterogeneity statistics.

    Raises:
        ValueError: If ``effect_sizes`` and ``ses`` have different lengths
            or if fewer than two studies are provided.

    """
    if len(effect_sizes) != len(ses):
        raise ValueError("effect_sizes and ses must have equal length")
    if len(effect_sizes) < 2:
        raise ValueError("At least two studies are required for meta-analysis")

    from scipy.stats import norm  # type: ignore[import-untyped]

    weights = _compute_weights(ses, tau_squared=0.0)
    pooled = _pool_effect(effect_sizes, weights)
    pooled_se = math.sqrt(1.0 / sum(weights))
    ci_lower, ci_upper = _build_ci(pooled, pooled_se, ci)
    z = pooled / pooled_se if pooled_se > 0 else 0.0
    p_value = float(2.0 * norm.sf(abs(z)))

    q_test = compute_q_test(effect_sizes, weights)

    return MetaAnalysisResult(
        pooled_effect=pooled,
        se=pooled_se,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        z_score=z,
        p_value=p_value,
        model="fixed",
        q_test=q_test,
    )


def random_effects_meta_analysis(
    effect_sizes: list[float],
    ses: list[float],
    ci: float = 0.95,
) -> MetaAnalysisResult:
    """Pool effect sizes using a DerSimonian-Laird random-effects model.

    Under the random-effects assumption studies estimate different true
    effects drawn from a distribution with variance τ².  The τ² estimate
    from :func:`compute_q_test` is added to each study's variance before
    computing weights, shrinking extreme estimates toward the pooled mean.

    Args:
        effect_sizes: Effect size estimate (e.g., log OR, SMD) per study.
        ses: Standard error of the effect size estimate per study.
        ci: Confidence level for the interval (default 0.95 → 95% CI).

    Returns:
        A :class:`MetaAnalysisResult` with the pooled estimate and
        heterogeneity statistics.

    Raises:
        ValueError: If ``effect_sizes`` and ``ses`` have different lengths
            or if fewer than two studies are provided.

    """
    if len(effect_sizes) != len(ses):
        raise ValueError("effect_sizes and ses must have equal length")
    if len(effect_sizes) < 2:
        raise ValueError("At least two studies are required for meta-analysis")

    from scipy.stats import norm  # type: ignore[import-untyped]

    # Compute τ² using fixed-effects weights first (DerSimonian-Laird method)
    fixed_weights = _compute_weights(ses, tau_squared=0.0)
    q_test = compute_q_test(effect_sizes, fixed_weights)
    tau_squared = q_test.tau_squared

    # Re-weight with τ² incorporated
    re_weights = _compute_weights(ses, tau_squared=tau_squared)
    pooled = _pool_effect(effect_sizes, re_weights)
    pooled_se = math.sqrt(1.0 / sum(re_weights))
    ci_lower, ci_upper = _build_ci(pooled, pooled_se, ci)
    z = pooled / pooled_se if pooled_se > 0 else 0.0
    p_value = float(2.0 * norm.sf(abs(z)))

    return MetaAnalysisResult(
        pooled_effect=pooled,
        se=pooled_se,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        z_score=z,
        p_value=p_value,
        model="random",
        q_test=q_test,
    )
