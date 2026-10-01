from __future__ import annotations

from dataclasses import dataclass

from .domain import Candle, Fill, Order, Side


@dataclass(frozen=True)
class ExecutionConfig:
    commission_bps: float = 1.0
    slippage_bps: float = 2.0
    collision_policy: str = "stop_first"


class ExecutionSimulator:
    """Deterministic OHLC execution model.

    Entry orders fill at the next candle's open. Existing stops/targets are
    evaluated against the candle range. If both are touched in one candle,
    the configured collision policy resolves the unknowable intrabar order.
    """

    def __init__(self, config: ExecutionConfig | None = None) -> None:
        self.config = config or ExecutionConfig()
        if self.config.collision_policy not in {"stop_first", "target_first"}:
            raise ValueError("Unsupported collision policy")

    def entry_fill(self, order: Order, candle: Candle) -> Fill:
        if order.side is Side.LONG:
            price = candle.open * (1 + self.config.slippage_bps / 10_000)
        else:
            price = candle.open * (1 - self.config.slippage_bps / 10_000)
        return Fill(order.symbol, order.side, order.quantity, price, candle.timestamp, "entry", order.strategy)

    def exit_fill(self, position, candle: Candle) -> Fill | None:
        stop_hit = candle.low <= position.stop_loss if position.side is Side.LONG else candle.high >= position.stop_loss
        target_hit = False
        if position.target is not None:
            target_hit = candle.high >= position.target if position.side is Side.LONG else candle.low <= position.target

        if not stop_hit and not target_hit:
            return None

        if stop_hit and target_hit:
            reason = "stop" if self.config.collision_policy == "stop_first" else "target"
        else:
            reason = "stop" if stop_hit else "target"

        raw_price = position.stop_loss if reason == "stop" else position.target
        assert raw_price is not None
        if position.side is Side.LONG:
            price = raw_price * (1 - self.config.slippage_bps / 10_000)
        else:
            price = raw_price * (1 + self.config.slippage_bps / 10_000)
        return Fill(position.symbol, position.side, position.quantity, price, candle.timestamp, reason, position.strategy)

    def commission(self, notional: float) -> float:
        return abs(notional) * self.config.commission_bps / 10_000
