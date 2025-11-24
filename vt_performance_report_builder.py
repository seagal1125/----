
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

# --- Analysis Text ---
winner_analysis = """
### 群組特性分析

領先群體展現了非常鮮明的產業特性，主要由以下兩大類別驅動：

1.  **AI 與半導體產業鏈**: 這是今年最強勁的成長引擎。從上游的晶片設計與製造 (AMD, INTC, NVDA)、半導體設備 (ASML, AMAT, LRCX)，到AI軟體與應用 (PLTR, ORCL)，幾乎佔據了報酬率榜單的頂端。這反映了市場資金高度集中於人工智慧的軍備競賽相關領域。
2.  **全球金融與銀行股**: 另一股強勁的支撐力來自於全球性的銀行與金融機構 (例如 SAN, JPM, GS, MS, C)。這可能反映了在一個成長的經濟環境中，金融業的獲利預期良好。
"""

loser_analysis = """
### 群組特性分析

落後群體的組成則相對多元，但可以看出幾個主要特徵：

1.  **傳統消費與民生必需品**: 此類別包含許多大型且成熟的公司，如可口可樂(KO)、百事(PEP)、寶僑(PG)、沃爾瑪(WMT)等。這些防禦性股票在市場追求高成長性時，通常表現較為溫和。
2.  **醫療保健與製藥 (表現分歧)**: 雖然禮來(LLY)表現不錯，但此區塊的多數公司，如默克(MRK)、聯合健康(UNH)、直覺外科(ISRG)等，今年表現相對疲軟甚至下跌。
3.  **成長趨緩的科技與媒體股**: 部分過往的明星科技股，如 Salesforce(CRM)、Adobe(ADBE)、迪士尼(DIS)等，因面臨市場競爭、成長放緩或轉型挑戰，其股價表現不如搭上AI熱潮的同業。
4.  **能源股**: 雖然國際局勢多變，但埃克森美孚(XOM)、雪佛龍(CVX)等能源巨頭今年的報酬也僅為個位數，未能跟上指數的漲幅。
"""

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(f'# VT 及其前100大持股一年期績效分析報告 (2024/04/30 ~ 2025/04/30)\n\n')
    f.write(f'**統計區間**: 2024-04-30 至 2025-04-30\n\n')
    f.write(f'## 整體市場表現\n\n在此統計區間內，Vanguard 全世界股票ETF (VT) 的整體績效為 **+{vt_return_pct:.2f}%**。\n\n---\n')
    f.write(f'## 績效領先群 (超越 VT)\n\n在成功取得數據的成分股中，共有 **{len(winners)}** 支股票的一年期報酬率超越了 VT 本身的 +{vt_return_pct:.2f}%。\n')
    f.write(winner_analysis)
    f.write('\n### 領先群績效列表\n')
    f.write('| 排名 | 代號 (Ticker) | 公司名稱 | 中文名稱 | 一年期報酬率 |\n')
    f.write('| :--- | :--- | :--- | :--- | :--- |\n')
    for i, item in enumerate(winners):
        rank = i + 1
        ticker = item.get('ticker', '')
        long_name = item.get('longName', '')
        original_ticker = ticker.split('.')[0].replace('-','/')
        chinese_name = name_map.get(original_ticker, '')
        return_pct = item['total_return_pct']
        f.write(f'| {rank} | {ticker} | {long_name} | {chinese_name} | +{return_pct:.2f}% |\n')
    
    f.write('\n---\n')
    f.write(f'## 績效落後群 (落後 VT)\n\n在其餘成功抓取的 **{len(losers)}** 支成分股中，它們的表現不及 VT 的 +{vt_return_pct:.2f}%。\n')
    f.write(loser_analysis)
    f.write('\n### 落後群績效列表\n')
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

print(f"Successfully generated complete report with analysis at {md_path}")
