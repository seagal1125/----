import requests
import datetime
import time
import json
import os

# --- 組態設定 ---
DATA_DIR = "data"
START_YEAR = 2002
START_MONTH = 10
END_YEAR = 2025
END_MONTH = 10
BASE_URL = "https://www.twse.com.tw/rwd/zh/FTSE/TAI50I"

# 偽裝成瀏覽器發送請求，可提高成功率
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def generate_months():
    """產生器函式：生成所有需要抓取的年月"""
    year = START_YEAR
    month = START_MONTH
    while True:
        yield year, month
        if year == END_YEAR and month == END_MONTH:
            break
        month += 1
        if month > 12:
            month = 1
            year += 1

def fetch_and_save():
    """主程式：每個月的資料抓取並立即儲存成獨立檔案"""
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"開始抓取資料，每筆將儲存至 {DATA_DIR}/")

    for year, month in generate_months():
        date_str = f"{year}{month:02d}01"
        url = f"{BASE_URL}?date={date_str}&response=json"
        filename = os.path.join(DATA_DIR, f"TAI50I_{year}-{month:02d}.json")

        # 若檔案已存在則跳過
        if os.path.exists(filename):
            print(f"{filename} 已存在，跳過。")
            continue

        print(f"正在抓取 {year}-{month:02d} 的資料...", end='', flush=True)
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("stat") == "OK":
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(" ✅ 成功！已儲存。")
            else:
                print(f" ❌ 失敗 (stat: {data.get('stat')})")

        except requests.exceptions.RequestException as e:
            print(f" ❌ 網路錯誤: {e}")
        except json.JSONDecodeError:
            print(" ❌ 回傳內容非有效 JSON")

        # 禮貌性暫停，避免被封鎖
        time.sleep(5)

    print("\n✅ 全部資料抓取完成！")

if __name__ == "__main__":
    print("======================================================")
    print("台灣50報酬指數歷史資料批次下載腳本")
    print("======================================================")
    print(f"預計抓取區間: {START_YEAR}/{START_MONTH} - {END_YEAR}/{END_MONTH}")
    print("每月資料將各自儲存在 data/ 目錄中。")
    print("------------------------------------------------------")

    try:
        fetch_and_save()
    except KeyboardInterrupt:
        print("\n\n⚠️ 操作已由使用者取消。")