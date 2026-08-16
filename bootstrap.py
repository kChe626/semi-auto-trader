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
from broker.exit_lookup import BrokerExitLookup
from broker.order_executor import OrderExecutor
from broker.order_verifier import AlpacaOrderVerifier
from broker.position_monitor import PositionMonitor
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
from dashboard.dashboard_approval_service import (
    DashboardApprovalService,
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
from execution.order_lifecycle_service import (
    OrderLifecycleService,
)
from execution.sqlite_trade_repository import (
    SqliteTradeRepository,
)
from execution.trade_executor import TradeExecutor
from risk.portfolio_manager import PortfolioManager
from scanner.market_data import get_historical_bars
from trade_management.exit_reconciler import (
    ExitReconciler,
)
from trade_management.lifecycle_engine import (
    TradeLifecycleEngine,
)
from trade_management.position_management_coordinator import (
    PositionManagementCoordinator,
)
from trade_management.position_management_service import (
    PositionManagementService,
)
from trade_management.position_reconciler import (
    PositionReconciler,
)
from trade_management.state_reconciler import (
    TradeStateReconciler,
)
from trade_management.trade_manager import (
    TradeManager,
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


def create_trade_manager(
    *,
    trading_client,
    trade_journal: TradeJournal,
    trade_repository: SqliteTradeRepository,
) -> TradeManager:
    """
    Construct the production broker-state lifecycle
    manager.

    This includes:
    - broker order reconciliation
    - broker position reconciliation
    - closed-position reconciliation
    - persisted-order lifecycle synchronization
    - smart open-position management
    """

    monitor = PositionMonitor(
        trading_client
    )

    order_reconciler = TradeStateReconciler(
        trade_journal
    )

    position_reconciler = PositionReconciler(
        trade_journal
    )

    exit_lookup = BrokerExitLookup(
        trading_client
    )

    exit_reconciler = ExitReconciler(
        trade_journal,
        exit_lookup=exit_lookup,
    )

    order_lifecycle_service = OrderLifecycleService(
        broker=trading_client,
        repository=trade_repository,
    )

    position_management_service = (
        PositionManagementService(
            trading_client=trading_client,
            journal=trade_journal,
        )
    )

    position_management_coordinator = (
        PositionManagementCoordinator(
            journal=trade_journal,
            management_service=(
                position_management_service
            ),
            historical_loader=(
                get_historical_bars
            ),
        )
    )

    lifecycle_engine = TradeLifecycleEngine(
        monitor=monitor,
        order_reconciler=order_reconciler,
        position_reconciler=position_reconciler,
        exit_reconciler=exit_reconciler,
        order_lifecycle_service=(
            order_lifecycle_service
        ),
        position_management_coordinator=(
            position_management_coordinator
        ),
    )

    return TradeManager(
        lifecycle_engine
    )


def create_dashboard_approval_service(
    *,
    database_path: Path | str = DATABASE_PATH,
) -> DashboardApprovalService:
    """
    Construct the production dashboard approval path.

    Approval performs fresh portfolio and broker
    preflight validation immediately before paper
    execution.
    """

    trading_client = create_trading_client()

    trade_journal = TradeJournal(
        database_path=database_path,
    )

    trade_repository = create_trade_repository(
        database_path=database_path,
    )

    order_executor = OrderExecutor(
        trading_client
    )

    trade_executor = TradeExecutor(
        broker=order_executor,
        journal=trade_journal,
        repository=trade_repository,
        order_verifier=AlpacaOrderVerifier(
            trading_client
        ),
    )

    portfolio_manager = PortfolioManager(
        trading_client
    )

    preflight_runner = partial(
        run_broker_preflight,
        trading_client,
    )

    return DashboardApprovalService(
        trade_executor=trade_executor,
        portfolio_manager=portfolio_manager,
        preflight_runner=preflight_runner,
    )


def create_dashboard_service(
    *,
    database_path: Path | str = DATABASE_PATH,
) -> DashboardCompositionService:
    """
    Construct the production dashboard dependency
    graph.

    Broker lifecycle state is synchronized before
    dashboard account, scanner, trade-history, and
    analytics data are loaded.
    """

    trading_client = create_trading_client()

    trade_journal = TradeJournal(
        database_path=database_path,
    )

    trade_repository = create_trade_repository(
        database_path=database_path,
    )

    trade_manager = create_trade_manager(
        trading_client=trading_client,
        trade_journal=trade_journal,
        trade_repository=trade_repository,
    )

    trade_manager.start_cycle()

    closed_trade_repository = ClosedTradeRepository(
        event_source=trade_journal,
    )

    account = trading_client.get_account()

    account_equity = float(
        account.equity
    )

    preflight_runner = partial(
        run_broker_preflight,
        trading_client,
    )

    trade_workflow = TradeWorkflow(
        account_equity=account_equity,
        risk_percent=RISK_PERCENT,
        max_position_percent=(
            MAX_POSITION_PERCENT
        ),
        stop_loss_percent=(
            STOP_LOSS_PERCENT
        ),
        reward_risk_ratio=(
            REWARD_RISK_RATIO
        ),
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
        equity_curve=(
            EquityCurveCalculator
        ),
        drawdown_calculator=(
            DrawdownCalculator
        ),
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