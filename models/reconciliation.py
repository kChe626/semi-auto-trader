from dataclasses import dataclass


@dataclass(frozen=True)
class ReconciliationResult:
    order_id: str
    symbol: str
    broker_status: str
    previous_status: str | None
    recorded_status: str | None
    changed: bool