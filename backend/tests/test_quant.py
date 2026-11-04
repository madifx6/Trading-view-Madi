import pytest
import pandas as pd
import numpy as np
from app.quant.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_wma,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_adx,
    calculate_stochastic,
    calculate_cci,
    calculate_momentum,
    calculate_roc,
    calculate_vwap
)

@pytest.fixture
def sample_ohlcv():
    np.random.seed(42)
    n = 100
    close = 1.0850 + np.cumsum(np.random.normal(0, 0.0005, n))
    high = close + np.abs(np.random.normal(0, 0.0003, n))
    low = close - np.abs(np.random.normal(0, 0.0003, n))
    open_p = close + np.random.normal(0, 0.0002, n)
    volume = pd.Series(np.random.randint(100, 2000, n), dtype=float)
    return pd.DataFrame({
        "open": open_p,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume
    })

def test_all_13_indicators(sample_ohlcv):
    c = sample_ohlcv["close"]
    h = sample_ohlcv["high"]
    l = sample_ohlcv["low"]
    v = sample_ohlcv["volume"]

    # 1. SMA
    sma = calculate_sma(c, 14)
    assert len(sma) == 100
    assert not np.isnan(sma.iloc[-1])

    # 2. EMA
    ema = calculate_ema(c, 14)
    assert len(ema) == 100
    assert not np.isnan(ema.iloc[-1])

    # 3. WMA
    wma = calculate_wma(c, 14)
    assert len(wma) == 100
    assert not np.isnan(wma.iloc[-1])

    # 4. RSI
    rsi = calculate_rsi(c, 14)
    assert 0.0 <= rsi.iloc[-1] <= 100.0

    # 5. MACD
    macd = calculate_macd(c)
    assert "macd" in macd and "signal" in macd and "histogram" in macd

    # 6. Bollinger Bands
    bb = calculate_bollinger_bands(c, 20)
    assert (bb["upper"] >= bb["lower"]).all() or np.isnan(bb["upper"].iloc[0])

    # 7. ATR
    atr = calculate_atr(h, l, c, 14)
    assert (atr >= 0).all()

    # 8. ADX
    adx = calculate_adx(h, l, c, 14)
    assert len(adx) == 100

    # 9. Stochastic
    stoch = calculate_stochastic(h, l, c, 14, 3)
    assert (stoch["k"] >= 0).all() and (stoch["k"] <= 100).all()

    # 10. CCI
    cci = calculate_cci(h, l, c, 20)
    assert not np.isinf(cci.iloc[-1])

    # 11. Momentum
    mom = calculate_momentum(c, 10)
    assert len(mom) == 100

    # 12. ROC
    roc = calculate_roc(c, 12)
    assert len(roc) == 100

    # 13. VWAP
    vwap = calculate_vwap(h, l, c, v)
    assert len(vwap) == 100
    assert not np.isnan(vwap.iloc[-1])

def test_indicators_edge_cases():
    empty = pd.Series([], dtype=float)
    assert len(calculate_sma(empty, 14)) == 0
    assert len(calculate_ema(empty, 14)) == 0
    assert len(calculate_rsi(empty, 14)) == 0

    flat = pd.Series([10.0] * 50)
    rsi_flat = calculate_rsi(flat, 14)
    assert not np.isnan(rsi_flat.iloc[-1])
