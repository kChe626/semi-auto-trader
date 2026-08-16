from __future__ import annotations

from pathlib import Path
from unittest.mock import ANY, Mock, patch

import bootstrap
from execution.sqlite_trade_repository import (
    SqliteTradeRepository,
)


def test_create_dashboard_service_wires_trade_workflow(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "trades.db"

    trading_client = Mock(
        name="trading-client",
    )
    trade_journal = Mock(
        name="trade-journal",
    )
    trade_repository = Mock(
        name="trade-repository",
    )
    trade_manager = Mock(
        name="trade-manager",
    )
    closed_trade_repository = Mock(
        name="closed-trade-repository",
    )
    trade_workflow = Mock(
        name="trade-workflow",
    )
    dashboard_service = Mock(
        name="dashboard-service",
    )

    account = Mock(
        name="account",
    )
    account.equity = "100000.00"

    trading_client.get_account.return_value = (
        account
    )

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
            "create_trade_repository",
            return_value=trade_repository,
        ) as trade_repository_factory,
        patch.object(
            bootstrap,
            "create_trade_manager",
            return_value=trade_manager,
        ) as trade_manager_factory,
        patch.object(
            bootstrap,
            "ClosedTradeRepository",
            return_value=closed_trade_repository,
        ) as closed_repository_class,
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
        result = (
            bootstrap.create_dashboard_service(
                database_path=database_path,
            )
        )

    assert result is dashboard_service

    trade_journal_class.assert_called_once_with(
        database_path=database_path,
    )

    trade_repository_factory.assert_called_once_with(
        database_path=database_path,
    )

    trade_manager_factory.assert_called_once_with(
        trading_client=trading_client,
        trade_journal=trade_journal,
        trade_repository=trade_repository,
    )

    trade_manager.start_cycle.assert_called_once_with()

    closed_repository_class.assert_called_once_with(
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
        equity_curve=(
            bootstrap.EquityCurveCalculator
        ),
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


def test_create_trade_repository_uses_database_path(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "trades.db"

    repository = Mock(
        spec=SqliteTradeRepository,
    )

    with patch.object(
        bootstrap,
        "SqliteTradeRepository",
        return_value=repository,
    ) as repository_class:
        result = (
            bootstrap.create_trade_repository(
                database_path=database_path,
            )
        )

    assert result is repository

    repository_class.assert_called_once_with(
        database_path=database_path,
    )


def test_create_trade_manager_wires_position_management(
    tmp_path: Path,
) -> None:
    trading_client = Mock(
        name="trading-client",
    )

    trade_journal = Mock(
        name="trade-journal",
    )

    trade_repository = Mock(
        name="trade-repository",
    )

    position_management_service = Mock(
        name="position-management-service",
    )

    position_management_coordinator = Mock(
        name="position-management-coordinator",
    )

    lifecycle_engine = Mock(
        name="lifecycle-engine",
    )

    trade_manager = Mock(
        name="trade-manager",
    )

    with (
        patch.object(
            bootstrap,
            "PositionManagementService",
            return_value=position_management_service,
        ) as service_class,
        patch.object(
            bootstrap,
            "PositionManagementCoordinator",
            return_value=position_management_coordinator,
        ) as coordinator_class,
        patch.object(
            bootstrap,
            "TradeLifecycleEngine",
            return_value=lifecycle_engine,
        ) as lifecycle_engine_class,
        patch.object(
            bootstrap,
            "TradeManager",
            return_value=trade_manager,
        ) as trade_manager_class,
    ):
        result = bootstrap.create_trade_manager(
            trading_client=trading_client,
            trade_journal=trade_journal,
            trade_repository=trade_repository,
        )

    assert result is trade_manager

    service_class.assert_called_once_with(
        trading_client=trading_client,
        journal=trade_journal,
    )

    coordinator_class.assert_called_once_with(
        journal=trade_journal,
        management_service=(
            position_management_service
        ),
        historical_loader=(
            bootstrap.get_historical_bars
        ),
    )

    assert (
        lifecycle_engine_class
        .call_args
        .kwargs[
            "position_management_coordinator"
        ]
        is position_management_coordinator
    )

    trade_manager_class.assert_called_once_with(
        lifecycle_engine
    )