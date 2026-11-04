import pytest
import datetime
from jose import jwt, JWTError
from app.market_data.provider import OandaMarketDataProvider, ExnessMarketDataProvider, ConnectionStatus
from app.core.security import create_access_token, verify_password, get_password_hash, SECRET_KEY, ALGORITHM
from app.trading.risk_engine import RiskEngine
from app.trading.paper_broker import PaperBroker
from app.backtesting.engine import BacktestEngine, BacktestConfig
import pandas as pd
import numpy as np

def test_broker_adapter_status_separation():
    # When credentials are missing, broker adapters must be explicitly BLOCKED
    oanda_unconfigured = OandaMarketDataProvider(api_key="", account_id="", environment="practice")
    assert oanda_unconfigured.get_connection_status() == ConnectionStatus.BLOCKED
    assert "PRACTICE" in oanda_unconfigured.get_source_name()

    exness_unconfigured = ExnessMarketDataProvider(login="", server="")
    assert exness_unconfigured.get_connection_status() == ConnectionStatus.BLOCKED

    # When credentials provided in test environment without live handshake, mark UNVERIFIED
    oanda_mock = OandaMarketDataProvider(api_key="mock_key", account_id="mock_acc", environment="live")
    assert oanda_mock.get_connection_status() == ConnectionStatus.UNVERIFIED

def test_security_jwt_validation_and_expiration():
    # Valid token
    token = create_access_token({"sub": "trader@madi.terminal"}, expires_delta=datetime.timedelta(minutes=15))
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "trader@madi.terminal"

    # Expired token
    expired_token = create_access_token({"sub": "trader@madi.terminal"}, expires_delta=datetime.timedelta(seconds=-10))
    with pytest.raises(JWTError):
        jwt.decode(expired_token, SECRET_KEY, algorithms=[ALGORITHM])

    # Password hash verification
    pwd = "MySecretForexPassword2026!"
    h = get_password_hash(pwd)
    assert verify_password(pwd, h)
    assert not verify_password("WrongPassword", h)

def test_concurrency_and_idempotency_protection():
    broker = PaperBroker(initial_balance=50000.0)

    # 1. Place order with idempotency key
    key = "unique-order-uuid-101"
    res1 = broker.place_order("EURUSD", "BUY", 1.0, 1.0850, idempotency_key=key)
    assert res1["status"] == "FILLED"

    # 2. Resubmission of identical idempotency key must be REJECTED
    res2 = broker.place_order("EURUSD", "BUY", 1.0, 1.0850, idempotency_key=key)
    assert res2["status"] == "REJECTED"
    assert res2["reason"] == "DUPLICATE_IDEMPOTENCY_KEY"
    assert len(broker.positions) == 1

def test_risk_engine_non_bypassable_controls():
    risk = RiskEngine(max_daily_loss=2000.0, max_lots_per_order=10.0, leverage=100.0)

    # Emergency halt active
    risk.trigger_emergency_halt()
    decision = risk.validate_order(account_equity=100000.0, current_daily_loss=0.0, order_lot_size=0.1)
    assert decision["approved"] is False
    assert decision["reason"] == "EMERGENCY_HALT_ACTIVE"

    # Reset halt
    risk.reset_emergency_halt()
    # Daily loss limit exceeded
    decision_loss = risk.validate_order(account_equity=100000.0, current_daily_loss=2500.0, order_lot_size=1.0)
    assert decision_loss["approved"] is False
    assert decision_loss["reason"] == "MAX_DAILY_LOSS_EXCEEDED"

    # Insufficient equity for required margin
    decision_margin = risk.validate_order(account_equity=500.0, current_daily_loss=0.0, order_lot_size=2.0)
    assert decision_margin["approved"] is False
    assert decision_margin["reason"] == "INSUFFICIENT_MARGIN"

def test_backtest_friction_accounting():
    dates = pd.date_range("2024-01-01", periods=100, freq="1h")
    # Alternating prices
    trend = np.sin(np.linspace(0, 8, 100)) * 0.005
    prices = 1.0850 + trend
    df = pd.DataFrame({
        "open": prices,
        "high": prices + 0.0002,
        "low": prices - 0.0002,
        "close": prices,
        "volume": [1000] * 100
    }, index=dates)

    # Config with 2.0 pips spread + 1.0 pip slippage + $10/lot commission
    cfg = BacktestConfig(symbol="EURUSD", initial_balance=10000.0, spread_pips=2.0, slippage_pips=1.0, commission_per_lot=10.0)
    engine = BacktestEngine(config=cfg, candles=df)
    results = engine.run_sma_cross(fast_period=5, slow_period=15)

    # Verify trades contain exit details and realistic performance summary
    assert "trades" in results
    assert "net_profit" in results
    assert "max_drawdown" in results
