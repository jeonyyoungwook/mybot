import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
import os

# 경고 메시지 차단
warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# 1. 페이지 설정 (가장 먼저 와야 함)
# ---------------------------------------------------------
st.set_page_config(
    page_title="전설의 돌파매매",
    page_icon="💎",
    layout="wide"
)

# ---------------------------------------------------------
# 2. 분석 로직 (CSV 파일 우선 로드 방식 적용)
# ---------------------------------------------------------
def analyze_one_stock(row, start_str):
    try:
        code = str(row['Code']) # 코드는 문자열로 변환
        code = code.zfill(6)    # 6자리 숫자로 맞춤 (엑셀 로드시 0 빠지는 것 방지)
        
        name = row['Name']
        marcap = row.get('Marcap', 0)
        
        # 데이터 수집
        df = fdr.DataReader(code, start_str)
        if len(df) < 65: return None
        if df.iloc[-1]['Volume'] == 0: return None
        
        # 이동평균 및 라인 계산
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

        # 돌파매매 조건 확인
        is_breakout = (yesterday['Close'] < yesterday['Black_Line']) and (today['Close'] > today['Black_Line'])
        dist_blue = (today['Close'] - today['Blue_Line']) / today['Blue_Line'] * 100
        is_blue_safe = (dist_blue <= 25) and (today['Low_20'] > today['Blue_Line'])
        is_money_in = today['Amount'] > 500000000 

        if is_breakout and is_blue_safe and is_money_in:
            danbam_val = today['Danbam_Gray'] 
            current_price = today['Close']
            stop_loss_price = int(today['Low']) 
            target_price = int(danbam_val)      
            
            if current_price < danbam_val:
                upside_room = (danbam_val - current_price) / current_price * 100
                if upside_room >= 5.0:
                    rate = (current_price - yesterday['Close']) / yesterday['Close'] * 100
                    return {
                        '종목명': name, '코드': code,
                        '현재가': float(current_price), '등락률': rate,
                        '목표가': target_price, '손절가': stop_loss_price,
                        '단밤여력': upside_room,
                        '거래대금(억)': round(today['Amount'] / 100000000, 1),
                        '시가총액(억)': round(marcap / 100000000, 0)
                    }
    except: return None
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def run_analysis(market, min_price, max_price):
    # [수정됨] KRX 접속 차단 대비: 파일에서 먼저 읽기 시도
    csv_file = 'krx_stock_list.csv'
    df_krx = None
    
    if os.path.exists(csv_file):
        try:
            # Code 컬럼을 문자로 읽어서 '005930' 앞의 0이 사라지지 않게 함
            df_krx = pd.read_csv(csv_file, dtype={'Code': str})
            
            # 시장 필터링
            if market == 'KOSPI':
                df_krx = df_krx[df_krx['Market'] == 'KOSPI']
            elif market == 'KOSDAQ':
                df_krx = df_krx[df_krx['Market'] == 'KOSDAQ']
                
        except Exception as e:
            st.warning(f"CSV 파일 읽기 실패, 웹 다운로드를 시도합니다: {e}")
    
    # 파일이 없거나 읽기 실패시 웹에서 다운로드 (서버 차단시 여기서 에러 발생 가능)
    if df_krx is None:
        try:
            df_krx = fdr.StockListing(market)
        except Exception as e:
            st.error("❌ 종목 목록을 불러오지 못했습니다. (서버 IP 차단됨)")
            st.info("💡 해결법: 로컬에서 'krx_stock_list.csv'를 생성하여 깃허브에 같이 업로드해주세요.")
            return pd.DataFrame()
    
    # 필터링 로직
    if 'Dept' in df_krx.columns: 
        df_krx = df_krx[~df_krx['Dept'].fillna('').str.contains('관리|환기|투자주의')]
    df_krx = df_krx[~df_krx['Name'].str.contains('스팩|ETF|ETN')]
    
    # Code가 숫자로만 되어있는지, '0'으로 끝나는지 확인 (우선주 제외 등)
    df_krx['Code'] = df_krx['Code'].astype(str).str.zfill(6)
    df_krx = df_krx[df_krx['Code'].str.endswith('0')]
    
    if 'Close' in df_krx.columns:
        df_krx['Close'] = pd.to_numeric(df_krx['Close'], errors='coerce')
        df_krx = df_krx[(df_krx['Close'] >= min_price) & (df_krx['Close'] <= max_price)]
        
    target_stocks = df_krx.sort_values('Marcap', ascending=False).head(2000)
    
    results = []
    end_date = datetime.now()
    start_str = (end_date - timedelta(days=200)).strftime("%Y-%m-%d")

    # 진행률 표시줄
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_stocks = len(target_stocks)
    completed = 0

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(analyze_one_stock, row, start_str) for _, row in target_stocks.iterrows()]
        
        for future in as_completed(futures):
            completed += 1
            if completed % 10 == 0:
                progress_bar.progress(completed / total_stocks)
                status_text.text(f"분석 중... ({completed}/{total_stocks})")
            
            res = future.result()
            if res:
                 if min_price <= res['현재가'] <= max_price: results.append(res)
    
    progress_bar.empty()
    status_text.empty()
    
    if not results: return pd.DataFrame()
    
    df = pd.DataFrame(results).sort_values('등락률', ascending=False).reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = 'No'
    return df

