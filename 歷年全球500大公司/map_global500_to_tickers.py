#!/usr/bin/env python3
"""
Append Yahoo Finance tickers to the Fortune Global 500 CSV files.

For each company we attempt to infer an equity ticker by querying Yahoo's
symbol search API. Results are cached locally to avoid repeated lookups.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import ssl
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


CSV_DIR = Path(__file__).with_name("csv")
OUTPUT_DIR = Path(__file__).with_name("csv_with_ticker")
CACHE_FILE = Path(__file__).with_name("ticker_cache.json")
HEADERS = {"User-Agent": "Mozilla/5.0"}
YAHOO_SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"
STOP_WORDS = {
    "INC",
    "INCORPORATED",
    "CO",
    "COMPANY",
    "CORPORATION",
    "CORP",
    "GROUP",
    "LIMITED",
    "LTD",
    "PLC",
    "HOLDINGS",
    "HOLDING",
    "SA",
    "SPA",
    "AG",
    "NV",
    "SASA",
    "LLC",
    "LP",
    "BV",
    "ASA",
    "AB",
    "OYJ",
    "A/S",
    "S.A.",
    "S.A",
    "P.L.C",
    "SE",
    "GMBH",
    "L.L.C.",
    "PTE",
    "LIMITADA",
}
RAW_MANUAL_OVERRIDES = {
    "WALMART": "WMT",
    "WAL-MART STORES": "WMT",
    "AMAZON.COM": "AMZN",
    "BERKSHIRE HATHAWAY": "BRK.B",
    "ALPHABET": "GOOGL",
    "APPLE": "AAPL",
    "META PLATFORMS": "META",
    "TESLA": "TSLA",
    "MICROSOFT": "MSFT",
    "JPMORGAN CHASE": "JPM",
    "EXXON MOBIL": "XOM",
    "SAUDI ARAMCO": "2222.SR",
    "PETROCHINA": "0857.HK",
    "CHINA PETROLEUM & CHEMICAL": "0386.HK",
    "SINOPEC": "0386.HK",
    "STATE GRID": "",
    "CHINA STATE CONSTRUCTION ENGINEERING": "601668.SS",
    "CHINA RAILWAY ENGINEERING": "601186.SS",
    "CHINA RAILWAY CONSTRUCTION": "601186.SS",
    "BP": "BP",
    "ROYAL DUTCH SHELL": "SHEL",
    "SHELL": "SHEL",
    "TOTALENERGIES": "TTE",
    "VOLKSWAGEN": "VWAGY",
    "TOYOTA MOTOR": "TM",
    "HON HAI PRECISION INDUSTRY": "2317.TW",
    "FOXCONN": "2317.TW",
    "INDUSTRIAL AND COMMERCIAL BANK OF CHINA": "1398.HK",
    "BANK OF CHINA": "3988.HK",
    "CHINA CONSTRUCTION BANK": "0939.HK",
    "AGRICULTURAL BANK OF CHINA": "1288.HK",
    "ICBC": "1398.HK",
    "CHINA MOBILE COMMUNICATIONS": "0941.HK",
    "CHINA MOBILE": "0941.HK",
    "PING AN INSURANCE": "2318.HK",
    "A.P. MOLLER - MAERSK": "AMKBY",
    "MAERSK": "AMKBY",
    "A.P. MOLER MAERSK GROUP": "AMKBY",
    "ALLIANCE BOOTS": "",
    "AETNA": "AET",
    "BT": "BT.A",
    "CEPSA": "CEP.MC",
    "COSMO OIL": "5007.T",
    "CREDIT INDUSTRIEL COMMERCIAL": "CIC.PA",
    "CIE NATIONALE A PORTEFEUILLE": "CNP.BR",
    "CIENATIONALEPORTEFEUILLE": "CNP.BR",
    "ENCANA": "ECA",
    "EXPRESS SCRIPTS": "ESRX",
    "FINMECCANICA": "LDO.MI",
    "FONCIERE EURIS": "EURS.PA",
    "FONCIREEURIS": "EURS.PA",
    "FRANZ HANIEL": "",
    "FRANZHANIEL": "",
    "GASTERRA": "",
    "GAZPROM": "OGZPY",
    "GMAC": "ALLY",
    "GROUPE CAISSE D EPARGNE": "",
    "GROUPE AUCHAN": "",
    "GROUPAMA": "",
    "HBOS": "HBOS.L",
    "HUTCHISON WHAMPOA": "0001.HK",
    "ITAUSA INVESTIMENTOS ITAU": "ITSA4.SA",
    "J.C. PENNEY": "JCP",
    "JCPENNEY": "JCP",
    "KFW BANKENGRUPPE": "",
    "LAFARGE": "LG.PA",
    "LANDESBANK BADEN WURTTEMBERG": "",
    "LIBERTY MUTUAL INSURANCE GROUP": "",
    "LUKOIL": "LUKOY",
    "MARATHON OIL": "MRO",
    "MIGROS": "",
    "NIPPON OIL": "5001.T",
    "PEMEX": "",
    "RABOBANK": "",
    "ROSNEFT OIL": "ROSN.ME",
    "SABMILLER": "SBMRY",
    "SANTANDER CENTRAL HISPANO": "SAN",
    "SANTANDER CENTRAL HISPANO GROUP": "SAN",
    "SBERBANK": "SBRCY",
    "STATE FARM INSURANCE COS": "",
    "STATE GRID": "",
    "SUPERVALU": "SVU",
    "SURGUTNEFTEGAS": "SGTZY",
    "TIAA CREF": "",
    "VATTENFALL": "",
    "WALGREEN": "WAG",
    "WELLPOINT": "WLP",
    "WOLSELEY": "WOS.L",
    "WYETH": "WYE",
    "XSTRATA": "XTA.L",
    "ZF FRIEDRICHSHAFEN": "",
}
SSL_CONTEXT = ssl._create_unverified_context()


def main() -> None:
    parser = argparse.ArgumentParser(description="Append Yahoo tickers to Global 500 CSVs.")
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        help="Specific years to process (e.g. 2008 2009). Defaults to all available years.",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)
    cache = load_cache()
    name_to_key: Dict[str, str] = {}

    csv_paths = sorted(CSV_DIR.glob("fortune_global500_*.csv"))
    if args.years:
        target = {str(year) for year in args.years}
        csv_paths = [
            path for path in csv_paths if path.stem.rsplit("_", 1)[-1] in target
        ]
        if not csv_paths:
            raise SystemExit("No CSV files found for the requested years.")

    for path in csv_paths:
        with path.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            company_col = find_company_column(reader.fieldnames or [])
            for row in reader:
                raw_name = row.get(company_col, "")
                name = normalize_company_name(raw_name)
                if not name:
                    continue
                key = canonical_key(name)
                if key:
                    if key not in name_to_key or score_name(name) > score_name(name_to_key[key]):
                        name_to_key[key] = name

    ensure_tickers(name_to_key, cache)
    write_enriched_files(cache, csv_paths)


def load_cache() -> Dict[str, str]:
    if CACHE_FILE.exists():
        with CACHE_FILE.open(encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_cache(cache: Dict[str, str]) -> None:
    with CACHE_FILE.open("w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False, indent=2, sort_keys=True)


def find_company_column(headers: Sequence[str]) -> str:
    for header in headers:
        if "公司" in header:
            return header
    raise ValueError("No company column found")


def normalize_company_name(raw: str) -> str:
    if not raw:
        return ""
    text = raw.strip().strip('"')
    text = text.replace("\u3000", " ").replace("\xa0", " ").replace("＆", "&")

    for open_char, close_char in [("（", "）"), ("(", ")")]:
        if open_char in text and close_char in text:
            start = text.index(open_char) + 1
            end = text.index(close_char, start)
            text = text[start:end]
            break
    else:
        if "（" in text:
            text = text.split("（", 1)[-1]
        elif "(" in text:
            text = text.split("(", 1)[-1]

    text = text.strip(" ()（）")
    text = re.sub(r"(?<=[A-Za-z])\d+(?=[A-Za-z])", "", text)
    text = re.sub(r"^\d+", "", text)
    text = re.sub(r"\d+$", "", text)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if ord(ch) < 128)
    text = text.replace("@", "A")
    text = text.replace("*", "")
    text = re.sub(r"[\"']", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def canonical_key(name: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", name.upper())


def score_name(name: str) -> int:
    return sum(ch.isalpha() for ch in name)


MANUAL_OVERRIDES = {canonical_key(name): ticker for name, ticker in RAW_MANUAL_OVERRIDES.items()}


def ensure_tickers(name_map: Dict[str, str], cache: Dict[str, str]) -> None:
    unresolved: List[str] = []
    for key, name in sorted(name_map.items(), key=lambda item: item[1]):
        manual = MANUAL_OVERRIDES.get(key)
        if manual is not None:
            cache[key] = manual
            if not manual:
                continue
            # Manual override satisfied; move on.
            continue
        cached = cache.get(key)
        if cached:
            continue
        ticker = resolve_ticker(name)
        cache[key] = ticker
        if not ticker:
            unresolved.append(name)
    save_cache(cache)
    if unresolved:
        print(f"Tickers missing for {len(unresolved)} company names (see ticker_cache.json).")


def resolve_ticker(name: str) -> str:
    manual_key = canonical_key(name)
    if manual_key in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[manual_key]

    queries = generate_queries(name)
    for query in queries:
        if not query:
            continue
        quotes = search_yahoo(query)
        symbol = select_best_symbol(quotes)
        if symbol is not None:
            return symbol
    return ""


def generate_queries(name: str) -> List[str]:
    queries: List[str] = []
    cleaned = name.replace(",", " ").replace(".", " ").replace("-", " ")
    cleaned = cleaned.replace("/", " ").replace("&", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    tokens = cleaned.split()

    def push(candidate: str) -> None:
        candidate = candidate.strip()
        if candidate and candidate not in queries:
            queries.append(candidate)

    push(name)
    if cleaned != name:
        push(cleaned)

    filtered_tokens = [tok for tok in tokens if tok.upper() not in STOP_WORDS]
    if filtered_tokens:
        push(" ".join(filtered_tokens))
        if len(filtered_tokens) >= 2:
            push(" ".join(filtered_tokens[:2]))
            push(" ".join(filtered_tokens[-2:]))
        push(filtered_tokens[-1])

    if tokens:
        push(tokens[-1])

    return queries[:4]


def search_yahoo(query: str) -> List[Dict[str, str]]:
    params = {
        "q": query,
        "lang": "en-US",
        "region": "US",
    }
    url = f"{YAHOO_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=10) as resp:
                data = json.load(resp)
            time.sleep(0.05)
            return data.get("quotes", [])
        except urllib.error.HTTPError as err:
            if err.code == 429:
                time.sleep(1.5 * (attempt + 1))
                continue
        except Exception:
            time.sleep(0.5 * (attempt + 1))
    return []


def select_best_symbol(quotes: Sequence[Dict[str, str]]) -> Optional[str]:
    for quote in quotes:
        symbol = quote.get("symbol") or ""
        if not symbol:
            continue
        quote_type = (quote.get("quoteType") or "").upper()
        if quote_type not in {"EQUITY", "ETF", "ADR"}:
            continue
        return symbol
    return None


def write_enriched_files(cache: Dict[str, str], paths: Sequence[Path]) -> None:
    for path in paths:
        with path.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            fieldnames = list(reader.fieldnames or [])
            company_col = find_company_column(fieldnames)
            output_path = OUTPUT_DIR / path.name
            with output_path.open("w", encoding="utf-8", newline="") as out_fh:
                writer = csv.DictWriter(out_fh, fieldnames=fieldnames + ["ticker"])
                writer.writeheader()
                for row in reader:
                    name = normalize_company_name(row.get(company_col, ""))
                    key = canonical_key(name)
                    row["ticker"] = cache.get(key, "")
                    writer.writerow(row)
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
