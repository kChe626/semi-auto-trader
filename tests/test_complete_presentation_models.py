from __future__ import annotations

from unittest.mock import Mock

from dashboard.complete_presentation_models import (
    CompleteDashboardViewModel,
)


def _build_view_model() -> CompleteDashboardViewModel:
    return CompleteDashboardViewModel(
        account=Mock(name="account"),
        scanner=Mock(name="scanner"),
        workflow=Mock(name="workflow"),
        analytics=Mock(name="analytics"),
        trade_history=Mock(
            name="trade-history"
        ),
    )


def test_complete_dashboard_stores_all_sections() -> None:
    account = Mock(name="account")
    scanner = Mock(name="scanner")
    workflow = Mock(name="workflow")
    analytics = Mock(name="analytics")
    trade_history = Mock(name="trade-history")

    view_model = CompleteDashboardViewModel(
        account=account,
        scanner=scanner,
        workflow=workflow,
        analytics=analytics,
        trade_history=trade_history,
    )

    assert view_model.account is account
    assert view_model.scanner is scanner
    assert view_model.workflow is workflow
    assert view_model.analytics is analytics
    assert view_model.trade_history is trade_history


def test_complete_dashboard_is_immutable() -> None:
    view_model = _build_view_model()

    try:
        view_model.workflow = Mock()
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "CompleteDashboardViewModel must be immutable"
        )