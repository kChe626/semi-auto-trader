from unittest.mock import Mock, call, patch

import pytest

from notifications import telegram_notifier


def test_send_telegram_message_sends_to_owner_only(
) -> None:
    response = Mock()
    response.raise_for_status.return_value = None

    with (
        patch.dict(
            "os.environ",
            {
                "TELEGRAM_BOT_TOKEN": "test-token",
                "TELEGRAM_CHAT_ID": "111111",
                "TELEGRAM_READ_ONLY_CHAT_IDS": "",
            },
            clear=False,
        ),
        patch.object(
            telegram_notifier.requests,
            "post",
            return_value=response,
        ) as post,
    ):
        result = (
            telegram_notifier
            .send_telegram_message(
                "Test message"
            )
        )

    assert result is True

    post.assert_called_once_with(
        (
            "https://api.telegram.org/"
            "bottest-token/sendMessage"
        ),
        data={
            "chat_id": 111111,
            "text": "Test message",
        },
        timeout=10,
    )

    response.raise_for_status.assert_called_once_with()


def test_send_telegram_message_sends_to_read_only_recipients(
) -> None:
    response = Mock()
    response.raise_for_status.return_value = None

    with (
        patch.dict(
            "os.environ",
            {
                "TELEGRAM_BOT_TOKEN": "test-token",
                "TELEGRAM_CHAT_ID": "111111",
                "TELEGRAM_READ_ONLY_CHAT_IDS": (
                    "222222,333333"
                ),
            },
            clear=False,
        ),
        patch.object(
            telegram_notifier.requests,
            "post",
            return_value=response,
        ) as post,
    ):
        result = (
            telegram_notifier
            .send_telegram_message(
                "Trade alert"
            )
        )

    assert result is True

    assert post.call_args_list == [
        call(
            (
                "https://api.telegram.org/"
                "bottest-token/sendMessage"
            ),
            data={
                "chat_id": 111111,
                "text": "Trade alert",
            },
            timeout=10,
        ),
        call(
            (
                "https://api.telegram.org/"
                "bottest-token/sendMessage"
            ),
            data={
                "chat_id": 222222,
                "text": "Trade alert",
            },
            timeout=10,
        ),
        call(
            (
                "https://api.telegram.org/"
                "bottest-token/sendMessage"
            ),
            data={
                "chat_id": 333333,
                "text": "Trade alert",
            },
            timeout=10,
        ),
    ]


def test_send_telegram_message_deduplicates_recipients(
) -> None:
    response = Mock()
    response.raise_for_status.return_value = None

    with (
        patch.dict(
            "os.environ",
            {
                "TELEGRAM_BOT_TOKEN": "test-token",
                "TELEGRAM_CHAT_ID": "111111",
                "TELEGRAM_READ_ONLY_CHAT_IDS": (
                    "111111,222222,222222"
                ),
            },
            clear=False,
        ),
        patch.object(
            telegram_notifier.requests,
            "post",
            return_value=response,
        ) as post,
    ):
        telegram_notifier.send_telegram_message(
            "Trade alert"
        )

    assert post.call_count == 2

    sent_chat_ids = [
        item.kwargs["data"]["chat_id"]
        for item in post.call_args_list
    ]

    assert sent_chat_ids == [
        111111,
        222222,
    ]


def test_send_telegram_message_requires_bot_token(
) -> None:
    with patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "",
            "TELEGRAM_CHAT_ID": "111111",
        },
        clear=False,
    ):
        with pytest.raises(
            ValueError,
            match="Missing TELEGRAM_BOT_TOKEN",
        ):
            telegram_notifier.send_telegram_message(
                "Test"
            )


def test_send_telegram_message_requires_owner_chat_id(
) -> None:
    with patch.dict(
        "os.environ",
        {
            "TELEGRAM_BOT_TOKEN": "test-token",
            "TELEGRAM_CHAT_ID": "",
        },
        clear=False,
    ):
        with pytest.raises(
            ValueError,
            match="Missing TELEGRAM_CHAT_ID",
        ):
            telegram_notifier.send_telegram_message(
                "Test"
            )