# ---------------------------------------------------------
# 3. 차트 시각화 함수
# ---------------------------------------------------------
def get_chart_fig(code, name):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180) 
        df = fdr.DataReader(code, start_date)
        if len(df) < 20: return None

        high_12 = df['High'].rolling(window=12).max()
        low_12 = df['Low'].rolling(window=12).min()
        df['Black_Line'] = (high_12 + low_12) / 2
        df['Blue_Line'] = df['Low'].rolling(window=60).min()
        h_20 = df['High'].rolling(window=20).max()
        l_20 = df['Low'].rolling(window=20).min()
        df['Danbam_Gray'] = l_20 + (h_20 - l_20) * 0.618
        
        color_fuc = lambda x: 'red' if x >= 0 else 'blue'
        df['Color'] = (df['Close'] - df['Open']).apply(color_fuc)

        fig, axes = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
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
        ax.text(df.index[-1], stop_val, f' Stop: {int(stop_val):,}', color='red', fontweight='bold', va='top', ha='right')

        ax.set_title(f"{name}({code})", fontsize=15, fontweight='bold')
        ax.legend(loc='upper left'); ax.grid(True, alpha=0.3)
        
        ax2 = axes[1]
        ax2.bar(df.index, df['Volume'], color=df['Color'], alpha=0.6, width=0.8)
        ax2.set_ylabel("Volume"); ax2.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig
    except Exception as e: 
        st.error(f"Chart Error: {e}")
        return None

# ---------------------------------------------------------
# 4. 메인 화면 구성
# ---------------------------------------------------------
st.title("💎 전설의 돌파매매 (Web Ver.)")
st.markdown("---")

# CSV 파일 확인 (사용자 안내용)
if not os.path.exists('krx_stock_list.csv'):
    st.warning("⚠️ 'krx_stock_list.csv' 파일이 없습니다. 서버에서 종목 수집 시 오류가 발생할 수 있습니다.")

# 사이드바: 입력값 받기
st.sidebar.header("🔍 검색 옵션")
market_choice = st.sidebar.selectbox("시장 선택", ["KOSPI", "KOSDAQ", "KRX(전체)"])
if market_choice == "KRX(전체)": market = "KRX"
else: market = market_choice

min_p = st.sidebar.number_input("최소 가격 (원)", value=0, step=1000)
max_p = st.sidebar.number_input("최대 가격 (원)", value=10000000, step=1000)

run_btn = st.sidebar.button("🚀 분석 시작", type="primary")

# 분석 실행
if run_btn:
    with st.spinner("데이터 스캔 중입니다... 잠시만 기다려주세요."):
        df_result = run_analysis(market, min_p, max_p)
    
    if df_result.empty:
        st.warning("조건에 맞는 종목을 찾지 못했거나 데이터를 불러오지 못했습니다.")
    else:
        st.success(f"총 {len(df_result)}개의 종목을 찾았습니다!")
        
        # 결과 데이터프레임 표시
        st.dataframe(
            df_result.style.format({
                '현재가': '{:,.0f}', '목표가': '{:,.0f}', '손절가': '{:,.0f}',
                '등락률': '{:.2f}%', '단밤여력': '{:.2f}%',
                '거래대금(억)': '{:,.1f}', '시가총액(억)': '{:,.0f}'
            }).background_gradient(subset=['등락률'], cmap='Reds'),
            use_container_width=True
        )

        # 엑셀 다운로드 버튼
        csv = df_result.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "💾 엑셀(CSV) 다운로드",
            csv,
            "stock_analysis.csv",
            "text/csv",
            key='download-csv'
        )
        
        # 차트 보기 섹션
        st.markdown("### 📊 차트 상세보기")
        selected_stock = st.selectbox(
            "차트를 볼 종목을 선택하세요", 
            df_result['종목명'] + " (" + df_result['코드'] + ")"
        )
        
        if selected_stock:
            code_to_plot = selected_stock.split('(')[-1].replace(')', '')
            name_to_plot = selected_stock.split(' (')[0]
            
            fig = get_chart_fig(code_to_plot, name_to_plot)
            if fig:
                st.pyplot(fig)
