from __future__ import annotations

from typing import Any, Protocol

from execution.trade_mapper import TradeMapper
from models.trade import Trade
from models.trade_plan import TradePlan
from models.workflow_result import WorkflowResult


class BrokerProtocol(Protocol):
    def submit_order(
        self,
        workflow: Any,
    ) -> Any:
        ...

    def submit_bracket_order(
        self,
        plan: TradePlan,
    ) -> Any:
        ...


class JournalProtocol(Protocol):
    def record_event(
        self,
        *,
        trade_id: str,
        event: str,
    ) -> Any:
        ...


class RepositoryProtocol(Protocol):
    def save(
        self,
        trade: Trade | Any,
    ) -> None:
        ...


class TradeExecutor:
    def __init__(
        self,
        *,
        broker: BrokerProtocol,
        journal: JournalProtocol,
        repository: RepositoryProtocol,
    ) -> None:
        self._broker = broker
        self._journal = journal
        self._repository = repository

    def execute(
        self,
        workflow: Any,
    ) -> Any:
        if isinstance(workflow, WorkflowResult):
            return self._execute_workflow_result(
                workflow
            )

        return self._execute_legacy_workflow(
            workflow
        )

    def _execute_workflow_result(
        self,
        workflow: WorkflowResult,
    ) -> Any:
        if not workflow.ready_for_approval:
            raise ValueError(
                "Trade workflow is not ready for execution"
            )

        submitted_order = (
            self._broker.submit_bracket_order(
                workflow.plan
            )
        )

        parent_order_id = self._get_parent_order_id(
            submitted_order
        )

        trade = TradeMapper.map_submitted_trade(
            plan=workflow.plan,
            parent_order_id=parent_order_id,
        )

        self._repository.save(
            trade
        )

        self._journal.record_event(
            trade_id=trade.trade_id,
            event="TRADE_SUBMITTED",
        )

        return submitted_order

    def _execute_legacy_workflow(
        self,
        workflow: Any,
    ) -> Any:
        if workflow.status != "READY FOR APPROVAL":
            raise ValueError(
                "Trade workflow is not ready for execution"
            )

        result = self._broker.submit_order(
            workflow
        )

        self._repository.save(
            workflow
        )

        self._journal.record_event(
            trade_id=workflow.trade_id,
            event="TRADE_SUBMITTED",
        )

        return result

    @staticmethod
    def _get_parent_order_id(
        submitted_order: Any,
    ) -> str:
        order_id = getattr(
            submitted_order,
            "id",
            None,
        )

        if order_id is None:
            raise ValueError(
                "Submitted order is missing an id"
            )

        parent_order_id = str(order_id).strip()

        if not parent_order_id:
            raise ValueError(
                "Submitted order is missing an id"
            )

        return parent_order_id