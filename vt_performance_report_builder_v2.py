import json
import os

perf_path = 'vt_performance_results_latest.json'
map_path = 'vt_company_name_map.json'
md_path = 'VT_1yr_report_2024-04-30.md'

try:
    with open(perf_path, 'r', encoding='utf-8') as f:
        perf_data = json.load(f)
    with open(map_path, 'r', encoding='utf-8') as f:
        name_map = json.load(f)
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit()

all_items = perf_data.get('items', [])
successful_results = []
for item in all_items:
    if 'error' not in item:
        successful_results.append(item)

sorted_results = sorted(successful_results, key=lambda x: x.get('total_return', -999), reverse=True)
vt_performance = next((item for item in sorted_results if item['ticker'] == 'VT'), None)

if not vt_performance:
    print("Error: VT performance data not found.")
    exit()

vt_return = vt_performance['total_return']
vt_return_pct = vt_performance['total_return_pct']

winners = [item for item in sorted_results if item['ticker'] != 'VT' and item['total_return'] > vt_return]
losers = sorted([item for item in sorted_results if item['ticker'] != 'VT' and item['total_return'] <= vt_return], key=lambda x: x.get('total_return', -999), reverse=True)

with open(md_path, 'w', encoding='utf-8') as f:
    f.write('# VT 及其前100大持股一年期績效分析報告\n\n')
    f.write('**統計區間**: 2024-04-30 至 2025-04-30\n\n')
    f.write(f'## 整體市場表現\n\n在此統計區間內，Vanguard 全世界股票ETF (VT) 的整體績效為 **+{vt_return_pct:.2f}%**。\n\n---\n')
    f.write(f'## 績效領先群 (超越 VT)\n\n在成功取得數據的成分股中，共有 **{len(winners)}** 支股票的一年期報酬率超越了 VT 本身的 +{vt_return_pct:.2f}%。\n')
    f.write('### 群組特性分析\n領先群體展現了非常鮮明的產業特性...\n')
    f.write('### 領先群績效列表\n')
    f.write('| 排名 | 代號 (Ticker) | 公司名稱 | 中文名稱 | 一年期報酬率 |\n')
    f.write('| :--- | :--- | :--- | :--- | :--- |\n')
    for i, item in enumerate(winners):
        ticker = item.get('ticker', '')
        long_name = item.get('longName', '')
        original_ticker = ticker.split('.')[0].replace('-','/')
        chinese_name = name_map.get(original_ticker, '')
        return_pct = item['total_return_pct']
        f.write(f'| {i+1} | {ticker} | {long_name} | {chinese_name} | +{return_pct:.2f}% |\n')
    
    f.write('\n---\n')
    f.write(f'## 績效落後群 (落後 VT)\n\n在其餘成功抓取的 **{len(losers)}** 支成分股中，它們的表現不及 VT 的 +{vt_return_pct:.2f}%。\n')
    f.write('### 群組特性分析\n落後群體的組成則相對多元...\n')
    f.write('### 落後群績效列表\n')
    f.write('| 排名 | 代號 (Ticker) | 公司名稱 | 中文名稱 | 一年期報酬率 |\n')
    f.write('| :--- | :--- | :--- | :--- | :--- |\n')
    for i, item in enumerate(losers):
        rank = len(winners) + i + 1
        ticker = item.get('ticker', '')
        long_name = item.get('longName', '')
        original_ticker = ticker.split('.')[0].replace('-','/')
        chinese_name = name_map.get(original_ticker, '')
        return_pct = item['total_return_pct']
        sign = '+' if return_pct >= 0 else ''
        f.write(f'| {rank} | {ticker} | {long_name} | {chinese_name} | {sign}{return_pct:.2f}% |\n')

os.remove(perf_path)

print(f"Successfully generated complete report at {md_path}")
