from core.data_loader import load_eod_data
from core.indicators import ema, rsi, atr, adx
from core.swings import detect_swings
from core.strategy_engine import StrategyEngine

# ─────────────────────────────
# CONFIG (example – tweak later)
# ─────────────────────────────
CONFIG = {
    "risk_profile": {
        "type": "risk_taker",
        "risk_per_trade_pct": 1.0,
    },
    "rrr": {
        "minimum": 1.5,
        "preferred": 2.0,
    },
    "candlestick_patterns": {
        "HAMMER": True,
        "BULLISH_ENGULFING": True,
        "MORNING_STAR": True,
        "SHOOTING_STAR": True,
        "BEARISH_ENGULFING": True,
        "EVENING_STAR": True,
    },
    "trade_limits": {
        "max_open_trades": 5,
    },
}

CAPITAL = 1_000_000  # ₹10 lakh example

# ─────────────────────────────
# LOAD & PREP DATA
# ─────────────────────────────
def prepare_df(csv_path):
    df = load_eod_data(csv_path)

    df["ema20"] = ema(df["close"], 20)
    df["ema50"] = ema(df["close"], 50)
    df["rsi"] = rsi(df["close"])
    df["atr"] = atr(df)
    df["adx"] = adx(df)
    df["volume_sma"] = df["volume"].rolling(20).mean()

    df = detect_swings(df)
    return df


market_data = {
    "TCS": prepare_df("nse-data/data/TCS.csv"),
    # Add more later:
    "INFY": prepare_df("nse-data/data/INFY.csv"),
    # "RELIANCE": prepare_df("data/RELIANCE.csv"),
}

# ─────────────────────────────
# RUN STRATEGY ENGINE
# ─────────────────────────────
engine = StrategyEngine(CONFIG)

signals = engine.run(
    market_data=market_data,
    capital=CAPITAL,
)

# ─────────────────────────────
# OUTPUT (DRY RUN RESULT)
# ─────────────────────────────
print("\nFINAL TRADE CANDIDATES (DRY RUN)\n")

if not signals:
    print("No trades selected.")
else:
    for s in signals:
        print(
            f"{s['symbol']} | {s['pattern']} | {s['direction']} | "
            f"Entry: {s['entry']} | SL: {s['stop_loss']} | "
            f"Target: {s['target']} | Qty: {s['quantity']} | "
            f"RRR: {s['rrr']} | Strength: {s['strength']}"
        )
