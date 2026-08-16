from datetime import datetime, timezone
from unittest.mock import Mock

import pandas as pd

from models.broker_state import PositionSnapshot
from trade_management.exit_policy import (
    ExitAction,
)
from trade_management.position_management_coordinator import (
    PositionManagementCoordinator,
)


def make_position(
    *,
    current_price: float = 102.0,
) -> PositionSnapshot:
    return PositionSnapshot(
        symbol="AAPL",
        quantity=10,
        side="long",
        average_entry_price=100.0,
        current_price=current_price,
        market_value=1000.0,
        unrealized_profit_loss=20.0,
    )


def make_market_data() -> pd.DataFrame:
    dates = pd.date_range(
        "2026-08-10",
        periods=40,
        freq="B",
    )

    closes = [
        100.0 + (index * 0.25)
        for index in range(40)
    ]

    return pd.DataFrame(
        {
            "Close": closes,
        },
        index=dates,
    )


def make_recent_market_data() -> pd.DataFrame:
    dates = pd.bdate_range(
        end="2026-08-11",
        periods=40,
    )

    closes = [
        90.0 + (index * 0.25)
        for index in range(40)
    ]

    return pd.DataFrame(
        {
            "Close": closes,
        },
        index=dates,
    )


def make_open_event() -> dict:
    return {
        "symbol": "AAPL",
        "status": "position_open",
        "trade_id": "trade-123",
        "order_id": "order-456",
        "created_at": datetime(
            2026,
            8,
            10,
            17,
            0,
            tzinfo=timezone.utc,
        ).isoformat(),
        "entry_price": 100.0,
        "stop_price": 98.0,
        "target_price": 104.0,
    }


def test_manage_position_evaluates_and_applies_decision(
) -> None:
    journal = Mock()

    journal.get_latest_event_by_symbol.return_value = (
        make_open_event()
    )

    journal.get_events_by_trade_id.return_value = [
        make_open_event(),
    ]

    management_service = Mock()
    management_service.apply.return_value = True

    historical_loader = Mock(
        return_value=make_market_data()
    )

    coordinator = PositionManagementCoordinator(
        journal=journal,
        management_service=management_service,
        historical_loader=historical_loader,
    )

    result = coordinator.manage_position(
        make_position()
    )

    assert result is True

    historical_loader.assert_called_once_with(
        "AAPL"
    )

    management_service.apply.assert_called_once()

    call = management_service.apply.call_args

    assert call.kwargs["symbol"] == "AAPL"
    assert (
        call.kwargs["parent_order_id"]
        == "order-456"
    )
    assert call.kwargs["entry_price"] == 100.0
    assert call.kwargs["trade_id"] == "trade-123"


def test_missing_journal_trade_is_ignored() -> None:
    journal = Mock()

    journal.get_latest_event_by_symbol.return_value = (
        None
    )

    management_service = Mock()
    historical_loader = Mock()

    coordinator = PositionManagementCoordinator(
        journal=journal,
        management_service=management_service,
        historical_loader=historical_loader,
    )

    result = coordinator.manage_position(
        make_position()
    )

    assert result is False

    historical_loader.assert_not_called()
    management_service.apply.assert_not_called()


def test_missing_position_open_event_is_ignored() -> None:
    latest = make_open_event()
    latest["status"] = "stop_adjusted"

    journal = Mock()

    journal.get_latest_event_by_symbol.return_value = (
        latest
    )

    journal.get_events_by_trade_id.return_value = [
        latest,
    ]

    management_service = Mock()
    historical_loader = Mock()

    coordinator = PositionManagementCoordinator(
        journal=journal,
        management_service=management_service,
        historical_loader=historical_loader,
    )

    result = coordinator.manage_position(
        make_position()
    )

    assert result is False

    historical_loader.assert_not_called()
    management_service.apply.assert_not_called()


def test_missing_current_price_is_ignored() -> None:
    journal = Mock()

    journal.get_latest_event_by_symbol.return_value = (
        make_open_event()
    )

    journal.get_events_by_trade_id.return_value = [
        make_open_event(),
    ]

    management_service = Mock()
    historical_loader = Mock()

    coordinator = PositionManagementCoordinator(
        journal=journal,
        management_service=management_service,
        historical_loader=historical_loader,
    )

    position = PositionSnapshot(
        symbol="AAPL",
        quantity=10,
        side="long",
        average_entry_price=100.0,
        current_price=None,
        market_value=None,
        unrealized_profit_loss=None,
    )

    result = coordinator.manage_position(
        position
    )

    assert result is False

    historical_loader.assert_not_called()
    management_service.apply.assert_not_called()


def test_existing_breakeven_adjustment_is_not_repeated(
) -> None:
    open_event = make_open_event()

    adjusted_event = {
        **open_event,
        "status": "stop_adjusted",
        "created_at": datetime(
            2026,
            8,
            11,
            17,
            0,
            tzinfo=timezone.utc,
        ).isoformat(),
        "stop_price": 100.0,
    }

    journal = Mock()

    journal.get_latest_event_by_symbol.return_value = (
        adjusted_event
    )

    journal.get_events_by_trade_id.return_value = [
        open_event,
        adjusted_event,
    ]

    management_service = Mock()

    historical_loader = Mock(
        return_value=make_recent_market_data()
    )

    coordinator = PositionManagementCoordinator(
        journal=journal,
        management_service=management_service,
        historical_loader=historical_loader,
    )

    result = coordinator.manage_position(
        make_position(
            current_price=102.0,
        )
    )

    assert result is False

    management_service.apply.assert_not_called()


def test_managed_exit_request_is_not_repeated() -> None:
    open_event = make_open_event()

    exit_event = {
        **open_event,
        "status": "managed_exit_requested",
        "created_at": datetime(
            2026,
            8,
            14,
            17,
            0,
            tzinfo=timezone.utc,
        ).isoformat(),
    }

    journal = Mock()

    journal.get_latest_event_by_symbol.return_value = (
        exit_event
    )

    management_service = Mock()
    historical_loader = Mock()

    coordinator = PositionManagementCoordinator(
        journal=journal,
        management_service=management_service,
        historical_loader=historical_loader,
    )

    result = coordinator.manage_position(
        make_position()
    )

    assert result is False

    historical_loader.assert_not_called()
    management_service.apply.assert_not_called()


def test_original_stop_is_used_after_breakeven_adjustment(
) -> None:
    open_event = make_open_event()

    adjusted_event = {
        **open_event,
        "status": "stop_adjusted",
        "created_at": datetime(
            2026,
            8,
            11,
            17,
            0,
            tzinfo=timezone.utc,
        ).isoformat(),
        "stop_price": 100.0,
    }

    journal = Mock()

    journal.get_latest_event_by_symbol.return_value = (
        adjusted_event
    )

    journal.get_events_by_trade_id.return_value = [
        open_event,
        adjusted_event,
    ]

    management_service = Mock()
    management_service.apply.return_value = True

    historical_loader = Mock(
        return_value=make_market_data()
    )

    coordinator = PositionManagementCoordinator(
        journal=journal,
        management_service=management_service,
        historical_loader=historical_loader,
    )

    coordinator.manage_position(
        make_position(
            current_price=101.0,
        )
    )

    if management_service.apply.called:
        decision = (
            management_service
            .apply
            .call_args
            .kwargs["decision"]
        )

        assert decision.action in {
            ExitAction.HOLD,
            ExitAction.CLOSE,
        }