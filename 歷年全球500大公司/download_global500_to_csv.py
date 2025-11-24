#!/usr/bin/env python3
"""
Fetch Fortune Global 500 annual rankings and export each year to a CSV file.
"""
from __future__ import annotations

import csv
import ssl
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.request import urlopen

from bs4 import BeautifulSoup  # type: ignore[import-not-found]


BASE_URL = "https://www.fortunechina.com/fortune500/c/"
LIST_FILE = Path(__file__).with_name("list.html")
OUTPUT_DIR = Path(__file__).parent / "csv"
HTML_DIR = Path(__file__).parent / "html"
SSL_CONTEXT = ssl._create_unverified_context()
SUMMARY_KEYWORDS = ("总计", "总数", "合计")


def normalize(text: str) -> str:
    """Trim whitespace and collapse internal runs."""
    cleaned = text.replace("\xa0", " ").strip()
    return " ".join(cleaned.split())


def iter_year_links() -> List[Tuple[int, str]]:
    """Yield (year, url) pairs found in list.html sorted descending by year."""
    html = LIST_FILE.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    links: List[Tuple[int, str]] = []

    for anchor in soup.find_all("a"):
        href = anchor.get("href")
        raw_year = anchor.get("data-year") or normalize(anchor.get_text())
        if not href or not raw_year or not raw_year.isdigit():
            continue
        year = int(raw_year)
        full_url = resolve_url(href)
        links.append((year, full_url))

    links.sort(reverse=True)
    return links


def fetch_html(url: str) -> str:
    """Download a page, skipping certificate verification when needed."""
    with urlopen(url, context=SSL_CONTEXT) as response:
        return response.read().decode("utf-8", errors="replace")


def select_data_table(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Pick the first table that contains at least 100 rows of <td> data.

    This guards against layout tables and focuses on the ranking itself.
    """
    best_match: tuple[int, BeautifulSoup] | None = None
    for table in soup.find_all("table"):
        row_count = sum(1 for row in table.find_all("tr") if row.find_all("td"))
        if row_count >= 50:
            return table
        if not best_match or row_count > best_match[0]:
            best_match = (row_count, table)
    if best_match:
        return best_match[1]
    raise ValueError("Failed to locate ranking table.")


def resolve_url(href: str) -> str:
    """Convert relative href values into fully-qualified URLs."""
    if href.startswith(("http://", "https://")):
        return href

    normalized = href
    while normalized.startswith("../"):
        normalized = normalized[3:]
    normalized = normalized.lstrip("./")
    return urljoin(BASE_URL, normalized)


def load_paginated_pages(year: int, base_url: str) -> List[Tuple[str, Path, BeautifulSoup]]:
    """
    Fetch the base article and any paginated sub-pages that share the same stem.

    The result is sorted so that the main page comes first followed by numbered
    suffix pages in ascending order.
    """
    base_path = urlparse(base_url).path
    base_stem = base_path.rsplit(".", 1)[0]

    year_dir = HTML_DIR / str(year)
    year_dir.mkdir(parents=True, exist_ok=True)

    pending: List[str] = [base_url]
    visited: set[str] = set()
    pages: dict[str, Tuple[Path, BeautifulSoup]] = {}

    while pending:
        current = pending.pop()
        if current in visited:
            continue

        html, file_path = fetch_or_cache_html(year_dir, current)
        soup = BeautifulSoup(html, "html.parser")
        pages[current] = (file_path, soup)
        visited.add(current)

        for anchor in soup.find_all("a"):
            href = anchor.get("href")
            if not href:
                continue
            candidate = urljoin(current, href)
            candidate, _ = urldefrag(candidate)
            cand_path = urlparse(candidate).path
            if not cand_path.endswith(".htm"):
                continue
            cand_stem = cand_path.rsplit(".", 1)[0]
            if cand_stem == base_stem or cand_stem.startswith(base_stem + "_"):
                if candidate not in visited and candidate not in pending:
                    pending.append(candidate)

    def sort_key(url: str) -> Tuple[int, int]:
        cand_path = urlparse(url).path
        cand_stem = cand_path.rsplit(".", 1)[0]
        if cand_stem == base_stem:
            return (0, 0)
        suffix = cand_stem[len(base_stem) + 1 :]
        order = int(suffix) if suffix.isdigit() else 0
        return (1, order)

    sorted_urls = sorted(pages.keys(), key=sort_key)
    return [(url, pages[url][0], pages[url][1]) for url in sorted_urls]


def fetch_or_cache_html(year_dir: Path, url: str) -> Tuple[str, Path]:
    """Download an HTML page if missing locally; always return its content and path."""
    filename = page_filename(url)
    file_path = year_dir / filename
    if file_path.exists():
        html = file_path.read_text(encoding="utf-8")
    else:
        html = fetch_html(url)
        file_path.write_text(html, encoding="utf-8")
    return html, file_path


def page_filename(url: str) -> str:
    """Generate a stable filename for the given page URL."""
    parsed = urlparse(url)
    name = Path(parsed.path).name
    return name or "index.html"


def extract_table(table: BeautifulSoup) -> Tuple[List[str], List[List[str]]]:
    """Return the header row and cleaned row data from the given table."""
    header: List[str] | None = None
    data_rows: List[List[str]] = []
    last_rank: int | None = None

    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if not cells:
            continue
        texts = [normalize(cell.get_text()) for cell in cells]
        if header is None:
            header = texts
            continue
        if not texts:
            continue
        if any(keyword in cell for cell in texts for keyword in SUMMARY_KEYWORDS):
            continue
        if any("资料来源" in cell for cell in texts):
            continue
        rank_cell = texts[0]
        if rank_cell.replace(",", "").isdigit():
            last_rank = int(rank_cell.replace(",", ""))
        elif not rank_cell:
            if last_rank is None:
                continue
            last_rank += 1
            texts[0] = str(last_rank)
        else:
            continue
        data_rows.append(normalize_row(texts, len(header)))

    if header is None:
        raise ValueError("Table missing header row.")

    if header and header[0].isdigit():
        header[0] = "排名"

    return header, data_rows


def normalize_row(values: Sequence[str], width: int) -> List[str]:
    """Ensure row length matches header width by trimming or padding."""
    row = list(values[:width])
    if len(row) < width:
        row.extend([""] * (width - len(row)))
    return row


def write_csv(path: Path, header: Sequence[str], rows: Iterable[Sequence[str]]) -> None:
    """Write the ranking table to disk."""
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    HTML_DIR.mkdir(exist_ok=True)

    for year, url in iter_year_links():
        pages = load_paginated_pages(year, url)
        header: List[str] | None = None
        all_rows: List[List[str]] = []

        for page_url, _, soup in pages:
            table = select_data_table(soup)
            page_header, page_rows = extract_table(table)

            if header is None:
                header = page_header
            elif len(page_header) != len(header):
                raise ValueError(f"Header mismatch for year {year} at {page_url}")

            all_rows.extend(page_rows)

        if header is None:
            raise ValueError(f"Missing header for year {year}")

        csv_path = OUTPUT_DIR / f"fortune_global500_{year}.csv"
        write_csv(csv_path, header, all_rows)
        print(f"{year}: wrote {len(all_rows)} rows across {len(pages)} page(s) to {csv_path}")


if __name__ == "__main__":
    main()
