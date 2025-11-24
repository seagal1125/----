
import yfinance as yf
import pandas as pd
import json
import re
from pathlib import Path

def get_return(ticker, company_name, start_date, end_date):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        if df.empty:
            return {"ticker": ticker, "company_name": company_name, "error": "No data found"}
        
        close_prices = df['Close'].dropna()
        if close_prices.empty:
            return {"ticker": ticker, "company_name": company_name, "error": "No close price data"}

        start_price = close_prices.iloc[0]
        end_price = close_prices.iloc[-1]
        
        total_return = (end_price / start_price) - 1.0
        
        return {
            "ticker": str(ticker),
            "company_name": str(company_name),
            "total_return_pct": float(round(total_return * 100, 2)),
            "start_date": str(close_prices.index[0].strftime('%Y-%m-%d')),
            "end_date": str(close_prices.index[-1].strftime('%Y-%m-%d')),
        }
    except Exception as e:
        return {"ticker": str(ticker), "company_name": str(company_name), "error": str(e)}

def main():
    tickers_to_process = [
        'SHEL', 'XOM', 'WMT', 'BP', '0386.HK', 'PTR', 'CVX', 'COP', 'TM', 'TTE', 
        'VOW3.DE', '6178.T', 'GLEN.L', 'OGZPY', 'EOAN.DE', 'E', 'ING', 'GM', 
        '005930.KS', 'MBG.DE', 'GE', 'PBR', 'BRK-B', 'AXAHY', 'FNMA', 'F', 
        'ALIZY', 'NTTYY', 'BNPQY', 'HPQ', 'T', 'ENGIE.PA', 'VLO', 'MCK', 
        '6501.T', 'CA.PA', 'EQNR', '5020.T', 'NSANY', '2317.TW', 'SAN', 'EXO.MI', 
        'BAC', 'SIEGY', 'G', 'LUKOY', 'VZ', 'JPM', 'ENLAY', 'HSBC', '1398.HK', 
        'AAPL', 'CVS', 'IBM', 'CRARY', 'TSCDY', 'C', 'CAH', 'BASFY', 'UNH', 
        'HMC', '034730.KS', 'PCRFY', 'SCGLY', 'PETRONAS.CS', 'BMW.DE', 'MT', 
        'NSRGY', 'B4B.DE', 'ECIFY', 'KR', 'MURGY', '0939.HK', 'COST', 'FMCC', 
        'WFC', '0941.HK', 'TEF', 'IOC.NS', '1288.HK', 'STLA', 'PG', 'SONY', 
        'BDORY', 'DTEGY', 'REPYY', 'ADM', '3988.HK', 'ABC', 'PTT.BK', 'TOSYY', 
        'DPSGY', 'RELIANCE.NS', '601668.SS'
    ]
    company_names_map = {
        'SHEL': '荷蘭皇家殼牌石油公司', 'XOM': '埃克森美孚', 'WMT': '沃爾瑪', 'BP': '英國石油', 
        '0386.HK': '中國石油化工（中石化）', 'PTR': '中國石油天然氣（中石油）', 'CVX': '雪佛龍', 
        'COP': '康菲石油', 'TM': '豐田汽車', 'TTE': '道達爾', 'VOW3.DE': '大眾', 
        '6178.T': '日本郵政控股', 'GLEN.L': '嘉能可', 'OGZPY': '俄羅斯天然氣工業', 
        'EOAN.DE': '意昂集團', 'E': '埃尼石油', 'ING': '荷蘭國際集團', 'GM': '通用汽車', 
        '005930.KS': '三星電子', 'MBG.DE': '戴姆勒', 'GE': '通用電氣', 'PBR': '巴西國家石油', 
        'BRK-B': '伯克希爾哈撒韋', 'AXAHY': '安盛', 'FNMA': '房利美', 'F': '福特', 
        'ALIZY': '安聯保險', 'NTTYY': '日本電報電話', 'BNPQY': '法國巴黎銀行', 'HPQ': '惠普', 
        'T': '美國電話電報（AT&T）', 'ENGIE.PA': '法國燃氣蘇伊士', 'VLO': '瓦萊羅能源', 
        'MCK': '麥克森', '6501.T': '日立', 'CA.PA': '家樂福', 'EQNR': '挪威國家石油', 
        '5020.T': 'JX 控股', 'NSANY': '日產', '2317.TW': '鴻海（富士康）', 'SAN': '西班牙國家銀行', 
        'EXO.MI': 'EXOR 集團', 'BAC': '美國銀行', 'SIEGY': '西門子', 'G': '意大利忠利保險', 
        'LUKOY': '盧克石油', 'VZ': '威瑞森', 'JPM': '摩根大通', 'ENLAY': '意大利國家電力', 
        'HSBC': '匯豐', '1398.HK': '中國工商銀行', 'AAPL': '蘋果', 'CVS': 'CVS Caremark', 
        'IBM': 'IBM', 'CRARY': '法國農業信貸', 'TSCDY': '樂購 Tesco', 'C': '花旗', 
        'CAH': '康德樂', 'BASFY': '巴斯夫', 'UNH': '聯合健康', 'HMC': '本田', 
        '034730.KS': 'SK 集團', 'PCRFY': '松下', 'SCGLY': '法國興業銀行', 
        'PETRONAS.CS': '馬來西亞國家石油', 'BMW.DE': 'BMW', 'MT': '安賽樂米塔爾', 
        'NSRGY': '雀巢', 'B4B.DE': '麥德龍', 'ECIFY': '法國電力', 'KR': '克羅格', 
        'MURGY': '慕尼黑再保', '0939.HK': '中國建設銀行', 'COST': '好市多', 'FMCC': '房地美', 
        'WFC': '富國銀行', '0941.HK': '中國移動', 'TEF': '西班牙電話', 'IOC.NS': '印度石油', 
        '1288.HK': '中國農業銀行', 'STLA': '標致', 'PG': '寶潔', 'SONY': '索尼', 
        'BDORY': '巴西銀行', 'DTEGY': '德國電信', 'REPYY': '雷普索爾', 'ADM': 'ADM 公司', 
        '3988.HK': '中國銀行', 'ABC': '美源伯根', 'PTT.BK': '泰國國家石油', 'TOSYY': '東芝', 
        'DPSGY': '德國郵政', 'RELIANCE.NS': '信實工業', '601668.SS': '中國建築工程'
    }

    start_date = '2013-01-01'
    end_date = '2025-10-21'
    
    results = [get_return(ticker, company_names_map.get(ticker, ''), start_date, end_date) for ticker in tickers_to_process]
    
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
