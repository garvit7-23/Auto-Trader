import pandas as pd
from typing import Optional, Tuple


def get_recent_support(
    df: pd.DataFrame,
    idx: int,
    lookback: int = 20,
) -> Optional[float]:
    """
    Returns the most recent swing low price before idx.
    """
    if idx <= 0:
        return None

    window = df.iloc[max(0, idx - lookback):idx]
    swing_lows = window[window["swing_low"]]

    if swing_lows.empty:
        return None

    return swing_lows.iloc[-1]["low"]


def get_recent_resistance(
    df: pd.DataFrame,
    idx: int,
    lookback: int = 20,
) -> Optional[float]:
    """
    Returns the most recent swing high price before idx.
    """
    if idx <= 0:
        return None

    window = df.iloc[max(0, idx - lookback):idx]
    swing_highs = window[window["swing_high"]]

    if swing_highs.empty:
        return None

    return swing_highs.iloc[-1]["high"]


def is_near_support(
    price: float,
    support: float,
    atr: float,
    atr_multiplier: float = 0.5,
) -> bool:
    """
    Checks if price is near support within ATR tolerance.
    """
    if support is None or atr is None:
        return False

    return abs(price - support) <= atr_multiplier * atr


def is_near_resistance(
    price: float,
    resistance: float,
    atr: float,
    atr_multiplier: float = 0.5,
) -> bool:
    """
    Checks if price is near resistance within ATR tolerance.
    """
    if resistance is None or atr is None:
        return False

    return abs(price - resistance) <= atr_multiplier * atr


def get_sr_levels(
    df: pd.DataFrame,
    idx: int,
    atr_multiplier: float = 0.5,
    lookback: int = 20,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Convenience function to return both support and resistance.
    """
    support = get_recent_support(df, idx, lookback)
    resistance = get_recent_resistance(df, idx, lookback)
    return support, resistance
