import os

from config.telegram_config import (
    load_telegram_config,
)


def test_load_telegram_config_reads_dotenv_values(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "TELEGRAM_APPROVAL_ENABLED",
        "true",
    )

    monkeypatch.setenv(
        "TELEGRAM_BOT_TOKEN",
        "test-token",
    )

    monkeypatch.setenv(
        "TELEGRAM_CHAT_ID",
        "123456",
    )

    from config import telegram_config

    load_telegram_config()

    assert (
        telegram_config.TELEGRAM_APPROVAL_ENABLED
        is True
    )

    assert (
        telegram_config.TELEGRAM_BOT_TOKEN
        == "test-token"
    )

    assert (
        telegram_config.TELEGRAM_CHAT_ID
        == 123456
    )