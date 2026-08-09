from unittest.mock import Mock, patch

import pytest

from broker import alpaca_client


def test_create_trading_client_uses_paper_mode(
) -> None:
    trading_client = Mock(
        name="trading-client"
    )

    with (
        patch.dict(
            "os.environ",
            {
                "ALPACA_API_KEY": "test-key",
                "ALPACA_SECRET_KEY": "test-secret",
            },
            clear=False,
        ),
        patch.object(
            alpaca_client,
            "TradingClient",
            return_value=trading_client,
        ) as trading_client_class,
    ):
        result = (
            alpaca_client.create_trading_client()
        )

    assert result is trading_client

    trading_client_class.assert_called_once_with(
        "test-key",
        "test-secret",
        paper=True,
    )


def test_create_trading_client_requires_api_key(
) -> None:
    with patch.dict(
        "os.environ",
        {
            "ALPACA_API_KEY": "",
            "ALPACA_SECRET_KEY": "test-secret",
        },
        clear=False,
    ):
        with pytest.raises(
            ValueError,
            match=(
                "Missing ALPACA_API_KEY "
                "or ALPACA_SECRET_KEY"
            ),
        ):
            alpaca_client.create_trading_client()


def test_create_trading_client_requires_secret_key(
) -> None:
    with patch.dict(
        "os.environ",
        {
            "ALPACA_API_KEY": "test-key",
            "ALPACA_SECRET_KEY": "",
        },
        clear=False,
    ):
        with pytest.raises(
            ValueError,
            match=(
                "Missing ALPACA_API_KEY "
                "or ALPACA_SECRET_KEY"
            ),
        ):
            alpaca_client.create_trading_client()