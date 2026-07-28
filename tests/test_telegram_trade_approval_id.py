from unittest.mock import MagicMock

from notifications.telegram_trade_approval import (
    TelegramTradeApproval,
)


class Plan:
    symbol = "NVDA"
    signal_type = "BUY"
    quantity = 10
    entry_price = 175.00
    stop_price = 170.00
    target_price = 185.00
    trade_id = "TRD-123"


def test_telegram_approval_requires_matching_trade_id() -> None:
    approval = TelegramTradeApproval(
        request_response=MagicMock(
            return_value="APPROVE TRD-123",
        ),
    )

    result = approval(
        Plan(),
    )

    assert result is True


def test_telegram_approval_rejects_wrong_trade_id() -> None:
    approval = TelegramTradeApproval(
        request_response=MagicMock(
            return_value="APPROVE TRD-999",
        ),
    )

    result = approval(
        Plan(),
    )

    assert result is False