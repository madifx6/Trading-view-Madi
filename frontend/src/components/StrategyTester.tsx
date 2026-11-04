"use client";

import React, { useState } from "react";
import { Play, Settings, List, BarChart2 } from "lucide-react";

export default function StrategyTester() {
  const [activeTab, setActiveTab] = useState<"overview" | "trades" | "properties">("overview");
  const [fastSMA, setFastSMA] = useState(9);
  const [slowSMA, setSlowSMA] = useState(21);
  const [initialCapital, setInitialCapital] = useState(10000);
  const [results, setResults] = useState<any>(null);
  const [isRunning, setIsRunning] = useState(false);

  const runBacktest = async () => {
    setIsRunning(true);
    try {
      const res = await fetch("http://localhost:8000/api/backtest/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: "EURUSD",
          fast_period: fastSMA,
          slow_period: slowSMA,
          initial_balance: initialCapital,
        }),
      });
      const data = await res.json();
      setResults(data);
    } catch (e) {
      console.error("Backtest failed:", e);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-surface border-t border-border select-none text-xs">
      <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-panel">
        <div className="flex items-center space-x-6">
          <span className="font-semibold text-gray-200">Strategy Tester</span>
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab("overview")}
              id="tab-overview"
              className={`px-3 py-1 rounded flex items-center space-x-1 ${
                activeTab === "overview" ? "bg-accent text-white" : "text-gray-400 hover:text-white"
              }`}
            >
              <BarChart2 className="w-3.5 h-3.5" />
              <span>Overview</span>
            </button>
            <button
              onClick={() => setActiveTab("trades")}
              id="tab-trades"
              className={`px-3 py-1 rounded flex items-center space-x-1 ${
                activeTab === "trades" ? "bg-accent text-white" : "text-gray-400 hover:text-white"
              }`}
            >
              <List className="w-3.5 h-3.5" />
              <span>List of Trades</span>
            </button>
            <button
              onClick={() => setActiveTab("properties")}
              id="tab-properties"
              className={`px-3 py-1 rounded flex items-center space-x-1 ${
                activeTab === "properties" ? "bg-accent text-white" : "text-gray-400 hover:text-white"
              }`}
            >
              <Settings className="w-3.5 h-3.5" />
              <span>Properties</span>
            </button>
          </div>
        </div>

        <button
          onClick={runBacktest}
          disabled={isRunning}
          id="btn-run-strategy"
          className="flex items-center space-x-1.5 px-3 py-1 bg-bull hover:bg-bull/90 text-white font-medium rounded shadow transition"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{isRunning ? "Simulating..." : "Run Test"}</span>
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {activeTab === "overview" && (
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-panel p-3 rounded border border-border">
              <span className="text-gray-400">Net Profit</span>
              <div className={`text-base font-bold mt-1 ${results?.net_profit >= 0 ? "text-bull" : "text-bear"}`}>
                ${results ? results.net_profit.toFixed(2) : "0.00"}
              </div>
            </div>
            <div className="bg-panel p-3 rounded border border-border">
              <span className="text-gray-400">Profit Factor</span>
              <div className="text-base font-bold text-gray-200 mt-1">
                {results ? results.profit_factor : "1.00"}
              </div>
            </div>
            <div className="bg-panel p-3 rounded border border-border">
              <span className="text-gray-400">Total Closed Trades</span>
              <div className="text-base font-bold text-gray-200 mt-1">
                {results ? results.total_trades : "0"}
              </div>
            </div>
            <div className="bg-panel p-3 rounded border border-border">
              <span className="text-gray-400">Percent Profitable</span>
              <div className="text-base font-bold text-bull mt-1">
                {results ? `${results.win_rate}%` : "0.0%"}
              </div>
            </div>
          </div>
        )}

        {activeTab === "trades" && (
          <div className="w-full h-full overflow-auto">
            <table className="w-full text-left border-collapse" id="trades-table">
              <thead>
                <tr className="border-b border-border text-gray-400">
                  <th className="py-2 px-3">#</th>
                  <th className="py-2 px-3">Side</th>
                  <th className="py-2 px-3">Entry Time</th>
                  <th className="py-2 px-3">Entry Price</th>
                  <th className="py-2 px-3">Exit Time</th>
                  <th className="py-2 px-3">Exit Price</th>
                  <th className="py-2 px-3">PnL ($)</th>
                </tr>
              </thead>
              <tbody>
                {results?.trades?.map((trade: any, idx: number) => (
                  <tr key={idx} className="border-b border-border/50 hover:bg-panel">
                    <td className="py-1.5 px-3 text-gray-400">{idx + 1}</td>
                    <td className={`py-1.5 px-3 font-semibold ${trade.side === "BUY" ? "text-bull" : "text-bear"}`}>
                      {trade.side}
                    </td>
                    <td className="py-1.5 px-3 text-gray-400">{trade.entry_time.slice(0, 16)}</td>
                    <td className="py-1.5 px-3">{trade.entry_price}</td>
                    <td className="py-1.5 px-3 text-gray-400">{trade.exit_time.slice(0, 16)}</td>
                    <td className="py-1.5 px-3">{trade.exit_price}</td>
                    <td className={`py-1.5 px-3 font-mono ${trade.pnl >= 0 ? "text-bull" : "text-bear"}`}>
                      {trade.pnl > 0 ? `+${trade.pnl}` : trade.pnl}
                    </td>
                  </tr>
                ))}
                {(!results || !results.trades || results.trades.length === 0) && (
                  <tr>
                    <td colSpan={7} className="text-center py-8 text-gray-500">
                      No strategy execution trades yet. Click "Run Test" above to backtest.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "properties" && (
          <div className="max-w-md space-y-4">
            <div className="flex justify-between items-center">
              <label className="text-gray-300">Initial Capital ($)</label>
              <input
                type="number"
                value={initialCapital}
                onChange={(e) => setInitialCapital(Number(e.target.value))}
                className="bg-panel border border-border rounded px-2 py-1 text-white w-28 text-right"
              />
            </div>
            <div className="flex justify-between items-center">
              <label className="text-gray-300">Fast SMA Period</label>
              <input
                type="number"
                value={fastSMA}
                onChange={(e) => setFastSMA(Number(e.target.value))}
                className="bg-panel border border-border rounded px-2 py-1 text-white w-28 text-right"
              />
            </div>
            <div className="flex justify-between items-center">
              <label className="text-gray-300">Slow SMA Period</label>
              <input
                type="number"
                value={slowSMA}
                onChange={(e) => setSlowSMA(Number(e.target.value))}
                className="bg-panel border border-border rounded px-2 py-1 text-white w-28 text-right"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
