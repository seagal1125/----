
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
        .nodata-table th { background-color: #e2e3e5; }
        footer { text-align: center; margin-top: 3rem; color: #6c757d; font-size: 0.9rem; }
        .content-section { margin-bottom: 2rem; line-height: 1.7; }
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
        <div class="content-section">__OVERALL_SECTION__</div>
        <div class="content-section">
            <h2>績效超越 VT 名單 (__LEN_WINNERS__ 家)</h2>
            __WINNERS_TABLE__
        </div>
        <div class="content-section">
            <h2>績效落後 VT 名單 (__LEN_LOSERS__ 家)</h2>
            __LOSERS_TABLE__
        </div>
        <div class="content-section">__LIMITATIONS_SECTION__</div>
        <div class="content-section">__CONCLUSION_SECTION__</div>
        <footer><p>本報告僅供資訊分享，不構成任何投資建議。</p></footer>
    </div>
</body>
</html>
    