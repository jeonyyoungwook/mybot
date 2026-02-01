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

# ---------------------------------------------------------
# 1. 기본 설정 및 방문자 로직
# ---------------------------------------------------------
st.set_page_config(page_title="전설의 매매 검색기", layout="wide")

# 세션 상태 초기화
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

# [오늘 방문자 카운터 함수]
def get_today_visitors():
    file_path = "visitor_log.txt"
    today_str = datetime.now().strftime("%Y-%m-%d")
    count = 0
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read().strip().split(",")
            if len(content) == 2 and content[0] == today_str:
                count = int(content[1])
    
    if 'has_visited' not in st.session_state:
        count += 1
        st.session_state['has_visited'] = True
        with open(file_path, "w") as f:
            f.write(f"{today_str},{count}")
            
    return count

# 폰트 설정
@st.cache_resource
def set_korean_font():
    font_path = "NanumGothic.ttf"
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rc('font', family='NanumGothic')
    else:
        plt.rc('font', family='sans-serif') 
        plt.rcParams['axes.unicode_minus'] = False

set_korean_font()

# ---------------------------------------------------------
# 2. 지표 계산 함수
# ---------------------------------------------------------
def get_tick_size(price, market):
    if market == 'KOSPI':
        if price < 2000: return 1
        if price < 5000: return 5
        if price < 20000: return 10
        if price < 50000: return 50
        if price < 200000: return 100
        if price < 500000: return 500
        return 1000
    else: # KOSDAQ
        if price < 1000: return 1
        if price < 5000: return 5
        if price < 10000: return 10
        if price < 50000: return 50
        return 100

def calculate_rsi(series, period=14):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_indicators(df):
    if len(df) < 120: return df

    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    df['MA88'] = df['Close'].rolling(window=88).mean() 
    df['MA112'] = df['Close'].rolling(window=112).mean()
    df['MA120'] = df['Close'].rolling(window=120).mean()
    df['MA224'] = df['Close'].rolling(window=224).mean()

    df['Blue_Line'] = df['Low'].rolling(window=60).min()
    
    h12 = df['High'].shift(1).rolling(12).max()
    l12 = df['Low'].shift(1).rolling(12).min()
    df['Black_Line'] = (h12 + l12) / 2 

    h20 = df['High'].shift(1).rolling(20).max()
    l20 = df['Low'].shift(1).rolling(20).min()
    df['Gray_Line'] = l20 + (h20 - l20) * 0.618

    high9 = df['High'].rolling(window=9).max()
    low9 = df['Low'].rolling(window=9).min()
    tenkan = (high9 + low9) / 2
    high26 = df['High'].rolling(window=26).max()
    low26 = df['Low'].rolling(window=26).min()
    kijun = (high26 + low26) / 2
    df['Span1'] = ((tenkan + kijun) / 2).shift(26)
    high52 = df['High'].rolling(window=52).max()
    low52 = df['Low'].rolling(window=52).min()
    df['Span2'] = ((high52 + low52) / 2).shift(26)

    df['Amount'] = df['Close'] * df['Volume']
    df['RSI'] = calculate_rsi(df['Close'])
    return df

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

