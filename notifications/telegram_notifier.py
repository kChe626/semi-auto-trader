import os

import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(message: str) -> bool:
    """
    Send a Telegram message.

    Returns True if successful.
    """
    if not BOT_TOKEN:
        raise ValueError(
            "Missing TELEGRAM_BOT_TOKEN in .env"
        )

    if not CHAT_ID:
        raise ValueError(
            "Missing TELEGRAM_CHAT_ID in .env"
        )

    url = (
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    )

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
        },
        timeout=10,
    )

    response.raise_for_status()

    return True


if __name__ == "__main__":
    send_telegram_message(
        "✅ Semi Auto Trader connected successfully!"
    )