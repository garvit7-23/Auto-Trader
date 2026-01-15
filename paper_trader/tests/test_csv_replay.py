from core.strategy_engine import StrategyEngine
from paper_trader.config import CONFIG   # your strategy config
from paper_trader.engine.paper_engine import PaperTradingEngine
from paper_trader.feeds.csv_replay import CSVReplayFeed

engine = PaperTradingEngine(initial_capital=1_000_000)
engine.set_strategy(StrategyEngine(CONFIG))

feed = CSVReplayFeed(
    engine=engine,
    csv_path="nse-data/data/INFY.csv",
    symbol="INFY",
    sleep=None,  # set to 0.5 for slow motion
)

final_state = feed.run()

print("\n📊 FINAL SNAPSHOT")
print(final_state)
