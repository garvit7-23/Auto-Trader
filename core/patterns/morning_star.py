import pandas as pd
from typing import Dict, Optional


def is_morning_star(
    df: pd.DataFrame,
    idx: int,
    ema20_col: str = "ema20",
    ema50_col: str = "ema50",
    atr_col: str = "atr",
    volume_col: str = "volume",
    volume_ma_col: str = "volume_sma",
    risk_mode: str = "risk_taker",
    config: Optional[Dict] = None,
) -> Optional[Dict]:

    if idx < 2:
        return None

    # ─────────────────────────────
    # 1. Trend filter (LIGHT)
    # ─────────────────────────────
    if df.iloc[idx][ema20_col] < df.iloc[idx][ema50_col]:
        return None

    cfg = {
        "max_indecision_body_pct": 0.25,
        "volume_multiplier": 1.3,
        "sl_atr_buffer": 0.0,
    }

    if config:
        cfg.update(config)

    p1 = df.iloc[idx - 2]
    p2 = df.iloc[idx - 1]
    p3 = df.iloc[idx]

    # ─────────────────────────────
    # 2. P1 strong bearish candle
    # ─────────────────────────────
    if p1["close"] >= p1["open"]:
        return None

    p1_body = abs(p1["close"] - p1["open"])

    # ─────────────────────────────
    # 3. P2 indecision candle
    # ─────────────────────────────
    p2_body = abs(p2["close"] - p2["open"])
    p2_range = p2["high"] - p2["low"]

    if p2_range == 0:
        return None

    if p2_body / p2_range > cfg["max_indecision_body_pct"]:
        return None

    if p2["open"] > p1["close"]:
        return None

    # ─────────────────────────────
    # 4. P3 strong bullish candle
    # ─────────────────────────────
    if p3["close"] <= p3["open"]:
        return None

    if p3["open"] < p2["close"]:
        return None

    if p3["close"] <= p1["open"]:
        return None

    # ─────────────────────────────
    # 5. Volume confirmation
    # ─────────────────────────────
    if p3[volume_col] < cfg["volume_multiplier"] * p3[volume_ma_col]:
        return None

    # ─────────────────────────────
    # 6. Stop loss
    # ─────────────────────────────
    stop_loss = min(p1["low"], p2["low"], p3["low"]) - (
        cfg["sl_atr_buffer"] * p3[atr_col]
    )

    return {
        "pattern": "MORNING_STAR",
        "direction": "LONG",
        "pattern_index": idx,
        "signal_index": idx,
        "entry_price": round(p3["close"], 2),
        "stop_loss": round(stop_loss, 2),
        "strength": round(p1_body / max(p2_body, 0.01), 2),
    }
