from datetime import datetime

from autotrader.domain import Candle, Fill, Side
from autotrader.execution import ExecutionSimulator
from autotrader.portfolio import Portfolio


def test_long_round_trip_preserves_equity_before_fees():
    execution = ExecutionSimulator()
    p = Portfolio(100_000, execution)
    t = datetime(2024, 1, 1)
    entry = Fill("TEST", Side.LONG, 100, 100.0, t, "entry", "test")
    p.apply_entry(entry, 95.0, 110.0)
    assert round(p.equity({"TEST": 100.0}), 8) == round(100_000 - execution.commission(10_000), 8)


def test_short_open_has_zero_mark_to_market_pnl_at_entry():
    execution = ExecutionSimulator()
    p = Portfolio(100_000, execution)
    t = datetime(2024, 1, 1)
    p.apply_entry(Fill("TEST", Side.SHORT, 100, 100.0, t, "entry", "test"), 105.0, 90.0)
    assert round(p.equity({"TEST": 100.0}), 8) == round(100_000 - execution.commission(10_000), 8)


def test_short_profit_increases_equity_when_price_falls():
    execution = ExecutionSimulator()
    p = Portfolio(100_000, execution)
    t = datetime(2024, 1, 1)
    p.apply_entry(Fill("TEST", Side.SHORT, 100, 100.0, t, "entry", "test"), 105.0, 90.0)
    assert p.equity({"TEST": 90.0}) > p.equity({"TEST": 100.0})
