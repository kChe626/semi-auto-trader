from alpaca.trading.client import TradingClient

from config.trading_config import MAX_OPEN_TRADES


class PortfolioManager:
    """
    Portfolio-level risk checks.

    Determines whether the account is allowed
    to open another position.
    """

    def __init__(
        self,
        trading_client: TradingClient,
    ) -> None:
        self._client = trading_client

    def can_open_new_trade(self) -> tuple[bool, str]:
        """
        Returns:
            (True, "") if another trade is allowed.

            (False, reason) otherwise.
        """
        positions = self._client.get_all_positions()

        if len(positions) >= MAX_OPEN_TRADES:
            return (
                False,
                f"Maximum open trades ({MAX_OPEN_TRADES}) reached.",
            )

        return True, ""