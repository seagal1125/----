from __future__ import annotations

"""
MCP Stock Analyzer Server (Python + yfinance)

（精簡傳輸量版本）
- 避免把整段 OHLCV 都丟回去吃 token：
  - `get_price_history` 預設只回「日期+收盤價」，除非 `full=True` 才回傳完整 OHLCV。
  - 新增 `get_summary_return`：只回必要統計（start/end 價、總報酬率、CAGR）。

提供工具：
- get_stock_info：股票基本資訊
- get_price_history：歷史股價（預設精簡輸出；支援 full=True）
- get_summary_return：輕量版報酬率摘要
- calc_return：區間報酬率與 CAGR（含精確時間對齊）
- compare_returns：多標的區間報酬率 / CAGR 比較
- calc_risk_metrics：風險指標（年化波動、Sharpe、Beta、最大回撤、Downside）

需求：
    pip install fastmcp yfinance pandas numpy

啟動：
    python mcp_stock.py

Claude 設定（claude_mcp.json 範例）：
{
  "mcpServers": {
    "stock-analyzer": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/TO/mcp_stock.py"]
    }
  }
}
"""

import math
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf
from mcp.server.fastmcp import FastMCP

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


# -----------------------------
# MCP 伺服器
# -----------------------------

mcp = FastMCP("stock-analyzer")


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
def calc_risk_metrics(
    ticker: str,
    start: str,
    end: str,
    benchmark: str = "SPY",
    risk_free_rate_annual: float = 0.0,
) -> Dict:
    """風險指標：年化波動、Sharpe、Beta、最大回撤、Downside Deviation。"""
    price = _fetch_history(ticker, start=start, end=end, interval="1d")["Adj Close"].dropna()
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

    # Downside Deviation
    downside = rets[rets < 0]
    downside_std = float(downside.std()) if not downside.empty else 0.0
    downside_dev_annual = downside_std * math.sqrt(252.0)

    # Beta 相對基準
    beta = None
    try:
        bench_price = _fetch_history(benchmark, start=start, end=end, interval="1d")["Adj Close"].dropna()
        bench_rets = bench_price.pct_change().dropna()
        df2 = pd.DataFrame({"asset": rets, "bench": bench_rets}).dropna()
        if not df2.empty and df2["bench"].var() > 0:
            cov = float(np.cov(df2["asset"], df2["bench"], ddof=1)[0][1])
            var_b = float(np.var(df2["bench"], ddof=1))
            beta = cov / var_b if var_b > 0 else None
    except Exception:
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
        "downside_deviation_annual": r(downside_dev_annual),
    }


@mcp.tool()
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


@mcp.tool()
def calculate_portfolio_performance(
    allocations: Dict[str, float], 
    start: Optional[str] = None, 
    end: Optional[str] = None, 
    period: Optional[str] = "max",
    risk_free_rate_annual: float = 0.0,
) -> Dict:
    """
    Calculates the performance of a portfolio with specified allocations.
    Returns overall CAGR, risk metrics, and annual returns for the portfolio.
    """
    if not allocations or not isinstance(allocations, dict):
        raise ValueError("Allocations must be a non-empty dictionary of ticker: weight.")
    
    if not math.isclose(sum(allocations.values()), 1.0):
        raise ValueError(f"Allocation weights must sum to 1.0. Current sum is {sum(allocations.values())}.")

    # 1. Fetch and align data
    portfolio_df = pd.DataFrame()
    for ticker in allocations.keys():
        df = _fetch_history(ticker, start=start, end=end, period=period, interval="1d")
        portfolio_df[ticker] = df["Adj Close"]
    
    # Drop rows with any missing values
    portfolio_df = portfolio_df.dropna()
    
    if portfolio_df.empty:
        raise ValueError("Could not find overlapping date range for the given tickers.")

    # 2. Calculate portfolio daily returns
    daily_returns = portfolio_df.pct_change().dropna()
    
    # Get weights in the same order as columns
    weights = np.array([allocations[ticker] for ticker in daily_returns.columns])
    
    # Calculate weighted daily portfolio returns
    portfolio_daily_returns = daily_returns.dot(weights)
    portfolio_daily_returns.name = "portfolio"

    # --- 3. Calculate Overall Metrics ---
    
    # CAGR
    n_days = (portfolio_daily_returns.index[-1] - portfolio_daily_returns.index[0]).days
    years = _annualize_days(n_days)
    cumulative_return = (1 + portfolio_daily_returns).prod() - 1
    cagr = (1 + cumulative_return) ** (1.0 / years) - 1.0 if years > 0 else 0.0

    # Annual Volatility
    vol_annual = float(portfolio_daily_returns.std()) * math.sqrt(252.0)

    # Sharpe Ratio
    rf_daily = risk_free_rate_annual / 252.0
    avg_daily_ret = float(portfolio_daily_returns.mean())
    sharpe = (avg_daily_ret - rf_daily) / float(portfolio_daily_returns.std()) * math.sqrt(252.0) if portfolio_daily_returns.std() > 0 else None

    # Max Drawdown
    cum_returns = (1 + portfolio_daily_returns).cumprod()
    running_max = cum_returns.cummax()
    drawdown = cum_returns / running_max - 1.0
    max_dd = float(drawdown.min())

    # --- 4. Calculate Annual Returns ---
    yearly_groups = portfolio_daily_returns.groupby(portfolio_daily_returns.index.year)
    annual_returns_list = []
    for year, group in yearly_groups:
        if group.empty:
            continue
        
        yearly_cum_ret = (1 + group).prod() - 1.0
        annual_returns_list.append({
            "year": int(year),
            "return_pct": float(round(yearly_cum_ret * 100, 4))
        })

    # --- 5. Consolidate and Return ---
    def r(v, n=6):
        return round(v, n) if isinstance(v, (int, float)) else v

    return {
        "portfolio_summary": {
            "start_date": portfolio_df.index[0].strftime('%Y-%m-%d'),
            "end_date": portfolio_df.index[-1].strftime('%Y-%m-%d'),
            "cagr_pct": r(cagr * 100),
            "annual_volatility_pct": r(vol_annual * 100),
            "sharpe_ratio": r(sharpe),
            "max_drawdown_pct": r(max_dd * 100),
        },
        "annual_returns": annual_returns_list
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
