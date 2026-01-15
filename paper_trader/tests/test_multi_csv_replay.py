# paper_trader/tests/test_multi_csv_replay.py

from paper_trader.engine.paper_engine import PaperTradingEngine
from paper_trader.feeds.multi_csv_replay import MultiCSVReplayFeed
from core.strategy_engine import StrategyEngine
from paper_trader.config import CONFIG


def run_test():
    print("🚀 Initializing engine")

    engine = PaperTradingEngine(initial_capital=1_000_000)

    strategy = StrategyEngine(CONFIG)
    engine.set_strategy(strategy)

    feed = MultiCSVReplayFeed(
        engine=engine,
        data_dir="nse-data/data",  # 🔥 YOUR 80 CSVs FOLDER
    )

    final_state = feed.run()

    print("\n📊 FINAL SNAPSHOT")
    print(final_state)


if __name__ == "__main__":
    run_test()
