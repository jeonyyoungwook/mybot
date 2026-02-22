import streamlit as st
import google.generativeai as genai
from PIL import Image
import re
import urllib.parse

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
# ✅ 유튜브 링크 예쁘게 표시하는 함수
# --------------------------------------------------------------------------------
def format_youtube_links(text):
    """
    유튜브 링크를 예쁜 카드 형식으로 변환
    """
    # 유튜브 링크 패턴 (watch, shorts, youtu.be 모두 지원)
    youtube_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'https?://(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]+)',
        r'https?://youtu\.be/([a-zA-Z0-9_-]+)'
    ]
    
    def replace_youtube(match):
        video_id = match.group(1)
        full_url = match.group(0)
        
        # 예쁜 카드 형식으로 변환
        return f"""
<div style="border: 2px solid #ff0000; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #fff5f5;">
    <h4 style="color: #ff0000; margin-top: 0;">📺 추천 영상</h4>
    <a href="{full_url}" target="_blank">
        <img src="https://img.youtube.com/vi/{video_id}/mqdefault.jpg" style="width: 100%; border-radius: 5px; margin: 10px 0;">
    </a>
    <a href="{full_url}" target="_blank" style="display: inline-block; background-color: #ff0000; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold;">
        🎬 영상 바로보기 →
    </a>
</div>
"""
    
    formatted_text = text
    for pattern in youtube_patterns:
        formatted_text = re.sub(pattern, replace_youtube, formatted_text)
    
    return formatted_text

def make_links_clickable(text):
    """일반 URL을 클릭 가능한 링크로 변환 (유튜브 제외)"""
    # 유튜브가 아닌 다른 링크만 변환
    url_pattern = r'(https?://(?!(?:www\.)?youtube\.com|youtu\.be)[^\s\)]+)'
    
    def replace_url(match):
        url = match.group(1).rstrip('.,;:!?')
        return f'[🔗 링크 보기]({url})'
    
    return re.sub(url_pattern, replace_url, text)

def add_youtube_search_links(text):
    """주요 키워드에 유튜브 검색 링크 추가"""
    keywords = [
        "재료역학", "열역학", "유체역학", "기계요소설계",
        "SFD", "BMD", "베르누이", "모어원", "좌굴", "엔트로피",
        "랭킨 사이클", "오토 사이클", "디젤 사이클",
        "레이놀즈 수", "기어", "베어링", "나사", "에너지 보존",
        "응력", "변형률", "전단력", "굽힘모멘트"
    ]
    
    modified_text = text
    used_keywords = set()
    
    for keyword in keywords:
        # 각 키워드를 한 번만 링크로 변환
        if keyword in modified_text and keyword not in used_keywords:
            search_query = urllib.parse.quote(f"{keyword} 일반기계기사")
            youtube_link = f"https://www.youtube.com/results?search_query={search_query}"
            
            pattern = f"(?<!\\[)\\b({re.escape(keyword)})\\b(?!\\])"
            replacement = f"[\\1 📺]({youtube_link})"
            modified_text = re.sub(pattern, replacement, modified_text, count=1)
            used_keywords.add(keyword)
    
    return modified_text

# --------------------------------------------------------------------------------
# [Part 1] Gemini AI 튜터
# --------------------------------------------------------------------------------

# 세션 스테이트 초기화
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = None
if 'model_name' not in st.session_state:
    st.session_state.model_name = None
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

