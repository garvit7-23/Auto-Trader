from datetime import datetime
import pandas as pd

from paper_trader.engine.paper_engine import PaperTradingEngine
from core.strategy_engine import StrategyEngine
from paper_trader.config import CONFIG



# ---- Fake candle generator ----
def candle(ts, o, h, l, c, v=1000, symbol="TEST"):
    return {
        "symbol": symbol,
        "timestamp": ts,
        "open": o,
        "high": h,
        "low": l,
        "close": c,
        "volume": v,
    }


def run_test():
    SYMBOL = "TEST"

    # 1️⃣ Create engine
    engine = PaperTradingEngine(initial_capital=1_000_000)

    # 2️⃣ Inject strategy
    strategy = StrategyEngine(CONFIG)
    engine.set_strategy(strategy)

    # 3️⃣ Load EMPTY market data with symbol
    empty_df = pd.DataFrame(
        columns=["timestamp", "open", "high", "low", "close", "volume"]
    )

    engine.load_market_data({
        SYMBOL: empty_df
    })

    # 4️⃣ Start engine
    engine.start()

    print("✅ Engine initialized")
    print("Capital:", engine.portfolio.cash)

    # ---- Feed candles ----
    candles = [
        candle("2024-01-01", 100, 105, 95, 102),
        candle("2024-01-02", 102, 108, 101, 107),
        candle("2024-01-03", 107, 110, 104, 109),
        candle("2024-01-04", 109, 112, 108, 111),
    ]

    for i, c in enumerate(candles):
        print(f"\n🕯️ Tick {i + 1}")
        result = engine.on_tick(c)
        print(result)
        print(engine.portfolio.snapshot())


if __name__ == "__main__":
    run_test()
