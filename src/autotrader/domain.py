from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class Side(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"

    @property
    def sign(self) -> int:
        return 1 if self is Side.LONG else -1


@dataclass(frozen=True)
class Candle:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        if self.high < max(self.open, self.close) or self.low > min(self.open, self.close):
            raise ValueError("Invalid OHLC candle")
        if self.high < self.low:
            raise ValueError("Candle high cannot be below low")


@dataclass(frozen=True)
class Signal:
    symbol: str
    side: Side
    stop_loss: float
    target: Optional[float] = None
    strategy: str = "unknown"


@dataclass(frozen=True)
class Order:
    symbol: str
    side: Side
    quantity: int
    created_at: datetime
    strategy: str
    stop_loss: float
    target: Optional[float] = None


@dataclass(frozen=True)
class Fill:
    symbol: str
    side: Side
    quantity: int
    price: float
    timestamp: datetime
    reason: str
    strategy: str


@dataclass(frozen=True)
class Position:
    symbol: str
    side: Side
    quantity: int
    entry_price: float
    entry_time: datetime
    stop_loss: float
    target: Optional[float]
    strategy: str

    def unrealized_pnl(self, price: float) -> float:
        return (price - self.entry_price) * self.quantity * self.side.sign

    def market_value(self, price: float) -> float:
        return self.quantity * price if self.side is Side.LONG else 0.0

    def short_liability(self, price: float) -> float:
        return self.quantity * price if self.side is Side.SHORT else 0.0
