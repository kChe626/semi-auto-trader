from __future__ import annotations

from collections.abc import Callable

from notifications.telegram_approval_client import (
    TelegramApprovalClient,
)
from notifications.telegram_bot_api import (
    TelegramBotApi,
)
from notifications.telegram_trade_approval import (
    TelegramTradeApproval,
)


def create_telegram_trade_approval(
    *,
    send_message: Callable[[str], None] | None = None,
    receive_reply: Callable[[], str] | None = None,
    fetch_update: Callable[[], dict] | None = None,
    authorized_chat_id: int | None = None,
    minimum_update_id: int | None = None,
    max_attempts: int | None = None,
    telegram_api: TelegramBotApi | None = None,
) -> TelegramTradeApproval:
    if telegram_api is not None:
        send_message = telegram_api.send_message
        fetch_update = telegram_api.fetch_update

    if send_message is None:
        raise ValueError(
            "send_message is required"
        )

    if receive_reply is None:
        receive_reply = lambda: "REJECT"

    client = TelegramApprovalClient(
        send_message=send_message,
        receive_reply=receive_reply,
    )

    def request_response(
        message: str,
    ) -> str:
        return client.request_response(
            message,
            fetch_update=fetch_update,
            authorized_chat_id=authorized_chat_id,
            minimum_update_id=minimum_update_id,
            max_attempts=max_attempts,
        )

    return TelegramTradeApproval(
        request_response=request_response,
    )