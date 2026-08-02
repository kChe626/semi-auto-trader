from pathlib import Path

from execution.sqlite_telegram_update_repository import (
    SqliteTelegramUpdateRepository,
)
from notifications.telegram_approval_client import (
    TelegramApprovalClient,
)


def test_duplicate_update_is_blocked_after_restart(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "trades.db"

    repository = (
        SqliteTelegramUpdateRepository(
            database_path=database_path,
        )
    )

    repository.save_last_update_id(
        100
    )

    updates = iter(
        [
            {
                "update_id": 100,
                "chat_id": 123,
                "text": "APPROVE TRD-123",
            },
            {
                "update_id": 101,
                "chat_id": 123,
                "text": "APPROVE TRD-456",
            },
        ]
    )

    client = TelegramApprovalClient(
        send_message=lambda message: None,
        receive_reply=lambda: "REJECT",
        update_repository=repository,
    )

    result = client.receive_authorized_reply(
        fetch_update=lambda: next(updates),
        authorized_chat_id=123,
    )

    assert result == "APPROVE TRD-456"

    assert (
        repository.get_last_update_id()
        == 101
    )