from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from broker.order_verifier import verify_submitted_order


def test_verify_submitted_order_returns_order() -> None:
    client = MagicMock()

    expected_order = SimpleNamespace(
        id="paper-order-123",
        symbol="META",
        status="accepted",
    )

    client.get_order_by_id.return_value = expected_order

    result = verify_submitted_order(
        client=client,
        order_id="paper-order-123",
    )

    assert result is expected_order

    client.get_order_by_id.assert_called_once_with(
        "paper-order-123"
    )


def test_verify_submitted_order_rejects_missing_id() -> None:
    client = MagicMock()

    with pytest.raises(
        ValueError,
        match="without an order ID",
    ):
        verify_submitted_order(
            client=client,
            order_id=None,
        )

    client.get_order_by_id.assert_not_called()


def test_verify_submitted_order_propagates_api_error() -> None:
    client = MagicMock()

    client.get_order_by_id.side_effect = RuntimeError(
        "Alpaca API unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="Alpaca API unavailable",
    ):
        verify_submitted_order(
            client=client,
            order_id="paper-order-123",
        )