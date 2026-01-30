import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import time

# ---------------------------------------------------------
# 0. 페이지 설정 및 폰트 설정
# ---------------------------------------------------------
st.set_page_config(page_title="전설의 매매 (Web)", layout="wide")

@st.cache_resource
def set_korean_font():
    # 1. 현재 폴더에 있는 폰트 파일 우선 적용
    font_path = 'NanumGothic.ttf' 
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        font_prop = fm.FontProperties(fname=font_path)
        plt.rc('font', family=font_prop.get_name())
    else:
        # 2. 파일이 없으면 시스템 폰트 시도
        plt.rc('font', family='NanumGothic')
    
    plt.rcParams['axes.unicode_minus'] = False

set_korean_font()

# ---------------------------------------------------------
# [추가] 방문자 수 및 동시 접속자 집계 함수
# ---------------------------------------------------------
def get_traffic_metrics():
    # 1. 동시 접속자 수 (Streamlit Runtime 접근)
    try:
        from streamlit.runtime import get_instance
        runtime = get_instance()
        session_info = runtime._session_manager._session_info_map
        active_users = len(session_info)
    except:
        active_users = 1 # 오류 시 기본값

    # 2. 방문자 수 기록 (CSV 파일 사용)
    file_path = "visitors.csv"
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 기본값
    total_visits = 0
    today_visits = 0
    
    # 파일이 있으면 읽기
    if os.path.exists(file_path):
        try:
            df_v = pd.read_csv(file_path)
            if not df_v.empty:
                last_date = df_v.iloc[-1]['date']
                total_visits = int(df_v.iloc[-1]['total'])
                today_visits = int(df_v.iloc[-1]['today'])
                
                # 날짜가 바뀌었으면 오늘 방문자 초기화
                if last_date != today_str:
                    today_visits = 0
        except:
            pass
            
    # 카운트 증가 (새로고침 할 때마다 증가)
    # Session State를 써서 한 세션 내에서는 증가 안 하게 할 수도 있지만, 
    # 여기서는 단순 조회를 위해 실행 시마다 증가시킴
    if 'visited' not in st.session_state:
        today_visits += 1
        total_visits += 1
        st.session_state.visited = True
        
        # 저장
        new_data = pd.DataFrame({'date': [today_str], 'today': [today_visits], 'total': [total_visits]})
        new_data.to_csv(file_path, index=False)

    return active_users, today_visits, total_visits

# ---------------------------------------------------------
# 1. 지표 계산 함수
# ---------------------------------------------------------
def calculate_indicators(df):
    if len(df) < 10: return df
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    df['MA88'] = df['Close'].rolling(window=88).mean()
    df['MA112'] = df['Close'].rolling(window=112).mean()
    df['Blue_Line'] = df['Low'].rolling(window=60).min()
    
    high_shift = df['High'].shift(1)
    low_shift = df['Low'].shift(1)
    h12 = high_shift.rolling(12).max()
    l12 = low_shift.rolling(12).min()
    df['Black_Line'] = (h12 + l12) / 2
    
    h20 = high_shift.rolling(20).max()
    l20 = low_shift.rolling(20).min()
    df['Gray_Line'] = l20 + (h20 - l20) * 0.618
    return df

def calculate_adx_simple(df, n=14):
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff()
    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), -minus_dm, 0.0)
    
    tr = pd.concat([df['High'] - df['Low'],
                    abs(df['High'] - df['Close'].shift(1)),
                    abs(df['Low'] - df['Close'].shift(1))], axis=1).max(axis=1)
    
    atr = tr.ewm(alpha=1/n, adjust=False).mean()
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).ewm(alpha=1/n, adjust=False).mean() / atr)
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).abs().ewm(alpha=1/n, adjust=False).mean() / atr)
    div = plus_di + minus_di
    dx = (abs(plus_di - minus_di) / div.replace(0, 1)) * 100
    return dx.ewm(alpha=1/n, adjust=False).mean()

