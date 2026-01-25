import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

# 경고 무시 및 설정
warnings.filterwarnings('ignore')
st.set_page_config(page_title="전설의 돌파매매 BII", layout="wide")

# ---------------------------------------------------------
# 1. 분석 함수 (캐싱 적용으로 속도 향상)
# ---------------------------------------------------------
@st.cache_data(ttl=3600) # 1시간마다 데이터 갱신
def get_stock_listing(market):
    df = fdr.StockListing(market)
    # 필터링
    if 'Dept' in df.columns: 
        df = df[~df['Dept'].fillna('').str.contains('관리|환기|투자주의')]
    df = df[~df['Name'].str.contains('스팩|ETF|ETN')]
    df = df[df['Code'].str.endswith('0')]
    return df

def analyze_one_stock(row, start_str):
    try:
        code = row['Code']
        name = row['Name']
        marcap = row.get('Marcap', 0)
        
        df = fdr.DataReader(code, start_str)
        if len(df) < 65: return None
        if df.iloc[-1]['Volume'] == 0: return None
        
        # 지표 계산
        high_12 = df['High'].rolling(window=12).max()
        low_12 = df['Low'].rolling(window=12).min()
        black_line = (high_12 + low_12) / 2
        blue_line = df['Low'].rolling(window=60).min()
        
        h_20 = df['High'].rolling(window=20).max()
        l_20 = df['Low'].rolling(window=20).min()
        danbam_gray = l_20 + (h_20 - l_20) * 0.618 
        low_20 = df['Low'].rolling(window=20).min()
        amount = df['Close'] * df['Volume']
        
        today = df.iloc[-1]
        yesterday = df.iloc[-2]
        today_black = black_line.iloc[-1]
        yesterday_black = black_line.iloc[-2]
        today_blue = blue_line.iloc[-1]
        
        if today_blue == 0 or today['Close'] == 0: return None

        # 돌파매매 조건
        is_breakout = (yesterday['Close'] < yesterday_black) and (today['Close'] > today_black)
        dist_blue = (today['Close'] - today_blue) / today_blue * 100
        is_blue_safe = (dist_blue <= 25) and (low_20.iloc[-1] > today_blue)
        is_money_in = amount.iloc[-1] > 500000000 

        if is_breakout and is_blue_safe and is_money_in:
            danbam_val = danbam_gray.iloc[-1]
            current_price = today['Close']
            
            if current_price < danbam_val:
                upside_room = (danbam_val - current_price) / current_price * 100
                if upside_room >= 5.0:
                    rate = (current_price - yesterday['Close']) / yesterday['Close'] * 100
                    return {
                        '종목명': name, '코드': code,
                        '현재가': current_price, '등락률': rate,
                        '목표가': int(danbam_val), '손절가': int(today['Low']),
                        '단밤여력': upside_room,
                        '거래대금(억)': round(amount.iloc[-1] / 100000000, 1),
                        '시가총액(억)': round(marcap / 100000000, 0)
                    }
    except: return None
    return None

# ---------------------------------------------------------
# 2. 차트 그리기 함수 (Matplotlib -> Streamlit)
# ---------------------------------------------------------
def plot_chart(code, name):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180) 
    df = fdr.DataReader(code, start_date)
    
    if len(df) < 20: 
        st.error("데이터가 부족합니다.")
        return

    # 지표 계산
    high_12 = df['High'].rolling(window=12).max()
    low_12 = df['Low'].rolling(window=12).min()
    df['Black_Line'] = (high_12 + low_12) / 2
    df['Blue_Line'] = df['Low'].rolling(window=60).min()
    h_20 = df['High'].rolling(window=20).max()
    l_20 = df['Low'].rolling(window=20).min()
    df['Danbam_Gray'] = l_20 + (h_20 - l_20) * 0.618
    
    # BII 계산
    range_val = (df['High'] - df['Low']).replace(0, 0.0001)
    df['BII_Raw'] = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / range_val * df['Volume']
    df['BII_Signal'] = df['BII_Raw'].rolling(window=9).mean()
    bii_colors = ['red' if x >= 0 else 'blue' for x in df['BII_Raw']]

    # 차트 그리기
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    
    # 상단 차트
    ax = axes[0]
    ax.plot(df.index, df['Close'], color='green', alpha=0.5, label='Close')
    ax.plot(df.index, df['Black_Line'], color='black', linewidth=2, label='기준선')
    ax.plot(df.index, df['Blue_Line'], color='blue', linestyle='--', label='지지선')
    ax.plot(df.index, df['Danbam_Gray'], color='gray', linestyle=':', linewidth=1)
    ax.scatter(df.index[-1], df['Close'].iloc[-1], color='red', s=150, marker='*', zorder=5)
    
    target_val = df['Danbam_Gray'].iloc[-1]
    stop_val = df['Low'].iloc[-1]
    
    ax.axhline(y=target_val, color='green', linestyle='--', alpha=0.6)
    ax.text(df.index[-1], target_val, f' Target: {int(target_val):,}', color='green', fontweight='bold', va='bottom', ha='right')
    ax.axhline(y=stop_val, color='red', linestyle='-', alpha=0.4) 
    
    ax.set_title(f"{name}({code}) | Target: {int(target_val):,}", fontsize=15, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # 하단 BII 차트
    ax2 = axes[1]
    ax2.bar(df.index, df['BII_Raw'], color=bii_colors, alpha=0.6, width=0.8, label='세력강도')
    ax2.plot(df.index, df['BII_Signal'], color='gold', linewidth=1.5, label='자금흐름')
    ax2.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    ax2.set_ylabel("BII Signal")
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig) # 스트림릿에 차트 출력

