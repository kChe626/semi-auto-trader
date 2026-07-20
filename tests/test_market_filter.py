import pandas as pd
import pytest

from scanner.market_filter import (
    MarketRegime,
    get_market_regime,
    market_is_bullish,
)


def configure_market_data(
    monkeypatch,
    close_price: float,
    sma_value: float,
) -> None:
    data = pd.DataFrame(
        {
            "Close": [close_price],
            "SMA_50": [sma_value],
        }
    )

    monkeypatch.setattr(
        "scanner.market_filter.get_historical_bars",
        lambda symbol: data,
    )

    monkeypatch.setattr(
        "scanner.market_filter.add_sma",
        lambda data, period: data,
    )


def test_market_regime_is_bullish(
    monkeypatch,
) -> None:
    configure_market_data(
        monkeypatch,
        close_price=102.00,
        sma_value=100.00,
    )

    assert (
        get_market_regime()
        is MarketRegime.BULLISH
    )


def test_market_regime_is_neutral_above_sma(
    monkeypatch,
) -> None:
    configure_market_data(
        monkeypatch,
        close_price=100.50,
        sma_value=100.00,
    )

    assert (
        get_market_regime()
        is MarketRegime.NEUTRAL
    )


def test_market_regime_is_neutral_below_sma(
    monkeypatch,
) -> None:
    configure_market_data(
        monkeypatch,
        close_price=99.50,
        sma_value=100.00,
    )

    assert (
        get_market_regime()
        is MarketRegime.NEUTRAL
    )


def test_market_regime_is_bearish(
    monkeypatch,
) -> None:
    configure_market_data(
        monkeypatch,
        close_price=98.00,
        sma_value=100.00,
    )

    assert (
        get_market_regime()
        is MarketRegime.BEARISH
    )


def test_market_is_bullish_allows_neutral_market(
    monkeypatch,
) -> None:
    configure_market_data(
        monkeypatch,
        close_price=99.50,
        sma_value=100.00,
    )

    assert market_is_bullish() is True


def test_market_is_bullish_blocks_bearish_market(
    monkeypatch,
) -> None:
    configure_market_data(
        monkeypatch,
        close_price=98.00,
        sma_value=100.00,
    )

    assert market_is_bullish() is False


def test_market_regime_rejects_zero_sma(
    monkeypatch,
) -> None:
    configure_market_data(
        monkeypatch,
        close_price=100.00,
        sma_value=0.00,
    )

    with pytest.raises(
        ValueError,
        match="must be greater than zero",
    ):
        get_market_regime()