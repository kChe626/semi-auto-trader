from __future__ import annotations

from pathlib import Path

from analytics.drawdown import DrawdownCalculator
from analytics.equity_curve import EquityCurveCalculator
from analytics.monthly_performance import (
    MonthlyPerformanceCalculator,
)
from analytics.performance_statistics import (
    PerformanceStatistics,
)
from analytics.trade_distribution import (
    TradeDistributionCalculator,
)
from analytics.yearly_performance import (
    YearlyPerformanceCalculator,
)
from broker.alpaca_client import create_trading_client
from dashboard.composition_service import (
    DashboardCompositionService,
)
from dashboard.service_factory import (
    create_dashboard_composition_service,
)
from database.closed_trade_repository import (
    ClosedTradeRepository,
)
from database.trade_journal import (
    DATABASE_PATH,
    TradeJournal,
)


def create_dashboard_service(
    *,
    database_path: Path | str = DATABASE_PATH,
) -> DashboardCompositionService:
    """
    Construct the production dashboard dependency graph.

    This composition root connects:

    - Alpaca paper-trading account data
    - the SQLite trade journal
    - the closed-trade repository
    - all dashboard analytics calculators
    - the dashboard composition service
    """

    trading_client = create_trading_client()

    trade_journal = TradeJournal(
        database_path=database_path,
    )

    closed_trade_repository = ClosedTradeRepository(
        event_source=trade_journal,
    )

    return create_dashboard_composition_service(
        trading_client=trading_client,
        closed_trade_repository=(
            closed_trade_repository
        ),
        performance_statistics=(
            PerformanceStatistics
        ),
        equity_curve=EquityCurveCalculator,
        drawdown_calculator=DrawdownCalculator,
        monthly_performance_calculator=(
            MonthlyPerformanceCalculator
        ),
        yearly_performance_calculator=(
            YearlyPerformanceCalculator
        ),
        trade_distribution_calculator=(
            TradeDistributionCalculator
        ),
    )