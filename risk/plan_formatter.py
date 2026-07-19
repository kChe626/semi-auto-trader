from models.trade_plan import TradePlan


def format_trade_plan(plan: TradePlan) -> str:
    """
    Return a readable summary of a proposed trade.
    """
    estimated_position_value = plan.entry_price * plan.quantity

    return (
        f"\n"
        f"{'=' * 42}\n"
        f"TRADE PLAN: {plan.signal_type} {plan.symbol}\n"
        f"{'=' * 42}\n"
        f"Entry Price:       ${plan.entry_price:,.2f}\n"
        f"Stop Price:        ${plan.stop_price:,.2f}\n"
        f"Target Price:      ${plan.target_price:,.2f}\n"
        f"Quantity:          {plan.quantity:,} shares\n"
        f"Position Value:    ${estimated_position_value:,.2f}\n"
        f"Risk per Share:    ${plan.risk_per_share:,.2f}\n"
        f"Reward per Share:  ${plan.reward_per_share:,.2f}\n"
        f"Total Risk:        ${plan.total_risk:,.2f}\n"
        f"Risk/Reward Ratio: {plan.risk_reward_ratio:.2f}:1\n"
        f"{'=' * 42}"
    )