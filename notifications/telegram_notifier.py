from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()


def _get_bot_token() -> str:
    bot_token = os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )

    if not bot_token:
        raise ValueError(
            "Missing TELEGRAM_BOT_TOKEN in .env"
        )

    return bot_token


def _get_owner_chat_id() -> int:
    chat_id = os.getenv(
        "TELEGRAM_CHAT_ID"
    )

    if not chat_id:
        raise ValueError(
            "Missing TELEGRAM_CHAT_ID in .env"
        )

    return int(chat_id)


def _get_read_only_chat_ids() -> tuple[int, ...]:
    value = os.getenv(
        "TELEGRAM_READ_ONLY_CHAT_IDS",
        "",
    )

    return tuple(
        int(chat_id.strip())
        for chat_id in value.split(",")
        if chat_id.strip()
    )


def _send_to_chat(
    *,
    bot_token: str,
    chat_id: int,
    message: str,
) -> None:
    url = (
        "https://api.telegram.org/"
        f"bot{bot_token}/sendMessage"
    )

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message,
        },
        timeout=10,
    )

    response.raise_for_status()


def send_telegram_message(
    message: str,
) -> bool:
    """
    Send a Telegram notification to the owner and
    all configured read-only recipients.

    Read-only recipients receive messages only.
    They are not authorized to approve trades.
    """

    bot_token = _get_bot_token()

    owner_chat_id = _get_owner_chat_id()

    read_only_chat_ids = (
        _get_read_only_chat_ids()
    )

    recipient_ids = (
        owner_chat_id,
        *read_only_chat_ids,
    )

    unique_recipient_ids = tuple(
        dict.fromkeys(
            recipient_ids
        )
    )

    for chat_id in unique_recipient_ids:
        _send_to_chat(
            bot_token=bot_token,
            chat_id=chat_id,
            message=message,
        )

    return True


if __name__ == "__main__":
    send_telegram_message(
        "Semi Auto Trader connected successfully!"
    )