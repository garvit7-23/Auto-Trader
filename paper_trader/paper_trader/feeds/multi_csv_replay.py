# paper_trader/feeds/multi_csv_replay.py

import os
import pandas as pd
from typing import Dict

from core.strategy_engine import StrategyEngine
from paper_trader.config import CONFIG
from paper_trader.engine.paper_engine import PaperTradingEngine


class MultiCSVReplayFeed:
    """
    Replays multiple CSV files candle-by-candle
    into the PaperTradingEngine (portfolio-level simulation).
    """

    def __init__(
        self,
        engine: PaperTradingEngine,
        data_dir: str,
    ):
        self.engine = engine
        self.data_dir = data_dir
        self.data: Dict[str, pd.DataFrame] = {}
        self.max_bars = 0

        # ✅ CREATE STRATEGY ENGINE ONCE
        self.strategy_engine = StrategyEngine(CONFIG)

    # ─────────────────────────────
    # LOAD ALL CSVs
    # ─────────────────────────────

    def load(self):
        for file in os.listdir(self.data_dir):
            if not file.endswith(".csv"):
                continue

            symbol = file.replace(".csv", "")
            path = os.path.join(self.data_dir, file)

            df = pd.read_csv(path)

            required = {"date", "open", "high", "low", "close", "volume"}
            if not required.issubset(df.columns):
                continue

            df = df.sort_values("date").reset_index(drop=True)
            self.data[symbol] = df

        if not self.data:
            raise RuntimeError("No valid CSVs found")

        # Align all symbols to shortest history
        self.max_bars = min(len(df) for df in self.data.values())

        # Preload empty market data into engine
        self.engine.load_market_data({
            symbol: df.iloc[:0]
            for symbol, df in self.data.items()
        })

    # ─────────────────────────────
    # REPLAY LOOP
    # ─────────────────────────────

    def run(self):
        if not self.data:
            self.load()

        print(f"▶ Starting MULTI-SYMBOL replay ({len(self.data)} symbols)")

        # ✅ INJECT STRATEGY ENGINE
        self.engine.set_strategy(self.strategy_engine)

        self.engine.start()

        for idx in range(self.max_bars):
            for symbol, df in self.data.items():
                candle = df.iloc[idx].to_dict()
                self.engine.on_tick(candle, symbol=symbol)

        print("✅ Multi-symbol CSV replay finished")
        return self.engine.snapshot()
