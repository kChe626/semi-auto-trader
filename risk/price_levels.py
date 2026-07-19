def calculate_price_levels(
    signal_type: str,
    entry_price: float,
    stop_loss_percent: float = 0.02,
    reward_risk_ratio: float = 2.0,
) -> tuple[float, float]:
    """
    Calculate stop and target prices from an entry price.

    Example BUY:
        Entry:  $100
        Stop:   2% below entry = $98
        Risk:   $2 per share
        Target: 2:1 reward/risk = $104

    Example SELL:
        Entry:  $100
        Stop:   2% above entry = $102
        Target: $96
    """
    normalized_signal_type = signal_type.upper()

    if normalized_signal_type not in {"BUY", "SELL"}:
        raise ValueError("Signal type must be BUY or SELL.")

    if entry_price <= 0:
        raise ValueError("Entry price must be greater than zero.")

    if not 0 < stop_loss_percent < 1:
        raise ValueError(
            "Stop-loss percent must be greater than zero and less than 1."
        )

    if reward_risk_ratio <= 0:
        raise ValueError("Reward-risk ratio must be greater than zero.")

    risk_per_share = entry_price * stop_loss_percent

    if normalized_signal_type == "BUY":
        stop_price = entry_price - risk_per_share
        target_price = entry_price + (
            risk_per_share * reward_risk_ratio
        )
    else:
        stop_price = entry_price + risk_per_share
        target_price = entry_price - (
            risk_per_share * reward_risk_ratio
        )

    return round(stop_price, 2), round(target_price, 2)