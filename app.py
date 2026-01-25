import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

# ---------------------------------------------------------
# 1. 기본 설정
# ---------------------------------------------------------
warnings.filterwarnings('ignore')
st.set_page_config(page_title="전설의 돌파매매", page_icon="💎", layout="wide")

# ---------------------------------------------------------
# 2. 분석 함수 (종목 하나 분석)
# ---------------------------------------------------------
def analyze_one_stock(row, start_str):
    try:
        code = row['Code']
        name = row['Name']
        marcap = row.get('Marcap', 0)
        
        # 데이터 수집 (최근 데이터만 빠르게)
        df = fdr.DataReader(code, start_str)
        if len(df) < 65: return None
        if df.iloc[-1]['Volume'] == 0: return None
        
        # 지표 계산
        high_12 = df['High'].rolling(window=12).max()
        low_12 = df['Low'].rolling(window=12).min()
        df['Black_Line'] = (high_12 + low_12) / 2
        df['Blue_Line'] = df['Low'].rolling(window=60).min()
        
        h_20 = df['High'].rolling(window=20).max()
        l_20 = df['Low'].rolling(window=20).min()
        df['Danbam_Gray'] = l_20 + (h_20 - l_20) * 0.618 
        df['Low_20'] = df['Low'].rolling(window=20).min()
        df['Amount'] = df['Close'] * df['Volume']
        
        today = df.iloc[-1]
        yesterday = df.iloc[-2]
        
        if today['Blue_Line'] == 0 or today['Close'] == 0: return None

        # 매매 조건
        is_breakout = (yesterday['Close'] < yesterday['Black_Line']) and (today['Close'] > today['Black_Line'])
        dist_blue = (today['Close'] - today['Blue_Line']) / today['Blue_Line'] * 100
        is_blue_safe = (dist_blue <= 25) and (today['Low_20'] > today['Blue_Line'])
        is_money_in = today['Amount'] > 500000000 

        if is_breakout and is_blue_safe and is_money_in:
            danbam_val = today['Danbam_Gray'] 
            current_price = today['Close']
            
            if current_price < danbam_val:
                upside_room = (danbam_val - current_price) / current_price * 100
                if upside_room >= 5.0:
                    rate = (current_price - yesterday['Close']) / yesterday['Close'] * 100
                    return {
                        '종목명': name, 
                        '코드': code,
                        '현재가': float(current_price), 
                        '등락률': rate,
                        '목표가': int(danbam_val), 
                        '손절가': int(today['Low']),
                        '단밤여력': upside_room,
                        '거래대금(억)': round(today['Amount'] / 100000000, 1),
                        '시가총액(억)': round(marcap / 100000000, 0)
                    }
    except: return None
    return None

# ---------------------------------------------------------
# 3. 전체 실행 함수 (캐싱 적용)
# ---------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def run_analysis(market_code, min_p, max_p):
    # 시장 데이터 가져오기
    df_krx = fdr.StockListing(market_code)
    
    # 기본 필터링
    if 'Dept' in df_krx.columns: 
        df_krx = df_krx[~df_krx['Dept'].fillna('').str.contains('관리|환기|투자주의')]
    df_krx = df_krx[~df_krx['Name'].str.contains('스팩|ETF|ETN')]
    df_krx = df_krx[df_krx['Code'].str.endswith('0')]
    
    if 'Close' in df_krx.columns:
        df_krx['Close'] = pd.to_numeric(df_krx['Close'], errors='coerce')
        df_krx = df_krx[(df_krx['Close'] >= min_p) & (df_krx['Close'] <= max_p)]
    
    # 시총 상위 2000개만 (속도 위해)
    target_stocks = df_krx.sort_values('Marcap', ascending=False).head(2000)
    
    results = []
    end_date = datetime.now()
    start_str = (end_date - timedelta(days=200)).strftime("%Y-%m-%d")
    
    # 진행 상황 표시용
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(target_stocks)
    done = 0

    # 멀티스레딩으로 고속 분석
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(analyze_one_stock, row, start_str) for _, row in target_stocks.iterrows()]
        
        for future in as_completed(futures):
            done += 1
            if done % 20 == 0: 
                progress_bar.progress(done / total)
                status_text.text(f"🔍 전체 {total}개 중 {done}개 분석 완료...")
            
            res = future.result()
            if res:
                results.append(res)
            
    progress_bar.empty()
    status_text.empty()
    
    if not results: return pd.DataFrame()
    
    df = pd.DataFrame(results).sort_values('등락률', ascending=False).reset_index(drop=True)
    df.index += 1
    return df

