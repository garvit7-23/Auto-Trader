import math
from typing import Dict, List

from core.patterns.hammer import is_hammer
from core.patterns.shooting_star import is_shooting_star
from core.patterns.bullish_engulfing import is_bullish_engulfing
from core.patterns.bearish_engulfing import is_bearish_engulfing
from core.patterns.morning_star import is_morning_star
from core.patterns.evening_star import is_evening_star

def debug(msg: str):
    if DEBUG:
        print(msg)


DEBUG = True  # 🔥 TEMP: turn off later

PATTERN_FUNCTIONS = {
    "HAMMER": is_hammer,
    "SHOOTING_STAR": is_shooting_star,
    "BULLISH_ENGULFING": is_bullish_engulfing,
    "BEARISH_ENGULFING": is_bearish_engulfing,
    "MORNING_STAR": is_morning_star,
    "EVENING_STAR": is_evening_star,
}


class StrategyEngine:
    def __init__(self, config: Dict):
        self.config = config

    # ---------------- Risk & RRR ---------------- #

    def calculate_position_size(
        self,
        capital: float,
        entry: float,
        stop: float,
        risk_pct: float,
    ) -> int:
        if entry is None or stop is None:
            return 0

        if math.isnan(entry) or math.isnan(stop):
            return 0

        per_share_risk = abs(entry - stop)
        if per_share_risk <= 0 or math.isnan(per_share_risk):
            return 0

        risk_amount = capital * (risk_pct / 100)
        return int(risk_amount // per_share_risk)

    def calculate_rrr(
        self,
        entry: float,
        stop: float,
        target: float,
        direction: str,
    ) -> float:
        if direction == "LONG":
            return (target - entry) / (entry - stop)
        else:
            return (entry - target) / (stop - entry)

    # ---------------- Scanner Mode ---------------- #

    def generate_signals_for_symbol(
        self,
        symbol: str,
        df,
        capital: float,
    ) -> List[Dict]:

        signals = []

        risk_mode = self.config["risk_profile"]["type"]
        base_risk = self.config["risk_profile"]["risk_per_trade_pct"]
        pattern_risk = self.config.get("pattern_risk", {})
        min_rrr = self.config["rrr"]["minimum"]

        for idx in range(len(df)):
            for pattern_name, pattern_func in PATTERN_FUNCTIONS.items():

                if not self.config["candlestick_patterns"].get(pattern_name, True):
                    continue

                signal = pattern_func(df=df, idx=idx, risk_mode=risk_mode)
                if not signal:
                    continue

                entry = signal["entry_price"]
                stop = signal["stop_loss"]

                if entry is None or stop is None:
                    continue
                if math.isnan(entry) or math.isnan(stop):
                    continue

                r_multiple = self.config["rrr"]["preferred"]
                target = (
                    entry + r_multiple * (entry - stop)
                    if signal["direction"] == "LONG"
                    else entry - r_multiple * (stop - entry)
                )

                rrr = self.calculate_rrr(entry, stop, target, signal["direction"])
                if rrr < min_rrr:
                    continue

                risk_pct = base_risk * pattern_risk.get(
                    signal["pattern"], 1.0
                )

                qty = self.calculate_position_size(
                    capital, entry, stop, risk_pct
                )
                if qty <= 0:
                    continue

                signals.append({
                    "symbol": symbol,
                    "pattern": signal["pattern"],
                    "direction": signal["direction"],
                    "entry": round(entry, 2),
                    "stop_loss": round(stop, 2),
                    "target": round(target, 2),
                    "rrr": round(rrr, 2),
                    "quantity": qty,
                    "signal_index": signal["signal_index"],
                    "strength": signal.get("strength", 0),
                })

        return signals

    # ---------------- Backtest Mode ---------------- #

    def generate_signals_for_index(
        self,
        symbol: str,
        df,
        idx: int,
        capital: float,
    ) -> List[Dict]:

        if idx < 50:
            return []

        signals = []

        risk_mode = self.config["risk_profile"]["type"]
        base_risk = self.config["risk_profile"]["risk_per_trade_pct"]
        pattern_risk = self.config.get("pattern_risk", {})
        min_rrr = self.config["rrr"]["minimum"]

        for pattern_name, pattern_func in PATTERN_FUNCTIONS.items():

            if not self.config["candlestick_patterns"].get(pattern_name, True):
                continue

            signal = pattern_func(df=df, idx=idx, risk_mode=risk_mode)
            if not signal:
               debug(f"[{symbol}] idx={idx} | {pattern_name} ❌ no pattern")
               continue


            entry = signal["entry_price"]
            stop = signal["stop_loss"]

            if entry is None or stop is None:
                continue
            if math.isnan(entry) or math.isnan(stop):
                continue

            r_multiple = self.config["rrr"]["preferred"]
            target = (
                entry + r_multiple * (entry - stop)
                if signal["direction"] == "LONG"
                else entry - r_multiple * (stop - entry)
            )

            rrr = self.calculate_rrr(entry, stop, target, signal["direction"])
            if rrr < min_rrr:
                debug(
                f"[{symbol}] idx={idx} | {pattern_name} ❌ RRR {rrr:.2f} < {min_rrr}"
                )
                continue

            risk_pct = base_risk * pattern_risk.get(
                signal["pattern"], 1.0
            )

            qty = self.calculate_position_size(
                capital, entry, stop, risk_pct
            )
            if qty <= 0:
             debug(
             f"[{symbol}] idx={idx} | {pattern_name} ❌ qty=0 "
             f"(entry={entry}, stop={stop}, risk={risk_pct})"
             )
             continue
            
            debug(
             f"[{symbol}] idx={idx} | {pattern_name} ✅ SIGNAL "
             f"RRR={rrr:.2f} qty={qty}"
              )

            signals.append({
                "symbol": symbol,
                "pattern": signal["pattern"],
                "direction": signal["direction"],
                "entry": round(entry, 2),
                "stop_loss": round(stop, 2),
                "target": round(target, 2),
                "rrr": round(rrr, 2),
                "quantity": qty,
                "signal_index": idx,
                "strength": signal.get("strength", 0),
            })

        return signals
