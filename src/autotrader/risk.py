from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .domain import Signal, Side


@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    quantity: int = 0
    reason: Optional[str] = None


@dataclass(frozen=True)
class RiskConfig:
    risk_per_trade: float = 0.01
    max_position_notional_pct: float = 0.25
    max_open_positions: int = 5
    min_quantity: int = 1


class RiskManager:
    """Pure position-sizing and admission policy.

    The manager never mutates portfolio state. It receives the current equity,
    price, stop distance, and portfolio occupancy and returns an auditable
    approval/rejection decision.
    """

    def __init__(self, config: RiskConfig | None = None) -> None:
        self.config = config or RiskConfig()

    def evaluate(
        self,
        signal: Signal,
        *,
        equity: float,
        open_positions: int,
        current_price: float,
    ) -> RiskDecision:
        if equity <= 0:
            return RiskDecision(False, reason="non_positive_equity")
        if open_positions >= self.config.max_open_positions:
            return RiskDecision(False, reason="max_open_positions")
        if signal.stop_loss <= 0 or current_price <= 0:
            return RiskDecision(False, reason="invalid_price")

        risk_per_share = abs(current_price - signal.stop_loss)
        if risk_per_share <= 0:
            return RiskDecision(False, reason="zero_stop_distance")

        risk_budget = equity * self.config.risk_per_trade
        quantity = int(risk_budget // risk_per_share)
        max_notional_qty = int(
            (equity * self.config.max_position_notional_pct) // current_price
        )
        quantity = min(quantity, max_notional_qty)

        if quantity < self.config.min_quantity:
            return RiskDecision(False, reason="position_below_minimum")

        return RiskDecision(True, quantity=quantity)
