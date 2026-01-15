# core/api/deps.py
from core.strategy_engine import StrategyEngine

CONFIG = {
    "risk_profile": {
        "type": "risk_taker",
        "risk_per_trade_pct": 1.0,
    },
    "pattern_risk": {
        "HAMMER": 1.5,
        "SHOOTING_STAR": 1.5,
        "BULLISH_ENGULFING": 0.5,
    },
    "rrr": {
        "minimum": 1.5,
        "preferred": 2.0,
    },
    "candlestick_patterns": {
        "HAMMER": True,
        "BULLISH_ENGULFING": True,
        "MORNING_STAR": False,
        "SHOOTING_STAR": True,
        "BEARISH_ENGULFING": False,
        "EVENING_STAR": False,
    },
    "trade_limits": {
        "max_open_trades": 5,
    },
}

engine = StrategyEngine(CONFIG)
