from collections.abc import Callable
from typing import Any


NotificationSender = Callable[[str], bool]


def send_notification_safely(
    notification_sender: NotificationSender | None,
    message: str,
) -> None:
    """
    Send a notification without allowing notification failures
    to stop the trading workflow.
    """
    if notification_sender is None:
        return

    try:
        notification_sender(message)
    except Exception as error:
        print(
            "\nTelegram notification failed: "
            f"{error}"
        )


def format_trade_alert(
    plan: Any,
    score: float,
) -> str:
    """
    Format a trade opportunity for Telegram.
    """
    rsi = getattr(plan, "rsi", None)

    rsi_text = (
        f"{rsi:.2f}"
        if rsi is not None
        else "Unavailable"
    )

    return (
        "🚨 TRADE OPPORTUNITY\n\n"
        f"Symbol: {plan.symbol}\n"
        f"Side: {plan.signal_type}\n"
        f"Score: {score:.2f}\n\n"
        f"Entry: ${plan.entry_price:,.2f}\n"
        f"Stop: ${plan.stop_price:,.2f}\n"
        f"Target: ${plan.target_price:,.2f}\n"
        f"Quantity: {plan.quantity}\n\n"
        f"Risk per share: "
        f"${plan.risk_per_share:,.2f}\n"
        f"Total risk: ${plan.total_risk:,.2f}\n"
        f"Reward/Risk: "
        f"{plan.risk_reward_ratio:.2f}\n"
        f"RSI: {rsi_text}\n\n"
        "Waiting for terminal approval."
    )