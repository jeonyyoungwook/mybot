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

# ---------------------------------------------------------
# 1. 페이지 설정 및 폰트 초기화
# ---------------------------------------------------------
st.set_page_config(page_title="Quant Farming Pro", page_icon="🚜", layout="wide")

@st.cache_resource
def set_font_korean():
    # 나눔고딕 폰트 다운로드 및 설정 (스트림릿 클라우드용)
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
# 2. 데이터 처리 및 지표 계산 함수 (캐싱 적용)
# ---------------------------------------------------------
def calculate_indicators(df):
    cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for c in cols:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce')
    
    if len(df) < 52: return df

    # 이동평균선
    for w in [5, 20, 60, 112, 224]:
        df[f'MA{w}'] = df['Close'].rolling(w).mean()

    # [SECRET] 농사 파종선 (BB 38-0.6)
    df['F_Mid'] = df['Close'].rolling(window=38).mean()
    df['F_Std'] = df['Close'].rolling(window=38).std()
    df['Farming_Line']  = df['F_Mid'] + (df['F_Std'] * 0.6)

    # 일목균형표
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

@st.cache_data(ttl=3600) # 1시간 캐싱
def get_stock_data(code):
    try:
        # 최근 2년치 데이터
        df = fdr.DataReader(code, (datetime.now()-timedelta(days=730)))
        if df is None or df.empty: return None
        df = calculate_indicators(df)
        return df
    except: return None

# ---------------------------------------------------------
# 3. 핵심 분석 로직 (V9.8 - 2% 맥점 타점)
# ---------------------------------------------------------
def analyze_nongsa(row, mode):
    try:
        code = str(row['Code'])
        name = row['Name']
        market = row.get('Market', 'KOSDAQ')
        
        df = get_stock_data(code)
        if df is None or len(df) < 130: return None
        
        curr = df['Close'].iloc[-1]
        t = df.iloc[-1]
        y = df.iloc[-2]
        
        score_str=""; stop=0; support=0
        
        ma224 = t.get('MA224', 0); ma5 = t.get('MA5', 0)
        span1 = t.get('Span1', 0); span2 = t.get('Span2', 0)
        
        if ma224 == 0 or ma5 == 0 or span1 == 0: return None
        
        # 기본 필터: 최소한의 추세 유지
        is_safe = (t['Close'] >= t['Open']) or (curr >= ma5)
        if not is_safe: return None

        # [농사 A] 파종선 2% 초근접 맥점 (핵심 로직)
        if mode == 'N1':
            farming_line = t.get('Farming_Line', 0)
            if farming_line == 0: return None
            
            # 이격도 계산 (0 ~ 2.0%)
            gap = (curr - farming_line) / farming_line * 100
            
            # 밑에서 올라왔는지 확인 (최근 5일 저가가 파종선 아래)
            recent_lows = df['Low'].iloc[-5:].min()
            was_below = recent_lows < farming_line

            if 0 <= gap <= 2.0 and was_below and t['Amount'] > 3e8:
                score_str = f"🎯 파종 맥점 (이격 {gap:.2f}%)" 
                support = farming_line 
                stop = int(support * 0.97)

        # [농사 B] 구름대 맥점
        elif mode == 'N2':
            cloud_gap = abs(span1 - span2)
            is_thin_cloud = (cloud_gap / curr) <= 0.04
            cloud_bottom = min(span1, span2)
            recent_low = df['Low'].iloc[-40:].min()
            is_floor = (curr - recent_low) / recent_low <= 0.15

            if is_thin_cloud and is_floor:
                score_str = "🚜 농사 맥점 (구름대 변곡)"
                support = min(cloud_bottom, ma224) 
                stop = int(support * 0.96)

        if not score_str: return None

        return {
            'Market': market, 
            'Name': name, 
            'Code': code, 
            'Close': int(curr), 
            'Change': round((curr-y['Close'])/y['Close']*100, 2),
            'Note': score_str, 
            'Target': int(curr*1.15), 
            'StopLoss': stop, 
            'Support': int(support), 
            'Amount': int(t['Amount'])
        }
    except: return None

