from datetime import datetime

from autotrader.domain import Candle, Position, Side
from autotrader.execution import ExecutionConfig, ExecutionSimulator


def candle(**kwargs):
    return Candle(**kwargs)


def test_entry_is_filled_at_next_open_with_slippage():
    execution = ExecutionSimulator(ExecutionConfig(slippage_bps=10))
    order = __import__("autotrader.domain", fromlist=["Order"]).Order(
        "TEST", Side.LONG, 1, datetime(2024, 1, 1), "test", 90.0, 110.0
    )
    fill = execution.entry_fill(order, candle(symbol="TEST", timestamp=datetime(2024,1,2), open=100, high=105, low=95, close=102, volume=1))
    assert fill.price == 100.1


def test_stop_wins_collision_under_conservative_policy():
    execution = ExecutionSimulator(ExecutionConfig(collision_policy="stop_first", slippage_bps=0))
    position = Position("TEST", Side.LONG, 1, 100, datetime(2024,1,1), 95, 105, "test")
    fill = execution.exit_fill(position, candle(symbol="TEST", timestamp=datetime(2024,1,2), open=100, high=110, low=90, close=100, volume=1))
    assert fill is not None
    assert fill.reason == "stop"
    assert fill.price == 95
