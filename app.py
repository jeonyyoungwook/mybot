import os
import time
import urllib.request

# 1. 설치 (화면에 로그가 많이 뜰 수 있습니다)
print("🚀 프로그램 설치 중... (약 1~2분 소요)")
os.system("pip install -q streamlit pyupbit pandas pyngrok")
os.system("npm install -g localtunnel")

# 2. 봇 코드 파일 생성 (app.py)
bot_code = """
import streamlit as st
import pyupbit
import pandas as pd
import time

# 페이지 설정
st.set_page_config(page_title="코랩용 단타봇", layout="wide")

# 세션 상태 초기화
if 'analyzed' not in st.session_state: st.session_state['analyzed'] = False
if 'target_ticker' not in st.session_state: st.session_state['target_ticker'] = ""

st.title("💎 구글 코랩용 AI 단타 봇")
st.markdown("---")

# 사이드바: 로그인
with st.sidebar:
    st.header("🔑 로그인 설정")
    st.info("주의: IP 미지정 API 키를 사용하세요.")
    access_key = st.text_input("Access Key", type="password")
    secret_key = st.text_input("Secret Key", type="password")
    
    if access_key and secret_key:
        try:
            upbit = pyupbit.Upbit(access_key, secret_key)
            krw = upbit.get_balance("KRW")
            if krw is not None:
                st.success(f"✅ 로그인 성공! 잔고: {krw:,.0f} 원")
            else:
                st.error("🚨 잔고 조회 실패 (IP 설정을 확인하세요)")
        except Exception as e:
            st.error(f"로그인 에러: {e}")

# 메인: 코인 선택
st.subheader("🔍 분석할 코인 선택")
try:
    tickers = pyupbit.get_tickers(fiat="KRW")
except:
    tickers = ["KRW-BTC", "KRW-ETH", "KRW-XRP"]

col1, col2 = st.columns([3, 1])
with col1:
    selected_ticker = st.selectbox("코인 목록", tickers)
with col2:
    if st.button("📊 분석 시작", use_container_width=True):
        st.session_state['analyzed'] = True
        st.session_state['target_ticker'] = selected_ticker

# 분석 결과 화면
if st.session_state['analyzed']:
    ticker = st.session_state['target_ticker']
    st.markdown("---")
    
    with st.spinner(f"{ticker} 분석 중..."):
        try:
            df = pyupbit.get_ohlcv(ticker, interval="day", count=10)
            curr_price = pyupbit.get_current_price(ticker)
            
            # 전략: 변동성 돌파
            noise = 1 - abs(df['open'] - df['close']) / (df['high'] - df['low'])
            k = noise.tail(5).mean()
            volatility = (df.iloc[-2]['high'] - df.iloc[-2]['low']) * k
            target_price = df.iloc[-1]['open'] + volatility
            
            # 화면 표시
            c1, c2, c3 = st.columns(3)
            c1.metric("현재가", f"{curr_price:,.0f} 원")
            c2.metric("목표 매수가", f"{target_price:,.0f} 원")
            
            # 차트
            st.line_chart(df['close'].tail(20))
            
            # 매매 신호
            if curr_price >= target_price:
                st.success("🚀 **매수 신호 발생!** (현재가가 목표가를 넘었습니다)")
                
                # 매수 로직
                st.write("▼ 아래 버튼을 누르면 잔고의 50%만큼 시장가 매수합니다.")
                if st.button("💸 매수 실행 (시장가)"):
                    if access_key and secret_key:
                        upbit = pyupbit.Upbit(access_key, secret_key)
                        krw = upbit.get_balance("KRW")
                        if krw and krw > 5000:
                            # 50% 매수
                            buy_amount = krw * 0.5
                            upbit.buy_market_order(ticker, buy_amount)
                            st.toast(f"✅ 주문 완료! 약 {buy_amount:,.0f}원 매수됨.")
                            st.success("주문이 전송되었습니다.")
                        else:
                            st.warning("잔액이 부족하거나(5천원 미만) 로그인이 필요합니다.")
                    else:
                        st.error("먼저 왼쪽 사이드바에서 API 키를 입력하세요.")
            else:
                st.info(f"💤 관망 중... (목표가까지 {target_price - curr_price:,.0f}원 남음)")
                
        except Exception as e:
            st.error(f"데이터 분석 실패: {e}")
"""

# 파일 저장
with open("app.py", "w", encoding='utf-8') as f:
    f.write(bot_code)

print("✅ 설치 및 파일 생성 완료!")
print("="*60)
print("🔑 아래 IP 숫자를 복사하세요 (Password):")
# 외부 IP 확인
print(urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip())
print("="*60)
print("🌐 잠시 후 아래 'your url is...' 옆의 링크를 클릭하세요.")

# 3. 실행 (백그라운드)
os.system("streamlit run app.py & npx localtunnel --port 8501")
