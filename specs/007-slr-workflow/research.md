# Research: SLR Workflow (007)

**Branch**: `007-slr-workflow` | **Date**: 2026-03-18

---

## 1. Cohen's Kappa for Inter-Rater Agreement

### Decision
Use `sklearn.metrics.cohen_kappa_score` (scikit-learn) as the primary Kappa implementation; add `scikit-learn>=1.5` to `backend/pyproject.toml`.

### Rationale
- scikit-learn's `cohen_kappa_score` handles zero-variance edge cases gracefully (returns NaN rather than raising) and supports multiclass (>2 categories, e.g., accepted/rejected/duplicate).
- scipy has no built-in Kappa function; implementing from the raw formula is error-prone at edge cases.
- numpy/scipy are already added as part of this feature, so scikit-learn adds minimal overhead.

### Edge Cases Handled
- **Zero-variance distribution** (one rater assigns all papers to the same category): κ is undefined. The service layer must detect this and return `None` with a human-readable warning rather than propagating NaN to the API.
- **Prevalence paradox** (very imbalanced categories): Standard κ can be misleadingly low. Document this limitation in the UI; do not substitute Gwet's AC1 at this time (YAGNI — not required by spec).
- **Fleiss' κ (>2 raters)**: Out of scope for the initial implementation. The spec requires calculation between *pairs* of reviewers only.

### Alternatives Considered
- `statsmodels.stats.inter_rater.cohen_kappa`: Heavier dependency, adds Fleiss' κ and Gwet's AC1. Deferred — spec requires only pairwise Cohen's Kappa.
- Pure formula implementation: Fragile at edge cases; not worth the maintenance burden when scikit-learn is production-quality.

---

## 2. Meta-Analysis Statistics

### Decision
Implement fixed-effects (inverse-variance) and random-effects (DerSimonian-Laird) meta-analysis as in-house pure NumPy/SciPy functions in `backend/src/backend/services/statistics.py`. Add `scipy>=1.13` and `numpy>=1.26` to `backend/pyproject.toml`.

### Rationale
- `scipy.stats.chi2.sf()` provides the Q-test p-value (one line); `scipy.stats.norm.ppf()` provides the z-critical value for confidence intervals. All other computations are NumPy array arithmetic following the DerSimonian-Laird formulas.
- `pymare` is unmaintained (last commit 2019). `statsmodels` meta-analysis module is sparse and poorly documented. In-house implementation gives full control, type safety via Pydantic, and zero hidden behaviour.
- Approximately 80–120 lines of well-tested pure functions; not a maintenance burden.

### Key Formulas

**Fixed-effects pooled effect**: `θ̂ = Σ(w_i × θ_i) / Σ(w_i)` where `w_i = 1/SE_i²`

**Cochran's Q**: `Q = Σ w_i(θ_i - θ̂)²`; p-value: `scipy.stats.chi2.sf(Q, df=k-1)`

**DerSimonian-Laird τ²**: `τ² = max(0, (Q - (k-1)) / c)` where `c = Σw_i - Σw_i²/Σw_i`

**Random-effects pooled effect**: same formula as fixed-effects but with `w'_i = 1/(SE_i² + τ²)`

**I² heterogeneity**: `I² = max(0, (Q - (k-1)) / Q)` — reported alongside Q and τ²

### Heterogeneity → Model Selection Gate
The system automatically suggests a model: if `Q p-value > 0.10` → fixed-effects; if `Q p-value ≤ 0.10` → random-effects. The researcher may override with a recorded justification. This avoids a type-switching if-chain: the model selection is passed as a strategy to `MetaAnalysisSynthesizer`.

### Alternatives Considered
- `pymare`: Unmaintained; rejected.
- `statsmodels.stats.meta`: Sparse documentation, not production-tested for Python 3.14; deferred.

---

## 3. Forest Plot and Funnel Plot (Matplotlib)

### Decision
Implement `generate_forest_plot()` and `generate_funnel_plot()` in `backend/src/backend/services/visualization.py` using the existing matplotlib Agg/SVG pattern (matching `generate_bar_chart` and `generate_bubble_chart`).

