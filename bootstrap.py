from __future__ import annotations

from functools import partial
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
from application.trade_workflow import TradeWorkflow
from broker.alpaca_client import create_trading_client
from broker.preflight_service import run_broker_preflight
from config.trading_config import (
    MAX_POSITION_PERCENT,
    REWARD_RISK_RATIO,
    RISK_PERCENT,
    STOP_LOSS_PERCENT,
)
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
from execution.sqlite_trade_repository import (
    SqliteTradeRepository,
)
def create_trade_repository(
    *,
    database_path: Path | str = DATABASE_PATH,
) -> SqliteTradeRepository:
    """
    Construct the production SQLite trade repository.
    """

    return SqliteTradeRepository(
        database_path=database_path,
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
    - the trade preparation workflow
    - broker preflight validation
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

    account = trading_client.get_account()
    account_equity = float(account.equity)

    preflight_runner = partial(
        run_broker_preflight,
        trading_client,
    )

    trade_workflow = TradeWorkflow(
        account_equity=account_equity,
        risk_percent=RISK_PERCENT,
        max_position_percent=MAX_POSITION_PERCENT,
        stop_loss_percent=STOP_LOSS_PERCENT,
        reward_risk_ratio=REWARD_RISK_RATIO,
        preflight_runner=preflight_runner,
    )

    return create_dashboard_composition_service(
        trading_client=trading_client,
        trade_workflow=trade_workflow,
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