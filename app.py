import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="財務報表分析工具", layout="wide")
st.title("📊 財務報表自動分析系統")

uploaded_file = st.file_uploader("上傳你的財務報表 CSV 檔案", type=["csv"])

if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file, header=None, encoding='utf-8-sig')
    
    data_start = None
    for i, row in df_raw.iterrows():
        if str(row[0]).strip().startswith('營業收入'):
            data_start = i
            break
    
    if data_start is None:
        st.error("無法辨識檔案格式，請確認包含「營業收入」")
        st.stop()
    
    data = df_raw.iloc[data_start:].reset_index(drop=True)
    quarters = ["最新季", "前一季", "前二季", "前三季", "前四季", "前五季"]
    
    clean_data = {}
    for _, row in data.iterrows():
        item_name = str(row[0]).strip()
        if item_name == "" or "財務報告書" in item_name:
            continue
        values = []
        for j in range(1, len(row), 2):
            val = str(row[j]).strip().replace(',', '').replace(' ', '')
            values.append(float(val) if val not in ['-', '', 'nan'] else np.nan)
        if values:
            clean_data[item_name] = values[:6]
    
    df = pd.DataFrame(clean_data, index=quarters[:len(list(clean_data.values())[0])]).T
    
    st.subheader("財務數據總覽")
    st.dataframe(df.round(2), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("最新季營收", f"{df.loc['營業收入'].iloc[0]:,.0f} 億元")
        st.metric("最新季稅後淨利", f"{df.loc['稅後淨利'].iloc[0]:,.2f} 億元")
    with col2:
        st.metric("最新季 EPS", f"{df.loc['每股稅後盈餘(元)'].iloc[0]:.2f} 元")
        avg_margin = (df.loc['稅後淨利'] / df.loc['營業收入'] * 100).mean()
        st.metric("平均淨利率", f"{avg_margin:.2f}%")
    
    st.subheader("營收與獲利趨勢")
    fig, ax = plt.subplots(figsize=(10, 5))
    df.loc['營業收入'].plot(marker='o', ax=ax, label='營業收入')
    df.loc['稅後淨利'].plot(marker='o', ax=ax, label='稅後淨利')
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    st.success("✅ 分析完成！")
else:
    st.info("👆 請上傳 CSV 檔案開始分析")

st.caption("財務報表分析工具")
