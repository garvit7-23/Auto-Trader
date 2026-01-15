import pandas as pd
from typing import Dict, Optional

def is_hammer(
    df: pd.DataFrame,
    idx: int,
    atr_col: str = "atr",
    volume_col: str = "volume",
    volume_ma_col: str = "volume_sma",
    swing_low_col: str = "swing_low",
    ema20_col: str = "ema20",
    ema50_col: str = "ema50",
    risk_mode: str = "risk_taker",  # risk_taker | risk_averse
    config: Optional[Dict] = None
) -> Optional[Dict]:
    """
    Detects a bullish hammer at index `idx`.

    Returns:
        dict with signal details if hammer is valid
        None if not a valid hammer
    """

    if idx < 2 or idx >= len(df) - 1:
        return None

    cfg = {
        "max_body_pct": 0.30,
        "min_shadow_body_ratio": 2.0,
        "max_upper_shadow_pct": 0.25,
        "support_atr_tolerance": 0.5,
        "volume_multiplier": 1.3,
        "sl_atr_buffer": 0.0,  # optional
    }

    if config:
        cfg.update(config)

    row = df.iloc[idx]

    open_, high, low, close = row["open"], row["high"], row["low"], row["close"]

    body = abs(close - open_)
    candle_range = high - low

    if candle_range == 0:
        return None

    lower_shadow = min(open_, close) - low
    upper_shadow = high - max(open_, close)

    # ─────────────────────────────
    # 1. Prior trend check (bearish)
    # ─────────────────────────────
    if not (
        close < row[ema50_col]
        and row[ema20_col] < row[ema50_col]
    ):
        return None

    # ─────────────────────────────
    # 2. Candle structure rules
    # ─────────────────────────────
    if body / candle_range > cfg["max_body_pct"]:
        return None

    if lower_shadow < cfg["min_shadow_body_ratio"] * body:
        return None

    if upper_shadow / candle_range > cfg["max_upper_shadow_pct"]:
        return None

    # ─────────────────────────────
    # 3. Support proximity check
    # ─────────────────────────────
    recent_swing_lows = df.loc[:idx - 1].loc[df[swing_low_col]].tail(1)
    if recent_swing_lows.empty:
        return None

    swing_low_price = recent_swing_lows["low"].values[0]

    if abs(low - swing_low_price) > cfg["support_atr_tolerance"] * row[atr_col]:
        return None

    # ─────────────────────────────
    # 4. Volume confirmation
    # ─────────────────────────────
    if row[volume_col] < cfg["volume_multiplier"] * row[volume_ma_col]:
        return None

    # ─────────────────────────────
    # 5. Risk-averse confirmation
    # ─────────────────────────────
    entry_idx = idx
    entry_price = close

    if risk_mode == "risk_averse":
        next_row = df.iloc[idx + 1]
        if next_row["close"] <= next_row["open"]:
            return None
        entry_idx = idx + 1
        entry_price = next_row["close"]

    # ─────────────────────────────
    # 6. Stop-loss (textbook)
    # ─────────────────────────────
    stop_loss = low - (cfg["sl_atr_buffer"] * row[atr_col])

    return {
        "pattern": "HAMMER",
        "direction": "LONG",
        "signal_index": entry_idx,
        "entry_price": round(entry_price, 2),
        "stop_loss": round(stop_loss, 2),
        "pattern_index": idx,
        "strength": round(lower_shadow / body, 2),
    }
