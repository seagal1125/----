# 2008 年《财富》世界 500 强前 100 VS VT 長期績效回測報告

**方法論**  
- 來源：`歷年全球500大公司/csv_with_ticker/fortune_global500_2008.csv` 取排名前 100 家企業；官方榜單公告日為 **2008-10-15**。
- 工具：以 `stock_analyzer.py compare_returns` 批次向 yfinance 擷取每日還原股價，參數 `auto_adjust=False` 並選用 `Adj Close`；若起始日非交易日，會自動落在最接近的下一個交易日。
- 區間：公告日 (2008-10-15) 至今日 **2025-10-23**；以等權方式計算個股總報酬，不進行再平衡或值加權。
**統計區間**：2008-10-15 ～ 2025-10-23  
**樣本涵蓋**：原始 100 檔企業，其中 83 檔可計算、17 檔無股價資料  
**基準（VT）**：總報酬 +499.03%，CAGR 11.09%

---

## 整體市場表現
- `VT` 同期總報酬 **+499.03%**，年化報酬 **11.09%**。
- 83 檔可取得完整股價的公司平均總報酬 **+480.10%**，較 VT 落後 **18.93 個百分點**；中位數僅 **+263.13%**。
- 僅 **27 檔（32.5%）** 擊敗 VT；若以原始 100 檔計算，勝率降低為 27/100。
- 金融危機期間退市或無公開市場資料的 17 檔個股無法計算，詳列於「資料限制」段落。

## 長期贏家：頂尖 10 檔
1. **美國醫療分銷成為最大贏家**：Cencora（COR，舊稱 AmerisourceBergen）與 McKesson 搭上美國醫療支出成長，報酬雙雙突破 20 倍。
2. **房市復甦推動居家零售股暴衝**：金融海嘯後的低基期讓 Home Depot、Costco 在住房循環與會員經濟擴張下長期領跑。
3. **大型金融與科技股成功復原**：摩根大通、摩根士丹利回到資本市場舞台；三星電子在智慧型手機與半導體浪潮中提供 11 倍以上報酬。

| 公司 | Ticker | 總報酬% | CAGR% |
|:------------------------|:----------|----------:|-------:|
| AMERISOURCEBERGEN | COR | +3123.18% | +22.64% |
| HOME DEPOT | HD | +2897.74% | +22.12% |
| COSTCO WHOLESALE | COST | +2422.75% | +20.89% |
| UNITEDHEALTH GROUP | UNH | +2027.14% | +19.68% |
| MCKESSON | MCK | +2021.39% | +19.66% |
| VALERO ENERGY | VLO | +1649.19% | +18.31% |
| MUNICH RE GROUP | MUV2.DE | +1182.92% | +16.18% |
| MORGAN STANLEY | MS | +1150.57% | +16.00% |
| SAMSUNG ELECTRONICS | 005930.KS | +1143.80% | +15.97% |
| J.P. MORGAN CHASE & CO. | JPM | +1067.34% | +15.53% |

## 長期落後者：末段 10 檔
1. **歐洲工業與通信股長期結構性逆風**：Volkswagen、Thyssenkrupp、Vodafone 在電動化、鋼鐵產能過剩與通信競爭下持續萎縮。
2. **金融危機重災戶難以東山再起**：蘇格蘭皇家銀行、花旗即便存活，也因大幅稀釋與監管重壓長年落後。
3. **能源與大宗商品波動大**：Repsol、YPF、ArcelorMittal 等受油價與鋼鐵週期拖累，長期報酬仍為負。

| 公司 | Ticker | 總報酬% | CAGR% |
|:------------------------|:----------|----------:|-------:|
| VOLKSWAGEN | VWAGY | -68.94% | -6.64% |
| NOKIA | NOK | -35.77% | -2.57% |
| THYSSENKRUPP | TKA.DE | -29.56% | -2.04% |
| VODAFONE | VOD.L | -24.80% | -1.66% |
| ROYAL BANK OF SCOTLAND | NWG.L | -21.83% | -1.44% |
| REPSOL YPF | YPF | -19.34% | -1.25% |
| CITIGROUP | C | -19.32% | -1.25% |
| ARCELORMITTAL | MT | -13.25% | -0.83% |
| TELEFONICA | TEF | -11.32% | -0.70% |
| CARREFOUR | CA.PA | -9.64% | -0.59% |

