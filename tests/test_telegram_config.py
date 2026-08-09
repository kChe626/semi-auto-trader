from config.telegram_config import (
    TELEGRAM_APPROVAL_ENABLED,
)


def test_telegram_approval_defaults_disabled() -> None:
    assert TELEGRAM_APPROVAL_ENABLED is False


def test_telegram_config_reads_environment_values(
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

    monkeypatch.setenv(
        "TELEGRAM_READ_ONLY_CHAT_IDS",
        "222222,333333",
    )

    from config import telegram_config

    telegram_config.load_telegram_config()

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

    assert (
        telegram_config.TELEGRAM_READ_ONLY_CHAT_IDS
        == (
            222222,
            333333,
        )
    )


def test_telegram_config_defaults_read_only_ids_empty(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "TELEGRAM_APPROVAL_ENABLED",
        "false",
    )

    monkeypatch.delenv(
        "TELEGRAM_READ_ONLY_CHAT_IDS",
        raising=False,
    )

    from config import telegram_config

    telegram_config.load_telegram_config()

    assert (
        telegram_config.TELEGRAM_READ_ONLY_CHAT_IDS
        == ()
    )


def test_telegram_config_ignores_blank_read_only_values(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "TELEGRAM_APPROVAL_ENABLED",
        "false",
    )

    monkeypatch.setenv(
        "TELEGRAM_READ_ONLY_CHAT_IDS",
        "222222, ,333333,",
    )

    from config import telegram_config

    telegram_config.load_telegram_config()

    assert (
        telegram_config.TELEGRAM_READ_ONLY_CHAT_IDS
        == (
            222222,
            333333,
        )
    )


def test_telegram_config_rejects_enabled_without_credentials(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "TELEGRAM_APPROVAL_ENABLED",
        "true",
    )

    monkeypatch.delenv(
        "TELEGRAM_BOT_TOKEN",
        raising=False,
    )

    monkeypatch.delenv(
        "TELEGRAM_CHAT_ID",
        raising=False,
    )

    from config import telegram_config

    try:
        telegram_config.load_telegram_config()
    except ValueError as error:
        assert (
            "Telegram approval credentials are required"
            in str(error)
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )