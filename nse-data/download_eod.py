from nselib.capital_market import price_volume_data
import pandas as pd
import time
import os

# ---------------- CONFIG ----------------
FROM_DATE = "01-01-2018"
TO_DATE = "01-01-2024"
DATA_DIR = "nse-data/data"
SLEEP_SECONDS = 2
# ----------------------------------------

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# NIFTY 100 symbols (EQ only)
NIFTY_100 = [
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
    "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BPCL", "BHARTIARTL",
    "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY",
    "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE",
    "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "ITC",
    "INDUSINDBK", "INFY", "JSWSTEEL", "KOTAKBANK", "LT",
    "LTIM", "M&M", "MARUTI", "NESTLEIND", "NTPC",
    "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SBIN",
    "SUNPHARMA", "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TCS",
    "TECHM", "TITAN", "ULTRACEMCO", "UPL", "WIPRO",
    "ADANIGREEN", "ADANIPOWER", "AMBUJACEM", "ATGL", "BANKBARODA",
    "BOSCHLTD", "CANBK", "CHOLAFIN", "DLF", "GAIL",
    "GODREJCP", "HAVELLS", "ICICIGI", "ICICIPRULI", "INDIGO",
    "IOC", "IRCTC", "LUPIN", "NAUKRI", "NMDC",
    "PIDILITIND", "PNB", "SHREECEM", "SIEMENS", "SRF",
    "TORNTPHARM", "TRENT", "TVSMOTOR", "VEDL", "ZOMATO"
]

def download_symbol(symbol: str):
    print(f"⬇️  Downloading {symbol}...")

    df = price_volume_data(
        symbol=symbol,
        from_date=FROM_DATE,
        to_date=TO_DATE
    )

    # Select required columns
    df = df[
        [
            "Date",
            "OpenPrice",
            "HighPrice",
            "LowPrice",
            "ClosePrice",
            "TotalTradedQuantity",
        ]
    ]

    df.columns = ["date", "open", "high", "low", "close", "volume"]

    # Parse date
    df["date"] = pd.to_datetime(df["date"], format="%d-%b-%Y")

    # Convert numerics
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .astype(float)
        )

    df = df.sort_values("date").reset_index(drop=True)

    out_path = f"{DATA_DIR}/{symbol}.csv"
    df.to_csv(out_path, index=False)

    print(f"✅ Saved {symbol}: {len(df)} rows")


def main():
    failed = []

    for symbol in NIFTY_100:
        try:
            download_symbol(symbol)
            time.sleep(SLEEP_SECONDS)
        except Exception as e:
            print(f"❌ Failed {symbol}: {e}")
            failed.append(symbol)
            time.sleep(SLEEP_SECONDS)

    print("\n===== SUMMARY =====")
    print("Failed symbols:", failed)


if __name__ == "__main__":
    main()
