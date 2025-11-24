
from __future__ import annotations
import math
import argparse
import json
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

# -----------------------------
# Part 1: Core Library Functions
# All core logic for stock analysis. These are pure functions.
# -----------------------------

def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df

def _annualize_days(n_days: int) -> float:
    return max(n_days, 1) / 365.25

def _nan_none(v):
    if v is None: return None
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
    if start or end:
        df = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=False, progress=False)
    else:
        period = period or "1y"
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)

    if df is None or df.empty:
        raise ValueError(f"Could not get historical data for {ticker}. Check ticker or date range.")

    df = _ensure_datetime_index(df)
    if "Adj Close" not in df.columns:
        df["Adj Close"] = df["Close"]
    return df

@dataclass
class ReturnStats:
    ticker: str
    start_date: str
    end_date: str
    start_price: float
    end_price: float
    total_return: float
    cagr: float

    def to_dict(self) -> Dict:
        d = asdict(self)
        d.update({
            "total_return_pct": round(self.total_return * 100, 4),
            "cagr_pct": round(self.cagr * 100, 4),
        })
        return d

def get_stock_info(ticker: str) -> Dict:
    t = yf.Ticker(ticker)
    info = t.get_info() or {}
    fast = t.fast_info or {}
    out = {
        "ticker": ticker,
        "shortName": info.get("shortName") or info.get("longName"),
        "exchange": info.get("exchange") or fast.get("exchange"),
        "currency": info.get("currency") or fast.get("currency"),
        "quoteType": info.get("quoteType"),
        "marketCap": info.get("marketCap") or fast.get("market_cap"),
    }
    return {k: _nan_none(v) for k, v in out.items()}

def calc_return(ticker: str, start: str, end: str) -> Dict:
    df = _fetch_history(ticker, start=start, end=end, interval="1d")
    adj = df["Adj Close"].dropna()
    if adj.empty:
        raise ValueError(f"{ticker} has no valid data in the specified range.")

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
    results: List[Dict] = []
    
    # 1. Batch download historical data for all tickers at once
    try:
        # yf.download() supports a list of tickers
        df_all = yf.download(
            tickers, 
            start=start, 
            end=end, 
            interval="1d", 
            auto_adjust=False, 
            progress=False
        )
        
        if df_all is None or df_all.empty:
            raise ValueError("Could not get historical data for tickers.")
            
        # Get "Adj Close" data. yfinance uses a MultiIndex when downloading multiple tickers.
        adj = df_all["Adj Close"]
        
    except Exception as e:
        # If batch download fails, report error for all tickers
        error_msg = str(e)
        for t in tickers:
            results.append({"ticker": t, "error": error_msg})
        return {"items": results, "ranking": []}

    # 2. Process each ticker from the downloaded data
    for t in tickers:
        try:
            # Select the "Adj Close" for the specific ticker
            # The DataFrame structure is different for a single ticker vs. multiple
            if len(tickers) == 1:
                ticker_adj = adj.dropna()
            else:
                ticker_adj = adj[t].dropna()

            if ticker_adj.empty:
                raise ValueError(f"No valid 'Adj Close' data found for {t} in range.")

            # --- Core logic from calc_return ---
            start_price = float(ticker_adj.iloc[0])
            end_price = float(ticker_adj.iloc[-1])
            total_ret = (end_price / start_price) - 1.0

            n_days = (ticker_adj.index[-1] - ticker_adj.index[0]).days
            years = _annualize_days(n_days)
            cagr = (end_price / start_price) ** (1.0 / years) - 1.0 if end_price > 0 and start_price > 0 else 0.0

            stats = ReturnStats(
                ticker=t,
                start_date=ticker_adj.index[0].strftime("%Y-%m-%d"),
                end_date=ticker_adj.index[-1].strftime("%Y-%m-%d"),
                start_price=round(start_price, 6),
                end_price=round(end_price, 6),
                total_return=total_ret,
                cagr=cagr,
            )
            results.append(stats.to_dict())
            # --- End of core logic ---

        except Exception as e:
            # If processing a single ticker fails (e.g., no data for the period)
            results.append({"ticker": t, "error": str(e)})

    # 3. Sort the results
    sortable = [r for r in results if "total_return" in r]
    ranking = sorted(sortable, key=lambda x: x["total_return"], reverse=True)
    return {"items": results, "ranking": ranking}

