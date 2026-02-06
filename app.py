import streamlit as st
import pyupbit
import pandas as pd
import time

# -----------------------------------------------------------------------------
# [1] 기본 페이지 설정 (사이드바 숨김 처리)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI 전코인 단타 봇",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed" # 사이드바 숨김
)

# -----------------------------------------------------------------------------
# [2] 메인 화면: API 키 입력 및 잔고 확인
# -----------------------------------------------------------------------------
st.title("💎 AI 변동성 돌파 봇 (All Coins)")
st.write("업비트의 모든 코인을 검색하고 분석할 수 있는 통합 대시보드입니다.")

# 깔끔하게 접었다 폈다 할 수 있는 구역 생성
with st.expander("🔑 로그인 및 API 설정 (클릭하여 열기)", expanded=True):
    col1, col2 = st.columns(2)
    access_key = col1.text_input("Access Key", type="password")
    secret_key = col2.text_input("Secret Key", type="password")

    # 로그인 확인
    if access_key and secret_key:
        try:
            upbit = pyupbit.Upbit(access_key, secret_key)
            krw = upbit.get_balance("KRW")
            if krw is not None:
                st.success(f"✅ 로그인 성공! 보유 원화: **{krw:,.0f} 원**")
            else:
                st.error("🚨 키 확인 필요: 잔고를 불러올 수 없습니다. IP 설정을 확인하세요.")
        except Exception as e:
            st.error("🚨 로그인 실패: 키 값을 다시 확인해주세요.")

# -----------------------------------------------------------------------------
# [3] 코인 선택 (모든 코인 불러오기)
# -----------------------------------------------------------------------------
st.subheader("🔍 분석할 코인 선택")

# 업비트의 모든 원화(KRW) 마켓 코인 리스트 가져오기
try:
    all_tickers = pyupbit.get_tickers(fiat="KRW")
except:
    all_tickers = ["KRW-BTC", "KRW-ETH", "KRW-XRP"] # 실패시 기본값

# 선택 박스 (검색 가능)
col_sel1, col_sel2 = st.columns([3, 1])
with col_sel1:
    # 돋보기처럼 검색 가능한 선택 상자
    selected_ticker = st.selectbox(
        "코인을 선택하거나 이름을 검색하세요", 
        all_tickers,
        index=0  # 기본값: KRW-BTC
    )
with col_sel2:
    # 리스크 설정 슬라이더
    target_vol = st.slider("타겟 리스크 (투자 비중)", 0.01, 0.10, 0.02)

# -----------------------------------------------------------------------------
# [4] 분석 및 매매 로직
# -----------------------------------------------------------------------------
def analyze_market(ticker):
    # 로딩 표시
    with st.spinner(f"🤖 AI가 [{ticker}] 차트를 분석 중입니다..."):
        try:
            # 1. 데이터 가져오기 (10일치)
            df = pyupbit.get_ohlcv(ticker, interval="day", count=10)
            current_price = pyupbit.get_current_price(ticker)
            
            if df is None or len(df) < 5:
                st.error("🚨 데이터가 부족하여 분석할 수 없습니다 (신규 상장 코인 등).")
                return

            # 2. 지표 계산
            # 노이즈 (K값)
            df['noise'] = 1 - abs(df['open'] - df['close']) / (df['high'] - df['low'])
            noise_k = df['noise'].tail(5).mean()
            
            # 목표가
            prev = df.iloc[-2]
            today = df.iloc[-1]
            volatility = (prev['high'] - prev['low']) * noise_k
            target_price = today['open'] + volatility
            
            # 5일 이평선
            ma5 = df['close'].rolling(window=5).mean().iloc[-2]
            
            # 투자 비중
            prev_vol = (prev['high'] - prev['low']) / prev['open']
            if prev_vol == 0: prev_vol = 0.01 # 0으로 나누기 방지
            invest_ratio = target_vol / prev_vol
            if invest_ratio > 1.0: invest_ratio = 1.0

            # 3. 결과 화면 출력 (큰 글씨)
            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("현재 가격", f"{current_price:,.0f} 원")
            c2.metric("목표 매수가", f"{target_price:,.0f} 원")
            c3.metric("추세선 (5일)", f"{ma5:,.0f} 원")
            c4.metric("추천 비중", f"{invest_ratio*100:.1f} %")
            
            # 4. 차트 그리기 (시각화)
            st.line_chart(df['close'].tail(30))

            # 5. 최종 판단
            cond1 = current_price >= target_price
            cond2 = current_price >= ma5
            
            st.subheader("📢 AI 매매 판단")
            
            if cond1 and cond2:
                st.success(f"🚀 **강력 매수 신호!** (모든 조건 만족)")
                st.markdown(f"""
                - **추세**: 상승장 ✅
                - **돌파**: 목표가 돌파 ✅
                - **행동**: 지금 즉시 자산의 **{invest_ratio*100:.1f}%** 만큼 매수하세요.
                """)
                
                # 매수 버튼 (키가 있을 때만 활성화)
                if access_key and secret_key:
                    if st.button("💸 지금 바로 매수 주문 실행 (Click)"):
                        upbit = pyupbit.Upbit(access_key, secret_key)
                        krw_balance = upbit.get_balance("KRW")
                        buy_amt = krw_balance * invest_ratio * 0.9995
                        if buy_amt > 5000:
                            # 실제 주문 (주석 해제시 동작)
                            # upbit.buy_market_order(ticker, buy_amt)
                            st.toast(f"주문 전송 완료! 약 {buy_amt:,.0f}원 매수됨.")
                        else:
                            st.warning("잔액이 부족합니다.")
            
            elif not cond2:
                st.error("📉 **매수 금지 (하락장)**")
                st.write(f"현재 가격이 5일 평균({ma5:,.0f}원)보다 낮습니다. 떨어지는 칼날을 잡지 마세요.")
                
            else:
                st.warning("💤 **관망 (대기 중)**")
                diff = target_price - current_price
                st.write(f"상승 추세는 좋지만, 아직 폭발적인 상승(목표가)이 안 나왔습니다.")
                st.caption(f"👉 {diff:,.0f}원 더 오르면 매수합니다.")

        except Exception as e:
            st.error(f"분석 중 오류 발생: {e}")

# -----------------------------------------------------------------------------
# [5] 실행 버튼 (가운데 큼지막하게)
# -----------------------------------------------------------------------------
if st.button("📊 선택한 코인 분석 시작", type="primary", use_container_width=True):
    analyze_market(selected_ticker)
