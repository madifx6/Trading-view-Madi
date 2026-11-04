import pandas as pd
import numpy as np

def calculate_sma(series: pd.Series, period: int = 14) -> pd.Series:
    if len(series) < period:
        return pd.Series(index=series.index, dtype=float)
    return series.rolling(window=period).mean()

def calculate_ema(series: pd.Series, period: int = 14) -> pd.Series:
    if len(series) < period:
        return pd.Series(index=series.index, dtype=float)
    return series.ewm(span=period, adjust=False).mean()

def calculate_wma(series: pd.Series, period: int = 14) -> pd.Series:
    if len(series) < period:
        return pd.Series(index=series.index, dtype=float)
    weights = np.arange(1, period + 1)
    return series.rolling(period).apply(lambda p: np.dot(p, weights) / weights.sum(), raw=True)

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    if len(series) < period + 1:
        return pd.Series(50.0, index=series.index, dtype=float)
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)

def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    fast_ema = calculate_ema(series, fast)
    slow_ema = calculate_ema(series, slow)
    macd_line = fast_ema - slow_ema
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return {"macd": macd_line, "signal": signal_line, "histogram": histogram}

def calculate_bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0) -> dict:
    mid = calculate_sma(series, period)
    std = series.rolling(window=period).std()
    upper = mid + (std * std_dev)
    lower = mid - (std * std_dev)
    return {"upper": upper, "middle": mid, "lower": lower}

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean().fillna(0.0)

def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    tr = calculate_atr(high, low, close, period)
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    plus_di = 100 * (pd.Series(plus_dm).rolling(period).mean() / tr.replace(0, np.nan))
    minus_di = 100 * (pd.Series(minus_dm).rolling(period).mean() / tr.replace(0, np.nan))
    dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan))
    return dx.rolling(period).mean().fillna(25.0)

def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> dict:
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k_line = 100 * ((close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan))
    d_line = k_line.rolling(window=d_period).mean()
    return {"k": k_line.fillna(50.0), "d": d_line.fillna(50.0)}

def calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(period).mean()
    mean_dev = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    cci = (tp - sma_tp) / (0.015 * mean_dev.replace(0, np.nan))
    return cci.fillna(0.0)

def calculate_momentum(close: pd.Series, period: int = 10) -> pd.Series:
    return (close - close.shift(period)).fillna(0.0)

def calculate_roc(close: pd.Series, period: int = 12) -> pd.Series:
    return (((close - close.shift(period)) / close.shift(period).replace(0, np.nan)) * 100).fillna(0.0)

def calculate_vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    tp = (high + low + close) / 3
    vp = tp * volume
    vol_cumsum = volume.cumsum().replace(0, np.nan)
    return (vp.cumsum() / vol_cumsum).fillna(close)