# ---------------------------------------------------------
# 4. 차트 그리기 (전문가용 디자인 V9.8)
# ---------------------------------------------------------
def create_chart_figure(code, name, score_str, scenario_lines=None):
    df = get_stock_data(code)
    if df is None: return None
    
    # 최근 150봉
    if not isinstance(df.index, pd.DatetimeIndex): df.index = pd.to_datetime(df.index)
    plot_df = df.iloc[-150:] if len(df)>150 else df
    dates = plot_df.index
    
    # 캔버스 설정
    fig = plt.figure(figsize=(12, 8), constrained_layout=True)
    gs = fig.add_gridspec(2, 1, height_ratios=[4, 1])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)
    
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('#fcfcfc')
    ax2.set_facecolor('#fcfcfc')

    # 구름대
    if 'Span1' in plot_df.columns and 'Span2' in plot_df.columns:
        ax1.fill_between(dates, plot_df['Span1'], plot_df['Span2'], 
                         where=plot_df['Span1'] >= plot_df['Span2'], 
                         facecolor='#2ecc71', alpha=0.15, label='양운')
        ax1.fill_between(dates, plot_df['Span1'], plot_df['Span2'], 
                         where=plot_df['Span1'] < plot_df['Span2'], 
                         facecolor='#95a5a6', alpha=0.2, label='음운')

    # 이평선
    if 'MA224' in plot_df.columns: 
        ax1.plot(dates, plot_df['MA224'], color='#2c3e50', lw=1.5, alpha=0.8, label='224일선')
    if 'MA5' in plot_df.columns: 
        ax1.plot(dates, plot_df['MA5'], color='#e84393', lw=1, alpha=0.6, label='5일선')
    
    # ★ 파종선 (보라색)
    if 'Farming_Line' in plot_df.columns:
        ax1.plot(dates, plot_df['Farming_Line'], color='#8e44ad', lw=2.5, linestyle='--', label='특수 파종선')
        last_farm = plot_df['Farming_Line'].iloc[-1]
        ax1.text(dates[-1] + timedelta(days=2), last_farm, f" {int(last_farm):,}", 
                 color='#8e44ad', fontweight='bold', va='center', fontsize=9)

    # 캔들
    opens = plot_df['Open'].values; closes = plot_df['Close'].values
    highs = plot_df['High'].values; lows = plot_df['Low'].values
    colors = ['#c0392b' if c >= o else '#2980b9' for c, o in zip(closes, opens)]
    
    ax1.bar(dates, closes - opens, bottom=opens, width=0.6, color=colors, edgecolor=colors, alpha=0.9)
    ax1.vlines(dates, lows, highs, colors, lw=1)

    # 시나리오 라인
    if scenario_lines:
        for label, price, color in scenario_lines:
            ax1.axhline(price, color=color, ls='-', lw=1.2, alpha=0.9)
            ax1.text(dates[0], price, f"{label} ▶ {int(price):,}", color=color, fontweight='bold', fontsize=10, 
                     bbox=dict(facecolor='white', edgecolor=color, boxstyle='round,pad=0.2', alpha=0.9), va='center')

    # 타겟 표시
    last_date = dates[-1]; last_close = closes[-1]
    ax1.plot(last_date, last_close, marker='o', markersize=15, markerfacecolor='none', markeredgecolor='#e74c3c', markeredgewidth=2)

    # 거래량
    vols = plot_df['Volume'].values
    ax2.bar(dates, vols, color=colors, alpha=0.6, width=0.6)
    ax2.grid(True, axis='y', linestyle=':', color='#bdc3c7')
    ax2.set_ylabel('Vol')

    # 스타일
    title_html = f"{name} ({code}) | 현재가: {int(last_close):,}원 | {score_str}"
    ax1.set_title(title_html, fontsize=16, fontweight='bold', fontproperties=FONT_NAME, pad=15)
    ax1.grid(True, which='major', axis='both', linestyle='--', color='#bdc3c7', alpha=0.5)
    ax1.tick_params(axis='y', labelright=True)
    ax1.legend(loc='upper left', prop={'family':FONT_NAME, 'size':9})
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.setp(ax1.get_xticklabels(), visible=False)

    return fig