# ---------------------------------------------------------
# 3. 메인 화면 (UI 구성)
# ---------------------------------------------------------
st.title("💎 전설의 돌파매매 (BII 세력신호)")
st.markdown("---")

# 사이드바 입력
st.sidebar.header("🔍 검색 옵션")
market_option = st.sidebar.selectbox("시장 선택", ["KOSPI", "KOSDAQ", "KRX (전체)"], index=0)
market_code = "KRX" if "KRX" in market_option else market_option

min_price = st.sidebar.number_input("최소 가격", value=1000, step=100)
max_price = st.sidebar.number_input("최대 가격 (0=제한없음)", value=0, step=1000)
if max_price == 0: max_price = 99999999

if st.sidebar.button("🚀 종목 발굴 시작"):
    status_text = st.empty()
    bar = st.progress(0)
    
    status_text.text(f"{market_code} 데이터 수집 중...")
    df_krx = get_stock_listing(market_code)
    
    # 가격 필터링
    if 'Close' in df_krx.columns:
        df_krx['Close'] = pd.to_numeric(df_krx['Close'], errors='coerce')
        df_krx = df_krx[(df_krx['Close'] >= min_price) & (df_krx['Close'] <= max_price)]
    
    target_stocks = df_krx.sort_values('Marcap', ascending=False).head(2000)
    
    results = []
    end_date = datetime.now()
    start_str = (end_date - timedelta(days=200)).strftime("%Y-%m-%d")
    
    status_text.text(f"{len(target_stocks)}개 종목 정밀 분석 중... (잠시만 기다리세요)")
    
    # 스레딩 분석
    total_len = len(target_stocks)
    processed = 0
    
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(analyze_one_stock, row, start_str) for _, row in target_stocks.iterrows()]
        
        for future in as_completed(futures):
            processed += 1
            if processed % 50 == 0:
                bar.progress(min(processed / total_len, 1.0))
                
            if res := future.result():
                if min_price <= res['현재가'] <= max_price:
                    results.append(res)

    bar.progress(1.0)
    status_text.text("✅ 분석 완료!")
    
    if not results:
        st.warning("조건을 만족하는 종목이 없습니다.")
    else:
        # 결과 데이터프레임
        df_res = pd.DataFrame(results).sort_values('등락률', ascending=False).reset_index(drop=True)
        df_res.index = df_res.index + 1
        
        # 세션 상태에 저장 (차트 보기를 위해)
        st.session_state['df_res'] = df_res
        
        st.subheader(f"📊 검색 결과: {len(df_res)} 종목")
        
        # 테이블 보여주기 (숫자 포맷 적용)
        st.dataframe(
            df_res.style.format({
                '현재가': '{:,.0f}', '목표가': '{:,.0f}', '손절가': '{:,.0f}',
                '등락률': '{:.2f}%', '단밤여력': '{:.2f}%',
                '거래대금(억)': '{:,.1f}', '시가총액(억)': '{:,.0f}'
            }).background_gradient(subset=['단밤여력'], cmap='Greens')
        )

# 차트 보기 섹션 (결과가 있을 때만 표시)
if 'df_res' in st.session_state and not st.session_state['df_res'].empty:
    st.markdown("---")
    st.subheader("📈 상세 차트 & BII 신호 확인")
    
    df_res = st.session_state['df_res']
    # 선택 박스
    selected_stock = st.selectbox(
        "종목을 선택하세요:", 
        df_res.apply(lambda x: f"{x['종목명']} ({x['코드']})", axis=1)
    )
    
    if selected_stock:
        code = selected_stock.split('(')[1].replace(')', '')
        name = selected_stock.split(' (')[0]
        
        with st.spinner(f"{name} 차트 생성 중..."):
            plot_chart(code, name)