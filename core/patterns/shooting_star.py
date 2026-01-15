import pandas as pd
from typing import Dict, Optional

def is_shooting_star(
    df: pd.DataFrame,
    idx: int,
    ema20_col: str = "ema20",
    ema50_col: str = "ema50",
    atr_col: str = "atr",
    volume_col: str = "volume",
    volume_ma_col: str = "volume_sma",
    swing_high_col: str = "swing_high",
    risk_mode: str = "risk_taker",  # risk_taker | risk_averse
    config: Optional[Dict] = None
) -> Optional[Dict]:
    """
    Detects a Shooting Star pattern at index `idx`.
    """

    if idx < 2 or idx >= len(df) - 1:
        return None

    cfg = {
        "max_body_pct": 0.30,
        "min_shadow_body_ratio": 2.0,
        "max_lower_shadow_pct": 0.25,
        "resistance_atr_tolerance": 0.5,
        "volume_multiplier": 1.3,
        "close_near_low_pct": 0.20,
        "sl_atr_buffer": 0.0,
    }

    if config:
        cfg.update(config)

    row = df.iloc[idx]

    open_, high, low, close = row["open"], row["high"], row["low"], row["close"]

    body = abs(close - open_)
    candle_range = high - low

    if candle_range == 0:
        return None

    upper_shadow = high - max(open_, close)
    lower_shadow = min(open_, close) - low

    # ─────────────────────────────
    # 1. Prior trend check (bullish)
    # ─────────────────────────────
    if not (
        close > row[ema50_col]
        and row[ema20_col] > row[ema50_col]
    ):
        return None

    # ─────────────────────────────
    # 2. Candle structure rules
    # ─────────────────────────────
    if body / candle_range > cfg["max_body_pct"]:
        return None

    if upper_shadow < cfg["min_shadow_body_ratio"] * body:
        return None

    if lower_shadow / candle_range > cfg["max_lower_shadow_pct"]:
        return None

    # ─────────────────────────────
    # 3. Resistance proximity check
    # ─────────────────────────────
    recent_swing_highs = df.loc[:idx - 1].loc[df[swing_high_col]].tail(1)
    if recent_swing_highs.empty:
        return None

    swing_high_price = recent_swing_highs["high"].values[0]

    if abs(high - swing_high_price) > cfg["resistance_atr_tolerance"] * row[atr_col]:
        return None

    # ─────────────────────────────
    # 4. Volume confirmation
    # ─────────────────────────────
    if row[volume_col] < cfg["volume_multiplier"] * row[volume_ma_col]:
        return None

    # ─────────────────────────────
    # 5. Entry logic
    # ─────────────────────────────
    entry_idx = idx
    entry_price = close

    if risk_mode == "risk_taker":
        if close > low + cfg["close_near_low_pct"] * candle_range:
            return None

    if risk_mode == "risk_averse":
        next_row = df.iloc[idx + 1]
        if next_row["close"] >= next_row["open"]:
            return None
        entry_idx = idx + 1
        entry_price = next_row["close"]

    # ─────────────────────────────
    # 6. Stop loss
    # ─────────────────────────────
    stop_loss = high + (cfg["sl_atr_buffer"] * row[atr_col])

    return {
        "pattern": "SHOOTING_STAR",
        "direction": "SHORT",
        "pattern_index": idx,
        "signal_index": entry_idx,
        "entry_price": round(entry_price, 2),
        "stop_loss": round(stop_loss, 2),
        "strength": round(upper_shadow / body, 2)
    }
