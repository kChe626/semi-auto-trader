from trade_management.exit_policy import (
    ExitAction,
    evaluate_exit,
)


def test_holds_during_first_two_days() -> None:
    result = evaluate_exit(
        entry_price=100.0,
        initial_stop_price=98.0,
        current_price=99.0,
        short_sma=100.0,
        long_sma=99.0,
        trading_days_held=2,
    )

    assert result.action == ExitAction.HOLD


def test_moves_stop_to_breakeven_at_one_r() -> None:
    result = evaluate_exit(
        entry_price=100.0,
        initial_stop_price=98.0,
        current_price=102.0,
        short_sma=101.0,
        long_sma=99.0,
        trading_days_held=1,
    )

    assert (
        result.action
        == ExitAction.MOVE_STOP_TO_BREAKEVEN
    )


def test_closes_after_day_three_below_short_sma() -> None:
    result = evaluate_exit(
        entry_price=100.0,
        initial_stop_price=98.0,
        current_price=100.0,
        short_sma=101.0,
        long_sma=99.0,
        trading_days_held=3,
    )

    assert result.action == ExitAction.CLOSE


def test_closes_after_day_three_on_bearish_crossover() -> None:
    result = evaluate_exit(
        entry_price=100.0,
        initial_stop_price=98.0,
        current_price=101.0,
        short_sma=99.0,
        long_sma=100.0,
        trading_days_held=3,
    )

    assert result.action == ExitAction.CLOSE


def test_holds_profitable_trade_with_healthy_trend() -> None:
    result = evaluate_exit(
        entry_price=100.0,
        initial_stop_price=98.0,
        current_price=101.0,
        short_sma=100.5,
        long_sma=99.0,
        trading_days_held=4,
    )

    assert result.action == ExitAction.HOLD


def test_hard_exit_on_day_seven() -> None:
    result = evaluate_exit(
        entry_price=100.0,
        initial_stop_price=98.0,
        current_price=103.0,
        short_sma=102.0,
        long_sma=100.0,
        trading_days_held=7,
    )

    assert result.action == ExitAction.CLOSE
    assert "maximum holding period" in result.reason.lower()

def test_hard_exit_takes_priority_over_breakeven() -> None:
    result = evaluate_exit(
        entry_price=100.0,
        initial_stop_price=98.0,
        current_price=103.0,
        short_sma=102.0,
        long_sma=100.0,
        trading_days_held=7,
    )

    assert result.action == ExitAction.CLOSE


def test_trend_failure_takes_priority_after_day_three() -> None:
    result = evaluate_exit(
        entry_price=100.0,
        initial_stop_price=98.0,
        current_price=102.0,
        short_sma=103.0,
        long_sma=100.0,
        trading_days_held=4,
    )

    assert result.action == ExitAction.CLOSE