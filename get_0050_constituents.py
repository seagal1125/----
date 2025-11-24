import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

DATA_PATH = Path(__file__).resolve().parent / "data" / "0050成份股時間點回溯資料庫.json"

# Some legacy codes were later relisted under new ticker numbers.
# Map them so lookups always surface the up-to-date identifier.
CODE_REMAP = {
    "5854": "5880",
}


def _parse_month(value: str) -> dt.date:
    year, month = value.split("-")
    return dt.date(int(year), int(month), 1)


def _parse_date(value: str) -> dt.date:
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m"):
        try:
            parsed = dt.datetime.strptime(value, fmt)
            if fmt == "%Y-%m":
                return dt.date(parsed.year, parsed.month, 1)
            return parsed.date()
        except ValueError:
            continue
    raise ValueError("Unsupported date format. Use YYYY-MM or YYYY-MM-DD.")


def _load_database() -> Dict:
    with DATA_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def _compute_base_constituents(
    events: Sequence[Dict[str, Sequence[str]]],
    current: Set[str],
) -> Set[str]:
    state = set(current)
    for event in reversed(events):
        state.difference_update(event.get("added", []))
        state.update(event.get("removed", []))
    return state


def _build_timeline(
    events: Sequence[Dict[str, Sequence[str]]],
    base: Set[str],
) -> List[Tuple[Optional[dt.date], Set[str]]]:
    timeline: List[Tuple[Optional[dt.date], Set[str]]] = [(None, set(base))]
    state = set(base)
    for event in events:
        state.difference_update(event.get("removed", []))
        state.update(event.get("added", []))
        timeline.append((_parse_month(event["date"]), set(state)))
    return timeline


def _constituents_as_of(
    timeline: Iterable[Tuple[Optional[dt.date], Set[str]]],
    target: dt.date,
) -> Set[str]:
    effective: Optional[Set[str]] = None
    for event_date, members in timeline:
        if event_date is None or event_date <= target:
            effective = members
        else:
            break
    if effective is None:
        raise RuntimeError("Timeline is empty; cannot determine constituents.")

    normalized: Set[str] = set()
    for code in effective:
        normalized.add(CODE_REMAP.get(code, code))
    return normalized


def _format_output(
    tickers: Sequence[str],
    metadata: Dict[str, str],
    codes_only: bool,
) -> str:
    if codes_only:
        return "\n".join(tickers)

    lines = []
    for code in tickers:
        name = metadata.get(code, "<unknown>")
        lines.append(f"{code} - {name}")
    return "\n".join(lines)


def query_constituents(as_of: dt.date, codes_only: bool = False) -> str:
    data = _load_database()
    events = sorted(data["historical_changes"], key=lambda e: e["date"])
    current = set(data["current_constituents"])
    base = _compute_base_constituents(events, current)
    timeline = _build_timeline(events, base)

    members = _constituents_as_of(timeline, as_of)
    ordered = sorted(members)
    return _format_output(ordered, data["stock_metadata"], codes_only)


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Return the 0050 constituent list for the requested date.",
    )
    parser.add_argument(
        "date",
        help="As-of date (YYYY-MM or YYYY-MM-DD).",
    )
    parser.add_argument(
        "--codes-only",
        action="store_true",
        help="Print codes only, without company names.",
    )
    args = parser.parse_args(argv)

    as_of = _parse_date(args.date)
    result = query_constituents(as_of, codes_only=args.codes_only)
    print(result)


if __name__ == "__main__":
    main()
