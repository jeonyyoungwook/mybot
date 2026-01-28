import streamlit as st
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import os
import platform
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

# ---------------------------------------------------------
# 0. 설정 및 폰트 처리
# ---------------------------------------------------------
warnings.filterwarnings('ignore')
st.set_page_config(page_title="전설의 매매 (Web)", layout="wide")

# 한글 폰트 설정 (Streamlit Cloud 대응)
@st.cache_resource
def install_font():
    # 리눅스(Streamlit Cloud) 환경일 경우 폰트 다운로드
    if platform.system() == 'Linux':
        try:
            # 나눔고딕 폰트가 없으면 설치된 경로를 찾거나 다운로드 로직 필요
            # 여기서는 Streamlit Cloud에서 한글이 깨지지 않게 폰트 파일을 직접 지정하거나
            # 시스템 폰트를 찾는 방식을 사용합니다.
            import matplotlib.font_manager as fm
            font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
            if not os.path.exists(font_path):
                # 폰트 파일이 없을 경우 (대안: 로컬 폰트 사용하도록 안내하거나 기본 폰트 사용)
                pass 
            else:
                fm.fontManager.addfont(font_path)
                font_prop = fm.FontProperties(fname=font_path)
                plt.rc('font', family=font_prop.get_name())
                return font_prop.get_name()
        except:
            pass
    
    # 윈도우/맥 개발 환경용
    if platform.system() == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    elif platform.system() == 'Darwin':
        plt.rc('font', family='AppleGothic')
    
    plt.rcParams['axes.unicode_minus'] = False

install_font()

# ---------------------------------------------------------
# 1. 지표 및 로직 함수 (기존 로직 동일)
# ---------------------------------------------------------
def calculate_adx(df, n=14):
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff()
    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), -minus_dm, 0.0)
    tr = pd.concat([df['High'] - df['Low'], abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/n, adjust=False).mean()
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).ewm(alpha=1/n, adjust=False).mean() / atr)
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).abs().ewm(alpha=1/n, adjust=False).mean() / atr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    return dx.ewm(alpha=1/n, adjust=False).mean()

def calculate_indicators(df):
    if len(df) < 130: return df
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    df['MA88'] = df['Close'].rolling(window=88).mean()
    df['MA120'] = df['Close'].rolling(window=120).mean()
    df['Blue_Line'] = df['Low'].rolling(window=60).min()
    h12 = df['High'].rolling(12).max(); l12 = df['Low'].rolling(12).min()
    df['Breakout_Line'] = (h12 + l12) / 2
    h20 = df['High'].rolling(20).max(); l20 = df['Low'].rolling(20).min()
    df['Danbam_Gray'] = l20 + (h20 - l20) * 0.618
    df['Amount'] = df['Close'] * df['Volume']
    df['ADX'] = calculate_adx(df)
    return df

def get_blue_score(current_price, blue_line):
    if blue_line == 0 or pd.isna(blue_line): return 0, "오류"
    gap = (current_price - blue_line) / blue_line * 100
    if gap <= 3: return 98, "💎98점"
    elif gap <= 7: return 95, "🥇95점"
    elif gap <= 10: return 90, "🥈90점"
    else: return 80, "🥉80점"

def get_trend_breakout(df):
    try:
        if len(df) < 130: return None
        window = df.iloc[-180:-5].copy()
        if len(window) < 30: return None
        p1 = window['High'].idxmax(); p1_date = p1; p1_val = window.loc[p1]['High']
        if (window.index[-1] - p1_date).days < 30: return None
        after_p1 = window.loc[p1_date:].iloc[15:]
        if len(after_p1) < 10: return None
        p2 = after_p1['High'].idxmax(); p2_val = after_p1.loc[p2]['High']
        if p2_val >= p1_val: return None
        slope = (p2_val - p1_val) / (p2 - p1_date).days
        res_price = p1_val + (slope * (df.index[-1] - p1_date).days)
        if df['Close'].iloc[-1] <= res_price: return None
        if (df['Close'].iloc[-1] - res_price)/res_price > 0.05: return None
        return {'p1_date': p1_date, 'p1_val': p1_val, 'resistance': res_price}
    except: return None