# ---------------------------------------------------------
# 3. 분석 로직
# ---------------------------------------------------------
def analyze_stock(row, strategy_mode):
    try:
        code = row['Code']
        name = row['Name']
        market = row.get('Market', 'KOSDAQ') 

        days_to_fetch = 600 if strategy_mode in ['5', '8'] else 300
        df = fdr.DataReader(code, (datetime.now()-timedelta(days=days_to_fetch)))

        min_len = 225 if strategy_mode == '8' else 130
        if len(df) < min_len or df['Volume'].iloc[-1] == 0: return None

        df = calculate_indicators(df)
        curr = df['Close'].iloc[-1]
        
        # [공통 필터]
        min_amount = 500000000 if strategy_mode in ['0', '1'] else 3000000000
        if df['Amount'].iloc[-1] < min_amount: return None

        rsi = df['RSI'].iloc[-1]
        if not pd.isna(rsi) and rsi > 72: return None

        ma20 = df['MA20'].iloc[-1]
        if not pd.isna(ma20):
            if (curr - ma20) / ma20 * 100 > 15.0: return None

        ma120 = df['MA120'].iloc[-1]
        if not pd.isna(ma120) and curr < ma120:
            if (ma120 - curr) / curr * 100 < 1.0: return None 

        score_str = ""; note_str = ""; trend_info = None
        rec_entry = 0; target_price = 0; stop_loss = 0

        # [전략 로직]
        if strategy_mode == '0':
            t = df.iloc[-1]
            black = t['Black_Line']
            if pd.isna(black): return None
            if t['Low'] < black: return None
            if (t['Close'] - black) / black * 100 > 5.0: return None
            day_range = (t['High'] - t['Low']) / t['Open'] * 100
            if day_range > 15.0: return None 
            score_str = "🐣단밤 칼지지 (침범X)"; rec_entry = int(black); stop_loss = int(black * 0.99)

        elif strategy_mode == '11':
            t = df.iloc[-1]; y = df.iloc[-2]
            if t['Amount'] < 10000000000: return None 
            change_rate = (t['Close'] - y['Close']) / y['Close'] * 100
            if change_rate < 5.0: return None
            day_range = t['High'] - t['Low']
            fibo_0236 = t['High'] - (day_range * 0.236)
            gap = abs(curr - fibo_0236) / fibo_0236 * 100
            if gap <= 0.7 or ((t['Low'] <= fibo_0236 * 1.005) and (t['Close'] >= fibo_0236)):
                score_str = f"✨피보0.236 칼각 (대금{int(t['Amount']/100000000)}억)"; rec_entry = int(fibo_0236); target_price = int(t['High']); stop_loss = int(t['High'] - (day_range * 0.382)) 
            else: return None

        elif strategy_mode == '8':
            t = df.iloc[-1]
            ma112 = t['MA112']; black = t['Black_Line']; gray = t['Gray_Line']
            if t['Close'] < t['Open']: return None
            if pd.isna(ma112) or pd.isna(black) or pd.isna(gray): return None
            if not (-2.0 <= (curr - ma112)/ma112*100 <= 5.0): return None
            if curr < black: return None
            gap_gray = (curr - gray)/gray*100
            if not (-3.0 <= gap_gray <= 3.0): return None
            score_str = "🛫이륙준비 (정배열초기)"; rec_entry = int(curr); stop_loss = int(min(ma112, black)*0.97)

        elif strategy_mode == '2':
            t = df.iloc[-1]; ma20 = t['MA20']; ma60 = t['MA60']
            if pd.isna(ma20) or pd.isna(ma60): return None
            if ma20 < ma60: return None 
            if rsi > 60: return None 
            gap = (curr - ma20) / ma20 * 100
            if not (-2.0 <= gap <= 1.5): return None 
            recent_high = df['High'].iloc[-20:].max()
            if recent_high < ma20 * 1.10: return None 
            vol_ma20 = df['Volume'].iloc[-20:].mean()
            if df['Volume'].iloc[-1] > vol_ma20 * 1.5: return None 
            score_str = "🚀급등 후 찐눌림"; rec_entry = int(curr); target_price = int(recent_high); stop_loss = int(ma60)

        elif strategy_mode == '3':
            t = df.iloc[-1]; y = df.iloc[-2]; ma20 = t['MA20']; blue_line = t['Blue_Line']
            if pd.isna(ma20) or pd.isna(blue_line): return None
            if (curr - blue_line) / blue_line * 100 > 15.0: return None
            if not (y['Close'] < y['MA20'] and t['Close'] > t['MA20']): return None
            if t['Close'] <= t['Open']: return None
            if t['Volume'] < y['Volume'] * 1.5: return None
            score_str = "🏆바닥권 20일선 돌파"; rec_entry = int(curr); stop_loss = int(ma20)

        elif strategy_mode == '1':
            t = df.iloc[-1]; blue = t['Blue_Line']
            if pd.isna(blue) or blue == 0: return None
            if (curr - blue) / blue * 100 > 5.0: return None
            if t['Close'] <= t['Open']: return None
            if pd.isna(t['MA5']) or t['Close'] < t['MA5']: return None
            score_str = "💎찐바닥(추세전환)"; rec_entry = int(curr); stop_loss = int(blue)

        elif strategy_mode == '4':
            t = df.iloc[-1]
            if pd.isna(t['MA120']) or pd.isna(t['MA60']) or pd.isna(t['MA20']): return None
            if not (t['MA20'] > t['MA60'] > t['MA120']): return None
            rb = df['Blue_Line'].iloc[-60:]
            if (rb.diff() < 0).any(): return None
            if rb.iloc[-1] < rb.iloc[0] * 1.10: return None
            if curr < t['MA60']: return None
            if curr > t['MA60'] * 1.25: return None
            score_str = "⚡정배열 계단상승"; rec_entry = int(curr); stop_loss = int(t['MA60'])

        elif strategy_mode == '10':
            t = df.iloc[-1]; y = df.iloc[-2]
            if pd.isna(t['Span1']) or pd.isna(t['Span2']): return None
            if t['Span1'] > t['Span2'] * 1.05: return None
            is_above_now = t['Close'] > t['Span1']
            was_below_recently = False
            for i in range(1, 4):
                if df['Close'].iloc[-1-i] <= df['Span1'].iloc[-1-i] * 1.02:
                    was_below_recently = True; break
            if not (is_above_now and was_below_recently): return None
            if t['Close'] <= t['Open']: return None
            if pd.isna(t['MA60']) or t['Close'] < t['MA60']: return None
            if (t['Close'] - y['Close']) / y['Close'] * 100 > 27.0: return None
            if y['Volume'] == 0: return None
            if t['Volume'] / y['Volume'] * 100 < 200.0: return None
            score_str = f"☁️구름돌파 ({int(t['Volume']/y['Volume']*100)}%)"; rec_entry = int(curr); stop_loss = int(min(t['MA60'], t['Span1']))

        elif strategy_mode == '7':
            t = df.iloc[-1]; y = df.iloc[-2]
            if (t['Close'] - y['Close']) / y['Close'] * 100 < 5.0: return None
            if t['Amount'] < 10000000000: return None
            vol_ma20 = df['Volume'].iloc[-21:-1].mean()
            if t['Volume'] < y['Volume'] * 2.0 and t['Volume'] < vol_ma20 * 2.0: return None
            body = t['Close'] - t['Open']
            upper_tail = t['High'] - t['Close']
            if body <= 0: return None 
            if upper_tail > body: return None 
            score_str = f"🔥급등포착(+{round((t['Close']-y['Close'])/y['Close']*100,1)}%)"; 
            rec_entry = int(curr); stop_loss = int(t['Open'])

        elif strategy_mode == '6':
            found = False
            for i in range(1, 6):
                idx = -i
                t = df.iloc[idx]
                ma88 = t.get('MA88', 0)
                if pd.isna(ma88) or ma88 == 0: continue
                if not (t['MA20'] > t['MA60'] > ma88): continue
                if not (t['Low'] <= ma88 * 1.03 and t['Close'] >= ma88): continue
                if t['Close'] <= t['Open']: continue
                if t['ADX'] > 35: continue
                score_str = f"🌸MA88 지지 ({df.index[idx].strftime('%m/%d')})"; 
                rec_entry = int(t['Close']); stop_loss = int(t['Low']); found = True; break
            if not found: return None

        elif strategy_mode == '5':
            trend_info = get_trend_breakout(df)
            if not trend_info: return None
            g = (curr - df['MA20'].iloc[-1]) / df['MA20'].iloc[-1] * 100
            if g > 5 or g < -3: return None
            score_str = "📐스나이퍼"; rec_entry = int(curr); stop_loss = int(df['MA20'].iloc[-1])

        else: return None

        start_price = df.iloc[-1]['Open']
        vi_price = start_price * 1.10
        tick_size = get_tick_size(vi_price, market)
        calc_target = vi_price - (tick_size * 4)

        if calc_target > curr: target_price = int(calc_target); note_str += " [VI 4호가전]"
        else: target_price = int(curr * 1.10); note_str += " [추가상승]"

        if target_price <= curr: target_price = int(curr * 1.05)
        if rec_entry == 0: rec_entry = int(curr)
        if stop_loss == 0: stop_loss = int(curr * 0.95)

        return {
            '시장': market, '종목명': name, '코드': code,
            '현재가': curr,
            '거래대금': int(df['Amount'].iloc[-1]),
            '등락률': round((curr - df['Close'].iloc[-2])/df['Close'].iloc[-2]*100, 2),
            'RSI': round(rsi, 1),
            '점수': score_str, '비고': note_str,
            '목표가': target_price, '추천진입가': rec_entry, '손절선': stop_loss,
            'trend_info': trend_info
        }
    except Exception as e:
        return None

