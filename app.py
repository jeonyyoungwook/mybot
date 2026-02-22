import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="일반기계기사 학습 가이드",
    page_icon="⚙️",
    layout="centered"
)

# 제목 및 소개
st.title("⚙️ 일반기계기사 독학 가이드 🎬")
st.write("유튜브 무료 강의와 핵심 기출 풀이 영상 모음입니다. 주제를 클릭하면 유튜브 검색 결과로 연결됩니다.")
st.markdown("---")

# 1. 추천 채널 섹션
st.header("📺 1. 추천 유튜브 채널")
st.info("채널명을 클릭하면 해당 채널의 일반기계기사 영상 목록으로 이동합니다.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("👉 **[기계달인 (전과목 강의)](https://www.youtube.com/results?search_query=기계달인+일반기계기사)**")
    st.markdown("👉 **[에듀윌 기계 (핵심 요약)](https://www.youtube.com/results?search_query=에듀윌+기계기사)**")
    st.markdown("👉 **[메가파이 (자격증 꿀팁)](https://www.youtube.com/results?search_query=메가파이+기계)**")

with col2:
    st.markdown("👉 **[한솔아카데미 (기출 해설)](https://www.youtube.com/results?search_query=한솔아카데미+일반기계기사)**")
    st.markdown("👉 **[공밀레 (개념 이해)](https://www.youtube.com/results?search_query=공밀레+기계)**")

st.markdown("---")

# 2. 과목별 핵심 강의 섹션
st.header("🔍 2. 과목별 핵심 강의")
st.caption("각 항목을 클릭하면 관련 유튜브 강의 검색 결과가 새 창에서 열립니다.")

# 재료역학
with st.expander("1️⃣ 재료역학 (기계구조해석) - 펼쳐보기", expanded=True):
    st.markdown("""
    - 🧱 **[기초/입문: 재료역학 기초 강의 보기](https://www.youtube.com/results?search_query=일반기계기사+재료역학+기초)**
    - 📉 **[SFD/BMD: 전단력/굽힘모멘트 선도 그리기](https://www.youtube.com/results?search_query=재료역학+SFD+BMD)**
    - ➰ **[보의 처짐: 보의 처짐 공식 및 문제풀이](https://www.youtube.com/results?search_query=재료역학+보의+처짐)**
    - 🌀 **[모어원: 모어원(Mohr's Circle) 그리는 법](https://www.youtube.com/results?search_query=재료역학+모어원)**
    - 🏛️ **[기둥/좌굴: 오일러의 좌굴 공식](https://www.youtube.com/results?search_query=재료역학+기둥+좌굴)**
    - 📝 **[기출문제: 재료역학 기출문제 풀이](https://www.youtube.com/results?search_query=일반기계기사+재료역학+기출)**
    """)

# 열역학
with st.expander("2️⃣ 기계열역학 (열·유체해석 Part 1)"):
    st.markdown("""
    - 🔥 **[기초/법칙: 열역학 1법칙 & 2법칙](https://www.youtube.com/results?search_query=일반기계기사+열역학+법칙)**
    - 💨 **[이상기체: 이상기체 상태방정식 강의](https://www.youtube.com/results?search_query=열역학+이상기체+상태방정식)**
    - 🔄 **[동력 사이클: 오토/디젤/사바테 사이클 비교](https://www.youtube.com/results?search_query=열역학+오토+디젤+사이클)**
    - 🏭 **[증기 사이클: 랭킨 사이클 완벽 정리](https://www.youtube.com/results?search_query=열역학+랭킨사이클)**
    - ❄️ **[냉동: 냉동 사이클 & 성적계수(COP)](https://www.youtube.com/results?search_query=열역학+냉동사이클)**
    """)

# 유체역학
with st.expander("3️⃣ 기계유체역학 (열·유체해석 Part 2)"):
    st.markdown("""
    - 💧 **[기초 성질: 유체역학 점성/밀도/비중](https://www.youtube.com/results?search_query=유체역학+점성+밀도)**
    - 🌊 **[베르누이: 베르누이 방정식 문제풀이](https://www.youtube.com/results?search_query=유체역학+베르누이)**
    - 🚰 **[관로 유동: 관 마찰 손실수두 계산](https://www.youtube.com/results?search_query=유체역학+관마찰+손실)**
    - 📏 **[차원 해석: 버킹엄 파이 정리](https://www.youtube.com/results?search_query=유체역학+버킹엄+파이)**
    - ⚙️ **[유체 기계: 펌프/수차/비속도](https://www.youtube.com/results?search_query=유체기계+펌프+수차)**
    """)

# 기계요소설계
with st.expander("4️⃣ 기계요소설계 (기계제도 및 설계)"):
    st.markdown("""
    - 🔩 **[나사/리벳: 나사 효율 및 리벳 이음](https://www.youtube.com/results?search_query=기계설계+나사+리벳)**
    - 🔨 **[축 설계: 축 지름 및 강도 계산](https://www.youtube.com/results?search_query=기계설계+축+설계)**
    - ⚙️ **[기어: 기어 모듈/속도비 계산](https://www.youtube.com/results?search_query=기계설계+기어+계산)**
    - 🔘 **[베어링: 베어링 수명시간 공식](https://www.youtube.com/results?search_query=기계설계+베어링+수명)**
    - 🛑 **[브레이크: 브레이크 제동 토크](https://www.youtube.com/results?search_query=기계설계+브레이크)**
    """)

st.markdown("---")

# 3. 실기 대비 섹션
st.header("🎯 3. 실기 대비 (필답형 & 작업형)")

with st.container():
    st.markdown("""
    - 📝 **[필답형 요약 정리 (공식 암기용)](https://www.youtube.com/results?search_query=일반기계기사+실기+필답형+요약)**
    - 📝 **[필답형 기출 문제 풀이](https://www.youtube.com/results?search_query=일반기계기사+실기+필답형+기출)**
    - 💻 **[작업형 인벤터 기초 강의](https://www.youtube.com/results?search_query=일반기계기사+작업형+인벤터+기초)**
    - 📐 **[작업형 투상(도면해독) 연습](https://www.youtube.com/results?search_query=일반기계기사+작업형+투상)**
    - 📏 **[작업형 거칠기 & 기하공차 넣는 법](https://www.youtube.com/results?search_query=일반기계기사+거칠기+기하공차)**
    """)

st.markdown("---")
st.write("🔥 **일반기계기사 합격을 기원합니다!** Created with Python & Streamlit")
