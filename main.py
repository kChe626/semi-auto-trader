from broker.alpaca_client import create_trading_client
from broker.order_confirmation import confirm_paper_order
from broker.order_executor import OrderExecutor
from broker.order_verifier import verify_submitted_order
from broker.preflight_service import run_broker_preflight
from config.trading_config import (
    EXECUTION_ENABLED,
    MAX_POSITION_PERCENT,
    REWARD_RISK_RATIO,
    RISK_PERCENT,
    STOP_LOSS_PERCENT,
)
from config.watchlist import WATCHLIST
from notifications.notification_service import (
    NotificationSender,
    format_trade_alert,
    send_notification_safely,
)
from notifications.telegram_notifier import (
    send_telegram_message,
)
from risk.plan_formatter import format_trade_plan
from risk.portfolio_manager import PortfolioManager
from risk.risk_manager import RiskManager
from risk.signal_to_plan import create_trade_plan_from_signal
from scanner.market_filter import market_is_bullish
from scanner.scanner import scan_market
from scanner.trade_ranker import rank_trade_plans


def main(
    notification_sender: NotificationSender | None = None,
) -> None:
    trading_client = create_trading_client()

    try:
        account = trading_client.get_account()
        account_equity = float(account.equity)
    except Exception as error:
        message = (
            "Unable to retrieve Alpaca account information: "
            f"{error}"
        )
        print(message)

        send_notification_safely(
            notification_sender,
            f"⚠️ TRADER ERROR\n\n{message}",
        )
        return

    print("=" * 60)
    print("SEMI-AUTOMATED PAPER TRADER")
    print("=" * 60)
    print(f"Account Equity: ${account_equity:,.2f}")
    print()

    try:
        bullish_market = market_is_bullish()
    except Exception as error:
        message = (
            "Unable to evaluate the market trend: "
            f"{error}"
        )
        print(message)

        send_notification_safely(
            notification_sender,
            f"⚠️ MARKET FILTER ERROR\n\n{message}",
        )
        return

    print("=" * 60)
    print("MARKET FILTER")
    print("=" * 60)

    if not bullish_market:
        print(
            "SPY is meaningfully below its "
            "50-day SMA."
        )
        print("No new long trades today.")

        send_notification_safely(
            notification_sender,
            (
                "📉 NO TRADES TODAY\n\n"
                "SPY is meaningfully below its "
                "50-day SMA.\n"
                "The market filter blocked new "
                "long trades."
            ),
        )
        return

    print("Market filter passed.")
    print(
        "SPY is bullish or within the "
        "neutral range of its 50-day SMA."
    )
    print(f"Scanning {len(WATCHLIST)} symbols...")
    print()

    risk_manager = RiskManager(
        account_equity=account_equity,
        max_position_percent=MAX_POSITION_PERCENT,
    )

    portfolio_manager = PortfolioManager(
        trading_client
    )

    order_executor = OrderExecutor(
        trading_client
    )

    try:
        signals = scan_market()
    except Exception as error:
        message = f"Market scan failed: {error}"
        print(f"\n{message}")

        send_notification_safely(
            notification_sender,
            f"⚠️ MARKET SCAN ERROR\n\n{message}",
        )
        return

    if not signals:
        print("\nNo valid trade signals found.")

        send_notification_safely(
            notification_sender,
            (
                "🔍 SCAN COMPLETE\n\n"
                "No valid trade signals were found."
            ),
        )
        return

    eligible_plans = []

    for signal in signals:
        plan = create_trade_plan_from_signal(
            signal=signal,
            account_equity=account_equity,
            risk_percent=RISK_PERCENT,
            stop_loss_percent=STOP_LOSS_PERCENT,
            reward_risk_ratio=REWARD_RISK_RATIO,
        )

        plan = risk_manager.apply_position_limit(
            plan
        )

        if plan.quantity <= 0:
            print(
                f"\nSkipping {plan.symbol}: "
                "quantity is zero after risk limits."
            )
            continue

        eligible_plans.append(plan)

    if not eligible_plans:
        print(
            "\nNo trade plans remained after "
            "risk limits were applied."
        )

        send_notification_safely(
            notification_sender,
            (
                "⚠️ NO ELIGIBLE TRADES\n\n"
                "Signals were found, but no trade "
                "plans remained after risk limits."
            ),
        )
        return

    ranked_trades = rank_trade_plans(
        eligible_plans
    )

    print()
    print("=" * 60)
    print("TRADE RANKINGS")
    print("=" * 60)

    for position, trade_score in enumerate(
        ranked_trades,
        start=1,
    ):
        print(
            f"{position}. "
            f"{trade_score.plan.symbol} | "
            f"Score: {trade_score.score:.2f}"
        )

        for reason in trade_score.reasons:
            print(f"   - {reason}")

    print("=" * 60)

    for trade_score in ranked_trades:
        plan = trade_score.plan

        print()
        print(
            "Evaluating ranked candidate: "
            f"{plan.symbol}"
        )
        print(
            "Trade score: "
            f"{trade_score.score:.2f}"
        )
        print()
        print(format_trade_plan(plan))

        try:
            allowed, portfolio_reason = (
                portfolio_manager.can_open_new_trade()
            )
        except Exception as error:
            message = (
                f"Skipping {plan.symbol}: "
                "unable to check portfolio state: "
                f"{error}"
            )
            print(message)

            send_notification_safely(
                notification_sender,
                (
                    "⚠️ PORTFOLIO CHECK ERROR\n\n"
                    f"{message}"
                ),
            )
            continue

        if not allowed:
            message = (
                f"Skipping {plan.symbol}: "
                f"{portfolio_reason}"
            )
            print(message)

            send_notification_safely(
                notification_sender,
                (
                    "🚫 TRADE BLOCKED\n\n"
                    f"Symbol: {plan.symbol}\n"
                    f"Reason: {portfolio_reason}"
                ),
            )
            continue

        try:
            preflight = run_broker_preflight(
                client=trading_client,
                plan=plan,
            )
        except Exception as error:
            message = (
                f"Skipping {plan.symbol}: "
                f"broker preflight failed: {error}"
            )
            print(message)

            send_notification_safely(
                notification_sender,
                (
                    "⚠️ PREFLIGHT ERROR\n\n"
                    f"{message}"
                ),
            )
            continue

        if not preflight.approved:
            print(
                f"\nPreflight rejected "
                f"{plan.symbol}:"
            )

            for reason in preflight.reasons:
                print(f"  - {reason}")

            reason_text = "\n".join(
                f"• {reason}"
                for reason in preflight.reasons
            )

            send_notification_safely(
                notification_sender,
                (
                    "🚫 PREFLIGHT REJECTED\n\n"
                    f"Symbol: {plan.symbol}\n\n"
                    f"{reason_text}"
                ),
            )
            continue

        print("\nPreflight checks passed.")

        send_notification_safely(
            notification_sender,
            format_trade_alert(
                plan=plan,
                score=trade_score.score,
            ),
        )

        if not EXECUTION_ENABLED:
            print(
                "\nExecution is disabled. "
                "No paper order was submitted for "
                f"{plan.symbol}."
            )
            print(
                "Set EXECUTION_ENABLED = True in "
                "config/trading_config.py when ready."
            )

            send_notification_safely(
                notification_sender,
                (
                    "ℹ️ EXECUTION DISABLED\n\n"
                    f"{plan.symbol} passed preflight, "
                    "but paper execution is disabled."
                ),
            )
            return

        if not confirm_paper_order(plan):
            print(
                f"\nPaper order for "
                f"{plan.symbol} cancelled."
            )

            send_notification_safely(
                notification_sender,
                (
                    "❌ ORDER CANCELLED\n\n"
                    f"Paper order for {plan.symbol} "
                    "was not approved in the terminal."
                ),
            )
            continue

        try:
            order = (
                order_executor.submit_bracket_order(
                    plan
                )
            )
        except Exception as error:
            print(
                "\nPaper order submission failed for "
                f"{plan.symbol}: {error}"
            )

            send_notification_safely(
                notification_sender,
                (
                    "⚠️ ORDER SUBMISSION FAILED\n\n"
                    f"Symbol: {plan.symbol}\n"
                    f"Error: {error}"
                ),
            )
            continue

        order_id = getattr(
            order,
            "id",
            None,
        )

        if order_id is None:
            print(
                "\nWarning: Alpaca returned an order "
                "without an order ID."
            )

            send_notification_safely(
                notification_sender,
                (
                    "⚠️ MISSING ORDER ID\n\n"
                    f"Alpaca accepted the {plan.symbol} "
                    "request but returned no order ID."
                ),
            )
            return

        try:
            verified_order = verify_submitted_order(
                client=trading_client,
                order_id=order_id,
            )
        except Exception as error:
            print(
                "\nPaper order was submitted, but "
                "broker verification failed: "
                f"{error}"
            )
            print(
                f"Submitted Order ID: {order_id}"
            )

            send_notification_safely(
                notification_sender,
                (
                    "⚠️ ORDER VERIFICATION FAILED\n\n"
                    f"Symbol: {plan.symbol}\n"
                    f"Order ID: {order_id}\n"
                    f"Error: {error}"
                ),
            )
            return

        order_status = getattr(
            verified_order,
            "status",
            "Unavailable",
        )

        order_symbol = getattr(
            verified_order,
            "symbol",
            plan.symbol,
        )

        print()
        print("=" * 60)
        print(
            "PAPER ORDER SUBMITTED AND VERIFIED"
        )
        print("=" * 60)
        print(f"Symbol:   {order_symbol}")
        print(f"Side:     {plan.signal_type}")
        print(f"Quantity: {plan.quantity}")
        print(f"Score:    {trade_score.score:.2f}")
        print(f"Order ID: {order_id}")
        print(f"Status:   {order_status}")
        print("=" * 60)

        send_notification_safely(
            notification_sender,
            (
                "✅ PAPER ORDER SUBMITTED\n\n"
                f"Symbol: {order_symbol}\n"
                f"Side: {plan.signal_type}\n"
                f"Quantity: {plan.quantity}\n"
                f"Entry: ${plan.entry_price:,.2f}\n"
                f"Stop: ${plan.stop_price:,.2f}\n"
                f"Target: ${plan.target_price:,.2f}\n"
                f"Score: {trade_score.score:.2f}\n"
                f"Status: {order_status}\n"
                f"Order ID: {order_id}"
            ),
        )

        return

    print("\nNo paper orders were submitted.")

    send_notification_safely(
        notification_sender,
        (
            "ℹ️ SCAN COMPLETE\n\n"
            "Candidates were evaluated, but no "
            "paper orders were submitted."
        ),
    )


if __name__ == "__main__":
    main(
        notification_sender=send_telegram_message
    )