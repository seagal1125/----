#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# VT Bollinger Band backtest script per user requirements.
# - Fetches VT (Vanguard Total World Stock ETF) with yfinance (auto_adjust=True).
# - Detects independent buy signals when Close <= LowerBand, with a cooldown until price closes back above SMA.
# - Analysis 1: For each interval between consecutive signals [T_i, T_{i+1}), computes the fraction of days where P(d) > P_{i+1}.
#   The overall average win rate is the simple mean across intervals.
# - Analysis 2: For every trading day up to the second-to-last signal date, computes calendar-day waits to the next signal;
#   reports the average waiting days.
# - Parameters PERIOD (SMA/STD window) and STD_DEV_FACTOR configurable via CLI.
# - Prints a summary report in Traditional Chinese matching the requested format.

import argparse
import sys
from typing import List, Tuple

import pandas as pd


def compute_bollinger(df: pd.DataFrame, period: int, k: float) -> pd.DataFrame:
    s = df["Close"]
    sma = s.rolling(window=period, min_periods=period).mean()
    std = s.rolling(window=period, min_periods=period).std(ddof=0)
    lower = sma - k * std
    out = df.copy()
    out["SMA"] = sma
    out["Lower"] = lower
    return out


def find_independent_signals(df: pd.DataFrame) -> List[Tuple[pd.Timestamp, float]]:
    allow_signal = True
    signals: List[Tuple[pd.Timestamp, float]] = []
    for ts, row in df.iterrows():
        close = row["Close"]
        sma = row["SMA"]
        lower = row["Lower"]
        if pd.isna(sma) or pd.isna(lower):
            continue
        if allow_signal and close <= lower:
            signals.append((ts, float(close)))
            allow_signal = False
            continue
        if not allow_signal and close > sma:
            allow_signal = True
    return signals


def analysis_win_rate(df: pd.DataFrame, signals: List[Tuple[pd.Timestamp, float]]) -> Tuple[float, int]:
    if len(signals) < 2:
        return float("nan"), 0
    win_rates = []
    for i in range(len(signals) - 1):
        t1, _ = signals[i]
        t2, p2 = signals[i + 1]
        mask = (df.index >= t1) & (df.index < t2)
        seg = df.loc[mask]
        if seg.empty:
            continue
        wins = (seg["Close"] > p2).sum()
        total = len(seg)
        win_rate = wins / total * 100.0
        win_rates.append(win_rate)
    if not win_rates:
        return float("nan"), 0
    return float(pd.Series(win_rates).mean()), len(win_rates)


def analysis_avg_wait_calendar_days(df: pd.DataFrame, signals: List[Tuple[pd.Timestamp, float]]) -> float:
    if len(signals) < 2:
        return float("nan")
    signal_dates = pd.to_datetime([t for t, _ in signals])
    second_last_signal_date = signal_dates[-2]
    trading_dates = df.index[df.index <= second_last_signal_date]
    waits = []
    for d in trading_dates:
        idx = signal_dates.searchsorted(d, side="right")
        if idx >= len(signal_dates):
            break
        next_sig_date = signal_dates[idx]
        waits.append((next_sig_date.date() - d.date()).days)
    if not waits:
        return float("nan")
    return float(pd.Series(waits).mean())

def load_data(ticker: str, start: str = None, end: str = None) -> pd.DataFrame:
    try:
        import yfinance as yf
    except Exception:
        print("請先安裝 yfinance： pip install yfinance", file=sys.stderr)
        raise
    if start or end:
        hist = yf.Ticker(ticker).history(start=start, end=end, auto_adjust=True)
    else:
        hist = yf.Ticker(ticker).history(period="max", auto_adjust=True)
    if hist.empty:
        print("抓不到價格資料，請檢查網路或 Ticker 是否正確。", file=sys.stderr)
        sys.exit(1)
    df = hist[["Close"]].copy()
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df

def run(period: int, std_factor: float, ticker: str = "VT", start: str = None, end: str = None) -> str:
    df = load_data(ticker, start=start, end=end)
    df = compute_bollinger(df, period=period, k=std_factor)
    signals = find_independent_signals(df)
    avg_win_rate, n_intervals = analysis_win_rate(df, signals)
    avg_wait_days = analysis_avg_wait_calendar_days(df, signals)
    start_date = df.index.min().strftime("%Y-%m-%d")
    end_date = df.index.max().strftime("%Y-%m-%d")

    lines = []
    lines.append("=" * 50)
    lines.append("VT 布林通道策略分析報告")
    lines.append("=" * 50)
    lines.append(f"分析區間: [{start_date}] 至 [{end_date}]")
    lines.append(f"使用參數: 期間={period} 天, 標準差倍數={std_factor}")
    lines.append("-" * 50)
    if n_intervals == 0 or pd.isna(avg_win_rate):
        lines.append("平均勝率: 無法計算（有效訊號區間不足）")
    else:
        lines.append(f"平均勝率: {avg_win_rate:.2f}% (共 {n_intervals} 個分析區間)")
    if pd.isna(avg_wait_days):
        lines.append("平均等待天數: 無法計算（有效訊號不足）")
    else:
        lines.append(f"平均等待天數: {avg_wait_days:.1f} 天")
    lines.append("=" * 50)
    return "\n".join(lines)

def main(argv=None):
    parser = argparse.ArgumentParser(description="VT 布林通道策略回測")
    parser.add_argument("--period", type=int, default=15, help="布林通道期間 (SMA/STD 天數)")
    parser.add_argument("--std", type=float, default=1.5, help="標準差倍數")
    parser.add_argument("--start", type=str, default=None, help="可選：自訂起始日 YYYY-MM-DD")
    parser.add_argument("--end", type=str, default=None, help="可選：自訂結束日 YYYY-MM-DD")
    parser.add_argument("--ticker", type=str, default="VT", help="Ticker (預設: VT)")
    args = parser.parse_args(argv)
    report = run(args.period, args.std, ticker=args.ticker, start=args.start, end=args.end)
    print(report)


if __name__ == "__main__":
    main()
