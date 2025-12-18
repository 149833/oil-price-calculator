import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="中油油價計算器", page_icon="⛽")
st.title("⛽ 中油 92/95 油價自動計算器")

# 抓取中油官網數據
@st.cache_data(ttl=3600)  # 每小時自動更新一次，避免過度抓取
def get_oil_prices():
    url = "https://www.cpc.com.tw/historyprice.aspx?n=2890"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        cols = soup.find("table").find_all("tr")[1].find_all("td")
        return {
            "date": cols[0].text.strip(),
            "92": float(cols[1].text.strip()),
            "95": float(cols[2].text.strip())
        }
    except:
        return None

prices = get_oil_prices()

if prices:
    st.info(f"📅 最新調價日期：{prices['date']}")
    
    # 介面選擇
    col1, col2 = st.columns(2)
    with col1:
        oil_type = st.selectbox("選擇油品", ["92 無鉛", "95 無鉛"])
    with col2:
        discount = st.number_input("每公升折扣 (元)", min_value=0.0, value=0.0, step=0.1)

    unit_price = prices["92"] if oil_type == "92 無鉛" else prices["95"]
    final_price = unit_price - discount

    st.subheader(f"💡 {oil_type} 折扣後：{final_price:.2f} 元/L")

    # 生成表格
    df = pd.DataFrame({
        "總價 (元)": [t for t in range(80, 155, 5)],
        "公升數 (L)": [round(t / final_price, 2) for t in range(80, 155, 5)]
    })
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.error("暫時無法連線至中油官網，請稍後再試。")
