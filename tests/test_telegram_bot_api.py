from unittest.mock import MagicMock

from notifications.telegram_bot_api import (
    TelegramBotApi,
)


def test_send_message_posts_to_telegram_api() -> None:
    post = MagicMock()

    api = TelegramBotApi(
        bot_token="test-token",
        chat_id=123456,
        post=post,
    )

    api.send_message("Approve META trade?")

    post.assert_called_once_with(
        "https://api.telegram.org/bottest-token/sendMessage",
        json={
            "chat_id": 123456,
            "text": "Approve META trade?",
        },
        timeout=10,
    )

def test_send_message_raises_for_http_error() -> None:
    response = MagicMock()
    post = MagicMock(
        return_value=response,
    )

    api = TelegramBotApi(
        bot_token="test-token",
        chat_id=123456,
        post=post,
    )

    api.send_message("Approve META trade?")

    response.raise_for_status.assert_called_once_with()

def test_fetch_update_requests_latest_telegram_update() -> None:
    response = MagicMock()
    response.json.return_value = {
        "ok": True,
        "result": [
            {
                "update_id": 101,
                "message": {
                    "chat": {
                        "id": 123456,
                    },
                    "text": "APPROVE",
                },
            }
        ],
    }

    get = MagicMock(
        return_value=response,
    )

    api = TelegramBotApi(
        bot_token="test-token",
        chat_id=123456,
        post=MagicMock(),
        get=get,
    )

    update = api.fetch_update()

    get.assert_called_once_with(
        "https://api.telegram.org/bottest-token/getUpdates",
        params={
            "timeout": 10,
        },
        timeout=15,
    )

    response.raise_for_status.assert_called_once_with()

    assert update == {
        "update_id": 101,
        "chat_id": 123456,
        "text": "APPROVE",
    }

def test_fetch_update_returns_empty_dict_when_no_updates_exist() -> None:
    response = MagicMock()
    response.json.return_value = {
        "ok": True,
        "result": [],
    }

    api = TelegramBotApi(
        bot_token="test-token",
        chat_id=123456,
        post=MagicMock(),
        get=MagicMock(return_value=response),
    )

    result = api.fetch_update()

    assert result == {}
    response.raise_for_status.assert_called_once_with()