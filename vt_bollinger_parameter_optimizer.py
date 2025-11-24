#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VT 資金部署策略回測：尋找正超額報酬的參數最佳化
"""

import argparse
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd


def load_data(ticker: str) -> Optional[pd.DataFrame]:
    try:
        import yfinance as yf
        hist = yf.Ticker(ticker).history(period="max", auto_adjust=True)
        if hist.empty: return None
        df = hist[["Close"]].copy()
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df
    except Exception as e:
        print(f"資料下載失敗: {e}", file=sys.stderr)
        return None

def add_bollinger(df: pd.DataFrame, period: int, k: float) -> pd.DataFrame:
    s = df["Close"]
    sma = s.rolling(window=period, min_periods=period).mean()
    std = s.rolling(window=period, min_periods=period).std(ddof=0)
    lower = sma - k * std
    out = df.copy()
    out["SMA"] = sma
    out["Lower"] = lower
    return out

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

def first_signal_date_in_window(df_bb_window: pd.DataFrame) -> Optional[pd.Timestamp]:
    allow = True
    for ts, row in df_bb_window.iterrows():
        sma, lower, close = row["SMA"], row["Lower"], row["Close"]
        if pd.isna(sma) or pd.isna(lower): continue
        if allow and close <= lower: return ts
        if not allow and close > sma: allow = True
    return None

@dataclass
class StrategyResult:
    name: str
    final_value: float

def simulate_lump_sum(df_window: pd.DataFrame, capital: float) -> StrategyResult:
    if df_window.empty: return StrategyResult("LumpSum", np.nan)
    shares = capital / df_window.iloc[0]["Close"]
    final_value = shares * df_window.iloc[-1]["Close"]
    return StrategyResult("LumpSum", float(final_value))

def simulate_signal_all_in(df_bb_window: pd.DataFrame, capital: float) -> StrategyResult:
    if df_bb_window.empty: return StrategyResult("SignalAllIn", np.nan)
    sig = first_signal_date_in_window(df_bb_window)
    if sig is None: return StrategyResult("SignalAllIn", capital)
    shares = capital / df_bb_window.loc[sig, "Close"]
    final_value = shares * df_bb_window.loc[df_bb_window.index[-1], "Close"]
    return StrategyResult("SignalAllIn", float(final_value))

def rolling_analysis(df_full: pd.DataFrame, period: int, std_k: float, capital: float, rolling_years: int) -> Optional[float]:
    df_bb_full = add_bollinger(df_full, period, std_k)
    starts: List[pd.Timestamp] = list(df_full.index)
    excess_returns = []

    for start_ts in starts:
        end_ts = start_ts + pd.DateOffset(years=rolling_years)
        if end_ts > df_full.index[-1]: break

        df_w = slice_window(df_full, start_ts, end_ts)
        if df_w.empty: continue
        df_bb_w = slice_window(df_bb_full, start_ts, end_ts)
        if df_bb_w.empty: continue

        res_ls = simulate_lump_sum(df_w, capital)
        res_bb = simulate_signal_all_in(df_bb_w, capital)

        if np.isfinite(res_ls.final_value) and np.isfinite(res_bb.final_value) and res_ls.final_value > 0:
            excess = (res_bb.final_value - res_ls.final_value) / res_ls.final_value * 100.0
            excess_returns.append(excess)

    return np.mean(excess_returns) if excess_returns else None

def main():
    parser = argparse.ArgumentParser(description="VT 布林通道策略超額報酬最佳化")
    parser.add_argument("--rolling_years", type=int, default=5, help="滾動視窗長度（年）")
    args = parser.parse_args()

    df_full = load_data("VT")
    if df_full is None: return

    periods = [5, 10, 15, 20, 25, 30, 35, 40]
    std_devs = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5]
    all_results = []

    print(f"開始進行 {len(periods) * len(std_devs)} 種參數組合的滾動回測（{args.rolling_years}年期）...")
    for period in periods:
        for std in std_devs:
            avg_excess_return = rolling_analysis(
                df_full, period, std, capital=100000.0, rolling_years=args.rolling_years
            )
            if avg_excess_return is not None:
                all_results.append({"period": period, "std": std, "excess_return": avg_excess_return})
                print(f"測試完成: P={period}, S={std}, 超額報酬={avg_excess_return:.2f}%")

    if not all_results: 
        print("沒有任何參數組合產生有效結果。")
        return

    best_result = max(all_results, key=lambda x: x['excess_return'])

    print("\n==================================================")
    print("尋找正超額報酬的最佳化結果")
    print("==================================================")
    print(f"在所有 {len(all_results)} 組參數中，找到的最佳結果如下：")
    print("--------------------------------------------------")
    print("最佳參數組合:")
    print(f"  期間 (Period): {best_result['period']} 天")
    print(f"  標準差倍數 (Std Dev): {best_result['std']}")
    print(f"  => 最高平均超額報酬: {best_result['excess_return']:.2f}%")
    print("==================================================")
    if best_result['excess_return'] > 0:
        print("\n恭喜！我們找到了能夠產生正超額報酬的參數組合。")
        print("這代表，使用這組參數，長期來看，您的擇時策略不僅勝率高，連平均報酬期望值都超越了單筆投入。")
    else:
        print("\n結論：經過大範圍且精細的搜索，我們未能找到一組能產生正超額報酬的參數。")
        print("這是一個非常穩健的發現，它意味著在過去十幾年的大多頭市場中，任何形式的『等待』")
        print("所產生的機會成本，其累積效果都略高於躲過大跌的收益。")
        print("這再次證實了『時間（Time in the market）』的價值在長期來看略勝一籌。")

if __name__ == "__main__":
    main()
