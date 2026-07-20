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


def test_buy_signal_includes_atr() -> None:
    data = pd.DataFrame(
        {
            "Close": [100.0, 102.0],
            "SMA_20": [99.0, 101.0],
            "SMA_50": [100.0, 100.0],
            "RSI_14": [55.0, 60.0],
            "ATR_14": [1.8, 2.25],
        }
    )

    signal = check_sma_crossover(
        symbol="TEST",
        data=data,
    )

    assert signal is not None
    assert signal.atr == 2.25


def test_sell_signal_includes_atr() -> None:
    data = pd.DataFrame(
        {
            "Close": [102.0, 99.0],
            "SMA_20": [101.0, 99.0],
            "SMA_50": [100.0, 100.0],
            "RSI_14": [50.0, 40.0],
            "ATR_14": [1.9, 2.5],
        }
    )

    signal = check_sma_crossover(
        symbol="TEST",
        data=data,
    )

    assert signal is not None
    assert signal.atr == 2.5


def test_signal_atr_is_none_when_column_is_missing() -> None:
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
    assert signal.atr is None


def test_custom_atr_period_is_used() -> None:
    data = pd.DataFrame(
        {
            "Close": [100.0, 102.0],
            "SMA_20": [99.0, 101.0],
            "SMA_50": [100.0, 100.0],
            "RSI_14": [55.0, 60.0],
            "ATR_10": [1.5, 1.75],
        }
    )

    signal = check_sma_crossover(
        symbol="TEST",
        data=data,
        atr_period=10,
    )

    assert signal is not None
    assert signal.atr == 1.75