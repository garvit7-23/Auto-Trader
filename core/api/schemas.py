# core/api/schemas.py
from typing import List, Dict
from pydantic import BaseModel


class Candle(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class SignalRequest(BaseModel):
    symbol: str
    candles: List[Candle]
    capital: float


class SignalResponse(BaseModel):
    symbol: str
    signals: List[Dict]
