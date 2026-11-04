from datetime import datetime, timezone
from typing import Dict, List, Any
import uuid

class PaperBroker:
    def __init__(self, initial_balance: float = 100000.0, leverage: float = 100.0):
        self.balance = initial_balance
        self.equity = initial_balance
        self.margin_used = 0.0
        self.leverage = leverage
        self.positions: List[Dict[str, Any]] = []
        self.order_history: List[Dict[str, Any]] = []
        self.processed_idempotency_keys = set()

    def place_order(
        self,
        symbol: str,
        side: str,
        lots: float,
        current_price: float,
        stop_loss: float | None = None,
        take_profit: float | None = None,
        idempotency_key: str | None = None
    ) -> Dict[str, Any]:
        if idempotency_key and idempotency_key in self.processed_idempotency_keys:
            return {"status": "REJECTED", "reason": "DUPLICATE_IDEMPOTENCY_KEY"}

        if idempotency_key:
            self.processed_idempotency_keys.add(idempotency_key)

        required_margin = (lots * 100000.0) / self.leverage
        if self.balance - self.margin_used < required_margin:
            return {"status": "REJECTED", "reason": "INSUFFICIENT_MARGIN"}

        spread = 0.00015  # 1.5 pips default spread
        fill_price = current_price + (spread / 2 if side == "BUY" else -spread / 2)

        position_id = str(uuid.uuid4())[:8]
        pos = {
            "id": position_id,
            "symbol": symbol,
            "side": side,
            "lots": lots,
            "open_price": round(fill_price, 5),
            "current_price": round(fill_price, 5),
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "profit": 0.0,
            "open_time": datetime.now(timezone.utc).isoformat()
        }
        self.positions.append(pos)
        self.margin_used += required_margin

        order_record = {
            "order_id": str(uuid.uuid4())[:8],
            "position_id": position_id,
            "symbol": symbol,
            "side": side,
            "lots": lots,
            "fill_price": fill_price,
            "time": datetime.now(timezone.utc).isoformat(),
            "status": "FILLED"
        }
        self.order_history.append(order_record)
        return order_record

    def close_position(self, position_id: str, current_price: float) -> Dict[str, Any]:
        pos = next((p for p in self.positions if p["id"] == position_id), None)
        if not pos:
            return {"status": "ERROR", "reason": "POSITION_NOT_FOUND"}

        pip_factor = 100.0 if "JPY" in pos["symbol"] or "XAU" in pos["symbol"] else 10000.0
        price_diff = (current_price - pos["open_price"]) if pos["side"] == "BUY" else (pos["open_price"] - current_price)
        pnl = price_diff * pos["lots"] * 100000.0

        self.balance += pnl
        self.margin_used -= (pos["lots"] * 100000.0) / self.leverage
        self.equity = self.balance
        self.positions.remove(pos)

        close_record = {
            "position_id": position_id,
            "symbol": pos["symbol"],
            "pnl": round(pnl, 2),
            "close_price": current_price,
            "close_time": datetime.now(timezone.utc).isoformat(),
            "status": "CLOSED"
        }
        self.order_history.append(close_record)
        return close_record
