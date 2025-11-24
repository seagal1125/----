#!/usr/bin/env python3
"""Batch runner to backfill TWSE daily reports across trading days."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional

import pandas as pd
import yfinance as yf

from daily_sector_report import run_reports


def _list_trading_days(year: int, through: Optional[str]) -> List[date]:
    if through:
        through_dt = pd.to_datetime(through).date()
    else:
        today = date.today()
        through_dt = date(year, 12, 31)
        if year == today.year and today < through_dt:
            through_dt = today

    end_plus = through_dt + timedelta(days=2)
    hist = yf.download(
        "^TWII",
        start=f"{year}-01-01",
        end=end_plus.strftime("%Y-%m-%d"),
        interval="1d",
        auto_adjust=False,
        progress=False,
    )
    if hist.empty:
        raise RuntimeError("Unable to retrieve TWII trading calendar from yfinance.")
    trading_days = [idx.date() for idx in hist.index if idx.year == year and idx.date() <= through_dt]
    return trading_days


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch-generate TWSE reports for each trading day in a year.")
    parser.add_argument("--year", type=int, default=date.today().year, help="Target year of trading days")
    parser.add_argument("--through", help="Optional YYYY-MM-DD to stop processing earlier")
    parser.add_argument("--listed-csv", default="data/上市公司基本資料.csv")
    parser.add_argument("--industry-csv", default="data/industry_codes.csv")
    parser.add_argument("--analysis-dir", default="分析報告")
    parser.add_argument("--top-n", type=int, default=3)
    parser.add_argument("--stocks-per-sector", type=int, default=5)
    parser.add_argument("--max-dates", type=int, help="Limit number of trading days processed (for testing)")
    args = parser.parse_args()

    analysis_dir = Path(args.analysis_dir)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    trading_days = _list_trading_days(year=args.year, through=args.through)
    if args.max_dates is not None:
        trading_days = trading_days[: args.max_dates]

    for day in trading_days:
        run_reports(
            target_date=day.strftime("%Y-%m-%d"),
            listed_csv=args.listed_csv,
            industry_csv=args.industry_csv,
            analysis_dir=analysis_dir,
            top_n=args.top_n,
            stocks_per_sector=args.stocks_per_sector,
        )


if __name__ == "__main__":
    main()
