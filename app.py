import streamlit as st
import pyupbit
import pandas as pd
import time

# -----------------------------------------------------------------------------
# [1] 기본 페이지 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI 비트코인 단타 봇",
    page_icon="💸",
    layout="wide"
)

st.title("💸 AI 변동성 돌파 단타 봇 (V1.0)")
st.caption("전략: 변동성 돌파 + 5일 이평선(추세) + 노이즈 필터 + 자금 관리(2% 룰)")

# -----------------------------------------------------------------------------
# [2] 사이드바 (설정)
# -----------------------------------------------------------------------------
st.sidebar.header("🔧 설정 메뉴")

# API 키 입력 (저장되지 않음)
access_key = st.sidebar.text_input("Access Key", type="password")
secret_key = st.sidebar.text_input("Secret Key", type="password")

# 코인 선택
ticker = st.sidebar.selectbox("거래할 코인", ["KRW-BTC", "KRW-ETH", "KRW-XRP", "KRW-SOL"])

# 목표 리스크 (기본 2%)
target_vol = st.sidebar.slider("타겟 리스크 (높을수록 공격적)", 0.01, 0.05, 0.02)

st.sidebar.markdown("---")
st.sidebar.info("💡 **전략 요약**\n\n1. 상승장일 때만 산다.\n2. 시장이 깔끔하면 많이 산다.\n3. 시장이 지저분하면 적게 산다.")

# -----------------------------------------------------------------------------
# [3] 데이터 분석 함수 (우리가 코랩에서 테스트한 것들)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=10) # 10초마다 데이터 갱신
def get_analysis(ticker):
    try:
        # 최근 10일치 데이터 가져오기
        df = pyupbit.get_ohlcv(ticker, interval="day", count=10)
        if df is None or len(df) < 5: return None
        
        current_price = pyupbit.get_current_price(ticker)
        
        # 1. 노이즈 비율 계산 (최근 5일 평균)
        df['noise'] = 1 - abs(df['open'] - df['close']) / (df['high'] - df['low'])
        noise_k = df['noise'].tail(5).mean()
        
        # 2. 변동성 돌파 목표가 계산 (K = noise_k)
        prev = df.iloc[-2]
        today = df.iloc[-1]
        range_val = prev['high'] - prev['low']
        target_price = today['open'] + (range_val * noise_k)
        
        # 3. 5일 이동평균선 계산
        ma5 = df['close'].rolling(window=5).mean().iloc[-2]
        
        # 4. 자금 관리 (투자 비중)
        yesterday_vol = (prev['high'] - prev['low']) / prev['open']
        invest_ratio = target_vol / yesterday_vol
        if invest_ratio > 1.0: invest_ratio = 1.0
        
        return {
            'current_price': current_price,
            'target_price': target_price,
            'ma5': ma5,
            'noise_k': noise_k,
            'invest_ratio': invest_ratio,
            'today_open': today['open']
        }
    except:
        return None

# -----------------------------------------------------------------------------
# [4] 메인 화면 표시
# -----------------------------------------------------------------------------
if st.button("🔄 시장 데이터 분석 실행"):
    with st.spinner("AI가 시장 데이터를 분석 중입니다..."):
        data = get_analysis(ticker)
        
    if data:
        # 주요 지표 표시
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("현재 가격", f"{data['current_price']:,.0f} 원")
        col2.metric("목표 매수가", f"{data['target_price']:,.0f} 원")
        col3.metric("5일 이평선", f"{data['ma5']:,.0f} 원")
        col4.metric("추천 투자비중", f"{data['invest_ratio']*100:.1f} %")
        
        st.markdown("---")
        
        # 매매 조건 판단
        cond1 = data['current_price'] >= data['target_price'] # 돌파 성공?
        cond2 = data['current_price'] >= data['ma5']          # 상승장?
        
        st.subheader("🤖 AI 매매 판단 결과")
        
        if cond1 and cond2:
            st.success(f"🚀 **매수 신호 발생!** (조건 1, 2 모두 만족)")
            st.write(f"👉 **전략**: 보유 현금의 **{data['invest_ratio']*100:.1f}%** 만큼만 매수하세요.")
            
            # 자동 매매 실행 로직 (키가 있을 때만)
            if access_key and secret_key:
                try:
                    upbit = pyupbit.Upbit(access_key, secret_key)
                    krw = upbit.get_balance("KRW")
                    if krw > 5000:
                        buy_amount = krw * data['invest_ratio'] * 0.9995 # 수수료 제외
                        st.info(f"💸 자동 주문 시도: 약 {buy_amount:,.0f}원 매수")
                        # 주석을 풀면 진짜 매수됩니다!
                        # upbit.buy_market_order(ticker, buy_amount) 
                        # st.toast("주문 완료!")
                    else:
                        st.warning("잔액이 부족하거나 이미 매수했습니다.")
                except Exception as e:
                    st.error(f"주문 실패: {e}")
        
        elif not cond1 and cond2:
            st.warning("💤 **대기 중** (상승장이지만, 아직 목표가 돌파 전입니다)")
            diff = data['target_price'] - data['current_price']
            st.write(f"-> 목표가까지 **{diff:,.0f}원** 남았습니다.")
            
        elif cond1 and not cond2:
            st.error("🛡️ **매수 금지** (목표가는 넘었지만, 하락장입니다)")
            st.write("-> 5일 이평선 아래라 위험합니다.")
            
        else:
            st.error("🥶 **관망 필요** (하락장이며, 힘도 없습니다)")
            
    else:
        st.error("데이터를 가져올 수 없습니다. 잠시 후 다시 시도하세요.")
