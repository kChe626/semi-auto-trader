from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Protocol

from dashboard.account_service import (
    AccountDashboardData,
)
from dashboard.dashboard_service import DashboardData
from models.trade_signal import TradeSignal


class DashboardAnalyticsServiceProtocol(Protocol):
    """
    Minimum analytics-service operation required by the
    dashboard composition service.
    """

    def load_dashboard_data(
        self,
        *,
        starting_equity: float,
    ) -> DashboardData:
        ...


class DashboardAccountServiceProtocol(Protocol):
    """
    Minimum account-service operation required by the
    dashboard composition service.
    """

    def load_account_data(
        self,
    ) -> AccountDashboardData:
        ...


ScannerLoader = Callable[
    [],
    Iterable[TradeSignal],
]


@dataclass(frozen=True)
class CompleteDashboardData:
    """
    Complete read-only dashboard snapshot.

    This combines broker account data, scanner signals,
    and closed-trade analytics without introducing
    Streamlit dependencies.
    """

    account_data: AccountDashboardData
    scanner_signals: tuple[TradeSignal, ...]
    analytics_data: DashboardData


class DashboardCompositionService:
    """
    Coordinates the dashboard's account, scanner, and
    analytics backend services.

    This service performs orchestration only. It does not
    calculate analytics, access SQLite directly, call
    Streamlit, or submit broker orders.
    """

    def __init__(
        self,
        *,
        account_service: DashboardAccountServiceProtocol,
        scanner_loader: ScannerLoader,
        analytics_service: (
            DashboardAnalyticsServiceProtocol
        ),
    ) -> None:
        self._account_service = account_service
        self._scanner_loader = scanner_loader
        self._analytics_service = analytics_service

    def load_complete_dashboard_data(
        self,
    ) -> CompleteDashboardData:
        """
        Load one complete dashboard snapshot.
        """

        account_data = (
            self._account_service.load_account_data()
        )

        scanner_signals = tuple(
            self._scanner_loader()
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
            analytics_data=analytics_data,
        )