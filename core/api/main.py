# core/api/main.py
from fastapi import FastAPI
import pandas as pd

from core.api.schemas import SignalRequest, SignalResponse
from core.api.deps import engine
from core.indicators import ema, rsi, atr, adx
from core.swings import detect_swings

app = FastAPI(
    title="Strategy Engine API",
    version="1.0.0",
)


def prepare_df_from_api(candles):
    df = pd.DataFrame([c.dict() for c in candles])

    df["ema20"] = ema(df["close"], 20)
    df["ema50"] = ema(df["close"], 50)
    df["rsi"] = rsi(df["close"])
    df["atr"] = atr(df)
    df["adx"] = adx(df)
    df["volume_sma"] = df["volume"].rolling(20).mean()

    return detect_swings(df)


@app.post("/signals", response_model=SignalResponse)
def generate_signals(payload: SignalRequest):
    df = prepare_df_from_api(payload.candles)

    signals = engine.generate_signals_for_symbol(
        symbol=payload.symbol,
        df=df,
        capital=payload.capital,
    )

    return {
        "symbol": payload.symbol,
        "signals": signals,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
