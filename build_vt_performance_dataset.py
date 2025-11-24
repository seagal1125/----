
import json
from mcp_stock import compare_returns

tickers = ['VT', 'MSFT', 'AAPL', 'NVDA', 'AMZN', 'GOOGL', 'META', 'GOOG', 'LLY', 'BRK-B', '2330.TW', 'AVGO', 'JPM', 'TSLA', 'XOM', 'UNH', 'V', 'NOVO-B', 'PG', 'MA', 'JNJ', 'ASML', 'HD', 'MRK', 'COST', 'ABBV', 'CVX', '7203.T', '700.HK', 'NESN', '005930', 'BAC', 'WMT', 'AMD', 'CRM', 'PEP', 'KO', 'NFLX', 'SHEL.L', 'AZN.L', 'TMO', 'WFC', 'LIN', 'ADBE', 'MC.PA', 'DIS', 'NOVN', 'MCD', 'SAP.DE', 'ACN', 'CSCO', 'QCOM', 'ABT', 'GE', 'ORCL', 'INTU', 'CAT', 'AMAT', 'VZ', 'HSBA.L', 'DHR', 'TXN', '9988.HK', 'IBM', 'COP', 'CMCSA', 'TTE.PA', 'PM', 'AMGN', 'RTX', 'PFE', 'UNP', 'ROG', 'NOW', 'SIE.DE', 'BHP.AX', 'NEE', 'AXP', 'RY.TO', 'GS', 'SPGI', 'LOW', 'UBER', 'ISRG', 'INTC', 'ULVR.L', 'HON', 'ETN', 'ELV', 'MU', 'CBA.AX', 'SU.PA', 'PGR', 'T', 'BKNG', 'SYK', 'LRCX', 'C', 'BRK-A', 'BLK', '8306.T']

result = compare_returns(tickers=tickers, start='2024-04-30', end='2025-05-01')

with open('vt_performance_results_latest.json', 'w', encoding='utf-8') as f:
    json.dump(result, f)

print("Successfully generated vt_performance_results_latest.json")