with st.container():
    st.markdown("### 🤖 AI 튜터에게 질문하기")
    st.caption("궁금한 개념을 텍스트 또는 **이미지(스크린샷, 문제 사진)**로 질문하세요!")

    tab1, tab2 = st.tabs(["📝 텍스트 질문", "📸 이미지 질문"])
    
    # ========== 탭 1: 텍스트 질문 ==========
    with tab1:
        with st.form(key="text_question_form", clear_on_submit=True):
            query = st.text_input("질문 입력", placeholder="예: 재료역학 공부 순서 알려줘")
            
            col1, col2 = st.columns([1, 5])
            with col1:
                text_submit_btn = st.form_submit_button("🔍 질문하기", use_container_width=True)
            with col2:
                pass

        if text_submit_btn and query:
            try:
                if "GOOGLE_API_KEY" in st.secrets:
                    api_key = st.secrets["GOOGLE_API_KEY"]
                    genai.configure(api_key=api_key)
                    
                    with st.spinner("AI가 답변을 생성 중입니다..."):
                        available_models = []
                        for m in genai.list_models():
                            if 'generateContent' in m.supported_generation_methods:
                                available_models.append(m.name)
                        
                        model_name = None
                        for model_candidate in available_models:
                            if 'gemini-1.5' in model_candidate:
                                model_name = model_candidate
                                break
                        
                        if not model_name and available_models:
                            model_name = available_models[0]
                        
                        if model_name:
                            model = genai.GenerativeModel(model_name)
                            
                            # ✅ 프롬프트 개선: 유튜브 영상 추천 요청
                            enhanced_query = f"""
다음 질문에 대해 일반기계기사 시험 준비생 관점에서 친절하게 답변해주세요:

{query}

답변 형식:
1. 핵심 개념 설명 (이해하기 쉽게)
2. 공식이나 계산 방법 (있다면)
3. 시험 출제 경향 및 주의사항
4. 추천 학습 자료:
   - 유튜브 검색 키워드 3개 (구체적으로)
   - 관련 영상이 있다면 채널명과 제목
"""
                            
                            response = model.generate_content(enhanced_query)
                            
                            st.session_state.ai_response = response.text
                            st.session_state.model_name = model_name
                            st.session_state.uploaded_image = None
                        else:
                            st.error("사용 가능한 모델을 찾을 수 없습니다.")
                else:
                    st.error("⚠️ API 키가 설정되지 않았습니다.")
                    
            except Exception as e:
                st.error(f"❌ 에러 발생: {e}")
    
    # ========== 탭 2: 이미지 질문 ==========
    with tab2:
        st.markdown("📌 **문제 사진, 도면, 공식 스크린샷** 등을 업로드하세요!")
        
        uploaded_file = st.file_uploader(
            "이미지 업로드 (JPG, PNG)", 
            type=['jpg', 'jpeg', 'png'],
            help="문제 사진이나 이해가 안 되는 부분 스크린샷을 올려주세요",
            key=f"uploader_{st.session_state.uploader_key}"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="업로드된 이미지", use_container_width=True)
            
            if st.button("🖼️ 이미지 삭제", key="delete_image"):
                st.session_state.uploader_key += 1
                st.session_state.uploaded_image = None
                st.rerun()
        
        with st.form(key="image_question_form", clear_on_submit=True):
            image_query = st.text_input(
                "이미지에 대한 질문 (선택)", 
                placeholder="예: 이 문제 풀이 과정 설명해줘"
            )
            
            col1, col2 = st.columns([1, 5])
            with col1:
                image_submit_btn = st.form_submit_button("🔍 이미지 질문", use_container_width=True)
            with col2:
                pass
        
        if image_submit_btn and uploaded_file is not None:
            try:
                if "GOOGLE_API_KEY" in st.secrets:
                    api_key = st.secrets["GOOGLE_API_KEY"]
                    genai.configure(api_key=api_key)
                    
                    with st.spinner("AI가 이미지를 분석 중입니다..."):
                        available_models = []
                        for m in genai.list_models():
                            if 'generateContent' in m.supported_generation_methods:
                                available_models.append(m.name)
                        
                        model_name = None
                        for model_candidate in available_models:
                            if 'gemini-1.5' in model_candidate or 'vision' in model_candidate.lower():
                                model_name = model_candidate
                                break
                        
                        if not model_name and available_models:
                            model_name = available_models[0]
                        
                        if model_name:
                            model = genai.GenerativeModel(model_name)
                            
                            image = Image.open(uploaded_file)
                            
                            if image_query:
                                prompt = f"""
이미지를 분석하고 다음 질문에 답해주세요:
{image_query}

답변에 포함할 내용:
1. 이미지에 보이는 핵심 내용 설명
2. 문제라면 단계별 풀이 과정
3. 관련 개념 및 공식
4. 유튜브 검색 키워드 추천
"""
                            else:
                                prompt = """
이 이미지를 자세히 분석하고 설명해주세요.

답변 형식:
1. 이미지에 포함된 내용 (문제, 도면, 공식 등)
2. 관련 개념 설명
3. 문제라면 풀이 과정
4. 학습에 도움이 될 유튜브 검색 키워드
"""
                            
                            response = model.generate_content([prompt, image])
                            
                            st.session_state.ai_response = response.text
                            st.session_state.model_name = model_name
                            st.session_state.uploaded_image = image
                        else:
                            st.error("사용 가능한 모델을 찾을 수 없습니다.")
                else:
                    st.error("⚠️ API 키가 설정되지 않았습니다.")
                    
            except Exception as e:
                st.error(f"❌ 에러 발생: {e}")
                if "403" in str(e):
                    st.warning("API 키가 유출되었거나 만료되었습니다. 새로운 키를 발급받으세요.")

    # ✅ 위쪽 삭제 버튼
    st.markdown("")
    if st.session_state.ai_response:
        if st.button("🗑️ 답변 삭제", key="delete_top"):
            st.session_state.ai_response = None
            st.session_state.model_name = None
            st.session_state.uploaded_image = None
            st.session_state.uploader_key += 1
            st.rerun()

    # ✅ 저장된 답변 표시 (유튜브 링크 예쁘게)
    if st.session_state.ai_response:
        st.success("✅ 답변 완료!")
        
        if st.session_state.uploaded_image:
            col_img, col_space = st.columns([1, 2])
            with col_img:
                st.image(st.session_state.uploaded_image, caption="질문한 이미지", use_column_width=True)
        
        # ✅ 링크 변환 순서: 유튜브 카드 → 키워드 검색 → 일반 링크
        response_text = st.session_state.ai_response
        response_text = format_youtube_links(response_text)  # 유튜브 → 카드
        response_text = add_youtube_search_links(response_text)  # 키워드 검색
        response_text = make_links_clickable(response_text)  # 일반 링크
        
        st.markdown("---")
        st.markdown("### 💡 AI 답변")
        st.markdown(response_text, unsafe_allow_html=True)
        st.caption(f"🤖 사용 모델: {st.session_state.model_name}")

