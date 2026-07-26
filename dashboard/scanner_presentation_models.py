from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScannerResultRowViewModel:
    """
    One display-ready market scanner result.

    All values are formatted for direct rendering by the
    dashboard UI.
    """

    symbol: str
    signal: str
    price: str
    short_sma: str
    long_sma: str
    rsi: str
    atr: str
    reason: str


@dataclass(frozen=True)
class ScannerSectionViewModel:
    """
    Display-ready market scanner section.
    """

    results: tuple[
        ScannerResultRowViewModel,
        ...
    ]

    @property
    def has_results(self) -> bool:
        """
        Return whether the scanner produced any signals.
        """

        return bool(self.results)