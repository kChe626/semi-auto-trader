from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Protocol

from config.trading_config import (
    ALLOW_LONG_TRADES,
    ALLOW_SHORT_TRADES,
)
from dashboard.account_service import (
    AccountDashboardData,
)
from dashboard.dashboard_service import DashboardData
from models.trade_signal import TradeSignal
from models.workflow_result import WorkflowResult
from scanner.trade_ranker import rank_trade_plans


class DashboardAnalyticsServiceProtocol(Protocol):
    """
    Operations required from the dashboard analytics
    service.
    """

    def load_dashboard_data(
        self,
        *,
        starting_equity: float,
    ) -> DashboardData:
        ...


class DashboardAccountServiceProtocol(Protocol):
    """
    Operations required from the dashboard account
    service.
    """

    def load_account_data(
        self,
    ) -> AccountDashboardData:
        ...


class TradeWorkflowProtocol(Protocol):
    """
    Operations required from the trade workflow.
    """

    def prepare_trade(
        self,
        signal: TradeSignal,
    ) -> WorkflowResult:
        ...


ScannerLoader = Callable[
    [],
    Iterable[TradeSignal],
]


@dataclass(frozen=True)
class CompleteDashboardData:
    """
    Complete read-only dashboard snapshot.
    """

    account_data: AccountDashboardData
    scanner_signals: tuple[TradeSignal, ...]
    workflow_result: WorkflowResult | None
    analytics_data: DashboardData


class DashboardCompositionService:
    """
    Coordinate the backend services required to build
    one complete dashboard snapshot.
    """

    def __init__(
        self,
        *,
        account_service: DashboardAccountServiceProtocol,
        scanner_loader: ScannerLoader,
        trade_workflow: TradeWorkflowProtocol,
        analytics_service: (
            DashboardAnalyticsServiceProtocol
        ),
    ) -> None:
        self._account_service = account_service
        self._scanner_loader = scanner_loader
        self._trade_workflow = trade_workflow
        self._analytics_service = analytics_service

    def load_complete_dashboard_data(
        self,
    ) -> CompleteDashboardData:
        account_data = (
            self._account_service.load_account_data()
        )

        scanner_signals = tuple(
            self._scanner_loader()
        )

        workflow_result = (
            self._select_best_workflow(
                scanner_signals
            )
        )

        analytics_data = (
            self._analytics_service.load_dashboard_data(
                starting_equity=(
                    account_data.account.equity
                ),
            )
        )

        return CompleteDashboardData(
            account_data=account_data,
            scanner_signals=scanner_signals,
            workflow_result=workflow_result,
            analytics_data=analytics_data,
        )

    def _select_best_workflow(
        self,
        scanner_signals: tuple[TradeSignal, ...],
    ) -> WorkflowResult | None:
        if not scanner_signals:
            return None

        eligible_workflows: list[
            WorkflowResult
        ] = []

        for signal in scanner_signals:
            if not self._direction_is_allowed(
                signal.signal_type
            ):
                continue

            try:
                workflow = (
                    self._trade_workflow
                    .prepare_trade(
                        signal
                    )
                )
            except Exception:
                continue

            eligible_workflows.append(
                workflow
            )

        if not eligible_workflows:
            return None

        workflow_by_plan_id = {
            id(workflow.plan): workflow
            for workflow in eligible_workflows
        }

        ranked_trades = rank_trade_plans(
            [
                workflow.plan
                for workflow in eligible_workflows
            ]
        )

        best_trade = ranked_trades[0]

        return workflow_by_plan_id[
            id(best_trade.plan)
        ]

    @staticmethod
    def _direction_is_allowed(
        signal_type: str,
    ) -> bool:
        normalized = str(
            signal_type
        ).strip().upper()

        if normalized == "BUY":
            return ALLOW_LONG_TRADES

        if normalized == "SELL":
            return ALLOW_SHORT_TRADES

        return False