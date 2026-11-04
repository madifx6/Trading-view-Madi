import { create } from "zustand";

interface TerminalState {
  symbol: string;
  timeframe: string;
  chartType: string;
  selectedTool: string;
  activeIndicator: string | null;
  drawings: any[];
  setSymbol: (s: string) => void;
  setTimeframe: (tf: string) => void;
  setChartType: (ct: string) => void;
  setSelectedTool: (t: string) => void;
  setActiveIndicator: (ind: string | null) => void;
  addDrawing: (d: any) => void;
  clearDrawings: () => void;
}

export const useTerminalStore = create<TerminalState>((set) => ({
  symbol: "EURUSD",
  timeframe: "1m",
  chartType: "Candlestick",
  selectedTool: "cursor",
  activeIndicator: "RSI",
  drawings: [],
  setSymbol: (s) => set({ symbol: s }),
  setTimeframe: (tf) => set({ timeframe: tf }),
  setChartType: (ct) => set({ chartType: ct }),
  setSelectedTool: (t) => set({ selectedTool: t }),
  setActiveIndicator: (ind) => set({ activeIndicator: ind }),
  addDrawing: (d) => set((state) => ({ drawings: [...state.drawings, d] })),
  clearDrawings: () => set({ drawings: [] }),
}));
