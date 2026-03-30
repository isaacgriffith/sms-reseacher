"""Synthesis strategy implementations for SLR workflow (feature 007).

Provides the :class:`SynthesisStrategy` protocol and three concrete
implementations:

- :class:`MetaAnalysisSynthesizer` — quantitative pooling via fixed or
  random-effects meta-analysis with funnel plot.
- :class:`DescriptiveSynthesizer` — tabulated descriptive statistics with
  forest plot.
- :class:`QualitativeSynthesizer` — theme-to-paper mapping with optional
  sensitivity by paper exclusion.

All synthesizers accept user-supplied paper data via the ``parameters`` dict
so they are not coupled to a specific DB schema for the input data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from pydantic import BaseModel

from backend.core.config import get_settings
from backend.services import statistics, visualization
from backend.services.visualization import StudyPlotData

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


# ---------------------------------------------------------------------------
# Output model
# ---------------------------------------------------------------------------


class SynthesisOutput(BaseModel):
    """Results returned by every synthesis strategy.

    Attributes:
        computed_statistics: Pooled/tabulated numeric results keyed by name.
        forest_plot_svg: SVG string for a Forest plot (descriptive synthesis).
        funnel_plot_svg: SVG string for a Funnel plot (meta-analysis).
        qualitative_themes: Theme-to-paper mapping (qualitative synthesis).
        sensitivity_analysis: Subset re-run results keyed by subset name.

    """

    computed_statistics: dict[str, Any] | None = None
    forest_plot_svg: str | None = None
    funnel_plot_svg: str | None = None
    qualitative_themes: dict[str, Any] | None = None
    sensitivity_analysis: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------


class SynthesisStrategy(Protocol):
    """Typing protocol for synthesis strategy objects.

    All concrete synthesizers must implement the async ``run`` method with
    this signature so they can be dispatched interchangeably from the job.
    """

    async def run(
        self,
        study_id: int,
        parameters: dict[str, Any],
        db: AsyncSession,
    ) -> SynthesisOutput:
        """Execute the synthesis and return structured output.

        Args:
            study_id: FK of the study being synthesised.
            parameters: Caller-supplied configuration dict.
            db: Active async database session (may be used by subclasses to
                fetch additional study data).

        Returns:
            A :class:`SynthesisOutput` with all relevant fields populated.

        """
        ...


# ---------------------------------------------------------------------------
# Meta-analysis synthesizer
# ---------------------------------------------------------------------------


class MetaAnalysisSynthesizer:
    """Quantitative meta-analysis synthesis strategy.

    Accepts a list of paper dicts in ``parameters["papers"]`` and pools them
    using fixed or random-effects inverse-variance weighting.  A funnel plot
    is always generated.  Sensitivity analysis runs each named subset
    independently when ``parameters["subsets"]`` is provided.

    Example ``parameters`` structure::

        {
            "papers": [
                {"label": "Smith 2020", "effect_size": 0.4, "se": 0.1,
                 "ci_lower": 0.2, "ci_upper": 0.6, "weight": 1.0},
                ...
            ],
            "model_type": "auto",          # "fixed" | "random" | "auto"
            "heterogeneity_threshold": 0.1, # p-value cutoff for auto-select
            "confidence_interval": 0.95,
            "subsets": [                   # optional
                {"name": "Recent", "paper_indices": [0, 2]},
                ...
            ]
        }
    """

    async def run(
        self,
        study_id: int,
        parameters: dict[str, Any],
        db: AsyncSession,
    ) -> SynthesisOutput:
        """Run meta-analysis synthesis.

        Extracts effect sizes and standard errors from ``parameters["papers"]``,
        auto-selects or uses the specified model, pools effects, generates a
        funnel plot, and optionally runs sensitivity analyses on named subsets.

        Args:
            study_id: FK of the study (unused in the base implementation).
            parameters: Synthesis configuration (see class docstring).
            db: Active async database session.

        Returns:
            A :class:`SynthesisOutput` with ``computed_statistics``,
            ``funnel_plot_svg``, and optionally ``sensitivity_analysis``.

        Raises:
            ValueError: If fewer than two papers are supplied.

        """
        papers: list[dict[str, Any]] = parameters.get("papers", [])
        model_type: str = parameters.get("model_type", "auto")
        ci: float = float(parameters.get("confidence_interval", 0.95))
        het_threshold: float = float(parameters.get("heterogeneity_threshold", 0.1))

        effect_sizes = [float(p["effect_size"]) for p in papers]
        ses = [float(p["se"]) for p in papers]

        result = _run_meta(effect_sizes, ses, model_type, het_threshold, ci)

        plot_data = _build_plot_data(papers)
        pooled_point = StudyPlotData(
            label="Pooled",
            effect_size=result.pooled_effect,
            ci_lower=result.ci_lower,
            ci_upper=result.ci_upper,
        )
        funnel_svg = visualization.generate_funnel_plot(
            plot_data, pooled_point, title="Funnel Plot"
        )

        computed: dict[str, Any] = result.model_dump()

        sensitivity: dict[str, Any] | None = None
        subsets: list[dict[str, Any]] = parameters.get("subsets") or []
        if subsets:
            sensitivity = {}
            for subset in subsets:
                name: str = subset["name"]
                indices: list[int] = subset["paper_indices"]
                sub_papers = [papers[i] for i in indices if i < len(papers)]
                sub_es = [float(p["effect_size"]) for p in sub_papers]
                sub_ses = [float(p["se"]) for p in sub_papers]
                if len(sub_es) >= 2:
                    sub_result = _run_meta(sub_es, sub_ses, model_type, het_threshold, ci)
                    sensitivity[name] = sub_result.model_dump()
                else:
                    sensitivity[name] = {"error": "fewer than 2 papers in subset"}

        return SynthesisOutput(
            computed_statistics=computed,
            funnel_plot_svg=funnel_svg,
            sensitivity_analysis=sensitivity,
        )


# ---------------------------------------------------------------------------
# Descriptive synthesizer
# ---------------------------------------------------------------------------


class DescriptiveSynthesizer:
    """Descriptive synthesis strategy with tabulation and forest plot.

    Accepts a list of paper dicts in ``parameters["papers"]`` and renders a
    forest plot.  ``computed_statistics`` includes per-paper tabulation of
    sample sizes and effect sizes.

    Example ``parameters`` structure::

        {
            "papers": [
                {"label": "Jones 2019", "effect_size": 0.3,
                 "ci_lower": 0.1, "ci_upper": 0.5,
                 "weight": 1.0, "sample_size": 120, "unit": "SMD"},
                ...
            ],
            "subsets": [                   # optional
                {"name": "RCT only", "paper_indices": [0, 1]},
                ...
            ]
        }
    """

    async def run(
        self,
        study_id: int,
        parameters: dict[str, Any],
        db: AsyncSession,
    ) -> SynthesisOutput:
        """Run descriptive synthesis.

        Builds a forest plot from ``parameters["papers"]`` and tabulates
        sample sizes and effect sizes.  Raises ``ValueError`` when fewer
        papers are provided than ``settings.slr_min_synthesis_papers``.

        Args:
            study_id: FK of the study (unused in base implementation).
            parameters: Synthesis configuration (see class docstring).
            db: Active async database session.

        Returns:
            A :class:`SynthesisOutput` with ``computed_statistics``,
            ``forest_plot_svg``, and optionally ``sensitivity_analysis``.

        Raises:
            ValueError: If fewer than ``slr_min_synthesis_papers`` papers
                are supplied (propagated from
                :func:`visualization.generate_forest_plot`).

        """
        papers: list[dict[str, Any]] = parameters.get("papers", [])

        settings = get_settings()
        if len(papers) < settings.slr_min_synthesis_papers:
            raise ValueError(
                f"Forest plot requires at least "
                f"{settings.slr_min_synthesis_papers} studies; "
                f"got {len(papers)}"
            )

        plot_data = _build_plot_data(papers)
        # Pooled point for forest plot: use simple mean for descriptive
        all_es = [float(p["effect_size"]) for p in papers]
        mean_es = sum(all_es) / len(all_es)
        ci_vals = [float(p.get("ci_lower", 0.0)) for p in papers]
        ci_uppers = [float(p.get("ci_upper", 0.0)) for p in papers]
        pooled_point = StudyPlotData(
            label="Mean",
            effect_size=mean_es,
            ci_lower=min(ci_vals),
            ci_upper=max(ci_uppers),
        )
        forest_svg = visualization.generate_forest_plot(
            plot_data, pooled_point, title="Forest Plot"
        )

        computed: dict[str, Any] = {
            "n_papers": len(papers),
            "papers": [
                {
                    "label": p.get("label", ""),
                    "effect_size": float(p["effect_size"]),
                    "ci_lower": float(p.get("ci_lower", 0.0)),
                    "ci_upper": float(p.get("ci_upper", 0.0)),
                    "sample_size": p.get("sample_size"),
                    "unit": p.get("unit"),
                    "weight": float(p.get("weight", 1.0)),
                }
                for p in papers
            ],
        }

        sensitivity: dict[str, Any] | None = None
        subsets: list[dict[str, Any]] = parameters.get("subsets") or []
        if subsets:
            sensitivity = {}
            for subset in subsets:
                name: str = subset["name"]
                indices: list[int] = subset["paper_indices"]
                sub_papers = [papers[i] for i in indices if i < len(papers)]
                sensitivity[name] = {
                    "n_papers": len(sub_papers),
                    "effect_sizes": [float(p["effect_size"]) for p in sub_papers],
                }

        return SynthesisOutput(
            computed_statistics=computed,
            forest_plot_svg=forest_svg,
            sensitivity_analysis=sensitivity,
        )


# ---------------------------------------------------------------------------
# Qualitative synthesizer
# ---------------------------------------------------------------------------


class QualitativeSynthesizer:
    """Qualitative synthesis strategy using thematic mapping.

    Accepts a list of theme dicts in ``parameters["themes"]`` where each
    theme has a name and a list of paper IDs.  Paper IDs are accepted as-is
    (no DB validation).  Sensitivity can be performed by excluding the
    lowest-quality papers via ``parameters["exclude_paper_ids"]``.

    Example ``parameters`` structure::

        {
            "themes": [
                {"theme_name": "Usability", "paper_ids": [1, 3, 5]},
                {"theme_name": "Performance", "paper_ids": [2, 4]},
            ],
            "exclude_paper_ids": [5]     # optional
        }
    """

    async def run(
        self,
        study_id: int,
        parameters: dict[str, Any],
        db: AsyncSession,
    ) -> SynthesisOutput:
        """Run qualitative synthesis.

        Builds a theme-to-paper mapping from ``parameters["themes"]``.
        When ``parameters["exclude_paper_ids"]`` is provided, a sensitivity
        variant is stored with those paper IDs removed from every theme.

        Args:
            study_id: FK of the study (unused in base implementation).
            parameters: Synthesis configuration (see class docstring).
            db: Active async database session.

        Returns:
            A :class:`SynthesisOutput` with ``qualitative_themes`` and
            optionally ``sensitivity_analysis``.

        """
        themes: list[dict[str, Any]] = parameters.get("themes", [])

        theme_map: dict[str, list[int]] = {}
        for theme in themes:
            name: str = theme["theme_name"]
            paper_ids: list[int] = [int(pid) for pid in theme.get("paper_ids", [])]
            theme_map[name] = paper_ids

        qualitative: dict[str, Any] = {"themes": theme_map}

        sensitivity: dict[str, Any] | None = None
        exclude_ids: list[int] | None = parameters.get("exclude_paper_ids")
        if exclude_ids:
            exclude_set = {int(eid) for eid in exclude_ids}
            reduced: dict[str, list[int]] = {
                name: [pid for pid in pids if pid not in exclude_set]
                for name, pids in theme_map.items()
            }
            sensitivity = {
                "excluded_paper_ids": list(exclude_set),
                "themes": reduced,
            }

        return SynthesisOutput(
            qualitative_themes=qualitative,
            sensitivity_analysis=sensitivity,
        )


# ---------------------------------------------------------------------------
# Tertiary narrative synthesizer
# ---------------------------------------------------------------------------


class NarrativeSynthesisStrategy:
    """Narrative synthesis strategy for Tertiary Studies.

    Accepts a list of extraction dicts in ``parameters["extractions"]``,
    each representing a validated :class:`TertiaryDataExtraction` record for
    an included secondary study.  Uses the configured LLM to produce a
    narrative summary identifying convergent findings, divergent conclusions,
    and research gaps across the secondary studies.

    Example ``parameters`` structure::

        {
            "extractions": [
                {
                    "secondary_study_type": "SLR",
                    "research_questions_addressed": ["RQ1", "RQ2"],
                    "key_findings": "...",
                    "research_gaps": "...",
                    "synthesis_approach_used": "meta-analysis",
                    "study_period_start": 2015,
                    "study_period_end": 2022,
                },
                ...
            ]
        }
    """

    async def run(
        self,
        study_id: int,
        parameters: dict[str, Any],
        db: AsyncSession,
    ) -> SynthesisOutput:
        """Run LLM-assisted narrative synthesis over secondary-study extractions.

        Formats the extraction records as structured JSON for the LLM, requests a
        narrative paragraph identifying convergent findings, divergent conclusions,
        and research gaps, then returns the result in ``qualitative_themes``.

        Args:
            study_id: FK of the study being synthesised.
            parameters: Dict with ``"extractions"`` key containing extraction
                records as a list of dicts.
            db: Active async database session (unused by this strategy).

        Returns:
            A :class:`SynthesisOutput` with ``qualitative_themes`` populated
            as ``{"narrative": "<LLM-generated text>"}``.

        Raises:
            ValueError: If fewer than 2 extraction records are provided.

        """
        import json as _json

        extractions: list[dict[str, Any]] = parameters.get("extractions", [])
        if len(extractions) < 2:
            raise ValueError(
                "Narrative synthesis requires at least 2 extraction records; "
                f"got {len(extractions)}"
            )

        system_prompt = (
            "You are a systematic review expert performing a tertiary study narrative synthesis. "
            "Given a list of secondary study extraction records in JSON, write a concise "
            "narrative (3–5 paragraphs) that: "
            "(1) identifies convergent findings across the studies, "
            "(2) highlights divergent conclusions, "
            "(3) summarises key research gaps. "
            "Return only the narrative text — no JSON, no markdown fences."
        )
        user_content = _json.dumps(extractions, default=str)

        narrative_text = await _call_llm(system_prompt, user_content)

        return SynthesisOutput(
            qualitative_themes={"narrative": narrative_text},
        )


# ---------------------------------------------------------------------------
# Tertiary thematic analysis synthesizer
# ---------------------------------------------------------------------------


class ThematicAnalysisStrategy:
    """Thematic analysis synthesis strategy for Tertiary Studies.

    Accepts a list of extraction dicts in ``parameters["extractions"]`` and
    uses LLM-assisted clustering to group key findings and research gaps by
    theme.  Returns a theme-to-paper mapping in ``qualitative_themes``.

    Example ``parameters`` structure::

        {
            "extractions": [
                {
                    "secondary_study_type": "SMS",
                    "key_findings": "...",
                    "research_gaps": "...",
                },
                ...
            ]
        }
    """

    async def run(
        self,
        study_id: int,
        parameters: dict[str, Any],
        db: AsyncSession,
    ) -> SynthesisOutput:
        """Run LLM-assisted thematic clustering over secondary-study extractions.

        Formats the extraction records for the LLM and requests a JSON object
        mapping theme names to lists of zero-based extraction indices.

        Args:
            study_id: FK of the study being synthesised.
            parameters: Dict with ``"extractions"`` key containing extraction
                records as a list of dicts.
            db: Active async database session (unused by this strategy).

        Returns:
            A :class:`SynthesisOutput` with ``qualitative_themes`` populated
            as ``{"themes": {"<theme>": [<extraction_index>, ...], ...}}``.

        Raises:
            ValueError: If fewer than 2 extraction records are provided.

        """
        import json as _json

        extractions: list[dict[str, Any]] = parameters.get("extractions", [])
        if len(extractions) < 2:
            raise ValueError(
                f"Thematic analysis requires at least 2 extraction records; got {len(extractions)}"
            )

        system_prompt = (
            "You are a systematic review expert performing thematic analysis on tertiary "
            "study data. Given a JSON list of secondary study extraction records (each with "
            "key_findings and research_gaps), identify 3–7 recurring themes across the "
            "studies and return a JSON object where each key is a theme name and each value "
            "is a list of zero-based indices into the input list. "
            'Example: {"Theme A": [0, 2], "Theme B": [1, 3]}. '
            "Return only valid JSON — no prose, no markdown fences."
        )
        user_content = _json.dumps(extractions, default=str)

        raw_text = await _call_llm(system_prompt, user_content)

        # Strip optional markdown fences.
        raw_text = raw_text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        try:
            theme_map: dict[str, Any] = _json.loads(raw_text)
        except _json.JSONDecodeError:
            # Fallback: return the raw text as an unparsed result.
            theme_map = {"raw": raw_text}

        return SynthesisOutput(
            qualitative_themes={"themes": theme_map},
        )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


async def _call_llm(system_prompt: str, user_content: str) -> str:
    """Call the configured LLM and return the response text.

    Args:
        system_prompt: System role message text.
        user_content: User role message text.

    Returns:
        Raw text produced by the LLM.

    """
    from agents.core.llm_client import LLMClient  # local import to avoid circular

    client = LLMClient()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    return await client.complete(messages, max_tokens=1024)


def _build_plot_data(papers: list[dict[str, Any]]) -> list[StudyPlotData]:
    """Convert a list of paper dicts to :class:`StudyPlotData` objects.

    Args:
        papers: List of paper parameter dicts (must have ``label``,
            ``effect_size``, ``ci_lower``, ``ci_upper``, and optionally
            ``weight``).

    Returns:
        Ordered list of :class:`StudyPlotData` for plotting.

    """
    return [
        StudyPlotData(
            label=str(p.get("label", f"Study {i + 1}")),
            effect_size=float(p["effect_size"]),
            ci_lower=float(p.get("ci_lower", 0.0)),
            ci_upper=float(p.get("ci_upper", 0.0)),
            weight=float(p.get("weight", 1.0)),
        )
        for i, p in enumerate(papers)
    ]


def _run_meta(
    effect_sizes: list[float],
    ses: list[float],
    model_type: str,
    het_threshold: float,
    ci: float,
) -> statistics.MetaAnalysisResult:
    """Run fixed or random-effects meta-analysis with auto-selection.

    When ``model_type`` is ``"auto"``, the Q-test p-value is compared to
    ``het_threshold``.  A p-value below the threshold indicates significant
    heterogeneity, triggering random-effects; otherwise fixed-effects is used.

    Args:
        effect_sizes: Effect size estimates for each study.
        ses: Standard errors for each study.
        model_type: ``"fixed"``, ``"random"``, or ``"auto"``.
        het_threshold: P-value threshold for auto model selection.
        ci: Confidence interval level (e.g. 0.95).

    Returns:
        A :class:`statistics.MetaAnalysisResult` for the selected model.

    """
    if model_type == "auto":
        # Compute Q-test first with fixed weights to decide
        fixed_weights = [1.0 / se**2 for se in ses]
        q_result = statistics.compute_q_test(effect_sizes, fixed_weights)
        use_random = q_result.p_value < het_threshold
    else:
        use_random = model_type == "random"

    if use_random:
        return statistics.random_effects_meta_analysis(effect_sizes, ses, ci=ci)
    return statistics.fixed_effects_meta_analysis(effect_sizes, ses, ci=ci)
