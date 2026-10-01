from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .domain import Fill, Position, Side
from .execution import ExecutionSimulator


@dataclass(frozen=True)
class PortfolioSnapshot:
    timestamp: object
    cash: float
    equity: float
    realized_pnl: float
    unrealized_pnl: float
    open_positions: int


class Portfolio:
    """Single-account portfolio with explicit long/short cash accounting."""

    def __init__(self, initial_capital: float, execution: ExecutionSimulator) -> None:
        if initial_capital <= 0:
            raise ValueError("initial_capital must be positive")
        self.initial_capital = float(initial_capital)
        self.cash = float(initial_capital)
        self.realized_pnl = 0.0
        self.positions: Dict[str, Position] = {}
        self.execution = execution
        self._entry_cashflow: Dict[str, float] = {}

    def equity(self, prices: Dict[str, float]) -> float:
        value = self.cash
        for symbol, position in self.positions.items():
            price = prices[symbol]
            value += position.market_value(price)
            value -= position.short_liability(price)
        return value

    def unrealized_pnl(self, prices: Dict[str, float]) -> float:
        return sum(p.unrealized_pnl(prices[p.symbol]) for p in self.positions.values())

    def open_positions(self) -> int:
        return len(self.positions)

    def apply_entry(self, fill: Fill, stop_loss: float, target: Optional[float]) -> None:
        if fill.symbol in self.positions:
            raise ValueError(f"Position already exists for {fill.symbol}")
        notional = fill.price * fill.quantity
        fee = self.execution.commission(notional)
        if fill.side is Side.LONG:
            self.cash -= notional + fee
        else:
            self.cash += notional - fee
        self.positions[fill.symbol] = Position(
            fill.symbol, fill.side, fill.quantity, fill.price, fill.timestamp,
            stop_loss, target, fill.strategy
        )
        self._entry_cashflow[fill.symbol] = self.cash

    def apply_exit(self, fill: Fill) -> float:
        position = self.positions.pop(fill.symbol)
        if position.side is Side.LONG:
            cashflow = fill.price * fill.quantity
        else:
            cashflow = -fill.price * fill.quantity
        fee = self.execution.commission(fill.price * fill.quantity)
        self.cash += cashflow - fee
        pnl = position.unrealized_pnl(fill.price) - fee
        # Entry fees were already charged to cash; realized P&L here is the
        # price P&L plus exit fee. Entry fees are included in equity/cash history.
        self.realized_pnl += pnl
        self._entry_cashflow.pop(fill.symbol, None)
        return pnl

    def assert_invariants(self, prices: Dict[str, float]) -> None:
        if self.cash != self.cash:  # NaN guard
            raise AssertionError("cash is NaN")
        equity = self.equity(prices)
        if equity != equity:
            raise AssertionError("equity is NaN")
        if any(p.quantity <= 0 for p in self.positions.values()):
            raise AssertionError("positions must have positive quantity")
