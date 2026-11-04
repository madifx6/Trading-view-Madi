# Market Data Validation Report

## Scope of Inspection
1. **OANDA REST & Streaming:** Evaluated environment separation between practice (`api-fxpractice.oanda.com`) and live (`api-fxtrade.oanda.com`). When no API key is provided, connection status correctly evaluates to `BLOCKED`.
2. **Exness / MT5 Gateway:** Evaluated socket connector. When login or server are omitted, connection status correctly evaluates to `BLOCKED`.
3. **High-Fidelity Simulated Data:** Validated Brownian motion generator ensuring no artificial price teleportation, realistic spreads (1.5 pips default), and timestamp consistency.
4. **Data Attribution:** Every candle and tick explicitly includes its source (`SIMULATED_HIGH_FIDELITY`, `OANDA_V20_LIVE`, `EXNESS_MT5`) and status (`SIMULATED`, `LIVE`, `BLOCKED`, `UNVERIFIED`).
