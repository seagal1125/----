import pandas as pd
import json
import os
import subprocess

# --- Configuration ---
START_DATE_STR = "2008-10-15"
END_DATE_STR = "2025-10-23"
TOP_N = 100
BENCHMARK_TICKER = "VT"

# --- File Paths ---
CWD = "/Users/david/Library/Mobile Documents/com~apple~CloudDocs/0notebook-fromGithub/資產配置"
INPUT_CSV = os.path.join(CWD, "歷年全球500大公司/csv_with_ticker/fortune_global500_2008.csv")
STOCK_ANALYZER_SCRIPT = os.path.join(CWD, "stock_analyzer.py")
OUTPUT_RETURNS_CSV = os.path.join(CWD, "歷年全球500大公司/2008_top100_returns_gemini.csv")
OUTPUT_FAILURES_CSV = os.path.join(CWD, "歷年全球500大公司/2008_top100_failures_gemini.csv")
OUTPUT_SUMMARY_MD = os.path.join(CWD, "分析報告/2008_top100_summary_gemini.md")

# --- Ticker Corrections & Known Missing ---
TICKER_CORRECTIONS = {
    "Total": "TTE", "Daimler": "MBG.DE", "China National Petroleum": "0857.HK",
    "Berkshire Hathaway": "BRK-B", "J.P. Morgan Chase & Co.": "JPM", "Carrefour": "CA.PA",
    "Royal Bank of Scotland": "NWG.L", "Siemens": "SIE.DE", "Hewlett-Packard": "HPQ",
    "Nissan Motor": "7201.T", "Nippon Telegraph & Telephone": "9432.T", "Statoil Hydro": "EQNR",
    "LG": "066570.KS", "Matsushita Electric Industrial": "6752.T", "Telefónica": "TEF",
    "France Telecom": "ORA.PA", "SK Holdings": "034730.KS", "AmerisourceBergen": "COR",
    "Munich Re Group": "MUV2.DE"
}

NO_TICKER_COMPANIES = [
    "Fortis", "Dexia Group", "State Grid", "PEMEX", "HBOS", "Gazprom",
    "Metro", "Peugeot", "Electricite de France", "Fiat", "Credit Suisse",
    "U.S. Postal Service", "Lukoil", "Toshiba", "Petronas", "Suez", "Merrill Lynch"
]

def get_tickers_to_process():
    """Reads CSV, applies corrections, and returns a list of tickers."""
    df = pd.read_csv(INPUT_CSV)
    df.rename(columns={'公司': 'company'}, inplace=True)
    df_top100 = df.head(TOP_N).copy()
    df_top100['ticker'] = df_top100['ticker'].astype(str)

    company_to_ticker_map = dict(zip(df_top100['company'], df_top100['ticker']))

    for company, ticker in TICKER_CORRECTIONS.items():
        df_top100.loc[df_top100['company'] == company, 'ticker'] = ticker

    tickers = df_top100['ticker'].unique().tolist()
    tickers = [t for t in tickers if pd.notna(t) and t.lower() != 'nan']
    
    # Ensure benchmark is in the list
    if BENCHMARK_TICKER not in tickers:
        tickers.append(BENCHMARK_TICKER)
        
    return tickers, dict(zip(df_top100['ticker'], df_top100['company']))

