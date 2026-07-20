import math


def cap_position_size(
    quantity: int,
    entry_price: float,
    account_equity: float,
    max_position_percent: float,
) -> int:
    """
    Limit a position so it cannot exceed a percentage of account equity.
    """
    if quantity <= 0:
        return 0

    maximum_position_value = (
        account_equity * max_position_percent
    )

    maximum_quantity = math.floor(
        maximum_position_value / entry_price
    )

    return min(quantity, maximum_quantity)