from types import SimpleNamespace
from unittest.mock import MagicMock

from broker.preflight_service import run_broker_preflight
from models.trade_plan import TradePlan


def create_test_plan() -> TradePlan:
    return TradePlan(
        symbol="META",
        signal_type="BUY",
        entry_price=100.00,
        stop_price=98.00,
        target_price=104.00,
        quantity=10,
        risk_per_share=2.00,
        reward_per_share=4.00,
        total_risk=20.00,
        risk_reward_ratio=2.00,
    )


def create_mock_client() -> MagicMock:
    client = MagicMock()

    client.get_account.return_value = SimpleNamespace(
        buying_power="10000.00",
        trading_blocked=False,
    )

    client.get_clock.return_value = SimpleNamespace(
        is_open=True,
    )

    client.get_all_positions.return_value = []
    client.get_orders.return_value = []

    return client


def test_broker_preflight_approves_valid_trade() -> None:
    client = create_mock_client()

    result = run_broker_preflight(
        client=client,
        plan=create_test_plan(),
    )

    assert result.approved is True
    assert result.reasons == []

    client.get_account.assert_called_once()
    client.get_clock.assert_called_once()
    client.get_all_positions.assert_called_once()
    client.get_orders.assert_called_once()


def test_broker_preflight_detects_existing_position() -> None:
    client = create_mock_client()

    client.get_all_positions.return_value = [
        SimpleNamespace(symbol="META"),
    ]

    result = run_broker_preflight(
        client=client,
        plan=create_test_plan(),
    )

    assert result.approved is False
    assert any(
        "existing position" in reason
        for reason in result.reasons
    )


def test_broker_preflight_detects_open_order() -> None:
    client = create_mock_client()

    client.get_orders.return_value = [
        SimpleNamespace(symbol="META"),
    ]

    result = run_broker_preflight(
        client=client,
        plan=create_test_plan(),
    )

    assert result.approved is False
    assert any(
        "open order" in reason
        for reason in result.reasons
    )


def test_broker_preflight_rejects_closed_market() -> None:
    client = create_mock_client()
    client.get_clock.return_value = SimpleNamespace(
        is_open=False,
    )

    result = run_broker_preflight(
        client=client,
        plan=create_test_plan(),
    )

    assert result.approved is False
    assert "Market is closed." in result.reasons


def test_broker_preflight_rejects_blocked_account() -> None:
    client = create_mock_client()
    client.get_account.return_value = SimpleNamespace(
        buying_power="10000.00",
        trading_blocked=True,
    )

    result = run_broker_preflight(
        client=client,
        plan=create_test_plan(),
    )

    assert result.approved is False
    assert "Account is blocked from trading." in result.reasons