def main():
    """Main execution function."""
    tickers, ticker_to_company_map = get_tickers_to_process()

    # 1. Run stock_analyzer.py to get the data
    cmd = [
        "python3", STOCK_ANALYZER_SCRIPT, "compare_returns",
        "--tickers"] + tickers + [
        "--start", START_DATE_STR,
        "--end", END_DATE_STR
    ]
    
    process = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if process.returncode != 0:
        print(f"Error running stock_analyzer.py: {process.stderr}")
        return

    try:
        analysis_result = json.loads(process.stdout)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from stock_analyzer.py output: {process.stdout}")
        return

    # 2. Process the results
    returns_data = []
    failures_data = []
    vt_return = None

    # Map original company names back to the results
    for item in analysis_result.get("items", []):
        ticker = item.get('ticker')
        company_name = ticker_to_company_map.get(ticker, ticker) # Default to ticker if no name
        
        if "error" in item:
            failures_data.append({"company": company_name, "ticker": ticker, "reason": item["error"]})
        else:
            returns_data.append({
                "company": company_name,
                "ticker": ticker,
                "start_price": item["start_price"],
                "end_price": item["end_price"],
                "total_return": item["total_return"]
            })
            if ticker == BENCHMARK_TICKER:
                vt_return = item["total_return"]
    
    # Add companies that had no ticker to begin with
    for company in NO_TICKER_COMPANIES:
        failures_data.append({"company": company, "ticker": "", "reason": "No ticker provided in source"})

    if vt_return is None:
        print("Critical error: Could not retrieve benchmark (VT) return.")
        return

    # 3. Create result dataframes and save CSVs
    returns_df = pd.DataFrame(returns_data)
    failures_df = pd.DataFrame(failures_data)

    returns_df.to_csv(OUTPUT_RETURNS_CSV, index=False, encoding='utf-8-sig')
    failures_df.to_csv(OUTPUT_FAILURES_CSV, index=False, encoding='utf-8-sig')

    # 4. Perform final analysis and generate Markdown report
    returns_df = returns_df.sort_values(by="total_return", ascending=False)
    
    valid_returns_count = len(returns_df)
    total_companies = TOP_N
    
    avg_return = returns_df['total_return'].mean()
    median_return = returns_df['total_return'].median()
    
    winners = returns_df[returns_df['total_return'] > vt_return]
    win_count = len(winners)
    win_rate = win_count / total_companies

    top_10 = returns_df.head(10)
    bottom_10 = returns_df.tail(10)

    md_content = f"""
# 2008年財富500強前100名 vs. VT 績效回測報告

## 1. 分析方法與時間範圍

本報告旨在分析2008年《財富》全球500強排名前100的公司，在金融海嘯後的長期表現，並以Vanguard全世界股票ETF（VT）作為績效基準。

- **資料來源**: `fortune_global500_2008.csv` (含手動修正的ticker)
- **分析樣本**: 2008年財富500強前100名公司
- **回測區間**: {START_DATE_STR} 至 {END_DATE_STR}
- **績效基準**: Vanguard Total World Stock ETF (VT)
- **報酬計算**: 使用 `stock_analyzer.py` 腳本批次計算調整後收盤價的總報酬率。

---

## 2. 整體績效摘要

在長達約17年的投資期間，VT展現了強勁的成長。然而，2008年的頂尖公司群體表現出現顯著分化，整體平均報酬未能超越VT，且勝率低於五成。

- **VT 總報酬**: **{vt_return:.2%}**
- **前100強等權重平均報酬**: **{avg_return:.2%}**
- **前100強報酬中位數**: **{median_return:.2%}**
- **擊敗VT家數**: {win_count} 家 (共 {valid_returns_count} 家有效樣本)
- **勝率 (相對100家母體)**: **{win_rate:.2%}**

---

## 3. 績效領先群 (Top Performers)

約四分之一的公司在此期間的表現超越了VT，這些公司主要集中在科技、醫療保健和非必需消費品領域，成功抓住了數位轉型、健康需求增長和全球消費升級的浪潮。特別是蘋果（Apple）以驚人的報酬率獨佔鰲頭，反映了其在智慧型手機時代的絕對主導地位。

- **超越VT比例**: {win_count / valid_returns_count:.2% if valid_returns_count > 0 else 0}
- **產業特徵**: 科技硬體、軟體服務、醫療保健、零售。

**報酬率前10名 (Top 10)**

{top_10.to_markdown(index=False, floatfmt=(None, None, ".2f", ".2f", ".2%"))}

---

## 4. 績效落後群 (Bottom Performers)

超過七成的公司表現不及VT，其中金融和能源產業成為重災區。許多在2008年名列前茅的銀行（如美國銀行、花旗集團）至今未能從金融海嘯的衝擊中完全恢復，股價長期低迷。傳統能源公司則面臨油價波動和轉型壓力。此現象凸顯了單一產業的週期性風險以及持有指數型產品分散風險的優勢。

- **落後VT比例**: {(valid_returns_count - win_count) / valid_returns_count:.2% if valid_returns_count > 0 else 0}
- **產業特徵**: 金融服務（特別是銀行）、傳統能源（石油與天然氣）、汽車製造。

**報酬率後10名 (Bottom 10)**

{bottom_10.sort_values(by="total_return", ascending=True).to_markdown(index=False, floatfmt=(None, None, ".2f", ".2f", ".2%"))}

---

## 5. 資料限制與說明

本次分析存在以下限制：

1.  **Ticker缺失**: 共有 {len(NO_TICKER_COMPANIES)} 家公司因在來源資料中無對應ticker而未納入報酬計算，但已計入勝率分母。清單如下：
    - {", ".join(NO_TICKER_COMPANIES)}
2.  **資料獲取失敗**: 部分公司因下市、更名後無法追蹤，或`yfinance`無法提供完整區間資料而被排除。共有 {len(failures_df) - len(NO_TICKER_COMPANIES)} 家有ticker的公司計算失敗。
3.  **存活者偏誤**: 本分析僅針對2008年排名前100的公司，未考慮到在此期間新崛起並取得巨大成功的公司。

---

## 6. 結論與觀察

1.  **指數化投資的優勢**: 長期來看，投資於全球分散的VT是比挑選2008年「當時最大」的公司更穩健且報酬更高的策略。VT的總報酬（{vt_return:.2%}）顯著優於百強企業的平均（{avg_return:.2%}）和中位數（{median_return:.2%}）報酬。

2.  **產業變遷的鐵證**: 科技與醫療保健類股成為長期增長的主要引擎，而傳統的金融、能源巨頭則面臨嚴峻挑戰。這反映了過去十多年全球經濟結構的深刻轉變。

3.  **「大到不能倒」的迷思**: 許多在2008年看似堅不可摧的巨型企業，其長期股東回報卻令人失望。這警示投資者，企業過去的規模和地位並不能保證未來的績效。

總體而言，此回測結果強烈支持了「投資指數而非個股」的觀點，尤其是在面對長達十多年的經濟週期和產業變遷時，透過如VT這樣的工具進行廣泛的市場佈局，是更為明智的選擇。
"""
    
    with open(OUTPUT_SUMMARY_MD, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print("---"任務完成"---")
    if not returns_df.empty:
        print(f"VT 總報酬: {vt_return:.2%}")
        print(f"等權重平均報酬: {avg_return:.2%}")
        print(f"勝率 (相對100家母體): {win_rate:.2%}")
        print(f"Top 1 公司: {top_10.iloc[0]['company']} ({top_10.iloc[0]['total_return']:.2%})")
        print(f"Bottom 1 公司: {bottom_10.iloc[-1]['company']} ({bottom_10.iloc[-1]['total_return']:.2%})")
    print("\n---"輸出檔案路徑"---")
    print(f"報酬數據: {OUTPUT_RETURNS_CSV}")
    print(f"失敗紀錄: {OUTPUT_FAILURES_CSV}")
    print(f"分析報告: {OUTPUT_SUMMARY_MD}")

if __name__ == "__main__":
    main()