## 資料限制與特別說明
- 下列 17 家企業因退市、國營或缺乏長期股價資料，無法計算回測：FORTIS、DEXIA GROUP、STATE GRID、PEMEX、HBOS、GAZPROM、METRO、PEUGEOT、ELECTRICITE DE FRANCE、FIAT、CREDIT SUISSE、U.S. POSTAL SERVICE、LUKOIL、TOSHIBA、PETRONAS、SUEZ、MERRILL LYNCH。
- 國營能源（如 PEMEX、PETRONAS）、歐洲銀行（FORTIS、DEXIA、HBOS、CREDIT SUISSE）與郵政等機構缺少持續公開市場，顯示選股策略需處理非生存者資料。
- GM 於 2010 年重新上市、034730.KS 等韓股於 2009 年後才有完整資料；報酬期間依最早可取得的調整收盤價開始。
- 匯率影響與再投資假設未納入，本回測僅觀察以美元計價的終值/起值比。

## 百大公司完整名單與資料狀態
## 績效超越 VT 名單 (共 27 家)

長期來看，這些公司憑藉其在產業中的領導地位、創新能力或受惠於總體經濟順風，取得了超越全球市場平均的驚人回報。

|   排名 | 公司                              | Ticker    |    總報酬% |
|-----:|:--------------------------------|:----------|--------:|
|   96 | AMERISOURCEBERGEN               | COR       | 3123.18 |
|   65 | HOME DEPOT                      | HD        | 2897.74 |
|   99 | COSTCO WHOLESALE                | COST      | 2422.75 |
|   81 | UNITEDHEALTH GROUP              | UNH       | 2027.14 |
|   44 | MCKESSON                        | MCK       | 2021.39 |
|   49 | VALERO ENERGY                   | VLO       | 1649.19 |
|   98 | MUNICH RE GROUP                 | MUV2.DE   | 1182.92 |
|   62 | MORGAN STANLEY                  | MS        | 1150.57 |
|   38 | SAMSUNG ELECTRONICS             | 005930.KS | 1143.80 |
|   32 | J.P. MORGAN CHASE & CO.         | JPM       | 1067.34 |
|   37 | SIEMENS                         | SIE.DE    |  989.55 |
|   13 | FORD MOTOR                      | F         |  938.73 |
|   48 | HITACHI                         | 6501.T    |  923.43 |
|   22 | ALLIANZ                         | ALV.DE    |  914.34 |
|    1 | WAL-MART STORES                 | WMT       |  817.27 |
|   60 | CARDINAL HEALTH                 | CAH       |  801.93 |
|   86 | SK HOLDINGS                     | 034730.KS |  795.13 |
|   61 | GOLDMAN SACHS GROUP             | GS        |  780.95 |
|   78 | BMW                             | BMW.DE    |  693.13 |
|   87 | KROGER                          | KR        |  666.61 |
|   75 | SONY                            | SONY      |  605.55 |
|   93 | BOEING                          | BA        |  587.28 |
|   54 | NIPPON TELEGRAPH & TELEPHONE    | 9432.T    |  572.38 |
|   64 | DEUTSCHE TELEKOM                | DTE.DE    |  554.72 |
|   30 | BERKSHIRE HATHAWAY              | BRK-B     |  547.80 |
|   11 | DAIMLER                         | MBG.DE    |  517.67 |
|   46 | INTERNATIONAL BUSINESS MACHINES | IBM       |  503.66 |

## 績效落後 VT 名單 (共 56 家)

此名單中的公司多數來自週期性產業、面臨激烈競爭或在金融海嘯中元氣大傷，其長期股東回報顯著落後於市場指數。

