from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from dashboard.complete_presentation_models import (
    CompleteDashboardViewModel,
)
from dashboard.streamlit_renderer import (
    StreamlitDashboardRenderer,
)


class StreamlitAppProtocol(Protocol):
    def set_page_config(
        self,
        **kwargs: Any,
    ) -> Any:
        ...

    def title(self, body: str) -> Any:
        ...

    def error(self, body: str) -> Any:
        ...


DashboardViewModelLoader = Callable[
    [],
    CompleteDashboardViewModel,
]


def run_dashboard(
    *,
    load_view_model: DashboardViewModelLoader,
    streamlit_module: StreamlitAppProtocol,
) -> None:
    """
    Run the read-only dashboard UI.

    Runtime dependencies are injected so this module
    remains independently testable.
    """

    streamlit_module.set_page_config(
        page_title="Semi-Auto Trader",
        page_icon="📈",
        layout="wide",
    )

    streamlit_module.title(
        "Semi-Auto Trader Dashboard"
    )

    try:
        view_model = load_view_model()
    except Exception as error:
        streamlit_module.error(
            "Dashboard data could not be loaded: "
            f"{error}"
        )
        return

    renderer = StreamlitDashboardRenderer(
        streamlit_module=streamlit_module
    )

    renderer.render_account_section(
        view_model.account
    )