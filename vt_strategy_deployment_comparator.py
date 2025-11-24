#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd


# =========================
# 資料讀取與技術指標
# =========================
def load_data(ticker: str, start: Optional[str], end: Optional[str]) -> pd.DataFrame:
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


def add_bollinger(df: pd.DataFrame, period: int, k: float) -> pd.DataFrame:
    s = df["Close"]
    sma = s.rolling(window=period, min_periods=period).mean()
    std = s.rolling(window=period, min_periods=period).std(ddof=0)
    lower = sma - k * std
    out = df.copy()
    out["SMA"] = sma
    out["Lower"] = lower
    return out


# =========================
# 視窗切片與日/月節點
# =========================
def slice_window(df: pd.DataFrame, start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> pd.DataFrame:
    return df.loc[(df.index >= start_ts) & (df.index <= end_ts)].copy()


def first_trading_day_each_month(df: pd.DataFrame) -> List[pd.Timestamp]:
    months = pd.Index(df.index.to_period("M"))
    firsts = []
    seen = set()
    for i, p in enumerate(months):
        if p not in seen:
            firsts.append(df.index[i])
            seen.add(p)
    return firsts


# =========================
# 訊號與策略模擬
# =========================
def find_independent_signals(df_bb_window: pd.DataFrame) -> List[Tuple[pd.Timestamp, float]]:
    allow = True
    signals: List[Tuple[pd.Timestamp, float]] = []
    for ts, row in df_bb_window.iterrows():
        sma, lower, close = row["SMA"], row["Lower"], row["Close"]
        if pd.isna(sma) or pd.isna(lower):
            continue
        if allow and close <= lower:
            signals.append((ts, float(close)))
            allow = False
            continue
        if not allow and close > sma:
            allow = True
    return signals

@dataclass
class StrategyResult:
    name: str
    final_value: float
    total_return_pct: float

def simulate_lump_sum(df_window: pd.DataFrame, initial_capital: float) -> StrategyResult:
    if df_window.empty: return StrategyResult("期初單筆投入", np.nan, np.nan)
    first_day, last_day = df_window.index[0], df_window.index[-1]
    shares = initial_capital / df_window.loc[first_day, "Close"]
    final_value = shares * df_window.loc[last_day, "Close"]
    ret = (final_value / initial_capital - 1.0) * 100.0
    return StrategyResult("期初單筆投入", float(final_value), float(ret))

def simulate_signal_all_in(df_bb_window: pd.DataFrame, initial_capital: float) -> StrategyResult:
    sig = find_independent_signals(df_bb_window)[0] if find_independent_signals(df_bb_window) else None
    last_day = df_bb_window.index[-1]
    if sig is None:
        final_value = initial_capital
    else:
        ts, price = sig
        shares = initial_capital / price
        final_value = shares * df_bb_window.loc[last_day, "Close"]
    ret = (final_value / initial_capital - 1.0) * 100.0
    return StrategyResult("首次訊號單筆投入", float(final_value), float(ret))

def simulate_dca(df_window: pd.DataFrame, initial_capital: float, dca_months: int = 24) -> StrategyResult:
    if df_window.empty: return StrategyResult("分期投入 (DCA)", np.nan, np.nan)
    per_tranche = initial_capital / dca_months
    buy_days = first_trading_day_each_month(df_window)[:dca_months]
    shares = 0.0
    for d in buy_days:
        price = df_window.loc[d, "Close"]
        shares += per_tranche / price
    last_day = df_window.index[-1]
    final_value = shares * df_window.loc[last_day, "Close"]
    ret = (final_value / initial_capital - 1.0) * 100.0
    return StrategyResult("分期投入 (DCA)", float(final_value), float(ret))

# =========================
# 分析函式
# =========================
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

# =========================
# 報告
# =========================
def single_period_report(
    df_full: pd.DataFrame, period: int, std_k: float, initial_capital: float, dca_months: int
) -> str:
    df_bb_full = add_bollinger(df_full, period, std_k)
    start_date, end_date = df_full.index.min().strftime("%Y-%m-%d"), df_full.index.max().strftime("%Y-%m-%d")

    res_ls = simulate_lump_sum(df_full, initial_capital)
    res_bb = simulate_signal_all_in(df_bb_full, initial_capital)
    res_dca = simulate_dca(df_full, initial_capital, dca_months=dca_months)
    
    signals = find_independent_signals(df_bb_full)
    avg_wait_days = analysis_avg_wait_calendar_days(df_full, signals)

    def pct_diff(a: float, b: float) -> float: return np.nan if b == 0 else (a - b) / b * 100.0
    bb_vs_ls = pct_diff(res_bb.final_value, res_ls.final_value)
    dca_vs_ls = pct_diff(res_dca.final_value, res_ls.final_value)

    def fm(x: float) -> str: return f"${x:,.2f}"
    def fp(x: float) -> str: return "NA" if pd.isna(x) else f"{x:.2f}%"

    lines = []
    lines.append("=" * 70)
    lines.append("VT 資金部署策略回測")
    lines.append("=" * 70)
    lines.append(f"分析標的: VT")
    lines.append(f"分析區間: [{start_date}] 至 [{end_date}]")
    lines.append(f"初始總資金: {fm(initial_capital)}")
    lines.append(f"布林參數: 期間={period} 天, 標準差倍數={std_k}")
    lines.append(f"DCA 期數: {dca_months} 個月")
    lines.append("-" * 70)
    lines.append(f"{ '策略名稱':<20}{'最終資產價值':>20}{'總報酬率':>12}")
    lines.append("-" * 70)
    for r in [res_ls, res_bb, res_dca]:
        lines.append(f"{r.name:<20}{fm(r.final_value):>20}{fp(r.total_return_pct):>12}")
    lines.append("-" * 70)
    lines.append("相對期初單筆（以最終資產價值比較）：")
    lines.append(f"- 首次訊號單筆投入 vs 期初單筆：{fp(bb_vs_ls)}")
    lines.append(f"- 分期投入 (DCA)     vs 期初單筆：{fp(dca_vs_ls)}")
    if avg_wait_days is not None and not pd.isna(avg_wait_days):
        lines.append(f"此參數下的平均進場等待天數: {avg_wait_days:.1f} 天")
    lines.append("=" * 70)
    return "\n".join(lines)

def main(argv=None):
    parser = argparse.ArgumentParser(description="VT 資金部署策略回測")
    parser.add_argument("--period", type=int, default=5, help="布林期間")
    parser.add_argument("--std", type=float, default=1.75, help="標準差倍數")
    args = parser.parse_args(argv)

    df_full = load_data("VT", start=None, end=None)
    report = single_period_report(
        df_full=df_full, period=args.period, std_k=args.std, initial_capital=100000.0, dca_months=24
    )
    print(report)

if __name__ == "__main__":
    main()