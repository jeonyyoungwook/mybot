import streamlit as st
import pyupbit
import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ========================================
# [설정] 글로벌 설정
# ========================================
class Config:
    MIN_DATA_DAYS = 120
    MAX_WORKERS = 10  # 서버 부하 방지를 위해 조정
    
    # 전략 변수
    BB_PERIOD = 38
    BB_STD = 0.6
    
    # 기본 필터
    MIN_VOLUME = 0 

# ========================================
# [폰트] 한글 폰트 설정 (깃허브 파일 연동)
# ========================================
# 깃허브에 올려두신 폰트 파일명과 일치해야 합니다.
font_path = "NanumGothic.ttf" 

# 폰트 파일이 없으면 기본 폰트 사용 (에러 방지)
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rc("font", family="NanumGothic")
else:
    # 폰트가 없을 경우 시스템 기본 폰트 시도 (한글 깨짐 방지 노력)
    plt.rc("font", family="DejaVu Sans")

plt.rcParams["axes.unicode_minus"] = False

# ========================================
# [UI] 페이지 설정
# ========================================
st.set_page_config(page_title="HYBRID FARMING V11", page_icon="📈", layout="wide")

st.markdown("""
    <style>
        .main {background-color: #0e1117;}
        div[data-testid="stMetricValue"] {font-size: 1.1rem; color: #00FF00;}
        .info-box {
            padding: 20px; border-radius: 12px; margin-bottom: 20px;
            background: linear-gradient(135deg, #141e30 0%, #243b55 100%);
            color: white; border: 1px solid #444;
        }
    </style>
""", unsafe_allow_html=True)

# ========================================
# [DATA] 데이터 수집 (캐싱 적용)
# ========================================
@st.cache_data(ttl=3600) # 1시간마다 데이터 갱신 (서버 부하 방지)
def get_market_data(ticker, market_type):
    """코인과 주식 데이터를 통합해서 가져옴"""
    try:
        df = None
        if market_type == "COIN":
            df = pyupbit.get_ohlcv(ticker, interval="day", count=250)
        else: # STOCK
            df = fdr.DataReader(ticker)
            df = df.tail(250)
            df = df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume', 'Change': 'change'})
            df['value'] = df['close'] * df['volume']

        if df is None or len(df) < Config.MIN_DATA_DAYS:
            return None

        # --- 지표 계산 ---
        df['MA5'] = df['close'].rolling(5).mean()
        df['MA20'] = df['close'].rolling(20).mean()
        df['MA60'] = df['close'].rolling(60).mean()
        
        ma_len = 224 if len(df) >= 224 else 120
        df['MA224'] = df['close'].rolling(ma_len).mean()

        df['F_Mid'] = df['close'].rolling(38).mean()
        df['F_Std'] = df['close'].rolling(38).std()
        df['Farming_Line'] = df['F_Mid'] + (df['F_Std'] * 0.6)

        high_9 = df['high'].rolling(9).max()
        low_9 = df['low'].rolling(9).min()
        tenkan = (high_9 + low_9) / 2
        high_26 = df['high'].rolling(26).max()
        low_26 = df['low'].rolling(26).min()
        kijun = (high_26 + low_26) / 2
        df['Span1'] = (tenkan + kijun) / 2
        high_52 = df['high'].rolling(52).max()
        low_52 = df['low'].rolling(52).min()
        df['Span2'] = (high_52 + low_52) / 2
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        return df.dropna()

    except Exception as e:
        return None

