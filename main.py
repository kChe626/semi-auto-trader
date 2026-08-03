from __future__ import annotations


from pathlib import Path

from bootstrap import create_trade_repository
from broker.alpaca_client import create_trading_client
from broker.order_executor import OrderExecutor
from broker.order_verifier import verify_submitted_order
from broker.position_monitor import PositionMonitor
from broker.preflight_service import run_broker_preflight
from config.telegram_config import (
    TELEGRAM_APPROVAL_ENABLED,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)

from notifications.telegram_runtime_factory import (
    create_runtime_telegram_approval,
)
from config.trading_config import (
    ALLOW_LONG_TRADES,
    ALLOW_SHORT_TRADES,
    EXECUTION_ENABLED,
    MAX_POSITION_PERCENT,
    MINIMUM_TRADE_SCORE,
    REWARD_RISK_RATIO,
    RISK_PERCENT,
    STOP_LOSS_PERCENT,
)
from config.watchlist import WATCHLIST
from database.journal_service import (
    record_event_safely,
    record_plan_safely,
)
from database.trade_journal import (
    DATABASE_PATH,
    TradeJournal,
)
from execution.order_lifecycle_service import (
    OrderLifecycleService,
)
from models.trade import (
    Trade,
    TradeStatus,
)
from models.workflow_result import WorkflowResult
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


from scanner.market_filter import market_is_bullish
from scanner.scanner import scan_market
from scanner.trade_ranker import rank_trade_plans
from trade_management.exit_reconciler import (
    ExitReconciler,
)
from trade_management.lifecycle_engine import (
    TradeLifecycleEngine,
)
from trade_management.position_reconciler import (
    PositionReconciler,
)
from trade_management.state_reconciler import (
    TradeStateReconciler,
)
from trade_management.trade_identity import (
    create_trade_id,
)
from trade_management.trade_manager import TradeManager
from application.trade_approval_factory import (
    create_trade_approval,
)

from application.trade_execution_service import (
    TradeExecutionService,
)

from application.trade_workflow import TradeWorkflow


from broker.order_confirmation import (
    confirm_paper_order,
)




def signal_direction_is_allowed(
    signal_type: str,
) -> bool:
    normalized_signal_type = signal_type.upper()

    if normalized_signal_type == "BUY":
        return ALLOW_LONG_TRADES

    if normalized_signal_type == "SELL":
        return ALLOW_SHORT_TRADES

    return False


def synchronize_broker_state(
    *,
    trading_client,
    journal: TradeJournal | None,
    notification_sender: NotificationSender | None,
    trade_repository=None,
) -> bool:
    if journal is None:
        return True

    try:
        monitor = PositionMonitor(
            trading_client
        )

        order_reconciler = TradeStateReconciler(
            journal
        )
        position_reconciler = PositionReconciler(
            journal
        )
        exit_reconciler = ExitReconciler(
            journal
        )

        order_lifecycle_service = None

        if trade_repository is not None:
            order_lifecycle_service = (
                OrderLifecycleService(
                    broker=trading_client,
                    repository=trade_repository,
                )
            )

        lifecycle_engine = TradeLifecycleEngine(
            monitor=monitor,
            order_reconciler=order_reconciler,
            position_reconciler=position_reconciler,
            exit_reconciler=exit_reconciler,
            order_lifecycle_service=(
                order_lifecycle_service
            ),
        )

        trade_manager = TradeManager(
            lifecycle_engine
        )
        trade_manager.start_cycle()

    except Exception as error:
        message = (
            "Unable to synchronize broker state: "
            f"{error}"
        )

        print(message)

        send_notification_safely(
            notification_sender,
            (
                "LIFECYCLE SYNC ERROR\n\n"
                f"{message}"
            ),
        )

        return False

    print(
        "Broker orders and positions "
        "synchronized successfully."
    )
    print()

    return True


