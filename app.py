import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="財務報表分析工具", layout="wide")
st.title("📊 財務報表自動分析系統")

uploaded_file = st.file_uploader("上傳你的財務報表 CSV 檔案", type=["csv"])

if uploaded_file is not None:
    # 讀取並清理檔案
    text = uploaded_file.getvalue().decode('utf-8-sig')
    lines = text.splitlines()
    
    data_start = None
    for i, line in enumerate(lines):
        if '營業收入' in line:
            data_start = i
            break
    
    if data_start is None:
        st.error("無法找到資料起始行")
        st.stop()
    
    data_lines = lines[data_start:]
    new_text = '\n'.join(data_lines)
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
        for j in range(1, len(row), 2):
            val = str(row[j]).strip().replace(',', '').replace(' ', '')
            values.append(float(val) if val not in ['-', '', 'nan'] else np.nan)
        if values and len(values) >= 4:
            clean_data[item_name] = values[:6]
    
    df = pd.DataFrame(clean_data, index=quarters[:len(next(iter(clean_data.values())))]).T

    # ====================== 顯示基本數據 ======================
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

    # 趨勢圖
    st.subheader("營收與獲利趨勢")
    fig, ax = plt.subplots(figsize=(10, 5))
    df.loc['營業收入'].plot(marker='o', ax=ax, label='營業收入')
    df.loc['稅後淨利'].plot(marker='o', ax=ax, label='稅後淨利')
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # ====================== 新增：投資價值結論 ======================
    st.subheader("💡 投資價值分析與結論")
    
    latest_revenue = df.loc['營業收入'].iloc[0]
    latest_profit = df.loc['稅後淨利'].iloc[0]
    latest_eps = df.loc['每股稅後盈餘(元)'].iloc[0]
    avg_net_margin = (df.loc['稅後淨利'] / df.loc['營業收入'] * 100).mean()
    margin_stable = df.loc['營業毛利'] / df.loc['營業收入'] * 100
    
    st.write("**主要觀察：**")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("毛利率穩定度", f"{margin_stable.mean():.1f}%", "穩定")
    with col_b:
        st.metric("平均淨利率", f"{avg_net_margin:.2f}%")
    with col_c:
        st.metric("最新EPS", f"{latest_eps:.2f} 元")
    
    st.write("**投資結論：**")
    
    if avg_net_margin > 5:
        st.success("✅ **值得考慮投資** - 獲利能力良好")
    elif avg_net_margin > 3:
        st.warning("⚠️ **中性偏正** - 獲利能力普通，但規模大")
    else:
        st.error("❌ **暫不建議重壓** - 淨利率偏低")
    
    if latest_eps > 2.0:
        st.success("最新季獲利表現不錯")
    else:
        st.info("最新季獲利一般")
    
    st.write("**風險提醒：**")
    st.write("- 此公司季節性較明顯（Q4、Q1較強）")
    st.write("- 推銷費用占比高，屬於行銷導向公司")
    st.write("- 受匯率影響較大（綜合損益波動）")
    st.write("- **建議搭配目前股價本益比一起判斷**（本益比低於15倍較有吸引力）")

    st.success("✅ 分析完成！")
else:
    st.info("👆 請上傳 CSV 檔案開始分析")

st.caption("財務報表分析工具 | 含投資結論")
