# paper_trader/engine/portfolio.py

from typing import Dict, List
from paper_trader.engine.position import Position


class Portfolio:
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.equity = initial_capital

        self.open_positions: Dict[str, Position] = {}
        self.closed_trades: List[Dict] = []

    # ─────────────────────────────
    # POSITION MANAGEMENT
    # ─────────────────────────────

    def add_position(self, position: Position):
        self.open_positions[position.symbol] = position
        self.cash -= position.entry_price * position.quantity

    def close_position(
     self,
     symbol: str,
     exit_price: float,
     reason: str,
     exit_time=None,
     timestamp=None,
      ):
     position = self.open_positions.pop(symbol)

     close_time = exit_time if exit_time is not None else timestamp

     pnl = position.close(exit_price, close_time)
     self.cash += position.exit_price * position.quantity

     trade_record = position.to_dict()
     trade_record["pnl"] = pnl
     trade_record["exit_reason"] = reason

     self.closed_trades.append(trade_record)
     return pnl

 
    

    # ─────────────────────────────
    # MARK TO MARKET
    # ─────────────────────────────

    def mark_to_market(self, market_data: Dict[str, object], idx: int):
        unrealized = 0.0

        for symbol, position in self.open_positions.items():
            df = market_data[symbol]

            if idx >= len(df):
                continue

            price = df.iloc[idx]["close"]
            unrealized += position.unrealized_pnl(price)

        self.equity = self.cash + unrealized

    # ─────────────────────────────
    # SERIALIZATION / SNAPSHOT
    # ─────────────────────────────

    def serialize_positions(self):
        return {
            symbol: pos.to_dict()
            for symbol, pos in self.open_positions.items()
        }

    def snapshot(self):
        return {
            "cash": round(self.cash, 2),
            "equity": round(self.equity, 2),
            "open_positions": self.serialize_positions(),
            "closed_trades": self.closed_trades,
        }

    # ─────────────────────────────
    # RESET
    # ─────────────────────────────

    def reset(self):
        self.cash = self.initial_capital
        self.equity = self.initial_capital
        self.open_positions.clear()
        self.closed_trades.clear()
    
    def has_open_position(self, symbol: str) -> bool:
     return symbol in self.open_positions


    # paper_trader/engine/portfolio.py

    # ─────────────────────────────
    # ADAPTER METHODS (REQUIRED)
    # ─────────────────────────────

    def open_position(self, position: Position):
        """
        Adapter for ExecutionEngine
        """
        self.add_position(position)

    def get_position(self, symbol: str):
        return self.open_positions.get(symbol)