# ---------------------------------------------------------
# 4. 차트 그리기 함수
# ---------------------------------------------------------
def draw_chart(code, name):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180) 
        df = fdr.DataReader(code, start_date)
        if len(df) < 20: 
            st.error("데이터가 부족합니다.")
            return

        # 지표 재계산
        high_12 = df['High'].rolling(window=12).max()
        low_12 = df['Low'].rolling(window=12).min()
        df['Black_Line'] = (high_12 + low_12) / 2
        df['Blue_Line'] = df['Low'].rolling(window=60).min()
        
        h_20 = df['High'].rolling(window=20).max()
        l_20 = df['Low'].rolling(window=20).min()
        df['Danbam_Gray'] = l_20 + (h_20 - l_20) * 0.618
        
        fig, axes = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
        
        # 캔들 차트
        ax = axes[0]
        ax.plot(df.index, df['Close'], color='green', label='Close')
        ax.plot(df.index, df['Black_Line'], color='black', lw=2, label='기준선')
        ax.plot(df.index, df['Blue_Line'], color='blue', ls='--', label='지지선')
        ax.plot(df.index, df['Danbam_Gray'], color='gray', ls=':', label='목표라인')
        
        target = df['Danbam_Gray'].iloc[-1]
        ax.axhline(target, color='green', ls='--', alpha=0.5)
        ax.text(df.index[-1], target, f" Target: {int(target):,}", color='green', fontweight='bold', ha='right')
        
        ax.set_title(f"{name} ({code})", fontsize=14, fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(alpha=0.3)
        
        # 거래량 차트
        ax2 = axes[1]
        colors = ['red' if c >= o else 'blue' for c, o in zip(df['Close'], df['Open'])]
        ax2.bar(df.index, df['Volume'], color=colors, alpha=0.6)
        ax2.grid(alpha=0.3)
        
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"차트 오류: {e}")

# ---------------------------------------------------------
# 5. 메인 UI 구성
# ---------------------------------------------------------
st.title("💎 전설의 돌파매매 AI")
st.markdown("##### 👉 기준선 돌파 + 지지선 안전 + 거래량 폭발 종목을 찾아냅니다.")

with st.sidebar:
    st.header("⚙️ 검색 옵션")
    market_opt = st.selectbox("시장 선택", ["KOSPI", "KOSDAQ", "KRX"])
    min_price = st.number_input("최소 가격", value=1000, step=1000)
    max_price = st.number_input("최대 가격", value=500000, step=1000)
    search_btn = st.button("🚀 종목 발굴 시작", type="primary")

if search_btn:
    with st.spinner("빅데이터 분석 중입니다... 잠시만 기다려주세요!"):
        # 시장 코드 변환
        m_code = "KRX" if market_opt == "KRX" else market_opt
        
        result_df = run_analysis(m_code, min_price, max_price)
        
        if result_df.empty:
            st.warning("조건에 맞는 종목이 없습니다.")
        else:
            st.success(f"🎉 총 {len(result_df)}개의 보석 같은 종목을 찾았습니다!")
            
            # 메인 테이블 출력
            st.dataframe(
                result_df.style.format({
                    '현재가': '{:,.0f}', 
                    '목표가': '{:,.0f}', 
                    '손절가': '{:,.0f}',
                    '등락률': '{:.2f}%', 
                    '단밤여력': '{:.2f}%',
                    '거래대금(억)': '{:,.1f}', 
                    '시가총액(억)': '{:,.0f}'
                }).background_gradient(subset=['등락률'], cmap='Reds'),
                use_container_width=True
            )
            
            # 차트 보기 기능
            st.divider()
            st.subheader("📈 차트 분석기")
            stock_list = result_df['종목명'] + " (" + result_df['코드'] + ")"
            selected = st.selectbox("차트를 확인할 종목을 선택하세요:", stock_list)
            
            if selected:
                code_sel = selected.split('(')[1].replace(')', '')
                name_sel = selected.split(' (')[0]
                draw_chart(code_sel, name_sel)
