"""Visualization service: generates SVG charts from study extraction data."""

from __future__ import annotations

import io
from typing import Any

from backend.core.config import get_settings


def generate_bar_chart(
    data: dict[str, int | float],
    title: str,
    xlabel: str,
    ylabel: str,
) -> str:
    """Render a bar chart as an SVG string using matplotlib.

    Args:
        data: Mapping of category labels to numeric values.
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.

    Returns:
        A UTF-8 SVG string containing the rendered bar chart.

    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4))
    labels = list(data.keys())
    values = list(data.values())
    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    buf = io.StringIO()
    fig.savefig(buf, format="svg")
    plt.close(fig)
    return buf.getvalue()


def generate_bubble_chart(items: list[dict[str, Any]], title: str) -> str:
    """Render a bubble chart as an SVG string using plotly + kaleido.

    Each item must have ``label`` (str) and ``value`` (numeric) keys.
    Bubble size is proportional to ``value``.

    Args:
        items: List of dicts with ``label`` and ``value`` keys.
        title: Chart title.

    Returns:
        A UTF-8 SVG string containing the rendered bubble chart.

    """
    import plotly.graph_objects as go

    labels = [item["label"] for item in items]
    values = [item["value"] for item in items]
    fig = go.Figure(
        go.Scatter(
            x=list(range(len(labels))),
            y=[0] * len(labels),
            mode="markers+text",
            marker={"size": [max(10, v * 3) for v in values], "sizemode": "diameter"},
            text=labels,
            textposition="top center",
        )
    )
    fig.update_layout(
        title=title, showlegend=False, xaxis={"visible": False}, yaxis={"visible": False}
    )
    return fig.to_image(format="svg").decode("utf-8")


def _build_classification_data(
    extractions: list[dict[str, Any]], chart_type: str
) -> dict[str, int]:
    """Aggregate extraction data into a count mapping for a given chart type.

    Args:
        extractions: List of extraction dicts (each with fields matching
            DataExtraction columns: ``research_type``, ``venue_type``,
            ``venue_name``, ``author_details``, ``keywords``).
        chart_type: One of ``venue``, ``author``, ``locale``, ``institution``,
            ``year``, ``subtopic``, ``research_type``, ``research_method``.

    Returns:
        A dict mapping category label → count, sorted descending by count.

    """
    counts: dict[str, int] = {}

    for ext in extractions:
        if chart_type == "venue":
            key = ext.get("venue_name") or ext.get("venue_type") or "Unknown"
            counts[key] = counts.get(key, 0) + 1

        elif chart_type == "research_type":
            key = ext.get("research_type") or "unknown"
            counts[key] = counts.get(key, 0) + 1

        elif chart_type == "research_method":
            key = ext.get("venue_type") or "other"
            counts[key] = counts.get(key, 0) + 1

        elif chart_type == "author":
            for author in ext.get("author_details") or []:
                key = author.get("name") or "Unknown"
                counts[key] = counts.get(key, 0) + 1

        elif chart_type == "locale":
            for author in ext.get("author_details") or []:
                key = author.get("locale") or "Unknown"
                counts[key] = counts.get(key, 0) + 1

        elif chart_type == "institution":
            for author in ext.get("author_details") or []:
                key = author.get("institution") or "Unknown"
                counts[key] = counts.get(key, 0) + 1

        elif chart_type == "subtopic":
            for kw in ext.get("keywords") or []:
                counts[kw] = counts.get(kw, 0) + 1

        elif chart_type == "year":
            key = str(ext.get("year") or "Unknown")
            counts[key] = counts.get(key, 0) + 1

    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))


def generate_classification_charts(extractions: list[dict[str, Any]], chart_type: str) -> str:
    """Render a classification chart for one chart_type as an SVG string.

    Supports: venue, author, locale, institution, year, subtopic,
    research_type, research_method.

    Args:
        extractions: List of extraction dicts (DataExtraction column values).
        chart_type: Classification dimension to chart.

    Returns:
        A UTF-8 SVG string containing the rendered bar chart.

    """
    counts = _build_classification_data(extractions, chart_type)
    title_map = {
        "venue": "Papers by Venue",
        "author": "Papers by Author",
        "locale": "Papers by Author Locale",
        "institution": "Papers by Institution",
        "year": "Papers by Year",
        "subtopic": "Papers by Subtopic / Keyword",
        "research_type": "Papers by Research Type",
        "research_method": "Papers by Research Method",
    }
    title = title_map.get(chart_type, chart_type.replace("_", " ").title())
    return generate_bar_chart(
        counts, title=title, xlabel=chart_type.replace("_", " ").title(), ylabel="Count"
    )


def generate_frequency_infographic(year_counts: dict[str, int]) -> str:
    """Render a publication-frequency infographic as an SVG string.

    Displays a styled bar chart of publications per year suitable for
    inclusion in a systematic mapping study report.

    Args:
        year_counts: Mapping of year label (str) to paper count (int),
            e.g. ``{"2019": 5, "2020": 12, "2021": 8}``.

    Returns:
        A UTF-8 SVG string containing the rendered infographic.

    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    years = sorted(year_counts.keys())
    counts = [year_counts[y] for y in years]

    bars = ax.bar(years, counts, color="#4C72B0", edgecolor="white", linewidth=0.8)
    for bar, count in zip(bars, counts, strict=False):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.2,
            str(count),
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_title("Publication Frequency by Year", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Papers")
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    buf = io.StringIO()
    fig.savefig(buf, format="svg")
    plt.close(fig)
    return buf.getvalue()


class StudyPlotData:
    """Data for one study in a Forest or Funnel plot.

    Attributes:
        label: Study label shown on the plot y-axis.
        effect_size: Point estimate of the effect size.
        ci_lower: Lower bound of the confidence interval.
        ci_upper: Upper bound of the confidence interval.
        weight: Relative weight of the study (used for marker size).

    """

    def __init__(
        self,
        label: str,
        effect_size: float,
        ci_lower: float,
        ci_upper: float,
        weight: float = 1.0,
    ) -> None:
        """Initialise study plot data.

        Args:
            label: Study label shown on the plot y-axis.
            effect_size: Point estimate of the effect size.
            ci_lower: Lower bound of the confidence interval.
            ci_upper: Upper bound of the confidence interval.
            weight: Relative study weight (used for marker size scaling).

        """
        self.label = label
        self.effect_size = effect_size
        self.ci_lower = ci_lower
        self.ci_upper = ci_upper
        self.weight = weight


def generate_forest_plot(
    studies: list[StudyPlotData],
    pooled_estimate: StudyPlotData,
    title: str,
) -> str:
    """Render a Forest plot as an SVG string.

    Displays individual study effect sizes with confidence intervals and the
    pooled estimate as a diamond.  Raises ``ValueError`` when fewer studies
    are provided than the ``SLR_MIN_SYNTHESIS_PAPERS`` configuration setting
    because a Forest plot with too few data points is statistically meaningless.

    Args:
        studies: Per-study effect size data ordered as they should appear
            on the y-axis (bottom to top in traditional Forest plot order).
        pooled_estimate: Pooled effect size shown as a diamond at the bottom.
        title: Plot title rendered at the top of the figure.

    Returns:
        A UTF-8 SVG string containing the rendered Forest plot.

    Raises:
        ValueError: If ``len(studies)`` is less than
            ``settings.slr_min_synthesis_papers``.

    """
    settings = get_settings()
    if len(studies) < settings.slr_min_synthesis_papers:
        raise ValueError(
            f"Forest plot requires at least {settings.slr_min_synthesis_papers} studies; "
            f"got {len(studies)}"
        )

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(studies)
    fig_height = max(4.0, 1.0 + 0.5 * n)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    y_positions = list(range(n, 0, -1))  # top study at highest y

    for _i, (study, y) in enumerate(zip(studies, y_positions, strict=True)):
        marker_size = max(4.0, study.weight * 8.0)
        ax.plot(study.effect_size, y, "s", color="#4C72B0", markersize=marker_size)
        ax.plot(
            [study.ci_lower, study.ci_upper],
            [y, y],
            "-",
            color="#4C72B0",
            linewidth=1.0,
        )
        ax.text(
            ax.get_xlim()[0] if ax.get_xlim()[0] != 0 else -2.0,
            y,
            study.label,
            va="center",
            ha="right",
            fontsize=8,
        )

    # Pooled diamond at y=0
    diamond_x = [
        pooled_estimate.ci_lower,
        pooled_estimate.effect_size,
        pooled_estimate.ci_upper,
        pooled_estimate.effect_size,
        pooled_estimate.ci_lower,
    ]
    diamond_y = [0.0, 0.3, 0.0, -0.3, 0.0]
    ax.fill(diamond_x, diamond_y, color="#DD8452", zorder=3)

    ax.axvline(x=0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Effect Size")
    ax.set_yticks([])
    ax.spines[["top", "right", "left"]].set_visible(False)
    plt.tight_layout()

    buf = io.StringIO()
    fig.savefig(buf, format="svg")
    plt.close(fig)
    return buf.getvalue()


def generate_funnel_plot(
    studies: list[StudyPlotData],
    pooled_estimate: StudyPlotData,
    title: str,
) -> str:
    """Render a Funnel plot as an SVG string.

    A Funnel plot charts each study's effect size against its standard error
    (inverted y-axis so larger, more precise studies appear at the top).  A
    symmetric funnel envelope around the pooled estimate is drawn at ±1.96 SE.
    Asymmetry in the scatter indicates potential publication bias.

    Args:
        studies: Per-study effect size data.  ``ci_lower`` and ``ci_upper``
            are used to derive each study's standard error
            (SE = (ci_upper - ci_lower) / (2 × 1.96)).
        pooled_estimate: Pooled effect size used to centre the funnel envelope.
        title: Plot title rendered at the top of the figure.

    Returns:
        A UTF-8 SVG string containing the rendered Funnel plot.

    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np  # type: ignore[import-untyped]

    ses = [(s.ci_upper - s.ci_lower) / (2.0 * 1.96) for s in studies]
    effect_sizes = [s.effect_size for s in studies]

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(effect_sizes, ses, color="#4C72B0", s=40, zorder=3, label="Studies")

    # Funnel envelope: SE_range × 1.96 from pooled estimate
    se_max = max(ses) * 1.1 if ses else 1.0
    se_range = np.linspace(0, se_max, 200)
    ax.plot(
        pooled_estimate.effect_size + 1.96 * se_range,
        se_range,
        "--",
        color="#DD8452",
        linewidth=1.0,
        label="95% CI envelope",
    )
    ax.plot(
        pooled_estimate.effect_size - 1.96 * se_range,
        se_range,
        "--",
        color="#DD8452",
        linewidth=1.0,
    )

    ax.axvline(x=pooled_estimate.effect_size, color="gray", linestyle="--", linewidth=0.8)
    ax.invert_yaxis()
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Effect Size")
    ax.set_ylabel("Standard Error")
    ax.legend(fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    buf = io.StringIO()
    fig.savefig(buf, format="svg")
    plt.close(fig)
    return buf.getvalue()
