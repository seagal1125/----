import pandas as pd
import io
import re

def parse_md_table(md_content: str) -> pd.DataFrame:
    """Parses the markdown table from the report into a pandas DataFrame."""
    table_str = md_content.split("## 百大公司完整名單與資料狀態")[1].split("## 研究結論")[0]
    
    lines = table_str.strip().split('\n')
    lines = [line.strip() for line in lines if not re.match(r'^\|:---:\|', line.strip())]
    lines = [line for line in lines if line]

    csv_like_str = "\n".join(lines)
    
    df = pd.read_csv(io.StringIO(csv_like_str), sep='|', skipinitialspace=True)
    df = df.iloc[:, 1:-1]
    df.columns = [col.strip() for col in df.columns]
    
    df['總報酬%'] = df['總報酬%'].str.replace('%', '').str.replace('+', '')
    df['總報酬%'] = pd.to_numeric(df['總報酬%'], errors='coerce')
    
    return df

def generate_new_markdown(original_content: str, winners: pd.DataFrame, losers: pd.DataFrame):
    """Generates the new, expanded markdown report."""
    winners = winners.sort_values(by='總報酬%', ascending=False)
    losers = losers.sort_values(by='總報酬%', ascending=False)

    winners_md = winners[['排名', '公司', 'Ticker', '總報酬%']].to_markdown(index=False, floatfmt=(None, None, None, ".2f"))
    losers_md = losers[['排名', '公司', 'Ticker', '總報酬%']].to_markdown(index=False, floatfmt=(None, None, None, ".2f"))

    section_to_replace = original_content.split("## 百大公司完整名單與資料狀態")[1].split("## 研究結論")[0]
    
    new_sections = f"""
## 績效超越 VT 名單 (共 {len(winners)} 家)

長期來看，這些公司憑藉其在產業中的領導地位、創新能力或受惠於總體經濟順風，取得了超越全球市場平均的驚人回報。

{winners_md}

## 績效落後 VT 名單 (共 {len(losers)} 家)

此名單中的公司多數來自週期性產業、面臨激烈競爭或在金融海嘯中元氣大傷，其長期股東回報顯著落後於市場指數。

{losers_md}
"""
    
    new_content = original_content.replace(section_to_replace, new_sections)
    
    return new_content

