from __future__ import annotations

from collections.abc import Callable

from notifications.telegram_trade_approval import (
    TelegramTradeApproval,
)


def create_trade_approval(
    *,
    enabled: bool,
    approval: Callable | None = None,
) -> Callable:
    if not enabled:
        return lambda plan: True

    if approval is None:
        raise ValueError(
            "approval dependency is required when enabled"
        )

    return approval