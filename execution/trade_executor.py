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
        **kwargs: Any,
    ) -> Any:
        ...


class RepositoryProtocol(Protocol):
    def save(
        self,
        trade: Trade | Any,
    ) -> None:
        ...


class OrderVerifierProtocol(Protocol):
    def verify(
        self,
        order_id: str,
    ) -> Any:
        ...


class TradeExecutor:
    """
    Submit approved trade workflows and persist
    the resulting broker order state.
    """

    def __init__(
        self,
        *,
        broker: BrokerProtocol,
        journal: JournalProtocol,
        repository: RepositoryProtocol,
        order_verifier: OrderVerifierProtocol | None = None,
    ) -> None:
        self._broker = broker
        self._journal = journal
        self._repository = repository
        self._order_verifier = order_verifier

    def execute(
        self,
        workflow: Any,
    ) -> Any:
        if isinstance(
            workflow,
            WorkflowResult,
        ):
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

        trade_id = str(
            workflow.trade_id or ""
        ).strip()

        if not trade_id:
            raise ValueError(
                "Trade workflow is missing a trade_id"
            )

        submitted_order = (
            self._broker.submit_bracket_order(
                workflow.plan
            )
        )

        parent_order_id = self._get_parent_order_id(
            submitted_order
        )

        verified_order = submitted_order

        if self._order_verifier is not None:
            verified_order = (
                self._order_verifier.verify(
                    parent_order_id
                )
            )

        trade = TradeMapper.map_submitted_trade(
            trade_id=trade_id,
            plan=workflow.plan,
            parent_order_id=parent_order_id,
        )

        self._repository.save(
            trade
        )

        self._journal.record_event(
            symbol=workflow.plan.symbol,
            asset_type="stock",
            signal_type=workflow.plan.signal_type,
            entry_price=workflow.plan.entry_price,
            stop_price=workflow.plan.stop_price,
            target_price=workflow.plan.target_price,
            quantity=workflow.plan.quantity,
            total_risk=workflow.plan.total_risk,
            risk_reward_ratio=(
                workflow.plan.risk_reward_ratio
            ),
            status="trade_submitted",
            reason=(
                "Bracket order submitted to broker"
            ),
            trade_id=trade_id,
            order_id=parent_order_id,
        )

        return verified_order

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

        parent_order_id = str(
            order_id
        ).strip()

        if not parent_order_id:
            raise ValueError(
                "Submitted order is missing an id"
            )

        return parent_order_id