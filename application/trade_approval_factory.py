from __future__ import annotations

from collections.abc import Callable

from config.telegram_config import (
    TELEGRAM_APPROVAL_ENABLED,
)

from notifications.telegram_approval_factory import (
    create_telegram_trade_approval,
)


def create_trade_approval(
    *,
    enabled: bool | None = None,
    approval: Callable | None = None,
) -> Callable:
    """
    Create the trade approval handler.

    Behavior:
    - Explicit enabled flag preserves existing test/injection behavior.
    - Production mode uses Telegram configuration.
    - Disabled Telegram falls back safely.

    Architecture:
    application layer decides WHICH approval provider.
    notifications layer builds Telegram implementation.
    """

    # Backward compatibility:
    # Existing callers can inject an approval handler.
    if enabled is not None:
        if approval is not None:
            return approval

        return lambda plan: True

    # Production Telegram path.
    if TELEGRAM_APPROVAL_ENABLED:
        return create_telegram_trade_approval()

    # Optional injected approval fallback.
    if approval is not None:
        return approval

    # Safe paper-trading fallback.
    return lambda plan: True