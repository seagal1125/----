from __future__ import annotations

"""
MCP Stock Analyzer CLI (Python + yfinance)

提供工具：
- get_stock_info：股票基本資訊
- get_price_history：歷史股價
- get_summary_return：輕量版報酬率摘要
- calc_return：區間報酬率與 CAGR
- compare_returns：多標的區間報酬率 / CAGR 比較
- calc_risk_metrics：風險指標
- get_annual_returns：年度報酬率
"""

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf

# -----------------------------
# 小工具
# -----------------------------

def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df


def _annualize_days(n_days: int) -> float:
    # 以 365.25 計算年份，避免除以零
    return max(n_days, 1) / 365.25


def _nan_none(v):
    if v is None:
        return None
    try:
        if isinstance(v, float) and (math.isnan(v) or np.isnan(v)):
            return None
    except Exception:
        pass
    return v


def _fetch_history(
    ticker: str,
    period: Optional[str] = None,
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """取回歷史股價（優先使用 start/end；否則用 period）。"""
    if start or end:
        df = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=False, progress=False)
    else:
        period = period or "1y"
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)

    if df is None or df.empty:
        raise ValueError(f"無法取得 {ticker} 的歷史股價，請確認代號或時間區間是否正確。")

    df = _ensure_datetime_index(df)
    if "Adj Close" not in df.columns:
        df["Adj Close"] = df["Close"]
    return df


# -----------------------------
# 回傳資料結構
# -----------------------------

@dataclass
class ReturnStats:
    ticker: str
    start_date: str
    end_date: str
    start_price: float
    end_price: float
    total_return: float  # 累積報酬率（不含股利）
    cagr: float          # 複合年化報酬率

    def to_dict(self) -> Dict:
        d = asdict(self)
        d.update(
            {
                "total_return_pct": round(self.total_return * 100, 4),
                "cagr_pct": round(self.cagr * 100, 4),
            }
        )
        return d

def get_stock_info(ticker: str) -> Dict:
    """取得股票基本資訊（公司名稱、上市地、貨幣、可用區間等）。"""
    t = yf.Ticker(ticker)
    info = {}
    try:
        info = t.get_info()
    except Exception:
        info = {}

    try:
        fast = t.fast_info or {}
    except Exception:
        fast = {}

    out = {
        "ticker": ticker,
        "shortName": info.get("shortName") or info.get("longName"),
        "exchange": info.get("exchange") or fast.get("exchange"),
        "currency": info.get("currency") or fast.get("currency"),
        "quoteType": info.get("quoteType"),
        "marketCap": info.get("marketCap") or fast.get("market_cap"),
        "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh") or fast.get("year_high"),
        "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow") or fast.get("year_low"),
        "regularMarketPrice": info.get("regularMarketPrice") or fast.get("last_price"),
        "twoHundredDayAverage": info.get("twoHundredDayAverage"),
        "fiftyDayAverage": info.get("fiftyDayAverage"),
    }
    return {k: _nan_none(v) for k, v in out.items()}

def get_price_history(
    ticker: str,
    period: Optional[str] = "1y",
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
    full: bool = False,
    max_points: int = 1000,
) -> List[Dict]:
    """取得歷史股價。
    - 預設僅回傳「日期 + 收盤價（Adj Close）」，以節省 token。
    - `full=True` 時，回傳完整 OHLCV。
    - `max_points` 可限制回傳點數（>0 時生效）；若資料過多會做等距抽樣。
    """
    df = _fetch_history(ticker, period=period, interval=interval, start=start, end=end)

    # 等距抽樣（如果需要）
    if isinstance(max_points, int) and max_points > 0 and len(df) > max_points:
        idx = np.linspace(0, len(df) - 1, max_points).round().astype(int)
        df = df.iloc[idx]

    if not full:
        # 精簡輸出：日期 + Adj Close
        out = []
        for ts, row in df.iterrows():
            out.append({
                "date": ts.strftime("%Y-%m-%d"),
                "adj_close": _nan_none(row.get("Adj Close")),
            })
        return out

    # 完整輸出：OHLCV + Adj Close
    out = []
    for ts, row in df.iterrows():
        out.append(
            {
                "date": ts.strftime("%Y-%m-%d"),
                "open": _nan_none(row.get("Open")),
                "high": _nan_none(row.get("High")),
                "low": _nan_none(row.get("Low")),
                "close": _nan_none(row.get("Close")),
                "adj_close": _nan_none(row.get("Adj Close")),
                "volume": _nan_none(row.get("Volume")),
            }
        )
    return out

