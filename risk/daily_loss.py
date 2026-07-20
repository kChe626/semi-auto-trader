def calculate_daily_pnl(
    current_equity: float,
    previous_equity: float,
) -> float:
    """
    Calculate today's account-level profit or loss.

    A negative result represents a loss.
    """
    return current_equity - previous_equity


def calculate_daily_loss_limit(
    previous_equity: float,
    max_daily_loss_percent: float,
) -> float:
    """
    Return the maximum permitted daily loss in dollars.
    """
    if previous_equity <= 0:
        raise ValueError(
            "Previous equity must be greater than zero."
        )

    if not 0 < max_daily_loss_percent < 1:
        raise ValueError(
            "Maximum daily loss percent must be between 0 and 1."
        )

    return previous_equity * max_daily_loss_percent


def daily_loss_limit_reached(
    current_equity: float,
    previous_equity: float,
    max_daily_loss_percent: float,
) -> bool:
    """
    Return True when the account has reached or exceeded
    the configured daily loss limit.
    """
    daily_pnl = calculate_daily_pnl(
        current_equity=current_equity,
        previous_equity=previous_equity,
    )

    maximum_loss = calculate_daily_loss_limit(
        previous_equity=previous_equity,
        max_daily_loss_percent=max_daily_loss_percent,
    )

    return daily_pnl <= -maximum_loss