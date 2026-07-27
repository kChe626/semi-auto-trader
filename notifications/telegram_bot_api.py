from __future__ import annotations

from collections.abc import Callable
from typing import Any


class TelegramBotApi:
    def __init__(
        self,
        *,
        bot_token: str,
        chat_id: int,
        post: Callable[..., Any],
        get: Callable[..., Any] | None = None,
    ) -> None:
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._post = post
        self._get = get

    def send_message(self, message: str) -> None:
        url = (
            f"https://api.telegram.org/"
            f"bot{self._bot_token}/sendMessage"
        )

        response = self._post(
            url,
            json={
                "chat_id": self._chat_id,
                "text": message,
            },
            timeout=10,
        )

        response.raise_for_status()

    def fetch_update(self) -> dict:
        if self._get is None:
            raise RuntimeError(
                "Telegram GET transport is not configured."
            )

        url = (
            f"https://api.telegram.org/"
            f"bot{self._bot_token}/getUpdates"
        )

        response = self._get(
            url,
            params={
                "timeout": 10,
            },
            timeout=15,
        )

        response.raise_for_status()

        payload = response.json()
        results = payload.get("result", [])

        if not results:
            return {}

        update = results[-1]
        message = update.get("message", {})
        chat = message.get("chat", {})

        return {
            "update_id": update.get("update_id"),
            "chat_id": chat.get("id"),
            "text": message.get("text", ""),
        }