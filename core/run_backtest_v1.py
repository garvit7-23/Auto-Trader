from pathlib import Path

print("🔥 run_backtest_v1 MODULE LOADED 🔥")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "nse-data" / "data"


def main():
    print("🚀 main() STARTED")

    from core.data_loader import load_eod_data
    from core.indicators import ema, rsi, atr, adx
    from core.swings import detect_swings
    from core.strategy_engine import StrategyEngine
    from core.backtester_v1 import BacktesterV1

    # ✅ CONFIG MUST BE INDENTED 4 SPACES (INSIDE main)
    CONFIG = {
        "risk_profile": {
            "type": "risk_taker",
            "risk_per_trade_pct": 1.0
        },

        # 🔧 Pattern-wise risk multiplier
        "pattern_risk": {
            "HAMMER": 1.5,
            "SHOOTING_STAR": 1.5,
            "BULLISH_ENGULFING": 0.5,
        },

        "rrr": {
            "minimum": 1.5,
            "preferred": 2.0
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
            "max_open_trades": 5
        },
    }

    def prepare_df(path):
        df = load_eod_data(path)
        df["ema20"] = ema(df["close"], 20)
        df["ema50"] = ema(df["close"], 50)
        df["rsi"] = rsi(df["close"])
        df["atr"] = atr(df)
        df["adx"] = adx(df)
        df["volume_sma"] = df["volume"].rolling(20).mean()
        return detect_swings(df)

    # ───── LOAD DATA ─────
    market_data = {}

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"DATA_DIR not found: {DATA_DIR}")

    for file in DATA_DIR.iterdir():
        if file.suffix != ".csv":
            continue

        market_data[file.stem] = prepare_df(str(file))

    print(f"📦 Loaded {len(market_data)} symbols")

    engine = StrategyEngine(CONFIG)
    backtester = BacktesterV1(initial_capital=1_000_000)

    print("▶ Calling backtester.run()")

    results = backtester.run(
        market_data=market_data,
        strategy_engine=engine,
    )

    # ───── SUMMARY ─────
    print("\n✅ BACKTEST FINISHED\n")
    print(f"Final capital: {results['final_capital']}")
    print(f"Total trades: {results['total_trades']}")
    print(f"Wins: {results['wins']} | Losses: {results['losses']}")

    # ───── PATTERN STATS ─────
    print("\n📊 PATTERN-WISE PERFORMANCE\n")

    for pattern, s in results["pattern_stats"].items():
        print(
            f"{pattern:20s} | "
            f"Trades: {s['trades']:4d} | "
            f"Wins: {s['wins']:3d} | "
            f"Losses: {s['losses']:3d} | "
            f"WinRate: {s['win_rate']:5.1f}% | "
            f"AvgPnL: {s['avg_pnl']:8.2f} | "
            f"TotalPnL: {s['total_pnl']:10.2f}"
        )


if __name__ == "__main__":
    main()
