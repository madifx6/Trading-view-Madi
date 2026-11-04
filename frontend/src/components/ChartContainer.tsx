"use client";

import React, { useEffect, useRef, useState } from "react";
import { createChart, ColorType, CandlestickSeries, LineSeries } from "lightweight-charts";
import { useTerminalStore } from "@/store/terminalStore";

export default function ChartContainer() {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const candleSeriesRef = useRef<any>(null);
  const rsiSeriesRef = useRef<any>(null);

  const { symbol, timeframe, activeIndicator, selectedTool, drawings, addDrawing } = useTerminalStore();
  const [candles, setCandles] = useState<any[]>([]);
  const [drawingStart, setDrawingStart] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    fetch(`http://localhost:8000/api/candles?symbol=${symbol}&timeframe=${timeframe}&count=150`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.candles) {
          setCandles(data.candles);
        }
      })
      .catch((err) => console.error("Error fetching candles:", err));
  }, [symbol, timeframe]);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "#131722" },
        textColor: "#d1d4dc",
      },
      grid: {
        vertLines: { color: "#1e222d" },
        horzLines: { color: "#1e222d" },
      },
      crosshair: {
        mode: 1,
      },
      timeScale: {
        borderColor: "#2a2e39",
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: "#2a2e39",
      },
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#089981",
      downColor: "#f23645",
      borderVisible: false,
      wickUpColor: "#089981",
      wickDownColor: "#f23645",
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight,
        });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, []);

  useEffect(() => {
    if (!candleSeriesRef.current || candles.length === 0) return;

    const formatted = candles.map((c) => ({
      time: c.time,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close,
    })).sort((a, b) => a.time - b.time);

    candleSeriesRef.current.setData(formatted);

    if (activeIndicator === "RSI" && chartRef.current) {
      if (!rsiSeriesRef.current) {
        const rsiSeries = chartRef.current.addSeries(LineSeries, {
          color: "#9c27b0",
          lineWidth: 2,
          priceScaleId: "rsi",
        });
        chartRef.current.priceScale("rsi").applyOptions({
          scaleMargins: {
            top: 0.8,
            bottom: 0,
          },
        });
        rsiSeriesRef.current = rsiSeries;
      }
      const rsiData = formatted.map((c, idx) => ({
        time: c.time,
        value: 30 + (Math.sin(idx * 0.2) + 1) * 20,
      }));
      rsiSeriesRef.current.setData(rsiData);
    } else if (rsiSeriesRef.current && chartRef.current) {
      chartRef.current.removeSeries(rsiSeriesRef.current);
      rsiSeriesRef.current = null;
    }
  }, [candles, activeIndicator]);

  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (selectedTool === "cursor") return;
    const rect = e.currentTarget.getBoundingClientRect();
    setDrawingStart({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  const handleMouseUp = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!drawingStart || selectedTool === "cursor") return;
    const rect = e.currentTarget.getBoundingClientRect();
    const endX = e.clientX - rect.left;
    const endY = e.clientY - rect.top;

    addDrawing({
      type: selectedTool,
      x1: drawingStart.x,
      y1: drawingStart.y,
      x2: endX,
      y2: endY,
    });
    setDrawingStart(null);
  };

  return (
    <div
      className="relative w-full h-full cursor-crosshair select-none"
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
    >
      <div ref={chartContainerRef} className="w-full h-full" />
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        {drawings.map((d, index) => {
          if (d.type === "trendline") {
            return (
              <line
                key={index}
                x1={d.x1}
                y1={d.y1}
                x2={d.x2}
                y2={d.y2}
                stroke="#2962ff"
                strokeWidth="2"
              />
            );
          }
          if (d.type === "horizontal") {
            return (
              <line
                key={index}
                x1="0"
                y1={d.y1}
                x2="100%"
                y2={d.y1}
                stroke="#ff9800"
                strokeWidth="2"
                strokeDasharray="4"
              />
            );
          }
          if (d.type === "vertical") {
            return (
              <line
                key={index}
                x1={d.x1}
                y1="0"
                x2={d.x1}
                y2="100%"
                stroke="#e91e63"
                strokeWidth="2"
                strokeDasharray="4"
              />
            );
          }
          if (d.type === "rectangle") {
            const rx = Math.min(d.x1, d.x2);
            const ry = Math.min(d.y1, d.y2);
            const rw = Math.abs(d.x2 - d.x1);
            const rh = Math.abs(d.y2 - d.y1);
            return (
              <rect
                key={index}
                x={rx}
                y={ry}
                width={rw}
                height={rh}
                fill="rgba(41, 98, 255, 0.15)"
                stroke="#2962ff"
                strokeWidth="1.5"
              />
            );
          }
          if (d.type === "fibonacci") {
            const levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];
            const dy = d.y2 - d.y1;
            return (
              <g key={index}>
                {levels.map((lvl) => {
                  const ly = d.y1 + dy * lvl;
                  return (
                    <g key={lvl}>
                      <line
                        x1={Math.min(d.x1, d.x2)}
                        y1={ly}
                        x2={Math.max(d.x1, d.x2)}
                        y2={ly}
                        stroke="#00bcd4"
                        strokeWidth="1"
                        strokeDasharray="2"
                      />
                      <text
                        x={Math.min(d.x1, d.x2) + 5}
                        y={ly - 3}
                        fill="#00bcd4"
                        fontSize="10"
                      >
                        {(lvl * 100).toFixed(1)}%
                      </text>
                    </g>
                  );
                })}
              </g>
            );
          }
          return null;
        })}
      </svg>
      <div className="absolute top-3 left-4 flex items-center space-x-3 pointer-events-none bg-surface/80 backdrop-blur px-3 py-1.5 rounded border border-border">
        <span className="font-bold text-white tracking-wider">{symbol}</span>
        <span className="text-xs text-bull font-mono">1.08542</span>
        <span className="text-xs text-gray-400">O: 1.08510 H: 1.08560 L: 1.08490 C: 1.08542</span>
        <span className="text-[10px] text-blue-400 font-semibold px-1.5 py-0.5 rounded bg-blue-950/60 border border-blue-800">
          DATA SOURCE: SIMULATED_HIGH_FIDELITY
        </span>
      </div>
    </div>
  );
}
