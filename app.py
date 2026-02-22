import streamlit as st
import google.generativeai as genai
from PIL import Image
import re
import urllib.parse
import asyncio
import edge_tts
import io
import base64
from pathlib import Path
import tempfile

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="일반기계기사 학습 가이드",
    page_icon="⚙️",
    layout="wide"
)

# ========== 🎤 TTS 기능 추가 ==========
async def text_to_speech_async(text, voice="ko-KR-SunHiNeural"):
    """
    Edge TTS로 한국어 음성 생성 (비동기)
    voice 옵션:
    - ko-KR-SunHiNeural: 여자 목소리 (부드럽고 자연스러움)
    - ko-KR-InJoonNeural: 남자 목소리 (차분하고 명확함)
    """
    communicate = edge_tts.Communicate(text, voice)
    
    # 메모리에 저장
    audio_data = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.write(chunk["data"])
    
    audio_data.seek(0)
    return audio_data.getvalue()

def text_to_speech(text, voice="ko-KR-SunHiNeural"):
    """
    동기 래퍼 함수
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_bytes = loop.run_until_complete(text_to_speech_async(text, voice))
        loop.close()
        return audio_bytes
    except Exception as e:
        st.error(f"음성 생성 실패: {e}")
        return None

def create_audio_player(audio_bytes):
    """
    HTML5 오디오 플레이어 생성
    """
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
    <audio controls autoplay style="width: 100%;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        브라우저가 오디오를 지원하지 않습니다.
    </audio>
    """
    return audio_html

def clean_text_for_tts(text):
    """
    TTS용 텍스트 정제 (마크다운 제거, 특수문자 처리)
    """
    # 마크다운 링크 제거 [텍스트](url) -> 텍스트
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 마크다운 강조 제거 (**, __, ~~)
    text = re.sub(r'[*_~`]+', '', text)
    
    # 헤딩 마크 제거 (###, ##, #)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    
    # 이모지 제거 또는 설명으로 변환
    emoji_map = {
        '✅': '체크',
        '❌': '주의',
        '⚠️': '경고',
        '💡': '팁',
        '📺': '영상',
        '🔍': '검색',
        '📝': '노트',
        '🎯': '목표',
        '🔥': '중요',
        '📚': '학습',
        '⚙️': '기계',
        '🎬': '동영상'
    }
    
    for emoji, desc in emoji_map.items():
        text = text.replace(emoji, f' {desc} ')
    
    # 남은 이모지 제거
    text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
    
    # 연속 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    # 너무 긴 텍스트는 앞부분만 (TTS 제한 고려)
    max_length = 3000  # Edge TTS 권장 최대 길이
    if len(text) > max_length:
        text = text[:max_length] + "... 이하 생략됩니다."
    
    return text.strip()

# ========== 기존 코드 (유지) ==========

# 2. 제목 및 소개
st.title("⚙️ 일반기계기사 독학 가이드 🎬")
st.markdown("""
영욱이와 설매의 합격을 기원합니다.
유튜브 무료 강의와 핵심 기출 풀이 영상 모음입니다. 
주제를 클릭하면 **유튜브 검색 결과**로 바로 연결됩니다.
""")

st.divider()

# 기존 함수들 (그대로 유지)
def format_youtube_links(text):
    youtube_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'https?://(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]+)',
        r'https?://youtu\.be/([a-zA-Z0-9_-]+)'
    ]
    
    def replace_youtube(match):
        video_id = match.group(1)
        full_url = match.group(0)
        
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
    url_pattern = r'(https?://(?!(?:www\.)?youtube\.com|youtu\.be)[^\s\)]+)'
    
    def replace_url(match):
        url = match.group(1).rstrip('.,;:!?')
        return f'[🔗 링크 보기]({url})'
    
    return re.sub(url_pattern, replace_url, text)

