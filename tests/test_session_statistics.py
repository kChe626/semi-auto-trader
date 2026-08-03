from analytics.session_statistics import (
    SessionStatistics,
)


def test_counts_session_statuses() -> None:
    events = [
        {
            "status": "candidate_ranked",
        },
        {
            "status": "candidate_ranked",
        },
        {
            "status": "risk_filtered",
        },
        {
            "status": "preflight_passed",
        },
        {
            "status": "submitted_verified",
        },
    ]

    summary = SessionStatistics.calculate(
        events
    )

    assert summary.candidates_ranked == 2
    assert summary.risk_filtered == 1
    assert summary.preflight_passed == 1
    assert summary.submitted_verified == 1


def test_counts_execution_rejections() -> None:
    events = [
        {
            "status": "preflight_rejected",
        },
        {
            "status": "execution_disabled",
        },
        {
            "status": "user_cancelled",
        },
    ]

    summary = SessionStatistics.calculate(
        events
    )

    assert summary.preflight_rejected == 1
    assert summary.execution_disabled == 1
    assert summary.user_cancelled == 1


def test_empty_events_returns_zero_summary() -> None:
    summary = SessionStatistics.calculate(
        []
    )

    assert summary.candidates_ranked == 0
    assert summary.submitted_verified == 0
    assert summary.user_cancelled == 0


def test_unknown_statuses_are_ignored() -> None:
    events = [
        {
            "status": "something_new",
        },
        {
            "status": "candidate_ranked",
        },
    ]

    summary = SessionStatistics.calculate(
        events
    )

    assert summary.candidates_ranked == 1