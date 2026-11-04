"use client";

import React, { useState, useEffect } from "react";
import ChartContainer from "@/components/ChartContainer";
import StrategyTester from "@/components/StrategyTester";
import { useTerminalStore } from "@/store/terminalStore";
import {
  TrendingUp,
  Minus,
  Maximize2,
  MousePointer,
  Layers,
  Activity,
  ShieldAlert,
  Cpu,
  SlidersHorizontal,
  DollarSign
} from "lucide-react";

export default function TerminalPage() {
  const { symbol, setSymbol, timeframe, setTimeframe, selectedTool, setSelectedTool, activeIndicator, setActiveIndicator } = useTerminalStore();
  const [activeBottomTab, setActiveBottomTab] = useState<"strategy" | "positions" | "ai">("strategy");
  const [account, setAccount] = useState<any>({ balance: 100000.0, equity: 100000.0, positions: [] });
  const [aiData, setAiData] = useState<any>(null);

  const instruments = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "XAUUSD"];
  const timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"];

  const fetchAccount = () => {
    fetch("http://localhost:8000/api/paper/account")
      .then((r) => r.json())
      .then((d) => setAccount(d))
      .catch((e) => console.error(e));
  };

  useEffect(() => {
    fetchAccount();
    fetch(`http://localhost:8000/api/ai/analysis?symbol=${symbol}`)
      .then((r) => r.json())
      .then((d) => setAiData(d))
      .catch((e) => console.error(e));
  }, [symbol]);

  const placeOrder = async (side: "BUY" | "SELL") => {
    try {
      await fetch("http://localhost:8000/api/paper/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol,
          side,
          lots: 1.0,
          price: 1.0850,
          idempotency_key: `order-${Date.now()}`
        }),
      });
      fetchAccount();
    } catch (e) {
      console.error(e);
    }
  };

  const closePosition = async (id: string) => {
    try {
      await fetch("http://localhost:8000/api/paper/close", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          position_id: id,
          price: 1.0855
        }),
      });
      fetchAccount();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-background overflow-hidden text-sm">
      <div className="h-12 border-b border-border bg-panel flex items-center justify-between px-4 select-none">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded bg-accent flex items-center justify-center font-black text-xs text-white">M</div>
            <span className="font-bold tracking-wider text-white">MADI TERMINAL</span>
          </div>

          <div className="flex items-center bg-surface border border-border rounded px-2 py-1">
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              id="instrument-select"
              className="bg-transparent text-white font-semibold outline-none cursor-pointer"
            >
              {instruments.map((inst) => (
                <option key={inst} value={inst} className="bg-panel">
                  {inst}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-1">
            {timeframes.map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-2 py-0.5 rounded text-xs font-medium ${
                  timeframe === tf ? "bg-accent text-white" : "text-gray-400 hover:text-white"
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveIndicator(activeIndicator === "RSI" ? null : "RSI")}
              className={`px-2 py-1 rounded text-xs border ${
                activeIndicator === "RSI" ? "border-accent text-accent" : "border-border text-gray-400"
              }`}
            >
              RSI (14)
            </button>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3 text-xs bg-surface px-3 py-1 rounded border border-border">
            <span className="text-gray-400">Equity:</span>
            <span className="font-mono font-bold text-white">${account.equity?.toLocaleString()}</span>
          </div>
          <button
            onClick={() => placeOrder("BUY")}
            id="btn-buy"
            className="px-3 py-1 bg-bull hover:bg-bull/90 text-white font-bold rounded shadow text-xs"
          >
            BUY 1.0
          </button>
          <button
            onClick={() => placeOrder("SELL")}
            id="btn-sell"
            className="px-3 py-1 bg-bear hover:bg-bear/90 text-white font-bold rounded shadow text-xs"
          >
            SELL 1.0
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="w-12 border-r border-border bg-panel flex flex-col items-center py-3 space-y-3 select-none">
          <button
            onClick={() => setSelectedTool("cursor")}
            className={`p-2 rounded ${selectedTool === "cursor" ? "bg-accent text-white" : "text-gray-400 hover:text-white"}`}
            title="Cursor"
          >
            <MousePointer className="w-4 h-4" />
          </button>
          <button
            onClick={() => setSelectedTool("trendline")}
            className={`p-2 rounded ${selectedTool === "trendline" ? "bg-accent text-white" : "text-gray-400 hover:text-white"}`}
            title="Trendline"
          >
            <TrendingUp className="w-4 h-4" />
          </button>
          <button
            onClick={() => setSelectedTool("horizontal")}
            className={`p-2 rounded ${selectedTool === "horizontal" ? "bg-accent text-white" : "text-gray-400 hover:text-white"}`}
            title="Horizontal Line"
          >
            <Minus className="w-4 h-4" />
          </button>
          <button
            onClick={() => setSelectedTool("rectangle")}
            className={`p-2 rounded ${selectedTool === "rectangle" ? "bg-accent text-white" : "text-gray-400 hover:text-white"}`}
            title="Rectangle"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setSelectedTool("fibonacci")}
            className={`p-2 rounded ${selectedTool === "fibonacci" ? "bg-accent text-white" : "text-gray-400 hover:text-white"}`}
            title="Fibonacci Retracement"
          >
            <SlidersHorizontal className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 flex flex-col">
          <div className="flex-1 relative">
            <ChartContainer />
          </div>

          <div className="h-64 border-t border-border flex flex-col bg-surface">
            <div className="flex items-center space-x-4 px-4 py-1.5 border-b border-border bg-panel text-xs">
              <button
                onClick={() => setActiveBottomTab("strategy")}
                id="tab-strategy"
                className={`font-medium ${activeBottomTab === "strategy" ? "text-white border-b-2 border-accent" : "text-gray-400 hover:text-white"}`}
              >
                Strategy Tester
              </button>
              <button
                onClick={() => setActiveBottomTab("positions")}
                id="tab-positions"
                className={`font-medium ${activeBottomTab === "positions" ? "text-white border-b-2 border-accent" : "text-gray-400 hover:text-white"}`}
              >
                Paper Positions ({account.positions?.length || 0})
              </button>
              <button
                onClick={() => setActiveBottomTab("ai")}
                id="tab-ai"
                className={`font-medium ${activeBottomTab === "ai" ? "text-white border-b-2 border-accent" : "text-gray-400 hover:text-white"}`}
              >
                AI Multi-Agent Consensus
              </button>
            </div>

            <div className="flex-1 overflow-hidden">
              {activeBottomTab === "strategy" && <StrategyTester />}
              {activeBottomTab === "positions" && (
                <div className="p-4 overflow-auto h-full text-xs">
                  <table className="w-full text-left border-collapse" id="positions-table">
                    <thead>
                      <tr className="border-b border-border text-gray-400">
                        <th className="py-1.5 px-3">ID</th>
                        <th className="py-1.5 px-3">Symbol</th>
                        <th className="py-1.5 px-3">Side</th>
                        <th className="py-1.5 px-3">Lots</th>
                        <th className="py-1.5 px-3">Open Price</th>
                        <th className="py-1.5 px-3">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {account.positions?.map((p: any) => (
                        <tr key={p.id} className="border-b border-border/40 hover:bg-panel">
                          <td className="py-2 px-3 text-gray-400 font-mono">{p.id}</td>
                          <td className="py-2 px-3 font-semibold">{p.symbol}</td>
                          <td className={`py-2 px-3 font-bold ${p.side === "BUY" ? "text-bull" : "text-bear"}`}>{p.side}</td>
                          <td className="py-2 px-3">{p.lots}</td>
                          <td className="py-2 px-3">{p.open_price}</td>
                          <td className="py-2 px-3">
                            <button
                              onClick={() => closePosition(p.id)}
                              className="px-2 py-0.5 bg-bear/80 hover:bg-bear text-white rounded text-[11px]"
                            >
                              Close
                            </button>
                          </td>
                        </tr>
                      ))}
                      {(!account.positions || account.positions.length === 0) && (
                        <tr>
                          <td colSpan={6} className="text-center py-6 text-gray-500">
                            No open positions. Use BUY/SELL buttons in the top navbar to execute simulated orders.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
              {activeBottomTab === "ai" && (
                <div className="p-4 overflow-auto h-full text-xs space-y-3">
                  <div className="flex items-center space-x-3">
                    <span className="font-semibold text-gray-200">Consensus Setup:</span>
                    <span className={`font-bold px-2 py-0.5 rounded text-white ${aiData?.direction === "BUY" ? "bg-bull" : "bg-bear"}`}>
                      {aiData?.direction} {aiData?.symbol}
                    </span>
                    <span className="text-gray-400">Entry Zone: {aiData?.entry_zone}</span>
                    <span className="text-gray-400">Stop Loss: {aiData?.stop_loss}</span>
                    <span className="text-gray-400">Target: {aiData?.take_profit_levels?.[0]}</span>
                    <span className="text-blue-400 font-bold">Confidence: {(aiData?.calibrated_confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="space-y-1">
                    <span className="font-semibold text-gray-300">Supporting Evidence:</span>
                    {aiData?.supporting_evidence?.map((ev: string, idx: number) => (
                      <div key={idx} className="text-gray-400 flex items-center space-x-1.5">
                        <span className="text-bull">•</span>
                        <span>{ev}</span>
                      </div>
                    ))}
                  </div>
                  <div className="text-[11px] text-gray-500 italic">
                    {aiData?.disclaimer}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="w-64 border-l border-border bg-panel flex flex-col select-none">
          <div className="px-3 py-2 border-b border-border font-semibold text-xs text-gray-200">
            Market Watchlist
          </div>
          <div className="flex-1 overflow-auto divide-y divide-border/40">
            {instruments.map((inst) => (
              <div
                key={inst}
                onClick={() => setSymbol(inst)}
                className={`p-2.5 flex items-center justify-between cursor-pointer hover:bg-surface/60 transition ${
                  symbol === inst ? "bg-surface border-l-2 border-accent" : ""
                }`}
              >
                <div>
                  <div className="font-semibold text-xs text-white">{inst}</div>
                  <div className="text-[10px] text-gray-400">FX Spot</div>
                </div>
                <div className="text-right">
                  <div className="font-mono text-xs text-bull">1.08542</div>
                  <div className="text-[10px] text-gray-400">+0.15%</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
