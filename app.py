import streamlit as st
import pyupbit
import pandas as pd
import time
import datetime

# 1. 페이지 기본 설정
st.set_page_config(page_title="AI 자동매매 봇", layout="wide")

# 2. 스타일 설정 (다크모드 & 로그창)
st.markdown("""
    <style>
        .stButton>button { height: 50px; font-weight: bold; border-radius: 10px; }
        .log-box { 
            background-color: #1e1e1e; color: #00ff00; 
            padding: 10px; border-radius: 5px; font-family: monospace; 
            height: 200px; overflow-y: scroll;
        }
    </style>
""", unsafe_allow_html=True)

# 3. 상태 변수 초기화
if 'is_running' not in st.session_state: st.session_state['is_running'] = False
if 'logs' not in st.session_state: st.session_state['logs'] = []

# 4. 로그 함수
def log(msg):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state['logs'].append(f"[{now}] {msg}")
    # 로그가 너무 길어지면 앞부분 삭제
    if len(st.session_state['logs']) > 20:
        st.session_state['logs'].pop(0)

# 5. RSI 계산 함수
def get_rsi(ticker):
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute15", count=200) # 15분봉 기준
        if df is None: return 0
        delta = df['close'].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=13, adjust=False).mean()
        ema_down = down.ewm(com=13, adjust=False).mean()
        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    except:
        return 0

# --- 화면 구성 ---
st.title("🤖 24시간 AI 자동매매 (Auto Bot)")

# [사이드바] 설정 영역
with st.sidebar:
    st.header("⚙️ 설정")
    access = st.text_input("Access Key", type="password")
    secret = st.text_input("Secret Key", type="password")
    target_coin = st.selectbox("매매할 코인", ["KRW-BTC", "KRW-ETH", "KRW-XRP", "KRW-DOGE", "KRW-SOL"])
    
    st.markdown("---")
    st.subheader("매매 전략 (RSI)")
    buy_rsi = st.slider("매수 기준 (RSI 낮을 때)", 20, 40, 30)
    sell_rsi = st.slider("매도 기준 (RSI 높을 때)", 60, 80, 70)
    st.info("💡 15분봉 기준입니다.")

# [메인] 대시보드
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📡 실시간 현황")
    
    # 자동매매 시작/중지 버튼
    if st.session_state['is_running']:
        if st.button("⛔ 자동매매 중지", type="primary"):
            st.session_state['is_running'] = False
            log("사용자에 의해 중지됨.")
            st.experimental_rerun()
    else:
        if st.button("▶️ 자동매매 시작"):
            if access and secret:
                st.session_state['is_running'] = True
                log("자동매매 시작! 시세 감시 중...")
                st.experimental_rerun()
            else:
                st.error("키를 먼저 입력하세요.")

    # 현재 상태 표시
    if st.session_state['is_running']:
        st.success("✅ **작동 중... (브라우저를 닫지 마세요)**")
        
        # --- [핵심 로직] ---
        try:
            upbit = pyupbit.Upbit(access, secret)
            cur_price = pyupbit.get_current_price(target_coin)
            rsi = get_rsi(target_coin)
            krw = upbit.get_balance("KRW")
            coin_bal = upbit.get_balance(target_coin)
            coin_val = coin_bal * cur_price

            # 화면 표시
            m1, m2, m3 = st.columns(3)
            m1.metric("현재가", f"{cur_price:,.0f}원")
            m2.metric("RSI 지표", f"{rsi:.1f}")
            m3.metric("보유 상태", f"{'보유중' if coin_val > 5000 else '대기중'}")

            # 매수 로직
            if coin_val < 5000 and rsi <= buy_rsi:
                if krw >= 5000:
                    upbit.buy_market_order(target_coin, krw * 0.99) # 전량 매수
                    log(f"⚡ [매수] RSI {rsi:.1f} 포착 -> 매수 체결")
                else:
                    log("잔액 부족으로 매수 실패")

            # 매도 로직
            elif coin_val > 5000 and rsi >= sell_rsi:
                upbit.sell_market_order(target_coin, coin_bal) # 전량 매도
                log(f"💰 [매도] RSI {rsi:.1f} 도달 -> 익절/손절")
            
            else:
                # 아무 일도 없으면 로그만 가끔 찍기 (너무 자주 찍히지 않게)
                pass

        except Exception as e:
            log(f"에러 발생: {e}")
            st.error("API 키를 확인하거나 일시적인 오류입니다.")

        # 🔄 자동 새로고침 (이게 있어야 반복됨)
        time.sleep(3) # 3초마다 체크
        st.experimental_rerun()

    else:
        st.warning("💤 봇이 꺼져 있습니다. '시작' 버튼을 누르세요.")

# [로그창]
with col2:
    st.subheader("📜 거래 로그")
    log_text = "<br>".join(reversed(st.session_state['logs']))
    st.markdown(f"<div class='log-box'>{log_text}</div>", unsafe_allow_html=True)
