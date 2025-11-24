#!/usr/bin/env python3
"""
Compute TWD-converted cost, value, profit and ROI for USD-denominated ETFs.

Usage examples:
  python3 calc_vt_ief_report.py \
    --rate 29.26 \
    --asset VT:174357.2:191288.3 \
    --asset IEF:81931.1:84224.1

If no args are provided, defaults to the values you shared.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List


@dataclass
class AssetUSD:
    symbol: str
    cost_usd: float
    value_usd: float

    @property
    def profit_usd(self) -> float:
        return self.value_usd - self.cost_usd

    @property
    def roi(self) -> float:
        return (self.profit_usd / self.cost_usd) if self.cost_usd else 0.0


def parse_asset(arg: str) -> AssetUSD:
    try:
        sym, cost, value = arg.split(":", 2)
        return AssetUSD(sym.strip(), float(cost), float(value))
    except Exception:
        raise argparse.ArgumentTypeError(
            f"Invalid --asset '{arg}'. Expected format SYMBOL:COST_USD:VALUE_USD"
        )


def format_money(amount: float, currency: str = "") -> str:
    if currency:
        return f"{amount:,.2f} {currency}"
    return f"{amount:,.2f}"


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="USD ETF report in TWD")
    parser.add_argument(
        "--rate",
        type=float,
        default=29.26,
        help="TWD per USD exchange rate (default: 29.26)",
    )
    parser.add_argument(
        "--asset",
        action="append",
        type=parse_asset,
        help="Asset in the form SYMBOL:COST_USD:VALUE_USD (repeatable)",
    )

    args = parser.parse_args(argv)

    assets = args.asset
    if not assets:
        # Defaults from the user's message
        assets = [
            AssetUSD("VT", 174_357.2, 191_288.3),
            AssetUSD("IEF", 81_931.1, 84_224.1),
        ]

    rate = args.rate

    # Totals
    total_cost_usd = sum(a.cost_usd for a in assets)
    total_value_usd = sum(a.value_usd for a in assets)
    total_profit_usd = total_value_usd - total_cost_usd
    total_roi = (total_profit_usd / total_cost_usd) if total_cost_usd else 0.0

    # Header
    print("ETF  | Cost USD | Value USD | Profit USD | ROI   | Cost TWD | Value TWD | Profit TWD")
    print("-" * 86)

    for a in assets:
        cost_twd = a.cost_usd * rate
        value_twd = a.value_usd * rate
        profit_twd = value_twd - cost_twd
        print(
            f"{a.symbol:<4}| {a.cost_usd:>10,.2f} | {a.value_usd:>10,.2f} | "
            f"{a.profit_usd:>10,.2f} | {a.roi*100:>5.2f}% | "
            f"{cost_twd:>10,.0f} | {value_twd:>10,.0f} | {profit_twd:>10,.0f}"
        )

    print("-" * 86)
    print(
        f"SUM  | {total_cost_usd:>10,.2f} | {total_value_usd:>10,.2f} | {total_profit_usd:>10,.2f} | "
        f"{total_roi*100:>5.2f}% | {total_cost_usd*rate:>10,.0f} | {total_value_usd*rate:>10,.0f} | {(total_profit_usd*rate):>10,.0f}"
    )

    # Summary lines
    print()
    print(f"Exchange rate: {rate:.4f} TWD/USD")
    print(f"Total invested (TWD): {total_cost_usd*rate:,.0f}")
    print(f"Current value  (TWD): {total_value_usd*rate:,.0f}")
    print(f"Total profit   (TWD): {total_profit_usd*rate:,.0f} ({total_roi*100:.2f}%)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

