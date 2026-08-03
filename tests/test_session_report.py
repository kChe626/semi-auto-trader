from analytics.session_report import (
    format_session_report,
)

from analytics.session_statistics import (
    SessionSummary,
)


def test_formats_session_report() -> None:
    summary = SessionSummary(
        candidates_ranked=5,
        risk_filtered=2,
        preflight_passed=3,
        preflight_rejected=1,
        execution_disabled=0,
        user_cancelled=1,
        submitted_verified=2,
    )

    report = format_session_report(
        summary
    )

    assert "TRADING SESSION REPORT" in report
    assert "Candidates Ranked: 5" in report
    assert "Submitted Verified: 2" in report
    assert "User Cancelled: 1" in report