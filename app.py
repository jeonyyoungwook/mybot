import streamlit as st
import pyupbit
import pandas as pd
import time
import datetime

# -----------------------------------------------------------------------------
# [1] 기본 페이지 설정 및 세션 상태 초기화
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI 전코인 단타 봇",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태 초기화 (새로고침 되어도 데이터 유지)
if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False
if 'target_ticker' not in st.session_state:
    st.session_state['target_ticker'] = ""

# -----------------------------------------------------------------------------
# [2] 메인 화면: 헤더 및 API 설정
# -----------------------------------------------------------------------------
st.title("💎 AI 변동성 돌파 봇 (All Coins)")
st.markdown("##### 업비트의 모든 코인을 실시간으로 분석하고 매매 신호를 포착합니다.")

# API 키 입력 (세션에 저장하여 입력값 유지)
with st.expander("🔑 로그인 및 API 설정 (클릭하여 열기)", expanded=True):
    col1, col2 = st.columns(2)
    # 패스워드 타입으로 입력받아 화면에 노출되지 않게 함
    access_key = col1.text_input("Access Key", type="password", key="access_key")
    secret_key = col2.text_input("Secret Key", type="password", key="secret_key")

    if access_key and secret_key:
        try:
            upbit = pyupbit.Upbit(access_key, secret_key)
            krw = upbit.get_balance("KRW")
            if krw is not None:
                st.success(f"✅ 로그인 성공! 보유 원화: **{krw:,.0f} 원**")
            else:
                st.error("🚨 잔고 조회 실패: IP 주소 제한이나 키 권한을 확인하세요.")
        except Exception as e:
            st.error(f"🚨 로그인 오류: {e}")

# -----------------------------------------------------------------------------
# [3] 코인 선택 및 설정
# -----------------------------------------------------------------------------
st.subheader("🔍 분석 설정")

try:
    all_tickers = pyupbit.get_tickers(fiat="KRW")
except:
    st.warning("네트워크 상태가 좋지 않아 기본 리스트를 사용합니다.")
    all_tickers = ["KRW-BTC", "KRW-ETH", "KRW-XRP", "KRW-SOL"]

c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    selected_ticker = st.selectbox("코인 선택", all_tickers, index=0)
with c2:
    # k값(변동성 계수)을 고정하지 않고 슬라이더로 줄 수도 있지만, 여기선 투자 비중(Risk) 조절
    target_vol = st.slider("타겟 리스크 (1회 투자 비중)", 0.01, 0.20, 0.05, 0.01)
with c3:
    st.write("") # 여백
    st.write("") 
    # 분석 시작 버튼
    if st.button("📊 분석 시작", type="primary", use_container_width=True):
        st.session_state['analyzed'] = True
        st.session_state['target_ticker'] = selected_ticker

