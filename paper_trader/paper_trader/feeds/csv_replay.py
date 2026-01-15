import time
import pandas as pd
from typing import Optional

from core.strategy_engine import StrategyEngine
from paper_trader.config import CONFIG
from paper_trader.engine.paper_engine import PaperTradingEngine


class CSVReplayFeed:
    """
    Replays historical CSV data candle-by-candle
    into the PaperTradingEngine (live-like simulation).
    """

    def __init__(
        self,
        engine: PaperTradingEngine,
        csv_path: str,
        symbol: str,
        sleep: Optional[float] = None,  # seconds between ticks
    ):
        self.engine = engine
        self.csv_path = csv_path
        self.symbol = symbol
        self.sleep = sleep

        # ✅ CREATE STRATEGY ENGINE HERE
        self.strategy_engine = StrategyEngine(CONFIG)

        self.df: Optional[pd.DataFrame] = None
        self.pointer = 0

    # ─────────────────────────────
    # LOAD DATA
    # ─────────────────────────────

    def load(self):
        df = pd.read_csv(self.csv_path)

        required_cols = {"date", "open", "high", "low", "close", "volume"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"CSV missing columns: {missing}")

        df = df.sort_values("date").reset_index(drop=True)

        self.df = df
        self.pointer = 0

        # Initialize engine with EMPTY dataframe (streaming mode)
        self.engine.load_market_data({self.symbol: df.iloc[:0]})

    # ─────────────────────────────
    # REPLAY LOOP
    # ─────────────────────────────

    def run(self):
     if self.df is None:
         self.load()

     print(f"▶ Starting CSV replay for {self.symbol}")

     # Inject strategy
     self.engine.set_strategy(self.strategy_engine)

     # Start engine
     self.engine.start()

     while self.pointer < len(self.df):
         candle = self.df.iloc[self.pointer].to_dict()

         self.engine.on_tick(candle, symbol=self.symbol)

         self.pointer += 1

         if self.sleep:
             time.sleep(self.sleep)

     print("✅ CSV replay finished")
     return self.engine.snapshot()

