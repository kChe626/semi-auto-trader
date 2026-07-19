from models.trade_plan import TradePlan
from risk.position_sizer import calculate_position_size


def build_trade_plan(
    symbol: str,
    signal_type: str,
    account_equity: float,
    risk_percent: float,
    entry_price: float,
    stop_price: float,
    target_price: float,
) -> TradePlan:
    """
    Build a complete trade plan from a signal and risk settings.
    """
    normalized_signal_type = signal_type.upper()

    if normalized_signal_type not in {"BUY", "SELL"}:
        raise ValueError("Signal type must be BUY or SELL.")

    if entry_price <= 0 or stop_price <= 0 or target_price <= 0:
        raise ValueError("Entry, stop, and target prices must be greater than zero.")

    if normalized_signal_type == "BUY":
        if stop_price >= entry_price:
            raise ValueError("For a BUY trade, stop price must be below entry price.")

        if target_price <= entry_price:
            raise ValueError("For a BUY trade, target price must be above entry price.")

        risk_per_share = entry_price - stop_price
        reward_per_share = target_price - entry_price

    else:
        if stop_price <= entry_price:
            raise ValueError("For a SELL trade, stop price must be above entry price.")

        if target_price >= entry_price:
            raise ValueError("For a SELL trade, target price must be below entry price.")

        risk_per_share = stop_price - entry_price
        reward_per_share = entry_price - target_price

    quantity = calculate_position_size(
        account_equity=account_equity,
        risk_percent=risk_percent,
        entry_price=entry_price,
        stop_price=stop_price,
    )

    total_risk = quantity * risk_per_share
    risk_reward_ratio = reward_per_share / risk_per_share

    return TradePlan(
        symbol=symbol,
        signal_type=normalized_signal_type,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=target_price,
        quantity=quantity,
        risk_per_share=risk_per_share,
        reward_per_share=reward_per_share,
        total_risk=total_risk,
        risk_reward_ratio=risk_reward_ratio,
    )