from unittest.mock import MagicMock

from application.trade_approval_factory import (
    create_trade_approval,
)


def test_create_trade_approval_returns_callable() -> None:
    approval = create_trade_approval(
        enabled=False,
    )

    assert callable(approval)

from unittest.mock import MagicMock


def test_create_trade_approval_returns_injected_approval_when_enabled() -> None:
    telegram_approval = MagicMock()

    approval = create_trade_approval(
        enabled=True,
        approval=telegram_approval,
    )

    assert approval is telegram_approval

from unittest.mock import MagicMock

from application.trade_approval_factory import (
    create_trade_approval,
)


def test_factory_uses_telegram_when_enabled(
    monkeypatch,
) -> None:
    from notifications.telegram_trade_approval import (
        TelegramTradeApproval,
    )

    telegram_approval = MagicMock()

    monkeypatch.setattr(
        "application.trade_approval_factory.TELEGRAM_APPROVAL_ENABLED",
        True,
        raising=False,
    )

    monkeypatch.setattr(
        "application.trade_approval_factory.TelegramTradeApproval",
        lambda: telegram_approval,
    )

    result = create_trade_approval(
        approval=MagicMock(),
    )

    assert result is telegram_approval