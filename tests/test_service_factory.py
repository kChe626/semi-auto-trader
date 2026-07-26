from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

from dashboard.composition_service import (
    DashboardCompositionService,
)
from dashboard.service_factory import (
    create_dashboard_composition_service,
)


STARTING_EQUITY = 100_000.0


def make_factory_dependencies() -> dict[str, Mock]:
    return {
        "trading_client": Mock(),
        "closed_trade_repository": Mock(),
        "performance_statistics": Mock(),
        "equity_curve": Mock(),
        "drawdown_calculator": Mock(),
        "monthly_performance_calculator": Mock(),
        "yearly_performance_calculator": Mock(),
        "trade_distribution_calculator": Mock(),
    }


def configure_successful_dependencies(
    dependencies: dict[str, Mock],
) -> None:
    dependencies[
        "trading_client"
    ].get_account.return_value = SimpleNamespace(
        status="ACTIVE",
        cash="100000",
        equity="100000",
        buying_power="400000",
        portfolio_value="100000",
        last_equity="100000",
        trading_blocked=False,
        account_blocked=False,
    )

    dependencies[
        "trading_client"
    ].get_all_positions.return_value = []

    dependencies[
        "closed_trade_repository"
    ].get_all.return_value = []

    dependencies[
        "performance_statistics"
    ].calculate.return_value = "statistics"

    dependencies[
        "equity_curve"
    ].calculate.return_value = "equity"

    dependencies[
        "drawdown_calculator"
    ].calculate.return_value = "drawdown"

    dependencies[
        "monthly_performance_calculator"
    ].calculate.return_value = "monthly"

    dependencies[
        "yearly_performance_calculator"
    ].calculate.return_value = "yearly"

    dependencies[
        "trade_distribution_calculator"
    ].by_symbol.return_value = "symbols"

    dependencies[
        "trade_distribution_calculator"
    ].by_weekday.return_value = "weekdays"


def test_factory_returns_composition_service() -> None:
    dependencies = make_factory_dependencies()

    service = create_dashboard_composition_service(
        **dependencies
    )

    assert isinstance(
        service,
        DashboardCompositionService,
    )


def test_factory_wires_account_service() -> None:
    dependencies = make_factory_dependencies()

    configure_successful_dependencies(
        dependencies
    )

    service = create_dashboard_composition_service(
        **dependencies
    )

    result = (
        service.load_complete_dashboard_data()
    )

    assert result.account_data.account.status == (
        "ACTIVE"
    )

    assert result.account_data.account.cash == (
        100000.0
    )

    assert result.account_data.account.equity == (
        STARTING_EQUITY
    )

    assert (
        result.account_data.account.buying_power
        == 400000.0
    )

    dependencies[
        "trading_client"
    ].get_account.assert_called_once_with()

    dependencies[
        "trading_client"
    ].get_all_positions.assert_called_once_with()


def test_factory_wires_repository() -> None:
    dependencies = make_factory_dependencies()

    configure_successful_dependencies(
        dependencies
    )

    trade_one = Mock(name="trade-one")
    trade_two = Mock(name="trade-two")

    dependencies[
        "closed_trade_repository"
    ].get_all.return_value = [
        trade_one,
        trade_two,
    ]

    service = create_dashboard_composition_service(
        **dependencies
    )

    result = (
        service.load_complete_dashboard_data()
    )

    assert (
        result.analytics_data.closed_trades
        == (
            trade_one,
            trade_two,
        )
    )

    dependencies[
        "closed_trade_repository"
    ].get_all.assert_called_once_with()


def test_factory_wires_all_analytics_calculators() -> None:
    dependencies = make_factory_dependencies()

    configure_successful_dependencies(
        dependencies
    )

    service = create_dashboard_composition_service(
        **dependencies
    )

    result = (
        service.load_complete_dashboard_data()
    )

    assert (
        result.analytics_data.performance_statistics
        == "statistics"
    )

    assert (
        result.analytics_data.equity_curve
        == "equity"
    )

    assert (
        result.analytics_data.drawdown
        == "drawdown"
    )

    assert (
        result.analytics_data.monthly_performance
        == "monthly"
    )

    assert (
        result.analytics_data.yearly_performance
        == "yearly"
    )

    assert (
        result.analytics_data.symbol_distribution
        == "symbols"
    )

    assert (
        result.analytics_data.weekday_distribution
        == "weekdays"
    )


def test_factory_preserves_same_trade_snapshot() -> None:
    dependencies = make_factory_dependencies()

    configure_successful_dependencies(
        dependencies
    )

    trades = [
        Mock(name="trade-one"),
        Mock(name="trade-two"),
    ]

    dependencies[
        "closed_trade_repository"
    ].get_all.return_value = trades

    equity_curve_result = Mock(
        name="equity-curve-result"
    )

    dependencies[
        "equity_curve"
    ].calculate.return_value = (
        equity_curve_result
    )

    service = create_dashboard_composition_service(
        **dependencies
    )

    service.load_complete_dashboard_data()

    expected_trades = tuple(trades)

    dependencies[
        "performance_statistics"
    ].calculate.assert_called_once_with(
        expected_trades
    )

    dependencies[
        "equity_curve"
    ].calculate.assert_called_once_with(
        expected_trades,
        starting_equity=STARTING_EQUITY,
    )

    dependencies[
        "drawdown_calculator"
    ].calculate.assert_called_once_with(
        equity_curve_result
    )

    dependencies[
        "monthly_performance_calculator"
    ].calculate.assert_called_once_with(
        expected_trades
    )

    dependencies[
        "yearly_performance_calculator"
    ].calculate.assert_called_once_with(
        expected_trades
    )

    dependencies[
        "trade_distribution_calculator"
    ].by_symbol.assert_called_once_with(
        expected_trades
    )

    dependencies[
        "trade_distribution_calculator"
    ].by_weekday.assert_called_once_with(
        expected_trades
    )


def test_factory_does_not_load_data_during_creation() -> None:
    dependencies = make_factory_dependencies()

    create_dashboard_composition_service(
        **dependencies
    )

    dependencies[
        "trading_client"
    ].get_account.assert_not_called()

    dependencies[
        "trading_client"
    ].get_all_positions.assert_not_called()

    dependencies[
        "closed_trade_repository"
    ].get_all.assert_not_called()

    dependencies[
        "performance_statistics"
    ].calculate.assert_not_called()

    dependencies[
        "equity_curve"
    ].calculate.assert_not_called()

    dependencies[
        "drawdown_calculator"
    ].calculate.assert_not_called()