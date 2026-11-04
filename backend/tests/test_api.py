from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "emergency_halt" in data

def test_instruments_endpoint():
    response = client.get("/api/instruments")
    assert response.status_code == 200
    instruments = response.json()
    assert len(instruments) >= 12
    symbols = [i["symbol"] for i in instruments]
    assert "EURUSD" in symbols
    assert "USDJPY" in symbols

def test_candles_endpoint():
    response = client.get("/api/candles?symbol=EURUSD&timeframe=1m&count=50")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "EURUSD"
    assert len(data["candles"]) == 50
    assert "source" in data

def test_ai_analysis_endpoint():
    response = client.get("/api/ai/analysis?symbol=EURUSD&timeframe=1h")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "EURUSD"
    assert data["validation_status"] == "VALIDATED"
    assert "supporting_evidence" in data

def test_paper_trading_endpoints():
    res_acc = client.get("/api/paper/account")
    assert res_acc.status_code == 200
    acc_data = res_acc.json()
    assert acc_data["balance"] >= 10000.0

    res_order = client.post("/api/paper/order", json={
        "symbol": "EURUSD",
        "side": "BUY",
        "lots": 1.0,
        "price": 1.0850,
        "idempotency_key": "api-test-01"
    })
    assert res_order.status_code == 200
    order_data = res_order.json()
    assert order_data["status"] == "FILLED"
    pos_id = order_data["position_id"]

    res_close = client.post("/api/paper/close", json={
        "position_id": pos_id,
        "price": 1.0865
    })
    assert res_close.status_code == 200
    assert res_close.json()["status"] == "CLOSED"

def test_backtest_run_endpoint():
    response = client.post("/api/backtest/run", json={
        "symbol": "EURUSD",
        "fast_period": 5,
        "slow_period": 15,
        "initial_balance": 10000.0
    })
    assert response.status_code == 200
    data = response.json()
    assert "net_profit" in data
    assert "profit_factor" in data
