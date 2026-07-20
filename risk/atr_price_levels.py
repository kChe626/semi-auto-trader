def calculate_atr_price_levels(
    entry_price: float,
    atr: float,
    signal_type: str,
    atr_multiplier: float = 2.0,
    reward_ratio: float = 2.0,
) -> tuple[float, float]:
    """
    Calculate stop-loss and target prices using ATR.

    Returns:
        tuple[float, float]: stop price, target price
    """
    if entry_price <= 0:
        raise ValueError("entry_price must be greater than zero")

    if atr <= 0:
        raise ValueError("atr must be greater than zero")

    if atr_multiplier <= 0:
        raise ValueError("atr_multiplier must be greater than zero")

    if reward_ratio <= 0:
        raise ValueError("reward_ratio must be greater than zero")

    normalized_signal = signal_type.upper()
    risk_distance = atr * atr_multiplier
    reward_distance = risk_distance * reward_ratio

    if normalized_signal == "BUY":
        stop_price = entry_price - risk_distance
        target_price = entry_price + reward_distance
    elif normalized_signal == "SELL":
        stop_price = entry_price + risk_distance
        target_price = entry_price - reward_distance
    else:
        raise ValueError("signal_type must be BUY or SELL")

    if stop_price <= 0 or target_price <= 0:
        raise ValueError("calculated price levels must be greater than zero")

    return round(stop_price, 2), round(target_price, 2)