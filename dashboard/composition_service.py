from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Protocol

from dashboard.account_service import (
    AccountDashboardData,
)
from dashboard.dashboard_service import DashboardData
from models.trade_signal import TradeSignal
from models.workflow_result import WorkflowResult


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

    Combines account data, scanner signals, the prepared
    trade workflow result, and trade analytics without
    introducing presentation-layer dependencies.
    """

    account_data: AccountDashboardData
    scanner_signals: tuple[TradeSignal, ...]
    workflow_result: WorkflowResult
    analytics_data: DashboardData


class DashboardCompositionService:
    """
    Coordinate the backend services required to build one
    complete dashboard snapshot.

    This service performs orchestration only. It does not
    render Streamlit components, calculate analytics,
    access SQLite directly, or submit broker orders.
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
        """
        Load one complete dashboard snapshot.

        The first scanner signal is prepared for manual
        trade approval.
        """

        account_data = (
            self._account_service.load_account_data()
        )

        scanner_signals = tuple(
            self._scanner_loader()
        )

        workflow_result = (
            self._trade_workflow.prepare_trade(
                scanner_signals[0]
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