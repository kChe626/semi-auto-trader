from __future__ import annotations

from dashboard.account_service import (
    AccountService,
    TradingClientProtocol,
)
from dashboard.composition_service import (
    DashboardCompositionService,
)
from dashboard.dashboard_service import (
    ClosedTradeRepositoryProtocol,
    DashboardService,
    DrawdownCalculatorProtocol,
    EquityCurveCalculatorProtocol,
    TradeAnalyticsCalculatorProtocol,
    TradeDistributionCalculatorProtocol,
)


def create_dashboard_composition_service(
    *,
    trading_client: TradingClientProtocol,
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

    Environment loading, SQLite initialization, and broker
    authentication remain outside this factory. This makes
    the factory deterministic and safe to import in tests.
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
        analytics_service=analytics_service,
    )