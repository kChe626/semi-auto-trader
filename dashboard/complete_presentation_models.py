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
from dashboard.trade_workflow_presentation_models import (
    TradeWorkflowViewModel,
)


@dataclass(frozen=True, slots=True)
class CompleteDashboardViewModel:
    account: AccountSectionViewModel
    scanner: ScannerSectionViewModel
    workflow: TradeWorkflowViewModel
    analytics: AnalyticsSectionViewModel
    trade_history: TradeHistorySectionViewModel