
import json
import os

# File paths
json_path = 'vt_holdings_snapshot_latest.json'
map_path = 'vt_company_name_map.json'
md_path = 'vt_holdings.md'

# Read the name map file
with open(map_path, 'r', encoding='utf-8') as f:
    name_map = json.load(f)

# Read the full JSON file
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract holdings
holdings = data.get('fund', {}).get('entity', [])

# Build the Markdown content
lines = []
lines.append('| Rank | Ticker | Company Name | Chinese Company Name | % Of Assets |')
lines.append('| :--- | :--- | :--- | :--- | :--- |')

# Heuristic mapping for yfinance tickers
suffix_map = {
    'TW': '.TW', 'JP': '.T', 'AU': '.AX', 'CA': '.TO', 'IN': '.NS',
    'GB': '.L', 'JE': '.L', 'DE': '.DE', 'FR': '.PA'
}

for i, item in enumerate(holdings):
    rank = i + 1
    ticker = item.get('ticker', '')
    long_name = item.get('longName', '')
    percent_weight = item.get('percentWeight', '0')
    isin = item.get('isin', '')
    country_code = isin[:2]

    yfinance_ticker = ticker
    # Apply suffix based on ISIN country code
    suffix = suffix_map.get(country_code)
    if suffix:
        yfinance_ticker = f'{ticker}{suffix}'
    # Special heuristic for Hong Kong stocks (4-digit tickers)
    elif country_code in ['HK', 'KY', 'BM'] and ticker.isdigit() and len(ticker) == 4:
        yfinance_ticker = f'{ticker}.HK'
    # Special heuristic for some European stocks without clear country mapping in ISIN
    elif ticker.endswith('.AS') or ticker.endswith('.PA') or ticker.endswith('.DE'): # Example for Amsterdam/Paris/Germany
        pass # Ticker is likely already in yfinance format

    # Look up the Chinese name using the original ticker
    chinese_name = name_map.get(ticker, '')
    
    lines.append(f'| {rank} | {yfinance_ticker} | {long_name} | {chinese_name} | {percent_weight}% |')

# Join the lines with newline characters
md_content = "\n".join(lines)

# Write the Markdown file
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f'Successfully applied advanced ticker corrections and updated {md_path}.')
