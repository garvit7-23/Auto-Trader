from nselib.capital_market import price_volume_data
import pandas as pd

# Fetch data for INFY
df = price_volume_data(
    symbol="INFY",
    from_date="01-01-2018",
    to_date="01-01-2024"
)

# Select correct columns (based on actual nselib output)
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

# Rename to standard OHLCV
df.columns = ["date", "open", "high", "low", "close", "volume"]

# Parse date (e.g. 01-Jan-2018)
df["date"] = pd.to_datetime(df["date"], format="%d-%b-%Y")

# Remove commas & convert to numeric
for col in ["open", "high", "low", "close", "volume"]:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

# Sort by date
df = df.sort_values("date").reset_index(drop=True)

# Save
df.to_csv("data/INFY.csv", index=False)

print("✅ INFY.csv saved:", len(df), "rows")
