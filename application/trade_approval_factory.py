from __future__ import annotations

from collections.abc import Callable

from config.telegram_config import (
    TELEGRAM_APPROVAL_ENABLED,
)

from notifications.telegram_trade_approval import (
    TelegramTradeApproval,
)


def create_trade_approval(
    *,
    enabled: bool | None = None,
    approval: Callable | None = None,
) -> Callable:
    """
    Create trade approval handler.

    Backward compatible:
    - enabled=True + approval -> injected approval
    - enabled=False -> safe fallback

    Production:
    - no explicit enabled flag -> Telegram config decides
    """

    if enabled is not None:
        if approval is not None:
            return approval

        return lambda plan: True

    if TELEGRAM_APPROVAL_ENABLED:
        return TelegramTradeApproval()

    if approval is not None:
        return approval

    return lambda plan: True