from __future__ import annotations

from collections.abc import Callable
from typing import Any


class TelegramTradeApproval:
    def __init__(
        self,
        *,
        request_response: Callable[[str], str],
    ) -> None:
        self._request_response = request_response

    def __call__(
        self,
        plan: Any,
    ) -> bool:
        message = self._format_message(
            plan
        )

        try:
            response = self._request_response(
                message
            )
        except Exception:
            return False

        return self._is_approved_response(
            response=response,
            plan=plan,
        )

    @staticmethod
    def _is_approved_response(
        *,
        response: str,
        plan: Any,
    ) -> bool:
        parts = (
            str(response)
            .strip()
            .upper()
            .split()
        )

        if not parts:
            return False

        if parts[0] != "APPROVE":
            return False

        trade_id = getattr(
            plan,
            "trade_id",
            None,
        )

        # Backward compatibility:
        # Allow plain APPROVE for older plans
        # that do not have a trade ID.
        if trade_id is None:
            return len(parts) == 1

        # Production safety:
        # Require matching trade ID.
        if len(parts) != 2:
            return False

        return (
            parts[1]
            == str(trade_id).upper()
        )

    @staticmethod
    def _format_message(
        plan: Any,
    ) -> str:
        trade_id = getattr(
            plan,
            "trade_id",
            None,
        )

        trade_id_line = ""

        if trade_id is not None:
            trade_id_line = (
                f"Trade ID: {trade_id}\n\n"
            )

        approval_text = (
            f"Reply APPROVE {trade_id} "
            "to submit.\n"
            f"Reply REJECT {trade_id} "
            "to cancel."
            if trade_id is not None
            else
            "Reply APPROVE to submit.\n"
            "Reply REJECT to cancel."
        )

        return (
            "PAPER TRADE APPROVAL\n\n"
            f"{trade_id_line}"
            f"Symbol: {plan.symbol}\n"
            f"Side: {plan.signal_type}\n"
            f"Quantity: {plan.quantity}\n"
            f"Entry: ${plan.entry_price:,.2f}\n"
            f"Stop: ${plan.stop_price:,.2f}\n"
            f"Target: ${plan.target_price:,.2f}\n\n"
            f"{approval_text}"
        )