# ---------------------------------------------------------
# 5. 메인 앱 실행 (Streamlit UI)
# ---------------------------------------------------------
def main():
    # 사이드바 설정
    st.sidebar.title("🚜 QUANT FARMING")
    st.sidebar.markdown("---")
    
    mode = st.sidebar.radio("전략 선택", ["농사 A (파종선 2% 맥점)", "농사 B (구름대 맥점)"])
    market_opt = st.sidebar.selectbox("시장 선택", ["전체", "KOSPI", "KOSDAQ"])
    min_price = st.sidebar.number_input("최소 주가", value=1000, step=100)
    max_price = st.sidebar.number_input("최대 주가", value=200000, step=1000)
    
    run_btn = st.sidebar.button("🔍 농사 종목 발굴 시작", type="primary")

    st.sidebar.markdown("---")
    st.sidebar.info("V9.8 Updated\n파종선 2% 이내 초근접\n맥점 타점 검색 시스템")

    # 메인 화면
    st.title("🚜 농사매매 발굴 시스템 [PRO]")
    st.markdown("파종선 밑에서 올라와 **딱 붙어있는(2% 이내)** 종목만 집중 타격합니다.")

    if 'results' not in st.session_state:
        st.session_state.results = None

    if run_btn:
        st_mode = 'N1' if "농사 A" in mode else 'N2'
        mkt_code = 'KRX' if market_opt == '전체' else market_opt
        
        status_text = st.empty()
        prog_bar = st.progress(0)
        
        try:
            status_text.info("토양(전 종목 데이터) 수집 중...")
            stocks = fdr.StockListing(mkt_code)
            stocks = stocks[~stocks['Name'].str.contains('스팩|ETF|ETN|리츠|우B')]
            
            # 가격 필터링 (미리 수행하여 API 호출 최소화)
            if 'Close' in stocks.columns:
                stocks['Close'] = pd.to_numeric(stocks['Close'].astype(str).str.replace(',', ''), errors='coerce')
                stocks = stocks.dropna(subset=['Close'])
                stocks = stocks[(stocks['Close'] >= min_price) & (stocks['Close'] <= max_price)]
            
            target_stocks = stocks.to_dict('records')
            total = len(target_stocks)
            results = []
            
            status_text.info(f"총 {total}개 종목 정밀 분석 중... (잠시만 기다려주세요)")
            
            # 멀티스레딩 분석
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(analyze_nongsa, row, st_mode): row for row in target_stocks}
                
                for i, future in enumerate(as_completed(futures)):
                    res = future.result()
                    if res: results.append(res)
                    
                    if i % 20 == 0:
                        prog_bar.progress((i + 1) / total)
            
            prog_bar.progress(100)
            
            if results:
                df_res = pd.DataFrame(results).sort_values('Change', ascending=False)
                st.session_state.results = df_res
                status_text.success(f"분석 완료! 총 {len(results)}개 파종 유망 종목 발견 🌱")
            else:
                st.session_state.results = pd.DataFrame()
                status_text.warning("조건에 맞는 종목을 찾지 못했습니다.")
                
        except Exception as e:
            st.error(f"오류 발생: {e}")

    # 결과 화면 출력
    if st.session_state.results is not None and not st.session_state.results.empty:
        df_display = st.session_state.results
        
        # 1. 요약 리스트
        st.subheader("📋 포착 종목 리스트")
        st.dataframe(
            df_display[['Market', 'Name', 'Code', 'Close', 'Change', 'Note', 'Support']],
            column_config={
                "Name": "종목명", "Code": "코드", "Close": "현재가", 
                "Change": "등락률(%)", "Note": "포착 내용", "Support": "기준선(맥점)"
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.markdown("---")
        
        # 2. 상세 분석 (차트)
        st.subheader("📊 차트 상세 분석")
        
        # 종목 선택 Selectbox
        selected_option = st.selectbox(
            "분석할 종목을 선택하세요:",
            options=df_display['Code'].tolist(),
            format_func=lambda x: f"{df_display[df_display['Code']==x]['Name'].values[0]} ({x})"
        )
        
        if selected_option:
            row = df_display[df_display['Code'] == selected_option].iloc[0]
            
            # 파종 시나리오 설정 UI
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.info(f"**{row['Name']}**")
                st.write(f"현재가: {row['Close']:,}원")
                st.write(f"**기준선: {row['Support']:,}원**")
                
                base_price = st.number_input("파종 기준가", value=int(row['Support']), step=10)
                split_level = st.slider("분할 매수 단계", 1, 4, 1)
                
                scenario_lines = []
                colors = ['red', '#ff9800', '#ff9800', '#ff9800']
                share_text_plan = ""
                
                for i in range(1, split_level + 1):
                    p = int(base_price * (1 - (i-1)*0.05))
                    label = f"{i}차(맥점)" if i==1 else f"{i}차"
                    scenario_lines.append((label, p, colors[i-1]))
                    share_text_plan += f"\n👉 {label}: {p:,}원"

                # 공유 텍스트 생성
                share_text = f"""[🚜 농사매매 맥점 포착]
🌱 종목: {row['Name']} ({row['Code']})
💰 현재가: {row['Close']:,}원
🎯 타점: {row['Note']}
🛡 기준선: {row['Support']:,}원 (파종선)
{f"{chr(10)}📉 [분할 파종 계획]{share_text_plan}" if split_level > 1 else f"{chr(10)}👉 1차 진입: {row['Support']:,}원 부근"}
(본 정보는 참고용입니다)"""
                
                st.text_area("공유용 텍스트 (복사하세요)", share_text, height=180)

            with col2:
                # 차트 그리기
                fig = create_chart_figure(row['Code'], row['Name'], row['Note'], scenario_lines)
                if fig:
                    st.pyplot(fig)
                else:
                    st.error("데이터 로드 실패")

if __name__ == '__main__':
    main()
