import streamlit as st
import google.generativeai as genai

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="일반기계기사 학습 가이드",
    page_icon="⚙️",
    layout="wide"
)

# 2. 제목 및 소개
st.title("⚙️ 일반기계기사 독학 가이드 🎬")
st.markdown("""
유튜브 무료 강의와 핵심 기출 풀이 영상 모음입니다. 
주제를 클릭하면 **유튜브 검색 결과**로 바로 연결됩니다.
""")

st.divider()

# --------------------------------------------------------------------------------
# [Part 1] Gemini AI 튜터 ✅ 사용 가능한 모델 자동 감지
# --------------------------------------------------------------------------------
with st.container():
    st.markdown("### 🤖 AI 튜터에게 질문하기")
    st.caption("궁금한 개념(예: 베르누이 방정식, 랭킨 사이클)을 입력하면 AI가 설명해줍니다.")

    query = st.text_input("질문 입력", placeholder="예: 재료역학 공부 순서 알려줘")

    if query:
        try:
            if "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
                genai.configure(api_key=api_key)
                
                with st.spinner("AI가 답변을 생성 중입니다..."):
                    # ✅ 해결: 사용 가능한 모델 목록에서 자동 선택
                    available_models = []
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            available_models.append(m.name)
                    
                    # 우선순위: gemini-1.5 > gemini-1.0
                    model_name = None
                    for model_candidate in available_models:
                        if 'gemini-1.5-flash' in model_candidate or 'gemini-1.5-pro' in model_candidate:
                            model_name = model_candidate
                            break
                    
                    if not model_name and available_models:
                        model_name = available_models[0]
                    
                    if model_name:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(query)
                        
                        st.success("답변 완료!")
                        st.markdown(f"**💡 AI 답변:**\n\n{response.text}")
                        st.caption(f"사용된 모델: {model_name}")
                    else:
                        st.error("사용 가능한 모델을 찾을 수 없습니다.")
            else:
                st.error("⚠️ API 키 설정이 필요합니다. (App Settings > Secrets 확인)")
                
        except Exception as e:
            st.error(f"에러 발생: {e}")
            # 디버깅용: 사용 가능한 모델 출력
            try:
                st.warning("사용 가능한 모델 목록:")
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        st.text(f"- {m.name}")
            except:
                pass

st.divider()

# --------------------------------------------------------------------------------
# [Part 2] 📺 1. 추천 유튜브 채널
# --------------------------------------------------------------------------------
st.header("📺 1. 추천 유튜브 채널")
st.caption("채널명을 클릭하면 해당 채널의 영상 목록으로 이동합니다.")

col_ch1, col_ch2, col_ch3, col_ch4, col_ch5 = st.columns(5)

with col_ch1:
    st.markdown("👉 [**기계달인**](https://www.youtube.com/results?search_query=기계달인+일반기계기사)\n(전과목 강의)")
with col_ch2:
    st.markdown("👉 [**에듀윌 기계**](https://www.youtube.com/results?search_query=에듀윌+일반기계기사)\n(핵심 요약)")
with col_ch3:
    st.markdown("👉 [**메가파이**](https://www.youtube.com/results?search_query=메가파이+일반기계기사)\n(자격증 꿀팁)")
with col_ch4:
    st.markdown("👉 [**한솔아카데미**](https://www.youtube.com/results?search_query=한솔아카데미+일반기계기사)\n(기출 해설)")
with col_ch5:
    st.markdown("👉 [**공밀레**](https://www.youtube.com/results?search_query=공밀레+재료역학)\n(개념 이해)")

st.markdown("")

# --------------------------------------------------------------------------------
# [Part 3] 🔍 2. 과목별 핵심 강의
# --------------------------------------------------------------------------------
st.header("🔍 2. 과목별 핵심 강의")

