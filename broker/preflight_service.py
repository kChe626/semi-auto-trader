from alpaca.trading.client import TradingClient
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest

from models.preflight_result import PreflightResult
from models.trade_plan import TradePlan
from risk.preflight_checker import check_trade_preflight


def run_broker_preflight(
    client: TradingClient,
    plan: TradePlan,
) -> PreflightResult:
    """
    Retrieve current Alpaca account state and run trade preflight checks.

    This function does not submit an order.
    """
    account = client.get_account()
    clock = client.get_clock()
    positions = client.get_all_positions()

    open_orders = client.get_orders(
        filter=GetOrdersRequest(
            status=QueryOrderStatus.OPEN,
        )
    )

    symbol = plan.symbol.upper()

    has_existing_position = any(
        position.symbol.upper() == symbol
        for position in positions
    )

    has_open_order = any(
        order.symbol.upper() == symbol
        for order in open_orders
    )

    return check_trade_preflight(
        plan,
        market_is_open=bool(clock.is_open),
        buying_power=float(account.buying_power),
        trading_blocked=bool(account.trading_blocked),
        has_existing_position=has_existing_position,
        has_open_order=has_open_order,
    )