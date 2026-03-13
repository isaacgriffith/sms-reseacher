"""Visualization service: generates SVG charts from study extraction data."""

from __future__ import annotations

import io
from typing import Any


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
    fig.update_layout(title=title, showlegend=False, xaxis={"visible": False}, yaxis={"visible": False})
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


def generate_classification_charts(
    extractions: list[dict[str, Any]], chart_type: str
) -> str:
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
    return generate_bar_chart(counts, title=title, xlabel=chart_type.replace("_", " ").title(), ylabel="Count")


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
    for bar, count in zip(bars, counts):
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
