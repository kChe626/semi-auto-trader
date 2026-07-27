from __future__ import annotations

from typing import Any, Protocol


class TradeExecutorProtocol(Protocol):
    def execute(
        self,
        workflow: Any,
    ) -> Any:
        ...


class DashboardApprovalService:
    def __init__(
        self,
        *,
        trade_executor: TradeExecutorProtocol,
    ) -> None:
        self._trade_executor = trade_executor

    def approve(
        self,
        workflow: Any,
    ) -> Any:
        if (
            workflow.status
            != "READY FOR APPROVAL"
        ):
            raise ValueError(
                "Trade workflow is not ready "
                "for approval"
            )

        return self._trade_executor.execute(
            workflow
        )