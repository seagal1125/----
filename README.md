# Stock Analyzer Project

This project is a comprehensive toolkit for analyzing the Taiwan Stock Exchange (TWSE). It includes tools for fetching stock data, calculating returns, generating daily sector-based reports, retrieving historical constituents of ETFs like 0050, and performing deep-dive market trend analyses.

## Table of Contents

1.  [Installation](https://www.google.com/search?q=%23installation)
2.  [Tool Usage (CLI & MCP)](https://www.google.com/search?q=%23tool-usage-cli--mcp)
      * [`stock_analyzer.py` (CLI Mode)](https://www.google.com/search?q=%231-command-line-interface-cli-mode)
      * [`daily_sector_report.py` (Daily Reports)](https://www.google.com/search?q=%232-daily-twse-reports-cli)
      * [Codex CLI Prompts](https://www.google.com/search?q=%233-%E6%8C%87%E4%BB%A4%E5%BC%8F-promptcodex-cli)
      * [`get_0050_constituents.py`](https://www.google.com/search?q=%233-0050-constituent-lookup)
      * [`stock_analyzer.py` (MCP Server Mode)](https://www.google.com/search?q=%234-mcp-server-mode)
      * [`batch_daily_sector_report.py`](https://www.google.com/search?q=%235-%E6%89%B9%E6%AC%A1%E5%9B%9E%E5%A1%AB-batch)
3.  [分析任務與 Prompt 指南](https://www.google.com/search?q=%23%E5%88%86%E6%9E%90%E4%BB%BB%E5%8B%99%E8%88%87-prompt-%E6%8C%87%E5%8D%97)
      * [VT 持股回測報告](https://www.google.com/search?q=%23vt-%E6%8C%81%E8%82%A1%E5%9B%9E%E6%B8%AC%E5%A0%B1%E5%91%8A)
      * [特定族群單日急跌分析](https://www.google.com/search?q=%23%E7%89%B9%E5%AE%9A%E6%97%8F%E7%BE%A4%E5%96%AE%E6%97%A5%E6%80%A5%E8%B7%8C%E5%88%86%E6%9E%90)
      * [台股中期市場趨勢深度量化分析報告](https://www.google.com/search?q=%23%E5%8F%B0%E8%82%A1%E4%B8%AD%E6%9C%9F%E5%B8%82%E5%A0%B4%E8%B6%A8%E5%8B%A2%E6%B7%B1%E5%BA%A6%E9%87%8F%E5%8C%96%E5%88%86%E6%9E%90%E5%A0%B1%E5%91%8A-2025q3-q4)
      * [日報 HTML 轉換指南 (當日作業)](https://www.google.com/search?q=%23%E6%97%A5%E5%A0%B1-html-%E8%BD%89%E6%8F%9B%E6%8C%87%E5%8D%97-%E7%95%B6%E6%97%A5%E4%BD%9C%E6%A5%AD)

-----

## Installation

Before using the tools, install the required Python libraries:

```bash
pip install yfinance pandas numpy fastmcp
```

-----

## Tool Usage (CLI & MCP)

### 1\. Command-Line Interface (CLI) Mode (`stock_analyzer.py`)

The CLI mode allows you to directly call analysis functions from your terminal.

#### General Syntax

```bash
python stock_analyzer.py [COMMAND] [ARGUMENTS]
```

#### `get_stock_info`

Fetches basic information for a given stock ticker.

```bash
python stock_analyzer.py get_stock_info 2330.TW
```

#### `compare_returns`

Compares the performance (total return and CAGR) of stocks over a period.

```bash
python stock_analyzer.py compare_returns --tickers 6669.TW 2330.TW ^TWII --start 2025-01-01 --end 2025-11-19
```

### 2\. Daily TWSE reports (CLI)

Run the automation harness to regenerate all three daily markdown reports:

```bash
python daily_sector_report.py --top-n 3
```

Optional: Use `--date YYYY-MM-DD` to trace back to historical trading days:

```bash
python daily_sector_report.py --top-n 4 --date 2025-11-05
```

Using `daily_sector_report.py` recalculates 3 md files for the specified YYYYMMDD. The output files are located in the `分析報告/` directory:

  - `台股族群漲幅分析_<YYYYMMDD>.md`
  - `台股族群漲幅分析_<YYYYMMDD>_族群個股解讀.md`
  - `台股贏過大盤個股觀察_<YYYYMMDD>.md`

> **Note:** The text sections like「族群概覽」「解讀」「後續觀察」「觀察重點」「為何能贏過大盤」 in these md files are hardcoded boilerplate templates. Please use an LLM (Codex CLI) to re-analyze and complete the analysis, then write the results back to the md files.

If YYYY-MM-DD is today (e.g., 2025-11-24):
Organize into Animal Crossing style HTML, do not omit content, ensure format is easy to understand. Use LLM functions directly to organize into HTML. Do not use program code to convert files, otherwise daily formats will be inconsistent and cause errors. Save to the `TW_DAY` directory under the `HTML` directory, creating HTML files according to the date.

### 3\. 指令式 Prompt（Codex CLI）

若要以 LLM 生成更完整的敘事，可依序在 Codex CLI 中使用 `data/日報酬Prompt/` 下列三個 prompt：

1.  `1-stock_analyzer_prompt_20251110.txt`：呼叫 `stock_analyzer.py analyze_twse_today_by_sector` 生成主報告（檔名 `台股族群漲幅分析_<date>.md`）。
2.  `2-top_sector_contrib_prompt_20251110.txt`：輸入 `N`（預設 3）分析前 N 大族群，輸出 `台股族群漲幅分析_<date>_族群個股解讀.md`。
3.  `3-outperformers_prompt_20251110.txt`：列出贏過大盤的個股並說明原因，輸出 `台股贏過大盤個股觀察_<date>.md`。

建議流程：先執行 CLI 自動化快速取得底稿，再視需求用上述 prompt 重寫段落，使敘事與當天盤勢貼合。

### 3\. 0050 constituent lookup

Use `get_0050_constituents.py` to retrieve the historical component list for Yuanta Taiwan 50 (0050).

```bash
python get_0050_constituents.py 2025-10-22
```

*Add `--codes-only` for raw ticker codes.*

### 4\. MCP Server Mode

This mode runs the application as a background server for programmatic integration.

```bash
python stock_analyzer.py server
```

### 5\. 批次回填 (Batch)

若要一次回填全年有開市的日期，可使用批次腳本：

```bash
python batch_daily_sector_report.py --year 2025 --top-n 3 --max-dates 5
```

*Note: Downloads 1000+ daily stock lines per trading day; takes time.*

-----

# 分析任務與 Prompt 指南

本章節提供針對特定分析目標的 Prompt 指引，結合上述工具進行深度市場分析。

## VT 持股回測報告

參考 `分析報告/VT持股資料_2024-12.md` 抓前100大公司 利用 `stock_analyzer.py` 從 2025-01-01 計算到今天 2025-11-19 報酬率。
學習 `分析報告/2025_VT持股回測報告_2025YTD_2025-11-05.md` 的格式，出具分析報告並存到 md 檔案。

## 特定族群單日急跌分析

(範例：記憶體族群)

今天記憶體族群跌很多，你用 `stock_analyzer.py` 計算一下記憶體的跌幅，並分析原因。

## 台股中期市場趨勢深度量化分析報告 (2025Q3-Q4)

**最終目標：**

基於提供的 `分析報告/台股族群每日分析/202507-202509` 及 `分析報告/台股族群每日分析/` 目錄下，從 **2025年7月1日到11月13日** 的所有 Markdown 文件，產出一份關於此期間台股市場趨勢的深度、量化、且客觀的分析報告，存到一份新的 md 檔案。

### 核心要求與限制條件：

1.  **數據優先，文本為輔：**

      * \*\*主要限制：\*\*不能被報告中如「解讀」、「觀察重點」、「為何能贏過大盤」等樣板化、重複性高的描述性文字所誤導，這些段落是 hard code 在程式裡產生的。
      * \*\*核心方法：\*\*分析必須根植於文件中的純數據，例如：
          * 各產業族群的「對大盤貢獻度 (%)」。
          * 個股的「指數貢獻」、「日報酬」、「市值權重」。
          * 大盤整體的「等權漲幅」與「市值加權漲幅」之間的差異。
      * \*\*目的：\*\*從原始數據的重複模式中，獨立推導出市場的真實趨勢與結構，而非複述報告的現成結論。

2.  **加入總體量化指標：**

      * \*\*新增任務：\*\*在數據分析的基礎上，必須加入整個分析期間 (20250701-20251113) 的總體漲幅數據，使分析更具說服力。
      * **具體指標：**
          * 計算台股加權指數 (^TWII) 在此期間的總報酬率。
          * 計算關鍵個股或族群的總報酬率。
      * \*\*執行方式：\*\*選擇最快速、精確的方式（建議使用 `stock_analyzer.py` 工具計算）。

### 我的執行策略與步驟 (供參考)：

1.  **選擇最高效的工具：**

      * 判斷使用 `stock_analyzer.py` 的 `compare_returns` 功能是最佳選擇，能精確計算指定時間區間的總報酬率。

2.  **數據計算階段：**

      * 定義時間區間：`start="2025-07-01"`, `end="2025-11-13"`。
      * 定義計算標的：大盤 (^TWII)、關鍵個股（基於第一輪分析中頻繁出現的撐盤要角、核心族群）。
      * 執行指令：構建並執行 `python stock_analyzer.py compare_returns ...` 命令，獲取精確的總報酬率數據。

3.  **分析與整合階段：**

      * \*\*數據佐證：\*\*將計算出的總報酬率數據（例如：某個股 +30.15% vs. 大盤 +7.26%）作為最強力的證據，用來驗證和強化從每日數據中觀察到的趨勢。
      * **重新組織報告架構 (舉例，不可照抄)：**
        1.  \*開篇點題：\*首先呈現最重要的量化結果——大盤與關鍵個股的總報酬率對比，設定報告基調。
        2.  \*數據驅動的論證：\*分點闡述核心觀察，每一點都緊密結合「每日數據模式」和「總體量化數據」。
              * 論點一（趨勢核心）：用關鍵個股遠超大盤的總報酬率，證明「特定主題驅動的集中式上漲」。
              * 論點二（市場結構）：用權值股與大盤的差距，及每日「市值 vs. 等權」背離，證明「指數失真與廣度不足」。
              * 論點三（輪動角色）：根據每日數據中非核心族群貢獻度的短暫性，定義其「短線避風港」角色。
        3.  \*最終總結：\*綜合所有數據和分析，給出一個清晰、客觀且有數據支撐的最終市場定調。

## 日報 HTML 轉換指南 (當日作業)

若 YYYY-MM-DD 為今日 (例如 2025-11-24)：

整理成 動物森友會 風格的html 不要省略內容 格式易理解
你直接用LLM的功能整理出HTML
不要用寫程式的方式轉檔 不然每天的格式不統一 會出錯
存到HTML目錄下的 TW\_DAY目錄 按照日期建立html檔案

---
參考 分析報告/VT持股資料_2024-12.md 抓前100大公司 利用 stock_analyzer.py 從2025-01-01

 計算到今天 2025-11-19 報酬率 學習 分析報告/2025_VT持股回測報告_2025YTD_2025-11-05.md

 出具分析報告 存到md檔案  

---

今天記憶體族群跌很多 你用stock_analyzer.py 計算一下記憶體的跌幅 並分析原因

---


最終目標：

  基於提供的 分析報告/台股族群每日分析/202507-202509 及 分析報告/台股族群每日分析/ 目錄下 從 2025年7月1日到11月13日的所有 Markdown 文件，產出一份關於此期間台股市場趨勢的深度、量化、且客觀的分析報告，存到一份新的md檔案。

  核心要求與限制條件：

   1. 數據優先，文本為輔 (來自您的第二個指令)
       * 主要限制：不能被報告中如「解讀」、「觀察重點」、「為何能贏過大盤」等樣板化、重複性高的描述性文字所誤導，這些段落是hard code在程式裡產生的，所以每個檔案都一樣。
       * 核心方法：分析必須根植於文件中的純數據，例如：
           * 各產業族群的「對大盤貢獻度 (%)」。
           * 個股的「指數貢獻」、「日報酬」、「市值權重」。
           * 大盤整體的「等權漲幅」與「市值加權漲幅」之間的差異。
       * 目的：從原始數據的重複模式中，獨立推導出市場的真實趨勢與結構，而非複述報告的現成結論。

   2. 加入總體量化指標 (來自您的第三個指令)
       * 新增任務：在數據分析的基礎上，必須加入整個分析期間 (20250701-20251113) 的總體漲幅數據，使分析更具說服力。
       * 具體指標：
           * 計算台股加權指數 (^TWII) 在此期間的總報酬率。
           * 計算關鍵個股或族群的總報酬率。
       * 執行方式：在「從 .md 檔案手動整理」和「使用 stock_analyzer.py 工具計算」兩種方式中，選擇最快速、精確的一種。

  我的執行策略與步驟：

   1. 選擇最高效的工具：
       * 我判斷使用 stock_analyzer.py 的 compare_returns 功能是最佳選擇。因為它能精確計算指定時間區間的總報酬率，遠比手動從每日變動率中反推總漲幅來得快且準確。

   2. 數據計算階段：
       * 定義時間區間：start="2025-07-01", end="2025-11-13"。
       * 定義計算標的：
           * 大盤：^TWII。
           * 關鍵個股：基於第一輪分析中頻繁出現的撐盤要角，我選擇了最具代表性的幾家公司，你要挑出核心族群以及一些個股。
       * 執行指令：構建並執行 python stock_analyzer.py compare_returns ... 命令，獲取精確的總報酬率數據。

   3. 分析與整合階段：
       * 數據佐證：將計算出的總報酬率數據（例如，緯穎 +30.15% vs. 大盤 +7.26%）作為最強力的證據，用來驗證和強化從每日數據中觀察到的趨勢。
       * 重新組織報告架構(以下只是舉例 不能照抄 只可學架構 並重新分析)：
           1. 開篇點題：首先呈現最重要的量化結果——大盤與關鍵個股的總報酬率對比。這直接回應了您的最終要求，並立即設定了報告的基調。
           2. 數據驅動的論證：分點闡述我的核心觀察，每一點都必須緊密結合第一步的「每日數據模式」和第二步的「總體量化數據」。
               * 論點一（趨勢核心）：用關鍵個股遠超大盤的總報酬率，證明「AI 龍頭驅動的集中式上漲」這一結論。
               * 論點二（市場結構）：用台積電的總報酬率與大盤的差距，以及每日「市值 vs. 等權」的背離，證明「指數失真與廣度不足」的現象。
               * 論點三（輪動角色）：根據每日數據中非電族群貢獻度的短暫與不持續性，定義其「短線避風港」的角色。
           3. 最終總結：綜合所有數據和分析，給出一個清晰、客觀且有數據支撐的最終市場定調。

---



# Stock Analyzer

This is a versatile stock analysis tool that provides functionalities both as a command-line interface (CLI) and as an MCP (Machine-to-Machine Communication Protocol) server.

## Installation

Before using the tool, you need to install the required Python libraries. You can do this using pip:

```bash
pip install yfinance pandas numpy fastmcp
```

## Usage

The script `stock_analyzer.py` can be used in two modes: CLI or MCP server.

### 1. Command-Line Interface (CLI) Mode

The CLI mode allows you to directly call analysis functions from your terminal.

#### General Syntax

```bash
python stock_analyzer.py [COMMAND] [ARGUMENTS]
```

---

#### `get_stock_info`

Fetches basic information for a given stock ticker.

**Usage:**

```bash
python stock_analyzer.py get_stock_info <TICKER>
```

**Example:**

```bash
python stock_analyzer.py get_stock_info 2330.TW
```

---

#### `compare_returns`

Compares the performance (total return and CAGR) of one or more stocks over a specified period.

**Usage:**

```bash
python stock_analyzer.py compare_returns --tickers <TICKER_1> <TICKER_2> ... --start <YYYY-MM-DD> --end <YYYY-MM-DD>
```

**Arguments:**

*   `--tickers`: A list of stock tickers to compare.
*   `--start`: The start date for the comparison (in YYYY-MM-DD format).
*   `--end`: The end date for the comparison (in YYYY-MM-DD format).

**Example:**

```bash
python stock_analyzer.py compare_returns --tickers 6669.TW 2330.TW --start 2025-01-01 --end 2025-10-22
```

### 2. Daily TWSE reports (CLI)

Run the automation harness to regenerate all三份日報 Markdown：

```bash
python daily_sector_report.py --top-n 3
```

可選 `--date YYYY-MM-DD` 追溯歷史交易日，例如：

```bash
python daily_sector_report.py --top-n 4 --date 2025-11-05
```
使用 daily_sector_report.py  重新計算YYYYMMDD的3個md檔案
產出的3個md檔案位於 `分析報告/` 目錄下：

- `台股族群漲幅分析_<YYYYMMDD>.md`
- `台股族群漲幅分析_<YYYYMMDD>_族群個股解讀.md`
- `台股贏過大盤個股觀察_<YYYYMMDD>.md`

> 注意：這3個md檔案的「族群概覽」「解讀」「後續觀察」「觀察重點」「為何能贏過大盤」文字為程式硬編碼範本，請再用 LLM（Codex CLI）重新分析，少的部分也要補齊分析，分析結果回寫md檔案。

YYYY-MM-DD為今日 2025-11-26

整理成 動物森友會 風格的html 不要省略內容 格式易理解 
你直接用LLM的功能整理出HTML
不要用寫程式的方式轉檔 不然每天的格式不統一 會出錯
存到HTML目錄下的 TW_DAY目錄 按照日期建立html檔案 現在還沒有13:30收盤 要註明是盤中的分析 盤中要再將html存入mid目錄 如果html已經存在 你就要依序再存成v2 v3 v4 ...

### 3. 指令式 Prompt（Codex CLI）

若要以 LLM 生成更完整的敘事，可依序在 Codex CLI 中使用 `data/日報酬Prompt/` 下列三個 prompt：

1. `1-stock_analyzer_prompt_20251110.txt`：呼叫 `stock_analyzer.py analyze_twse_today_by_sector` 生成主報告（檔名 `台股族群漲幅分析_<date>.md`）。
2. `2-top_sector_contrib_prompt_20251110.txt`：輸入 `N`（預設 3）分析前 N 大族群，輸出 `台股族群漲幅分析_<date>_族群個股解讀.md`。
3. `3-outperformers_prompt_20251110.txt`：列出贏過大盤的個股並說明原因，輸出 `台股贏過大盤個股觀察_<date>.md`。

建議流程：先執行 CLI 自動化快速取得底稿，再視需求用上述 prompt 重寫「族群概覽」「解讀」「觀察重點」等段落，使敘事與當天盤勢貼合。

### 3. 0050 constituent lookup

Use `get_0050_constituents.py` to retrieve the historical component list for Yuanta Taiwan 50 (0050) on any date.

**Usage:**

```bash
python get_0050_constituents.py <DATE>
```

* `DATE` accepts `YYYY-MM-DD` or `YYYY-MM`.
* Add `--codes-only` if you prefer raw ticker codes without company names.

**Example:**

```bash
python get_0050_constituents.py 2025-10-22
```

### 4. MCP Server Mode

### 5. 批次回填 (Batch)

若要一次回填全年有開市的日期，可使用批次腳本：

```bash
python batch_daily_sector_report.py --year 2025 --top-n 3 --max-dates 5
```

- 會以 yfinance 的 `^TWII` 日線推導當年所有交易日，逐日呼叫 CLI 產出三份報告。
- `--through YYYY-MM-DD` 可提前結束；`--max-dates` 可限制處理天數以利測試（可省略）。
- 注意：每個交易日都會重新下載 1000+ 檔台股日線，時間較長，建議在網路穩定時執行。

This mode runs the application as a background server, listening for JSON-RPC commands over standard input/output. This is intended for programmatic integration with other tools.

**To run the server:**

```bash
python stock_analyzer.py server
```

The server will start and wait for commands. You can then send JSON-RPC requests to its standard input.
