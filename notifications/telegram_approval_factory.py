from __future__ import annotations

from collections.abc import Callable

from notifications.telegram_approval_client import (
    TelegramApprovalClient,
)
from notifications.telegram_trade_approval import (
    TelegramTradeApproval,
)


def create_telegram_trade_approval(
    *,
    send_message: Callable[[str], None],
    receive_reply: Callable[[], str],
    fetch_update: Callable[[], dict] | None = None,
    authorized_chat_id: int | None = None,
    minimum_update_id: int | None = None,
    max_attempts: int | None = None,
) -> TelegramTradeApproval:
    client = TelegramApprovalClient(
        send_message=send_message,
        receive_reply=receive_reply,
    )

    def request_response(message: str) -> str:
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