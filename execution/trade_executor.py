from __future__ import annotations

from typing import Any, Protocol


class BrokerProtocol(Protocol):
    def submit_order(
        self,
        workflow: Any,
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
        trade: Any,
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