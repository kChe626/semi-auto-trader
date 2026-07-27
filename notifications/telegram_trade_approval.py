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
        message = self._format_message(plan)

        try:
            response = self._request_response(
                message
            )
        except Exception:
            return False

        return (
            str(response)
            .strip()
            .upper()
            == "APPROVE"
        )

    @staticmethod
    def _format_message(
        plan: Any,
    ) -> str:
        return (
            "PAPER TRADE APPROVAL\n\n"
            f"Symbol: {plan.symbol}\n"
            f"Side: {plan.signal_type}\n"
            f"Quantity: {plan.quantity}\n"
            f"Entry: ${plan.entry_price:,.2f}\n"
            f"Stop: ${plan.stop_price:,.2f}\n"
            f"Target: ${plan.target_price:,.2f}\n\n"
            "Reply APPROVE to submit.\n"
            "Reply REJECT to cancel."
        )