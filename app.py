import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="財務報表分析工具", layout="wide")
st.title("📊 財務報表自動分析系統")

uploaded_file = st.file_uploader("上傳你的財務報表 CSV 檔案", type=["csv"])

if uploaded_file is not None:
    # 讀取原始文字
    text = uploaded_file.getvalue().decode('utf-8-sig')
    lines = text.splitlines()
    
    # 找到「營業收入」開始的真正資料行
    data_start = None
    for i, line in enumerate(lines):
        if '營業收入' in line:
            data_start = i
            break
    
    if data_start is None:
        st.error("無法找到資料起始行，請確認檔案包含「營業收入」")
        st.stop()
    
    # 只取從「營業收入」開始的資料
    data_lines = lines[data_start:]
    new_text = '\n'.join(data_lines)
    
    # 使用 StringIO 重新讀取
    from io import StringIO
    df_raw = pd.read_csv(StringIO(new_text), header=None, encoding='utf-8-sig')
    
    data = df_raw.reset_index(drop=True)
    quarters = ["最新季", "前一季", "前二季", "前三季", "前四季", "前五季"]
    
    clean_data = {}
    for _, row in data.iterrows():
        item_name = str(row[0]).strip()
        if item_name == "" or "財務報告書" in item_name or item_name.startswith("本業獲利"):
            continue
            
        values = []
        for j in range(1, len(row), 2):   # 取金額欄
            val = str(row[j]).strip().replace(',', '').replace(' ', '')
            if val in ['-', '', 'nan', '']:
                values.append(np.nan)
            else:
                try:
                    values.append(float(val))
                except:
                    values.append(np.nan)
        
        if values and len(values) >= 4:
            clean_data[item_name] = values[:6]
    
    if not clean_data:
        st.error("資料清理失敗，請檢查檔案格式")
        st.stop()
    
    df = pd.DataFrame(clean_data, index=quarters[:len(next(iter(clean_data.values())))]).T
    
    # 顯示結果
    st.subheader("財務數據總覽")
    st.dataframe(df.round(2), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("最新季營收", f"{df.loc['營業收入'].iloc[0]:,.0f} 億元")
        st.metric("最新季稅後淨利", f"{df.loc.get('稅後淨利', pd.Series([0])).iloc[0]:,.2f} 億元")
    with col2:
        st.metric("最新季 EPS", f"{df.loc.get('每股稅後盈餘(元)', pd.Series([0])).iloc[0]:.2f} 元")
        if '營業收入' in df.index and '稅後淨利' in df.index:
            avg_margin = (df.loc['稅後淨利'] / df.loc['營業收入'] * 100).mean()
            st.metric("平均淨利率", f"{avg_margin:.2f}%")
    
    # 趨勢圖
    st.subheader("營收與獲利趨勢")
    fig, ax = plt.subplots(figsize=(10, 5))
    df.loc['營業收入'].plot(marker='o', ax=ax, label='營業收入')
    if '稅後淨利' in df.index:
        df.loc['稅後淨利'].plot(marker='o', ax=ax, label='稅後淨利')
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    st.success("✅ 分析完成！")
else:
    st.info("👆 請上傳 CSV 檔案開始分析")

st.caption("財務報表分析工具 | 修正版")
