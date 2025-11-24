
import json
import os

# Define the expanded mapping for known Chinese company names
name_map = {
    'NVDA': '輝達', 'MSFT': '微軟', 'AAPL': '蘋果', 'AMZN': '亞馬遜', 'META': 'Meta Platforms',
    'GOOGL': 'Alphabet (Google)', 'GOOG': 'Alphabet (Google)', 'TSLA': '特斯拉', '2330': '台積電',
    'JPM': '摩根大通', 'BRK.B': '波克夏·海瑟威', 'LLY': '禮來', 'V': 'Visa', '700': '騰訊控股',
    'NFLX': '網飛', 'XOM': '埃克森美孚', 'ORCL': '甲骨文', 'MA': '萬事達卡', 'WMT': '沃爾瑪',
    'JNJ': '嬌生', 'COST': '好市多', 'ABBV': '艾伯維', 'HD': '家得寶', '9988': '阿里巴巴',
    'PLTR': '帕蘭泰爾', 'ASML': '艾司摩爾', 'PG': '寶僑', 'BAC': '美國銀行', 'GE': '通用電氣',
    'UNH': '聯合健康集團', 'CVX': '雪佛龍', '005930': '三星電子', 'SAP': '思愛普', 'CSCO': '思科',
    'WFC': '富國銀行', 'IBM': 'IBM', 'AMD': '超微', 'KO': '可口可樂', 'PM': '菲利普莫里斯',
    'HSBA': '匯豐控股', 'NOVN': '諾華', 'GS': '高盛', 'NESN': '雀巢', 'ABT': '亞培',
    'AZN': '阿斯特捷利康', 'RTX': '雷神技術', 'LIN': '林德集團', 'CRM': 'Salesforce', 'CAT': '開拓重工',
    'MCD': '麥當勞', 'MRK': '默克', 'SHEL': '殼牌', 'RY': '加拿大皇家銀行', 'DIS': '迪士尼',
    'ROG': '羅氏', '7203': '豐田汽車', 'SIE': '西門子', 'T': 'AT&T', 'UBER': '優步',
    'PEP': '百事', 'NOW': 'ServiceNow', 'MU': '美光科技', 'INTU': '財捷', 'VZ': '威瑞森',
    'C': '花旗集團', 'CBA': '澳大利亞聯邦銀行', 'TMO': '賽默飛世爾科技', 'MS': '摩根士丹利',
    'AXP': '美國運通', 'QCOM': '高通', 'SHOP': 'Shopify', '8306': '三菱日聯金融集團',
    'NOVO B': '諾和諾德', 'BLK': '貝萊德', 'BKNG': 'Booking Holdings', '6758': '索尼',
    'LRCX': '科林研發', 'APP': 'AppLovin', 'GEV': 'GE Vernova', 'TXN': '德州儀器',
    'AMAT': '應用材料', 'SCHW': '嘉信理財', 'ALV': '安聯', 'TJX': 'TJX', 'ISRG': '直覺外科',
    'MC': 'LVMH集團', 'BA': '波音', 'NEE': '新紀元能源', 'SAN': '桑坦德銀行', 'ACN': '埃森哲',
    'SU': '施耐德電氣', 'AMGN': '安進', 'ANET': 'Arista網路', 'ADBE': '奧多比', 'APH': '安費諾',
    'SPGI': '標普全球', 'ETN': '伊頓', 'INTC': '英特爾', 'PGR': '前進保險'
}

# File paths
json_path = os.path.join(os.getcwd(), 'vt_holdings_snapshot_latest.json')
md_path = os.path.join(os.getcwd(), 'vt_holdings.md')

# Read the full JSON file
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract holdings
holdings = data.get('fund', {}).get('entity', [])

# Build the Markdown content as a list of strings
lines = []
lines.append('| Rank | Ticker | Company Name | Chinese Company Name | % Of Assets |
')
lines.append('| :--- | :--- | :--- | :--- | :--- |
')

for i, item in enumerate(holdings):
    rank = i + 1
    ticker = item.get('ticker', '')
    long_name = item.get('longName', '')
    percent_weight = item.get('percentWeight', '0')
    chinese_name = name_map.get(ticker, '')
    lines.append(f'| {rank} | {ticker} | {long_name} | {chinese_name} | {percent_weight}% |
')

# Join the lines with newline characters
md_content = "".join(lines)

# Write the Markdown file
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f'Successfully updated {md_path} with {len(holdings)} holdings, including ranks and expanded Chinese names.')
