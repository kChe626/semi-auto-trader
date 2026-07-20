from alpaca.trading.enums import (
    OrderClass,
    OrderSide,
    TimeInForce,
)
from alpaca.trading.requests import (
    MarketOrderRequest,
    StopLossRequest,
    TakeProfitRequest,
)

from models.trade_plan import TradePlan


def build_bracket_order_request(
    plan: TradePlan,
) -> MarketOrderRequest:
    """
    Convert a TradePlan into an Alpaca bracket-order request.

    This function only builds the request object.
    It does not submit an order.
    """
    signal_type = plan.signal_type.upper()

    if signal_type not in {"BUY", "SELL"}:
        raise ValueError("Signal type must be BUY or SELL.")

    if plan.quantity <= 0:
        raise ValueError("Order quantity must be greater than zero.")

    if plan.entry_price <= 0:
        raise ValueError("Entry price must be greater than zero.")

    if plan.stop_price <= 0:
        raise ValueError("Stop price must be greater than zero.")

    if plan.target_price <= 0:
        raise ValueError("Target price must be greater than zero.")

    if signal_type == "BUY":
        side = OrderSide.BUY

        if plan.stop_price >= plan.entry_price:
            raise ValueError(
                "For a BUY order, stop price must be below entry price."
            )

        if plan.target_price <= plan.entry_price:
            raise ValueError(
                "For a BUY order, target price must be above entry price."
            )

    else:
        side = OrderSide.SELL

        if plan.stop_price <= plan.entry_price:
            raise ValueError(
                "For a SELL order, stop price must be above entry price."
            )

        if plan.target_price >= plan.entry_price:
            raise ValueError(
                "For a SELL order, target price must be below entry price."
            )

    return MarketOrderRequest(
        symbol=plan.symbol,
        qty=plan.quantity,
        side=side,
        time_in_force=TimeInForce.DAY,
        order_class=OrderClass.BRACKET,
        take_profit=TakeProfitRequest(
            limit_price=round(plan.target_price, 2),
        ),
        stop_loss=StopLossRequest(
            stop_price=round(plan.stop_price, 2),
        ),
    )