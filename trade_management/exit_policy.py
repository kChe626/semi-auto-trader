from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ExitAction(StrEnum):
    HOLD = "HOLD"
    MOVE_STOP_TO_BREAKEVEN = (
        "MOVE_STOP_TO_BREAKEVEN"
    )
    CLOSE = "CLOSE"


@dataclass(frozen=True)
class ExitDecision:
    action: ExitAction
    reason: str


def evaluate_exit(
    *,
    entry_price: float,
    initial_stop_price: float,
    current_price: float,
    short_sma: float,
    long_sma: float,
    trading_days_held: int,
) -> ExitDecision:
    """
    Evaluate active position-management rules.

    Priority:
    1. Hard exit at 7 trading days.
    2. From day 3 onward, exit on trend failure.
    3. Move stop to breakeven after +1R.
    4. Otherwise hold.
    """

    if entry_price <= 0:
        raise ValueError(
            "entry_price must be greater than zero"
        )

    if initial_stop_price <= 0:
        raise ValueError(
            "initial_stop_price must be "
            "greater than zero"
        )

    if current_price <= 0:
        raise ValueError(
            "current_price must be greater than zero"
        )

    if initial_stop_price >= entry_price:
        raise ValueError(
            "initial_stop_price must be "
            "below entry_price"
        )

    if trading_days_held < 0:
        raise ValueError(
            "trading_days_held cannot be negative"
        )

    # 1. Hard maximum holding period.
    if trading_days_held >= 7:
        return ExitDecision(
            action=ExitAction.CLOSE,
            reason=(
                "Maximum holding period reached."
            ),
        )

    # 2. Trend-management rules begin on day 3.
    if trading_days_held >= 3:
        if current_price < short_sma:
            return ExitDecision(
                action=ExitAction.CLOSE,
                reason=(
                    "Price closed below "
                    "the short SMA."
                ),
            )

        if short_sma < long_sma:
            return ExitDecision(
                action=ExitAction.CLOSE,
                reason=(
                    "Short SMA crossed below "
                    "the long SMA."
                ),
            )

    # 3. Protect a trade once it reaches +1R.
    risk_per_share = (
        entry_price - initial_stop_price
    )

    one_r_price = (
        entry_price + risk_per_share
    )

    if current_price >= one_r_price:
        return ExitDecision(
            action=(
                ExitAction
                .MOVE_STOP_TO_BREAKEVEN
            ),
            reason="Price reached +1R.",
        )

    # 4. Otherwise continue holding.
    if trading_days_held <= 2:
        return ExitDecision(
            action=ExitAction.HOLD,
            reason=(
                "Position is still within "
                "the initial holding window."
            ),
        )

    return ExitDecision(
        action=ExitAction.HOLD,
        reason="Trend remains healthy.",
    )