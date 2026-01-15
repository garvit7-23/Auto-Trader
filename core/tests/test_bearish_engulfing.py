from core.data_loader import load_eod_data
from core.indicators import ema, rsi, atr, adx
from core.swings import detect_swings
from core.patterns.bearish_engulfing import is_bearish_engulfing

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
CSV_PATH = "nse-data/data/TCS.csv"
RISK_MODE = "risk_taker"   # engulfing works best as risk_taker

# ─────────────────────────────
# LOAD & PREP DATA
# ─────────────────────────────
df = load_eod_data(CSV_PATH)

df["ema20"] = ema(df["close"], 20)
df["ema50"] = ema(df["close"], 50)
df["rsi"] = rsi(df["close"])
df["atr"] = atr(df)
df["adx"] = adx(df)
df["volume_sma"] = df["volume"].rolling(20).mean()

df = detect_swings(df)

print("\nRunning BEARISH ENGULFING pattern test...\n")

# ─────────────────────────────
# PATTERN SCAN
# ─────────────────────────────
signals = []

for idx in range(len(df)):
    signal = is_bearish_engulfing(
        df=df,
        idx=idx,
        risk_mode=RISK_MODE,
    )

    if signal:
        signals.append(signal)

        print(
            f"Date: {df.iloc[idx]['date'].date()} | "
            f"Pattern: {signal['pattern']} | "
            f"Direction: {signal['direction']} | "
            f"Entry: {signal['entry_price']} | "
            f"SL: {signal['stop_loss']} | "
            f"Strength: {signal.get('strength', 'NA')}"
        )

print(f"\nTotal BEARISH ENGULFING signals found: {len(signals)}")
