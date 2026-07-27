from __future__ import annotations

from pathlib import Path
from unittest.mock import ANY, Mock, patch

import bootstrap


def test_create_dashboard_service_wires_trade_workflow(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "trades.db"

    trading_client = Mock(
        name="trading-client"
    )
    trade_journal = Mock(
        name="trade-journal"
    )
    closed_trade_repository = Mock(
        name="closed-trade-repository"
    )
    trade_workflow = Mock(
        name="trade-workflow"
    )
    dashboard_service = Mock(
        name="dashboard-service"
    )

    account = Mock(name="account")
    account.equity = "100000.00"
    trading_client.get_account.return_value = account

    with (
        patch.object(
            bootstrap,
            "create_trading_client",
            return_value=trading_client,
        ),
        patch.object(
            bootstrap,
            "TradeJournal",
            return_value=trade_journal,
        ) as trade_journal_class,
        patch.object(
            bootstrap,
            "ClosedTradeRepository",
            return_value=closed_trade_repository,
        ) as repository_class,
        patch.object(
            bootstrap,
            "TradeWorkflow",
            return_value=trade_workflow,
        ) as workflow_class,
        patch.object(
            bootstrap,
            "create_dashboard_composition_service",
            return_value=dashboard_service,
        ) as service_factory,
    ):
        result = bootstrap.create_dashboard_service(
            database_path=database_path,
        )

    assert result is dashboard_service

    trade_journal_class.assert_called_once_with(
        database_path=database_path,
    )

    repository_class.assert_called_once_with(
        event_source=trade_journal,
    )

    workflow_class.assert_called_once_with(
        account_equity=100000.0,
        risk_percent=bootstrap.RISK_PERCENT,
        max_position_percent=(
            bootstrap.MAX_POSITION_PERCENT
        ),
        stop_loss_percent=(
            bootstrap.STOP_LOSS_PERCENT
        ),
        reward_risk_ratio=(
            bootstrap.REWARD_RISK_RATIO
        ),
        preflight_runner=ANY,
    )

    service_factory.assert_called_once_with(
        trading_client=trading_client,
        trade_workflow=trade_workflow,
        closed_trade_repository=(
            closed_trade_repository
        ),
        performance_statistics=(
            bootstrap.PerformanceStatistics
        ),
        equity_curve=bootstrap.EquityCurveCalculator,
        drawdown_calculator=(
            bootstrap.DrawdownCalculator
        ),
        monthly_performance_calculator=(
            bootstrap.MonthlyPerformanceCalculator
        ),
        yearly_performance_calculator=(
            bootstrap.YearlyPerformanceCalculator
        ),
        trade_distribution_calculator=(
            bootstrap.TradeDistributionCalculator
        ),
    )