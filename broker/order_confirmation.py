from models.trade_plan import TradePlan


CONFIRMATION_TEXT = "SUBMIT PAPER ORDER"


def confirm_paper_order(plan: TradePlan) -> bool:
    """
    Require an explicit confirmation phrase before submitting
    a paper-trading order.
    """
    print()
    print("PAPER TRADING CONFIRMATION")
    print("-" * 42)
    print(f"Symbol:   {plan.symbol}")
    print(f"Side:     {plan.signal_type}")
    print(f"Quantity: {plan.quantity}")
    print()
    print(
        f'Type "{CONFIRMATION_TEXT}" '
        "to submit this paper order."
    )
    print("Press Enter or type anything else to cancel.")

    response = input("\nConfirmation: ").strip()

    return response == CONFIRMATION_TEXT