# ========================================
# [LOGIC] 분석 로직
# ========================================
def analyze_ticker(ticker, name, market_type, show_all):
    df = get_market_data(ticker, market_type)
    if df is None: return None

    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    close = curr['close']
    ma224 = curr['MA224']
    farm_line = curr['Farming_Line']
    cloud_top = max(curr['Span1'], curr['Span2'])
    
    signal_type = "관망"
    score = 0
    target_price = close
    is_buy_signal = False

    # A. 파종선
    gap_farm = (close - farm_line) / farm_line * 100
    if -3.0 <= gap_farm <= 5.0 and close >= curr['MA20']:
        signal_type = "🌾 파종선 근접"
        score = 80 - abs(gap_farm)
        target_price = farm_line
        is_buy_signal = True
        
    # B. 224일선
    elif ma224 > 0:
        gap_ma = (close - ma224) / ma224 * 100
        if -2.0 <= gap_ma <= 7.0:
            signal_type = "🔥 224일선 돌파" if gap_ma >= 0 else "⏳ 224일선 대기"
            score = 90 - abs(gap_ma)
            target_price = ma224
            is_buy_signal = True

    # C. 구름대
    elif close > cloud_top:
        gap_cloud = (close - cloud_top) / cloud_top * 100
        if gap_cloud <= 10.0:
            signal_type = "☁️ 구름대 지지"
            score = 70 - gap_cloud
            target_price = cloud_top
            is_buy_signal = True

    if not show_all and not is_buy_signal: return None
    if not is_buy_signal: score = 0

    return {
        'code': ticker,
        'name': name,
        'price': close,
        'change': (close - prev['close']) / prev['close'] * 100,
        'volume_money': int(curr['value'] // 1000000),
        'signal': signal_type,
        'score': round(score, 1),
        'target': int(target_price),
        'rsi': round(curr['RSI'], 1),
        'market': market_type
    }

# ========================================
# [CHART] 차트 그리기
# ========================================
def draw_chart(ticker, market_type, info):
    df = get_market_data(ticker, market_type)
    if df is None: return None
    
    df = df.iloc[-120:]
    dates = df.index
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
    plt.subplots_adjust(hspace=0.05)
    
    # Price Chart
    ax1.plot(dates, df['MA224'], 'k-', lw=1.5, label='224일선')
    ax1.plot(dates, df['Farming_Line'], color='purple', linestyle='--', label='파종선')
    ax1.fill_between(dates, df['Span1'], df['Span2'], where=df['Span1']>=df['Span2'], color='green', alpha=0.1)
    ax1.fill_between(dates, df['Span1'], df['Span2'], where=df['Span1']<df['Span2'], color='red', alpha=0.1)
    
    for idx, row in df.iterrows():
        color = 'red' if row['close'] >= row['open'] else 'blue'
        ax1.vlines(idx, row['low'], row['high'], color=color, lw=1)
        ax1.vlines(idx, row['open'], row['close'], color=color, lw=4)
        
    ax1.set_title(f"{info['name']} ({ticker}) - {info['signal']}", fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.setp(ax1.get_xticklabels(), visible=False)
    
    # RSI Chart
    ax2.plot(dates, df['RSI'], color='orange', label='RSI')
    ax2.axhline(30, color='blue', linestyle='--')
    ax2.axhline(70, color='red', linestyle='--')
    ax2.fill_between(dates, 30, 70, color='gray', alpha=0.1)
    ax2.set_ylabel('RSI')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    
    return fig

# ========================================
# [MAIN]
# ========================================
def main():
    st.markdown("""
        <div class="info-box">
            <h2>📈 하이브리드 농사매매 V11.0 (Cloud)</h2>
            <p>코인(Upbit) + 주식(KR Stock) 통합 분석 시스템</p>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("🔍 검색 옵션")
        
        market_select = st.selectbox("시장 선택", ["코인 (Upbit)", "주식 (KOSPI/KOSDAQ)"])
        show_all = st.checkbox("조건 상관없이 모든 종목 보기", value=True)
        
        st.markdown("---")
        if "주식" in market_select:
            stock_scope = st.radio("주식 범위", ["KOSPI 상위 50", "KOSDAQ 상위 50", "주요 섹터 통합"])

        if st.button("🚀 데이터 분석 시작", type="primary"):
            st.session_state['run'] = True
            st.session_state['market'] = "COIN" if "코인" in market_select else "STOCK"
            st.session_state['stock_scope'] = stock_scope if "주식" in market_select else None
            st.session_state['show_all'] = show_all

    if st.session_state.get('run'):
        status = st.empty()
        bar = st.progress(0)
        
        results = []
        target_list = []
        
        status.info("목록 가져오는 중...")
        if st.session_state['market'] == "COIN":
            tickers = pyupbit.get_tickers(fiat="KRW")
            target_list = [(t, t.replace("KRW-", "")) for t in tickers]
        else:
            scope = st.session_state['stock_scope']
            try:
                if "KOSPI" in scope:
                    df_krx = fdr.StockListing('KOSPI')
                    target_list = [(row['Code'], row['Name']) for i, row in df_krx.head(50).iterrows()]
                elif "KOSDAQ" in scope:
                    df_krx = fdr.StockListing('KOSDAQ')
                    target_list = [(row['Code'], row['Name']) for i, row in df_krx.head(50).iterrows()]
                else:
                    df_k = fdr.StockListing('KOSPI').head(50)
                    df_q = fdr.StockListing('KOSDAQ').head(50)
                    target_list = [(row['Code'], row['Name']) for i, row in df_k.iterrows()] + \
                                  [(row['Code'], row['Name']) for i, row in df_q.iterrows()]
            except:
                st.error("주식 목록을 불러오는데 실패했습니다.")
                target_list = []

        status.info(f"총 {len(target_list)}개 종목 분석 시작... (클라우드 환경 최적화)")
        
        # 클라우드는 CPU가 약할 수 있으므로 worker 수 조절
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(analyze_ticker, t[0], t[1], st.session_state['market'], st.session_state['show_all']): t for t in target_list}
            
            completed = 0
            for future in as_completed(futures):
                res = future.result()
                if res: results.append(res)
                completed += 1
                bar.progress(completed / len(target_list))
                
        bar.empty()
        
        if results:
            results.sort(key=lambda x: x['score'], reverse=True)
            st.session_state['data'] = results
            status.success(f"분석 완료! {len(results)}개 종목 표시")
        else:
            status.warning("결과가 없습니다.")
        
        st.session_state['run'] = False

    if st.session_state.get('data'):
        data = st.session_state['data']
        
        df_show = pd.DataFrame(data)
        df_show = df_show[['name', 'price', 'change', 'signal', 'score', 'rsi', 'volume_money', 'code']]
        df_show.columns = ['종목명', '현재가', '등락률', '신호상태', '점수', 'RSI', '거래대금(백만)', '코드']
        
        df_show['등락률'] = df_show['등락률'].apply(lambda x: f"{x:+.2f}%")
        df_show['현재가'] = df_show['현재가'].apply(lambda x: f"{x:,.0f}")
        
        c1, c2 = st.columns([1.2, 1])
        
        with c1:
            st.subheader("📋 전체 종목 리스트")
            def highlight_signal(row):
                if "관망" not in row['신호상태']:
                    return ['background-color: #1e3c72'] * len(row)
                return [''] * len(row)
            
            st.dataframe(df_show.style.apply(highlight_signal, axis=1), height=600, use_container_width=True)
            
        with c2:
            st.subheader("📊 차트 상세분석")
            selected_name = st.selectbox("종목 선택", [d['name'] for d in data])
            
            if selected_name:
                item = next(d for d in data if d['name'] == selected_name)
                
                m1, m2, m3 = st.columns(3)
                m1.metric("현재가", f"{item['price']:,}원", f"{item['change']:+.2f}%")
                m2.metric("매매신호", item['signal'])
                m3.metric("점수", f"{item['score']}점")
                
                fig = draw_chart(item['code'], item['market'], item)
                if fig:
                    st.pyplot(fig)
                    
                st.info(f"💡 팁: 점수가 높을수록 유리한 위치입니다. (RSI: {item['rsi']})")

if __name__ == '__main__':
    main()
