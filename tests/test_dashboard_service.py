from __future__ import annotations

from unittest.mock import Mock

import pytest

from dashboard.dashboard_service import (
    DashboardData,
    DashboardService,
)


STARTING_EQUITY = 100_000.0


def make_service(
    *,
    repository: Mock | None = None,
    performance_statistics: Mock | None = None,
    equity_curve: Mock | None = None,
    drawdown_calculator: Mock | None = None,
    monthly_calculator: Mock | None = None,
    yearly_calculator: Mock | None = None,
    distribution_calculator: Mock | None = None,
) -> tuple[
    DashboardService,
    Mock,
    Mock,
    Mock,
    Mock,
    Mock,
    Mock,
    Mock,
]:
    repository = repository or Mock()

    performance_statistics = (
        performance_statistics or Mock()
    )

    equity_curve = equity_curve or Mock()

    drawdown_calculator = (
        drawdown_calculator or Mock()
    )

    monthly_calculator = (
        monthly_calculator or Mock()
    )

    yearly_calculator = (
        yearly_calculator or Mock()
    )

    distribution_calculator = (
        distribution_calculator or Mock()
    )

    service = DashboardService(
        closed_trade_repository=repository,
        performance_statistics=performance_statistics,
        equity_curve=equity_curve,
        drawdown_calculator=drawdown_calculator,
        monthly_performance_calculator=(
            monthly_calculator
        ),
        yearly_performance_calculator=(
            yearly_calculator
        ),
        trade_distribution_calculator=(
            distribution_calculator
        ),
    )

    return (
        service,
        repository,
        performance_statistics,
        equity_curve,
        drawdown_calculator,
        monthly_calculator,
        yearly_calculator,
        distribution_calculator,
    )


def test_load_dashboard_data_returns_snapshot() -> None:
    (
        service,
        repository,
        performance_statistics,
        equity_curve,
        drawdown_calculator,
        monthly_calculator,
        yearly_calculator,
        distribution_calculator,
    ) = make_service()

    trades = [
        Mock(name="trade-1"),
        Mock(name="trade-2"),
    ]

    repository.get_all.return_value = trades

    performance_statistics.calculate.return_value = (
        "statistics"
    )

    equity_curve.calculate.return_value = (
        "equity-curve"
    )

    drawdown_calculator.calculate.return_value = (
        "drawdown"
    )

    monthly_calculator.calculate.return_value = (
        "monthly"
    )

    yearly_calculator.calculate.return_value = (
        "yearly"
    )

    distribution_calculator.by_symbol.return_value = (
        "symbols"
    )

    distribution_calculator.by_weekday.return_value = (
        "weekdays"
    )

    result = service.load_dashboard_data(
        starting_equity=STARTING_EQUITY,
    )

    assert isinstance(result, DashboardData)
    assert result.closed_trades == tuple(trades)

    assert (
        result.performance_statistics
        == "statistics"
    )

    assert result.equity_curve == "equity-curve"
    assert result.drawdown == "drawdown"
    assert result.monthly_performance == "monthly"
    assert result.yearly_performance == "yearly"
    assert result.symbol_distribution == "symbols"
    assert result.weekday_distribution == "weekdays"


def test_repository_is_loaded_once() -> None:
    (
        service,
        repository,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = make_service()

    repository.get_all.return_value = []

    service.load_dashboard_data(
        starting_equity=STARTING_EQUITY,
    )

    repository.get_all.assert_called_once_with()


def test_same_immutable_trade_collection_is_used() -> None:
    (
        service,
        repository,
        performance_statistics,
        equity_curve,
        drawdown_calculator,
        monthly_calculator,
        yearly_calculator,
        distribution_calculator,
    ) = make_service()

    trades = [
        Mock(name="trade-1"),
        Mock(name="trade-2"),
    ]

    repository.get_all.return_value = trades

    equity_curve_result = Mock(
        name="equity-curve-result"
    )

    equity_curve.calculate.return_value = (
        equity_curve_result
    )

    result = service.load_dashboard_data(
        starting_equity=STARTING_EQUITY,
    )

    expected_trades = tuple(trades)

    performance_statistics.calculate\
        .assert_called_once_with(expected_trades)

    equity_curve.calculate.assert_called_once_with(
        expected_trades,
        starting_equity=STARTING_EQUITY,
    )

    drawdown_calculator.calculate\
        .assert_called_once_with(
            equity_curve_result
        )

    monthly_calculator.calculate\
        .assert_called_once_with(expected_trades)

    yearly_calculator.calculate\
        .assert_called_once_with(expected_trades)

    distribution_calculator.by_symbol\
        .assert_called_once_with(expected_trades)

    distribution_calculator.by_weekday\
        .assert_called_once_with(expected_trades)

    assert result.closed_trades == expected_trades


def test_empty_repository_still_runs_analytics() -> None:
    (
        service,
        repository,
        performance_statistics,
        equity_curve,
        drawdown_calculator,
        monthly_calculator,
        yearly_calculator,
        distribution_calculator,
    ) = make_service()

    repository.get_all.return_value = []

    equity_curve_result = Mock(
        name="empty-equity-curve"
    )

    equity_curve.calculate.return_value = (
        equity_curve_result
    )

    result = service.load_dashboard_data(
        starting_equity=STARTING_EQUITY,
    )

    assert result.closed_trades == ()

    performance_statistics.calculate\
        .assert_called_once_with(())

    equity_curve.calculate.assert_called_once_with(
        (),
        starting_equity=STARTING_EQUITY,
    )

    drawdown_calculator.calculate\
        .assert_called_once_with(
            equity_curve_result
        )

    monthly_calculator.calculate\
        .assert_called_once_with(())

    yearly_calculator.calculate\
        .assert_called_once_with(())

    distribution_calculator.by_symbol\
        .assert_called_once_with(())

    distribution_calculator.by_weekday\
        .assert_called_once_with(())


def test_repository_generator_is_materialized_once() -> None:
    (
        service,
        repository,
        performance_statistics,
        _,
        _,
        _,
        _,
        _,
    ) = make_service()

    trade_one = Mock(name="trade-1")
    trade_two = Mock(name="trade-2")

    repository.get_all.return_value = (
        trade
        for trade in (
            trade_one,
            trade_two,
        )
    )

    result = service.load_dashboard_data(
        starting_equity=STARTING_EQUITY,
    )

    expected_trades = (
        trade_one,
        trade_two,
    )

    assert result.closed_trades == expected_trades

    performance_statistics.calculate\
        .assert_called_once_with(expected_trades)


def test_analytics_exception_is_not_hidden() -> None:
    (
        service,
        repository,
        performance_statistics,
        _,
        _,
        _,
        _,
        _,
    ) = make_service()

    repository.get_all.return_value = []

    performance_statistics.calculate.side_effect = (
        RuntimeError("analytics failed")
    )

    with pytest.raises(
        RuntimeError,
        match="analytics failed",
    ):
        service.load_dashboard_data(
            starting_equity=STARTING_EQUITY,
        )


def test_invalid_starting_equity_is_rejected() -> None:
    (
        service,
        repository,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = make_service()

    with pytest.raises(
        ValueError,
        match=(
            "starting_equity must be greater than zero"
        ),
    ):
        service.load_dashboard_data(
            starting_equity=0.0,
        )

    repository.get_all.assert_not_called()