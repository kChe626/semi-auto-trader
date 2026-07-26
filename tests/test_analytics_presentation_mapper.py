from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock

from dashboard.analytics_presentation_mapper import (
    AnalyticsPresentationMapper,
)
from dashboard.analytics_presentation_models import (
    AnalyticsMetricViewModel,
    AnalyticsSectionViewModel,
    AnalyticsTableViewModel,
)
from dashboard.dashboard_service import DashboardData


@dataclass(frozen=True)
class FakePerformanceStatistics:
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    average_pnl: float
    profit_factor: float
    expectancy: float


@dataclass(frozen=True)
class FakeEquityPoint:
    trade_number: int
    equity: float


def make_dashboard_data(
    *,
    performance_statistics: object | None = None,
    equity_curve: object = (),
    drawdown: object = (),
    monthly_performance: object = (),
    yearly_performance: object = (),
    symbol_distribution: object = (),
    weekday_distribution: object = (),
) -> DashboardData:
    return DashboardData(
        closed_trades=(),
        performance_statistics=(
            performance_statistics
            if performance_statistics is not None
            else FakePerformanceStatistics(
                total_trades=10,
                winning_trades=6,
                losing_trades=4,
                win_rate=0.60,
                total_pnl=1250.5,
                average_pnl=125.05,
                profit_factor=1.75,
                expectancy=125.05,
            )
        ),
        equity_curve=equity_curve,
        drawdown=drawdown,
        monthly_performance=monthly_performance,
        yearly_performance=yearly_performance,
        symbol_distribution=symbol_distribution,
        weekday_distribution=weekday_distribution,
    )


def test_map_returns_analytics_section() -> None:
    mapper = AnalyticsPresentationMapper()

    result = mapper.map_analytics_section(
        make_dashboard_data()
    )

    assert isinstance(
        result,
        AnalyticsSectionViewModel,
    )


def test_performance_metrics_are_formatted() -> None:
    mapper = AnalyticsPresentationMapper()

    result = mapper.map_analytics_section(
        make_dashboard_data()
    )

    assert result.metrics == (
        AnalyticsMetricViewModel(
            label="Total Trades",
            value="10",
        ),
        AnalyticsMetricViewModel(
            label="Winning Trades",
            value="6",
        ),
        AnalyticsMetricViewModel(
            label="Losing Trades",
            value="4",
        ),
        AnalyticsMetricViewModel(
            label="Win Rate",
            value="60.00%",
        ),
        AnalyticsMetricViewModel(
            label="Net Profit/Loss",
            value="$1,250.50",
        ),
        AnalyticsMetricViewModel(
            label="Average Profit/Loss",
            value="$125.05",
        ),
        AnalyticsMetricViewModel(
            label="Profit Factor",
            value="1.75",
        ),
        AnalyticsMetricViewModel(
            label="Expectancy",
            value="$125.05",
        ),
    )


def test_negative_currency_is_formatted() -> None:
    mapper = AnalyticsPresentationMapper()

    statistics = {
        "total_trades": 2,
        "total_pnl": -250.75,
    }

    result = mapper.map_analytics_section(
        make_dashboard_data(
            performance_statistics=statistics
        )
    )

    assert result.metrics == (
        AnalyticsMetricViewModel(
            label="Total Trades",
            value="2",
        ),
        AnalyticsMetricViewModel(
            label="Net Profit/Loss",
            value="-$250.75",
        ),
    )


def test_percentage_over_one_is_treated_as_whole_percent() -> None:
    mapper = AnalyticsPresentationMapper()

    statistics = {
        "win_rate": 60.0,
    }

    result = mapper.map_analytics_section(
        make_dashboard_data(
            performance_statistics=statistics
        )
    )

    assert result.metrics == (
        AnalyticsMetricViewModel(
            label="Win Rate",
            value="60.00%",
        ),
    )


def test_missing_metrics_are_skipped() -> None:
    mapper = AnalyticsPresentationMapper()

    result = mapper.map_analytics_section(
        make_dashboard_data(
            performance_statistics={
                "total_trades": 3,
            }
        )
    )

    assert result.metrics == (
        AnalyticsMetricViewModel(
            label="Total Trades",
            value="3",
        ),
    )


