from __future__ import annotations

from dataclasses import dataclass

from dashboard.analytics_presentation_models import (
    AnalyticsSectionViewModel,
)
from dashboard.presentation_models import (
    AccountSectionViewModel,
)
from dashboard.scanner_presentation_models import (
    ScannerSectionViewModel,
)
from dashboard.trade_history_presentation_models import (
    TradeHistorySectionViewModel,
)


@dataclass(frozen=True, slots=True)
class CompleteDashboardViewModel:
    account: AccountSectionViewModel
    scanner: ScannerSectionViewModel
    analytics: AnalyticsSectionViewModel
    trade_history: TradeHistorySectionViewModel