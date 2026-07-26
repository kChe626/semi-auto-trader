from __future__ import annotations

from typing import Protocol

from dashboard.complete_presentation_models import (
    CompleteDashboardViewModel,
)
from dashboard.composition_service import (
    CompleteDashboardData,
)


class AccountPresentationMapperProtocol(Protocol):
    def map_account_section(
        self,
        account_data,
    ):
        ...


class ScannerPresentationMapperProtocol(Protocol):
    def map_scanner_section(
        self,
        signals,
    ):
        ...


class AnalyticsPresentationMapperProtocol(Protocol):
    def map_analytics_section(
        self,
        analytics_data,
    ):
        ...


class TradeHistoryPresentationMapperProtocol(Protocol):
    def map(
        self,
        closed_trades,
    ):
        ...


class CompleteDashboardPresentationMapper:
    """
    Maps a complete dashboard data snapshot into the
    complete dashboard presentation model.
    """

    def __init__(
        self,
        *,
        account_mapper: AccountPresentationMapperProtocol,
        scanner_mapper: ScannerPresentationMapperProtocol,
        analytics_mapper: AnalyticsPresentationMapperProtocol,
        trade_history_mapper: (
            TradeHistoryPresentationMapperProtocol
        ),
    ) -> None:
        self._account_mapper = account_mapper
        self._scanner_mapper = scanner_mapper
        self._analytics_mapper = analytics_mapper
        self._trade_history_mapper = trade_history_mapper

    def map_dashboard(
        self,
        dashboard_data: CompleteDashboardData,
    ) -> CompleteDashboardViewModel:
        account = (
            self._account_mapper.map_account_section(
                dashboard_data.account_data
            )
        )

        scanner = (
            self._scanner_mapper.map_scanner_section(
                dashboard_data.scanner_signals
            )
        )

        analytics = (
            self._analytics_mapper.map_analytics_section(
                dashboard_data.analytics_data
            )
        )

        trade_history = (
            self._trade_history_mapper.map(
                dashboard_data
                .analytics_data
                .closed_trades
            )
        )

        return CompleteDashboardViewModel(
            account=account,
            scanner=scanner,
            analytics=analytics,
            trade_history=trade_history,
        )