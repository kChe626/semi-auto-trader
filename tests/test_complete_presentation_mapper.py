from __future__ import annotations

from unittest.mock import Mock

import pytest

from dashboard.complete_presentation_mapper import (
    CompleteDashboardPresentationMapper,
)
from dashboard.complete_presentation_models import (
    CompleteDashboardViewModel,
)
from dashboard.composition_service import (
    CompleteDashboardData,
)


def make_mapper(
    *,
    account_mapper: Mock | None = None,
    scanner_mapper: Mock | None = None,
    workflow_mapper: Mock | None = None,
    analytics_mapper: Mock | None = None,
    trade_history_mapper: Mock | None = None,
) -> tuple[
    CompleteDashboardPresentationMapper,
    Mock,
    Mock,
    Mock,
    Mock,
    Mock,
]:
    account_mapper = account_mapper or Mock()
    scanner_mapper = scanner_mapper or Mock()
    workflow_mapper = workflow_mapper or Mock()
    analytics_mapper = analytics_mapper or Mock()
    trade_history_mapper = (
        trade_history_mapper or Mock()
    )

    mapper = CompleteDashboardPresentationMapper(
        account_mapper=account_mapper,
        scanner_mapper=scanner_mapper,
        workflow_mapper=workflow_mapper,
        analytics_mapper=analytics_mapper,
        trade_history_mapper=trade_history_mapper,
    )

    return (
        mapper,
        account_mapper,
        scanner_mapper,
        workflow_mapper,
        analytics_mapper,
        trade_history_mapper,
    )


def make_dashboard_data() -> CompleteDashboardData:
    analytics_data = Mock(name="analytics-data")
    analytics_data.closed_trades = (
        Mock(name="closed-trade"),
    )

    return CompleteDashboardData(
        account_data=Mock(name="account-data"),
        scanner_signals=(
            Mock(name="scanner-signal"),
        ),
        workflow_result=Mock(
            name="workflow-result"
        ),
        analytics_data=analytics_data,
    )


def test_map_dashboard_returns_complete_view_model() -> None:
    (
        mapper,
        account_mapper,
        scanner_mapper,
        workflow_mapper,
        analytics_mapper,
        trade_history_mapper,
    ) = make_mapper()

    account_view_model = Mock(
        name="account-view-model"
    )
    scanner_view_model = Mock(
        name="scanner-view-model"
    )
    workflow_view_model = Mock(
        name="workflow-view-model"
    )
    analytics_view_model = Mock(
        name="analytics-view-model"
    )
    trade_history_view_model = Mock(
        name="trade-history-view-model"
    )

    account_mapper.map_account_section.return_value = (
        account_view_model
    )
    scanner_mapper.map_scanner_section.return_value = (
        scanner_view_model
    )
    workflow_mapper.map.return_value = (
        workflow_view_model
    )
    analytics_mapper.map_analytics_section.return_value = (
        analytics_view_model
    )
    trade_history_mapper.map.return_value = (
        trade_history_view_model
    )

    result = mapper.map_dashboard(
        make_dashboard_data()
    )

    assert isinstance(
        result,
        CompleteDashboardViewModel,
    )
    assert result.account is account_view_model
    assert result.scanner is scanner_view_model
    assert result.workflow is workflow_view_model
    assert result.analytics is analytics_view_model
    assert (
        result.trade_history
        is trade_history_view_model
    )


def test_account_mapper_receives_account_data() -> None:
    (
        mapper,
        account_mapper,
        _,
        _,
        _,
        _,
    ) = make_mapper()

    dashboard_data = make_dashboard_data()

    mapper.map_dashboard(dashboard_data)

    account_mapper.map_account_section\
        .assert_called_once_with(
            dashboard_data.account_data
        )


def test_scanner_mapper_receives_scanner_signals() -> None:
    (
        mapper,
        _,
        scanner_mapper,
        _,
        _,
        _,
    ) = make_mapper()

    dashboard_data = make_dashboard_data()

    mapper.map_dashboard(dashboard_data)

    scanner_mapper.map_scanner_section\
        .assert_called_once_with(
            dashboard_data.scanner_signals
        )