def add_youtube_search_links(text):
    keywords = [
        "재료역학", "열역학", "유체역학", "기계요소설계",
        "SFD", "BMD", "베르누이", "모어원", "좌굴", "엔트로피",
        "랭킨 사이클", "오토 사이클", "디젤 사이클",
        "레이놀즈 수", "기어", "베어링", "나사", "에너지 보존",
        "응력", "변형률", "전단력", "굽힘모멘트"
    ]
    
    channel_names = [
        "홍교수", "기계의신", "기계달인", "에듀윌", "메가파이", 
        "한솔아카데미", "공밀레", "Learn Engineering"
    ]
    
    all_keywords = keywords + channel_names
    
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links_found = re.findall(link_pattern, text)
    
    protected_text = text
    placeholders = []
    for i, (link_text, link_url) in enumerate(links_found):
        placeholder = f"__LINK_PLACEHOLDER_{i}__"
        original = f"[{link_text}]({link_url})"
        protected_text = protected_text.replace(original, placeholder, 1)
        placeholders.append((placeholder, original))
    
    modified_text = protected_text
    used_keywords = set()
    
    for keyword in all_keywords:
        if keyword in modified_text and keyword not in used_keywords:
            search_query = urllib.parse.quote(f"{keyword} 일반기계기사")
            youtube_link = f"https://www.youtube.com/results?search_query={search_query}"
            
            pattern = rf'\b({re.escape(keyword)})\b'
            
            if re.search(pattern, modified_text):
                replacement = f'[\\1 📺]({youtube_link})'
                modified_text = re.sub(pattern, replacement, modified_text, count=1)
                used_keywords.add(keyword)
    
    channel_pattern = r'채널명:\s*([가-힣a-zA-Z\s]+?)(?=\n|$|특징)'
    
    def replace_channel(match):
        channel_name = match.group(1).strip()
        search_query = urllib.parse.quote(f"{channel_name} 일반기계기사")
        youtube_link = f"https://www.youtube.com/results?search_query={search_query}"
        return f'채널명: [{channel_name} 📺]({youtube_link})'
    
    modified_text = re.sub(channel_pattern, replace_channel, modified_text)
    
    video_pattern = r'추천 영상(?:\s*제목)?:\s*[""""]([^""""\n]+)[""""]'
    
    def replace_video(match):
        video_title = match.group(1).strip()
        search_query = urllib.parse.quote(video_title)
        youtube_link = f"https://www.youtube.com/results?search_query={search_query}"
        return f'추천 영상: ["{video_title}" 🎬]({youtube_link})'
    
    modified_text = re.sub(video_pattern, replace_video, modified_text)
    
    for placeholder, original in placeholders:
        modified_text = modified_text.replace(placeholder, original)
    
    return modified_text

def get_best_gemini_model():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        priority_order = [
            'gemini-3',
            'gemini-2.5',
            'gemini-2.0', 
            'gemini-1.5',
            'gemini-pro'
        ]
        
        for priority in priority_order:
            for model_name in available_models:
                if priority in model_name.lower():
                    return model_name
        
        if available_models:
            return available_models[0]
        
        return None
        
    except Exception as e:
        st.error(f"모델 목록 조회 실패: {e}")
        return None

def get_model_display_name(model_name):
    if not model_name:
        return "알 수 없음"
    
    model_mapping = {
        'gemini-3': 'Gemini 3 Flash',
        'gemini-2.5': 'Gemini 2.5 Flash',
        'gemini-2.0': 'Gemini 2.0 Flash',
        'gemini-1.5': 'Gemini 1.5 Pro',
        'gemini-pro': 'Gemini Pro'
    }
    
    for key, display_name in model_mapping.items():
        if key in model_name.lower():
            return display_name
    
    return model_name

# 세션 스테이트 초기화
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = None
if 'model_name' not in st.session_state:
    st.session_state.model_name = None
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'audio_playing' not in st.session_state:
    st.session_state.audio_playing = False
if 'selected_voice' not in st.session_state:
    st.session_state.selected_voice = "ko-KR-SunHiNeural"

# ========== AI 튜터 섹션 ==========
with st.container():
    st.markdown("### 🤖 AI 튜터에게 질문하기")
    st.caption("궁금한 개념을 텍스트 또는 **이미지(스크린샷, 문제 사진)**로 질문하세요!")

    tab1, tab2 = st.tabs(["📝 텍스트 질문", "📸 이미지 질문"])
    
    # 텍스트 질문 탭
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
                    
                    with st.spinner("🤖 AI가 답변을 생성 중입니다..."):
                        model_name = get_best_gemini_model()
                        
                        if model_name:
                            model = genai.GenerativeModel(model_name)
                            
                            enhanced_query = f"""
다음 질문에 대해 일반기계기사 시험 준비생 관점에서 친절하게 답변해주세요:

{query}

답변 형식:
1. 핵심 개념 설명 (이해하기 쉽게)
2. 공식이나 계산 방법 (있다면)
3. 시험 출제 경향 및 주의사항
4. 📺 추천 채널 및 영상 (아래 형식으로):
   
   **채널명:** 홍교수
   **특징:** 간결한 설명
   **추천 영상:** "열역학 1법칙 완벽 정리"
   
   (이런 식으로 2-3개 채널 추천)

5. 유튜브 검색 키워드 3개
"""
                            
                            response = model.generate_content(enhanced_query)
                            
                            st.session_state.ai_response = response.text
                            st.session_state.model_name = model_name
                            st.session_state.uploaded_image = None
                        else:
                            st.error("❌ 사용 가능한 Gemini 모델을 찾을 수 없습니다.")
                else:
                    st.error("⚠️ API 키가 설정되지 않았습니다. Streamlit Secrets에 GOOGLE_API_KEY를 추가하세요.")
                    
            except Exception as e:
                st.error(f"❌ 에러 발생: {e}")
                if "429" in str(e):
                    st.warning("⏰ API 사용량 제한에 도달했습니다. 잠시 후 다시 시도하세요.")
                elif "403" in str(e):
                    st.warning("🔑 API 키가 유효하지 않습니다. 새로운 키를 발급받으세요.")
    
    # 이미지 질문 탭
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
                    
                    with st.spinner("🖼️ AI가 이미지를 분석 중입니다..."):
                        model_name = get_best_gemini_model()
                        
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
4. 📺 추천 유튜브 채널 및 영상 (채널명과 영상 제목 포함)
5. 검색 키워드
"""
                            else:
                                prompt = """