|   排名 | 公司                              | Ticker    |   總報酬% |
|-----:|:--------------------------------|:----------|-------:|
|   82 | HYUNDAI MOTOR                   | 005380.KS | 481.84 |
|   15 | AXA                             | CS.PA     | 410.71 |
|    6 | CHEVRON                         | CVX       | 409.65 |
|    5 | TOYOTA MOTOR                    | TM        | 384.72 |
|   12 | GENERAL ELECTRIC                | GE        | 377.15 |
|   29 | AT&T                            | T         | 372.23 |
|   80 | CVS CAREMARK                    | CVS       | 351.80 |
|   10 | CONOCOPHILLIPS                  | COP       | 325.05 |
|   94 | PRUDENTIAL                      | PRU       | 322.75 |
|   79 | PROCTER & GAMBLE                | PG        | 317.35 |
|    3 | ROYAL DUTCH SHELL               | SHEL      | 291.30 |
|   53 | VERIZON COMMUNICATIONS          | VZ        | 283.94 |
|   55 | DEUTSCHE POST                   | DHL.DE    | 274.53 |
|   73 | BASF                            | BAS.DE    | 268.92 |
|   59 | STATOIL HYDRO                   | EQNR      | 263.13 |
|    8 | TOTAL                           | TTE       | 259.93 |
|   23 | CREDIT AGRICOLE                 | ACA.PA    | 244.01 |
|    2 | EXXON MOBIL                     | XOM       | 242.58 |
|   31 | UBS                             | UBS       | 229.74 |
|   57 | NESTLE                          | NESN.SW   | 227.49 |
|   34 | ASSICURAZIONI GENERALI          | G.MI      | 205.55 |
|   16 | SINOPEC                         | 0386.HK   | 186.66 |
|   28 | BANK OF AMERICA CORP.           | BAC       | 182.80 |
|    7 | ING GROUP                       | ING       | 179.47 |
|   25 | CHINA NATIONAL PETROLEUM        | 0857.HK   | 178.10 |
|    9 | GENERAL MOTORS                  | GM        | 163.48 |
|   35 | AMERICAN INTERNATIONAL GROUP    | AIG       | 157.07 |
|   21 | BNP PARIBAS                     | BNP.PA    | 154.12 |
|   27 | ENI                             | E         | 152.02 |
|   41 | HEWLETT-PACKARD                 | HPQ       | 146.96 |
|   20 | HSBC HOLDINGS                   | HSBC      | 133.41 |
|   40 | HONDA MOTOR                     | HMC       | 119.25 |
|   84 | FRANCE TELECOM                  | ORA.PA    | 118.15 |
|   58 | SANTANDER CENTRAL HISPANO GROUP | SAN       | 116.75 |
|   43 | SOCIETE GENERALE                | GLE.PA    | 114.57 |
|    4 | BP                              | BP        | 108.14 |
|   63 | PETROBRAS                       | PBR       |  92.61 |
|   69 | AVIVA                           | AV.L      |  73.68 |
|   70 | BARCLAYS                        | BARC.L    |  73.39 |
|   72 | MATSUSHITA ELECTRIC INDUSTRIAL  | 6752.T    |  60.16 |
|   52 | E.ON                            | EOAN.DE   |  56.28 |
|   26 | DEUTSCHE BANK                   | DBK.DE    |  45.04 |
|   77 | UNICREDIT GROUP                 | UCG.MI    |  40.52 |
|   51 | TESCO                           | TSCO.L    |   6.40 |
|   50 | NISSAN MOTOR                    | 7201.T    |   4.74 |
|   67 | LG                              | 066570.KS |  -2.11 |
|   33 | CARREFOUR                       | CA.PA     |  -9.64 |
|   76 | TELEFONICA                      | TEF       | -11.32 |
|   39 | ARCELORMITTAL                   | MT        | -13.25 |
|   17 | CITIGROUP                       | C         | -19.32 |
|   92 | REPSOL YPF                      | YPF       | -19.34 |
|   36 | ROYAL BANK OF SCOTLAND          | NWG.L     | -21.83 |
|   85 | VODAFONE                        | VOD.L     | -24.80 |
|   89 | THYSSENKRUPP                    | TKA.DE    | -29.56 |
|   88 | NOKIA                           | NOK       | -35.77 |
|   18 | VOLKSWAGEN                      | VWAGY     | -68.94 |
## 研究結論
1. **被動全球配置長期仍具優勢**：即使入選 2008 年全球龍頭，等權持有 17 年仍落後持續再平衡的 VT。
2. **結構成長產業勝出**：醫療分銷、居家零售、科技設備等具持續需求的產業創造 10 倍以上報酬。
3. **區域與產業集中風險顯著**：歐洲金融、通信、傳統工業面臨的監管與技術變革，使得龍頭地位不保，提醒投資人注意長期再平衡的重要性。

## 研究檔案
- `歷年全球500大公司/2008_top100_returns_latest.csv`：83 檔可計算個股的詳細績效。
- `歷年全球500大公司/2008_top100_missing_latest.csv`：缺資料名單與排名。
- `歷年全球500大公司/2008_top100_summary_latest.json`：整體統計摘要。

*免責聲明：本報告僅供資訊分享，不構成任何投資建議。*