def test_workflow_mapper_receives_workflow_result() -> None:
    (
        mapper,
        _,
        _,
        workflow_mapper,
        _,
        _,
    ) = make_mapper()

    dashboard_data = make_dashboard_data()

    mapper.map_dashboard(dashboard_data)

    workflow_mapper.map.assert_called_once_with(
        dashboard_data.workflow_result
    )


def test_analytics_mapper_receives_analytics_data() -> None:
    (
        mapper,
        _,
        _,
        _,
        analytics_mapper,
        _,
    ) = make_mapper()

    dashboard_data = make_dashboard_data()

    mapper.map_dashboard(dashboard_data)

    analytics_mapper.map_analytics_section\
        .assert_called_once_with(
            dashboard_data.analytics_data
        )


def test_trade_history_mapper_receives_closed_trades() -> None:
    (
        mapper,
        _,
        _,
        _,
        _,
        trade_history_mapper,
    ) = make_mapper()

    dashboard_data = make_dashboard_data()

    mapper.map_dashboard(dashboard_data)

    trade_history_mapper.map.assert_called_once_with(
        dashboard_data.analytics_data.closed_trades
    )


def test_sections_are_mapped_in_expected_order() -> None:
    calls: list[str] = []

    account_mapper = Mock()
    scanner_mapper = Mock()
    workflow_mapper = Mock()
    analytics_mapper = Mock()
    trade_history_mapper = Mock()

    account_mapper.map_account_section.side_effect = (
        lambda _: calls.append("account") or Mock()
    )

    scanner_mapper.map_scanner_section.side_effect = (
        lambda _: calls.append("scanner") or Mock()
    )

    workflow_mapper.map.side_effect = (
        lambda _: calls.append("workflow") or Mock()
    )

    analytics_mapper.map_analytics_section.side_effect = (
        lambda _: calls.append("analytics") or Mock()
    )

    trade_history_mapper.map.side_effect = (
        lambda _: calls.append("trade-history")
        or Mock()
    )

    mapper = CompleteDashboardPresentationMapper(
        account_mapper=account_mapper,
        scanner_mapper=scanner_mapper,
        workflow_mapper=workflow_mapper,
        analytics_mapper=analytics_mapper,
        trade_history_mapper=trade_history_mapper,
    )

    mapper.map_dashboard(
        make_dashboard_data()
    )

    assert calls == [
        "account",
        "scanner",
        "workflow",
        "analytics",
        "trade-history",
    ]


def test_account_mapper_exception_is_not_hidden() -> None:
    (
        mapper,
        account_mapper,
        scanner_mapper,
        workflow_mapper,
        analytics_mapper,
        trade_history_mapper,
    ) = make_mapper()

    account_mapper.map_account_section.side_effect = (
        RuntimeError("account mapping failed")
    )

    with pytest.raises(
        RuntimeError,
        match="account mapping failed",
    ):
        mapper.map_dashboard(
            make_dashboard_data()
        )

    scanner_mapper.map_scanner_section\
        .assert_not_called()

    workflow_mapper.map.assert_not_called()

    analytics_mapper.map_analytics_section\
        .assert_not_called()

    trade_history_mapper.map.assert_not_called()


def test_scanner_mapper_exception_is_not_hidden() -> None:
    (
        mapper,
        account_mapper,
        scanner_mapper,
        workflow_mapper,
        analytics_mapper,
        trade_history_mapper,
    ) = make_mapper()

    account_mapper.map_account_section.return_value = (
        Mock()
    )

    scanner_mapper.map_scanner_section.side_effect = (
        RuntimeError("scanner mapping failed")
    )

    with pytest.raises(
        RuntimeError,
        match="scanner mapping failed",
    ):
        mapper.map_dashboard(
            make_dashboard_data()
        )

    account_mapper.map_account_section\
        .assert_called_once()

    workflow_mapper.map.assert_not_called()

    analytics_mapper.map_analytics_section\
        .assert_not_called()

    trade_history_mapper.map.assert_not_called()


