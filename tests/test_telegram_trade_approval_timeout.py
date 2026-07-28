from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from notifications.telegram_trade_approval import (
    TelegramTradeApproval,
)


def test_approval_within_timeout_is_accepted() -> None:
    approval = TelegramTradeApproval(
        request_response=MagicMock(
            return_value="APPROVE TRD-123",
        ),
        approval_timeout_seconds=300,
        clock=lambda: datetime.now(timezone.utc),
    )

    plan = SimpleNamespace(
        trade_id="TRD-123",
        symbol="NVDA",
        signal_type="BUY",
        entry_price=175,
        stop_price=170,
        target_price=185,
        quantity=10,
    )

    assert approval(plan) is True


def test_expired_approval_is_rejected() -> None:
    created = datetime.now(
        timezone.utc
    ) - timedelta(
        seconds=301
    )

    approval = TelegramTradeApproval(
        request_response=MagicMock(
            return_value="APPROVE TRD-123",
        ),
        approval_timeout_seconds=300,
        clock=lambda: datetime.now(timezone.utc),
    )

    plan = SimpleNamespace(
        trade_id="TRD-123",
        approval_requested_at=created,
        symbol="NVDA",
        signal_type="BUY",
        entry_price=175,
        stop_price=170,
        target_price=185,
        quantity=10,
    )

    assert approval(plan) is False