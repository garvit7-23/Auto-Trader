from typing import Dict, List, Optional

import pandas as pd

from core.indicators import ema, rsi, atr, adx
from core.strategy_engine import StrategyEngine
from paper_trader.engine.portfolio import Portfolio
from paper_trader.engine.execution import ExecutionEngine


class PaperTradingEngine:
    """
    Event-driven paper trading engine.

    - Advances one candle at a time
    - Uses StrategyEngine for signal generation
    - Manages positions via Portfolio + ExecutionEngine
    """

    def __init__(self, initial_capital: float):
        # Core components
        self.portfolio = Portfolio(initial_capital)
        self.execution = ExecutionEngine(self.portfolio)

        # Injected later
        self.strategy_engine: Optional[StrategyEngine] = None

        # Market state
        self.market_data: Dict[str, pd.DataFrame] = {}
        self.symbols: List[str] = []

        # Time control
        self.current_index = 0
        self.max_bars = 0
        self.running = False

    # ─────────────────────────────
    # DEPENDENCY INJECTION
    # ─────────────────────────────

    def set_strategy(self, strategy_engine: StrategyEngine):
        self.strategy_engine = strategy_engine

    def load_market_data(self, market_data: Dict[str, pd.DataFrame]):
        """
        Preload mode (CSV replay).
        """
        self.market_data = market_data
        self.symbols = list(market_data.keys())
        self.max_bars = min(len(df) for df in market_data.values())

    # ─────────────────────────────
    # LIVE / REPLAY ENTRY POINT
    # ─────────────────────────────

    def on_tick(self, candle: Dict, symbol: str | None = None):
     """
     Live / replay mode entry point.

     - Single-symbol mode: symbol inferred
     - Multi-symbol mode: symbol explicitly passed
     """

     if self.strategy_engine is None:
        raise RuntimeError("StrategyEngine not set")

     # ───── Resolve symbol ─────
     if symbol is None:
         if not self.symbols:
             symbol = "SYMBOL"
             self.symbols = [symbol]
             self.market_data[symbol] = pd.DataFrame()
             self.current_index = 0
             self.running = True
         else:
             symbol = self.symbols[0]

     if symbol not in self.market_data:
         self.market_data[symbol] = pd.DataFrame()

     # ───── Append candle ─────
     df = self.market_data[symbol]
     df = pd.concat([df, pd.DataFrame([candle])], ignore_index=True)

     # ───── Indicators ─────
     from core.indicators import ema, rsi, atr, adx
     from core.swings import detect_swings

     df["ema20"] = ema(df["close"], 20)
     df["ema50"] = ema(df["close"], 50)
     df["rsi"] = rsi(df["close"])
     df["atr"] = atr(df)
     df["adx"] = adx(df)
     df["volume_sma"] = df["volume"].rolling(20).mean()

     # EXACT backtest parity
     df = detect_swings(df)

     # ───── WARM-UP GUARD ─────
     if len(df) < 60:
         self.market_data[symbol] = df
         self.current_index += 1
         return {
             "status": "warming_up",
             "index": self.current_index,
             "bars": len(df),
             "cash": self.portfolio.cash,
             "equity": self.portfolio.equity,
             " open_positions": 0,
         }

     self.market_data[symbol] = df
     self.max_bars = min(len(d) for d in self.market_data.values())

     return self.step()



    # ─────────────────────────────
    # CONTROL
    # ─────────────────────────────

    def start(self):
        if self.strategy_engine is None:
            raise RuntimeError("StrategyEngine not set")

        if not self.market_data:
            raise RuntimeError("Market data not loaded")

        self.current_index = 0
        self.portfolio.reset()
        self.running = True

    def stop(self):
        self.running = False

    # ─────────────────────────────
    # CORE LOOP (ONE TICK)
    # ─────────────────────────────

    def step(self) -> Dict:
     """
     Advance the engine by ONE candle.
     """

     if not self.running:
         return {"status": "stopped"}

     if self.current_index >= self.max_bars:
         self.running = False
         return {"status": "finished"}

     # ─────────────────────────
     # 1️⃣ EXIT LOGIC (current candle)
     # ─────────────────────────
     for symbol in list(self.portfolio.open_positions.keys()):
         df = self.market_data[symbol]

         if self.current_index >= len(df):
             continue

         row = df.iloc[self.current_index]
         self.execution.execute_exits(
             symbol=symbol,
             high=row["high"],
             low=row["low"],
             candle_time=row.get("date"),
         )

     # ─────────────────────────
     # 2️⃣ ENTRY LOGIC (previous candle)
     # ─────────────────────────
     signal_idx = self.current_index - 1

     if signal_idx < 2:
         self.current_index += 1
         return {
             "status": "warming_up",
             "index": self.current_index,
             "cash": self.portfolio.cash,
             "equity": self.portfolio.equity,
             "open_positions": len(self.portfolio.open_positions),
         }

     for symbol, df in self.market_data.items():

         if symbol in self.portfolio.open_positions:
             continue

         if signal_idx >= len(df):
             continue

         signals = self.strategy_engine.generate_signals_for_index(
             symbol=symbol,
             df=df,
             idx=signal_idx,
             capital=self.portfolio.cash,
         )

         if signals:
             row = df.iloc[self.current_index]
             self.execution.execute_entries(
                 signals=signals,
                 candle_time=row.get("date"),
             )

     # ─────────────────────────
     # 3️⃣ MARK TO MARKET
     # ─────────────────────────
     self.portfolio.mark_to_market(self.market_data, self.current_index)

     self.current_index += 1

     return {
         "status": "running",
         "index": self.current_index,
         "cash": self.portfolio.cash,
         "equity": self.portfolio.equity,
         "open_positions": len(self.portfolio.open_positions),
     }

  

    # ─────────────────────────────
    # SNAPSHOT
    # ─────────────────────────────

    def snapshot(self) -> Dict:
        return {
            "running": self.running,
            "current_index": self.current_index,
            "cash": self.portfolio.cash,
            "equity": self.portfolio.equity,
            "open_positions": self.portfolio.serialize_positions(),
            "closed_trades": self.portfolio.closed_trades,
        }