# 1️⃣ 재료역학
with st.expander("1️⃣ 재료역학 (기계구조해석) - 펼쳐보기", expanded=True):
    st.markdown("""
- [🧱 **기초/입문**: 재료역학 기초 강의 보기](https://www.youtube.com/results?search_query=재료역학+기초+강의)
- [📉 **SFD/BMD**: 전단력/굽힘모멘트 선도 그리기](https://www.youtube.com/results?search_query=SFD+BMD+그리는법)
- [➰ **보의 처짐**: 보의 처짐 공식 및 문제풀이](https://www.youtube.com/results?search_query=재료역학+보의+처짐)
- [🌀 **모어원**: 모어원(Mohr's Circle) 그리는 법](https://www.youtube.com/results?search_query=재료역학+모어원)
- [🏛️ **기둥/좌굴**: 오일러의 좌굴 공식](https://www.youtube.com/results?search_query=재료역학+좌굴+공식)
- [📝 **기출문제**: 재료역학 기출문제 풀이](https://www.youtube.com/results?search_query=일반기계기사+재료역학+기출문제)
""")

# 2️⃣ 기계열역학
with st.expander("2️⃣ 기계열역학 (열·유체해석 Part 1) - 펼쳐보기"):
    st.markdown("""
- [🔥 **기초 개념**: 열역학 0,1,2법칙](https://www.youtube.com/results?search_query=열역학+법칙+설명)
- [🔄 **사이클**: 오토/디젤/사바테/랭킨 사이클](https://www.youtube.com/results?search_query=열역학+사이클+정리)
- [🌡️ **엔트로피**: 엔트로피 개념 및 계산](https://www.youtube.com/results?search_query=열역학+엔트로피)
- [📝 **기출문제**: 열역학 기출문제 풀이](https://www.youtube.com/results?search_query=일반기계기사+열역학+기출)
""")

# 3️⃣ 기계유체역학
with st.expander("3️⃣ 기계유체역학 (열·유체해석 Part 2) - 펼쳐보기"):
    st.markdown("""
- [💧 **유체 성질**: 점성계수와 단위 변환](https://www.youtube.com/results?search_query=유체역학+점성계수)
- [🌪️ **베르누이**: 베르누이 방정식 응용](https://www.youtube.com/results?search_query=베르누이+방정식+문제풀이)
- [📏 **관로 마찰**: 레이놀즈 수와 손실수두](https://www.youtube.com/results?search_query=달시+바이스바흐+공식)
- [📝 **기출문제**: 유체역학 기출문제 풀이](https://www.youtube.com/results?search_query=일반기계기사+유체역학+기출)
""")

# 4️⃣ 기계요소설계
with st.expander("4️⃣ 기계요소설계 (기계제도 및 설계) - 펼쳐보기"):
    st.markdown("""
- [⚙️ **기어/베어링**: 기어 치형과 베어링 수명](https://www.youtube.com/results?search_query=기계요소설계+기어+베어링)
- [🔩 **나사/볼트**: 나사의 역학 및 효율](https://www.youtube.com/results?search_query=기계요소설계+나사+효율)
- [🛡️ **파손 이론**: 각종 파손 이론 정리](https://www.youtube.com/results?search_query=기계설계+파손이론)
""")

st.markdown("")

# --------------------------------------------------------------------------------
# [Part 4] 🎯 3. 실기 대비
# --------------------------------------------------------------------------------
st.header("🎯 3. 실기 대비 (필답형 & 작업형)")

col_prac1, col_prac2 = st.columns(2)

with col_prac1:
    st.subheader("📝 필답형")
    st.markdown("""
- [📖 **필답형 요약 정리** (공식 암기용)](https://www.youtube.com/results?search_query=일반기계기사+필답형+요약)
- [✍️ **필답형 기출 문제 풀이**](https://www.youtube.com/results?search_query=일반기계기사+필답형+기출)
""")

with col_prac2:
    st.subheader("💻 작업형 (2D/3D)")
    st.markdown("""
- [🖱️ **작업형 인벤터 기초 강의**](https://www.youtube.com/results?search_query=일반기계기사+인벤터+기초)
- [📐 **작업형 투상(도면해독) 연습**](https://www.youtube.com/results?search_query=일반기계기사+투상+연습)
- [📏 **거칠기 & 기하공차 넣는 법**](https://www.youtube.com/results?search_query=일반기계기사+거칠기+기하공차)
""")

st.divider()
st.caption("🔥 일반기계기사 합격을 기원합니다! | Created with Python & Streamlit")
