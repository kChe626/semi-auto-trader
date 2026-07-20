from models.preflight_result import PreflightResult
from models.trade_plan import TradePlan


def check_trade_preflight(
    plan: TradePlan,
    *,
    market_is_open: bool,
    buying_power: float,
    trading_blocked: bool,
    has_existing_position: bool,
    has_open_order: bool,
    allow_short_selling: bool = False,
) -> PreflightResult:
    """
    Validate a trade plan before it may be submitted to the broker.

    Every failed rule is returned so the user can see all reasons
    the proposed trade was rejected.
    """
    reasons: list[str] = []

    signal_type = plan.signal_type.upper()
    position_value = plan.entry_price * plan.quantity

    if signal_type not in {"BUY", "SELL"}:
        reasons.append(
            f"Unsupported signal type: {plan.signal_type}."
        )

    if signal_type == "SELL" and not allow_short_selling:
        reasons.append("Short selling is disabled.")

    if not market_is_open:
        reasons.append("Market is closed.")

    if trading_blocked:
        reasons.append("Account is blocked from trading.")

    if plan.quantity <= 0:
        reasons.append(
            "Trade quantity must be greater than zero."
        )

    if buying_power < position_value:
        reasons.append(
            "Insufficient buying power: "
            f"requires ${position_value:,.2f}, "
            f"available ${buying_power:,.2f}."
        )

    if has_existing_position:
        reasons.append(
            f"An existing position already exists for "
            f"{plan.symbol}."
        )

    if has_open_order:
        reasons.append(
            f"An open order already exists for "
            f"{plan.symbol}."
        )

    return PreflightResult(
        approved=not reasons,
        reasons=reasons,
    )