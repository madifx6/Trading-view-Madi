import pandas as pd
import numpy as np
from pydantic import BaseModel
from typing import List, Dict, Any

class BacktestConfig(BaseModel):
    symbol: str = "EURUSD"
    initial_balance: float = 10000.0
    spread_pips: float = 1.0
    slippage_pips: float = 0.5
    commission_per_lot: float = 7.0
    leverage: float = 100.0

class BacktestEngine:
    def __init__(self, config: BacktestConfig, candles: pd.DataFrame):
        self.config = config
        self.candles = candles

    def run_sma_cross(self, fast_period: int = 9, slow_period: int = 21) -> Dict[str, Any]:
        df = self.candles.copy()
        df["fast_sma"] = df["close"].rolling(fast_period).mean()
        df["slow_sma"] = df["close"].rolling(slow_period).mean()

        balance = self.config.initial_balance
        equity_curve = [balance]
        trades = []
        position = None

        pip_unit = 0.01 if "JPY" in self.config.symbol or "XAU" in self.config.symbol else 0.0001
        spread_cost = (self.config.spread_pips + self.config.slippage_pips) * pip_unit

        for i in range(slow_period + 1, len(df)):
            curr_row = df.iloc[i]
            prev_row = df.iloc[i - 1]

            bullish_cross = prev_row["fast_sma"] > prev_row["slow_sma"] and df.iloc[i - 2]["fast_sma"] <= df.iloc[i - 2]["slow_sma"]
            bearish_cross = prev_row["fast_sma"] < prev_row["slow_sma"] and df.iloc[i - 2]["fast_sma"] >= df.iloc[i - 2]["slow_sma"]

            if position:
                if (position["side"] == "BUY" and bearish_cross) or (position["side"] == "SELL" and bullish_cross):
                    close_price = curr_row["open"]
                    pnl_raw = (close_price - position["entry"]) if position["side"] == "BUY" else (position["entry"] - close_price)
                    pnl_dollars = (pnl_raw / pip_unit) * 10.0 * position["lots"] - self.config.commission_per_lot * position["lots"]
                    balance += pnl_dollars
                    trades.append({
                        "entry_time": str(position["time"]),
                        "exit_time": str(curr_row.name),
                        "side": position["side"],
                        "entry_price": round(position["entry"], 5),
                        "exit_price": round(close_price, 5),
                        "pnl": round(pnl_dollars, 2)
                    })
                    position = None

            if not position:
                if bullish_cross:
                    position = {
                        "side": "BUY",
                        "entry": curr_row["open"] + (spread_cost / 2),
                        "time": curr_row.name,
                        "lots": 1.0
                    }
                elif bearish_cross:
                    position = {
                        "side": "SELL",
                        "entry": curr_row["open"] - (spread_cost / 2),
                        "time": curr_row.name,
                        "lots": 1.0
                    }

            equity_curve.append(round(balance, 2))

        if position:
            last_row = df.iloc[-1]
            close_price = last_row["close"]
            pnl_raw = (close_price - position["entry"]) if position["side"] == "BUY" else (position["entry"] - close_price)
            pnl_dollars = (pnl_raw / pip_unit) * 10.0 * position["lots"] - self.config.commission_per_lot * position["lots"]
            balance += pnl_dollars
            trades.append({
                "entry_time": str(position["time"]),
                "exit_time": str(last_row.name),
                "side": position["side"],
                "entry_price": round(position["entry"], 5),
                "exit_price": round(close_price, 5),
                "pnl": round(pnl_dollars, 2)
            })

        net_profit = round(balance - self.config.initial_balance, 2)
        winning_trades = [t for t in trades if t["pnl"] > 0]
        losing_trades = [t for t in trades if t["pnl"] <= 0]
        win_rate = round((len(winning_trades) / len(trades) * 100) if trades else 0.0, 2)
        gross_profit = sum(t["pnl"] for t in winning_trades)
        gross_loss = abs(sum(t["pnl"] for t in losing_trades))
        profit_factor = round((gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 1.0), 2)

        peak = -np.inf
        max_dd = 0.0
        for val in equity_curve:
            if val > peak: peak = val
            dd = peak - val
            if dd > max_dd: max_dd = dd

        return {
            "initial_balance": self.config.initial_balance,
            "final_balance": round(balance, 2),
            "net_profit": net_profit,
            "profit_factor": profit_factor,
            "total_trades": len(trades),
            "win_rate": win_rate,
            "max_drawdown": round(max_dd, 2),
            "trades": trades,
            "equity_curve": equity_curve[-50:]
        }