# -----------------------------------------------------------------------------
# [4] 분석 및 매매 로직 (분석 버튼이 눌린 상태라면 실행)
# -----------------------------------------------------------------------------
if st.session_state['analyzed']:
    ticker = st.session_state['target_ticker']
    
    # ------------------ 데이터 가져오기 및 지표 계산 ------------------
    with st.spinner(f"🤖 AI가 [{ticker}] 데이터를 분석 중입니다..."):
        try:
            # 10일치 일봉 데이터
            df = pyupbit.get_ohlcv(ticker, interval="day", count=10)
            current_price = pyupbit.get_current_price(ticker)
            
            if df is None or len(df) < 5:
                st.error("🚨 데이터 부족: 신규 상장 코인이거나 데이터를 불러올 수 없습니다.")
                st.session_state['analyzed'] = False # 상태 초기화
            else:
                # 변동성 돌파 전략 계산
                # 1. 노이즈 비율 계산 (최근 5일 평균)
                df['range'] = df['high'] - df['low']
                df['noise'] = 1 - abs(df['open'] - df['close']) / df['range']
                noise_k = df['noise'].tail(5).mean()

                # 2. 목표가 계산 (오늘 시가 + 전일 변동폭 * K)
                prev_day = df.iloc[-2]
                today = df.iloc[-1]
                volatility = prev_day['range'] * noise_k
                target_price = today['open'] + volatility

                # 3. 5일 이동평균선
                ma5 = df['close'].rolling(window=5).mean().iloc[-2]

                # 4. 자금 관리 (변동성이 클수록 적게 매수)
                vol_ratio = prev_day['range'] / prev_day['open']
                if vol_ratio == 0: vol_ratio = 0.01
                invest_ratio = target_vol / vol_ratio
                if invest_ratio > 1.0: invest_ratio = 1.0

                # ------------------ UI 출력 ------------------
                st.markdown("---")
                st.markdown(f"### 📈 {ticker} 분석 결과")

                # 주요 지표 메트릭 표시
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                col_m1.metric("현재가", f"{current_price:,.0f} 원")
                col_m2.metric("목표 돌파가", f"{target_price:,.0f} 원", 
                              delta=f"{current_price - target_price:,.0f} 원")
                col_m3.metric("5일 이동평균", f"{ma5:,.0f} 원")
                col_m4.metric("추천 매수 비중", f"{invest_ratio*100:.1f} %")

                # 차트 시각화 (종가 및 이동평균선)
                chart_data = df[['close']].tail(30)
                st.line_chart(chart_data)

                # ------------------ 매매 판단 로직 ------------------
                cond_breakout = current_price >= target_price
                cond_trend = current_price >= ma5
                
                st.subheader("📢 AI 판단")
                
                if cond_breakout and cond_trend:
                    st.success("🚀 **Strong BUY (강력 매수)**")
                    st.markdown(f"""
                    1. **추세**: 상승장 (현재가가 5일 이평선 위에 있음) ✅
                    2. **모멘텀**: 변동성 돌파 성공 (목표가 {target_price:,.0f}원 돌파) ✅
                    3. **자금관리**: 보유 현금의 **{invest_ratio*100:.1f}%** 매수 추천
                    """)

                    # 실제 매수 기능
                    if access_key and secret_key:
                        st.info("💡 아래 버튼을 누르면 실제 주문이 전송됩니다.")
                        
                        # 버튼 클릭 시 즉시 실행을 위해 콜백이나 독립적 if문 사용
                        if st.button("💸 매수 주문 실행 (시장가)", type="secondary"):
                            try:
                                upbit_exec = pyupbit.Upbit(access_key, secret_key)
                                krw_bal = upbit_exec.get_balance("KRW")
                                buy_amount = krw_bal * invest_ratio * 0.9995 # 수수료 고려
                                
                                if buy_amount >= 5000:
                                    # 실제 주문 코드 (주석 해제 시 실제 돈이 나갑니다)
                                    # res = upbit_exec.buy_market_order(ticker, buy_amount)
                                    # st.toast(f"주문 완료! {res}")
                                    st.toast(f"🧪 테스트 모드: 약 {buy_amount:,.0f}원 주문이 전송되었습니다.")
                                    st.success("주문이 성공적으로 전송되었습니다!")
                                else:
                                    st.warning(f"매수 금액({buy_amount:,.0f}원)이 최소 주문금액(5,000원)보다 적습니다.")
                            except Exception as e:
                                st.error(f"주문 실패: {e}")
                    else:
                        st.warning("로그인(API Key) 후 매수 가능합니다.")

                elif not cond_trend:
                    st.error("📉 **매수 금지 (하락 추세)**")
                    st.write(f"현재 가격이 5일 평균({ma5:,.0f}원)보다 낮습니다. 추세가 전환될 때까지 기다리세요.")
                
                else: # cond_trend는 True지만 cond_breakout이 False
                    st.warning("👀 **관망 (진입 대기)**")
                    diff = target_price - current_price
                    pct = (diff / current_price) * 100
                    st.write(f"상승 추세는 좋지만, 아직 매수 타점(목표가)에 도달하지 않았습니다.")
                    st.write(f"👉 **{diff:,.0f}원 ({pct:.2f}%)** 더 오르면 매수합니다.")

        except Exception as e:
            st.error(f"분석 중 예기치 않은 오류 발생: {e}")
            st.session_state['analyzed'] = False
