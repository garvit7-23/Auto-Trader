import pandas as pd
from typing import Dict, Optional


def is_bullish_engulfing(
    df: pd.DataFrame,
    idx: int,
    ema20_col: str = "ema20",
    ema50_col: str = "ema50",
    rsi_col: str = "rsi",
    atr_col: str = "atr",
    volume_col: str = "volume",
    volume_ma_col: str = "volume_sma",
    risk_mode: str = "risk_taker",  # risk_taker | risk_averse
    config: Optional[Dict] = None,
) -> Optional[Dict]:
    """
    Detects a Bullish Engulfing pattern ending at index `idx`.
    """

    if idx < 1 or idx >= len(df) - 1:
        return None

    # ─────────────────────────────
    # 🔒 TREND & MOMENTUM FILTERS
    # ─────────────────────────────
    if df.iloc[idx][ema20_col] <= df.iloc[idx][ema50_col]:
        return None

    if df.iloc[idx][rsi_col] <= 50:
        return None

    cfg = {
        "volume_multiplier": 1.3,
        "body_strength_ratio": 1.1,
        "sl_atr_buffer": 0.0,
    }

    if config:
        cfg.update(config)

    p1 = df.iloc[idx - 1]
    p2 = df.iloc[idx]

    # ─────────────────────────────
    # Candle colour rules
    # ─────────────────────────────
    if p1["close"] >= p1["open"]:
        return None

    if p2["close"] <= p2["open"]:
        return None

    # ─────────────────────────────
    # Real body engulfing
    # ─────────────────────────────
    if not (
        p2["open"] <= p1["close"]
        and p2["close"] >= p1["open"]
    ):
        return None

    # ─────────────────────────────
    # Strength filter
    # ─────────────────────────────
    p1_body = abs(p1["close"] - p1["open"])
    p2_body = abs(p2["close"] - p2["open"])

    if p2_body < cfg["body_strength_ratio"] * p1_body:
        return None

    # ─────────────────────────────
    # Volume confirmation
    # ─────────────────────────────
    if p2[volume_col] < cfg["volume_multiplier"] * p2[volume_ma_col]:
        return None

    # ─────────────────────────────
    # Entry logic
    # ─────────────────────────────
    entry_idx = idx
    entry_price = p2["close"]

    if risk_mode == "risk_averse":
        next_row = df.iloc[idx + 1]
        if next_row["close"] <= next_row["open"]:
            return None
        entry_idx = idx + 1
        entry_price = next_row["close"]

    # ─────────────────────────────
    # Stop loss
    # ─────────────────────────────
    stop_loss = min(p1["low"], p2["low"]) - (
        cfg["sl_atr_buffer"] * p2[atr_col]
    )

    return {
        "pattern": "BULLISH_ENGULFING",
        "direction": "LONG",
        "pattern_index": idx,
        "signal_index": entry_idx,
        "entry_price": round(entry_price, 2),
        "stop_loss": round(stop_loss, 2),
        "strength": round(p2_body / max(p1_body, 0.01), 2),
    }
