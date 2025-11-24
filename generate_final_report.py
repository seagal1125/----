import pandas as pd
import io
import re
import markdown

def parse_full_md_report(md_content: str):
    """Parses the entire markdown report into structured data and HTML sections."""
    sections = {}
    parts = re.split(r'\n##\s+', md_content)
    
    intro_part = parts[0].split("##")[0].strip()
    sections['intro'] = markdown.markdown(intro_part)

    for part in parts[1:]:
        lines = part.split('\n', 1)
        title = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else ''
        
        key = title.split(' ')[0]
        if "績效超越" in title:
            sections['winners_text'] = markdown.markdown(content.split('| 排名')[0])
        elif "績效落後" in title:
            sections['losers_text'] = markdown.markdown(content.split('| 排名')[0])
        else:
            sections[key] = markdown.markdown(f"## {title}\n{content}")

    table_str = md_content.split("## 百大公司完整名單與資料狀態")[1].split("## 研究結論")[0]
    lines = table_str.strip().split('\n')
    lines = [line.strip() for line in lines if not re.match(r'^\|:---:|', line.strip())]
    lines = [line for line in lines if line]
    csv_like_str = "\n".join(lines)
    df = pd.read_csv(io.StringIO(csv_like_str), sep='|', skipinitialspace=True).iloc[:, 1:-1]
    df.columns = [col.strip() for col in df.columns]
    df['總報酬%'] = df['總報酬%'].str.replace('%', '').str.replace('+', '')
    df['總報酬%'] = pd.to_numeric(df['總報酬%'], errors='coerce')
    
    return df, sections

