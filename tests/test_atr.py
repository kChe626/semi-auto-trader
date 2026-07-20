import pandas as pd
import pytest

from scanner.indicators import add_atr


def make_ohlc_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "High": [10.0, 12.0, 13.0, 15.0, 14.0],
            "Low": [8.0, 9.0, 10.0, 11.0, 12.0],
            "Close": [9.0, 11.0, 12.0, 13.0, 13.5],
        }
    )


def test_add_atr_creates_atr_column() -> None:
    data = make_ohlc_data()

    result = add_atr(data, period=3)

    assert "ATR" in result.columns


def test_add_atr_does_not_modify_original_dataframe() -> None:
    data = make_ohlc_data()

    add_atr(data, period=3)

    assert "ATR" not in data.columns


def test_add_atr_calculates_true_range_correctly() -> None:
    data = make_ohlc_data()

    result = add_atr(data, period=3)

    # True ranges:
    # Row 0: High - Low = 2
    # Row 1: max(12 - 9, abs(12 - 9), abs(9 - 9)) = 3
    # Row 2: max(13 - 10, abs(13 - 11), abs(10 - 11)) = 3
    #
    # First complete 3-period ATR = (2 + 3 + 3) / 3
    assert result.loc[2, "ATR"] == pytest.approx(8 / 3)


def test_add_atr_returns_nan_until_period_is_reached() -> None:
    data = make_ohlc_data()

    result = add_atr(data, period=3)

    assert pd.isna(result.loc[0, "ATR"])
    assert pd.isna(result.loc[1, "ATR"])
    assert pd.notna(result.loc[2, "ATR"])


def test_add_atr_uses_requested_column_name() -> None:
    data = make_ohlc_data()

    result = add_atr(data, period=3, column_name="ATR_3")

    assert "ATR_3" in result.columns
    assert "ATR" not in result.columns


def test_add_atr_rejects_zero_period() -> None:
    data = make_ohlc_data()

    with pytest.raises(ValueError, match="period must be greater than zero"):
        add_atr(data, period=0)


def test_add_atr_rejects_negative_period() -> None:
    data = make_ohlc_data()

    with pytest.raises(ValueError, match="period must be greater than zero"):
        add_atr(data, period=-1)


def test_add_atr_rejects_missing_ohlc_columns() -> None:
    data = pd.DataFrame(
        {
            "High": [10.0],
            "Close": [9.0],
        }
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        add_atr(data, period=3)