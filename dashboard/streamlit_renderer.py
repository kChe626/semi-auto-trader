from __future__ import annotations

from typing import Any, Protocol, Sequence

from dashboard.presentation_models import (
    AccountSectionViewModel,
)


class MetricContainerProtocol(Protocol):
    def metric(
        self,
        label: str,
        value: str,
        delta: str | None = None,
    ) -> Any:
        ...


class StreamlitProtocol(Protocol):
    def header(self, body: str) -> Any:
        ...

    def subheader(self, body: str) -> Any:
        ...

    def columns(
        self,
        spec: int,
    ) -> Sequence[MetricContainerProtocol]:
        ...

    def dataframe(
        self,
        data: Any,
        *,
        use_container_width: bool,
        hide_index: bool,
    ) -> Any:
        ...

    def info(self, body: str) -> Any:
        ...

    def caption(self, body: str) -> Any:
        ...


class StreamlitDashboardRenderer:
    """
    Renders presentation-ready dashboard models.

    This class does not access Alpaca, SQLite, analytics
    services, or trade execution services.
    """

    def __init__(
        self,
        *,
        streamlit_module: StreamlitProtocol,
    ) -> None:
        self._st = streamlit_module

    def render_account_section(
        self,
        account: AccountSectionViewModel,
    ) -> None:
        self._st.header("Account Overview")

        self._render_primary_metrics(account)
        self._render_secondary_metrics(account)

        self._st.caption(
            f"Account status: {account.metrics.status}"
        )

        self._render_positions(account)

    def _render_primary_metrics(
        self,
        account: AccountSectionViewModel,
    ) -> None:
        columns = self._st.columns(4)

        columns[0].metric(
            "Portfolio Value",
            account.metrics.portfolio_value,
            (
                f"{account.metrics.daily_change} "
                f"({account.metrics.daily_change_percent})"
            ),
        )

        columns[1].metric(
            "Equity",
            account.metrics.equity,
        )

        columns[2].metric(
            "Cash",
            account.metrics.cash,
        )

        columns[3].metric(
            "Buying Power",
            account.metrics.buying_power,
        )

    def _render_secondary_metrics(
        self,
        account: AccountSectionViewModel,
    ) -> None:
        columns = self._st.columns(2)

        columns[0].metric(
            "Trading Status",
            account.metrics.trading_status,
        )

        columns[1].metric(
            "Open Positions",
            str(len(account.positions)),
        )

    def _render_positions(
        self,
        account: AccountSectionViewModel,
    ) -> None:
        self._st.subheader("Open Positions")

        if not account.has_open_positions:
            self._st.info(
                "There are no open positions."
            )
            return

        rows = [
            {
                "Symbol": position.symbol,
                "Side": position.side,
                "Quantity": position.quantity,
                "Average Entry Price": (
                    position.average_entry_price
                ),
                "Current Price": (
                    position.current_price
                ),
                "Market Value": (
                    position.market_value
                ),
                "Cost Basis": position.cost_basis,
                "Unrealized P/L": (
                    position.unrealized_profit_loss
                ),
                "Unrealized P/L %": (
                    position
                    .unrealized_profit_loss_percent
                ),
            }
            for position in account.positions
        ]

        self._st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )