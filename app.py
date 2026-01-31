import streamlit as st
import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import os
import platform
import json

# ---------------------------------------------------------
# 1. 방문자 수 카운트 & 상태 표시 로직
# ---------------------------------------------------------
def track_visitors():
    filename = 'visitors.json'
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    if not os.path.exists(filename):
        data = {'total': 0, 'today': 0, 'last_date': today_str}
    else:
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except:
            data = {'total': 0, 'today': 0, 'last_date': today_str}

    if data['last_date'] != today_str:
        data['today'] = 0
        data['last_date'] = today_str

    if 'visited' not in st.session_state:
        data['total'] += 1
        data['today'] += 1
        st.session_state['visited'] = True
        
        with open(filename, 'w') as f:
            json.dump(data, f)
            
    return data['today'], data['total']

# ---------------------------------------------------------
# 2. 폰트 및 페이지 설정
# ---------------------------------------------------------
st.set_page_config(page_title="전설의 매매 검색기", page_icon="💎", layout="wide")

def set_font_force():
    system_name = platform.system()
    f_path = ''
    if system_name == 'Linux':
        f_path = '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'
        if not os.path.exists(f_path):
            f_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
    elif system_name == 'Windows':
        f_path = 'C:/Windows/Fonts/malgun.ttf'
    elif system_name == 'Darwin':
        f_path = '/System/Library/Fonts/AppleSDGothicNeo.ttc'

    if os.path.exists(f_path):
        fm.fontManager.addfont(f_path)
        font_prop = fm.FontProperties(fname=f_path)
        plt.rc('font', family=font_prop.get_name())
        plt.rcParams['axes.unicode_minus'] = False
        return font_prop
    else:
        plt.rc('font', family='sans-serif')
        return None

FONT_PROP = set_font_force()

