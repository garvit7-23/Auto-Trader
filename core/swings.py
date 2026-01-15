import pandas as pd

def detect_swings(df: pd.DataFrame, lookback=3):
    df = df.copy()
    df["swing_high"] = False
    df["swing_low"] = False

    for i in range(lookback, len(df) - lookback):
        high = df.loc[i, "high"]
        low = df.loc[i, "low"]

        if high == max(df.loc[i-lookback:i+lookback, "high"]):
            df.loc[i, "swing_high"] = True

        if low == min(df.loc[i-lookback:i+lookback, "low"]):
            df.loc[i, "swing_low"] = True

    return df