def analyze_stock(row, strategy_mode):
    try:
        code = row['Code']; name = row['Name']; market = row.get('Market', 'N/A')
        df = fdr.DataReader(code, (datetime.now()-timedelta(days=450)))
        if len(df) < 130 or df['Volume'].iloc[-1] == 0 or df['Close'].iloc[-1] < 100: return None
        df = calculate_indicators(df)
        curr = df['Close'].iloc[-1]
        score_str = ""; note_str = ""; trend_info = None; rec_entry = 0; target_price = 0; stop_loss = 0
        
        # 전략 선택 로직
        if strategy_mode == '6': # 분홍화살표
            found = False
            for i in range(1, 16):
                idx = -i
                if abs(idx) >= len(df): break
                today = df.iloc[idx]; yest = df.iloc[idx-1]
                ma88 = today['MA88']
                if pd.isna(ma88) or ma88 == 0: continue
                if not (0.90 <= (today['Close'] / ma88) <= 1.10): continue
                if not (today['MA20'] > today['MA60'] > today['MA120']): continue
                if today['ADX'] < 15: continue
                cond_candle = (today['Close'] > today['Open']) and (yest['Close'] < yest['Open']) and (today['Close'] > yest['Open']) and (today['Open'] < yest['Close'])
                if cond_candle:
                    found_date = df.index[idx].strftime('%m/%d')
                    score_str = f"🌸{found_date} 포착"; note_str = f"{abs(idx)}일전"; rec_entry = int(today['Close']); target_price = int(curr * 1.15); stop_loss = int(yest['Low']); found = True; break
            if not found: return None
        elif strategy_mode == '0': # 단밤
            t = df.iloc[-1]; y = df.iloc[-2]
            if pd.isna(t['Breakout_Line']): return None
            if (y['Close'] < y['Breakout_Line']) and (t['Close'] > t['Breakout_Line']) and ((t['Close']-t['Blue_Line'])/t['Blue_Line'] <= 0.25) and (t['Amount'] > 500000000):
                if t['Close'] < t['Danbam_Gray'] and (t['Danbam_Gray']-t['Close'])/t['Close'] >= 0.05:
                    score_str = "🚀단밤돌파"; note_str = "기준선돌파"; rec_entry = int(curr); target_price = int(t['Danbam_Gray'])
                else: return None
            else: return None
        elif strategy_mode == '1': # 바닥주
            score_num, score_str = get_blue_score(curr, df['Blue_Line'].iloc[-1])
            if score_num < 90: return None
            score_str = f"{score_str} (바닥)"; rec_entry = int(curr)
        elif strategy_mode == '2': # 눌림목
            gap = (curr - df['MA20'].iloc[-1]) / df['MA20'].iloc[-1] * 100
            if not (-2.0 <= gap <= 4.0): return None
            score_str = "🚀눌림목"; rec_entry = int(curr)
        elif strategy_mode == '3': # 바닥+돌파
            score_num, score_str = get_blue_score(curr, df['Blue_Line'].iloc[-1])
            m_gap = (curr - df['MA20'].iloc[-1]) / df['MA20'].iloc[-1] * 100
            if score_num < 90 or not (0 <= m_gap <= 3): return None
            score_str = "🏆바닥+돌파"
        elif strategy_mode == '4': # 계단식
            blue_gap = (curr - df['Blue_Line'].iloc[-1]) / df['Blue_Line'].iloc[-1] * 100
            if blue_gap > 10.0: return None
            recent_blue = df['Blue_Line'].iloc[-60:]
            if (recent_blue.diff() < 0).any(): return None
            if recent_blue.iloc[-1] <= recent_blue.iloc[0]: return None
            steps = len(recent_blue.unique()) - 1 
            if steps < 1: return None 
            score_str = f"⚡계단 {steps}회"
        elif strategy_mode == '5': # 스나이퍼
            trend_info = get_trend_breakout(df)
            if not trend_info: return None
            gap = (curr - df['MA20'].iloc[-1]) / df['MA20'].iloc[-1] * 100
            if gap > 5 or gap < -3: return None
            score_str = "📐스나이퍼"
        else: return None

        if target_price == 0: target_price = int(curr * 1.15)
        if stop_loss == 0: stop_loss = int(curr * 0.95)
        
        return {'시장': market, '종목명': name, '코드': code, '현재가': curr, '등락률': round((curr - df['Close'].iloc[-2])/df['Close'].iloc[-2]*100, 2), '점수': score_str, '비고': note_str, '목표가': target_price, '추천진입가': rec_entry, '손절선': stop_loss, 'trend_info': trend_info}
    except: return None

