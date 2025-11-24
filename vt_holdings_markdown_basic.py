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

for i, item in enumerate(holdings):
    rank = i + 1
    ticker = item.get('ticker', '')
    long_name = item.get('longName', '')
    percent_weight = item.get('percentWeight', '0')
    # Look up the Chinese name, default to empty string if not found
    chinese_name = name_map.get(ticker, '')
    lines.append(f'| {rank} | {ticker} | {long_name} | {chinese_name} | {percent_weight}% |')

# Join the lines with newline characters
md_content = "\n".join(lines)

# Write the Markdown file
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f'Successfully updated {md_path} with {len(holdings)} holdings, including ranks and expanded Chinese names.')
