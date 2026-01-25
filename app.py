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
        
