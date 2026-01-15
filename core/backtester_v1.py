from collections import defaultdict


class BacktesterV1:
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.open_trades = {}
        self.closed_trades = []
        self.equity_curve = []

    def enter_trade(self, signal, date):
        self.open_trades[signal["symbol"]] = {
            **signal,
            "entry_date": date,
        }

    def exit_trade(self, symbol, price, date, reason):
        trade = self.open_trades.pop(symbol)

        pnl = (
            (price - trade["entry"]) * trade["quantity"]
            if trade["direction"] == "LONG"
            else (trade["entry"] - price) * trade["quantity"]
        )

        self.capital += pnl

        trade.update({
            "exit_price": price,
            "exit_date": date,
            "exit_reason": reason,
            "pnl": round(pnl, 2),
        })

        self.closed_trades.append(trade)

    def run(self, market_data: dict, strategy_engine):
        base_symbol = next(iter(market_data))
        dates = market_data[base_symbol]["date"].reset_index(drop=True)

        print("🚀 Backtest started")
        print(f"Bars: {len(dates)}")

        for i in range(len(dates)):
            current_date = dates.iloc[i]

            # ───── EXIT LOGIC ─────
            for symbol in list(self.open_trades.keys()):
                df = market_data[symbol]
                if i >= len(df):
                    continue

                row = df.iloc[i]
                trade = self.open_trades[symbol]
                high, low = row["high"], row["low"]

                if trade["direction"] == "LONG":
                    if low <= trade["stop_loss"]:
                        self.exit_trade(symbol, trade["stop_loss"], current_date, "STOP")
                    elif high >= trade["target"]:
                        self.exit_trade(symbol, trade["target"], current_date, "TARGET")
                else:
                    if high >= trade["stop_loss"]:
                        self.exit_trade(symbol, trade["stop_loss"], current_date, "STOP")
                    elif low <= trade["target"]:
                        self.exit_trade(symbol, trade["target"], current_date, "TARGET")

            # ───── ENTRY LOGIC ─────
            for symbol, df in market_data.items():
                if symbol in self.open_trades or i >= len(df):
                    continue

                signals = strategy_engine.generate_signals_for_index(
                    symbol=symbol,
                    df=df,
                    idx=i,
                    capital=self.capital,
                )

                for signal in signals:
                    self.enter_trade(signal, current_date)

            self.equity_curve.append(self.capital)

        print("✅ Backtest completed")

        return self._results()

    # ─────────────────────────────────────────────
    # RESULTS + PATTERN STATS
    # ─────────────────────────────────────────────
    def _results(self):
        pattern_stats = defaultdict(lambda: {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "total_pnl": 0.0,
        })

        for t in self.closed_trades:
            p = t["pattern"]
            pattern_stats[p]["trades"] += 1
            pattern_stats[p]["total_pnl"] += t["pnl"]

            if t["pnl"] > 0:
                pattern_stats[p]["wins"] += 1
            else:
                pattern_stats[p]["losses"] += 1

        for p, s in pattern_stats.items():
            s["win_rate"] = (s["wins"] / s["trades"]) * 100 if s["trades"] else 0
            s["avg_pnl"] = s["total_pnl"] / s["trades"] if s["trades"] else 0

        return {
            "final_capital": round(self.capital, 2),
            "total_trades": len(self.closed_trades),
            "wins": sum(1 for t in self.closed_trades if t["pnl"] > 0),
            "losses": sum(1 for t in self.closed_trades if t["pnl"] <= 0),
            "trades": self.closed_trades,
            "pattern_stats": dict(pattern_stats),
        }