# ---------------------------------------------------------
# 3. 지표 계산 함수
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
    
    div = plus_di + minus_di
    dx = (abs(plus_di - minus_di) / div.replace(0, 1)) * 100
    adx = dx.ewm(alpha=1/n, adjust=False).mean()
    return adx

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
    df['ADX'] = calculate_adx(df)
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
# 4. 분석 로직
# ---------------------------------------------------------
def analyze_stock(row, strategy_mode):
    try:
        code = row['Code']
        name = row['Name']
        market = row.get('Market', 'N/A')

        days_to_fetch = 600 if strategy_mode in ['5', '8'] else 300
        df = fdr.DataReader(code, (datetime.now()-timedelta(days=days_to_fetch)))

        min_len = 225 if strategy_mode == '8' else 130
        if len(df) < min_len or df['Volume'].iloc[-1] == 0: return None

        df = calculate_indicators(df)
        curr = df['Close'].iloc[-1]

        score_str = ""; note_str = ""; trend_info = None
        rec_entry = 0; target_price = 0; stop_loss = 0

        # [0] 🐣 단밤 돌파
        if strategy_mode == '0':
            t = df.iloc[-1]; y = df.iloc[-2]
            if pd.isna(t['Black_Line']): return None
            if (y['Close'] < y['Black_Line']) and (t['Close'] > t['Black_Line']):
               score_str = "🐣단밤돌파"; rec_entry = int(curr); target_price = int(t['Gray_Line'])
            else: return None
        # [1] 💎 최바닥주
        elif strategy_mode == '1':
            t = df.iloc[-1]; blue = t['Blue_Line']
            if pd.isna(blue) or blue == 0: return None
            if (curr - blue) / blue * 100 > 7.0: return None
            if t['Close'] <= t['Open']: return None
            if pd.isna(t['MA5']) or t['Close'] < t['MA5']: return None
            if t['Amount'] < 50000000: return None
            score_str = "💎찐바닥(추세전환)"; rec_entry = int(curr); stop_loss = int(blue)
        # [2] 🚀 눌림목
        elif strategy_mode == '2':
            t = df.iloc[-1]
            ma20 = t['MA20']; ma60 = t['MA60']
            if pd.isna(ma20) or pd.isna(ma60): return None
            if ma20 < ma60: return None 
            gap = (curr - ma20) / ma20 * 100
            if not (-2.0 <= gap <= 2.5): return None 
            recent_high = df['High'].iloc[-20:].max()
            if recent_high < ma20 * 1.10: return None 
            vol_ma20 = df['Volume'].iloc[-20:].mean()
            if df['Volume'].iloc[-1] > vol_ma20 * 2.0: return None 
            score_str = "🚀급등 후 눌림목"; rec_entry = int(curr); target_price = int(recent_high); stop_loss = int(ma60)
        # [3] 🏆 바닥+돌파
        elif strategy_mode == '3':
            t = df.iloc[-1]; y = df.iloc[-2]; ma20 = t['MA20']; blue_line = t['Blue_Line']
            if pd.isna(ma20) or pd.isna(blue_line): return None
            if (curr - blue_line) / blue_line * 100 > 15.0: return None
            if not (y['Close'] < y['MA20'] and t['Close'] > t['MA20']): return None
            if t['Close'] <= t['Open']: return None
            if t['Volume'] < y['Volume'] * 1.5: return None
            if t['Amount'] < 100000000: return None
            score_str = "🏆바닥권 20일선 돌파"; rec_entry = int(curr); target_price = int(t['MA60']) if t['MA60'] > curr else int(curr * 1.15); stop_loss = int(ma20)
        # [4] ⚡ 계단상승
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
        # [5] 📐 스나이퍼
        elif strategy_mode == '5':
            trend_info = get_trend_breakout(df)
            if not trend_info: return None
            g = (curr - df['MA20'].iloc[-1]) / df['MA20'].iloc[-1] * 100
            if g > 5 or g < -3: return None
            score_str = "📐스나이퍼"; rec_entry = int(curr); target_price = int(curr * 1.10); stop_loss = int(df['MA20'].iloc[-1])
        # [6] 🌸 분홍화살표
        elif strategy_mode == '6':
            found = False
            if df['Amount'].iloc[-1] < 300000000: return None
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
                rec_entry = int(t['Close']); target_price = int(curr * 1.15); 
                stop_loss = int(t['Low']); found = True; break
            if not found: return None
        # [7] 🔥 급등 단타
        elif strategy_mode == '7':
            t = df.iloc[-1]; y = df.iloc[-2]
            if (t['Close'] - y['Close']) / y['Close'] * 100 < 5.0: return None
            if t['Amount'] < 1000000000: return None
            vol_ma20 = df['Volume'].iloc[-21:-1].mean()
            if t['Volume'] < y['Volume'] * 2.0 and t['Volume'] < vol_ma20 * 2.0: return None
            body = t['Close'] - t['Open']
            upper_tail = t['High'] - t['Close']
            if body <= 0: return None 
            if upper_tail > body: return None 
            if not pd.isna(t['MA20']) and t['Close'] < t['MA20']: return None
            score_str = f"🔥급등포착(+{round((t['Close']-y['Close'])/y['Close']*100,1)}%)"; 
            rec_entry = int(curr); target_price = int(curr * 1.10); stop_loss = int(t['Open'])
        # [8] 🛫 이륙 준비
        elif strategy_mode == '8':
            t = df.iloc[-1]; ma112 = t['MA112']; black = t['Black_Line']
            if pd.isna(ma112) or pd.isna(black): return None
            if curr < ma112: return None
            if (curr - ma112) / ma112 * 100 > 5.0: return None
            if curr < black: return None
            if t['MA20'] < t['MA60']: return None
            if t['Amount'] < 500000000: return None
            score_str = "🛫이륙준비 (112선 지지)"; rec_entry = int(curr); 
            target_price = int(t['MA224'] if not pd.isna(t['MA224']) else curr*1.15); 
            stop_loss = int(ma112 * 0.98)
        # [9] 🌊 첫 턴
        elif strategy_mode == '9':
            t = df.iloc[-1]; y = df.iloc[-2]; y2 = df.iloc[-3]
            blue = t['Blue_Line']
            if min(t['Low'], y['Low'], y2['Low']) > blue * 1.015: return None
            if t['Close'] <= t['Open']: return None
            if y['Close'] > y['MA5']: return None
            if t['Close'] <= t['MA5']: return None
            if t['Close'] > t['MA60'] * 1.05: return None
            resistances = [t['MA20'], t['MA60'], t['MA120'], t['MA112'], t['MA224']]
            valid_resistances = [r for r in resistances if not pd.isna(r) and r > curr]
            if len(valid_resistances) > 0:
                nearest_wall = min(valid_resistances); profit_room = (nearest_wall - curr) / curr * 100
                if profit_room < 3.0: return None
                target_price = int(nearest_wall); note_str = f"기대수익: {profit_room:.1f}%"
            else: target_price = int(curr * 1.15); note_str = "상방열림"
            score_str = f"🌊확실한 턴 ({note_str})"; rec_entry = int(curr); stop_loss = int(t['Open'])
        # [10] ☁️ 일목균형표
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
            recent_high_60 = df['High'].iloc[-60:-1].max()
            if t['Close'] < recent_high_60: return None
            score_str = f"☁️구름돌파 ({int(t['Volume']/y['Volume']*100)}%)"; rec_entry = int(curr); target_price = int(curr * 1.15); stop_loss = int(min(t['MA60'], t['Span1']))
        else: return None

        if rec_entry == 0: rec_entry = int(curr)
        if target_price == 0: target_price = int(curr * 1.10)
        if stop_loss == 0: stop_loss = int(curr * 0.95)

        return {
            '시장': market, '종목명': name, '코드': code,
            '현재가': curr,
            '등락률': round((curr - df['Close'].iloc[-2])/df['Close'].iloc[-2]*100, 2),
            '점수': score_str, '비고': note_str,
            '목표가': target_price, '추천진입가': rec_entry, '손절선': stop_loss,
            'trend_info': trend_info
        }
    except Exception as e:
        return None

# ---------------------------------------------------------
# 5. 차트 그리기 함수
# ---------------------------------------------------------
def draw_chart(code, name, score_str, target_price, stop_loss):
    try:
        df = fdr.DataReader(code, (datetime.now()-timedelta(days=600)))
        df = calculate_indicators(df)
        plot_df = df.iloc[-150:] 

        fig, ax = plt.subplots(figsize=(12, 6)) 

        # 1. 캔들 그리기
        for idx in plot_df.index:
            o, h, l, c = plot_df.loc[idx, ['Open', 'High', 'Low', 'Close']]
            color = 'red' if c >= o else 'blue'
            ax.vlines(idx, l, h, color=color, linewidth=1)
            ax.bar(idx, height=c-o, bottom=o, width=0.6, color=color)

        # 2. 이동평균선
        if 'MA112' in plot_df.columns:
            ax.plot(plot_df.index, plot_df['MA112'], color='#800080', linewidth=2, linestyle='--', label='112일선')
        
        if 'MA224' in plot_df.columns:
            ax.plot(plot_df.index, plot_df['MA224'], color='#555555', linewidth=3, label='224일선')

        # 3. 목표가/손절선 (선 + 텍스트)
        ax.axhline(y=target_price, color='red', linestyle=':', linewidth=2)
        ax.axhline(y=stop_loss, color='blue', linestyle=':', linewidth=2)

        start_date = plot_df.index[0] # 왼쪽 정렬을 위해 시작 날짜 사용
        
        ax.text(start_date, target_price, f' 목표가 {int(target_price):,} ', 
                color='red', fontsize=11, fontweight='bold', ha='left', va='bottom', fontproperties=FONT_PROP)
        
        ax.text(start_date, stop_loss, f' 손절선 {int(stop_loss):,} ', 
                color='blue', fontsize=11, fontweight='bold', ha='left', va='top', fontproperties=FONT_PROP)

        # 4. 전략별 추가 지표
        if '구름' in score_str:
            ax.fill_between(plot_df.index, plot_df['Span1'], plot_df['Span2'], where=(plot_df['Span1'] >= plot_df['Span2']), facecolor='#ffbfbf', alpha=0.3)
            ax.fill_between(plot_df.index, plot_df['Span1'], plot_df['Span2'], where=(plot_df['Span1'] < plot_df['Span2']), facecolor='#aebbff', alpha=0.3)
            ax.plot(plot_df.index, plot_df['MA60'], color='orange', linewidth=2, label='60일선')
        elif 'MA88' in score_str:
            ax.plot(plot_df.index, plot_df['MA20'], color='green', linewidth=1)
            ax.plot(plot_df.index, plot_df['MA88'], color='magenta', linewidth=2, label='88일선')
        else:
            ax.plot(plot_df.index, plot_df['MA20'], color='green', linewidth=1, label='20일선')
            ax.plot(plot_df.index, plot_df['MA60'], color='orange', linewidth=1, label='60일선')

        ax.set_title(f"{name} ({code}) - {score_str}", fontproperties=FONT_PROP, fontsize=15)
        ax.grid(True, alpha=0.2, linestyle='--')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.legend(loc='best', prop=FONT_PROP)
        
        return fig
    except Exception as e:
        return None

# ---------------------------------------------------------
# 6. UI 메인 (Streamlit)
# ---------------------------------------------------------

today_cnt, total_cnt = track_visitors()

with st.sidebar:
    st.header("🔍 검색 설정")
    market_option = st.selectbox("시장 선택", ["KOSPI", "KOSDAQ", "KRX (전체)"])
    strategy_option = st.selectbox("전략 선택", [
        "0: 🐣 단밤 돌파",
        "1: 💎 찐바닥 (최바닥주)",
        "2: 🚀 급등 후 눌림목 (추천)",
        "3: 🏆 바닥권 20일선 돌파",
        "4: ⚡ 정배열 계단상승",
        "5: 📐 스나이퍼 (추세돌파)",
        "6: 🌸 MA88 지지 (분홍화살표)",
        "7: 🔥 급등 단타 (강력필터)",
        "8: 🛫 이륙 준비 (정배열 초입)",
        "9: 🌊 첫 턴 (손익비 필터)",
        "10: ☁️ 일목균형표 구름돌파"
    ], index=2)
    
    st.markdown("---")
    min_price = st.number_input("최소 주가 (원)", value=1000, step=100)
    max_price = st.number_input("최대 주가 (원)", value=500000, step=1000)
    
    st.markdown("---")
    st.info("💡 팁: '8번', '7번' 전략은 필터가 강화되어 종목이 적게 나올 수 있습니다.")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.title("💎 전설의 매매 (App Ver)")
