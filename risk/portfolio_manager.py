from alpaca.trading.client import TradingClient
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest

from config.trading_config import (
    MAX_DAILY_LOSS_PERCENT,
    MAX_OPEN_TRADES,
)
from risk.daily_loss import (
    calculate_daily_loss_limit,
    calculate_daily_pnl,
    daily_loss_limit_reached,
)


class PortfolioManager:
    """
    Enforce portfolio-level trading limits.
    """

    def __init__(
        self,
        trading_client: TradingClient,
    ) -> None:
        self._client = trading_client

    def can_open_new_trade(self) -> tuple[bool, str]:
        positions = self._client.get_all_positions()

        open_orders = self._client.get_orders(
            filter=GetOrdersRequest(
                status=QueryOrderStatus.OPEN,
            )
        )

        active_symbols = {
            position.symbol.upper()
            for position in positions
        }

        active_symbols.update(
            order.symbol.upper()
            for order in open_orders
            if getattr(order, "symbol", None)
        )

        if len(active_symbols) >= MAX_OPEN_TRADES:
            return (
                False,
                "Maximum active trades "
                f"({MAX_OPEN_TRADES}) reached.",
            )

        account = self._client.get_account()

        current_equity = float(account.equity)
        previous_equity = float(account.last_equity)

        if daily_loss_limit_reached(
            current_equity=current_equity,
            previous_equity=previous_equity,
            max_daily_loss_percent=MAX_DAILY_LOSS_PERCENT,
        ):
            daily_pnl = calculate_daily_pnl(
                current_equity=current_equity,
                previous_equity=previous_equity,
            )

            maximum_loss = calculate_daily_loss_limit(
                previous_equity=previous_equity,
                max_daily_loss_percent=MAX_DAILY_LOSS_PERCENT,
            )

            return (
                False,
                "Daily loss limit reached: "
                f"P/L ${daily_pnl:,.2f}, "
                f"limit -${maximum_loss:,.2f}.",
            )

        return True, ""