def get_summary_return(ticker: str, start: str, end: str) -> Dict:
    """輕量版報酬率摘要（只回必要統計），最省 token。
    回傳欄位：ticker, start_date, end_date, start_price, end_price, total_return_pct, cagr_pct
    """
    df = _fetch_history(ticker, start=start, end=end, interval="1d")
    adj = df["Adj Close"].dropna()
    if adj.empty:
        raise ValueError(f"{ticker} 在指定區間內無有效資料。")

    start_p = float(adj.iloc[0])
    end_p = float(adj.iloc[-1])
    total_ret = (end_p / start_p) - 1.0
    n_days = (adj.index[-1] - adj.index[0]).days
    years = _annualize_days(n_days)
    cagr = (end_p / start_p) ** (1.0 / years) - 1.0 if end_p > 0 and start_p > 0 else 0.0

    return {
        "ticker": ticker,
        "start_date": adj.index[0].strftime("%Y-%m-%d"),
        "end_date": adj.index[-1].strftime("%Y-%m-%d"),
        "start_price": round(start_p, 6),
        "end_price": round(end_p, 6),
        "total_return_pct": round(total_ret * 100, 4),
        "cagr_pct": round(cagr * 100, 4),
    }

def calc_return(ticker: str, start: str, end: str) -> Dict:
    """完整區間報酬率（數值 + 原始小數），適合要做後續計算的情境。"""
    df = _fetch_history(ticker, start=start, end=end, interval="1d")
    adj = df["Adj Close"].dropna()
    if adj.empty:
        raise ValueError(f"{ticker} 在指定區間內無有效資料。")

    start_price = float(adj.iloc[0])
    end_price = float(adj.iloc[-1])
    total_ret = (end_price / start_price) - 1.0

    n_days = (adj.index[-1] - adj.index[0]).days
    years = _annualize_days(n_days)
    cagr = (end_price / start_price) ** (1.0 / years) - 1.0 if end_price > 0 and start_price > 0 else 0.0

    stats = ReturnStats(
        ticker=ticker,
        start_date=adj.index[0].strftime("%Y-%m-%d"),
        end_date=adj.index[-1].strftime("%Y-%m-%d"),
        start_price=round(start_price, 6),
        end_price=round(end_price, 6),
        total_return=total_ret,
        cagr=cagr,
    )
    return stats.to_dict()

def compare_returns(tickers: List[str], start: str, end: str) -> Dict:
    """多標的區間報酬率比較，回傳每檔的 total_return 與 CAGR；同時附上依報酬率排序。"""
    results: List[Dict] = []
    for t in tickers:
        try:
            results.append(calc_return(t, start, end))
        except Exception as e:
            results.append({"ticker": t, "error": str(e)})
    sortable = [r for r in results if isinstance(r, dict) and "total_return" in r]
    ranking = sorted(sortable, key=lambda x: x["total_return"], reverse=True)
    return {"items": results, "ranking": ranking}

