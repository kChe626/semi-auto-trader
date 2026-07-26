from __future__ import annotations

from collections.abc import Iterable

from dashboard.scanner_presentation_models import (
    ScannerResultRowViewModel,
    ScannerSectionViewModel,
)
from models.trade_signal import TradeSignal


class ScannerPresentationMapper:
    """
    Convert scanner-domain signals into display-ready
    presentation models.
    """

    def map_scanner_section(
        self,
        signals: Iterable[TradeSignal],
    ) -> ScannerSectionViewModel:
        """
        Map scanner signals into one immutable UI section.
        """

        results = tuple(
            self._map_signal(signal)
            for signal in signals
        )

        return ScannerSectionViewModel(
            results=results,
        )

    @classmethod
    def _map_signal(
        cls,
        signal: TradeSignal,
    ) -> ScannerResultRowViewModel:
        return ScannerResultRowViewModel(
            symbol=signal.symbol,
            signal=signal.signal_type,
            price=cls._format_price(
                signal.price
            ),
            short_sma=cls._format_price(
                signal.short_sma
            ),
            long_sma=cls._format_price(
                signal.long_sma
            ),
            rsi=cls._format_number(
                signal.rsi
            ),
            atr=cls._format_price(
                signal.atr
            ),
            reason=signal.reason,
        )

    @staticmethod
    def _format_price(
        value: float | None,
    ) -> str:
        if value is None:
            return "—"

        return f"${value:,.2f}"

    @staticmethod
    def _format_number(
        value: float | None,
    ) -> str:
        if value is None:
            return "—"

        return f"{value:.2f}"