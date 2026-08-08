"""Inter-rater agreement reporting in the generated SLR report.

Regression tests for the kappa half of G53. The platform computes and stores
Cohen's kappa (``inter_rater_service.compute_and_store_kappa``) but the report
generator never read it, so SEGRESS items 8 / 16a / 18 — which require both the
method of assessing agreement and the resulting statistics — went unsatisfied
while the number sat one join away.

SEGRESS is explicit that SE reviews report kappa where PRISMA leaves agreement
implicit; see docs/methodology/10-reporting-and-evaluation.md.
"""

from types import SimpleNamespace

from backend.services.slr_report_service import _build_inter_rater_agreement


def _record(
    *,
    kappa: float | None,
    phase: str,
    n_papers: int = 40,
    threshold_met: bool = True,
    undefined_reason: str | None = None,
) -> SimpleNamespace:
    """Build a stand-in for an InterRaterAgreementRecord row."""
    return SimpleNamespace(
        kappa_value=kappa,
        phase=phase,
        n_papers=n_papers,
        threshold_met=threshold_met,
        kappa_undefined_reason=undefined_reason,
    )


def test_reports_both_pre_and_post_discussion_kappa() -> None:
    """Both agreement phases appear, because the initial value must be reported.

    Reporting only the post-discussion figure would overstate agreement: the
    corpus requires the *initial* kappa precisely because discussion inflates it.
    """
    # Arrange
    records = [
        _record(kappa=0.52, phase="pre_discussion", threshold_met=False),
        _record(kappa=0.81, phase="post_discussion", threshold_met=True),
    ]

    # Act
    section = _build_inter_rater_agreement(records)

    # Assert
    assert "0.52" in section
    assert "0.81" in section
    assert "pre-discussion" in section.lower()
    assert "post-discussion" in section.lower()


def test_states_when_no_agreement_was_assessed() -> None:
    """Silence is not acceptable — absence of assessment must be stated explicitly.

    A report that simply omits the section is indistinguishable from one where
    agreement was measured and forgotten.
    """
    # Arrange / Act
    section = _build_inter_rater_agreement([])

    # Assert
    assert section
    assert "no inter-rater agreement" in section.lower()


def test_undefined_kappa_reports_its_reason_rather_than_a_number() -> None:
    """A null kappa carries a reason; it must not be rendered as 0.0.

    ``safe_cohen_kappa`` returns None on zero-variance input (e.g. every paper
    accepted). Printing that as 0.0 would report perfect disagreement where the
    truth is that the statistic is undefined.
    """
    # Arrange
    records = [
        _record(
            kappa=None,
            phase="pre_discussion",
            undefined_reason="All decisions identical; kappa undefined.",
        )
    ]

    # Act
    section = _build_inter_rater_agreement(records)

    # Assert
    assert "undefined" in section.lower()
    assert "All decisions identical" in section
    assert "0.0" not in section


def test_reports_the_number_of_papers_the_statistic_rests_on() -> None:
    """N must accompany kappa — the same coefficient over 8 papers means less."""
    # Arrange
    records = [_record(kappa=0.74, phase="post_discussion", n_papers=126)]

    # Act
    section = _build_inter_rater_agreement(records)

    # Assert
    assert "126" in section
