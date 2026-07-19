import pandas as pd
import pytest

from scanner.indicators import add_rsi


def test_add_rsi_creates_expected_column() -> None:
    data = pd.DataFrame(
        {
            "Close": [
                100,
                101,
                102,
                101,
                103,
                104,
                106,
                105,
                107,
                108,
                110,
                109,
                111,
                113,
                114,
                115,
                114,
                116,
                118,
                117,
            ]
        }
    )

    result = add_rsi(data, period=14)

    assert "RSI_14" in result.columns
    assert result["RSI_14"].dropna().between(0, 100).all()


def test_add_rsi_does_not_modify_original_dataframe() -> None:
    data = pd.DataFrame(
        {
            "Close": range(100, 120),
        }
    )

    add_rsi(data, period=14)

    assert "RSI_14" not in data.columns


def test_add_rsi_rejects_invalid_period() -> None:
    data = pd.DataFrame(
        {
            "Close": [100, 101, 102],
        }
    )

    with pytest.raises(
        ValueError,
        match="RSI period must be greater than zero",
    ):
        add_rsi(data, period=0)


def test_add_rsi_rejects_missing_price_column() -> None:
    data = pd.DataFrame(
        {
            "Open": [100, 101, 102],
        }
    )

    with pytest.raises(
        ValueError,
        match="Missing required column: Close",
    ):
        add_rsi(data)