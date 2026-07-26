from __future__ import annotations

from unittest.mock import Mock

from dashboard.complete_presentation_models import (
    CompleteDashboardViewModel,
)


def test_complete_dashboard_stores_all_sections() -> None:
    account = Mock(name="account")
    scanner = Mock(name="scanner")
    analytics = Mock(name="analytics")
    trade_history = Mock(name="trade-history")

    view_model = CompleteDashboardViewModel(
        account=account,
        scanner=scanner,
        analytics=analytics,
        trade_history=trade_history,
    )

    assert view_model.account is account
    assert view_model.scanner is scanner
    assert view_model.analytics is analytics
    assert view_model.trade_history is trade_history


def test_complete_dashboard_is_immutable() -> None:
    view_model = CompleteDashboardViewModel(
        account=Mock(),
        scanner=Mock(),
        analytics=Mock(),
        trade_history=Mock(),
    )

    try:
        view_model.scanner = Mock()
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "CompleteDashboardViewModel must be immutable"
        )