# paper_trader/engine/position.py

from typing import Dict
from datetime import datetime


class Position:
    """
    Represents a single open or closed trade.
    Handles PnL math and lifecycle only.
    """

    def __init__(
        self,
        symbol: str,
        direction: str,        # "LONG" or "SHORT"
        entry_price: float,
        quantity: int,
        stop_loss: float,
        target: float,
        entry_time: datetime,
        pattern: str = "",
        signal_index: int = None,
    ):
        self.symbol = symbol
        self.direction = direction
        self.entry_price = float(entry_price)
        self.quantity = int(quantity)
        self.stop_loss = float(stop_loss)
        self.target = float(target)

        self.pattern = pattern
        self.signal_index = signal_index

        self.entry_time = entry_time
        self.exit_time = None
        self.exit_price = None
        self.exit_reason = None

        self.is_open = True

    # ─────────────────────────────
    # VALUES
    # ─────────────────────────────

    @property
    def entry_value(self) -> float:
        return round(self.entry_price * self.quantity, 2)

    @property
    def exit_value(self) -> float:
        if self.exit_price is None:
            return 0.0
        return round(self.exit_price * self.quantity, 2)

    # ─────────────────────────────
    # MARK TO MARKET
    # ─────────────────────────────

    def market_value(self, price: float) -> float:
        """
        Unrealized value at current price.
        """
        price = float(price)

        if self.direction == "LONG":
            return round(price * self.quantity, 2)
        else:
            # SHORT position value = cash locked + PnL
            return round(
                (self.entry_price + (self.entry_price - price)) * self.quantity,
                2,
            )

    def unrealized_pnl(self, price: float) -> float:
        price = float(price)

        if self.direction == "LONG":
            return round(
                (price - self.entry_price) * self.quantity,
                2,
            )
        else:
            return round(
                (self.entry_price - price) * self.quantity,
                2,
            )

    # ─────────────────────────────
    # EXIT
    # ─────────────────────────────

    def close(self, exit_price: float, reason: str) -> float:
        """
        Close the position and return realized PnL.
        """
        if not self.is_open:
            return 0.0

        self.exit_price = float(exit_price)
        self.exit_time = datetime.utcnow()
        self.exit_reason = reason
        self.is_open = False

        return self.realized_pnl

    @property
    def realized_pnl(self) -> float:
        if self.exit_price is None:
            return 0.0

        if self.direction == "LONG":
            return round(
                (self.exit_price - self.entry_price) * self.quantity,
                2,
            )
        else:
            return round(
                (self.entry_price - self.exit_price) * self.quantity,
                2,
            )

    # ─────────────────────────────
    # STOP / TARGET CHECKS
    # ─────────────────────────────

    def hit_stop(self, high: float, low: float) -> bool:
        if self.direction == "LONG":
            return low <= self.stop_loss
        else:
            return high >= self.stop_loss

    def hit_target(self, high: float, low: float) -> bool:
        if self.direction == "LONG":
            return high >= self.target
        else:
            return low <= self.target

    # ─────────────────────────────
    # SERIALIZATION
    # ─────────────────────────────

    def snapshot(self) -> Dict:
        """
        Lightweight snapshot for UI / API.
        """
        return {
            "symbol": self.symbol,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "quantity": self.quantity,
            "stop_loss": self.stop_loss,
            "target": self.target,
            "pattern": self.pattern,
            "is_open": self.is_open,
        }

    def to_dict(self) -> Dict:
        """
        Full trade record (for logs / stats).
        """
        return {
            "symbol": self.symbol,
            "direction": self.direction,
            "pattern": self.pattern,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
            "exit_reason": self.exit_reason,
            "pnl": self.realized_pnl,
            "signal_index": self.signal_index,
        }
