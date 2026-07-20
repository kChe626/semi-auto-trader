from alpaca.trading.client import TradingClient

from broker.order_builder import build_bracket_order_request
from models.trade_plan import TradePlan


class OrderExecutor:
    """
    Submit approved trade plans to Alpaca.
    """

    def __init__(self, trading_client: TradingClient) -> None:
        self._client = trading_client

    def submit_bracket_order(self, plan: TradePlan):
        """
        Build and submit a bracket order.

        Returns the Alpaca Order object.
        """
        request = build_bracket_order_request(plan)

        order = self._client.submit_order(
            order_data=request,
        )

        return order