def get_trend_breakout(df):
    try:
        if len(df) < 130: return None
        window = df.iloc[-180:-5]
        if len(window) < 30: return None
        p1 = window['High'].idxmax()
        p1_val = window.loc[p1]['High']
        days_diff = (window.index[-1] - p1).days
        if days_diff < 30: return None
        after_p1 = window.loc[p1:].iloc[15:]
        if len(after_p1) < 10: return None
        p2 = after_p1['High'].idxmax()
        p2_val = after_p1.loc[p2]['High']
        if p2_val >= p1_val: return None
        slope = (p2_val - p1_val) / (p2 - p1).days
        res_price = p1_val + (slope * (df.index[-1] - p1).days)
        curr = df['Close'].iloc[-1]
        if curr <= res_price: return None
        if (curr - res_price)/res_price > 0.05: return None
        return {'p1_date': p1, 'p1_val': p1_val, 'resistance': res_price}
    except: return None

# ---------------------------------------------------------
# 2. 종목 분석 함수
# ---------------------------------------------------------
def analyze_stock(row, strategy_mode):
    try:
        code = row['Code']; name = row['Name']; market = row.get('Market', 'N/A')
        
        if strategy_mode == '7': days_to_fetch = 60
        elif strategy_mode == '8': days_to_fetch = 300
        elif strategy_mode == '5': days_to_fetch = 400
        else: days_to_fetch = 250
        
        df = fdr.DataReader(code, (datetime.now()-timedelta(days=days_to_fetch)))
        
        min_len = 20
        if strategy_mode == '8': min_len = 120
        
        if len(df) < min_len or df['Volume'].iloc[-1] == 0: return None

        df = calculate_indicators(df)
        curr = df['Close'].iloc[-1]
        
        if strategy_mode == '6':
            df['ADX'] = calculate_adx_simple(df)

        rec_entry = 0; stop_loss = 0; target_price = 0
        ref_candle_info = None
        
        scan_df = df.iloc[-45:-2] 
        for idx_label in reversed(scan_df.index):
            candle = df.loc[idx_label]
            if candle['Open'] == 0: continue
            if (candle['Close'] - candle['Open']) / candle['Open'] >= 0.06:
                mid_price = (candle['High'] + candle['Low']) / 2
                rec_entry = int(mid_price)
                stop_loss = int(candle['Low'])
                target_price = int(curr * 1.15)
                ref_candle_info = {'date': idx_label, 'high': candle['High'], 'low': candle['Low'], 'mid': mid_price}
                break 

        if rec_entry == 0:
            rec_entry = int(df['MA5'].iloc[-1])
            stop_loss = int(curr * 0.95)
            target_price = int(curr * 1.10)

        if strategy_mode not in ['6', '7']:
            blue_line = df['Blue_Line'].iloc[-1]
            if pd.isna(blue_line) or blue_line == 0: return None
            if (curr - blue_line) / blue_line > 0.07: return None

        score_str = ""; note_str = ""; trend_info = None

        if strategy_mode == '8': 
            t = df.iloc[-1]
            if pd.isna(t['MA112']) or pd.isna(t['Black_Line']): return None
            gap_112 = (curr - t['MA112']) / t['MA112']
            if not (-0.03 <= gap_112 <= 0.08): return None
            if curr < t['Black_Line']: return None
            if curr > t['Gray_Line'] * 1.05: return None
            score_str = "🛫이륙준비"
        elif strategy_mode == '7':
            t = df.iloc[-1]
            if t['Close'] <= t['Open']: return None
            if (t['High'] - t['Close']) > (t['Close'] - t['Open']) * 2: return None
            score_str = "🔥급등주"
            rec_entry = int(t['Open'])
        elif strategy_mode == '6':
            t = df.iloc[-1]
            if pd.isna(t['MA88']): return None
            if not (0.90 <= (curr / t['MA88']) <= 1.10): return None
            if not (t['MA20'] > t['MA60']): return None
            if t['ADX'] < 15: return None
            score_str = "🌸분홍포착"
        elif strategy_mode == '5':
            trend_info = get_trend_breakout(df)
            if not trend_info: return None
            score_str = "📐스나이퍼"
        elif strategy_mode == '4':
            rb = df['Blue_Line'].iloc[-60:].values
            if np.any(np.diff(rb) < 0) or rb[-1] <= rb[0]: return None
            score_str = "⚡계단상승"
        elif strategy_mode == '3':
            m_gap = (curr - df['MA20'].iloc[-1]) / df['MA20'].iloc[-1]
            if not (0 <= m_gap <= 0.03): return None
            score_str = "🏆바닥+돌파"
        elif strategy_mode == '2':
            gap = (curr - df['MA20'].iloc[-1]) / df['MA20'].iloc[-1]
            if not (-0.02 <= gap <= 0.04): return None
            score_str = "🚀눌림목"
        elif strategy_mode == '1':
            score_str = "💎최바닥주"
        elif strategy_mode == '0':
            t = df.iloc[-1]; y = df.iloc[-2]
            if pd.isna(t['Black_Line']): return None
            if (y['Close'] < y['Black_Line']) and (t['Close'] > t['Black_Line']):
               score_str = "🐣단밤돌파"
            else: return None
        else: return None

        if ref_candle_info: note_str = f"기준봉({ref_candle_info['date'].strftime('%m/%d')}) 중심"
        else: note_str = "기준봉없음"

        if rec_entry > 0 and (curr - rec_entry) / rec_entry > 0.20: return None

        return {
            '시장': market, '종목명': name, '코드': code,
            '현재가': curr, '등락률': round((curr - df['Close'].iloc[-2])/df['Close'].iloc[-2]*100, 2),
            '점수': score_str, '비고': note_str,
            '목표가': target_price, '추천진입가': rec_entry, '손절선': stop_loss,
            'ref_info': ref_candle_info, 'trend_info': trend_info
        }
    except: return None