with col2:
    st.markdown(
        """
        <div style="background-color:#d4edda; padding:10px; border-radius:10px; text-align:center; border:1px solid #c3e6cb;">
            <span style="color:green; font-weight:bold; font-size:18px;">🟢 현재 접속중: ON</span>
        </div>
        """, unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f"""
        <div style="text-align:right; font-size:14px; color:gray;">
            오늘 접속자: <b>{today_cnt}</b>명<br>
            전체 접속자: <b>{total_cnt}</b>명
        </div>
        """, unsafe_allow_html=True
    )

st.markdown("---")

if st.button("🔍 종목 스캔 시작 (Start)", type="primary"):
    mode = strategy_option.split(":")[0] 
    market_code = "KOSPI" if market_option == "KOSPI" else "KOSDAQ" if market_option == "KOSDAQ" else "KRX"
    
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    status_text.text(f"⏳ {market_code} 종목 리스트 불러오는 중...")
    
    try:
        df_krx = fdr.StockListing(market_code)
        df_krx = df_krx[~df_krx['Name'].str.contains('스팩|ETF|ETN|리츠|우B|우C|홀딩스', regex=True)]
        
        for c in ['Close', 'Amount', 'ChagesRatio']: 
            df_krx[c] = pd.to_numeric(df_krx[c], errors='coerce')
            
        target = df_krx[(df_krx['Close'] >= min_price) & (df_krx['Close'] <= max_price)]
        
        total_items = len(target)
        status_text.text(f"📊 대상 종목: {total_items}개 분석 시작...")
        
        res = []
        completed = 0
        
        with ThreadPoolExecutor(max_workers=15) as exe:
            fut = [exe.submit(analyze_stock, row, mode) for _, row in target.iterrows()]
            for f in as_completed(fut):
                completed += 1
                if r := f.result():
                    res.append(r)
                if completed % (total_items // 100 + 1) == 0:
                    progress_bar.progress(completed / total_items)

        progress_bar.progress(1.0)
        
        if not res:
            status_text.error(f"❌ 조건에 맞는 종목이 없습니다. ({mode}번 전략)")
            if 'scan_result' in st.session_state:
                del st.session_state['scan_result'] 
        else:
            status_text.success(f"✨ {len(res)}개 종목 발견 완료!")
            df_r = pd.DataFrame(res).sort_values('등락률', ascending=False).reset_index(drop=True)
            st.session_state['scan_result'] = df_r

    except Exception as e:
        status_text.error(f"오류 발생: {e}")

# ---------------------------------------------------------
# 결과 표시 (차트 상단, 리스트 하단 구조)
# ---------------------------------------------------------
if 'scan_result' in st.session_state:
    df_r = st.session_state['scan_result']
    
    # 1. 차트가 들어갈 자리(상단)를 미리 확보 (Container)
    chart_container = st.container()

    # 2. 종목 리스트 표시 (하단)
    st.markdown("### 📋 검색된 종목 리스트")
    st.info("👇 리스트에서 종목을 클릭하면 **바로 위 상단**에 차트가 나타납니다.")

    event = st.dataframe(
        df_r[['시장', '종목명', '코드', '현재가', '등락률', '점수', '추천진입가', '목표가', '손절선']],
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True,
        height=400 # 모바일에서 너무 길지 않게 고정
    )

    # 3. 선택 이벤트 발생 시 -> 상단 Container에 차트 그리기
    if len(event.selection.rows) > 0:
        selected_index = event.selection.rows[0]
        selected_row = df_r.iloc[selected_index]
        
        with chart_container:
            st.markdown(f"### 📈 {selected_row['종목명']} ({selected_row['코드']}) 상세 분석")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("현재가", f"{int(selected_row['현재가']):,}원", f"{selected_row['등락률']}%")
            c2.metric("추천 진입가", f"{int(selected_row['추천진입가']):,}원")
            c3.metric("목표가", f"{int(selected_row['목표가']):,}원")
            c4.metric("손절가", f"{int(selected_row['손절선']):,}원")
            
            with st.spinner("차트 로딩 중..."):
                fig = draw_chart(
                    selected_row['코드'], 
                    selected_row['종목명'], 
                    selected_row['점수'], 
                    selected_row['목표가'], 
                    selected_row['손절선']
                )
                if fig:
                    st.pyplot(fig)
                    st.markdown(f"[🔗 네이버 증권 바로가기](https://finance.naver.com/item/main.naver?code={selected_row['코드']})")
            
            st.markdown("---") # 차트와 리스트 사이 구분선
