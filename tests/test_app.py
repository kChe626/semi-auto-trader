from __future__ import annotations

import importlib
import sys
from unittest.mock import Mock, patch


def import_app():
    """
    Import app.py with the module-level dashboard run
    patched so importing the module has no UI side effects.
    """

    sys.modules.pop("app", None)

    with patch(
        "dashboard.streamlit_app.run_dashboard"
    ):
        return importlib.import_module("app")


def test_create_presentation_mapper_wires_all_mappers(
) -> None:
    app = import_app()

    account_mapper = Mock(
        name="account-mapper"
    )
    scanner_mapper = Mock(
        name="scanner-mapper"
    )
    workflow_mapper = Mock(
        name="workflow-mapper"
    )
    analytics_mapper = Mock(
        name="analytics-mapper"
    )
    trade_history_mapper = Mock(
        name="trade-history-mapper"
    )

    app.create_presentation_mapper.clear()

    with (
        patch.object(
            app,
            "AccountPresentationMapper",
            return_value=account_mapper,
        ),
        patch.object(
            app,
            "ScannerPresentationMapper",
            return_value=scanner_mapper,
        ),
        patch.object(
            app,
            "TradeWorkflowPresentationMapper",
            return_value=workflow_mapper,
        ),
        patch.object(
            app,
            "AnalyticsPresentationMapper",
            return_value=analytics_mapper,
        ),
        patch.object(
            app,
            "TradeHistoryPresentationMapper",
            return_value=trade_history_mapper,
        ),
        patch.object(
            app,
            "CompleteDashboardPresentationMapper",
        ) as complete_mapper_class,
    ):
        complete_mapper = Mock(
            name="complete-presentation-mapper"
        )
        complete_mapper_class.return_value = (
            complete_mapper
        )

        result = app.create_presentation_mapper()

    assert result is complete_mapper

    complete_mapper_class.assert_called_once_with(
        account_mapper=account_mapper,
        scanner_mapper=scanner_mapper,
        workflow_mapper=workflow_mapper,
        analytics_mapper=analytics_mapper,
        trade_history_mapper=trade_history_mapper,
    )


def test_load_view_model_maps_loaded_dashboard_data(
) -> None:
    app = import_app()

    service = Mock(name="service")
    presentation_mapper = Mock(
        name="presentation-mapper"
    )
    dashboard_data = Mock(
        name="dashboard-data"
    )
    view_model = Mock(
        name="view-model"
    )

    service.load_complete_dashboard_data.return_value = (
        dashboard_data
    )
    presentation_mapper.map_dashboard.return_value = (
        view_model
    )

    with (
        patch.object(
            app,
            "create_service",
            return_value=service,
        ),
        patch.object(
            app,
            "create_presentation_mapper",
            return_value=presentation_mapper,
        ),
    ):
        result = app.load_view_model()

    assert result is view_model

    service.load_complete_dashboard_data\
        .assert_called_once_with()

    presentation_mapper.map_dashboard\
        .assert_called_once_with(
            dashboard_data
        )