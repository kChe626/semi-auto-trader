from unittest.mock import Mock

import pytest

from dashboard.composition_service import (
    CompleteDashboardData,
    DashboardCompositionService,
)
from models.preflight_result import PreflightResult
from models.trade_plan import TradePlan
from models.trade_signal import TradeSignal
from models.workflow_result import WorkflowResult


ACCOUNT_EQUITY = 100_000.00


def make_account_data() -> Mock:
    account_data = Mock(name="account-data")
    account_data.account.equity = ACCOUNT_EQUITY

    return account_data


def make_signal(
    symbol: str = "NVDA",
    signal_type: str = "BUY",
) -> TradeSignal:
    return TradeSignal(
        symbol=symbol,
        signal_type=signal_type,
        price=100.00,
        reason="Bullish crossover",
        atr=2.00,
        rsi=55.00,
        short_sma=101.00,
        long_sma=99.00,
    )


def make_plan(
    symbol: str = "NVDA",
    signal_type: str = "BUY",
    *,
    risk_reward_ratio: float = 2.00,
    total_risk: float = 100.00,
    rsi: float = 55.00,
    short_sma: float = 101.00,
    long_sma: float = 99.00,
) -> TradePlan:
    return TradePlan(
        symbol=symbol,
        signal_type=signal_type,
        entry_price=100.00,
        stop_price=98.00,
        target_price=104.00,
        quantity=10,
        risk_per_share=2.00,
        reward_per_share=4.00,
        total_risk=total_risk,
        risk_reward_ratio=risk_reward_ratio,
        rsi=rsi,
        short_sma=short_sma,
        long_sma=long_sma,
    )


