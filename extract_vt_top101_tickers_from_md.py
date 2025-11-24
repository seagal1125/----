
import os

md_path = 'vt_holdings.md'
tickers = []

with open(md_path, 'r', encoding='utf-8') as f:
    # Skip header lines
    for _ in range(2):
        next(f)
    
    # Read the next 101 lines for VT and top 100 holdings
    for i, line in enumerate(f):
        if i >= 101:
            break
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) > 1:
            # The ticker is the second column (index 1)
            tickers.append(parts[1])

# Print the tickers in a format that can be easily used in the next step
print(str(tickers))