### Forest Plot
- **Y-axis**: Study labels; `ax.invert_yaxis()` for top-to-bottom reading order.
- **Markers**: `ax.scatter(effect, y, s=weight*scale, marker='s')` — square markers sized proportionally to study weight.
- **CI lines**: `ax.hlines(y, ci_lower, ci_upper, linewidth=2)`.
- **Null effect line**: `ax.axvline(0, linestyle='--', color='#999')`.
- **Pooled diamond**: `matplotlib.patches.Polygon` with vertices at `(pooled_lower, y_bottom), (pooled, y_top), (pooled_upper, y_bottom), (pooled, y_min)`.
- **Minimum studies gate**: Raise `ValueError` if fewer than 3 studies provided (per SC-004).

### Funnel Plot
- **X-axis**: Effect size; **Y-axis**: Standard error (increasing downward via `ax.invert_yaxis()`).
- **Study points**: `ax.scatter(effect_sizes, ses, alpha=0.6)`.
- **Funnel envelope**: `np.linspace(0, max_se, 100)` → `x_upper/lower = pooled ± 1.96*se_range`; drawn with `ax.fill_between(..., alpha=0.15)`.
- **Pooled line**: `ax.axvline(pooled_estimate, color='red', linestyle='--')`.

### Alternatives Considered
- plotly interactive charts: Not suitable for SVG-serialised storage and PDF export; deferred to a future interactive UI enhancement.

---

## 4. Protocol Review Agent

### Decision
Implement `ProtocolReviewerAgent` in `agents/src/agents/services/protocol_reviewer.py` following the exact same pattern as `ScreenerAgent` and `SynthesiserAgent`: Jinja2 prompt templates, `LLMClient`, `ProviderConfig` injection.

### Prompt Template Location
`agents/src/agents/prompts/protocol_reviewer/system.md` + `user.md.j2`

The user template receives the full protocol fields (background, RQs, PICO(C), search strategy, inclusion/exclusion criteria, checklist definitions, synthesis approach) as Jinja2 variables and instructs the agent to evaluate:
1. Internal consistency (RQs align with PICO(C))
2. Completeness (all mandatory sections present)
3. Feasibility (search strategy matches declared databases)
4. Quality checklist alignment (checklist items trace to RQs)

The agent returns a structured JSON response parsed into a `ProtocolReviewResult` Pydantic model with a list of `ProtocolIssue` objects (section, severity, description, suggestion).

### ARQ Job
`backend/src/backend/jobs/protocol_review_job.py` — enqueues the agent call asynchronously; updates `ReviewProtocol.review_status` and stores the JSON report in `ReviewProtocol.review_report`.

---

## 5. Phase Gate Extension Strategy

### Decision
Create a separate `backend/src/backend/services/slr_phase_gate.py` that extends the existing `phase_gate.py` logic for SLR-type studies, following the Open-Closed Principle. The existing `get_unlocked_phases()` function is unchanged; the router calls `get_slr_unlocked_phases()` when `study.study_type == "systematic_literature_review"`.

### SLR Phase Gates
| Phase | Gate Condition |
|-------|---------------|
| Phase 2 (Search) | `ReviewProtocol.status == "validated"` |
| Phase 3 (QA) | At least one `SearchExecution` with `status=COMPLETED` |
| Phase 4 (Synthesis) | All accepted papers have at least one completed `QualityAssessmentScore` per assigned reviewer |
| Phase 5 (Report) | At least one `SynthesisResult` with `status=completed` for the study |

---

## 6. New Dependencies Summary

| Package | Version | Added To | Reason |
|---------|---------|----------|--------|
| `scipy` | `>=1.13` | `sms-backend` | chi2.sf for Q-test, norm.ppf for meta-analysis CIs |
| `scikit-learn` | `>=1.5` | `sms-backend` | `cohen_kappa_score` |
| `numpy` | `>=1.26` | `sms-backend` | Array arithmetic for statistics (explicit pin) |

No new dependencies required for `agents`, `db`, or `frontend` packages.