이 이미지를 자세히 분석하고 설명해주세요.

답변 형식:
1. 이미지에 포함된 내용 (문제, 도면, 공식 등)
2. 관련 개념 설명
3. 문제라면 풀이 과정
4. 📺 추천 유튜브 채널 및 영상
5. 검색 키워드
"""
                            
                            response = model.generate_content([prompt, image])
                            
                            st.session_state.ai_response = response.text
                            st.session_state.model_name = model_name
                            st.session_state.uploaded_image = image
                        else:
                            st.error("❌ 사용 가능한 Gemini 모델을 찾을 수 없습니다.")
                else:
                    st.error("⚠️ API 키가 설정되지 않았습니다.")
                    
            except Exception as e:
                st.error(f"❌ 에러 발생: {e}")
                if "429" in str(e):
                    st.warning("⏰ API 사용량 제한에 도달했습니다. 잠시 후 다시 시도하세요.")
                elif "403" in str(e):
                    st.warning("🔑 API 키가 유효하지 않습니다.")

    # ✅ 답변 표시 + TTS 기능
    st.markdown("")
    if st.session_state.ai_response:
        # 상단 컨트롤 버튼
        col_del, col_voice, col_tts = st.columns([1, 2, 2])
        
        with col_del:
            if st.button("🗑️ 답변 삭제", key="delete_top", use_container_width=True):
                st.session_state.ai_response = None
                st.session_state.model_name = None
                st.session_state.uploaded_image = None
                st.session_state.uploader_key += 1
                st.session_state.audio_playing = False
                st.rerun()
        
        with col_voice:
            voice_option = st.selectbox(
                "🎙️ 목소리 선택",
                options=[
                    ("ko-KR-SunHiNeural", "👩 여자 목소리 (부드러움)"),
                    ("ko-KR-InJoonNeural", "👨 남자 목소리 (차분함)")
                ],
                format_func=lambda x: x[1],
                key="voice_selector"
            )
            st.session_state.selected_voice = voice_option[0]
        
        with col_tts:
            if st.button("🔊 음성으로 듣기", key="tts_button", use_container_width=True):
                with st.spinner("🎤 음성을 생성하는 중..."):
                    # TTS용 텍스트 정제
                    clean_text = clean_text_for_tts(st.session_state.ai_response)
                    
                    # 음성 생성
                    audio_bytes = text_to_speech(clean_text, st.session_state.selected_voice)
                    
                    if audio_bytes:
                        st.session_state.audio_playing = True
                        st.success("✅ 음성이 준비되었습니다!")
        
        # 오디오 플레이어 표시
        if st.session_state.audio_playing:
            st.markdown("---")
            st.markdown("### 🎧 음성 재생")
            
            # 음성 재생
            clean_text = clean_text_for_tts(st.session_state.ai_response)
            audio_bytes = text_to_speech(clean_text, st.session_state.selected_voice)
            
            if audio_bytes:
                audio_html = create_audio_player(audio_bytes)
                st.markdown(audio_html, unsafe_allow_html=True)
                
                if st.button("⏹️ 음성 정지", key="stop_audio"):
                    st.session_state.audio_playing = False
                    st.rerun()
            
            st.markdown("---")
        
        # 업로드된 이미지 표시
        if st.session_state.uploaded_image:
            col_img, col_space = st.columns([1, 2])
            with col_img:
                st.image(st.session_state.uploaded_image, caption="질문한 이미지", use_column_width=True)
        
        # AI 답변 표시
        response_text = st.session_state.ai_response
        response_text = format_youtube_links(response_text)
        response_text = add_youtube_search_links(response_text)
        response_text = make_links_clickable(response_text)
        
        st.markdown("---")
        st.markdown("### 💡 AI 답변")
        st.markdown(response_text, unsafe_allow_html=True)
        
        # 모델 정보
        display_name = get_model_display_name(st.session_state.model_name)
        
        with st.expander("🤖 사용된 AI 모델 정보", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                **코어 모델:** {display_name}  
                **운영 티어:** Free Tier (무료 버전)  
                **기술 ID:** `{st.session_state.model_name}`
                """)
            with col2:
                st.markdown("""
                **지원 기능:**
                - ✅ 텍스트 생성
                - ✅ 이미지 분석 (Vision)
                - ✅ 멀티모달 처리
                - ✅ 음성 출력 (TTS)
                """)

