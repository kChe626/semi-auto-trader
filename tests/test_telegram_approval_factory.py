from unittest.mock import MagicMock

from notifications.telegram_approval_factory import (
    create_telegram_trade_approval,
)


def test_factory_returns_callable_approval() -> None:
    send_message = MagicMock()
    receive_reply = MagicMock(
        return_value="APPROVE",
    )

    approval = create_telegram_trade_approval(
        send_message=send_message,
        receive_reply=receive_reply,
    )

    assert callable(approval)

from types import SimpleNamespace


def test_factory_uses_authorized_polling() -> None:
    send_message = MagicMock()

    updates = iter(
        [
            {
                "update_id": 100,
                "chat_id": 999,
                "text": "APPROVE",
            },
            {
                "update_id": 101,
                "chat_id": 123,
                "text": "APPROVE",
            },
        ]
    )

    fetch_update = MagicMock(
        side_effect=lambda: next(updates),
    )

    approval = create_telegram_trade_approval(
        send_message=send_message,
        receive_reply=lambda: "",
        fetch_update=fetch_update,
        authorized_chat_id=123,
        minimum_update_id=100,
        max_attempts=5,
    )

    plan = SimpleNamespace(
        symbol="META",
        signal_type="BUY",
        entry_price=100.00,
        stop_price=98.00,
        target_price=104.00,
        quantity=10,
    )

    result = approval(plan)

    assert result is True
    assert send_message.call_count == 1
    assert fetch_update.call_count == 2

from types import SimpleNamespace


def test_factory_fails_closed_for_incomplete_polling_configuration() -> None:
    receive_reply = MagicMock(
        return_value="APPROVE",
    )
    fetch_update = MagicMock()

    approval = create_telegram_trade_approval(
        send_message=MagicMock(),
        receive_reply=receive_reply,
        fetch_update=fetch_update,
    )

    plan = SimpleNamespace(
        symbol="META",
        signal_type="BUY",
        entry_price=100.00,
        stop_price=98.00,
        target_price=104.00,
        quantity=10,
    )

    result = approval(plan)

    assert result is False
    receive_reply.assert_not_called()
    fetch_update.assert_not_called()

from notifications.telegram_bot_api import (
    TelegramBotApi,
)


def test_factory_can_build_from_telegram_api() -> None:
    api = TelegramBotApi(
        bot_token="test-token",
        chat_id=123456,
        post=MagicMock(),
        get=MagicMock(),
    )

    approval = create_telegram_trade_approval(
        telegram_api=api,
    )

    assert callable(approval)