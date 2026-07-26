from __future__ import annotations

from dashboard.analytics_presentation_mapper import (
    AnalyticsPresentationMapper,
)
from dashboard.complete_presentation_models import (
    CompleteDashboardViewModel,
)
from dashboard.composition_service import (
    CompleteDashboardData,
)
from dashboard.presentation_mapper import (
    AccountPresentationMapper,
)


class CompleteDashboardPresentationMapper:
    """
    Converts a complete dashboard backend snapshot into
    one display-ready dashboard view model.

    This mapper coordinates the existing account and
    analytics presentation mappers. It does not calculate
    analytics, load data, or call Streamlit.
    """

    def __init__(
        self,
        *,
        account_mapper: AccountPresentationMapper,
        analytics_mapper: AnalyticsPresentationMapper,
    ) -> None:
        self._account_mapper = account_mapper
        self._analytics_mapper = analytics_mapper

    def map_dashboard(
        self,
        dashboard_data: CompleteDashboardData,
    ) -> CompleteDashboardViewModel:
        """
        Map one backend dashboard snapshot into a complete
        presentation model.
        """

        account_view_model = (
            self._account_mapper.map_account_section(
                dashboard_data.account_data
            )
        )

        analytics_view_model = (
            self._analytics_mapper.map_analytics_section(
                dashboard_data.analytics_data
            )
        )

        return CompleteDashboardViewModel(
            account=account_view_model,
            analytics=analytics_view_model,
        )