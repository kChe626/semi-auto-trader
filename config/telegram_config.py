from __future__ import annotations

import os


TELEGRAM_APPROVAL_ENABLED = False

TELEGRAM_BOT_TOKEN: str | None = None

TELEGRAM_CHAT_ID: int | None = None


def load_telegram_config() -> None:
    """
    Load Telegram approval configuration.

    Environment variables:
        TELEGRAM_APPROVAL_ENABLED
        TELEGRAM_BOT_TOKEN
        TELEGRAM_CHAT_ID

    Safe default:
        Telegram approval disabled.

    When enabled:
        Bot token and chat ID are required.
    """

    global TELEGRAM_APPROVAL_ENABLED
    global TELEGRAM_BOT_TOKEN
    global TELEGRAM_CHAT_ID

    enabled_value = os.getenv(
        "TELEGRAM_APPROVAL_ENABLED",
        "false",
    )

    TELEGRAM_APPROVAL_ENABLED = (
        enabled_value.strip().lower()
        in {
            "true",
            "1",
            "yes",
            "y",
        }
    )

    TELEGRAM_BOT_TOKEN = os.getenv(
        "TELEGRAM_BOT_TOKEN",
    )

    chat_id_value = os.getenv(
        "TELEGRAM_CHAT_ID",
    )

    if chat_id_value:
        TELEGRAM_CHAT_ID = int(chat_id_value)
    else:
        TELEGRAM_CHAT_ID = None

    if TELEGRAM_APPROVAL_ENABLED:
        if (
            not TELEGRAM_BOT_TOKEN
            or TELEGRAM_CHAT_ID is None
        ):
            raise ValueError(
                "Telegram approval credentials are required"
            )