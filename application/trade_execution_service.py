from __future__ import annotations

from collections.abc import Callable
from typing import Any


class TradeExecutionService:
    """
    Coordinates human approval and trade execution.

    Approval happens before execution.
    This service does not create plans or manage risk.
    """

    def __init__(
        self,
        *,
        trade_approval: Callable[[Any], bool],
        trade_executor: Callable[[Any], Any],
        order_verifier: Callable[[Any], Any] | None = None,
    ) -> None:
        self._trade_approval = trade_approval
        self._trade_executor = trade_executor
        self._order_verifier = order_verifier

    def execute(
        self,
        workflow: Any,
    ) -> Any | None:
        plan = workflow.plan

        approved = self._trade_approval(
            plan
        )

        if not approved:
            return None

        order = self._trade_executor(
            workflow
        )

        if self._order_verifier is None:
            return order

        return self._order_verifier(
            order
        )