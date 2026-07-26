from __future__ import annotations

from dashboard.scanner_presentation_mapper import (
    ScannerPresentationMapper,
)
from dashboard.scanner_presentation_models import (
    ScannerResultRowViewModel,
    ScannerSectionViewModel,
)
from models.trade_signal import TradeSignal


def make_signal(
    *,
    symbol: str = "AAPL",
    signal_type: str = "BUY",
    price: float = 210.25,
    reason: str = "Bullish SMA crossover",
    rsi: float | None = 61.75,
    short_sma: float | None = 205.50,
    long_sma: float | None = 198.25,
    atr: float | None = 4.40,
) -> TradeSignal:
    return TradeSignal(
        symbol=symbol,
        signal_type=signal_type,
        price=price,
        reason=reason,
        rsi=rsi,
        short_sma=short_sma,
        long_sma=long_sma,
        atr=atr,
    )


def test_map_scanner_section_returns_view_model() -> None:
    mapper = ScannerPresentationMapper()

    result = mapper.map_scanner_section(
        [make_signal()]
    )

    assert isinstance(
        result,
        ScannerSectionViewModel,
    )
    assert result.has_results is True
    assert len(result.results) == 1


def test_map_scanner_section_maps_signal_values() -> None:
    mapper = ScannerPresentationMapper()

    result = mapper.map_scanner_section(
        [make_signal()]
    )

    row = result.results[0]

    assert isinstance(
        row,
        ScannerResultRowViewModel,
    )
    assert row.symbol == "AAPL"
    assert row.signal == "BUY"
    assert row.price == "$210.25"
    assert row.short_sma == "$205.50"
    assert row.long_sma == "$198.25"
    assert row.rsi == "61.75"
    assert row.atr == "$4.40"
    assert row.reason == "Bullish SMA crossover"


def test_map_scanner_section_preserves_order() -> None:
    mapper = ScannerPresentationMapper()

    result = mapper.map_scanner_section(
        [
            make_signal(symbol="AAPL"),
            make_signal(symbol="MSFT"),
            make_signal(symbol="NVDA"),
        ]
    )

    assert tuple(
        row.symbol
        for row in result.results
    ) == (
        "AAPL",
        "MSFT",
        "NVDA",
    )


def test_map_scanner_section_handles_empty_results() -> None:
    mapper = ScannerPresentationMapper()

    result = mapper.map_scanner_section([])

    assert result.results == ()
    assert result.has_results is False


def test_map_scanner_section_formats_large_price() -> None:
    mapper = ScannerPresentationMapper()

    result = mapper.map_scanner_section(
        [
            make_signal(
                price=1234.567,
            )
        ]
    )

    assert result.results[0].price == "$1,234.57"


def test_map_scanner_section_formats_missing_indicators() -> None:
    mapper = ScannerPresentationMapper()

    result = mapper.map_scanner_section(
        [
            make_signal(
                rsi=None,
                short_sma=None,
                long_sma=None,
                atr=None,
            )
        ]
    )

    row = result.results[0]

    assert row.rsi == "—"
    assert row.short_sma == "—"
    assert row.long_sma == "—"
    assert row.atr == "—"


def test_each_mapping_returns_new_view_model() -> None:
    mapper = ScannerPresentationMapper()

    signals = [make_signal()]

    first = mapper.map_scanner_section(signals)
    second = mapper.map_scanner_section(signals)

    assert first is not second
    assert first.results is not second.results