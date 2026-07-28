from unittest.mock import MagicMock

from application.trade_approval_factory import (
    create_trade_approval,
)


def test_factory_builds_telegram_approval_chain(
    monkeypatch,
) -> None:
    telegram_approval = MagicMock()

    monkeypatch.setattr(
        "application.trade_approval_factory.TELEGRAM_APPROVAL_ENABLED",
        True,
        raising=False,
    )

    monkeypatch.setattr(
        "application.trade_approval_factory.create_telegram_trade_approval",
        lambda: telegram_approval,
    )

    result = create_trade_approval()

    assert result is telegram_approval