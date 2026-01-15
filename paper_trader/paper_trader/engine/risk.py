# paper_trader/engine/risk.py

from datetime import date
from typing import Dict

from paper_trader.engine.portfolio import Portfolio
from paper_trader.engine.position import Position


class RiskManager:
    """
    Central risk gatekeeper.
    NO execution, NO signals, NO prices.
    Only answers: should we allow this trade?
    """

    def __init__(
        self,
        portfolio: Portfolio,
        max_open_positions: int = 5,
        max_risk_per_trade_pct: float = 1.0,
        max_daily_loss_pct: float = 3.0,
        max_drawdown_pct: float = 20.0,
    ):
        self.portfolio = portfolio

        self.max_open_positions = max_open_positions
        self.max_risk_per_trade_pct = max_risk_per_trade_pct
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_drawdown_pct = max_drawdown_pct

        self.starting_equity = portfolio.initial_capital
        self.today = None
        self.daily_pnl = 0.0

    # ─────────────────────────────
    # DAILY RESET
    # ─────────────────────────────

    def on_new_day(self, current_date: date):
        if self.today != current_date:
            self.today = current_date
            self.daily_pnl = 0.0

    # ─────────────────────────────
    # PNL TRACKING
    # ─────────────────────────────

    def register_closed_trade(self, pnl: float):
        self.daily_pnl += pnl

    # ─────────────────────────────
    # HARD STOPS
    # ─────────────────────────────

    def is_daily_loss_limit_hit(self) -> bool:
        max_loss = (
            self.portfolio.current_capital
            * self.max_daily_loss_pct
            / 100
        )
        return self.daily_pnl <= -max_loss

    def is_drawdown_limit_hit(self) -> bool:
        drawdown = (
            (self.starting_equity - self.portfolio.current_capital)
            / self.starting_equity
            * 100
        )
        return drawdown >= self.max_drawdown_pct

    # ─────────────────────────────
    # POSITION RULES
    # ─────────────────────────────

    def can_open_position(self, position: Position) -> bool:
        """
        Master risk gate.
        """

        # 1️⃣ Max open positions
        if self.portfolio.open_position_count() >= self.max_open_positions:
            return False

        # 2️⃣ Capital risk per trade
        trade_risk = abs(position.entry_price - position.stop_loss) * position.quantity
        max_allowed_risk = (
            self.portfolio.current_capital
            * self.max_risk_per_trade_pct
            / 100
        )

        if trade_risk > max_allowed_risk:
            return False

        # 3️⃣ Daily loss limit
        if self.is_daily_loss_limit_hit():
            return False

        # 4️⃣ Max drawdown protection
        if self.is_drawdown_limit_hit():
            return False

        return True
