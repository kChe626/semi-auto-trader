from unittest.mock import MagicMock

from notifications.telegram_runtime_factory import (
    create_runtime_telegram_approval,
)


def test_runtime_factory_builds_telegram_approval(
    monkeypatch,
) -> None:
    telegram_approval = MagicMock()

    monkeypatch.setattr(
        "notifications.telegram_runtime_factory.create_telegram_trade_approval",
        lambda **kwargs: telegram_approval,
    )

    result = create_runtime_telegram_approval(
        bot_token="test-token",
        chat_id=123456,
    )

    assert result is telegram_approval