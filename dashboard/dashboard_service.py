from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from models.closed_trade import ClosedTrade


class ClosedTradeRepositoryProtocol(Protocol):
    """
    Defines the repository operation required by the
    dashboard service.
    """

    def get_all(self) -> Sequence[ClosedTrade]:
        ...


class TradeAnalyticsCalculatorProtocol(Protocol):
    """
    Defines an analytics calculator that accepts a
    sequence of closed trades.
    """

    def calculate(
        self,
        trades: Sequence[ClosedTrade],
    ) -> Any:
        ...


class EquityCurveCalculatorProtocol(Protocol):
    """
    Defines the equity-curve calculation required by the
    dashboard.
    """

    def calculate(
        self,
        trades: Sequence[ClosedTrade],
        *,
        starting_equity: float,
    ) -> Any:
        ...


class DrawdownCalculatorProtocol(Protocol):
    """
    Defines the drawdown calculation required by the
    dashboard.
    """

    def calculate(
        self,
        curve: Any,
    ) -> Any:
        ...


class TradeDistributionCalculatorProtocol(
    Protocol
):
    """
    Defines the distribution calculations required by
    the dashboard.
    """

    def by_symbol(
        self,
        trades: Sequence[ClosedTrade],
    ) -> Any:
        ...

    def by_weekday(
        self,
        trades: Sequence[ClosedTrade],
    ) -> Any:
        ...


@dataclass(frozen=True)
class DashboardData:
    """
    Complete closed-trade analytics snapshot prepared
    for presentation.

    This model contains no Streamlit-specific objects.
    """

    closed_trades: tuple[ClosedTrade, ...]
    performance_statistics: Any
    equity_curve: Any
    drawdown: Any
    monthly_performance: Any
    yearly_performance: Any
    symbol_distribution: Any
    weekday_distribution: Any


class DashboardService:
    """
    Loads closed trades and prepares all analytics
    required by the Streamlit dashboard.

    The service orchestrates existing analytics modules.
    It does not access Streamlit, submit broker orders,
    or calculate analytics directly.
    """

    def __init__(
        self,
        *,
        closed_trade_repository: (
            ClosedTradeRepositoryProtocol
        ),
        performance_statistics: (
            TradeAnalyticsCalculatorProtocol
        ),
        equity_curve: EquityCurveCalculatorProtocol,
        drawdown_calculator: (
            DrawdownCalculatorProtocol
        ),
        monthly_performance_calculator: (
            TradeAnalyticsCalculatorProtocol
        ),
        yearly_performance_calculator: (
            TradeAnalyticsCalculatorProtocol
        ),
        trade_distribution_calculator: (
            TradeDistributionCalculatorProtocol
        ),
    ) -> None:
        self._closed_trade_repository = (
            closed_trade_repository
        )

        self._performance_statistics = (
            performance_statistics
        )

        self._equity_curve = equity_curve

        self._drawdown_calculator = (
            drawdown_calculator
        )

        self._monthly_performance_calculator = (
            monthly_performance_calculator
        )

        self._yearly_performance_calculator = (
            yearly_performance_calculator
        )

        self._trade_distribution_calculator = (
            trade_distribution_calculator
        )

    def load_dashboard_data(
        self,
        *,
        starting_equity: float,
    ) -> DashboardData:
        """
        Load closed trades and create one immutable
        analytics snapshot.

        starting_equity is supplied by the account layer
        so the analytics service remains independent from
        the broker client.
        """

        if starting_equity <= 0:
            raise ValueError(
                "starting_equity must be greater "
                "than zero"
            )

        closed_trades = tuple(
            self._closed_trade_repository.get_all()
        )

        equity_curve = (
            self._equity_curve.calculate(
                closed_trades,
                starting_equity=starting_equity,
            )
        )

        drawdown = (
            self._drawdown_calculator.calculate(
                equity_curve
            )
        )

        return DashboardData(
            closed_trades=closed_trades,
            performance_statistics=(
                self._performance_statistics.calculate(
                    closed_trades
                )
            ),
            equity_curve=equity_curve,
            drawdown=drawdown,
            monthly_performance=(
                self
                ._monthly_performance_calculator
                .calculate(closed_trades)
            ),
            yearly_performance=(
                self
                ._yearly_performance_calculator
                .calculate(closed_trades)
            ),
            symbol_distribution=(
                self
                ._trade_distribution_calculator
                .by_symbol(closed_trades)
            ),
            weekday_distribution=(
                self
                ._trade_distribution_calculator
                .by_weekday(closed_trades)
            ),
        )