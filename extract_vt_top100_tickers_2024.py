import json
import os

json_path = 'vt_holdings_snapshot_2024-04-30.json'
tickers = []

# Suffix mapping based on country code from the JSON file
suffix_map = {
    'TW': '.TW', 'JP': '.T', 'AU': '.AX', 'CA': '.TO', 'IN': '.NS',
    'GB': '.L', 'DE': '.DE', 'FR': '.PA', 'HK': '.HK'
}

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# The holdings are under the date key, then 'equity'
date_key = list(data.keys())[0]
holdings = data.get(date_key, {}).get('equity', [])

for i, item in enumerate(holdings[:100]):
    ticker = item.get('ticker', '')
    country = item.get('country', '')

    yfinance_ticker = ticker
    suffix = suffix_map.get(country)
    if suffix:
        # yfinance often uses '-' instead of '.' in tickers like BRK.B
        if '.' in ticker:
            ticker = ticker.replace('.', '-')
        yfinance_ticker = f'{ticker}{suffix}'
    
    tickers.append(yfinance_ticker)

# Print the tickers for the next step
print(str(tickers))
