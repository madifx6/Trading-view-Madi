import pytest
import pandas as pd
import numpy as np
from app.trading.risk_engine import RiskEngine
from app.trading.paper_broker import PaperBroker
from app.backtesting.engine import BacktestEngine, BacktestConfig

def test_risk_engine_rules():
    risk = RiskEngine(max_daily_loss=1000.0, max_drawdown=2000.0, max_lots_per_order=10.0, leverage=100.0)

    # 1. Normal order passes
    res = risk.validate_order(account_equity=50000.0, current_daily_loss=100.0, order_lot_size=1.0)
    assert res["approved"] is True
    assert res["required_margin"] == 1000.0

    # 2. Daily loss exceeded
    res_loss = risk.validate_order(account_equity=50000.0, current_daily_loss=1200.0, order_lot_size=1.0)
    assert res_loss["approved"] is False
    assert res_loss["reason"] == "MAX_DAILY_LOSS_EXCEEDED"

    # 3. Lot size limit exceeded
    res_lots = risk.validate_order(account_equity=50000.0, current_daily_loss=0.0, order_lot_size=15.0)
    assert res_lots["approved"] is False

    # 4. Emergency halt
    risk.trigger_emergency_halt()
    assert risk.is_emergency_halted() is True
    res_halt = risk.validate_order(account_equity=50000.0, current_daily_loss=0.0, order_lot_size=0.1)
    assert res_halt["approved"] is False
    assert res_halt["reason"] == "EMERGENCY_HALT_ACTIVE"

def test_paper_broker_execution_and_idempotency():
    broker = PaperBroker(initial_balance=10000.0, leverage=100.0)

    order1 = broker.place_order("EURUSD", "BUY", 1.0, 1.0850, idempotency_key="key-001")
    assert order1["status"] == "FILLED"
    assert len(broker.positions) == 1
    assert broker.margin_used == 1000.0

    order_dup = broker.place_order("EURUSD", "BUY", 1.0, 1.0850, idempotency_key="key-001")
    assert order_dup["status"] == "REJECTED"
    assert order_dup["reason"] == "DUPLICATE_IDEMPOTENCY_KEY"

    pos_id = order1["position_id"]
    close_res = broker.close_position(pos_id, current_price=1.0870)
    assert close_res["status"] == "CLOSED"
    assert len(broker.positions) == 0
    assert broker.margin_used == 0.0
    assert broker.balance > 10000.0

def test_backtest_engine_simulation():
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=120, freq="1h")
    trend = np.sin(np.linspace(0, 10, 120)) * 0.01
    prices = 1.0850 + trend
    df = pd.DataFrame({
        "open": prices,
        "high": prices + 0.0005,
        "low": prices - 0.0005,
        "close": prices,
        "volume": [1500] * 120
    }, index=dates)

    cfg = BacktestConfig(symbol="EURUSD", initial_balance=10000.0)
    engine = BacktestEngine(config=cfg, candles=df)
    results = engine.run_sma_cross(fast_period=5, slow_period=15)

    assert "total_trades" in results
    assert "win_rate" in results
    assert "profit_factor" in results
    assert len(results["equity_curve"]) > 0
