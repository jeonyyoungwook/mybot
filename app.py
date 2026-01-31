import streamlit as st
import streamlit.components.v1 as components
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
# 1. 페이지 설정 & 모바일 새로고침(Overscroll) 방지
# ---------------------------------------------------------
st.set_page_config(page_title="전설의 매매 검색기", page_icon="💎", layout="wide")

# [핵심] 모바일에서 화면을 당겨서 새로고침 되는 것 방지
st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            overscroll-behavior-y: none !important;
        }
    </style>
""", unsafe_allow_html=True)

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
# 2. 방문자 수 카운트
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
                
