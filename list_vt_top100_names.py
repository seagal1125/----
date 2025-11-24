
import json
import os

json_path = os.path.join(os.getcwd(), 'vt_holdings_snapshot_latest.json')

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

holdings = data.get('fund', {}).get('entity', [])

for i, item in enumerate(holdings[:100]):
    ticker = item.get('ticker', 'N/A')
    long_name = item.get('longName', 'N/A')
    print(f'{i+1}. Ticker: {ticker}, Name: {long_name}')