st.divider()

# ========== 나머지 기존 코드 (유튜브 채널, 과목별 강의 등) ==========
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

st.header("🔍 2. 과목별 핵심 강의")

with st.expander("1️⃣ 재료역학 (기계구조해석) - 펼쳐보기", expanded=False):
    st.markdown("""
- [🧱 **기초/입문**: 재료역학 기초 강의 보기](https://www.youtube.com/results?search_query=재료역학+기초+강의)
- [📉 **SFD/BMD**: 전단력/굽힘모멘트 선도 그리기](https://www.youtube.com/results?search_query=SFD+BMD+그리는법)
- [➰ **보의 처짐**: 보의 처짐 공식 및 문제풀이](https://www.youtube.com/results?search_query=재료역학+보의+처짐)
- [🌀 **모어원**: 모어원(Mohr's Circle) 그리는 법](https://www.youtube.com/results?search_query=재료역학+모어원)
- [🏛️ **기둥/좌굴**: 오일러의 좌굴 공식](https://www.youtube.com/results?search_query=재료역학+좌굴+공식)
- [📝 **기출문제**: 재료역학 기출문제 풀이](https://www.youtube.com/results?search_query=일반기계기사+재료역학+기출문제)
""")

with st.expander("2️⃣ 기계열역학 (열·유체해석 Part 1) - 펼쳐보기"):
    st.markdown("""
- [🔥 **기초 개념**: 열역학 0,1,2법칙](https://www.youtube.com/results?search_query=열역학+법칙+설명)
- [🔄 **사이클**: 오토/디젤/사바테/랭킨 사이클](https://www.youtube.com/results?search_query=열역학+사이클+정리)
- [🌡️ **엔트로피**: 엔트로피 개념 및 계산](https://www.youtube.com/results?search_query=열역학+엔트로피)
- [💨 **냉동 사이클**: 증기압축/흡수식 냉동](https://www.youtube.com/results?search_query=일반기계기사+냉동사이클)
- [📝 **기출문제**: 열역학 기출문제 풀이](https://www.youtube.com/results?search_query=일반기계기사+열역학+기출)
""")

with st.expander("3️⃣ 기계유체역학 (열·유체해석 Part 2) - 펼쳐보기"):
    st.markdown("""
- [💧 **유체 성질**: 점성계수와 단위 변환](https://www.youtube.com/results?search_query=유체역학+점성계수)
- [🌪️ **베르누이**: 베르누이 방정식 응용](https://www.youtube.com/results?search_query=베르누이+방정식+문제풀이)
- [📏 **관로 마찰**: 레이놀즈 수와 손실수두](https://www.youtube.com/results?search_query=달시+바이스바흐+공식)
- [⚡ **운동량 방정식**: 충격력 계산](https://www.youtube.com/results?search_query=유체역학+운동량방정식)
- [📝 **기출문제**: 유체역학 기출문제 풀이](https://www.youtube.com/results?search_query=일반기계기사+유체역학+기출)
""")

with st.expander("4️⃣ 기계요소설계 (기계제도 및 설계) - 펼쳐보기"):
    st.markdown("""
- [⚙️ **기어/베어링**: 기어 치형과 베어링 수명](https://www.youtube.com/results?search_query=기계요소설계+기어+베어링)
- [🔩 **나사/볼트**: 나사의 역학 및 효율](https://www.youtube.com/results?search_query=기계요소설계+나사+효율)
- [🛡️ **파손 이론**: 각종 파손 이론 정리](https://www.youtube.com/results?search_query=기계설계+파손이론)
- [🔗 **축/커플링**: 축 설계 및 키 결합](https://www.youtube.com/results?search_query=기계요소설계+축+설계)
- [📝 **기출문제**: 기계요소설계 기출](https://www.youtube.com/results?search_query=일반기계기사+기계요소설계+기출)
""")

st.markdown("")

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

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🔥 <strong>일반기계기사 합격을 응원합니다!</strong> 🔥</p>
    <p style='font-size: 0.9em;'>💡 TIP: AI 튜터에게 모르는 부분을 바로 질문하고 음성으로도 들어보세요!</p>
    <p style='font-size: 0.8em; margin-top: 10px;'>
        Made with ❤️ by Streamlit | Powered by Google Gemini AI + Edge TTS
    </p>
</div>
""", unsafe_allow_html=True)
