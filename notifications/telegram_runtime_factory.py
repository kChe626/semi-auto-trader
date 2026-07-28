from __future__ import annotations

from notifications.telegram_approval_factory import (
    create_telegram_trade_approval,
)

from notifications.telegram_bot_api import (
    TelegramBotApi,
)


def create_runtime_telegram_approval(
    *,
    bot_token: str,
    chat_id: int,
):
    telegram_api = TelegramBotApi(
        bot_token=bot_token,
        chat_id=chat_id,
        post=_default_post,
        get=_default_get,
    )

    return create_telegram_trade_approval(
        telegram_api=telegram_api,
        authorized_chat_id=chat_id,
    )


def _default_post(*args, **kwargs):
    import requests

    return requests.post(
        *args,
        **kwargs,
    )


def _default_get(*args, **kwargs):
    import requests

    return requests.get(
        *args,
        **kwargs,
    )