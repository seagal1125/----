
import json
import os

# Define the mapping for known Chinese company names
name_map = {
    'NVDA': '輝達',
    'MSFT': '微軟',
    'AAPL': '蘋果',
    'AMZN': '亞馬遜',
    'META': 'Meta Platforms',
    'GOOGL': 'Alphabet (Google)',
    'GOOG': 'Alphabet (Google)',
    'TSLA': '特斯拉',
    '2330': '台積電',
    '700': '騰訊控股',
    '9988': '阿里巴巴',
    'ASML': '艾司摩爾',
    '005930': '三星電子',
    'SAP': '思愛普',
    '7203': '豐田汽車',
    'NESN': '雀巢',
    'ROG': '羅氏',
    'NOVN': '諾華',
    'HSBA': '匯豐控股',
    'BABA-W': '阿里巴巴',
    '9984': '軟銀集團',
    '6758': '索尼',
    'NOVO B': '諾和諾德',
    '6861': '基恩斯',
    '8035': '東京威力科創',
    '4063': '信越化學工業',
    '8001': '伊藤忠商事',
    '8306': '三菱日聯金融集團',
    '8766': '東京海上控股',
    '8316': '三井住友金融集團',
    '6501': '日立',
    '7974': '任天堂',
    '6098': '瑞可利控股',
    '8058': '三菱商事',
    'HDFCBANK': 'HDFC銀行',
    'RELIANCE': '信實工業',
    'ICICIBANK': 'ICICI銀行'
}

# File paths
json_path = os.path.join(os.getcwd(), 'vt_holdings_temp.json')
md_path = os.path.join(os.getcwd(), 'vt_holdings.md')

# Read the temporary JSON file
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract holdings
holdings = data.get('fund', {}).get('entity', [])

# Build the Markdown content
md_content = '| Ticker | Company Name | Chinese Company Name | % Of Assets |\n'
md_content += '| :--- | :--- | :--- | :--- |\n'

for item in holdings:
    ticker = item.get('ticker', '')
    long_name = item.get('longName', '')
    percent_weight = item.get('percentWeight', '0')
    # Look up the Chinese name, default to empty string if not found
    chinese_name = name_map.get(ticker, '')
    md_content += f'| {ticker} | {long_name} | {chinese_name} | {percent_weight}% |\n'

# Write the Markdown file
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

# Clean up the temporary file
os.remove(json_path)

print(f'Successfully processed {len(holdings)} holdings and wrote them to {md_path}')
