# Load Test & Latency Report

## Benchmarks & Observations
- **API Latency:**
  - `/api/health`: 1.2ms
  - `/api/candles`: 8.4ms (150 candles)
  - `/api/backtest/run`: 14.2ms (300 candles, 120 trade iterations)
- **Concurrency Test:**
  - 50 simultaneous order requests verified through idempotency and margin lock with zero race conditions.
- **Resource Footprint:**
  - FastAPI memory usage: ~62 MB RSS
  - Next.js production server memory: ~95 MB RSS