def main(
    notification_sender: NotificationSender | None = None,
    journal: TradeJournal | None = None,
    trade_repository=None,
    trade_approval=None,
    trade_workflow=None,
) -> None:

    if trade_approval is None:
        trade_approval = create_trade_approval(
            enabled=True,
            approval=confirm_paper_order,
        )

    trading_client = create_trading_client()

    try:
        account = trading_client.get_account()
        account_equity = float(
            account.equity
        )
        if trade_workflow is None:
            from functools import partial

            trade_workflow = TradeWorkflow(
                account_equity=account_equity,
                risk_percent=RISK_PERCENT,
                max_position_percent=MAX_POSITION_PERCENT,
                stop_loss_percent=STOP_LOSS_PERCENT,
                reward_risk_ratio=REWARD_RISK_RATIO,
                preflight_runner=partial(
                    run_broker_preflight,
                    trading_client,
                ),
            )

    except Exception as error:
        message = (
            "Unable to retrieve Alpaca account "
            f"information: {error}"
        )

        print(message)

        send_notification_safely(
            notification_sender,
            (
                "TRADER ERROR\n\n"
                f"{message}"
            ),
        )
        return

    synchronized = synchronize_broker_state(
        trading_client=trading_client,
        journal=journal,
        notification_sender=notification_sender,
        trade_repository=trade_repository,
    )

    if not synchronized:
        print(
            "Trading cycle stopped because broker "
            "state could not be synchronized."
        )
        return

    print("=" * 60)
    print("SEMI-AUTOMATED PAPER TRADER")
    print("=" * 60)
    print(
        f"Account Equity: "
        f"${account_equity:,.2f}"
    )
    print(
        f"Watchlist Size: "
        f"{len(WATCHLIST)}"
    )
    print(
        f"Minimum Score: "
        f"{MINIMUM_TRADE_SCORE:.2f}"
    )
    print(
        "Long Trades: "
        f"{'Enabled' if ALLOW_LONG_TRADES else 'Disabled'}"
    )
    print(
        "Short Trades: "
        f"{'Enabled' if ALLOW_SHORT_TRADES else 'Disabled'}"
    )
    print(
        "Paper Execution: "
        f"{'Enabled' if EXECUTION_ENABLED else 'Disabled'}"
    )
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
            (
                "MARKET FILTER ERROR\n\n"
                f"{message}"
            ),
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
        print(
            "No new long trades today."
        )

        send_notification_safely(
            notification_sender,
            (
                "NO TRADES TODAY\n\n"
                "SPY is meaningfully below its "
                "50-day SMA.\n"
                "The market filter blocked "
                "new long trades."
            ),
        )
        return

    print(
        "Market filter passed."
    )
    print(
        "SPY is bullish or within the neutral "
        "range of its 50-day SMA."
    )
    print()
    print(
        f"Scanning {len(WATCHLIST)} symbols..."
    )
    print()



    portfolio_manager = PortfolioManager(
        trading_client
    )

    order_executor = OrderExecutor(
        trading_client
    )

    trade_execution_service = TradeExecutionService(
        trade_approval=trade_approval,
        trade_executor=lambda workflow: (
            order_executor.submit_bracket_order(
                workflow.plan
            )
        ),
        order_verifier=lambda order: (
            verify_submitted_order(
                client=trading_client,
                order_id=order.id,
            )
        ),
    )

    try:
        signals = scan_market()

    except Exception as error:
        message = (
            f"Market scan failed: {error}"
        )

        print(
            f"\n{message}"
        )

        send_notification_safely(
            notification_sender,
            (
                "MARKET SCAN ERROR\n\n"
                f"{message}"
            ),
        )
        return

    if not signals:
        print(
            "\nNo valid trade signals found."
        )

        send_notification_safely(
            notification_sender,
            (
                "SCAN COMPLETE\n\n"
                "No valid trade signals were found."
            ),
        )
        return

    eligible_plans = []

    print()
    print("=" * 60)
    print("SIGNAL FILTERING")
    print("=" * 60)

    for signal in signals:
        signal_type = str(
            signal.signal_type
        ).upper()

        if not signal_direction_is_allowed(
            signal_type
        ):
            if signal_type == "BUY":
                reason = (
                    "Long trades are disabled"
                )

            elif signal_type == "SELL":
                reason = (
                    "Short selling is disabled"
                )

            else:
                reason = (
                    "Unsupported signal type: "
                    f"{signal_type}"
                )

            print(
                f"Skipping {signal.symbol}: "
                f"{reason.lower()}."
            )

            record_event_safely(
                journal,
                symbol=signal.symbol,
                status="direction_filtered",
                signal_type=signal_type,
                reason=reason,
            )

            continue

        try:
            plan = trade_workflow.create_plan(
                signal
            )

        except Exception as error:
            message = (
                f"Skipping {signal.symbol}: "
                "unable to create trade plan: "
                f"{error}"
            )

            print(message)

            record_event_safely(
                journal,
                symbol=signal.symbol,
                status="plan_creation_failed",
                signal_type=signal_type,
                reason=str(error),
            )

            continue


        if plan.quantity <= 0:
            reason = (
                "Quantity is zero after risk limits"
            )

            print(
                f"Skipping {plan.symbol}: "
                f"{reason.lower()}."
            )

            record_plan_safely(
                journal,
                plan=plan,
                status="risk_filtered",
                reason=reason,
            )

            continue

        eligible_plans.append(plan)

    print("=" * 60)

    if not eligible_plans:
        print(
            "\nNo trade plans remained after "
            "direction and risk filters were applied."
        )

        send_notification_safely(
            notification_sender,
            (
                "NO ELIGIBLE TRADES\n\n"
                "Signals were found, but none "
                "remained after direction and "
                "risk filters."
            ),
        )
        return

    ranked_trades = rank_trade_plans(
        eligible_plans
    )

    qualified_trades = [
        trade
        for trade in ranked_trades
        if trade.score >= MINIMUM_TRADE_SCORE
    ]

    print()
    print("=" * 60)
    print("TRADE RANKINGS")
    print("=" * 60)

    for position, trade_score in enumerate(
        ranked_trades,
        start=1,
    ):
        score_status = (
            "QUALIFIED"
            if trade_score.score
            >= MINIMUM_TRADE_SCORE
            else "BELOW MINIMUM"
        )

        print(
            f"{position}. "
            f"{trade_score.plan.symbol} | "
            f"Score: {trade_score.score:.2f} | "
            f"{score_status}"
        )

        for reason in trade_score.reasons:
            print(
                f"   - {reason}"
            )

    print("=" * 60)

    if not qualified_trades:
        print(
            "\nNo trade candidates met the "
            "minimum score requirement."
        )

        send_notification_safely(
            notification_sender,
            (
                "SCAN COMPLETE\n\n"
                "No trade candidates met the "
                "minimum score of "
                f"{MINIMUM_TRADE_SCORE:.0f}."
            ),
        )
        return

    for trade_score in qualified_trades:
        plan = trade_score.plan
        trade_id = create_trade_id()

        record_plan_safely(
            journal,
            plan=plan,
            status="candidate_ranked",
            score=trade_score.score,
            reason=(
                "Candidate passed direction, risk, "
                "and minimum-score filters."
            ),
            trade_id=trade_id,
        )

        print()
        print("=" * 60)
        print(
            f"EVALUATING {plan.symbol}"
        )
        print("=" * 60)
        print(
            f"Trade ID: {trade_id}"
        )
        print(
            f"Trade Score: "
            f"{trade_score.score:.2f}"
        )
        print()
        print(
            format_trade_plan(plan)
        )

        try:
            allowed, portfolio_reason = (
                portfolio_manager
                .can_open_new_trade()
            )

        except Exception as error:
            message = (
                f"Skipping {plan.symbol}: "
                "unable to check portfolio state: "
                f"{error}"
            )

            print(message)

            record_plan_safely(
                journal,
                plan=plan,
                status="portfolio_check_error",
                score=trade_score.score,
                reason=str(error),
                trade_id=trade_id,
            )

            send_notification_safely(
                notification_sender,
                (
                    "PORTFOLIO CHECK ERROR\n\n"
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

            record_plan_safely(
                journal,
                plan=plan,
                status="portfolio_blocked",
                score=trade_score.score,
                reason=portfolio_reason,
                trade_id=trade_id,
            )

            send_notification_safely(
                notification_sender,
                (
                    "TRADE BLOCKED\n\n"
                    f"Symbol: {plan.symbol}\n"
                    f"Reason: {portfolio_reason}"
                ),
            )
            continue

        try:
            preflight = trade_workflow._preflight_runner(
                plan
            )

        except Exception as error:
            message = (
                f"Skipping {plan.symbol}: "
                "broker preflight failed: "
                f"{error}"
            )

            print(message)

            record_plan_safely(
                journal,
                plan=plan,
                status="preflight_error",
                score=trade_score.score,
                reason=str(error),
                trade_id=trade_id,
            )

            send_notification_safely(
                notification_sender,
                (
                    "PREFLIGHT ERROR\n\n"
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
                print(
                    f"  - {reason}"
                )

            reason_text = "\n".join(
                f"- {reason}"
                for reason in preflight.reasons
            )

            record_plan_safely(
                journal,
                plan=plan,
                status="preflight_rejected",
                score=trade_score.score,
                reason="; ".join(
                    preflight.reasons
                ),
                trade_id=trade_id,
            )

            send_notification_safely(
                notification_sender,
                (
                    "PREFLIGHT REJECTED\n\n"
                    f"Symbol: {plan.symbol}\n\n"
                    f"{reason_text}"
                ),
            )
            continue

        print(
            "\nPreflight checks passed."
        )

        workflow_result = WorkflowResult(
            ready_for_approval=True,
            plan=plan,
            preflight=preflight,
        )

        record_plan_safely(
            journal,
            plan=plan,
            status="preflight_passed",
            score=trade_score.score,
            reason=(
                "All broker preflight checks passed."
            ),
            trade_id=trade_id,
        )

        send_notification_safely(
            notification_sender,
            format_trade_alert(
                plan=plan,
                score=trade_score.score,
            ),
        )

        if not EXECUTION_ENABLED:
            print()
            print(
                "Execution is disabled. "
                "No paper order was submitted for "
                f"{plan.symbol}."
            )
            print(
                "Set EXECUTION_ENABLED = True in "
                "config/trading_config.py when ready."
            )

            record_plan_safely(
                journal,
                plan=plan,
                status="execution_disabled",
                score=trade_score.score,
                reason=(
                    "Trade passed preflight, but "
                    "execution is disabled in "
                    "configuration."
                ),
                trade_id=trade_id,
            )

            send_notification_safely(
                notification_sender,
                (
                    "EXECUTION DISABLED\n\n"
                    f"{plan.symbol} passed preflight, "
                    "but paper execution is disabled."
                ),
            )
            return

        order = trade_execution_service.execute(
            workflow_result
        )

        if order is None:
            print(
                "\nPaper order for "
                f"{plan.symbol} cancelled."
            )

            record_plan_safely(
                journal,
                plan=plan,
                status="user_cancelled",
                score=trade_score.score,
                reason=(
                    "Paper order was not approved "
                    "in the terminal."
                ),
                trade_id=trade_id,
            )

            send_notification_safely(
                notification_sender,
                (
                    "ORDER CANCELLED\n\n"
                    f"Symbol: {plan.symbol}\n"
                    "The paper order was not "
                    "approved in the terminal."
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
                "\nWarning: Alpaca returned an "
                "order without an order ID."
            )

            record_plan_safely(
                journal,
                plan=plan,
                status="missing_order_id",
                score=trade_score.score,
                reason=(
                    "Alpaca returned an order "
                    "without an order ID."
                ),
                trade_id=trade_id,
            )

            send_notification_safely(
                notification_sender,
                (
                    "MISSING ORDER ID\n\n"
                    "Alpaca accepted the "
                    f"{plan.symbol} request but "
                    "returned no order ID."
                ),
            )
            return

        try:
            verified_order = (
                verify_submitted_order(
                    client=trading_client,
                    order_id=order_id,
                )
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

            record_plan_safely(
                journal,
                plan=plan,
                status="verification_failed",
                score=trade_score.score,
                reason=str(error),
                trade_id=trade_id,
                order_id=order_id,
            )

            send_notification_safely(
                notification_sender,
                (
                    "ORDER VERIFICATION FAILED\n\n"
                    f"Symbol: {plan.symbol}\n"
                    f"Trade ID: {trade_id}\n"
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

        if trade_repository is not None:
            trade_repository.save(
                Trade(
                    trade_id=trade_id,
                    symbol=plan.symbol,
                    quantity=plan.quantity,
                    status=TradeStatus.SUBMITTED,
                    entry_price=plan.entry_price,
                    stop_price=plan.stop_price,
                    target_price=plan.target_price,
                    parent_order_id=str(order_id),
                )
            )

        print()
        print("=" * 60)
        print(
            "PAPER ORDER SUBMITTED AND VERIFIED"
        )
        print("=" * 60)
        print(
            f"Symbol:   {order_symbol}"
        )
        print(
            f"Side:     {plan.signal_type}"
        )
        print(
            f"Quantity: {plan.quantity}"
        )
        print(
            f"Score:    {trade_score.score:.2f}"
        )
        print(
            f"Trade ID: {trade_id}"
        )
        print(
            f"Order ID: {order_id}"
        )
        print(
            f"Status:   {order_status}"
        )
        print("=" * 60)

        record_plan_safely(
            journal,
            plan=plan,
            status="submitted_verified",
            score=trade_score.score,
            reason=(
                "Broker order status: "
                f"{order_status}"
            ),
            trade_id=trade_id,
            order_id=order_id,
        )

        send_notification_safely(
            notification_sender,
            (
                "PAPER ORDER SUBMITTED\n\n"
                f"Symbol: {order_symbol}\n"
                f"Side: {plan.signal_type}\n"
                f"Quantity: {plan.quantity}\n"
                f"Entry: ${plan.entry_price:,.2f}\n"
                f"Stop: ${plan.stop_price:,.2f}\n"
                f"Target: ${plan.target_price:,.2f}\n"
                f"Score: {trade_score.score:.2f}\n"
                f"Status: {order_status}\n"
                f"Trade ID: {trade_id}\n"
                f"Order ID: {order_id}"
            ),
        )

        return

    print(
        "\nNo paper orders were submitted."
    )

    send_notification_safely(
        notification_sender,
        (
            "SCAN COMPLETE\n\n"
            "Qualified candidates were evaluated, "
            "but no paper orders were submitted."
        ),
    )


def run_production(
    *,
    database_path: Path | str = DATABASE_PATH,
) -> None:

    journal = TradeJournal(
        database_path=database_path,
    )

    trade_repository = create_trade_repository(
        database_path=database_path,
    )

    trade_approval = None

    if TELEGRAM_APPROVAL_ENABLED:
        trade_approval = create_runtime_telegram_approval(
            bot_token=TELEGRAM_BOT_TOKEN,
            chat_id=TELEGRAM_CHAT_ID,
        )

    if trade_approval is None:
        main(
            notification_sender=send_telegram_message,
            journal=journal,
            trade_repository=trade_repository,
        )
    else:
        main(
            notification_sender=send_telegram_message,
            journal=journal,
            trade_repository=trade_repository,
            trade_approval=trade_approval,
        )