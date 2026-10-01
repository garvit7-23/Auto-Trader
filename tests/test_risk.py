from autotrader.domain import Signal, Side
from autotrader.risk import RiskConfig, RiskManager


def test_position_size_is_bounded_by_risk_and_notional():
    risk = RiskManager(RiskConfig(risk_per_trade=0.01, max_position_notional_pct=0.25))
    signal = Signal("TEST", Side.LONG, stop_loss=95, target=110, strategy="test")
    decision = risk.evaluate(signal, equity=100_000, open_positions=0, current_price=100)
    assert decision.approved
    assert decision.quantity == 200


def test_max_open_positions_is_enforced():
    risk = RiskManager(RiskConfig(max_open_positions=2))
    signal = Signal("TEST", Side.LONG, stop_loss=95, strategy="test")
    decision = risk.evaluate(signal, equity=100_000, open_positions=2, current_price=100)
    assert not decision.approved
    assert decision.reason == "max_open_positions"
