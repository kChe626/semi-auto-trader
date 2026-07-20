from unittest.mock import patch

from broker.order_confirmation import confirm_paper_order
from models.trade_plan import TradePlan


def create_test_plan() -> TradePlan:
    return TradePlan(
        symbol="META",
        signal_type="BUY",
        entry_price=100.00,
        stop_price=98.00,
        target_price=104.00,
        quantity=10,
        risk_per_share=2.00,
        reward_per_share=4.00,
        total_risk=20.00,
        risk_reward_ratio=2.00,
    )


def test_exact_confirmation_approves() -> None:
    with patch(
        "builtins.input",
        return_value="SUBMIT PAPER ORDER",
    ):
        approved = confirm_paper_order(
            create_test_plan()
        )

    assert approved is True


def test_other_input_cancels() -> None:
    with patch(
        "builtins.input",
        return_value="Y",
    ):
        approved = confirm_paper_order(
            create_test_plan()
        )

    assert approved is False


def test_blank_input_cancels() -> None:
    with patch(
        "builtins.input",
        return_value="",
    ):
        approved = confirm_paper_order(
            create_test_plan()
        )

    assert approved is False