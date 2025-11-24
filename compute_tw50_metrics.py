
import os
import json
import pandas as pd
import numpy as np

def main():
    # --- 設定 ---
    DATA_DIR = '/Users/david/Library/Mobile Documents/com~apple~CloudDocs/0notebook-fromGithub/資產配置/Data'
    START_DATE_LIMIT = '2002-10-18'
    END_DATE_LIMIT = '2025-10-03'

    # --- 1. 讀取與解析資料 ---
    all_records = []
    if not os.path.isdir(DATA_DIR):
        print(f"錯誤：找不到資料目錄 {DATA_DIR}")
        return

    file_list = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.json')])

    for filename in file_list:
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                if content.get('stat') != 'OK' or 'data' not in content:
                    continue
                
                for item in content['data']:
                    roc_date_str = item[0].strip()
                    tr_index_str = item[2].strip()
                    
                    parts = roc_date_str.split('/')
                    year = int(parts[0]) + 1911
                    month = int(parts[1])
                    day = int(parts[2])
                    gregorian_date = f"{year:04d}-{month:02d}-{day:02d}"
                    
                    value = float(tr_index_str.replace(',', ''))
                    
                    all_records.append({'date': gregorian_date, 'value': value})
            except (json.JSONDecodeError, IndexError, TypeError, ValueError) as e:
                print(f"處理檔案 {filename} 時發生錯誤: {e}")
                continue

    if not all_records:
        print("沒有成功解析任何資料點。")
        return

    # --- 2. 建立並排序 DataFrame ---
    df = pd.DataFrame(all_records)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date').set_index('date')
    df = df[~df.index.duplicated(keep='first')]
    df = df.loc[START_DATE_LIMIT:END_DATE_LIMIT]

    # 增加數據清洗步驟，避免無效值(如0)影響計算
    df['value'] = df['value'].replace(0, np.nan).ffill()

    if df.empty:
        print("在指定的時間區間內沒有資料。")
        return

    # --- DEBUG: 檢查資料品質 ---
    print("--- DataFrame Head ---")
    print(df.head())
    print("\n--- NaN Check in 'value' column ---")
    print(df['value'].isnull().sum())
    
    # --- 3. 計算績效指標 ---
    rets = df['value'].pct_change().dropna()

    print("\n--- Daily Returns ('rets') Head ---")
    print(rets.head())

    start_price = df['value'].iloc[0]
    end_price = df['value'].iloc[-1]
    n_days = (df.index[-1] - df.index[0]).days
    years = n_days / 365.25
    cagr = (end_price / start_price) ** (1 / years) - 1 if years > 0 else 0

    rets = df['value'].pct_change().dropna()
    vol_annual = rets.std() * np.sqrt(252)
    sharpe_ratio = (rets.mean() / rets.std()) * np.sqrt(252) if rets.std() > 0 else 0

    cum_returns = (1 + rets).cumprod()
    running_max = cum_returns.cummax()
    drawdown = (cum_returns - running_max) / running_max
    max_dd = drawdown.min()

    # --- 4. 輸出結果 ---
    results = {
        "ticker": "台灣50報酬指數",
        "start_date": df.index[0].strftime('%Y-%m-%d'),
        "end_date": df.index[-1].strftime('%Y-%m-%d'),
        "cagr_pct": round(cagr * 100, 4),
        "annual_volatility_pct": round(vol_annual * 100, 4),
        "sharpe_ratio": round(sharpe_ratio, 4),
        "max_drawdown_pct": round(max_dd * 100, 4)
    }

    print(json.dumps(results, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
