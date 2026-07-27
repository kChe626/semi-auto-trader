from __future__ import annotations

from dashboard.account_service import (
    AccountService,
    TradingClientProtocol,
)
from dashboard.composition_service import (
    DashboardCompositionService,
    TradeWorkflowProtocol,
)
from dashboard.dashboard_service import (
    ClosedTradeRepositoryProtocol,
    DashboardService,
    DrawdownCalculatorProtocol,
    EquityCurveCalculatorProtocol,
    TradeAnalyticsCalculatorProtocol,
    TradeDistributionCalculatorProtocol,
)
from scanner.scanner import scan_market


def create_dashboard_composition_service(
    *,
    trading_client: TradingClientProtocol,
    trade_workflow: TradeWorkflowProtocol,
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
) -> DashboardCompositionService:
    """
    Create the complete dashboard backend service graph.

    Environment loading, SQLite initialization, broker
    authentication, workflow configuration, presentation
    mapping, and Streamlit rendering remain outside this
    factory.

    Keeping those responsibilities outside the factory
    makes it deterministic and safe to import in tests.
    """

    account_service = AccountService(
        trading_client=trading_client,
    )

    analytics_service = DashboardService(
        closed_trade_repository=(
            closed_trade_repository
        ),
        performance_statistics=(
            performance_statistics
        ),
        equity_curve=equity_curve,
        drawdown_calculator=drawdown_calculator,
        monthly_performance_calculator=(
            monthly_performance_calculator
        ),
        yearly_performance_calculator=(
            yearly_performance_calculator
        ),
        trade_distribution_calculator=(
            trade_distribution_calculator
        ),
    )

    return DashboardCompositionService(
        account_service=account_service,
        scanner_loader=scan_market,
        trade_workflow=trade_workflow,
        analytics_service=analytics_service,
    )