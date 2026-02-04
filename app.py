import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import os
import urllib.request
import math
import io

# ---------------------------------------------------------
# 1. 페이지 설정
# ---------------------------------------------------------
st.set_page_config(page_title="Quant Farming Pro", page_icon="🚜", layout="wide")

st.markdown("""
    <style>
        .block-container {padding-top: 2rem; padding-bottom: 5rem;}
        html {scroll-behavior: smooth;}
        .stButton button {width: 100%; border-radius: 5px;}
        /* 테이블 헤더 스타일 */
        thead tr th:first-child {display:none}
        tbody th {display:none}
        
        /* 버튼 스타일링 */
        .chart-btn {
            background-color: #e3f2fd; color: #1565c0; 
            border: 1px solid #1565c0; border-radius: 5px; 
            padding: 5px 10px; cursor: pointer; text-decoration: none; font-size: 12px;
        }
        .chart-btn:hover {background-color: #bbdefb;}
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def set_font_korean():
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        urllib.request.urlretrieve(url, font_path)
    
    fe = fm.FontEntry(fname=font_path, name='NanumGothic')
    fm.fontManager.ttflist.insert(0, fe)
    plt.rc('font', family='NanumGothic')
    plt.rcParams['axes.unicode_minus'] = False
    return 'NanumGothic'

FONT_NAME = set_font_korean()

# ---------------------------------------------------------
# 2. 로직 및 데이터 (V9.8 동일)
# ---------------------------------------------------------
def calculate_indicators(df):
    cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for c in cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce')
    if len(df) < 52: return df

    for w in [5, 20, 60, 112, 224]:
        df[f'MA{w}'] = df['Close'].rolling(w).mean()

    df['F_Mid'] = df['Close'].rolling(window=38).mean()
    df['F_Std'] = df['Close'].rolling(window=38).std()
    df['Farming_Line']  = df['F_Mid'] + (df['F_Std'] * 0.6)

    high_9 = df['High'].rolling(window=9).max()
    low_9 = df['Low'].rolling(window=9).min()
    df['Tenkan'] = (high_9 + low_9) / 2
    high_26 = df['High'].rolling(window=26).max()
    low_26 = df['Low'].rolling(window=26).min()
    df['Kijun'] = (high_26 + low_26) / 2
    df['Span1'] = (df['Tenkan'] + df['Kijun']) / 2
    high_52 = df['High'].rolling(window=52).max()
    low_52 = df['Low'].rolling(window=52).min()
    df['Span2'] = (high_52 + low_52) / 2
    df['Amount'] = df['Close'] * df['Volume']
    return df

@st.cache_data(ttl=3600)
def get_stock_data(code):
    try:
        df = fdr.DataReader(code, (datetime.now()-timedelta(days=730)))
        if df is None or df.empty: return None
        df = calculate_indicators(df)
        return df
    except: return None

def analyze_nongsa(row, mode):
    try:
        code = str(row['Code']); name = row['Name']; market = row.get('Market', 'KOSDAQ')
        df = get_stock_data(code)
        if df is None or len(df) < 130: return None
        
        curr = df['Close'].iloc[-1]; t = df.iloc[-1]; y = df.iloc[-2]
        score_str=""; stop=0; support=0
        
        ma224 = t.get('MA224', 0); ma5 = t.get('MA5', 0); span1 = t.get('Span1', 0)
        if ma224 == 0 or ma5 == 0 or span1 == 0: return None
        
        is_safe = (t['Close'] >= t['Open']) or (curr >= ma5)
        if not is_safe: return None

        if mode == 'N1':
            farming_line = t.get('Farming_Line', 0)
            if farming_line == 0: return None
            gap = (curr - farming_line) / farming_line * 100
            recent_lows = df['Low'].iloc[-5:].min()
            was_below = recent_lows < farming_line
            if 0 <= gap <= 2.0 and was_below and t['Amount'] > 3e8:
                score_str = f"🎯 파종 맥점 ({gap:.2f}%)" 
                support = farming_line 
                stop = int(support * 0.97)

        elif mode == 'N2':
            span2 = t.get('Span2', 0)
            cloud_gap = abs(span1 - span2)
            is_thin_cloud = (cloud_gap / curr) <= 0.04
            cloud_bottom = min(span1, span2)
            recent_low = df['Low'].iloc[-40:].min()
            is_floor = (curr - recent_low) / recent_low <= 0.15
            if is_thin_cloud and is_floor:
                score_str = "🚜 농사 맥점 (구름대)"
                support = min(cloud_bottom, ma224) 
                stop = int(support * 0.96)

        if not score_str: return None

        return {
            'Market': market, 'Name': name, 'Code': code, 
            'Close': int(curr), 'Change': round((curr-y['Close'])/y['Close']*100, 2),
            'Note': score_str, 'Target': int(curr*1.15), 'StopLoss': stop, 
            'Support': int(support), 'Amount': int(t['Amount'])
        }
    except: return None

def create_chart_figure(code, name, score_str, scenario_lines=None):
    df = get_stock_data(code)
    if df is None: return None
    
    if not isinstance(df.index, pd.DatetimeIndex): df.index = pd.to_datetime(df.index)
    plot_df = df.iloc[-150:] if len(df)>150 else df
    dates = plot_df.index
    
    fig = plt.figure(figsize=(12, 8), constrained_layout=True)
    gs = fig.add_gridspec(2, 1, height_ratios=[4, 1])
    ax1 = fig.add_subplot(gs[0, 0]); ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)
    
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('#fcfcfc'); ax2.set_facecolor('#fcfcfc')

    if 'Span1' in plot_df.columns and 'Span2' in plot_df.columns:
        ax1.fill_between(dates, plot_df['Span1'], plot_df['Span2'], where=plot_df['Span1']>=plot_df['Span2'], facecolor='#2ecc71', alpha=0.15, label='양운')
        ax1.fill_between(dates, plot_df['Span1'], plot_df['Span2'], where=plot_df['Span1']<plot_df['Span2'], facecolor='#95a5a6', alpha=0.2, label='음운')

    if 'MA224' in plot_df.columns: ax1.plot(dates, plot_df['MA224'], color='#2c3e50', lw=1.5, alpha=0.8, label='224일선')
    if 'MA5' in plot_df.columns: ax1.plot(dates, plot_df['MA5'], color='#e84393', lw=1, alpha=0.6, label='5일선')
    
    if 'Farming_Line' in plot_df.columns:
        ax1.plot(dates, plot_df['Farming_Line'], color='#8e44ad', lw=2.5, linestyle='--', label='특수 파종선')
        ax1.text(dates[-1]+timedelta(days=2), plot_df['Farming_Line'].iloc[-1], f" {int(plot_df['Farming_Line'].iloc[-1]):,}", color='#8e44ad', fontweight='bold', va='center', fontsize=9)

    opens = plot_df['Open'].values; closes = plot_df['Close'].values
    highs = plot_df['High'].values; lows = plot_df['Low'].values
    colors = ['#c0392b' if c >= o else '#2980b9' for c, o in zip(closes, opens)]
    
    ax1.bar(dates, closes - opens, bottom=opens, width=0.6, color=colors, edgecolor=colors, alpha=0.9)
    ax1.vlines(dates, lows, highs, colors, lw=1)

    if scenario_lines:
        for label, price, color in scenario_lines:
            ax1.axhline(price, color=color, ls='-', lw=1.2, alpha=0.9)
            ax1.text(dates[0], price, f"{label} ▶ {int(price):,}", color=color, fontweight='bold', fontsize=10, bbox=dict(facecolor='white', edgecolor=color, boxstyle='round,pad=0.2', alpha=0.9), va='center')

    ax1.plot(dates[-1], closes[-1], marker='o', markersize=20, markerfacecolor='none', markeredgecolor='#e74c3c', markeredgewidth=2)
    ax2.bar(dates, plot_df['Volume'].values, color=colors, alpha=0.6, width=0.6)
    ax2.grid(True, axis='y', linestyle=':', color='#bdc3c7')

    title_html = f"{name} ({code}) | 현재가: {int(closes[-1]):,}원 | {score_str}"
    ax1.set_title(title_html, fontsize=16, fontweight='bold', fontproperties=FONT_NAME, pad=15)
    ax1.grid(True, which='major', axis='both', linestyle='--', color='#bdc3c7', alpha=0.5)
    ax1.tick_params(axis='y', labelright=True)
    ax1.legend(loc='upper left', prop={'family':FONT_NAME, 'size':9})
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.setp(ax1.get_xticklabels(), visible=False)
    return fig

# ---------------------------------------------------------
# 3. 메인 앱
# ---------------------------------------------------------
def main():
    if 'results' not in st.session_state: st.session_state.results = None
    if 'page' not in st.session_state: st.session_state.page = 1
    if 'selected_stock' not in st.session_state: st.session_state.selected_stock = None
    if 'split_lv' not in st.session_state: st.session_state.split_lv = 1

    # 헤더
    c1, c2 = st.columns([3, 1])
    c1.title("🚜 QUANT FARMING V9.9")
    c1.markdown("파종선 밑에서 올라와 **딱 붙어있는(2% 이내)** 종목만 집중 타격")
    c2.markdown("### ")
    
    st.divider()

    # 검색 패널
    col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 0.8])
    with col1: mode = st.selectbox("📋 전략", ["농사 A (파종선 2% 맥점)", "농사 B (구름대 맥점)"])
    with col2: mkt_opt = st.selectbox("🏢 시장", ["전체", "KOSPI", "KOSDAQ"])
    with col3: min_p = st.number_input("📉 최소가", 1000, step=100)
    with col4: max_p = st.number_input("📈 최대가", 200000, step=1000)
    with col5:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True) 
        run_btn = st.button("🚀 검색", type="primary")

    if run_btn:
        st.session_state.page = 1
        st.session_state.selected_stock = None
        st_mode = 'N1' if "농사 A" in mode else 'N2'
        mkt_code = 'KRX' if mkt_opt == '전체' else mkt_opt
        
        with st.status("🔍 데이터 스캔 중...", expanded=True) as status:
            stocks = fdr.StockListing(mkt_code)
            stocks = stocks[~stocks['Name'].str.contains('스팩|ETF|ETN|리츠|우B')]
            if 'Close' in stocks.columns:
                stocks['Close'] = pd.to_numeric(stocks['Close'].astype(str).str.replace(',', ''), errors='coerce')
                stocks = stocks.dropna(subset=['Close'])
                stocks = stocks[(stocks['Close'] >= min_p) & (stocks['Close'] <= max_p)]
            
            target_list = stocks.to_dict('records')
            results = []
            
            with ThreadPoolExecutor(max_workers=10) as exe:
                futures = {exe.submit(analyze_nongsa, r, st_mode): r for r in target_list}
                for f in as_completed(futures):
                    res = f.result()
                    if res: results.append(res)
            
            status.update(label="✅ 완료!", state="complete", expanded=False)
            
            if results:
                st.session_state.results = pd.DataFrame(results).sort_values('Change', ascending=False)
                st.success(f"{len(results)}개 종목 발견!")
            else:
                st.session_state.results = pd.DataFrame()
                st.warning("결과 없음")

    # 결과 표시
    if st.session_state.results is not None and not st.session_state.results.empty:
        df = st.session_state.results
        
        # 엑셀/복사 기능
        ec1, ec2 = st.columns([1, 4])
        with ec1:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 엑셀 다운로드", csv, "farming_list.csv", "text/csv")
        with ec2:
            code_list = ";".join(df['Code'].astype(str).tolist())
            with st.expander("📋 전체 종목코드 복사 (클릭)"):
                st.code(code_list, language=None)

        # 페이징
        items_per_page = 5
        total_pages = math.ceil(len(df) / items_per_page)
        start_idx = (st.session_state.page - 1) * items_per_page
        df_page = df.iloc[start_idx : start_idx + items_per_page]

        st.markdown("<div id='list_top'></div>", unsafe_allow_html=True)
        st.markdown(f"### 📋 검색 결과 (Page {st.session_state.page}/{total_pages})")

        # 커스텀 리스트 렌더링
        for idx, row in df_page.iterrows():
            with st.container():
                c_1, c_2, c_3, c_4, c_5, c_6 = st.columns([1.5, 1, 2, 1, 1.5, 1])
                c_1.markdown(f"**{row['Name']}** <span style='color:gray; font-size:0.8em;'>{row['Code']}</span>", unsafe_allow_html=True)
                c_2.write(f"{row['Market']}")
                c_3.markdown(f"<span style='color:red'>{row['Note']}</span>", unsafe_allow_html=True)
                c_4.write(f"{row['Close']:,}원")
                c_5.write(f"기준: {row['Support']:,}원")
                
                # 차트 보기 버튼
                if c_6.button("📊 차트 보기", key=f"btn_{row['Code']}"):
                    st.session_state.selected_stock = row['Code']

                st.markdown("---", unsafe_allow_html=True)

        # 페이지네이션
        col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns([1, 1, 2, 1, 1])
        def change_page(p): st.session_state.page = p
        
        with col_p1: 
            if st.session_state.page > 1: st.button("⏪ 맨앞", on_click=change_page, args=(1,))
        with col_p2: 
            if st.session_state.page > 1: st.button("◀ 이전", on_click=change_page, args=(st.session_state.page-1,))
        with col_p4: 
            if st.session_state.page < total_pages: st.button("다음 ▶", on_click=change_page, args=(st.session_state.page+1,))
        with col_p5: 
            if st.session_state.page < total_pages: st.button("맨뒤 ⏩", on_click=change_page, args=(total_pages,))

        # 차트 섹션
        if st.session_state.selected_stock:
            sel_row = df[df['Code'] == st.session_state.selected_stock].iloc[0]
            st.markdown(f"### 📊 정밀 분석: {sel_row['Name']}")
            
            chart_col1, chart_col2 = st.columns([1, 2.5])
            
            with chart_col1:
                st.info(f"**맥점(기준): {sel_row['Support']:,}원**")
                
                # 분할 매수 버튼식 UI
                st.write("🔧 **분할 파종 설정**")
                cols_lv = st.columns(4)
                if cols_lv[0].button("1차"): st.session_state.split_lv = 1
                if cols_lv[1].button("2차"): st.session_state.split_lv = 2
                if cols_lv[2].button("3차"): st.session_state.split_lv = 3
                if cols_lv[3].button("4차"): st.session_state.split_lv = 4
                
                base_price = st.number_input("기준가", value=int(sel_row['Support']), step=10)
                
                scenario_lines = []
                colors = ['red', '#ff9800', '#ff9800', '#ff9800']
                share_plan = ""
                
                for i in range(1, st.session_state.split_lv + 1):
                    p = int(base_price * (1 - (i-1)*0.05))
                    label = f"{i}차(맥점)" if i==1 else f"{i}차"
                    scenario_lines.append((label, p, colors[i-1]))
                    share_plan += f"\n👉 {label}: {p:,}원"

                # 공유 텍스트 (코드 블록으로 복사 쉽게)
                share_txt = f"[🚜 농사매매]\n{sel_row['Name']}({sel_row['Code']})\n현재: {sel_row['Close']:,}원\n타점: {sel_row['Note']}\n기준: {sel_row['Support']:,}원\n{share_plan if st.session_state.split_lv > 1 else ''}"
                st.code(share_txt, language="text")
                
                # 리스트 이동 버튼
                st.markdown("<a href='#list_top'><button style='width:100%; padding:10px; background:#f0f2f6; border:1px solid #ccc; border-radius:5px; font-weight:bold; cursor:pointer;'>⬆️ 리스트로 이동</button></a>", unsafe_allow_html=True)

            with chart_col2:
                fig = create_chart_figure(sel_row['Code'], sel_row['Name'], sel_row['Note'], scenario_lines)
                if fig: st.pyplot(fig)

if __name__ == '__main__':
    main()
