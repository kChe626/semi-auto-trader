from notifications.telegram_approval_client import (
    TelegramApprovalClient,
)


def test_duplicate_update_id_is_ignored() -> None:
    updates = iter(
        [
            {
                "update_id": 100,
                "chat_id": 123,
                "text": "APPROVE TRD-OLD",
            },
            {
                "update_id": 100,
                "chat_id": 123,
                "text": "APPROVE TRD-DUPLICATE",
            },
            {
                "update_id": 101,
                "chat_id": 123,
                "text": "APPROVE TRD-NEW",
            },
        ]
    )

    client = TelegramApprovalClient(
        send_message=lambda message: None,
        receive_reply=lambda: "REJECT",
    )

    first = client.receive_authorized_reply(
        fetch_update=lambda: next(updates),
        authorized_chat_id=123,
    )

    second = client.receive_authorized_reply(
        fetch_update=lambda: next(updates),
        authorized_chat_id=123,
    )

    assert first == "APPROVE TRD-OLD"
    assert second == "APPROVE TRD-NEW"


def test_older_update_id_is_ignored() -> None:
    client = TelegramApprovalClient(
        send_message=lambda message: None,
        receive_reply=lambda: "REJECT",
    )

    updates = iter(
        [
            {
                "update_id": 99,
                "chat_id": 123,
                "text": "APPROVE OLD",
            },
            {
                "update_id": 101,
                "chat_id": 123,
                "text": "APPROVE NEW",
            },
        ]
    )

    result = client.receive_authorized_reply(
        fetch_update=lambda: next(updates),
        authorized_chat_id=123,
        minimum_update_id=100,
    )

    assert result == "APPROVE NEW"