"""Root conftest: enforce reason= on all skip/xfail markers.

Applied to every pytest session that collects from the workspace root,
ensuring no test is silently skipped without a documented justification.
"""

import pytest


def pytest_collection_finish(session: pytest.Session) -> None:
    """Fail the session if any skip or xfail marker lacks a non-empty reason.

    Args:
        session: The pytest session whose items have been fully collected.
    """
    violations: list[str] = []
    for item in session.items:
        for marker_name in ("skip", "xfail"):
            marker = item.get_closest_marker(marker_name)
            if marker is None:
                continue
            reason = marker.kwargs.get("reason", "") or (
                marker.args[0] if marker.args else ""
            )
            if not str(reason).strip():
                violations.append(
                    f"{item.nodeid}: @pytest.mark.{marker_name} missing reason="
                )
    if violations:
        pytest.fail(
            "The following markers are missing a reason=:\n"
            + "\n".join(f"  {v}" for v in violations),
            pytrace=False,
        )
