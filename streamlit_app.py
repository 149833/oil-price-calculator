import requests
from bs4 import BeautifulSoup

def get_cpc_92_price_from_history():
    """
    嘗試從中油網頁抓取 92 無鉛汽油價格。
    如果成功回傳價格(float)，失敗回傳 None。
    """
    url = "https://www.cpc.com.tw/historyprice.aspx?n=2890"
    
    try:
        response = requests.get(url, timeout=5) # 設定 5 秒超時，避免卡住
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"網頁連線異常 (狀態碼：{response.status_code})")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        
        for table in tables:
            headers = [th.text.strip() for th in table.find_all('th')]
            if "92 無鉛汽油" in str(headers):
                rows = table.find_all('tr')
                if len(rows) > 1:
                    latest_row = rows[1]
                    cols = latest_row.find_all('td')
                    
                    if len(cols) >= 2:
                        price_text = cols[1].text.strip()
                        date_text = cols[0].text.strip()
                        print(f"已成功抓取中油官網資料 (生效日期: {date_text})")
                        return float(price_text)
        
        print("警告：網頁結構改變，找不到價格資料。")
        return None

    except Exception as e:
        print(f"自動抓取失敗：{e}")
        return None

def get_valid_price_input():
    """
    當自動抓取失敗時，讓使用者手動輸入的函式
    """
    while True:
        try:
            user_input = input(">> 請手動輸入今日 '92無鉛汽油' 單價：")
            price = float(user_input)
            if price > 0:
                return price
            else:
                print("油價必須大於 0，請重新輸入。")
        except ValueError:
            print("格式錯誤，請輸入數字 (例如: 26.8)。")

def calculate_liters():
    print("--- 自動油價試算程式 (含手動備援) ---")
    
    # 1. 嘗試獲取油單價
    unit_price = get_cpc_92_price_from_history()
    
    # 如果抓取失敗 (unit_price 是 None)，切換為手動輸入模式
    if unit_price is None:
        print("無法取得線上價格，轉為手動輸入模式。")
        unit_price = get_valid_price_input()
        
    print(f"今日計算基準單價： {unit_price} 元/公升")
    
    # 2. 設定折扣
    try:
        discount_input = input("請輸入每公升折扣金額 (預設為0，直接按 Enter 跳過): ")
        if discount_input.strip() == "":
            discount = 0.0
        else:
            discount = float(discount_input)
    except ValueError:
        print("折扣輸入錯誤，將設為 0")
        discount = 0.0

    final_unit_price = unit_price - discount
    print(f"折扣後單價： {final_unit_price:.2f} 元/公升")
    print("-" * 35)
    print(f"{'總價 (元)':<10} | {'公升數 (L)':<10}")
    print("-" * 35)

    # 3. 總價設定從 80 開始，每 5 為單位，列至 150
    for total_price in range(80, 151, 5):
        if final_unit_price <= 0:
            print(f"{total_price:<14} | 錯誤 (單價<=0)")
        else:
            liters = total_price / final_unit_price
            liters_rounded = round(liters, 2)
            print(f"{total_price:<14} | {liters_rounded:<10}")

if __name__ == "__main__":
    calculate_liters()