# ---------------------------------------------------------
# 2. UI 및 메인 실행
# ---------------------------------------------------------
st.title("💎 전설의 매매 Ver 14.2 (Web)")
st.markdown("---")

# 사이드바 입력
with st.sidebar:
    st.header("🔍 검색 옵션")
    market_option = st.selectbox("시장 선택", ["전체", "KOSPI", "KOSDAQ"])
    min_p = st.number_input("최소 주가", value=1000, step=1000)
    max_p = st.number_input("최대 주가 (0=제한없음)", value=0, step=1000)
    
    st.header("👇 전략 선택")
    st_mode = st.selectbox("전략을 선택하세요", [
        "6. 🌸 분홍화살표 (15일 이내 포착)",
        "0. 🐣 단밤 돌파",
        "1. 💎 바닥주",
        "2. 🚀 20일선 눌림목",
        "3. 🏆 바닥+돌파",
        "4. ⚡ 계단식 상승",
        "5. 📐 스나이퍼 추세"
    ])
    mode_map = {'6': '6', '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5'}
    selected_mode = st_mode.split('.')[0]
    
    run_btn = st.button("🚀 분석 시작")

# 세션 상태 초기화
if 'result_df' not in st.session_state:
    st.session_state.result_df = None

# 분석 실행
if run_btn:
    st.info("데이터 분석 중입니다... (잠시만 기다려주세요)")
    try:
        m_val = 'KRX' if market_option == "전체" else market_option
        df_krx = fdr.StockListing(m_val)
        df_krx = df_krx[~df_krx['Name'].str.contains('스팩|ETF|ETN|리츠|우B|우C', regex=True)]
        if 'Marcap' in df_krx.columns: 
            df_krx = df_krx[pd.to_numeric(df_krx['Marcap'], errors='coerce') > 30000000000]
        if 'Close' in df_krx.columns:
            df_krx['Close'] = pd.to_numeric(df_krx['Close'], errors='coerce')
            max_val = 99999999 if max_p == 0 else max_p
            df_krx = df_krx[(df_krx['Close'] >= min_p) & (df_krx['Close'] <= max_val)]
        
        target = df_krx.sort_values('Marcap', ascending=False).head(1000) # 속도를 위해 1000개 제한
        
        results = []
        progress_bar = st.progress(0)
        total = len(target)
        
        with ThreadPoolExecutor(max_workers=10) as exe:
            futures = [exe.submit(analyze_stock, row, selected_mode) for _, row in target.iterrows()]
            for i, f in enumerate(as_completed(futures)):
                if res := f.result():
                    results.append(res)
                progress_bar.progress((i + 1) / total)
        
        if results:
            df_res = pd.DataFrame(results).sort_values('등락률', ascending=False).reset_index(drop=True)
            df_res.index += 1
            st.session_state.result_df = df_res
            st.success(f"검색 완료! 총 {len(df_res)}개 종목 발견")
        else:
            st.session_state.result_df = pd.DataFrame()
            st.warning("검색 결과가 없습니다.")
            
    except Exception as e:
        st.error(f"오류 발생: {e}")