def generate_final_html_report(stats: dict, df: pd.DataFrame, sections: dict):
    """Generates the final, beautiful, and complete HTML report."""
    vt_return_val = stats['vt_return_val']
    winners = df[df['總報酬%'] > vt_return_val].copy().sort_values(by='總報酬%', ascending=False)
    losers = df[df['總報酬%'] <= vt_return_val].copy().sort_values(by='總報酬%', ascending=False)

    def style_return(r):
        if pd.isna(r): return 'N/A'
        color = '#28a745' if r > vt_return_val else ('#dc3545' if r < 0 else '#6c757d')
        return f'<span style="color: {color}; font-weight: bold;">{r:+.2f}%</span>'

    winners['總報酬%'] = winners['總報酬%'].apply(style_return)
    losers['總報酬%'] = losers['總報酬%'].apply(style_return)

    # Using simple .replace() to avoid any formatting issues.
    html_template = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__TITLE__</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f8f9fa; color: #212529; margin: 0; padding: 2rem; }
        .container { max-width: 960px; margin: auto; background: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1, h2 { color: #343a40; border-bottom: 2px solid #dee2e6; padding-bottom: 0.5rem; }
        h1 { text-align: center; font-size: 2.5rem; margin-bottom: 1rem; }
        h2 { margin-top: 2.5rem; }
        .summary { background-color: #e9ecef; padding: 1.5rem; border-radius: 8px; margin: 2rem 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
        .stat { padding: 1rem; background: #fff; border-radius: 5px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .stat h3 { margin: 0 0 0.5rem 0; color: #495057; font-size: 1rem; }
        .stat p { margin: 0; font-size: 1.75rem; font-weight: bold; }
        .stat .vt-return { color: #007bff; }
        .stat .win-rate { color: #28a745; }
        .stat .avg-return { color: #fd7e14; }
        .stat .median-return { color: #ffc107; }
        table { width: 100%; border-collapse: collapse; margin-top: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        th, td { padding: 0.85rem 1rem; text-align: left; border-bottom: 1px solid #dee2e6; }
        th { background-color: #f2f2f2; font-weight: 600; }
        tr:nth-child(even) { background-color: #f8f9fa; }
        .winners-table th { background-color: #d4edda; }
        .losers-table th { background-color: #f8d7da; }
        footer { text-align: center; margin-top: 3rem; color: #6c757d; font-size: 0.9rem; }
        .content-section { margin-bottom: 2rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>2008年財富100強 vs VT 績效分析</h1>
        <div class="content-section">__INTRO_SECTION__</div>
        <div class="summary">
            <div class="stat">
                <h3>基準 (VT) 總報酬</h3>
                <p class="vt-return">__VT_RETURN__</p>
            </div>
            <div class="stat">
                <h3>百大企業勝率</h3>
                <p class="win-rate">__WIN_RATE__</p>
            </div>
            <div class="stat">
                <h3>樣本平均報酬</h3>
                <p class="avg-return">__AVG_RETURN__</p>
            </div>
             <div class="stat">
                <h3>樣本報酬中位數</h3>
                <p class="median-return">__MEDIAN_RETURN__</p>
            </div>
        </div>
        <div class="content-section">__OVERALL_PERF_SECTION__</div>
        <div class="content-section">
            <h2>績效超越 VT 名單 (__LEN_WINNERS__ 家)</h2>
            __WINNERS_TEXT__
            __WINNERS_TABLE__
        </div>
        <div class="content-section">
            <h2>績效落後 VT 名單 (__LEN_LOSERS__ 家)</h2>
            __LOSERS_TEXT__
            __LOSERS_TABLE__
        </div>
        <div class="content-section">__LIMITATIONS_SECTION__</div>
        <div class="content-section">__CONCLUSION_SECTION__</div>
        <footer><p>本報告僅供資訊分享，不構成任何投資建議。</p></footer>
    </div>
</body>
</html>
    '''
    
    replacements = {
        "__TITLE__": stats['title'],
        "__INTRO_SECTION__": sections.get('intro', ''),
        "__VT_RETURN__": stats['vt_return'],
        "__WIN_RATE__": stats['win_rate'],
        "__AVG_RETURN__": stats['avg_return'],
        "__MEDIAN_RETURN__": stats['median_return'],
        "__OVERALL_PERF_SECTION__": sections.get('整體市場表現', ''),
        "__LEN_WINNERS__": str(len(winners)),
        "__WINNERS_TEXT__": sections.get('winners_text', ''),
        "__WINNERS_TABLE__": winners[['排名', '公司', 'Ticker', '總報酬%']].to_html(index=False, classes='winners-table', escape=False),
        "__LEN_LOSERS__": str(len(losers)),
        "__LOSERS_TEXT__": sections.get('losers_text', ''),
        "__LOSERS_TABLE__": losers[['排名', '公司', 'Ticker', '總報酬%']].to_html(index=False, classes='losers-table', escape=False),
        "__LIMITATIONS_SECTION__": sections.get('資料限制與特別說明', ''),
        "__CONCLUSION_SECTION__": sections.get('研究結論', '')
    }

    final_html = html_template
    for placeholder, value in replacements.items():
        final_html = final_html.replace(placeholder, value)

    return final_html

def main():
    md_path = "/Users/david/Library/Mobile Documents/com~apple~CloudDocs/0notebook-fromGithub/資產配置/分析報告/2008_FortuneTop100_vs_VT_完整分析報告.md"
    html_path = "/Users/david/Library/Mobile Documents/com~apple~CloudDocs/0notebook-fromGithub/資產配置/分析報告/2008_FortuneTop100_vs_VT_最終版報告.html"
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    df, sections = parse_full_md_report(md_content)
    
    vt_return_val = 499.03
    winners_count = len(df[df['總報酬%'] > vt_return_val])

    stats = {
        "title": "2008 財富100強 vs. VT 最終分析報告",
        "vt_return": f"+{vt_return_val:.2f}%",
        "vt_return_val": vt_return_val,
        "win_rate": f"{winners_count} / 100",
        "avg_return": f"+{df['總報酬%'].mean():.2f}%",
        "median_return": f"+{df['總報酬%'].median():.2f}%"
    }

    final_html = generate_final_html_report(stats, df, sections)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"Final HTML report successfully generated at: {html_path}")

if __name__ == "__main__":
    main()