st.divider()

# --------------------------------------------------------------------------------
# [Part 2] 📺 1. 추천 유튜브 채널
# --------------------------------------------------------------------------------
st.header("📺 1. 추천 유튜브 채널")
st.caption("채널명을 클릭하면 해당 채널의 영상 목록으로 이동합니다.")

col_ch1, col_ch2, col_ch3, col_ch4, col_ch5 = st.columns(5)

with col_ch1:
    st.markdown("👉 [**기계달인**](https://www.youtube.com/results?search_query=기계달인+일반기계기사)\n\n(전과목 강의)")
with col_ch2:
    st.markdown("👉 [**에듀윌 기계**](https://www.youtube.com/results?search_query=에듀윌+일반기계기사)\n\n(핵심 요약)")
with col_ch3:
    st.markdown("👉 [**메가파이**](https://www.youtube.com/results?search_query=메가파이+일반기계기사)\n\n(자격증 꿀팁)")
with col_ch4:
    st.markdown("👉 [**한솔아카데미**](https://www.youtube.com/results?search_query=한솔아카데미+일반기계기사)\n\n(기출 해설)")
with col_ch5:
    st.markdown("👉 [**공밀레**](https://www.youtube.com/results?search_query=공밀레+재료역학)\n\n(개념 이해)")

st.markdown("")

# --------------------------------------------------------------------------------
# [Part 3] 🔍 2. 과목별 핵심 강의
# --------------------------------------------------------------------------------
st.header("🔍 2. 과목별 핵심 강의")

