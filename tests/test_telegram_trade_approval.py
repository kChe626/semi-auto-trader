from types import SimpleNamespace
from unittest.mock import MagicMock

from notifications.telegram_trade_approval import (
    TelegramTradeApproval,
)


def test_telegram_approval_returns_true_for_approve() -> None:
    request_response = MagicMock(
        return_value="APPROVE",
    )

    approval = TelegramTradeApproval(
        request_response=request_response,
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

    request_response.assert_called_once()

    message = (
        request_response
        .call_args
        .args[0]
    )

    assert "META" in message
    assert "BUY" in message
    assert "$100.00" in message
    assert "$98.00" in message
    assert "$104.00" in message
    assert "10" in message
    assert "APPROVE" in message
    assert "REJECT" in message

def test_telegram_approval_returns_false_for_reject() -> None:
    request_response = MagicMock(
        return_value="REJECT",
    )

    approval = TelegramTradeApproval(
        request_response=request_response,
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

def test_telegram_approval_ignores_case_and_whitespace() -> None:
    request_response = MagicMock(
        return_value="  approve  ",
    )

    approval = TelegramTradeApproval(
        request_response=request_response,
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

def test_telegram_approval_returns_false_when_request_fails() -> None:
    request_response = MagicMock(
        side_effect=TimeoutError(
            "Telegram response timed out"
        ),
    )

    approval = TelegramTradeApproval(
        request_response=request_response,
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