def calc_risk_metrics(
    ticker: str,
    start: str,
    end: str,
    benchmark: str = "SPY",
    risk_free_rate_annual: float = 0.0,
) -> Dict:
    """風險指標：年化波動、Sharpe、Beta、最大回撤、Downside Deviation。"""
    price = _fetch_history(ticker, start=start, end=end, interval="1d")["Adj Close"].dropna().squeeze()
    if price.empty:
        raise ValueError(f"{ticker} 在指定區間內無有效資料。")

    rets = price.pct_change().dropna()

    # 年化波動
    daily_std = float(rets.std())
    vol_annual = daily_std * math.sqrt(252.0)

    # Sharpe
    rf_daily = risk_free_rate_annual / 252.0
    avg_daily = float(rets.mean())
    sharpe = (avg_daily - rf_daily) / daily_std * math.sqrt(252.0) if daily_std > 0 else None

    # 最大回撤
    cum = (1 + rets).cumprod()
    running_max = cum.cummax()
    drawdown = cum / running_max - 1.0
    max_dd = float(drawdown.min())
    
    trough_date = drawdown.idxmin()
    peak_date = price.loc[:trough_date].idxmax()
    peak_price = price.loc[peak_date]
    trough_price = price.loc[trough_date]

    # Downside Deviation
    downside = rets[rets < 0]
    downside_std = float(downside.std()) if not downside.empty else 0.0
    downside_dev_annual = downside_std * math.sqrt(252.0)

    # Beta 相對基準
    if ticker == benchmark:
        beta = 1.0
    else:
        beta = None
        try:
            bench_price = _fetch_history(benchmark, start=start, end=end, interval="1d")["Adj Close"].dropna()
            bench_rets = bench_price.pct_change().dropna()
            
            rets.name = ticker
            bench_rets.name = benchmark

            combined_df = pd.concat([rets, bench_rets], axis=1)
            df2 = combined_df.dropna()

            if not df2.empty and benchmark in df2.columns and df2[benchmark].var() > 0:
                cov = df2[ticker].cov(df2[benchmark])
                var_b = df2[benchmark].var()
                beta = cov / var_b if var_b > 0 else None
        except Exception as e:
            print(f"Error calculating beta for {ticker}: {e}", file=sys.stderr)
            beta = None

    def r(v, n=6):
        if v is None:
            return None
        try:
            return round(float(v), n)
        except Exception:
            return v

    return {
        "ticker": ticker,
        "start": start,
        "end": end,
        "benchmark": benchmark,
        "risk_free_rate_annual": risk_free_rate_annual,
        "n_days": int((price.index[-1] - price.index[0]).days),
        "annual_volatility": r(vol_annual),
        "sharpe_ratio": r(sharpe),
        "beta": r(beta),
        "max_drawdown": r(max_dd),
        "max_drawdown_peak_date": peak_date.strftime('%Y-%m-%d'),
        "max_drawdown_peak_price": r(peak_price),
        "max_drawdown_trough_date": trough_date.strftime('%Y-%m-%d'),
        "max_drawdown_trough_price": r(trough_price),
        "downside_deviation_annual": r(downside_dev_annual),
    }

def get_annual_returns(ticker: str) -> List[Dict]:
    """取得指定標的自掛牌以來每年的報酬率。"""
    # 1. Fetch complete history
    df = _fetch_history(ticker, period="max", interval="1d")
    if df.empty:
        raise ValueError(f"無法取得 {ticker} 的歷史股價。")

    adj = df["Adj Close"].dropna()
    
    # Group by year
    yearly_groups = adj.groupby(adj.index.year)
    
    results = []
    for year, group in yearly_groups:
        if group.empty:
            continue
        
        # Calculate return for the year
        start_price = group.iloc[0]
        end_price = group.iloc[-1]
        yearly_return = (end_price / start_price) - 1.0
        
        results.append({
            "year": int(year), # Cast to standard int
            "start_date": group.index[0].strftime('%Y-%m-%d'),
            "end_date": group.index[-1].strftime('%Y-%m-%d'),
            "return_pct": float(round(yearly_return * 100, 4)) # Cast to standard float
        })
        
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock Analyzer CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # compare_returns command
    parser_compare = subparsers.add_parser("compare_returns")
    parser_compare.add_argument("--tickers", required=True, help="JSON string of a list of tickers")
    parser_compare.add_argument("--start", required=True)
    parser_compare.add_argument("--end", required=True)

    # calc_risk_metrics command
    parser_risk = subparsers.add_parser("calc_risk_metrics")
    parser_risk.add_argument("--ticker", required=True)
    parser_risk.add_argument("--start", required=True)
    parser_risk.add_argument("--end", required=True)
    parser_risk.add_argument("--benchmark", default="^TWII")

    # get_annual_returns command
    parser_annual = subparsers.add_parser("get_annual_returns")
    parser_annual.add_argument("--ticker", required=True)

    args = parser.parse_args()

    result = None
    if args.command == "compare_returns":
        tickers = json.loads(args.tickers)
        result = compare_returns(tickers=tickers, start=args.start, end=args.end)
    elif args.command == "calc_risk_metrics":
        result = calc_risk_metrics(ticker=args.ticker, start=args.start, end=args.end, benchmark=args.benchmark)
    elif args.command == "get_annual_returns":
        result = get_annual_returns(ticker=args.ticker)

    if result:
        print(json.dumps(result, indent=2))