# 1️⃣ 재료역학
with st.expander("1️⃣ 재료역학 (기계구조해석) - 펼쳐보기", expanded=False):
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
- [💨 **냉동 사이클**: 증기압축/흡수식 냉동](https://www.youtube.com/results?search_query=일반기계기사+냉동사이클)
- [📝 **기출문제**: 열역학 기출문제 풀이](https://www.youtube.com/results?search_query=일반기계기사+열역학+기출)
""")

# 3️⃣ 기계유체역학
with st.expander("3️⃣ 기계유체역학 (열·유체해석 Part 2) - 펼쳐보기"):
    st.markdown("""
- [💧 **유체 성질**: 점성계수와 단위 변환](https://www.youtube.com/results?search_query=유체역학+점성계수)
- [🌪️ **베르누이**: 베르누이 방정식 응용](https://www.youtube.com/results?search_query=베르누이+방정식+문제풀이)
- [📏 **관로 마찰**: 레이놀즈 수와 손실수두](https://www.youtube.com/results?search_query=달시+바이스바흐+공식)
- [⚡ **운동량 방정식**: 충격력 계산](https://www.youtube.com/results?search_query=유체역학+운동량방정식)
- [📝 **기출문제**: 유체역학 기출문제 풀이](https://www.youtube.com/results?search_query=일반기계기사+유체역학+기출)
""")

# 4️⃣ 기계요소설계
with st.expander("4️⃣ 기계요소설계 (기계제도 및 설계) - 펼쳐보기"):
    st.markdown("""
- [⚙️ **기어/베어링**: 기어 치형과 베어링 수명](https://www.youtube.com/results?search_query=기계요소설계+기어+베어링)
- [🔩 **나사/볼트**: 나사의 역학 및 효율](https://www.youtube.com/results?search_query=기계요소설계+나사+효율)
- [🛡️ **파손 이론**: 각종 파손 이론 정리](https://www.youtube.com/results?search_query=기계설계+파손이론)
- [🔗 **축/커플링**: 축 설계 및 키 결합](https://www.youtube.com/results?search_query=기계요소설계+축+설계)
- [📝 **기출문제**: 기계요소설계 기출](https://www.youtube.com/results?search_query=일반기계기사+기계요소설계+기출)
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
- [🎯 **자주 나오는 공식 정리**](https://www.youtube.com/results?search_query=일반기계기사+필답형+공식)
""")

with col_prac2:
    st.subheader("💻 작업형 (2D/3D)")
    st.markdown("""
- [🖱️ **작업형 인벤터 기초 강의**](https://www.youtube.com/results?search_query=일반기계기사+인벤터+기초)
- [📐 **작업형 투상(도면해독) 연습**](https://www.youtube.com/results?search_query=일반기계기사+투상+연습)
- [📏 **거칠기 & 기하공차 넣는 법**](https://www.youtube.com/results?search_query=일반기계기사+거칠기+기하공차)
- [⚡ **작업형 기출 실습**](https://www.youtube.com/results?search_query=일반기계기사+작업형+기출)
""")

st.divider()

# --------------------------------------------------------------------------------
# [Part 5] 📚 4. 학습 팁 & 자료
# --------------------------------------------------------------------------------
st.header("📚 4. 학습 팁 & 추가 자료")

with st.expander("💡 효율적인 학습 방법", expanded=False):
    st.markdown("""
### 📌 필기 시험 준비 전략
1. **과목별 배점 파악**: 과목당 40점 이상, 전체 60점 이상
2. **학습 순서 추천**: 재료역학 → 열역학 → 유체역학 → 기계요소설계
3. **기출문제 중심**: 최근 10개년 기출 3회독 이상
4. **취약 과목 집중**: 과락 방지가 최우선

### 📌 실기 시험 준비 전략
1. **필답형**: 주요 공식 암기 + 단위 환산 연습
2. **작업형**: 인벤터 기본 조작 숙달 (최소 20시간)
3. **시간 배분**: 필답 40분, 작업 80분 목표
4. **기하공차/거칠기**: 실전 배치 연습 필수
""")

with st.expander("📖 추천 교재 & 사이트", expanded=False):
    st.markdown("""
### 📚 추천 교재
- **SD에듀** / **예문사** 일반기계기사 필기/실기 교재
- **성안당** 과년도 기출문제집

### 🌐 유용한 사이트
- [큐넷 (Q-Net)](https://www.q-net.or.kr) - 시험 접수 및 기출문제
- [기계기술사 카페](https://cafe.naver.com/mechanicalengineer) - 학습 커뮤니티
- [공학용 계산기 사용법](https://www.youtube.com/results?search_query=공학용계산기+사용법)
""")

st.divider()

# --------------------------------------------------------------------------------
# 푸터
# --------------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🔥 <strong>일반기계기사 합격을 응원합니다!</strong> 🔥</p>
    <p style='font-size: 0.9em;'>💡 TIP: AI 튜터에게 모르는 부분을 바로 질문하세요!</p>
    <p style='font-size: 0.8em; margin-top: 10px;'>
        Made with ❤️ by Streamlit | Powered by Google Gemini AI
    </p>
</div>
""", unsafe_allow_html=True)
