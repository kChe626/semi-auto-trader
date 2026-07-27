import pytest

from unittest.mock import MagicMock

from notifications.telegram_approval_client import (
    TelegramApprovalClient,
)


def test_request_response_sends_message_and_returns_reply() -> None:
    send_message = MagicMock()
    receive_reply = MagicMock(
        return_value="APPROVE",
    )

    client = TelegramApprovalClient(
        send_message=send_message,
        receive_reply=receive_reply,
    )

    result = client.request_response(
        "Approve META?"
    )

    assert result == "APPROVE"

    send_message.assert_called_once_with(
        "Approve META?"
    )
    receive_reply.assert_called_once()
     
def test_request_response_does_not_receive_when_send_fails() -> None:
    send_message = MagicMock(
        side_effect=ConnectionError(
            "Telegram send failed"
        ),
    )
    receive_reply = MagicMock()

    client = TelegramApprovalClient(
        send_message=send_message,
        receive_reply=receive_reply,
    )

    with pytest.raises(
        ConnectionError,
        match="Telegram send failed",
    ):
        client.request_response(
            "Approve META?"
        )

    receive_reply.assert_not_called()

def test_receive_reply_ignores_unauthorized_chat() -> None:
    updates = iter(
        [
            {
                "chat_id": 999,
                "text": "APPROVE",
            },
            {
                "chat_id": 123,
                "text": "REJECT",
            },
        ]
    )

    fetch_update = MagicMock(
        side_effect=lambda: next(updates),
    )

    client = TelegramApprovalClient(
        send_message=MagicMock(),
        receive_reply=lambda: "",
    )

    result = client.receive_authorized_reply(
        fetch_update=fetch_update,
        authorized_chat_id=123,
    )

    assert result == "REJECT"
    assert fetch_update.call_count == 2

def test_receive_reply_ignores_invalid_commands() -> None:
    updates = iter(
        [
            {
                "chat_id": 123,
                "text": "hello",
            },
            {
                "chat_id": 123,
                "text": "APPROVE",
            },
        ]
    )

    fetch_update = MagicMock(
        side_effect=lambda: next(updates),
    )

    client = TelegramApprovalClient(
        send_message=MagicMock(),
        receive_reply=lambda: "",
    )

    result = client.receive_authorized_reply(
        fetch_update=fetch_update,
        authorized_chat_id=123,
    )

    assert result == "APPROVE"
    assert fetch_update.call_count == 2

def test_receive_reply_ignores_updates_before_request() -> None:
    updates = iter(
        [
            {
                "update_id": 100,
                "chat_id": 123,
                "text": "APPROVE",
            },
            {
                "update_id": 102,
                "chat_id": 123,
                "text": "REJECT",
            },
        ]
    )

    fetch_update = MagicMock(
        side_effect=lambda: next(updates),
    )

    client = TelegramApprovalClient(
        send_message=MagicMock(),
        receive_reply=lambda: "",
    )

    result = client.receive_authorized_reply(
        fetch_update=fetch_update,
        authorized_chat_id=123,
        minimum_update_id=101,
    )

    assert result == "REJECT"
    assert fetch_update.call_count == 2

def test_receive_reply_returns_reject_after_max_attempts() -> None:
    fetch_update = MagicMock(
        return_value={
            "update_id": 200,
            "chat_id": 999,
            "text": "APPROVE",
        }
    )

    client = TelegramApprovalClient(
        send_message=MagicMock(),
        receive_reply=lambda: "",
    )

    result = client.receive_authorized_reply(
        fetch_update=fetch_update,
        authorized_chat_id=123,
        max_attempts=3,
    )

    assert result == "REJECT"
    assert fetch_update.call_count == 3

def test_request_response_uses_authorized_reply_polling() -> None:
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

    client = TelegramApprovalClient(
        send_message=send_message,
        receive_reply=lambda: "",
    )

    result = client.request_response(
        "Approve META?",
        fetch_update=fetch_update,
        authorized_chat_id=123,
        minimum_update_id=100,
        max_attempts=5,
    )

    assert result == "APPROVE"

    send_message.assert_called_once_with(
        "Approve META?"
    )

    assert fetch_update.call_count == 2

def test_request_response_rejects_incomplete_polling_configuration() -> None:
    send_message = MagicMock()
    receive_reply = MagicMock(
        return_value="APPROVE",
    )
    fetch_update = MagicMock()

    client = TelegramApprovalClient(
        send_message=send_message,
        receive_reply=receive_reply,
    )

    result = client.request_response(
        "Approve META?",
        fetch_update=fetch_update,
    )

    assert result == "REJECT"
    receive_reply.assert_not_called()
    fetch_update.assert_not_called()

def test_receive_reply_rejects_non_positive_max_attempts() -> None:
    fetch_update = MagicMock()

    client = TelegramApprovalClient(
        send_message=MagicMock(),
        receive_reply=lambda: "",
    )

    result = client.receive_authorized_reply(
        fetch_update=fetch_update,
        authorized_chat_id=123,
        max_attempts=0,
    )

    assert result == "REJECT"
    fetch_update.assert_not_called()