# -----------------------------
# Part 1.5: Sector/Industry Helpers for TWSE
# -----------------------------

def _read_twse_listed_csv(path: str) -> pd.DataFrame:
    """Read TWSE listed company basics CSV and return minimal mapping.

    Expected columns include: 公司代號, 公司名稱, 公司簡稱, 產業別, 已發行普通股數或TDR原股發行股數
    """
    df = pd.read_csv(path, encoding="utf-8-sig")
    cols = ["公司代號", "公司名稱", "公司簡稱", "產業別", "已發行普通股數或TDR原股發行股數"]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")
    # Normalize types
    df["公司代號"] = df["公司代號"].astype(str).str.zfill(4)
    df["產業別"] = df["產業別"].astype(str).str.zfill(2)
    # Shares as numeric
    df["已發行普通股數或TDR原股發行股數"] = pd.to_numeric(df["已發行普通股數或TDR原股發行股數"], errors="coerce")
    return df[cols].copy()

def _read_industry_codes(path: str) -> Dict[str, str]:
    """Return mapping from TWSE industry codes to human-readable names."""
    df = pd.read_csv(path, encoding="utf-8-sig")
    required = {"code", "name"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise ValueError(f"Industry code CSV missing columns: {missing}")
    df["code"] = df["code"].astype(str).str.zfill(2)
    df["name"] = df["name"].astype(str).str.strip()
    return dict(zip(df["code"], df["name"]))

def _build_tw_tickers(codes: List[str]) -> List[str]:
    """Append .TW suffix for TWSE tickers (ignoring OTC for now)."""
    return [f"{c}.TW" for c in codes]

def _latest_two_days_returns(df_adj: pd.DataFrame) -> pd.Series:
    """Compute last daily return per column from an Adj Close frame.

    Returns a Series indexed by ticker with percentage return (e.g., 0.0123 for +1.23%).
    """
    # Keep last 3 rows to be safe (in case of NaNs)
    tail = df_adj.tail(3)
    # For each column, find last two valid prices
    rets = {}
    for col in tail.columns:
        s = tail[col].dropna()
        if len(s) >= 2:
            prev, last = float(s.iloc[-2]), float(s.iloc[-1])
            if prev > 0 and last > 0:
                rets[col] = (last / prev) - 1.0
    return pd.Series(rets)

def _latest_two_prices(df_adj: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """Return (prev_close, last_close) per column from an Adj Close frame.

    If a column lacks two valid prices, it is omitted from both series.
    """
    tail = df_adj.tail(3)
    prev_map, last_map = {}, {}
    for col in tail.columns:
        s = tail[col].dropna()
        if len(s) >= 2:
            prev_map[col] = float(s.iloc[-2])
            last_map[col] = float(s.iloc[-1])
    return pd.Series(prev_map), pd.Series(last_map)


def _download_adj_close_batches(
    tickers: List[str],
    batch_size: int = 180,
    period: Optional[str] = "7d",
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """Download Adj Close prices for tickers in batches and return a combined DataFrame."""
    all_adj: List[pd.DataFrame] = []
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i : i + batch_size]
        try:
            params = {
                "interval": "1d",
                "auto_adjust": False,
                "progress": False,
                "group_by": "column",
            }
            if start or end:
                params["start"] = start
                params["end"] = end
            else:
                params["period"] = period or "7d"
            df_all = yf.download(batch, **params)
            if df_all is None or df_all.empty:
                continue
            if isinstance(df_all.columns, pd.MultiIndex):
                if "Adj Close" in df_all.columns.get_level_values(0):
                    adj = df_all["Adj Close"].copy()
                else:
                    adj = df_all["Close"].copy()
            else:
                adj = df_all.get("Adj Close") or df_all.get("Close")
                if isinstance(adj, pd.Series):
                    adj = adj.to_frame(batch[0])
            if adj is None or adj.empty:
                continue
            all_adj.append(adj)
        except Exception:
            continue
    if not all_adj:
        raise RuntimeError("No price data downloaded. Network access may be blocked.")
    adj_all = pd.concat(all_adj, axis=1)
    adj_all = adj_all.loc[:, ~adj_all.columns.duplicated()]
    return adj_all

def analyze_twse_today_by_sector(
    listed_csv_path: str,
    output_md_path: str,
    batch_size: int = 180,
    weighting: str = "cap",
    industry_codes_path: Optional[str] = None,
    target_date: Optional[str] = None,
    preloaded_prices: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Fetch latest daily returns for TWSE listed companies and summarize by industry.

    - Reads mapping from `listed_csv_path` (TWSE 上市公司基本資料.csv)
    - Downloads recent prices via yfinance in batches
    - Computes最後兩個可得交易日的報酬；若提供 target_date 則只取該日期（含日前一交易日）的資料
    - Groups by 產業別 (industry code) and produces summary stats
    - Writes a compact Markdown report to `output_md_path`

    Returns a tuple of (per_stock_df, per_industry_df)
    """
    base_df = _read_twse_listed_csv(listed_csv_path)
    industry_map: Dict[str, str] = {}
    if industry_codes_path:
        try:
            industry_map = _read_industry_codes(industry_codes_path)
        except Exception:
            industry_map = {}
    if industry_map:
        base_df["產業名稱"] = base_df["產業別"].map(industry_map)
    codes = base_df["公司代號"].tolist()
    tickers = _build_tw_tickers(codes)

    # Determine download window
    download_kwargs: Dict[str, str] = {"period": "7d"}
    target_ts: Optional[pd.Timestamp] = None
    if target_date:
        target_ts = pd.to_datetime(target_date).normalize()
        start_ts = target_ts - pd.Timedelta(days=10)
        end_ts = target_ts + pd.Timedelta(days=1)
        download_kwargs = {
            "start": start_ts.strftime("%Y-%m-%d"),
            "end": end_ts.strftime("%Y-%m-%d"),
        }

    if preloaded_prices is not None:
        adj_all = preloaded_prices.copy()
    else:
        adj_all = _download_adj_close_batches(
            tickers,
            batch_size=batch_size,
            period=download_kwargs.get("period"),
            start=download_kwargs.get("start"),
            end=download_kwargs.get("end"),
        )

    if target_ts is not None:
        adj_all = adj_all.loc[:target_ts]

    daily_ret = _latest_two_days_returns(adj_all)
    if daily_ret.empty:
        raise RuntimeError("Unable to compute returns from the downloaded data.")

    # Map ticker back to code
    code_from_ticker = {f"{c}.TW": c for c in codes}
    prev_px, last_px = _latest_two_prices(adj_all)
    per_stock = pd.DataFrame({
        "ticker": daily_ret.index,
        "日報酬": daily_ret.values,
        "公司代號": [code_from_ticker.get(t) for t in daily_ret.index],
        "昨收": [prev_px.get(t, np.nan) for t in daily_ret.index],
        "今收": [last_px.get(t, np.nan) for t in daily_ret.index],
    })
    per_stock = per_stock.merge(base_df, how="left", on="公司代號")
    # 市值（用昨收估算權重）
    per_stock["昨日市值"] = per_stock["已發行普通股數或TDR原股發行股數"].fillna(0) * per_stock["昨收"].fillna(0)

    # Aggregation
    g = per_stock.groupby("產業別")
    # 基礎統計
    per_industry = g["日報酬"].agg(["count", "mean", "median"]).reset_index()
    # 市值加權平均與貢獻度（使用昨日市值作權重）
    # 全市場權重母數
    total_cap_prev = float(per_stock["昨日市值"].sum())
    if total_cap_prev > 0:
        per_stock["權重_市值"] = per_stock["昨日市值"] / total_cap_prev
        per_stock["貢獻度"] = per_stock["權重_市值"] * per_stock["日報酬"]
    else:
        per_stock["權重_市值"] = 0.0
        per_stock["貢獻度"] = 0.0

    # 族群市值加權平均（分子=各股昨日市值×報酬，分母=各族群昨日市值）
    def _cap_weighted_mean(df_part: pd.DataFrame) -> float:
        cap = float(df_part["昨日市值"].sum())
        if cap <= 0:
            return float("nan")
        return float((df_part["日報酬"] * df_part["昨日市值"]).sum() / cap)

    per_industry["cap_mean"] = g.apply(_cap_weighted_mean).values
    # 族群對大盤日漲幅的貢獻（加總 權重×報酬）
    per_industry["cap_contrib"] = g["貢獻度"].sum().values
    if industry_map:
        per_industry["產業名稱"] = per_industry["產業別"].map(industry_map)

    # 排序：預設依市值加權貢獻度排序，再備用等權平均
    sort_col = "cap_contrib" if weighting == "cap" else "mean"
    per_industry = per_industry.sort_values(by=sort_col, ascending=False)

    # Compose Markdown
    lines: List[str] = []
    lines.append("# 台股族群當日漲幅分析（等權/市值加權）")
    lines.append("")
    lines.append("- 方法：等權與市值加權（用昨收×已發行股數近似市值）兩種；依 產業別 分組。")
    lines.append("- 資料：yfinance 近兩個交易日收盤價；公司基本資料與股數取自上市公司基本資料.csv；產業名稱對照表參考 industry_codes.csv。")
    # 整體大盤（等權 vs 市值加權）
    overall_eq = float(per_stock["日報酬"].mean()) if len(per_stock) else float("nan")
    overall_cap = float((per_stock["日報酬"] * per_stock["昨日市值"]).sum() / total_cap_prev) if total_cap_prev>0 else float("nan")
    lines.append(f"- 大盤等權日漲幅：{overall_eq*100:.2f}% ；市值加權日漲幅：{overall_cap*100:.2f}%")
    lines.append("")
    lines.append("## 族群（前 10）：市值加權貢獻度")
    def _industry_label(code: str) -> str:
        name = industry_map.get(code)
        return f"{code}-{name}" if name else str(code)

    def _fmt_pct(value: float) -> str:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return "N/A"
        return f"{value*100:.2f}%"

    head = per_industry.head(10)
    for _, r in head.iterrows():
        mean_eq = r.get("mean", float("nan"))
        mean_cap = r.get("cap_mean", float("nan"))
        contrib = r.get("cap_contrib", float("nan"))
        lines.append(
            f"- 產業別 {_industry_label(r['產業別'])}: 等權均值 {mean_eq*100:.2f}%、市值加權均值 {mean_cap*100:.2f}%、對大盤貢獻 {contrib*100:.2f}%、樣本 {int(r['count'])}"
        )
    lines.append("")
    lines.append("## 族群（後 10）：市值加權貢獻度")
    tail = per_industry.tail(10)
    for _, r in tail.iterrows():
        mean_eq = r.get("mean", float("nan"))
        mean_cap = r.get("cap_mean", float("nan"))
        contrib = r.get("cap_contrib", float("nan"))
        lines.append(
            f"- 產業別 {_industry_label(r['產業別'])}: 等權均值 {mean_eq*100:.2f}%、市值加權均值 {mean_cap*100:.2f}%、對大盤貢獻 {contrib*100:.2f}%、樣本 {int(r['count'])}"
        )
    lines.append("")

    # Summary of top/bottom sectors and stocks
    def _format_sector_line(row):
        return (
            f"- {_industry_label(row['產業別'])}: 市值貢獻 {_fmt_pct(row['cap_contrib'])}、"
            f"市值加權 {_fmt_pct(row['cap_mean'])}、等權 {_fmt_pct(row['mean'])}"
        )

    def _format_stock_line(row):
        return (
            f"- {row['公司名稱']} ({row['公司代號']} / {row.get('產業名稱', '')}): "
            f"日報酬 {_fmt_pct(row['日報酬'])}、權重 {_fmt_pct(row['權重_市值'])}、貢獻 {_fmt_pct(row['貢獻度'])}"
        )

    pos_sectors = per_industry.sort_values("cap_contrib", ascending=False).head(3)
    neg_sectors = per_industry.sort_values("cap_contrib", ascending=True).head(3)
    lines.append("## 今日撐盤族群（貢獻 Top 3）")
    for _, row in pos_sectors.iterrows():
        lines.append(_format_sector_line(row))
    lines.append("")
    lines.append("## 今日拖累族群（貢獻 Bottom 3）")
    for _, row in neg_sectors.iterrows():
        lines.append(_format_sector_line(row))
    lines.append("")

    per_stock_sorted = per_stock.sort_values("貢獻度", ascending=False)
    pos_stocks = per_stock_sorted.head(5)
    neg_stocks = per_stock_sorted.tail(5).sort_values("貢獻度")
    lines.append("## 權值股貢獻（Top 5）")
    for _, row in pos_stocks.iterrows():
        lines.append(_format_stock_line(row))
    lines.append("")
    lines.append("## 權值股拖累（Bottom 5）")
    for _, row in neg_stocks.iterrows():
        lines.append(_format_stock_line(row))
    lines.append("")

    # Save
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return per_stock, per_industry


def download_twse_price_history(
    listed_csv_path: str,
    start_date: str,
    end_date: str,
    batch_size: int = 180,
) -> pd.DataFrame:
    """Download Adj Close prices for all TWSE tickers between start_date and end_date (inclusive)."""
    base_df = _read_twse_listed_csv(listed_csv_path)
    tickers = _build_tw_tickers(base_df["公司代號"].tolist())
    adj_all = _download_adj_close_batches(
        tickers,
        batch_size=batch_size,
        start=start_date,
        end=end_date,
        period=None,
    )
    return adj_all

# -----------------------------
# Part 2: Application Entry Points (CLI and MCP Server)
# -----------------------------

def run_mcp_server():
    """Initializes and runs the MCP server."""
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("stock-analyzer")

    # Dynamically wrap and register library functions as MCP tools
    @mcp.tool()
    def mcp_get_stock_info(ticker: str) -> Dict:
        return get_stock_info(ticker)

    @mcp.tool()
    def mcp_compare_returns(tickers: List[str], start: str, end: str) -> Dict:
        return compare_returns(tickers, start, end)
    
    @mcp.tool()
    def mcp_calc_return(ticker: str, start: str, end: str) -> Dict:
        return calc_return(ticker, start, end)

    print("Starting MCP server on stdio...", flush=True)
    mcp.run(transport="stdio")

def main():
    """Main function to run the CLI."""
    parser = argparse.ArgumentParser(
        description="A stock analysis tool that can be run as a CLI or MCP server.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Server Command ---
    subparsers.add_parser("server", help="Run the application as an MCP server.")

    # --- CLI Commands ---
    # --- get_stock_info ---
    info_parser = subparsers.add_parser("get_stock_info", help="Get basic information for a stock.")
    info_parser.add_argument("ticker", help="The stock ticker symbol (e.g., AAPL, 2330.TW).")

    # --- compare_returns ---
    compare_parser = subparsers.add_parser("compare_returns", help="Compare the performance of multiple stocks over a period.")
    compare_parser.add_argument("--tickers", nargs="+", required=True, help="A list of stock ticker symbols.")
    compare_parser.add_argument("--start", required=True, help="Start date in YYYY-MM-DD format.")
    compare_parser.add_argument("--end", required=True, help="End date in YYYY-MM-DD format.")

    # --- analyze_twse_today_by_sector ---
    # Note: argparse uses add_parser (not add_subparser)
    sector_parser = subparsers.add_parser(
        "analyze_twse_today_by_sector",
        help="Fetch latest returns for TWSE stocks and summarize by industry."
    )
    sector_parser.add_argument("--listed_csv", required=True, help="Path to 上市公司基本資料.csv")
    sector_parser.add_argument("--output_md", required=True, help="Output Markdown report path")
    sector_parser.add_argument("--batch_size", type=int, default=180, help="Batch size for yfinance download")
    sector_parser.add_argument("--weighting", choices=["equal", "cap"], default="cap", help="Aggregation weighting: equal or market-cap weighted")
    sector_parser.add_argument("--industry_codes", help="Path to industry_codes.csv for friendly labels")
    sector_parser.add_argument("--date", help="Target date in YYYY-MM-DD; defaults to latest")

    args = parser.parse_args()

    try:
        if args.command == "server":
            run_mcp_server()
        elif args.command == "get_stock_info":
            result = get_stock_info(args.ticker)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "compare_returns":
            result = compare_returns(tickers=args.tickers, start=args.start, end=args.end)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "analyze_twse_today_by_sector":
            per_stock, per_industry = analyze_twse_today_by_sector(
                listed_csv_path=args.listed_csv,
                output_md_path=args.output_md,
                batch_size=args.batch_size,
                weighting=args.weighting,
                industry_codes_path=args.industry_codes,
                target_date=args.date,
            )
            print(json.dumps({
                "stocks": int(len(per_stock)),
                "industries": int(len(per_industry)),
                "top_industry": per_industry.iloc[0].to_dict() if not per_industry.empty else None,
            }, ensure_ascii=False, indent=2))
        else:
            parser.print_help()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
