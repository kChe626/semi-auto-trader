from __future__ import annotations

from dashboard.account_service import (
    AccountDashboardData,
    OpenPosition,
)
from dashboard.presentation_models import (
    AccountMetricsViewModel,
    AccountSectionViewModel,
    PositionRowViewModel,
)


class AccountPresentationMapper:
    """
    Converts normalized account-domain data into
    display-ready dashboard values.

    This mapper contains formatting logic only. It does
    not call Alpaca, SQLite, analytics calculators, or
    Streamlit.
    """

    def map_account_section(
        self,
        account_data: AccountDashboardData,
    ) -> AccountSectionViewModel:
        daily_change = (
            account_data.account.equity
            - account_data.account.last_equity
        )

        daily_change_percent = (
            self._calculate_change_percent(
                current_value=account_data.account.equity,
                previous_value=(
                    account_data.account.last_equity
                ),
            )
        )

        positions = tuple(
            self._map_position(position)
            for position in account_data.open_positions
        )

        return AccountSectionViewModel(
            metrics=AccountMetricsViewModel(
                status=account_data.account.status,
                cash=self._format_currency(
                    account_data.account.cash
                ),
                equity=self._format_currency(
                    account_data.account.equity
                ),
                buying_power=self._format_currency(
                    account_data.account.buying_power
                ),
                portfolio_value=self._format_currency(
                    account_data.account.portfolio_value
                ),
                daily_change=self._format_signed_currency(
                    daily_change
                ),
                daily_change_percent=(
                    self._format_signed_percent(
                        daily_change_percent
                    )
                ),
                trading_status=(
                    self._build_trading_status(
                        trading_blocked=(
                            account_data
                            .account
                            .trading_blocked
                        ),
                        account_blocked=(
                            account_data
                            .account
                            .account_blocked
                        ),
                    )
                ),
            ),
            positions=positions,
            has_open_positions=bool(positions),
        )

    def _map_position(
        self,
        position: OpenPosition,
    ) -> PositionRowViewModel:
        return PositionRowViewModel(
            symbol=position.symbol,
            side=position.side.title(),
            quantity=self._format_quantity(
                position.quantity
            ),
            average_entry_price=self._format_currency(
                position.average_entry_price
            ),
            current_price=self._format_currency(
                position.current_price
            ),
            market_value=self._format_currency(
                position.market_value
            ),
            cost_basis=self._format_currency(
                position.cost_basis
            ),
            unrealized_profit_loss=(
                self._format_signed_currency(
                    position.unrealized_profit_loss
                )
            ),
            unrealized_profit_loss_percent=(
                self._format_signed_percent(
                    position
                    .unrealized_profit_loss_percent
                )
            ),
        )

    @staticmethod
    def _calculate_change_percent(
        *,
        current_value: float,
        previous_value: float,
    ) -> float:
        if previous_value == 0:
            return 0.0

        return (
            current_value - previous_value
        ) / previous_value

    @staticmethod
    def _format_currency(
        value: float,
    ) -> str:
        return f"${value:,.2f}"

    @staticmethod
    def _format_signed_currency(
        value: float,
    ) -> str:
        sign = "+" if value >= 0 else "-"

        return f"{sign}${abs(value):,.2f}"

    @staticmethod
    def _format_signed_percent(
        value: float,
    ) -> str:
        return f"{value:+.2%}"

    @staticmethod
    def _format_quantity(
        value: float,
    ) -> str:
        if value.is_integer():
            return str(int(value))

        return f"{value:.4f}".rstrip("0").rstrip(".")

    @staticmethod
    def _build_trading_status(
        *,
        trading_blocked: bool,
        account_blocked: bool,
    ) -> str:
        if account_blocked:
            return "Account Blocked"

        if trading_blocked:
            return "Trading Blocked"

        return "Trading Enabled"