def test_workflow_mapper_exception_is_not_hidden() -> None:
    (
        mapper,
        account_mapper,
        scanner_mapper,
        workflow_mapper,
        analytics_mapper,
        trade_history_mapper,
    ) = make_mapper()

    account_mapper.map_account_section.return_value = (
        Mock()
    )
    scanner_mapper.map_scanner_section.return_value = (
        Mock()
    )
    workflow_mapper.map.side_effect = RuntimeError(
        "workflow mapping failed"
    )

    with pytest.raises(
        RuntimeError,
        match="workflow mapping failed",
    ):
        mapper.map_dashboard(
            make_dashboard_data()
        )

    account_mapper.map_account_section\
        .assert_called_once()

    scanner_mapper.map_scanner_section\
        .assert_called_once()

    analytics_mapper.map_analytics_section\
        .assert_not_called()

    trade_history_mapper.map.assert_not_called()


def test_analytics_mapper_exception_is_not_hidden() -> None:
    (
        mapper,
        account_mapper,
        scanner_mapper,
        workflow_mapper,
        analytics_mapper,
        trade_history_mapper,
    ) = make_mapper()

    account_mapper.map_account_section.return_value = (
        Mock()
    )
    scanner_mapper.map_scanner_section.return_value = (
        Mock()
    )
    workflow_mapper.map.return_value = Mock()
    analytics_mapper.map_analytics_section.side_effect = (
        RuntimeError("analytics mapping failed")
    )

    with pytest.raises(
        RuntimeError,
        match="analytics mapping failed",
    ):
        mapper.map_dashboard(
            make_dashboard_data()
        )

    account_mapper.map_account_section\
        .assert_called_once()

    scanner_mapper.map_scanner_section\
        .assert_called_once()

    workflow_mapper.map.assert_called_once()

    trade_history_mapper.map.assert_not_called()


def test_trade_history_mapper_exception_is_not_hidden() -> None:
    (
        mapper,
        account_mapper,
        scanner_mapper,
        workflow_mapper,
        analytics_mapper,
        trade_history_mapper,
    ) = make_mapper()

    account_mapper.map_account_section.return_value = (
        Mock()
    )
    scanner_mapper.map_scanner_section.return_value = (
        Mock()
    )
    workflow_mapper.map.return_value = Mock()
    analytics_mapper.map_analytics_section.return_value = (
        Mock()
    )
    trade_history_mapper.map.side_effect = (
        RuntimeError(
            "trade history mapping failed"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="trade history mapping failed",
    ):
        mapper.map_dashboard(
            make_dashboard_data()
        )

    account_mapper.map_account_section\
        .assert_called_once()

    scanner_mapper.map_scanner_section\
        .assert_called_once()

    workflow_mapper.map.assert_called_once()

    analytics_mapper.map_analytics_section\
        .assert_called_once()


def test_each_mapping_returns_new_view_model() -> None:
    (
        mapper,
        account_mapper,
        scanner_mapper,
        workflow_mapper,
        analytics_mapper,
        trade_history_mapper,
    ) = make_mapper()

    account_mapper.map_account_section.return_value = (
        Mock()
    )
    scanner_mapper.map_scanner_section.return_value = (
        Mock()
    )
    workflow_mapper.map.return_value = Mock()
    analytics_mapper.map_analytics_section.return_value = (
        Mock()
    )
    trade_history_mapper.map.return_value = (
        Mock()
    )

    dashboard_data = make_dashboard_data()

    first_result = mapper.map_dashboard(
        dashboard_data
    )
    second_result = mapper.map_dashboard(
        dashboard_data
    )

    assert first_result is not second_result

    assert (
        account_mapper
        .map_account_section
        .call_count
        == 2
    )

    assert (
        scanner_mapper
        .map_scanner_section
        .call_count
        == 2
    )

    assert workflow_mapper.map.call_count == 2

    assert (
        analytics_mapper
        .map_analytics_section
        .call_count
        == 2
    )

    assert (
        trade_history_mapper
        .map
        .call_count
        == 2
    )