# 결과 출력 및 차트
if st.session_state.result_df is not None and not st.session_state.result_df.empty:
    df = st.session_state.result_df
    
    # 1. 결과 테이블
    st.subheader(f"📊 검색 결과 ({len(df)}개)")
    
    # 표시할 컬럼 정리
    disp_cols = ['종목명', '코드', '현재가', '등락률', '점수', '목표가', '손절선']
    st.dataframe(df[disp_cols].style.format({'현재가':'{:,}', '등락률':'{:.2f}%', '목표가':'{:,}', '손절선':'{:,}'}))
    
    st.markdown("---")
    
    # 2. 차트 시각화 선택
    st.subheader("📈 차트 상세 보기")
    selected_stock = st.selectbox("종목을 선택하세요", df['종목명'] + " (" + df['코드'] + ")")
    
    if selected_stock:
        code = selected_stock.split('(')[1].replace(')', '')
        row = df[df['코드'] == code].iloc[0]
        
        # 차트 그리기 (기존 로직 이식)
        try:
            df_chart = fdr.DataReader(code, (datetime.now()-timedelta(days=400)))
            df_chart = calculate_indicators(df_chart)
            
            fig, ax1 = plt.subplots(figsize=(12, 6))
            ax1.plot(df_chart.index, df_chart['Close'], color='green', alpha=0.6, label='종가')
            ax1.plot(df_chart.index, df_chart['MA20'], color='black', linestyle='--', label='20일선')
            
            # 목표/손절 라인
            if row['목표가'] > 0:
                ax1.axhline(row['목표가'], color='red', linestyle='-.', alpha=0.8)
                ax1.text(df_chart.index[-1], row['목표가'], f" 목표 {row['목표가']:,}", color='red', fontweight='bold', va='bottom')
            if row['손절선'] > 0:
                ax1.axhline(row['손절선'], color='blue', linestyle='-.', alpha=0.8)
                ax1.text(df_chart.index[-1], row['손절선'], f" 손절 {row['손절선']:,}", color='blue', fontweight='bold', va='top')

            # 화살표 등 표시
            score_str = row['점수']
            if '포착' in score_str or '분홍' in score_str:
                found_any = False
                for i in range(1, 30):
                    idx = -i
                    if abs(idx) >= len(df_chart): break
                    t = df_chart.iloc[idx]; y = df_chart.iloc[idx-1]
                    cond = (not pd.isna(t['MA88'])) and (0.9 <= t['Close']/t['MA88'] <= 1.1) and \
                           (t['MA20'] > t['MA60'] > t['MA120']) and (t['ADX'] >= 15) and \
                           (t['Close'] > t['Open'] and y['Close'] < y['Open'] and t['Close'] > y['Open'] and t['Open'] < y['Close'])
                    if cond:
                        ax1.scatter(df_chart.index[idx], df_chart['Low'].iloc[idx]*0.97, color='magenta', marker='^', s=150, zorder=10)
                        found_any = True
                if found_any:
                    ax1.plot(df_chart.index, df_chart['MA60'], color='green', alpha=0.5); ax1.plot(df_chart.index, df_chart['MA88'], color='orange', linewidth=1.5)

            elif '단밤' in score_str:
                ax1.plot(df_chart.index, df_chart['Breakout_Line'], color='black'); ax1.plot(df_chart.index, df_chart['Danbam_Gray'], color='gray', linestyle=':')
                ax1.scatter(df_chart.index[-1], df_chart['Close'].iloc[-1], color='red', s=150, marker='*')
            elif row['trend_info']:
                ti = row['trend_info']
                ax1.plot([ti['p1_date'], df_chart.index[-1]], [ti['p1_val'], ti['resistance']], color='red', linewidth=2)
            else:
                ax1.plot(df_chart.index, df_chart['Blue_Line'], color='blue', linestyle='--')

            ax1.set_title(f"{row['종목명']} ({code}) - {score_str}")
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            
            st.pyplot(fig) # 스트림릿에 차트 출력
            
        except Exception as e:
            st.error(f"차트 생성 실패: {e}")
