import pandas as pd
from typing import Dict, Optional

def is_bearish_engulfing(
    df: pd.DataFrame,
    idx: int,
    ema20_col: str = "ema20",
    ema50_col: str = "ema50",
    atr_col: str = "atr",
    volume_col: str = "volume",
    volume_ma_col: str = "volume_sma",
    risk_mode: str = "risk_taker",  # risk_taker | risk_averse
    config: Optional[Dict] = None
) -> Optional[Dict]:
    """
    Detects a Bearish Engulfing pattern ending at index `idx` (P2).
    """

    if idx < 1 or idx >= len(df) - 1:
        return None

    cfg = {
        "volume_multiplier": 1.3,
        "body_strength_ratio": 1.1,
        "sl_atr_buffer": 0.0
    }

    if config:
        cfg.update(config)

    p1 = df.iloc[idx - 1]
    p2 = df.iloc[idx]

    # ─────────────────────────────
    # 1. Prior trend check (bullish)
    # ─────────────────────────────
    if not (
        p2["close"] > p2[ema50_col]
        and p2[ema20_col] > p2[ema50_col]
    ):
        return None

    # ─────────────────────────────
    # 2. Candle colour rules
    # ─────────────────────────────
    if not (p1["close"] > p1["open"]):
        return None

    if not (p2["close"] < p2["open"]):
        return None

    # ─────────────────────────────
    # 3. Real body engulfing
    # ─────────────────────────────
    if not (
        p2["open"] >= p1["close"]
        and p2["close"] <= p1["open"]
    ):
        return None

    # ─────────────────────────────
    # 4. Strength filter
    # ─────────────────────────────
    p1_body = abs(p1["close"] - p1["open"])
    p2_body = abs(p2["close"] - p2["open"])

    if p2_body < cfg["body_strength_ratio"] * p1_body:
        return None

    # ─────────────────────────────
    # 5. Volume confirmation (P2)
    # ─────────────────────────────
    if p2[volume_col] < cfg["volume_multiplier"] * p2[volume_ma_col]:
        return None

    # ─────────────────────────────
    # 6. Entry logic
    # ─────────────────────────────
    entry_idx = idx
    entry_price = p2["close"]

    if risk_mode == "risk_averse":
        next_row = df.iloc[idx + 1]
        if next_row["close"] >= next_row["open"]:
            return None
        entry_idx = idx + 1
        entry_price = next_row["close"]

    # ─────────────────────────────
    # 7. Stop loss
    # ─────────────────────────────
    stop_loss = max(p1["high"], p2["high"]) + (
        cfg["sl_atr_buffer"] * p2[atr_col]
    )

    return {
        "pattern": "BEARISH_ENGULFING",
        "direction": "SHORT",
        "pattern_index": idx,
        "signal_index": entry_idx,
        "entry_price": round(entry_price, 2),
        "stop_loss": round(stop_loss, 2),
        "strength": round(p2_body / p1_body, 2)
    }
