from __future__ import annotations

from dataclasses import dataclass

from dashboard.analytics_presentation_models import (
    AnalyticsSectionViewModel,
)
from dashboard.presentation_models import (
    AccountSectionViewModel,
)


@dataclass(frozen=True)
class CompleteDashboardViewModel:
    """
    Complete display-ready dashboard model.

    This object contains only presentation-ready values.
    It has no broker, database, analytics, or Streamlit
    dependencies.
    """

    account: AccountSectionViewModel
    analytics: AnalyticsSectionViewModel