# ---------------------------------------------------------
# 3. 차트 시각화
# ---------------------------------------------------------
def plot_chart(code, name, score_str, ref_info, trend_info):
    try:
        set_korean_font()
        df = fdr.DataReader(code, (datetime.now()-timedelta(days=500)))
        df = calculate_indicators(df)

        if len(df) > 250: plot_df = df.iloc[-250:]
        else: plot_df = df

        last_date = plot_df.index[-1]; curr = plot_df['Close'].iloc[-1]

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(plot_df.index, plot_df['Close'], color='green', alpha=0.6, label='종가')
        ax1.plot(plot_df.index, plot_df['MA112'], color='blue', linestyle='-', linewidth=1.5, label='112일선')
        ax1.plot(plot_df.index, plot_df['Black_Line'], color='black', linestyle='-', alpha=0.7, label='검은선')
        
        if ref_info:
            r_date = ref_info['date']
            if r_date in plot_df.index:
                mid = ref_info['mid']
                ax1.axvline(x=r_date, color='orange', linestyle='--', alpha=0.5)
                ax1.axhline(y=mid, color='red', linestyle='-', linewidth=2, label=f'타점(중심): {int(mid):,}')
                ax1.text(plot_df.index[-1], mid, f" BUY: {int(mid):,}", color='red', fontweight='bold', ha='left')

        if trend_info:
             ax1.plot([trend_info['p1_date'], last_date], [trend_info['p1_val'], trend_info['resistance']], color='purple', linewidth=2, label='추세저항선')

        ax1.scatter(last_date, curr, color='red', s=150, zorder=10)
        ax1.set_title(f"{name} ({code}) - {score_str}", fontsize=15, fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error(f"차트 생성 실패: {e}")

# ---------------------------------------------------------
# 4. Streamlit Main UI
# ---------------------------------------------------------
def main():
    # 사이드바 방문자 정보 표시 (최상단)
    active_u, today_v, total_v = get_traffic_metrics()
    
    st.sidebar.title("🚀 전설의 매매 Ver 25.11")
    
    # 방문자 현황 카드
    st.sidebar.markdown(f"""
    <div style="background-color:#f0f2f6; padding:10px; border-radius:10px; margin-bottom:10px;">
        <h4 style="margin:0; color:#333;">📡 접속 현황</h4>
        <p style="margin:5px 0 0 0;">🟢 <b>동시 접속자:</b> {active_u}명</p>
        <p style="margin:0;">📅 <b>오늘 방문자:</b> {today_v}명</p>
        <p style="margin:0;">👥 <b>누적 방문자:</b> {total_v}명</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")

    # 사이드바 입력
    market_option = st.sidebar.selectbox("시장 선택", ["전체", "KOSPI", "KOSDAQ"], index=0)
    market_code = 'KOSPI' if market_option == 'KOSPI' else 'KOSDAQ' if market_option == 'KOSDAQ' else 'KRX'

    min_price = st.sidebar.number_input("최소 주가", value=1000, step=100)
    max_price = st.sidebar.number_input("최대 주가 (0=무제한)", value=0, step=1000)
    if max_price == 0: max_price = 9999999999

    st.sidebar.markdown("---")
    
    # 전략 리스트
    strategy_map = {
        "0. 🐣 단밤 돌파": "0", "1. 💎 최바닥주": "1", "2. 🚀 눌림목": "2",
        "3. 🏆 바닥+돌파": "3", "4. ⚡ 계단식": "4", "5. 📐 스나이퍼": "5",
        "6. 🌸 분홍화살표": "6", "7. 🔥 실시간 급등": "7", "8. 🛫 이륙 준비 (추천)": "8"
    }
    strategy_label = st.sidebar.selectbox("전략 선택", list(strategy_map.keys()), index=8)
    mode = strategy_map[strategy_label]

    run_btn = st.sidebar.button("🔍 분석 시작", type="primary")

    if 'results' not in st.session_state:
        st.session_state.results = None

    if run_btn:
        st.session_state.results = None
        with st.status("데이터 수집 및 분석 중... (잠시만 기다려주세요)", expanded=True) as status:
            try:
                st.write("1. 전 종목 리스트 가져오는 중...")
                df_krx = fdr.StockListing(market_code)
                df_krx = df_krx[~df_krx['Name'].str.contains('스팩|ETF|ETN|리츠|우B|우C')]
                
                cols_to_num = ['Close', 'Amount', 'Marcap', 'Volume']
                for c in cols_to_num:
                    if c in df_krx.columns: df_krx[c] = pd.to_numeric(df_krx[c], errors='coerce')
                
                df_krx = df_krx[
                    (df_krx['Close'] >= min_price) & 
                    (df_krx['Close'] <= max_price) &
                    (df_krx['Volume'] > 0) 
                ]
                target = df_krx.sort_values('Marcap', ascending=False)
                st.write(f"📊 1차 필터링 완료: {len(target)}개 종목 분석 시작")
                
                res = []
                workers = 20
                
                progress_bar = st.progress(0)
                total_scan = len(target)
                completed = 0

                with ThreadPoolExecutor(max_workers=workers) as exe:
                    fut = [exe.submit(analyze_stock, row, mode) for _, row in target.iterrows()]
                    for f in as_completed(fut):
                        completed += 1
                        if completed % 50 == 0:
                            progress_bar.progress(completed / total_scan)
                        if r := f.result():
                            res.append(r)
                
                progress_bar.progress(1.0)
                
                if res:
                    df_r = pd.DataFrame(res).sort_values('등락률', ascending=False).reset_index(drop=True)
                    df_r.index += 1
                    st.session_state.results = df_r
                    status.update(label="분석 완료!", state="complete", expanded=False)
                else:
                    status.update(label="검색 결과가 없습니다.", state="error")
            
            except Exception as e:
                st.error(f"오류 발생: {e}")

    if st.session_state.results is not None:
        df_res = st.session_state.results
        st.success(f"🎯 총 {len(df_res)}개 종목이 발견되었습니다.")
        
        display_cols = ['시장', '종목명', '코드', '현재가', '등락률', '점수', '비고', '추천진입가', '목표가', '손절선']
        st.dataframe(
            df_res[display_cols].style.format({
                '현재가': '{:,.0f}', '추천진입가': '{:,.0f}', 
                '목표가': '{:,.0f}', '손절선': '{:,.0f}', '등락률': '{:.2f}%'
            }),
            use_container_width=True,
            height=300
        )

        st.divider()
        st.subheader("📊 차트 상세 보기")
        
        options = [f"{i}. [{row['시장']}] {row['종목명']} ({row['코드']})" for i, row in df_res.iterrows()]
        selected_option = st.selectbox("종목을 선택하세요:", options)
        
        if selected_option:
            idx = int(selected_option.split('.')[0])
            row = df_res.loc[idx]
            
            c1, c2, c3 = st.columns(3)
            c1.metric("현재가", f"{int(row['현재가']):,}원", f"{row['등락률']}%")
            c2.metric("추천 진입", f"{int(row['추천진입가']):,}원")
            c3.metric("손절가", f"{int(row['손절선']):,}원")
            
            st.info(f"💡 상태: {row['점수']} | {row['비고']}")
            
            with st.spinner("차트 그리는 중..."):
                plot_chart(row['코드'], row['종목명'], row['점수'], row['ref_info'], row.get('trend_info'))

if __name__ == "__main__":
    main()