def generate_html_report(stats: dict, winners: pd.DataFrame, losers: pd.DataFrame, no_data: pd.DataFrame):
    """Generates a simple and beautiful HTML report using .format() for safety."""
    winners = winners.sort_values(by='總報酬%', ascending=False)
    losers = losers.sort_values(by='總報酬%', ascending=False)

    def style_return(r):
        if pd.isna(r): return 'N/A'
        color = '#28a745' if r > stats['vt_return_val'] else ('#dc3545' if r < 0 else '#ffc107')
        return f'<span style="color: {color}; font-weight: bold;">{r:+.2f}%</span>'

    winners_html_table = winners.copy()
    winners_html_table['總報酬%'] = winners_html_table['總報酬%'].apply(style_return)
    
    losers_html_table = losers.copy()
    losers_html_table['總報酬%'] = losers_html_table['總報酬%'].apply(style_return)

    html_template = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2008年財富100強 vs VT 績效分析報告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f8f9fa; color: #212529; margin: 0; padding: 2rem; }}
        .container {{ max-width: 960px; margin: auto; background: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1, h2 {{ color: #343a40; border-bottom: 2px solid #dee2e6; padding-bottom: 0.5rem; }}
        h1 {{ text-align: center; }}
        .summary {{ background-color: #e9ecef; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }}
        .stat {{ padding: 1rem; background: #fff; border-radius: 5px; text-align: center; }}
        .stat h3 {{ margin: 0 0 0.5rem 0; color: #495057; font-size: 1rem; }}
        .stat p {{ margin: 0; font-size: 1.5rem; font-weight: bold; }}
        .stat .vt-return {{ color: #007bff; }}
        .stat .win-rate {{ color: #28a745; }}
        .stat .avg-return {{ color: #ffc107; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        tr:hover {{ background-color: #e9ecef; }}
        .winners-table th {{ background-color: #d4edda; }}
        .losers-table th {{ background-color: #f8d7da; }}
        .nodata-table th {{ background-color: #e2e3e5; }}
        footer {{ text-align: center; margin-top: 2rem; color: #6c757d; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>2008年財富100強 vs VT 績效分析報告</h1>
        <p style="text-align: center; color: #6c757d;">分析區間：2008-10-15 至 2025-10-23</p>

        <div class="summary">
            <div class="stat">
                <h3>基準 (VT) 總報酬</h3>
                <p class="vt-return">{vt_return}</p>
            </div>
            <div class="stat">
                <h3>百大企業勝率</h3>
                <p class="win-rate">{win_rate}</p>
            </div>
            <div class="stat">
                <h3>可計算樣本平均報酬</h3>
                <p class="avg-return">{avg_return}</p>
            </div>
             <div class="stat">
                <h3>樣本報酬中位數</h3>
                <p class="avg-return">{median_return}</p>
            </div>
        </div>

        <h2>績效超越 VT 名單 ({len_winners} 家)</h2>
        <p>長期來看，這些公司憑藉其在產業中的領導地位、創新能力或受惠於總體經濟順風，取得了超越全球市場平均的驚人回報。</p>
        {winners_table}

        <h2>績效落後 VT 名單 ({len_losers} 家)</h2>
        <p>此名單中的公司多數來自週期性產業、面臨激烈競爭或在金融海嘯中元氣大傷，其長期股東回報顯著落後於市場指數。</p>
        {losers_table}
        
        <h2>無股價資料名單 ({len_nodata} 家)</h2>
        <p>下列公司因下市、被收購、轉為國營或數據源缺失，無法納入本次報酬計算。</p>
        {nodata_table}

        <footer>
            <p>本報告僅供資訊分享，不構成任何投資建議。</p>
        </footer>
    </div>
</body>
</html>
    '''
    
    return html_template.format(
        vt_return=stats['vt_return'],
        win_rate=stats['win_rate'],
        avg_return=stats['avg_return'],
        median_return=stats['median_return'],
        len_winners=len(winners),
        winners_table=winners_html_table[['排名', '公司', 'Ticker', '總報酬%']].to_html(index=False, classes='winners-table', escape=False),
        len_losers=len(losers),
        losers_table=losers_html_table[['排名', '公司', 'Ticker', '總報酬%']].to_html(index=False, classes='losers-table', escape=False),
        len_nodata=len(no_data),
        nodata_table=no_data[['排名', '公司']].to_html(index=False, classes='nodata-table')
    )

def main():
    # --- Config ---
    vt_return_val = 499.03
    report_path = "/Users/david/Library/Mobile Documents/com~apple~CloudDocs/0notebook-fromGithub/資產配置/分析報告/2008_FortuneTop100_vs_VT報告.md"
    new_md_path = "/Users/david/Library/Mobile Documents/com~apple~CloudDocs/0notebook-fromGithub/資產配置/分析報告/2008_FortuneTop100_vs_VT_完整分析報告.md"
    html_path = "/Users/david/Library/Mobile Documents/com~apple~CloudDocs/0notebook-fromGithub/資產配置/分析報告/2008_FortuneTop100_vs_VT_視覺化報告.html"

    # 1. Read and parse data
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    df = parse_md_table(content)

    # 2. Separate into groups
    winners = df[df['總報酬%'] > vt_return_val].copy()
    losers = df[df['總報酬%'] <= vt_return_val].copy()
    no_data = df[df['資料狀態'] == '無公開交易數據'].copy()
    
    # 3. Generate new Markdown file
    new_md_content = generate_new_markdown(content, winners, losers)
    with open(new_md_path, 'w', encoding='utf-8') as f:
        f.write(new_md_content)

    # 4. Generate HTML file
    stats = {
        "vt_return": f"+{vt_return_val:.2f}%",
        "vt_return_val": vt_return_val,
        "win_rate": f"{len(winners)} / 100",
        "avg_return": f"+{df['總報酬%'].mean():.2f}%",
        "median_return": f"+{df['總報酬%'].median():.2f}%"
    }
    html_content = generate_html_report(stats, winners, losers, no_data)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"報告已生成：")
    print(f"Markdown: {new_md_path}")
    print(f"HTML: {html_path}")

if __name__ == "__main__":
    main()