import pandas as pd

# ─────────────────────────────
# Core imports
# ─────────────────────────────
from core.data_loader import load_eod_data
from core.indicators import ema, rsi, atr, adx
from core.swings import detect_swings
from core.support_resistance import (
    get_recent_support,
    get_recent_resistance,
)

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
CSV_PATH = "nse-data/data/TCS.csv"   # change to any NIFTY100 stock
SWING_LOOKBACK = 3

# ─────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────
df = load_eod_data("nse-data/data/TCS.csv")
print(df.head())

print("\nLoaded data:")
print(df.head(3))

# ─────────────────────────────
# 2. INDICATORS
# ─────────────────────────────
df["ema20"] = ema(df["close"], 20)
df["ema50"] = ema(df["close"], 50)
df["rsi"] = rsi(df["close"])
df["atr"] = atr(df)
df["adx"] = adx(df)

# Volume average (needed by patterns later)
df["volume_sma"] = df["volume"].rolling(20).mean()

# ─────────────────────────────
# 3. SWING DETECTION (Dow structure)
# ─────────────────────────────
df = detect_swings(df, lookback=SWING_LOOKBACK)

# ─────────────────────────────
# 4. BASIC SANITY CHECK
# ─────────────────────────────
print("\nLast 10 rows with indicators:")
print(df.tail(10)[[
    "date",
    "close",
    "ema20",
    "ema50",
    "rsi",
    "atr",
    "adx",
    "swing_high",
    "swing_low"
]])

# ─────────────────────────────
# 5. SUPPORT / RESISTANCE CHECK
# ─────────────────────────────
idx = len(df) - 1

support = get_recent_support(df, idx)
resistance = get_recent_resistance(df, idx)

print("\nSupport / Resistance check:")
print("Recent Support   :", support)
print("Recent Resistance:", resistance)

# ─────────────────────────────
# 6. TREND CONTEXT CHECK
# ─────────────────────────────
last_row = df.iloc[idx]

print("\nTrend context:")
print("Close  :", last_row['close'])
print("EMA20  :", last_row['ema20'])
print("EMA50  :", last_row['ema50'])
print("Uptrend:", last_row["ema20"] > last_row["ema50"])
print("Downtrend:", last_row["ema20"] < last_row["ema50"])

# ─────────────────────────────
# 7. DATA QUALITY CHECK
# ─────────────────────────────
print("\nNaN check (should be False):")
print(df.tail(1).isna().any())

print("\n✅ CORE FOUNDATION TEST COMPLETE")