# ---------------------------------------------------------
# 4. 차트 생성 함수
# ---------------------------------------------------------
def plot_chart(code, name, score_str, target_price, stop_loss):
    try:
        df = fdr.DataReader(code, (datetime.now()-timedelta(days=600)))
        df = calculate_indicators(df)
        if len(df) > 150: plot_df = df.iloc[-150:]
        else: plot_df = df
        
        fig, ax1 = plt.subplots(figsize=(10, 5)) 

        if '단밤' in score_str:
            ax1.plot(plot_df.index, plot_df['Black_Line'], color='black', linewidth=3, label='검은선 (강력지지)')
            ax1.fill_between(plot_df.index, plot_df['Black_Line'], plot_df['Gray_Line'], color='gray', alpha=0.1)
        
        if plot_df['RSI'].iloc[-1] > 65:
            ax1.text(plot_df.index[-1], plot_df['High'].iloc[-1]*1.05, '⚠️RSI높음', color='orange', fontweight='bold')

        ax1.plot(plot_df.index, plot_df['MA20'], color='#e74c3c', linewidth=1.5, label='20일선')
        ax1.plot(plot_df.index, plot_df['MA60'], color='#2ecc71', linewidth=1.5, label='60일선')
        ax1.plot(plot_df.index, plot_df['MA120'], color='#9b59b6', linewidth=2, linestyle='--', label='120일선')

        for idx in plot_df.index:
            o, h, l, c = plot_df.loc[idx, ['Open', 'High', 'Low', 'Close']]
            color = '#ed3738' if c >= o else '#007afe'
            ax1.vlines(idx, l, h, color=color, linewidth=1)
            ax1.bar(idx, height=c-o, bottom=o, width=0.6, color=color, align='center')

        if target_price > 0:
            ax1.axhline(target_price, color='red', linestyle='-.', linewidth=1.5)
            ax1.text(plot_df.index[-1], target_price, f' 🎯 {target_price:,}', color='red', va='bottom', fontweight='bold')
        if stop_loss > 0:
            ax1.axhline(stop_loss, color='blue', linestyle='-.', linewidth=1.5)
            ax1.text(plot_df.index[-1], stop_loss, f' 🛑 {stop_loss:,}', color='blue', va='top', fontweight='bold')

        ax1.set_title(f"{name} ({code}) - {score_str}", fontsize=15, fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.2, linestyle='--')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.tight_layout()
        
        return fig
    except Exception as e:
        st.error(f"차트 생성 중 오류: {e}")
        return None

