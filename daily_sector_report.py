#!/usr/bin/env python3
"""Automate generation of daily TWSE sector and stock reports.

This script encapsulates the three manual steps described in
data/日報酬Prompt/:
- 1-stock_analyzer_prompt_20251110.txt
- 2-top_sector_contrib_prompt_20251110.txt
- 3-outperformers_prompt_20251110.txt

It reuses stock_analyzer.analyze_twse_today_by_sector to download prices
and then emits three Markdown files under 分析報告/ with today's date.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from stock_analyzer import analyze_twse_today_by_sector, download_twse_price_history


SECTOR_REASON_HINTS: Dict[str, str] = {
    "半導體": "AI 晶片、HBM 與高階製程需求持續升溫。",
    "電腦及週邊設備": "AI 伺服器與機櫃升級帶動 ODM 與散熱需求。",
    "電子零組件": "資料中心電源、PCB 與散熱零組件出貨動能強勁。",
    "其他電子": "車用/伺服器線束與網通設備訂單穩定成長。",
    "油電燃氣": "油價企穩推動煉油與石化利差改善。",
    "金融保險": "債券殖利率回落與利差收益穩定。",
}


def fmt_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _resolve_sector_reason(name: str | None) -> str:
    if not name:
        return "資金集中在龍頭股，族群內主要權值股同步上漲。"
    for key, reason in SECTOR_REASON_HINTS.items():
        if key in name:
            return reason
    return "資金集中在龍頭股，族群內主要權值股同步上漲。"


def _ensure_columns(per_stock: pd.DataFrame) -> pd.DataFrame:
    defaults = {
        "日報酬": 0.0,
        "權重_市值": 0.0,
        "貢獻度": 0.0,
        "產業名稱": "",
    }
    for col, default in defaults.items():
        if col not in per_stock.columns:
            per_stock[col] = default
        per_stock[col] = per_stock[col].fillna(default)
    return per_stock


def generate_sector_detail_report(
    per_stock: pd.DataFrame,
    per_industry: pd.DataFrame,
    output_path: Path,
    top_n: int,
    stocks_per_sector: int,
    display_date: str,
) -> None:
    top_sectors = per_industry.sort_values("cap_contrib", ascending=False).head(top_n)

    lines = [f"# 台股族群漲幅解讀（{display_date}）", "", "## 族群概覽"]
    for _, row in top_sectors.iterrows():
        label = f"{row['產業別']}-{row.get('產業名稱', '')}".rstrip("-")
        lines.append(
            f"- {label}: 等權 {fmt_pct(row['mean'])}、市值加權 {fmt_pct(row['cap_mean'])}、對大盤貢獻 {fmt_pct(row['cap_contrib'])}"
        )

    for _, row in top_sectors.iterrows():
        code = row["產業別"]
        name = row.get("產業名稱", "")
        label = f"{code}-{name}".rstrip("-")
        lines.append("\n### " + label)
        sector_df = (
            per_stock[per_stock["產業別"] == code]
            .sort_values("貢獻度", ascending=False)
            .head(stocks_per_sector)
        )
        if sector_df.empty:
            lines.append("(無資料)")
            continue
        lines.append("| 公司代號 | 公司名稱 | 日報酬 | 市值權重 | 指數貢獻 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for _, stock in sector_df.iterrows():
            lines.append(
                f"| {stock['公司代號']} | {stock['公司名稱']} | {fmt_pct(stock['日報酬'])} | "
                f"{fmt_pct(stock['權重_市值'])} | {fmt_pct(stock['貢獻度'])} |"
            )
        leaders = ", ".join(
            f"{stock['公司名稱']}({fmt_pct(stock['日報酬'])})" for _, stock in sector_df.head(3).iterrows()
        )
        lines.append(
            f"**解讀**：{_resolve_sector_reason(name)} 主要由 {leaders} 帶動，放大指數貢獻。"
        )

    lines.append("\n## 後續觀察")
    lines.append("- 留意美股 AI 與記憶體指標走勢，決定半導體與伺服器供應鏈能否續強。")
    lines.append("- 若油價或美元波動加劇，電子權值股與傳產之間的輪動可能加速，建議保持分散配置。")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def generate_outperform_report(per_stock: pd.DataFrame, output_path: Path, display_date: str) -> None:
    overall_cap = float(per_stock["貢獻度"].sum())
    outperform = per_stock[per_stock["日報酬"] > overall_cap]
    outperform = outperform.sort_values("貢獻度", ascending=False).head(10)

    lines = [
        f"# 台股贏過大盤個股觀察（{display_date}）",
        f"- 大盤市值加權日漲幅：約 {fmt_pct(overall_cap)}，以下為漲幅高於大盤且對指數貢獻最大的 10 檔。",
        "",
        "| 排名 | 公司代號 | 公司名稱 | 產業 | 日報酬 | 市值權重 | 指數貢獻 | 為何能贏過大盤 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for idx, (_, row) in enumerate(outperform.iterrows(), start=1):
        reason = _resolve_sector_reason(row.get("產業名稱", ""))
        reason += f" {row['公司名稱']}單日{fmt_pct(row['日報酬'])}、對大盤貢獻{fmt_pct(row['貢獻度'])}。"
        lines.append(
            f"| {idx} | {row['公司代號']} | {row['公司名稱']} | {row.get('產業名稱', '')} | "
            f"{fmt_pct(row['日報酬'])} | {fmt_pct(row['權重_市值'])} | {fmt_pct(row['貢獻度'])} | {reason} |"
        )

    lines.append("\n## 觀察重點")
    lines.append("- AI 伺服器與半導體鏈仍占多數，市場集中度高，需留意美股科技股回檔風險。")
    lines.append("- 傳產與能源股若受原物料價格支撐，可能成為下一波補漲族群，可作為防守配置。")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def run_reports(
    target_date: Optional[str],
    listed_csv: str,
    industry_csv: str,
    analysis_dir: Path,
    top_n: int,
    stocks_per_sector: int,
    preloaded_prices: Optional[pd.DataFrame] = None,
) -> None:
    if target_date:
        date_obj = pd.to_datetime(target_date).date()
    else:
        date_obj = datetime.now().date()
    date_token = date_obj.strftime("%Y%m%d")
    display_date = date_obj.strftime("%Y-%m-%d")

    sector_md_path = analysis_dir / f"台股族群漲幅分析_{date_token}.md"

    per_stock, per_industry = analyze_twse_today_by_sector(
        listed_csv_path=listed_csv,
        output_md_path=str(sector_md_path),
        industry_codes_path=industry_csv,
        target_date=display_date,
        preloaded_prices=preloaded_prices,
    )

    per_stock = _ensure_columns(per_stock)
    per_industry = per_industry.fillna({"mean": 0.0, "cap_mean": 0.0, "cap_contrib": 0.0, "產業名稱": ""})

    detail_path = analysis_dir / f"台股族群漲幅分析_{date_token}_族群個股解讀.md"
    generate_sector_detail_report(
        per_stock=per_stock,
        per_industry=per_industry,
        output_path=detail_path,
        top_n=top_n,
        stocks_per_sector=stocks_per_sector,
        display_date=display_date,
    )

    outperform_path = analysis_dir / f"台股贏過大盤個股觀察_{date_token}.md"
    generate_outperform_report(per_stock=per_stock, output_path=outperform_path, display_date=display_date)


def run_batch(
    start_date: str,
    end_date: str,
    listed_csv: str,
    industry_csv: str,
    analysis_dir: Path,
    top_n: int,
    stocks_per_sector: int,
    batch_size: int,
) -> None:
    start_ts = pd.to_datetime(start_date).normalize()
    end_ts = pd.to_datetime(end_date).normalize()
    buffer_start = (start_ts - pd.Timedelta(days=10)).strftime("%Y-%m-%d")
    buffer_end = (end_ts + pd.Timedelta(days=2)).strftime("%Y-%m-%d")
    prices = download_twse_price_history(
        listed_csv_path=listed_csv,
        start_date=buffer_start,
        end_date=buffer_end,
        batch_size=batch_size,
    )
    prices.index = pd.to_datetime(prices.index)
    trading_days = [
        idx for idx in prices.index.unique()
        if start_ts <= idx <= end_ts
    ]
    trading_days.sort()
    for day in trading_days:
        run_reports(
            target_date=day.strftime("%Y-%m-%d"),
            listed_csv=listed_csv,
            industry_csv=industry_csv,
            analysis_dir=analysis_dir,
            top_n=top_n,
            stocks_per_sector=stocks_per_sector,
            preloaded_prices=prices,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate daily TWSE sector and stock reports.")
    parser.add_argument("--listed-csv", default="data/上市公司基本資料.csv", help="Path to 上市公司基本資料.csv")
    parser.add_argument("--industry-csv", default="data/industry_codes.csv", help="Path to industry_codes.csv")
    parser.add_argument("--analysis-dir", default="分析報告", help="Directory for output Markdown files")
    parser.add_argument("--top-n", type=int, default=3, help="Number of top sectors to analyze in detail")
    parser.add_argument("--stocks-per-sector", type=int, default=5, help="Stocks to list per sector")
    parser.add_argument("--date", help="Target date YYYY-MM-DD; defaults to today")
    parser.add_argument("--batch_start", help="YYYY-MM-DD start date for batch processing")
    parser.add_argument("--batch_end", help="YYYY-MM-DD end date for batch processing")
    parser.add_argument("--batch_size", type=int, default=180, help="Batch size for price downloads")

    args = parser.parse_args()

    analysis_dir = Path(args.analysis_dir)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    if args.batch_start and args.batch_end:
        run_batch(
            start_date=args.batch_start,
            end_date=args.batch_end,
            listed_csv=args.listed_csv,
            industry_csv=args.industry_csv,
            analysis_dir=analysis_dir,
            top_n=args.top_n,
            stocks_per_sector=args.stocks_per_sector,
            batch_size=args.batch_size,
        )
    else:
        run_reports(
            target_date=args.date,
            listed_csv=args.listed_csv,
            industry_csv=args.industry_csv,
            analysis_dir=analysis_dir,
            top_n=args.top_n,
            stocks_per_sector=args.stocks_per_sector,
        )


if __name__ == "__main__":
    main()
