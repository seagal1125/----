# Python 腳本功能總覽

| 檔名 | 功能簡述 |
| --- | --- |
| build_vt_performance_dataset.py | 呼叫 `mcp_stock.compare_returns` 批次下載 VT 與主要持股的一年期報酬，輸出為 `vt_performance_results_latest.json`，方便後續報告生成。 |
| bulk_performance_snapshot.py | 針對預先列出的眾多股票，自 2013 年起下載調整後收盤價並計算總報酬率，輸出為 JSON 陣列做臨時分析。 |
| compute_tw50_metrics.py | 解析本地 TWSE 0050 報酬指數資料，完成日期轉換、清洗與 CAGR、波動度、Sharpe、最大回撤等指標計算。 |
| download_tw50_index_history.py | 依月份呼叫證交所 API 下載台灣 50 報酬指數資料，逐檔儲存成 JSON 並包含失敗與重試處理。 |
| extract_vt_top100_tickers_2024.py | 讀取 `vt_holdings_snapshot_2024-04-30.json`，依國別附加 yfinance 尾碼，輸出前 100 大持股的可用代號列表。 |
| extract_vt_top101_tickers_from_md.py | 解析 `vt_holdings.md` 表格，擷取 VT 及前 100 大持股代號，提供後續腳本直接引用。 |
| get_0050_constituents.py | CLI 工具，依指定日期回溯 0050 成分股名單，可選擇只輸出代號或含公司名稱。 |
| list_vt_top100_names.py | 從 `vt_holdings_snapshot_latest.json` 印出前 100 大持股的原文名稱，方便快速檢視。 |
| mcp_stock.py | FastMCP 伺服器，對外提供 yfinance 驅動的股價查詢、報酬計算、風險指標與多標的比較等工具。 |
| mcp_stock_cli_client.py | 以 CLI 形式包裝與 `mcp_stock.py` 相同的功能，適合在終端機互動操作。 |
| simple_return_comparator.py | 下載兩檔股票在指定區間內的價格，計算單純報酬率並於終端機顯示。 |
| stock_analyzer.py | 核心分析腳本，兼具 CLI 與 MCP 伺服器模式，可取得基本資訊並比較多檔股票的收益表現。 |
| vt_bollinger_backtest_cli.py | 針對 VT 實作布林通道策略回測，輸出勝率與平均等待天數等摘要報告。 |
| vt_bollinger_backtest_report.py | 與 `vt_bollinger_backtest_cli.py` 邏輯相同，但著重於生成完整報告文字以供展示。 |
| vt_bollinger_parameter_optimizer.py | 對布林通道期間與標準差倍數進行網格搜尋，比較訊號進場與單筆投入的超額報酬。 |
| vt_holdings_markdown_basic.py | 從 `vt_holdings_snapshot_latest.json` 建立含排名與中文對照的 Markdown 表格。 |
| vt_holdings_markdown_from_temp.py | 以暫存檔 `vt_holdings_temp.json` 為來源生成 Markdown，完成後會刪除暫存檔。 |
| vt_holdings_markdown_full_final.py | 企圖提供完整持股表格與中文名稱，但程式內含未結束字串，執行前需先修正。 |
| vt_holdings_markdown_full_v2.py | `vt_holdings_snapshot_latest.json` 版本的改寫，加強中文名稱映射；目前同樣存在字串換行錯誤需處理。 |
| vt_holdings_markdown_suffix_heuristics.py | 對不同 ISIN 國別套用 yfinance 尾碼或特殊規則，再輸出 Markdown 表格。 |
| vt_holdings_markdown_ticker_suffix.py | 針對台灣等市場補上 `.TW` 等尾碼，同步維持原始代號的中文對照。 |
| vt_performance_report_builder.py | 讀取績效 JSON 與名稱對照，輸出包含贏家/落後者解析的 Markdown 報告，最後刪除來源檔。 |
| vt_performance_report_builder_v2.py | 舊版報告產生器，維持完整排序結果並具備中文名稱補充。 |
| vt_strategy_deployment_comparator.py | 針對 VT 比較期初單筆、布林訊號進場與 24 個月 DCA，多角度呈現策略績效並分析等待時間。 |

> 註：`vt_performance_report_template.md` 與 `vt_performance_report_template_v1.md` 為報告模板原稿，可配合上述生成器覆寫內容。另 `mcp_stock.py`、`stock_analyzer.py` 與 `get_0050_constituents.py` 已依 README 說明保留原檔名。
