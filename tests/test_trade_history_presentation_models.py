from dashboard.trade_history_presentation_models import (
    TradeHistoryRowViewModel,
    TradeHistorySectionViewModel,
)


def test_section_identifies_empty_history() -> None:
    section = TradeHistorySectionViewModel(
        rows=(),
    )

    assert section.has_rows is False


def test_section_identifies_trade_history() -> None:
    section = TradeHistorySectionViewModel(
        rows=(
            TradeHistoryRowViewModel(
                trade_id="1",
                symbol="AAPL",
                side="BUY",
                opened_at="2026-07-20",
                closed_at="2026-07-21",
                quantity="10",
                entry_price="$200.00",
                exit_price="$205.00",
                realized_profit_loss="$50.00",
                r_multiple="1.00",
                holding_duration="1 day",
            ),
        ),
    )

    assert section.has_rows is True