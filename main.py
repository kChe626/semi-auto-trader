from broker.alpaca_client import create_trading_client
from broker.order_confirmation import confirm_paper_order
from broker.order_executor import OrderExecutor
from broker.preflight_service import run_broker_preflight
from config.trading_config import (
    EXECUTION_ENABLED,
    MAX_POSITION_PERCENT,
    REWARD_RISK_RATIO,
    RISK_PERCENT,
    STOP_LOSS_PERCENT,
)
from config.watchlist import WATCHLIST
from risk.plan_formatter import format_trade_plan
from risk.portfolio_manager import PortfolioManager
from risk.risk_manager import RiskManager
from risk.signal_to_plan import create_trade_plan_from_signal
from scanner.scanner import scan_market


def main() -> None:
    trading_client = create_trading_client()

    try:
        account = trading_client.get_account()
        account_equity = float(account.equity)
    except Exception as error:
        print(
            f"Unable to retrieve Alpaca account information: "
            f"{error}"
        )
        return

    risk_manager = RiskManager(
        account_equity=account_equity,
        max_position_percent=MAX_POSITION_PERCENT,
    )

    portfolio_manager = PortfolioManager(trading_client)
    order_executor = OrderExecutor(trading_client)

    print("=" * 60)
    print("SEMI-AUTOMATED PAPER TRADER")
    print("=" * 60)
    print(f"Account Equity: ${account_equity:,.2f}")
    print(f"Scanning {len(WATCHLIST)} symbols...")
    print()

    try:
        signals = scan_market()
    except Exception as error:
        print(f"\nMarket scan failed: {error}")
        return

    if not signals:
        print("\nNo valid trade signals found.")
        return

    for signal in signals:
        plan = create_trade_plan_from_signal(
            signal=signal,
            account_equity=account_equity,
            risk_percent=RISK_PERCENT,
            stop_loss_percent=STOP_LOSS_PERCENT,
            reward_risk_ratio=REWARD_RISK_RATIO,
        )

        plan = risk_manager.apply_position_limit(plan)

        if plan.quantity <= 0:
            print(
                f"\nSkipping {plan.symbol}: "
                "quantity is zero after risk limits."
            )
            continue

        print()
        print(format_trade_plan(plan))

        try:
            allowed, portfolio_reason = (
                portfolio_manager.can_open_new_trade()
            )
        except Exception as error:
            print(
                f"Skipping {plan.symbol}: unable to check "
                f"portfolio state: {error}"
            )
            continue

        if not allowed:
            print(
                f"Skipping {plan.symbol}: "
                f"{portfolio_reason}"
            )
            continue

        try:
            preflight = run_broker_preflight(
                client=trading_client,
                plan=plan,
            )
        except Exception as error:
            print(
                f"Skipping {plan.symbol}: "
                f"broker preflight failed: {error}"
            )
            continue

        if not preflight.approved:
            print("\nPreflight rejected this trade:")

            for reason in preflight.reasons:
                print(f"  - {reason}")

            continue

        print("\nPreflight checks passed.")

        if not EXECUTION_ENABLED:
            print(
                f"\nExecution is disabled. "
                f"No paper order was submitted for "
                f"{plan.symbol}."
            )
            print(
                "Set EXECUTION_ENABLED = True in "
                "config/trading_config.py when ready."
            )
            continue

        if not confirm_paper_order(plan):
            print(
                f"\nPaper order for {plan.symbol} "
                "cancelled."
            )
            continue

        try:
            order = order_executor.submit_bracket_order(plan)
        except Exception as error:
            print(
                f"\nPaper order submission failed for "
                f"{plan.symbol}: {error}"
            )
            continue

        order_id = getattr(
            order,
            "id",
            "Unavailable",
        )
        order_status = getattr(
            order,
            "status",
            "Unavailable",
        )

        print()
        print("=" * 60)
        print("PAPER ORDER SUBMITTED")
        print("=" * 60)
        print(f"Symbol:   {plan.symbol}")
        print(f"Side:     {plan.signal_type}")
        print(f"Quantity: {plan.quantity}")
        print(f"Order ID: {order_id}")
        print(f"Status:   {order_status}")
        print("=" * 60)

        return

    print("\nNo paper orders were submitted.")


if __name__ == "__main__":
    main()