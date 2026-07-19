import math


def calculate_position_size(
    account_equity: float,
    risk_percent: float,
    entry_price: float,
    stop_price: float,
) -> int:
    """
    Calculate the number of shares allowed based on account risk.

    Example:
        Account equity: $10,000
        Risk percent:   1%
        Entry price:    $100
        Stop price:     $95

        Maximum account risk = $100
        Risk per share = $5
        Position size = 20 shares
    """
    if account_equity <= 0:
        raise ValueError("Account equity must be greater than zero.")

    if not 0 < risk_percent <= 1:
        raise ValueError(
            "Risk percent must be greater than zero and no more than 1."
        )

    if entry_price <= 0 or stop_price <= 0:
        raise ValueError("Entry and stop prices must be greater than zero.")

    risk_per_share = abs(entry_price - stop_price)

    if risk_per_share == 0:
        raise ValueError("Entry price and stop price cannot be equal.")

    maximum_risk = account_equity * risk_percent
    quantity = math.floor(maximum_risk / risk_per_share)

    return quantity