import pandas as pd

from scanner.market_filter import market_is_bullish


def test_market_filter_true(monkeypatch) -> None:
    data = pd.DataFrame(
        {
            "Close": [100, 105],
            "SMA_50": [99, 100],
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

    assert market_is_bullish() is True


def test_market_filter_false(monkeypatch) -> None:
    data = pd.DataFrame(
        {
            "Close": [100, 95],
            "SMA_50": [99, 100],
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

    assert market_is_bullish() is False