def make_workflow_result(
    symbol: str = "NVDA",
    signal_type: str = "BUY",
    *,
    risk_reward_ratio: float = 2.00,
    total_risk: float = 100.00,
    rsi: float = 55.00,
    short_sma: float = 101.00,
    long_sma: float = 99.00,
) -> WorkflowResult:
    return WorkflowResult(
        ready_for_approval=True,
        plan=make_plan(
            symbol=symbol,
            signal_type=signal_type,
            risk_reward_ratio=risk_reward_ratio,
            total_risk=total_risk,
            rsi=rsi,
            short_sma=short_sma,
            long_sma=long_sma,
        ),
        preflight=PreflightResult(
            approved=True,
            reasons=[],
        ),
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
        make_workflow_result()
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

    nvda_signal = make_signal("NVDA")
    aapl_signal = make_signal("AAPL")

    scanner_signals = [
        nvda_signal,
        aapl_signal,
    ]

    nvda_workflow = make_workflow_result(
        symbol="NVDA",
    )

    aapl_workflow = make_workflow_result(
        symbol="AAPL",
    )

    analytics_data = Mock(
        name="analytics-data"
    )

    account_service.load_account_data.return_value = (
        account_data
    )

    scanner_loader.return_value = (
        scanner_signals
    )

    def prepare_trade(
        signal: TradeSignal,
    ) -> WorkflowResult:
        if signal.symbol == "NVDA":
            return nvda_workflow

        return aapl_workflow

    trade_workflow.prepare_trade.side_effect = (
        prepare_trade
    )

    analytics_service.load_dashboard_data.return_value = (
        analytics_data
    )

    result = (
        service.load_complete_dashboard_data()
    )

    assert isinstance(
        result,
        CompleteDashboardData,
    )

    assert result.account_data is account_data

    assert result.scanner_signals == tuple(
        scanner_signals
    )

    assert result.workflow_result in (
        nvda_workflow,
        aapl_workflow,
    )

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

    analytics_service.load_dashboard_data.assert_called_once_with(
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

    workflow_result = (
        make_workflow_result()
    )

    def load_account_data() -> Mock:
        calls.append(
            "account"
        )

        return account_data

    def load_scanner_signals() -> list[
        TradeSignal
    ]:
        calls.append(
            "scanner"
        )

        return [
            signal,
        ]

    def prepare_trade(
        received_signal: TradeSignal,
    ) -> WorkflowResult:
        assert received_signal is signal

        calls.append(
            "workflow"
        )

        return workflow_result

    def load_dashboard_data(
        *,
        starting_equity: float,
    ) -> Mock:
        assert (
            starting_equity
            == ACCOUNT_EQUITY
        )

        calls.append(
            "analytics"
        )

        return Mock(
            name="analytics-data"
        )

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

    first_signal = make_signal(
        "NVDA"
    )

    second_signal = make_signal(
        "AAPL"
    )

    first_workflow = (
        make_workflow_result(
            symbol="NVDA",
        )
    )

    second_workflow = (
        make_workflow_result(
            symbol="AAPL",
        )
    )

    iterations = 0

    def generate_signals():
        nonlocal iterations

        iterations += 1

        yield first_signal
        yield second_signal

    scanner_loader.return_value = (
        generate_signals()
    )

    def prepare_trade(
        signal: TradeSignal,
    ) -> WorkflowResult:
        if signal.symbol == "NVDA":
            return first_workflow

        return second_workflow

    trade_workflow.prepare_trade.side_effect = (
        prepare_trade
    )

    result = (
        service.load_complete_dashboard_data()
    )

    assert iterations == 1

    assert result.scanner_signals == (
        first_signal,
        second_signal,
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
        RuntimeError(
            "account unavailable"
        )
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

    scanner_loader.side_effect = (
        RuntimeError(
            "scanner unavailable"
        )
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
        RuntimeError(
            "analytics unavailable"
        )
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

    first_result = (
        service.load_complete_dashboard_data()
    )

    second_result = (
        service.load_complete_dashboard_data()
    )

    assert first_result is not second_result

    assert first_result == second_result


def test_sell_signal_is_skipped_when_short_trades_disabled() -> None:
    account_service = Mock()
    scanner_loader = Mock()
    trade_workflow = Mock()
    analytics_service = Mock()

    sell_signal = make_signal(
        "AMD",
        signal_type="SELL",
    )

    buy_signal = make_signal(
        "CRM",
        signal_type="BUY",
    )

    buy_workflow = (
        make_workflow_result(
            symbol="CRM",
            signal_type="BUY",
        )
    )

    account_service.load_account_data.return_value = (
        make_account_data()
    )

    scanner_loader.return_value = [
        sell_signal,
        buy_signal,
    ]

    trade_workflow.prepare_trade.return_value = (
        buy_workflow
    )

    analytics_service.load_dashboard_data.return_value = (
        Mock(
            name="analytics-data"
        )
    )

    service = DashboardCompositionService(
        account_service=account_service,
        scanner_loader=scanner_loader,
        trade_workflow=trade_workflow,
        analytics_service=analytics_service,
    )

    result = (
        service.load_complete_dashboard_data()
    )

    trade_workflow.prepare_trade.assert_called_once_with(
        buy_signal
    )

    assert (
        result.workflow_result
        is buy_workflow
    )


def test_highest_ranked_eligible_workflow_is_selected() -> None:
    account_service = Mock()
    scanner_loader = Mock()
    trade_workflow = Mock()
    analytics_service = Mock()

    account_service.load_account_data.return_value = (
        make_account_data()
    )

    weaker_signal = make_signal(
        "AAPL",
        signal_type="BUY",
    )

    stronger_signal = make_signal(
        "CRM",
        signal_type="BUY",
    )

    weaker_workflow = (
        make_workflow_result(
            symbol="AAPL",
            rsi=69.00,
            short_sma=100.10,
            long_sma=100.00,
        )
    )

    stronger_workflow = (
        make_workflow_result(
            symbol="CRM",
            rsi=55.00,
            short_sma=103.00,
            long_sma=100.00,
        )
    )

    scanner_loader.return_value = [
        weaker_signal,
        stronger_signal,
    ]

    def prepare_trade(
        signal: TradeSignal,
    ) -> WorkflowResult:
        if signal.symbol == "AAPL":
            return weaker_workflow

        return stronger_workflow

    trade_workflow.prepare_trade.side_effect = (
        prepare_trade
    )

    analytics_service.load_dashboard_data.return_value = (
        Mock(
            name="analytics-data"
        )
    )

    service = DashboardCompositionService(
        account_service=account_service,
        scanner_loader=scanner_loader,
        trade_workflow=trade_workflow,
        analytics_service=analytics_service,
    )

    result = (
        service.load_complete_dashboard_data()
    )

    assert (
        result.workflow_result
        is stronger_workflow
    )


def test_no_signals_returns_no_workflow() -> None:
    (
        service,
        _,
        scanner_loader,
        trade_workflow,
        _,
    ) = make_service()

    scanner_loader.return_value = []

    result = (
        service.load_complete_dashboard_data()
    )

    assert result.workflow_result is None

    trade_workflow.prepare_trade.assert_not_called()


def test_only_disabled_sell_signals_returns_no_workflow() -> None:
    (
        service,
        _,
        scanner_loader,
        trade_workflow,
        _,
    ) = make_service()

    scanner_loader.return_value = [
        make_signal(
            "AMD",
            signal_type="SELL",
        ),
        make_signal(
            "AMAT",
            signal_type="SELL",
        ),
    ]

    result = (
        service.load_complete_dashboard_data()
    )

    assert result.workflow_result is None

    trade_workflow.prepare_trade.assert_not_called()