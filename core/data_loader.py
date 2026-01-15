from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent


def load_eod_data(csv_path: str) -> pd.DataFrame:
    """
    Loads EOD OHLCV data from CSV and performs basic sanitation.
    Expected columns:
    date, open, high, low, close, volume
    """

    csv_path = PROJECT_ROOT / csv_path

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    required_cols = {"date", "open", "high", "low", "close", "volume"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV missing required columns. Found: {df.columns}")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    numeric_cols = ["open", "high", "low", "close", "volume"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    df.dropna(subset=numeric_cols, inplace=True)

    df = df[
        (df["high"] >= df[["open", "close"]].max(axis=1)) &
        (df["low"] <= df[["open", "close"]].min(axis=1)) &
        (df["volume"] > 0)
    ]

    return df.reset_index(drop=True)