def test_dataclass_records_become_table() -> None:
    mapper = AnalyticsPresentationMapper()

    result = mapper.map_analytics_section(
        make_dashboard_data(
            equity_curve=(
                FakeEquityPoint(
                    trade_number=1,
                    equity=100100.0,
                ),
                FakeEquityPoint(
                    trade_number=2,
                    equity=100250.5,
                ),
            )
        )
    )

    assert result.equity_curve == (
        AnalyticsTableViewModel(
            columns=(
                "Trade Number",
                "Equity",
            ),
            rows=(
                (
                    "1",
                    "100,100.00",
                ),
                (
                    "2",
                    "100,250.50",
                ),
            ),
        )
    )


def test_dictionary_records_become_table() -> None:
    mapper = AnalyticsPresentationMapper()

    result = mapper.map_analytics_section(
        make_dashboard_data(
            symbol_distribution=(
                {
                    "symbol": "AAPL",
                    "trade_count": 3,
                    "net_pnl": 250.0,
                },
                {
                    "symbol": "MSFT",
                    "trade_count": 2,
                    "net_pnl": -50.0,
                },
            )
        )
    )

    assert result.symbol_distribution.columns == (
        "Symbol",
        "Trade Count",
        "Net Pnl",
    )

    assert result.symbol_distribution.rows == (
        (
            "AAPL",
            "3",
            "250.00",
        ),
        (
            "MSFT",
            "2",
            "-50.00",
        ),
    )


def test_object_records_become_table() -> None:
    mapper = AnalyticsPresentationMapper()

    result = mapper.map_analytics_section(
        make_dashboard_data(
            monthly_performance=(
                SimpleNamespace(
                    month="2026-07",
                    trade_count=4,
                ),
            )
        )
    )

    assert result.monthly_performance == (
        AnalyticsTableViewModel(
            columns=(
                "Month",
                "Trade Count",
            ),
            rows=(
                (
                    "2026-07",
                    "4",
                ),
            ),
        )
    )


def test_nested_records_attribute_is_supported() -> None:
    mapper = AnalyticsPresentationMapper()

    container = SimpleNamespace(
        records=(
            {
                "year": 2026,
                "net_pnl": 500.0,
            },
        )
    )

    result = mapper.map_analytics_section(
        make_dashboard_data(
            yearly_performance=container
        )
    )

    assert result.yearly_performance.rows == (
        (
            "2026",
            "500.00",
        ),
    )


def test_dates_are_formatted() -> None:
    mapper = AnalyticsPresentationMapper()

    result = mapper.map_analytics_section(
        make_dashboard_data(
            drawdown=(
                {
                    "date": date(2026, 7, 25),
                    "drawdown": -125.5,
                },
            )
        )
    )

    assert result.drawdown.rows == (
        (
            "2026-07-25",
            "-125.50",
        ),
    )


def test_empty_results_return_empty_tables() -> None:
    mapper = AnalyticsPresentationMapper()

    result = mapper.map_analytics_section(
        make_dashboard_data()
    )

    assert result.equity_curve.is_empty is True
    assert result.drawdown.is_empty is True
    assert (
        result.monthly_performance.is_empty
        is True
    )
    assert (
        result.yearly_performance.is_empty
        is True
    )
    assert (
        result.symbol_distribution.is_empty
        is True
    )
    assert (
        result.weekday_distribution.is_empty
        is True
    )


def test_scalar_result_becomes_single_value_table() -> None:
    mapper = AnalyticsPresentationMapper()

    result = mapper.map_analytics_section(
        make_dashboard_data(
            weekday_distribution="No data"
        )
    )

    assert result.weekday_distribution == (
        AnalyticsTableViewModel(
            columns=("Value",),
            rows=(("No data",),),
        )
    )


def test_private_object_attributes_are_excluded() -> None:
    mapper = AnalyticsPresentationMapper()

    record = Mock()
    record.__dict__ = {
        "symbol": "AAPL",
        "_internal": "hidden",
    }

    result = mapper.map_analytics_section(
        make_dashboard_data(
            symbol_distribution=(record,)
        )
    )

    assert result.symbol_distribution.columns == (
        "Symbol",
    )
    assert result.symbol_distribution.rows == (
        ("AAPL",),
    )