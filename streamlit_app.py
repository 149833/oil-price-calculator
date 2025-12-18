import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 設定網頁標題與圖示
st.set_page_config(page_title="中油油價計算器", page_icon="⛽", layout="centered")

st.title("⛽ 中油油價自動計算器")
st.markdown("自動從中油歷史價格網頁抓取最新數據")

# --- 抓取數據函數 ---
@st.cache_data(ttl=3600)  # 快取資料 1 小時，避免頻繁請求官網
def get_cpc_prices():
    url = "https://www.cpc.com.tw/historyprice.aspx?n=2890"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 抓取表格中第一列數據
        table = soup.find("table")
        first_row = table.find_all("tr")[1]
        cols = first_row.find_all("td")
        
        return {
            "date": cols[0].text.strip(),
            "92": float(cols[1].text.strip()),
            "95": float(cols[2].text.strip())
        }
    except Exception as e:
        st.error(f"無法抓取即時油價：{e}")
        return None

# --- 執行抓取 ---
prices = get_cpc_prices()

if prices:
    st.info(f"📅 最新調價日期：{prices['date']}")

    # --- 使用者輸入介面 ---
    # 選擇油品
    oil_option = st.radio("請選擇油品：", ["92 無鉛汽油", "95 無鉛汽油"], horizontal=True)
    
    # 基礎單價判斷
    base_price = prices["92"] if "92" in oil_option else prices["95"]
    
    # 折扣輸入（預設為 0）
    discount = st.number_input(f"每公升折扣金額 (元)", min_value=0.0, value=0.0, step=0.1)

    # 計算實付單價
    final_unit_price = base_price - discount
    
    st.subheader(f"💰 實付單價：{final_unit_price:.2f} 元/L")

    # --- 計算 80-150 元列表 ---
    data = []
    for total in range(80, 155, 5):
        liters = round(total / final_unit_price, 2)
        data.append({"總價 (元)": total, "公升數 (L)": liters})

    # 顯示表格
    df = pd.DataFrame(data)
    st.table(df) # 在手機上使用 table 顯示較為直觀

else:
    st.warning("目前無法取得數據，請確認網路連線或稍後再試。")