# ---------------------------------------------------------
# 5. 메인 UI
# ---------------------------------------------------------
def main():
    st.title("💎 전설의 매매 검색기 Ver 42.12")
    
    # 상태 표시
    today_visitor_count = get_today_visitors()
    col_status, col_visit = st.columns([1, 1])
    with col_status:
        st.success("🟢 **현재 접속중: ON**")
    with col_visit:
        st.info(f"📅 **오늘 방문자: {today_visitor_count}명**")
    
    st.markdown("---")

    # 사이드바
    with st.sidebar:
        st.header("🔍 검색 설정")
        market_option = st.selectbox("시장 선택", ["코스피", "코스닥", "전체"])
        market_code = 'KOSPI' if market_option == '코스피' else 'KOSDAQ' if market_option == '코스닥' else 'KRX'

        min_price = st.number_input("최소 주가 (원)", value=1000, step=100)
        max_price = st.number_input("최대 주가 (원, 0=제한없음)", value=0, step=1000)
        if max_price == 0: max_price = 9999999999

        st.markdown("### 📈 전략 선택")
        strategies = {
            '0': '0. 🐣 단밤 지지 (무관용 원칙)',
            '1': '1. 💎 최바닥주 (찐바닥)',
            '2': '2. 🚀 눌림목 (가짜 제거)',
            '3': '3. 🏆 바닥+돌파 (급등초기)',
            '4': '4. ⚡ 계단상승 (정배열)',
            '5': '5. 📐 스나이퍼',
            '6': '6. 🌸 분홍화살표 (88일선 지지)',
            '7': '7. 🔥 급등 단타 (강력필터)',
            '8': '8. 🛫 이륙 준비 (오류수정)',
            '9': '9. 🌊 첫 턴 (손익비 필터)',
            '10': '10. ☁️ 일목+대량거래',
            '11': '11. ✨ 15분봉 피보나치 0.236'
        }
        
        selected_strat_text = st.radio("원하는 전략을 선택하세요:", options=list(strategies.values()), index=2)
        mode = [k for k, v in strategies.items() if v == selected_strat_text][0]
        st.markdown("---")
        search_btn = st.button("🚀 종목 검색 시작", type="primary", use_container_width=True)

    # 검색 실행
    if search_btn:
        st.session_state.current_page = 0
        st.session_state.search_results = None
        
        st.info(f"📡 {market_option} 시장에서 [{strategies[mode]}] 전략으로 스캔 중입니다...")
        
        try:
            with st.spinner("종목 리스트 불러오는 중..."):
                df_krx = fdr.StockListing(market_code)
                df_krx = df_krx[~df_krx['Name'].str.contains('스팩|ETF|ETN|리츠|우B|우C|홀딩스', regex=True)]
                for c in ['Close', 'Amount', 'ChagesRatio']:
                    df_krx[c] = pd.to_numeric(df_krx[c], errors='coerce')
                target = df_krx[(df_krx['Close'] >= min_price) & (df_krx['Close'] <= max_price)]
            
            st.write(f"📊 분석 대상: **{len(target)}**개 종목")
            
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with ThreadPoolExecutor(max_workers=10) as exe:
                futures = {exe.submit(analyze_stock, row, mode): row for _, row in target.iterrows()}
                completed_count = 0
                total_count = len(target)
                
                for f in as_completed(futures):
                    res = f.result()
                    if res: results.append(res)
                    completed_count += 1
                    if completed_count % 10 == 0:
                        progress_bar.progress(completed_count / total_count)
                        status_text.text(f"분석 진행률: {int(completed_count/total_count*100)}%")
            
            progress_bar.progress(1.0); status_text.empty()
            
            if not results:
                st.warning("❌ 조건에 맞는 종목을 찾지 못했습니다.")
            else:
                df_res = pd.DataFrame(results).sort_values(['거래대금', '등락률'], ascending=[False, False])
                st.session_state.search_results = df_res
                st.success(f"✨ 총 {len(results)}개 알짜 종목 발견!")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

    # ---------------------------------------------------------
    # 결과 화면 (깔끔한 접이식 리스트)
    # ---------------------------------------------------------
    if st.session_state.search_results is not None:
        
        # 1. 앵커 태그 (위로 가기 목표 지점)
        st.markdown('<div id="result_list_top"></div>', unsafe_allow_html=True)

        df_res = st.session_state.search_results
        items_per_page = 5
        total_items = len(df_res)
        total_pages = (total_items - 1) // items_per_page + 1
        
        start_idx = st.session_state.current_page * items_per_page
        end_idx = start_idx + items_per_page
        current_page_data = df_res.iloc[start_idx:end_idx]

        st.markdown(f"### 📄 검색 결과 (페이지 {st.session_state.current_page + 1} / {total_pages})")

        # 2. 접이식 리스트 (Expander)
        for i, row in current_page_data.iterrows():
            # 요약 정보 (접혀있을 때 보이는 부분)
            summary = f"[{row['시장']}] {row['종목명']} ({row['코드']}) | {int(row['현재가']):,}원 | {row['등락률']}%"
            
            with st.expander(summary):
                # 펼쳤을 때 내용
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown(f"#### {row['종목명']}")
                    st.markdown(f"**유형:** {row['점수']}")
                    st.markdown(f"💰 대금: **{int(row['거래대금']/100000000)}억**")
                    st.markdown(f"📉 RSI: **{row['RSI']}**")
                    st.markdown(f"🟢 진입: **{int(row['추천진입가']):,}**")
                    st.markdown(f"🔴 목표: **{int(row['목표가']):,}**")
                    st.markdown(f"🔵 손절: **{int(row['손절선']):,}**")
                    st.link_button("네이버 증권", f"https://finance.naver.com/item/main.naver?code={row['코드']}")
                
                with c2:
                    # 차트 그리기
                    with st.spinner("차트 생성 중..."):
                        fig = plot_chart(row['코드'], row['종목명'], row['점수'], row['목표가'], row['손절선'])
                        if fig:
                            st.pyplot(fig)
                            plt.close(fig)
                            
                    # [위로 가기 버튼] 차트 바로 밑에 위치
                    st.markdown("""
                        <a href="#result_list_top" target="_self" style="text-decoration:none;">
                            <div style="
                                background-color: #f0f2f6;
                                padding: 10px;
                                border-radius: 5px;
                                text-align: center;
                                color: black;
                                font-weight: bold;
                                cursor: pointer;
                                margin-top: 10px;
                            ">
                                ⬆️ 리스트 맨 위로 이동
                            </div>
                        </a>
                    """, unsafe_allow_html=True)

        # 3. 페이지네이션 버튼
        st.markdown("<br>", unsafe_allow_html=True)
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            if st.button("◀ 이전 페이지", disabled=(st.session_state.current_page == 0), use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
        
        with col_page:
            st.markdown(f"<div style='text-align: center; font-weight: bold; padding-top: 10px;'>{st.session_state.current_page + 1} / {total_pages}</div>", unsafe_allow_html=True)

        with col_next:
            if st.button("다음 페이지 ▶", disabled=(st.session_state.current_page >= total_pages - 1), use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()

if __name__ == "__main__":
    main()
