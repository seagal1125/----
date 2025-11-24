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
| 排名 | 公司 | Ticker | 資料狀態 | 總報酬% |
|:---:|:------|:-------|:-----------|:-------|
| 1 | WAL-MART STORES | WMT | 有完整股價 | +817.27% |
| 2 | EXXON MOBIL | XOM | 有完整股價 | +242.58% |
| 3 | ROYAL DUTCH SHELL | SHEL | 有完整股價 | +291.30% |
| 4 | BP | BP | 有完整股價 | +108.14% |
| 5 | TOYOTA MOTOR | TM | 有完整股價 | +384.72% |
| 6 | CHEVRON | CVX | 有完整股價 | +409.65% |
| 7 | ING GROUP | ING | 有完整股價 | +179.47% |
| 8 | TOTAL | TTE | 有完整股價 | +259.93% |
| 9 | GENERAL MOTORS | GM | 有完整股價 | +163.48% |
| 10 | CONOCOPHILLIPS | COP | 有完整股價 | +325.05% |
| 11 | DAIMLER | MBG.DE | 有完整股價 | +517.67% |
| 12 | GENERAL ELECTRIC | GE | 有完整股價 | +377.15% |
| 13 | FORD MOTOR | F | 有完整股價 | +938.73% |
| 14 | FORTIS |  | 無公開交易數據 | N/A |
| 15 | AXA | CS.PA | 有完整股價 | +410.71% |
| 16 | SINOPEC | 0386.HK | 有完整股價 | +186.66% |
| 17 | CITIGROUP | C | 有完整股價 | -19.32% |
| 18 | VOLKSWAGEN | VWAGY | 有完整股價 | -68.94% |
| 19 | DEXIA GROUP |  | 無公開交易數據 | N/A |
| 20 | HSBC HOLDINGS | HSBC | 有完整股價 | +133.41% |
| 21 | BNP PARIBAS | BNP.PA | 有完整股價 | +154.12% |
| 22 | ALLIANZ | ALV.DE | 有完整股價 | +914.34% |
| 23 | CREDIT AGRICOLE | ACA.PA | 有完整股價 | +244.01% |
| 24 | STATE GRID |  | 無公開交易數據 | N/A |
| 25 | CHINA NATIONAL PETROLEUM | 0857.HK | 有完整股價 | +178.10% |
| 26 | DEUTSCHE BANK | DBK.DE | 有完整股價 | +45.04% |
| 27 | ENI | E | 有完整股價 | +152.02% |
| 28 | BANK OF AMERICA CORP. | BAC | 有完整股價 | +182.80% |
| 29 | AT&T | T | 有完整股價 | +372.23% |
| 30 | BERKSHIRE HATHAWAY | BRK-B | 有完整股價 | +547.80% |
| 31 | UBS | UBS | 有完整股價 | +229.74% |
| 32 | J.P. MORGAN CHASE & CO. | JPM | 有完整股價 | +1067.34% |
| 33 | CARREFOUR | CA.PA | 有完整股價 | -9.64% |
| 34 | ASSICURAZIONI GENERALI | G.MI | 有完整股價 | +205.55% |
| 35 | AMERICAN INTERNATIONAL GROUP | AIG | 有完整股價 | +157.07% |
| 36 | ROYAL BANK OF SCOTLAND | NWG.L | 有完整股價 | -21.83% |
| 37 | SIEMENS | SIE.DE | 有完整股價 | +989.55% |
| 38 | SAMSUNG ELECTRONICS | 005930.KS | 有完整股價 | +1143.80% |
| 39 | ARCELORMITTAL | MT | 有完整股價 | -13.25% |
| 40 | HONDA MOTOR | HMC | 有完整股價 | +119.25% |
| 41 | HEWLETT-PACKARD | HPQ | 有完整股價 | +146.96% |
| 42 | PEMEX |  | 無公開交易數據 | N/A |
| 43 | SOCIETE GENERALE | GLE.PA | 有完整股價 | +114.57% |
| 44 | MCKESSON | MCK | 有完整股價 | +2021.39% |
| 45 | HBOS |  | 無公開交易數據 | N/A |
| 46 | INTERNATIONAL BUSINESS MACHINES | IBM | 有完整股價 | +503.66% |
| 47 | GAZPROM |  | 無公開交易數據 | N/A |
| 48 | HITACHI | 6501.T | 有完整股價 | +923.43% |
| 49 | VALERO ENERGY | VLO | 有完整股價 | +1649.19% |
| 50 | NISSAN MOTOR | 7201.T | 有完整股價 | +4.74% |
| 51 | TESCO | TSCO.L | 有完整股價 | +6.40% |
| 52 | E.ON | EOAN.DE | 有完整股價 | +56.28% |
| 53 | VERIZON COMMUNICATIONS | VZ | 有完整股價 | +283.94% |
| 54 | NIPPON TELEGRAPH & TELEPHONE | 9432.T | 有完整股價 | +572.38% |
| 55 | DEUTSCHE POST | DHL.DE | 有完整股價 | +274.53% |
| 56 | METRO |  | 無公開交易數據 | N/A |
| 57 | NESTLE | NESN.SW | 有完整股價 | +227.49% |
| 58 | SANTANDER CENTRAL HISPANO GROUP | SAN | 有完整股價 | +116.75% |
| 59 | STATOIL HYDRO | EQNR | 有完整股價 | +263.13% |
| 60 | CARDINAL HEALTH | CAH | 有完整股價 | +801.93% |
| 61 | GOLDMAN SACHS GROUP | GS | 有完整股價 | +780.95% |
| 62 | MORGAN STANLEY | MS | 有完整股價 | +1150.57% |
| 63 | PETROBRAS | PBR | 有完整股價 | +92.61% |
| 64 | DEUTSCHE TELEKOM | DTE.DE | 有完整股價 | +554.72% |
| 65 | HOME DEPOT | HD | 有完整股價 | +2897.74% |
| 66 | PEUGEOT |  | 無公開交易數據 | N/A |
| 67 | LG | 066570.KS | 有完整股價 | -2.11% |
| 68 | ELECTRICITE DE FRANCE |  | 無公開交易數據 | N/A |
| 69 | AVIVA | AV.L | 有完整股價 | +73.68% |
| 70 | BARCLAYS | BARC.L | 有完整股價 | +73.39% |
| 71 | FIAT |  | 無公開交易數據 | N/A |
| 72 | MATSUSHITA ELECTRIC INDUSTRIAL | 6752.T | 有完整股價 | +60.16% |
| 73 | BASF | BAS.DE | 有完整股價 | +268.92% |
| 74 | CREDIT SUISSE |  | 無公開交易數據 | N/A |
| 75 | SONY | SONY | 有完整股價 | +605.55% |
| 76 | TELEFONICA | TEF | 有完整股價 | -11.32% |
| 77 | UNICREDIT GROUP | UCG.MI | 有完整股價 | +40.52% |
| 78 | BMW | BMW.DE | 有完整股價 | +693.13% |
| 79 | PROCTER & GAMBLE | PG | 有完整股價 | +317.35% |
| 80 | CVS CAREMARK | CVS | 有完整股價 | +351.80% |
| 81 | UNITEDHEALTH GROUP | UNH | 有完整股價 | +2027.14% |
| 82 | HYUNDAI MOTOR | 005380.KS | 有完整股價 | +481.84% |
| 83 | U.S. POSTAL SERVICE |  | 無公開交易數據 | N/A |
| 84 | FRANCE TELECOM | ORA.PA | 有完整股價 | +118.15% |
| 85 | VODAFONE | VOD.L | 有完整股價 | -24.80% |
| 86 | SK HOLDINGS | 034730.KS | 有完整股價 | +795.13% |
| 87 | KROGER | KR | 有完整股價 | +666.61% |
| 88 | NOKIA | NOK | 有完整股價 | -35.77% |
| 89 | THYSSENKRUPP | TKA.DE | 有完整股價 | -29.56% |
| 90 | LUKOIL |  | 無公開交易數據 | N/A |
| 91 | TOSHIBA |  | 無公開交易數據 | N/A |
| 92 | REPSOL YPF | YPF | 有完整股價 | -19.34% |
| 93 | BOEING | BA | 有完整股價 | +587.28% |
| 94 | PRUDENTIAL | PRU | 有完整股價 | +322.75% |
| 95 | PETRONAS |  | 無公開交易數據 | N/A |
| 96 | AMERISOURCEBERGEN | COR | 有完整股價 | +3123.18% |
| 97 | SUEZ |  | 無公開交易數據 | N/A |
| 98 | MUNICH RE GROUP | MUV2.DE | 有完整股價 | +1182.92% |
| 99 | COSTCO WHOLESALE | COST | 有完整股價 | +2422.75% |
| 100 | MERRILL LYNCH |  | 無公開交易數據 | N/A |

## 研究結論
1. **被動全球配置長期仍具優勢**：即使入選 2008 年全球龍頭，等權持有 17 年仍落後持續再平衡的 VT。
2. **結構成長產業勝出**：醫療分銷、居家零售、科技設備等具持續需求的產業創造 10 倍以上報酬。
3. **區域與產業集中風險顯著**：歐洲金融、通信、傳統工業面臨的監管與技術變革，使得龍頭地位不保，提醒投資人注意長期再平衡的重要性。

## 研究檔案
- `歷年全球500大公司/2008_top100_returns_latest.csv`：83 檔可計算個股的詳細績效。
- `歷年全球500大公司/2008_top100_missing_latest.csv`：缺資料名單與排名。
- `歷年全球500大公司/2008_top100_summary_latest.json`：整體統計摘要。

*免責聲明：本報告僅供資訊分享，不構成任何投資建議。*
