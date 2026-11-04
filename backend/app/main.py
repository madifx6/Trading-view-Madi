from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
import asyncio

from app.core.database import engine, get_db, Base
from app.core.models import User, Instrument, Workspace, Alert, PaperAccount
from app.core.security import get_password_hash, verify_password, create_access_token
from app.market_data.provider import HighFidelitySimulatedProvider, OandaMarketDataProvider, ExnessMarketDataProvider
from app.quant.indicators import calculate_sma, calculate_ema, calculate_rsi
from app.trading.risk_engine import RiskEngine
from app.trading.paper_broker import PaperBroker
from app.backtesting.engine import BacktestEngine, BacktestConfig
from app.ai.system import MultiAgentAISystem
import pandas as pd
import numpy as np

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MADI TERMINAL API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_provider = HighFidelitySimulatedProvider()
risk_engine = RiskEngine()
paper_broker = PaperBroker()
ai_system = MultiAgentAISystem()

def init_db_seed():
    db = next(get_db())
    if not db.query(Instrument).first():
        instruments = [
            ("EURUSD", "Euro / US Dollar", "FOREX_MAJOR", 0.0001, 5),
            ("GBPUSD", "British Pound / US Dollar", "FOREX_MAJOR", 0.0001, 5),
            ("USDJPY", "US Dollar / Japanese Yen", "FOREX_MAJOR", 0.01, 3),
            ("USDCHF", "US Dollar / Swiss Franc", "FOREX_MAJOR", 0.0001, 5),
            ("USDCAD", "US Dollar / Canadian Dollar", "FOREX_MAJOR", 0.0001, 5),
            ("AUDUSD", "Australian Dollar / US Dollar", "FOREX_MAJOR", 0.0001, 5),
            ("NZDUSD", "New Zealand Dollar / US Dollar", "FOREX_MAJOR", 0.0001, 5),
            ("EURJPY", "Euro / Japanese Yen", "FOREX_CROSS", 0.01, 3),
            ("GBPJPY", "British Pound / Japanese Yen", "FOREX_CROSS", 0.01, 3),
            ("EURGBP", "Euro / British Pound", "FOREX_CROSS", 0.0001, 5),
            ("EURCHF", "Euro / Swiss Franc", "FOREX_CROSS", 0.0001, 5),
            ("AUDJPY", "Australian Dollar / Japanese Yen", "FOREX_CROSS", 0.01, 3),
            ("XAUUSD", "Gold / US Dollar", "COMMODITY_FOREX", 0.01, 2)
        ]
        for s, n, c, p, d in instruments:
            db.add(Instrument(symbol=s, name=n, category=c, pip_size=p, digits=d))

        test_user = User(
            email="trader@madi.terminal",
            hashed_password=get_password_hash("MadiTerminal2026!"),
            full_name="Madi Lead Trader"
        )
        db.add(test_user)
        db.commit()

init_db_seed()

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "MADI_TERMINAL_BACKEND",
        "emergency_halt": risk_engine.is_emergency_halted(),
        "market_provider": data_provider.get_source_name()
    }

@app.get("/api/instruments")
def get_instruments(db: Session = Depends(get_db)):
    instruments = db.query(Instrument).all()
    return [{"symbol": i.symbol, "name": i.name, "category": i.category, "digits": i.digits} for i in instruments]

@app.get("/api/candles")
def get_candles(symbol: str = "EURUSD", timeframe: str = "1m", count: int = 200):
    candles = data_provider.get_historical_candles(symbol=symbol, timeframe=timeframe, count=count)
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "source": data_provider.get_source_name(),
        "candles": candles
    }

@app.post("/api/backtest/run")
def run_backtest(payload: Dict[str, Any]):
    symbol = payload.get("symbol", "EURUSD")
    candles_data = data_provider.get_historical_candles(symbol=symbol, timeframe="1h", count=300)
    df = pd.DataFrame(candles_data)
    df.set_index(pd.to_datetime(df["time"], unit="s"), inplace=True)

    cfg = BacktestConfig(
        symbol=symbol,
        initial_balance=float(payload.get("initial_balance", 10000.0)),
        spread_pips=float(payload.get("spread_pips", 1.0)),
        slippage_pips=float(payload.get("slippage_pips", 0.5)),
        commission_per_lot=float(payload.get("commission_per_lot", 7.0))
    )
    engine = BacktestEngine(config=cfg, candles=df)
    results = engine.run_sma_cross(
        fast_period=int(payload.get("fast_period", 9)),
        slow_period=int(payload.get("slow_period", 21))
    )
    return results

@app.get("/api/ai/analysis")
def get_ai_analysis(symbol: str = "EURUSD", timeframe: str = "1h"):
    candles = data_provider.get_historical_candles(symbol=symbol, timeframe=timeframe, count=50)
    return ai_system.analyze_market(symbol=symbol, timeframe=timeframe, candles=candles)

@app.get("/api/paper/account")
def get_paper_account():
    return {
        "balance": round(paper_broker.balance, 2),
        "equity": round(paper_broker.equity, 2),
        "margin_used": round(paper_broker.margin_used, 2),
        "positions": paper_broker.positions,
        "orders": paper_broker.order_history
    }

@app.post("/api/paper/order")
def place_paper_order(payload: Dict[str, Any]):
    symbol = payload.get("symbol", "EURUSD")
    side = payload.get("side", "BUY")
    lots = float(payload.get("lots", 1.0))
    current_price = float(payload.get("price", 1.0850))

    risk_check = risk_engine.validate_order(
        account_equity=paper_broker.equity,
        current_daily_loss=0.0,
        order_lot_size=lots
    )
    if not risk_check["approved"]:
        raise HTTPException(status_code=400, detail=risk_check["reason"])

    res = paper_broker.place_order(
        symbol=symbol,
        side=side,
        lots=lots,
        current_price=current_price,
        stop_loss=payload.get("stop_loss"),
        take_profit=payload.get("take_profit"),
        idempotency_key=payload.get("idempotency_key")
    )
    return res

@app.post("/api/paper/close")
def close_paper_position(payload: Dict[str, Any]):
    pos_id = payload.get("position_id")
    price = float(payload.get("price", 1.0850))
    res = paper_broker.close_position(position_id=pos_id, current_price=price)
    return res

@app.websocket("/ws/market-data")
async def websocket_market_data(websocket: WebSocket):
    await websocket.accept()
    try:
        base = 1.08500
        while True:
            base += float(np.random.normal(0, 0.0001))
            tick = {
                "symbol": "EURUSD",
                "bid": round(base, 5),
                "ask": round(base + 0.00015, 5),
                "time": int(asyncio.get_event_loop().time()),
                "source": "SIMULATED_TICK_STREAM"
            }
            await websocket.send_text(json.dumps(tick))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass
