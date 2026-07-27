from unittest.mock import Mock

import pytest

from dashboard.composition_service import (
    CompleteDashboardData,
    DashboardCompositionService,
)
from models.trade_signal import TradeSignal


ACCOUNT_EQUITY = 100_000.00


def make_account_data() -> Mock:
    account_data = Mock(name="account-data")
    account_data.account.equity = ACCOUNT_EQUITY

    return account_data


def make_signal(
    symbol: str = "NVDA",
) -> TradeSignal:
    return TradeSignal(
        symbol=symbol,
        signal_type="BUY",
        price=100.00,
        reason="Bullish crossover",
        atr=2.00,
        rsi=55.00,
        short_sma=101.00,
        long_sma=99.00,
    )


def make_service(
    *,
    account_service: Mock | None = None,
    scanner_loader: Mock | None = None,
    trade_workflow: Mock | None = None,
    analytics_service: Mock | None = None,
) -> tuple[
    DashboardCompositionService,
    Mock,
    Mock,
    Mock,
    Mock,
]:
    account_service = account_service or Mock()
    scanner_loader = scanner_loader or Mock()
    trade_workflow = trade_workflow or Mock()
    analytics_service = analytics_service or Mock()

    account_service.load_account_data.return_value = (
        make_account_data()
    )

    scanner_loader.return_value = [
        make_signal(),
    ]

    trade_workflow.prepare_trade.return_value = (
        Mock(name="workflow-result")
    )

    analytics_service.load_dashboard_data.return_value = (
        Mock(name="analytics-data")
    )

    service = DashboardCompositionService(
        account_service=account_service,
        scanner_loader=scanner_loader,
        trade_workflow=trade_workflow,
        analytics_service=analytics_service,
    )

    return (
        service,
        account_service,
        scanner_loader,
        trade_workflow,
        analytics_service,
    )


def test_load_complete_dashboard_data_returns_snapshot() -> None:
    (
        service,
        account_service,
        scanner_loader,
        trade_workflow,
        analytics_service,
    ) = make_service()

    account_data = make_account_data()
    scanner_signals = [
        make_signal("NVDA"),
        make_signal("AAPL"),
    ]
    workflow_result = Mock(name="workflow-result")
    analytics_data = Mock(name="analytics-data")

    account_service.load_account_data.return_value = (
        account_data
    )
    scanner_loader.return_value = scanner_signals
    trade_workflow.prepare_trade.return_value = (
        workflow_result
    )
    analytics_service.load_dashboard_data.return_value = (
        analytics_data
    )

    result = service.load_complete_dashboard_data()

    assert isinstance(result, CompleteDashboardData)
    assert result.account_data is account_data
    assert result.scanner_signals == tuple(
        scanner_signals
    )
    assert result.workflow_result is workflow_result
    assert result.analytics_data is analytics_data


def test_account_service_is_called_once() -> None:
    (
        service,
        account_service,
        _,
        _,
        _,
    ) = make_service()

    service.load_complete_dashboard_data()

    account_service.load_account_data.assert_called_once_with()


def test_scanner_loader_is_called_once() -> None:
    (
        service,
        _,
        scanner_loader,
        _,
        _,
    ) = make_service()

    service.load_complete_dashboard_data()

    scanner_loader.assert_called_once_with()


def test_analytics_service_is_called_once() -> None:
    (
        service,
        _,
        _,
        _,
        analytics_service,
    ) = make_service()

    service.load_complete_dashboard_data()

    analytics_service.load_dashboard_data\
        .assert_called_once_with(
            starting_equity=ACCOUNT_EQUITY,
        )


def test_services_are_loaded_in_expected_order() -> None:
    calls: list[str] = []

    account_service = Mock()
    scanner_loader = Mock()
    trade_workflow = Mock()
    analytics_service = Mock()

    account_data = make_account_data()
    signal = make_signal()
    workflow_result = Mock(name="workflow-result")

    def load_account_data() -> Mock:
        calls.append("account")

        return account_data

    def load_scanner_signals() -> list[TradeSignal]:
        calls.append("scanner")

        return [signal]

    def prepare_trade(
        received_signal: TradeSignal,
    ) -> Mock:
        assert received_signal is signal

        calls.append("workflow")

        return workflow_result

    def load_dashboard_data(
        *,
        starting_equity: float,
    ) -> Mock:
        assert starting_equity == ACCOUNT_EQUITY

        calls.append("analytics")

        return Mock(name="analytics-data")

    account_service.load_account_data.side_effect = (
        load_account_data
    )
    scanner_loader.side_effect = (
        load_scanner_signals
    )
    trade_workflow.prepare_trade.side_effect = (
        prepare_trade
    )
    analytics_service.load_dashboard_data.side_effect = (
        load_dashboard_data
    )

    service = DashboardCompositionService(
        account_service=account_service,
        scanner_loader=scanner_loader,
        trade_workflow=trade_workflow,
        analytics_service=analytics_service,
    )

    service.load_complete_dashboard_data()

    assert calls == [
        "account",
        "scanner",
        "workflow",
        "analytics",
    ]


