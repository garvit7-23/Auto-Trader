# paper_trader/engine/execution.py

from datetime import datetime
from typing import Dict, List

from paper_trader.engine.position import Position
from paper_trader.engine.portfolio import Portfolio


class ExecutionEngine:
    """
    Responsible for:
    - Opening positions from signals
    - Managing stop-loss / target exits per candle
    """

    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    # ─────────────────────────────
    # ENTRY
    # ─────────────────────────────

    def execute_entries(
        self,
        signals: List[Dict],
        candle_time: datetime,
    ):
        """
        Convert strategy signals into open positions.
        """

        for signal in signals:
            symbol = signal["symbol"]

            # One position per symbol (simple rule for now)
            if self.portfolio.has_open_position(symbol):
                continue

            qty = signal["quantity"]
            if qty <= 0:
                continue

            position = Position(
                symbol=symbol,
                direction=signal["direction"],
                entry_price=signal["entry"],
                quantity=qty,
                stop_loss=signal["stop_loss"],
                target=signal["target"],
                entry_time=candle_time,
                pattern=signal.get("pattern", ""),
                signal_index=signal.get("signal_index"),
            )

            self.portfolio.open_position(position)

    # ─────────────────────────────
    # EXIT
    # ─────────────────────────────

    def execute_exits(
        self,
        symbol: str,
        high: float,
        low: float,
        candle_time: datetime,
    ):
        """
        Check stop-loss and target for an open position
        using OHLC logic.
        """

        position = self.portfolio.get_position(symbol)
        if not position:
            return

        # STOP first (risk-first rule)
        if position.hit_stop(high=high, low=low):
            exit_price = position.stop_loss
            self.portfolio.close_position(
                symbol=symbol,
                exit_price=exit_price,
                reason="STOP",
                exit_time=candle_time,
            )
            return

        # TARGET second
        if position.hit_target(high=high, low=low):
            exit_price = position.target
            self.portfolio.close_position(
                symbol=symbol,
                exit_price=exit_price,
                reason="TARGET",
                exit_time=candle_time,
            )

    # ─────────────────────────────
    # BAR HANDLER
    # ─────────────────────────────

    def on_candle(
        self,
        symbol: str,
        candle: Dict,
        signals: List[Dict],
    ):
        """
        Called once per candle per symbol.
        """

        candle_time = candle.get("time") or datetime.utcnow()

        high = float(candle["high"])
        low = float(candle["low"])

        # 1️⃣ Exit logic (existing positions)
        self.execute_exits(
            symbol=symbol,
            high=high,
            low=low,
            candle_time=candle_time,
        )

        # 2️⃣ Entry logic (new signals)
        if signals:
            self.execute_entries(
                signals=signals,
                candle_time=candle_time,
            )
