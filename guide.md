# Fortune Global 500 Top-100 vs VT Return Comparison — Reproducibility Guide

本指南記錄 2008 年《财富》世界 500 强前 100 名公司相對 Vanguard 全世界股票 ETF（VT）長期報酬比較的完整計算流程，方便其他模型（例如 Gemini）照流程重算並核對結果。

---

## 1. 準備資料

1. 來源檔案：`歷年全球500大公司/csv_with_ticker/fortune_global500_2008.csv`。  
   - 這是已回寫過 ticker 的 CSV。若重新下載 HTML 產生原始檔，需先套用下表的 **Ticker 修正表** 再進入後續步驟。
2. 本次報告時間區間：`start = 2008-10-15`（公告日）、`end = 2025-10-23`（若無法抓到「今日」，則固定為此日期）。
3. 所有報酬使用 **auto_adjust 後的收盤價**（含股利再投資）計算簡單總報酬：`(end_price / start_price) - 1`。

### 1.1 Ticker 修正表（公告前 100 名）

| 公司名稱 | 修正後 Ticker | 備註 |
| --- | --- | --- |
| Total | `TTE` | 原檔為 `VTI` |
| Daimler | `MBG.DE` | 原檔 `DTG.DE` |
| China National Petroleum | `0857.HK` | 原檔 `CBUMY` |
| Berkshire Hathaway | `BRK-B` | 原檔 `BRK.B` |
| J.P. Morgan Chase & Co. | `JPM` | 原檔 `4JPM.TI` |
| Carrefour | `CA.PA` | 原檔 `CRERF` |
| Royal Bank of Scotland | `NWG.L` | 原檔 `RY.TO` |
| Siemens | `SIE.DE` | 原檔 `SHL.DE` |
| Hewlett-Packard | `HPQ` | 原檔 `HPE` |
| Nissan Motor | `7201.T` | 原檔 `NSANY` |
| Nippon Telegraph & Telephone | `9432.T` | 原檔 `NITT.VI` |
| Statoil Hydro | `EQNR` | 原檔 `HYFM` |
| LG | `066570.KS` | 原檔 `LGND` |
| Matsushita Electric Industrial（= Panasonic） | `6752.T` | 原檔 `1612.TW` |
| Telefónica | `TEF` | 原檔 `VIV` |
| France Telecom | `ORA.PA` | 原檔 `TEO` |
| SK Holdings | `034730.KS` | 原檔 `KO32.F` |
| AmerisourceBergen（現名 Cencora） | `COR` | 原檔 `ABG.BE` |
| Munich Re Group | `MUV2.DE` | 原檔 `1MUV2.MI` |

### 1.2 無法計算的 17 檔（標記為空 ticker）

Fortis、Dexia Group、State Grid、PEMEX、HBOS、Gazprom、Metro、Peugeot、Electricite de France、Fiat、Credit Suisse、U.S. Postal Service、Lukoil、Toshiba、Petronas、Suez、Merrill Lynch。  
原因多為退市、國營事業無上市資料或 ADR 永久下架。這 17 檔需維持空白並納入勝率分母。

---

## 2. 批次下載歷史價格

使用 `yfinance`（同 `stock_analyzer.py` 的 `compare_returns`）批次下載，自動調整價格即可避免自辦股利再投資。

### Python 範例程式
```python
import pandas as pd
import yfinance as yf
from pathlib import Path

START = pd.Timestamp('2008-10-15')
END = pd.Timestamp('2025-10-23')
csv_path = Path('歷年全球500大公司/csv_with_ticker/fortune_global500_2008.csv')
df = pd.read_csv(csv_path)
top100 = df[df['2008排名'].astype(float) <= 100][['公司', 'ticker']]

results = []
failed = []

for _, row in top100.iterrows():
    name = row['公司'].strip()
    ticker = row['ticker'].strip()
    if not ticker:  # 缺資料的 17 檔
        failed.append({'company': name, 'reason': 'no_ticker'})
        continue

    hist = yf.download(
        ticker,
        start=START - pd.Timedelta(days=5),
        end=END + pd.Timedelta(days=1),
        auto_adjust=True,
        interval='1d',
        progress=False
    )['Close'].dropna().sort_index()

    if hist.empty:
        failed.append({'company': name, 'ticker': ticker, 'reason': 'empty_data'})
        continue

    start_idx = hist.index.searchsorted(START)
    end_idx = hist.index.searchsorted(END, side='right') - 1

    if start_idx >= len(hist) or end_idx < 0:
        failed.append({'company': name, 'ticker': ticker, 'reason': 'no_data_in_range'})
        continue

    start_price = float(hist.iloc[start_idx])
    end_price = float(hist.iloc[end_idx])
    total_return = end_price / start_price - 1

    results.append({
        'company': name,
        'ticker': ticker,
        'start_price': start_price,
        'end_price': end_price,
        'total_return': total_return
    })

pd.DataFrame(results).to_csv('2008_top100_returns.csv', index=False)
pd.DataFrame(failed).to_csv('2008_top100_failures.csv', index=False)
```

### VT 的基準
```python
vt_hist = yf.download(
    'VT',
    start=START - pd.Timedelta(days=5),
    end=END + pd.Timedelta(days=1),
    auto_adjust=True,
    interval='1d',
    progress=False
)['Close'].dropna().sort_index()
vt_return = vt_hist.iloc[vt_hist.index.searchsorted(END, side='right') - 1] / \
            vt_hist.iloc[vt_hist.index.searchsorted(START)] - 1
```

---

## 3. 指標計算

假設 `returns_df = pd.read_csv('2008_top100_returns.csv')`：

1. **等權重總報酬**：`equal_weight = returns_df['total_return'].mean()`  
2. **中位數報酬**：`returns_df['total_return'].median()`  
3. **擊敗 VT 的股票數**：`hits = (returns_df['total_return'] > vt_return).sum()`  
4. **勝率（可計算樣本）**：`hits / len(returns_df)`  
5. **勝率（原始 100 檔分母）**：`hits / 100`（修正後報告採用此數字）  
6. **Top/Bottom 10**：`returns_df.nlargest(10, 'total_return')` / `returns_df.nsmallest(10, 'total_return')`

---

## 4. 檔案輸出

重算後請更新下列檔案：
1. `2008_top100_returns.csv`：所有可計算個股以及起迄價格、總報酬。  
2. `2008_top100_failures.csv`：缺失原因（含空 ticker、退市或資料不足）。  
3. （若需）`csv_with_ticker/fortune_global500_2008.csv` 也要同步回寫新的 ticker 修正，避免下次重複處理。

---

## 5. 報告撰寫重點（供驗證比對）

輸出報告已示範於 `分析報告/2008_FortuneTop100_vs_VT報告.md`，主要段落如下：

1. 數據來源、時間範圍、報酬計算方式。  
2. VT 與等權重組合報酬、勝率（須以 100 檔做母體）。  
3. 長期贏家與落後者（Top/Bottom 10 表格）。  
4. 資料限制：列出 17 檔缺資料公司與修正 ticker 表。  
5. 結論：比較 VT 與龍頭組合、對產業變化的觀察。

按照以上步驟即可重現原始計算流程並驗證最終結論。祝測試順利！
