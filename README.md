# Auto Trader – Event-Driven Paper Trading Engine

A realistic, event-driven **paper trading and backtesting system** designed to simulate live trading behavior using historical market data.

## Features

- Candle-by-candle CSV replay (live-like simulation)
- Single-symbol and multi-symbol portfolio trading
- Candlestick pattern strategy engine
- Risk-based position sizing
- Stop-loss and target-based execution
- Portfolio-level capital management
- Backtest vs replay consistency

## Architecture
```
AUTO_TRADER/
├── core/ # Strategy & analytics layer
│ ├── patterns/ # Candlestick pattern detection
│ ├── indicators.py
│ ├── swings.py
│ ├── strategy_engine.py
│ └── backtester.py
│
├── paper_trader/ # Execution & simulation engine
│ ├── engine/
│ │ ├── paper_engine.py
│ │ ├── execution.py
│ │ ├── portfolio.py
│ │ └── position.py
│ ├── feeds/
│ │ ├── csv_replay.py
│ │ └── multi_csv_replay.py
│ ├── api/ # Optional REST interface
│ └── tests/
│
├── README.md
├── pyproject.toml
└── pyproject.lock
```

## Execution Modes

### Single Symbol Replay
```bash
python -m paper_trader.tests.test_csv_replay
```
Multi Symbol Replay
```
python -m paper_trader.tests.test_multi_csv_replay
```