def test_scanner_generator_is_materialized_once() -> None:
    (
        service,
        _,
        scanner_loader,
        trade_workflow,
        _,
    ) = make_service()

    first_signal = make_signal("NVDA")
    second_signal = make_signal("AAPL")

    iterations = 0

    def generate_signals():
        nonlocal iterations

        iterations += 1

        yield first_signal
        yield second_signal

    scanner_loader.return_value = generate_signals()

    result = service.load_complete_dashboard_data()

    assert iterations == 1
    assert result.scanner_signals == (
        first_signal,
        second_signal,
    )

    trade_workflow.prepare_trade.assert_called_once_with(
        first_signal
    )


def test_account_exception_is_not_hidden() -> None:
    (
        service,
        account_service,
        scanner_loader,
        trade_workflow,
        analytics_service,
    ) = make_service()

    account_service.load_account_data.side_effect = (
        RuntimeError("account unavailable")
    )

    with pytest.raises(
        RuntimeError,
        match="account unavailable",
    ):
        service.load_complete_dashboard_data()

    scanner_loader.assert_not_called()
    trade_workflow.prepare_trade.assert_not_called()
    analytics_service.load_dashboard_data.assert_not_called()


def test_scanner_exception_is_not_hidden() -> None:
    (
        service,
        account_service,
        scanner_loader,
        trade_workflow,
        analytics_service,
    ) = make_service()

    scanner_loader.side_effect = RuntimeError(
        "scanner unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="scanner unavailable",
    ):
        service.load_complete_dashboard_data()

    account_service.load_account_data.assert_called_once_with()
    trade_workflow.prepare_trade.assert_not_called()
    analytics_service.load_dashboard_data.assert_not_called()


def test_analytics_exception_is_not_hidden() -> None:
    (
        service,
        account_service,
        scanner_loader,
        trade_workflow,
        analytics_service,
    ) = make_service()

    analytics_service.load_dashboard_data.side_effect = (
        RuntimeError("analytics unavailable")
    )

    with pytest.raises(
        RuntimeError,
        match="analytics unavailable",
    ):
        service.load_complete_dashboard_data()

    account_service.load_account_data.assert_called_once_with()
    scanner_loader.assert_called_once_with()
    trade_workflow.prepare_trade.assert_called_once()


def test_each_load_returns_new_snapshot() -> None:
    (
        service,
        _,
        _,
        _,
        _,
    ) = make_service()

    first_result = service.load_complete_dashboard_data()
    second_result = service.load_complete_dashboard_data()

    assert first_result is not second_result
    assert first_result == second_result


def test_first_scanner_signal_is_prepared_for_approval() -> None:
    account_service = Mock()
    scanner_loader = Mock()
    trade_workflow = Mock()
    analytics_service = Mock()

    account_data = make_account_data()
    first_signal = make_signal("NVDA")
    second_signal = make_signal("AAPL")
    workflow_result = Mock(name="workflow-result")
    analytics_data = Mock(name="analytics-data")

    account_service.load_account_data.return_value = (
        account_data
    )
    scanner_loader.return_value = [
        first_signal,
        second_signal,
    ]
    trade_workflow.prepare_trade.return_value = (
        workflow_result
    )
    analytics_service.load_dashboard_data.return_value = (
        analytics_data
    )

    service = DashboardCompositionService(
        account_service=account_service,
        scanner_loader=scanner_loader,
        trade_workflow=trade_workflow,
        analytics_service=analytics_service,
    )

    result = service.load_complete_dashboard_data()

    trade_workflow.prepare_trade.assert_called_once_with(
        first_signal
    )
    assert result.workflow_result is workflow_result