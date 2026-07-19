import pandas as pd

from scanner.signals import check_sma_crossover


def test_bullish_crossover_with_valid_rsi_returns_buy() -> None:
    data = pd.DataFrame(
        {
            "Close": [100.0, 102.0],
            "SMA_20": [99.0, 101.0],
            "SMA_50": [100.0, 100.0],
            "RSI_14": [55.0, 60.0],
        }
    )

    signal = check_sma_crossover(
        symbol="TEST",
        data=data,
    )

    assert signal is not None
    assert signal.signal_type == "BUY"
    assert signal.price == 102.0


def test_bullish_crossover_with_overbought_rsi_returns_none() -> None:
    data = pd.DataFrame(
        {
            "Close": [100.0, 102.0],
            "SMA_20": [99.0, 101.0],
            "SMA_50": [100.0, 100.0],
            "RSI_14": [68.0, 75.0],
        }
    )

    signal = check_sma_crossover(
        symbol="TEST",
        data=data,
    )

    assert signal is None


def test_bearish_crossover_with_valid_rsi_returns_sell() -> None:
    data = pd.DataFrame(
        {
            "Close": [102.0, 99.0],
            "SMA_20": [101.0, 99.0],
            "SMA_50": [100.0, 100.0],
            "RSI_14": [50.0, 40.0],
        }
    )

    signal = check_sma_crossover(
        symbol="TEST",
        data=data,
    )

    assert signal is not None
    assert signal.signal_type == "SELL"
    assert signal.price == 99.0


def test_bearish_crossover_with_oversold_rsi_returns_none() -> None:
    data = pd.DataFrame(
        {
            "Close": [102.0, 99.0],
            "SMA_20": [101.0, 99.0],
            "SMA_50": [100.0, 100.0],
            "RSI_14": [35.0, 25.0],
        }
    )

    signal = check_sma_crossover(
        symbol="TEST",
        data=data,
    )

    assert signal is None


def test_no_crossover_returns_none() -> None:
    data = pd.DataFrame(
        {
            "Close": [101.0, 102.0],
            "SMA_20": [101.0, 102.0],
            "SMA_50": [100.0, 100.5],
            "RSI_14": [55.0, 60.0],
        }
    )

    signal = check_sma_crossover(
        symbol="TEST",
        data=data,
    )

    assert signal is None