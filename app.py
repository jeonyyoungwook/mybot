import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from PIL import Image
import re
import urllib.parse
import asyncio
import edge_tts
import io
import base64

# ========== 페이지 설정 ==========
st.set_page_config(
    page_title="일반기계기사 AI 학습 가이드",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== CSS 스타일 ==========
st.markdown("""
<style>
    /* 전체 레이아웃 */
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 1200px;
    }
    
    /* 모바일 최적화 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem;
        }
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.3rem !important; }
        button { min-height: 48px !important; }
        input, textarea { font-size: 16px !important; }
    }
    
    /* YouTube 카드 */
    .youtube-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        color: white;
    }
    
    .youtube-card h3 {
        color: white;
        margin: 0 0 15px 0;
        font-size: 1.3rem;
    }
    
    .video-container {
        position: relative;
        width: 100%;
        padding-bottom: 56.25%;
        border-radius: 12px;
        overflow: hidden;
        background: #000;
        margin: 15px 0;
    }
    
    .video-container iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border: none;
    }
    
    .server-links {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 15px;
    }
    
    .server-btn {
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.3s;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .server-btn:hover {
        background: rgba(255,255,255,0.3);
        transform: translateY(-2px);
        color: white;
        text-decoration: none;
    }
    
    /* 음성 인식 버튼 */
    .voice-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 16px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(245,87,108,0.3);
    }
    
    #voiceBtn {
        background: white;
        color: #f5576c;
        border: none;
        padding: 18px 30px;
        font-size: 1.2rem;
        border-radius: 12px;
        cursor: pointer;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transition: all 0.3s;
        font-weight: bold;
        width: 100%;
        min-height: 60px;
    }
    
    #voiceBtn:hover {
        transform: scale(1.02);
    }
    
    #voiceBtn.recording {
        background: #ff3d00;
        color: white;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(255,61,0,0.7); }
        50% { box-shadow: 0 0 0 15px rgba(255,61,0,0); }
    }
    
    #status {
        color: white;
        text-align: center;
        font-size: 1rem;
        margin-top: 15px;
        min-height: 30px;
    }
    
    #result-box {
        display: none;
        background: white;
        color: #333;
        padding: 20px;
        border-radius: 12px;
        margin-top: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    #result-box.show {
        display: block;
    }
    
    .copy-btn {
        background: #10b981;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
        width: 100%;
        margin-top: 10px;
        min-height: 48px;
    }
    
    .copy-btn:hover {
        background: #059669;
    }
    
    /* AI 답변 영역 */
    .ai-response {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 16px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* 링크 스타일 */
    a {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    /* 카드 */
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    
    /* 탭 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        background-color: #f0f2f6;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* 음성 재생 영역 */
    audio {
        width: 100%;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== 유틸리티 함수 ==========
def create_invidious_player(video_id: str, title: str = "YouTube 영상") -> str:
    """Invidious 광고 없는 플레이어"""
    
    # 안정적인 Invidious 서버들 (2025년 기준)
    servers = [
        ("yewtu.be", "Yewtu.be"),
        ("inv.tux.pizza", "독일"),
        ("invidious.privacyredirect.com", "미국"),
        ("yt.artemislena.eu", "루마니아"),
        ("invidious.fdn.fr", "프랑스")
    ]
    
    main_server = servers[0][0]
    embed_url = f"https://{main_server}/embed/{video_id}?autoplay=0"
    
    server_links = ""
    for domain, name in servers:
        watch_url = f"https://{domain}/watch?v={video_id}"
        server_links += f'<a href="{watch_url}" target="_blank" class="server-btn">🎬 {name}</a>'
    
    return f"""
    <div class="youtube-card">
        <h3>📺 {title}</h3>
        <div class="video-container">
            <iframe 
                src="{embed_url}"
                allowfullscreen
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                loading="lazy"
            ></iframe>
        </div>
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.3);">
            <p style="margin: 0 0 10px 0; font-size: 0.9rem;">✅ 광고 100% 차단 | 다른 서버 선택:</p>
            <div class="server-links">
                {server_links}
                <a href="https://www.youtube.com/watch?v={video_id}" target="_blank" class="server-btn">📱 YouTube 원본</a>
            </div>
        </div>
    </div>
    """

def format_youtube_links(text: str) -> str:
    """텍스트에서 YouTube 링크 찾아서 플레이어로 변환"""
    patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'https?://youtu\.be/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        matches = list(re.finditer(pattern, text))
        for match in reversed(matches):
            video_id = match.group(1)
            player = create_invidious_player(video_id, "추천 영상")
            text = text[:match.start()] + player + text[match.end():]
    
    return text

def add_search_links(text: str) -> str:
    """키워드에 검색 링크 추가"""
    keywords = [
        "재료역학", "열역학", "유체역학", "기계요소설계",
        "SFD", "BMD", "베르누이", "모어원", "좌굴", "엔트로피"
    ]
    
    for keyword in keywords:
        if keyword in text:
            search_url = f"https://yewtu.be/search?q={urllib.parse.quote(keyword + ' 일반기계기사')}"
            pattern = rf'\b({re.escape(keyword)})\b'
            if re.search(pattern, text):
                replacement = f'[\\1 📺]({search_url})'
                text = re.sub(pattern, replacement, text, count=1)
    
    return text

# ========== TTS 기능 ==========
async def text_to_speech_async(text: str, voice: str = "ko-KR-SunHiNeural"):
    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_data = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        audio_data.seek(0)
        return audio_data.getvalue()
    except Exception as e:
        return None

def text_to_speech(text: str, voice: str = "ko-KR-SunHiNeural"):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_bytes = loop.run_until_complete(text_to_speech_async(text, voice))
        loop.close()
        return audio_bytes
    except:
        return None

def clean_text_for_tts(text: str) -> str:
    """TTS용 텍스트 정리"""
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[*_~`#]+', '', text)
    
    emojis = {'✅':'체크','❌':'주의','💡':'팁','📺':'영상','🔥':'중요'}
    for emoji, word in emojis.items():
        text = text.replace(emoji, word)
    
    text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text[:3000] if len(text) > 3000 else text

# ========== 음성 인식 컴포넌트 ==========
def create_voice_input():
    return """
    <div class="voice-container">
        <button id="voiceBtn">
            <span id="micIcon">🎤</span>
            <span id="btnText">음성으로 질문하기</span>
        </button>
        <div id="status">버튼을 누르고 말씀하세요</div>
    </div>
    
    <div id="result-box">
        <div id="finalResult"></div>
        <button class="copy-btn" onclick="copyText()">📋 입력창에 복사</button>
    </div>
    
    <script>
    const voiceBtn = document.getElementById('voiceBtn');
    const btnText = document.getElementById('btnText');
    const micIcon = document.getElementById('micIcon');
    const status = document.getElementById('status');
    const resultBox = document.getElementById('result-box');
    const finalResult = document.getElementById('finalResult');
    let recognizedText = '';
    
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        voiceBtn.disabled = true;
        btnText.textContent = '음성 인식 미지원';
        status.innerHTML = '❌ Chrome/Edge 브라우저를 사용하세요';
    } else {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'ko-KR';
        recognition.continuous = false;
        recognition.interimResults = true;
        
        voiceBtn.addEventListener('click', () => {
            if (voiceBtn.classList.contains('recording')) {
                recognition.stop();
                return;
            }
            
            recognition.start();
            voiceBtn.classList.add('recording');
            btnText.textContent = '듣는 중... (클릭하면 중지)';
            micIcon.textContent = '🔴';
            status.innerHTML = '🎧 말씀하세요...';
            resultBox.classList.remove('show');
        });
        
        recognition.onresult = (event) => {
            let interim = '', final = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    final += transcript;
                } else {
                    interim += transcript;
                }
            }
            
            if (interim) {
                status.innerHTML = '인식 중: "' + interim + '"';
            }
            
            if (final) {
                recognizedText = final;
                status.innerHTML = '✅ 인식 완료!';
                finalResult.textContent = '"' + final + '"';
                resultBox.classList.add('show');
                
                setTimeout(() => fillInput(final), 300);
            }
        };
        
        recognition.onerror = () => {
            voiceBtn.classList.remove('recording');
            btnText.textContent = '음성으로 질문하기';
            micIcon.textContent = '🎤';
            status.innerHTML = '❌ 오류 발생';
        };
        
        recognition.onend = () => {
            voiceBtn.classList.remove('recording');
            btnText.textContent = '음성으로 질문하기';
            micIcon.textContent = '🎤';
        };
    }
    
    function fillInput(text) {
        try {
            const inputs = window.parent.document.querySelectorAll('input[type="text"], textarea');
            for (let input of inputs) {
                if (!input.value || input.placeholder?.includes('질문')) {
                    input.value = text;
                    input.dispatchEvent(new Event('input', {bubbles: true}));
                    input.focus();
                    status.innerHTML = '✅ 입력창에 복사 완료!';
                    return;
                }
            }
        } catch(e) {}
    }
    
    function copyText() {
        if (recognizedText) {
            navigator.clipboard.writeText(recognizedText);
            fillInput(recognizedText);
        }
    }
    </script>
    """

# ========== Gemini 모델 ==========
def get_gemini_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        for priority in ['gemini-2.0-flash-exp', 'gemini-2.0', 'gemini-1.5', 'gemini-pro']:
            for model in models:
                if priority in model.lower():
                    return model
        
        return models[0] if models else None
    except:
        return None

# ========== 세션 초기화 ==========
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = None
if 'model_name' not in st.session_state:
    st.session_state.model_name = None
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'audio_playing' not in st.session_state:
    st.session_state.audio_playing = False
if 'selected_voice' not in st.session_state:
    st.session_state.selected_voice = "ko-KR-SunHiNeural"

# ========== 메인 UI ==========
st.title("⚙️ 일반기계기사 AI 학습 가이드")
st.markdown("""
<div style='text-align: center; color: #666; margin-bottom: 30px;'>
    <p style='font-size: 1.1rem;'>영욱이와 설매의 합격을 응원합니다 🔥</p>
    <p style='font-size: 0.95rem;'>광고 없는 YouTube 강의 + AI 튜터 + 음성 인식</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ========== AI 튜터 ==========
st.header("🤖 AI 튜터에게 질문하기")

# 음성 인식
st.markdown("### 🎤 음성으로 질문")
components.html(create_voice_input(), height=250, scrolling=False)

st.markdown("---")

# 텍스트/이미지 질문
tab1, tab2 = st.tabs(["📝 텍스트 질문", "📸 이미지 질문"])

with tab1:
    with st.form("text_form", clear_on_submit=True):
        query = st.text_input(
            "질문을 입력하세요",
            placeholder="예: 재료역학 공부 순서 알려줘",
            label_visibility="collapsed"
        )
        submit = st.form_submit_button("🔍 질문하기", use_container_width=True)
    
    if submit and query:
        if "GOOGLE_API_KEY" in st.secrets:
            try:
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                
                with st.spinner("🤖 AI가 답변 생성 중..."):
                    model_name = get_gemini_model()
                    
                    if model_name:
                        model = genai.GenerativeModel(model_name)
                        
                        prompt = f"""
다음 질문에 일반기계기사 시험 준비생 관점에서 답변해주세요:

{query}

답변 형식:
1. 핵심 개념 설명
2. 공식/계산 방법 (있다면)
3. 시험 출제 경향
4. 📺 추천 YouTube 영상 (URL 포함 - https://www.youtube.com/watch?v=VIDEO_ID 형식)
5. 검색 키워드 3개
"""
                        
                        response = model.generate_content(prompt)
                        st.session_state.ai_response = response.text
                        st.session_state.model_name = model_name
                        st.session_state.uploaded_image = None
                    else:
                        st.error("❌ 사용 가능한 모델이 없습니다")
            except Exception as e:
                st.error(f"❌ 오류: {e}")
        else:
            st.error("⚠️ API 키를 설정하세요 (Streamlit Secrets)")

with tab2:
    uploaded_file = st.file_uploader(
        "문제 사진/도면 업로드",
        type=['jpg', 'jpeg', 'png'],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이미지", use_column_width=True)
        
        if st.button("🗑️ 삭제", use_container_width=True):
            st.session_state.uploaded_image = None
            st.rerun()
    
    with st.form("image_form", clear_on_submit=True):
        image_query = st.text_input(
            "질문 (선택)",
            placeholder="예: 이 문제 풀이 설명해줘",
            label_visibility="collapsed"
        )
        image_submit = st.form_submit_button("🔍 분석하기", use_container_width=True)
    
    if image_submit and uploaded_file:
        if "GOOGLE_API_KEY" in st.secrets:
            try:
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                
                with st.spinner("🖼️ 이미지 분석 중..."):
                    model_name = get_gemini_model()
                    
                    if model_name:
                        model = genai.GenerativeModel(model_name)
                        image = Image.open(uploaded_file)
                        
                        prompt = f"""
이미지를 분석하고 {f'다음 질문에 답하세요: {image_query}' if image_query else '설명하세요'}

답변 형식:
1. 이미지 내용
2. 문제라면 단계별 풀이
3. 관련 개념/공식
4. 📺 추천 YouTube 영상 (URL 포함)
"""
                        
                        response = model.generate_content([prompt, image])
                        st.session_state.ai_response = response.text
                        st.session_state.model_name = model_name
                        st.session_state.uploaded_image = image
                    else:
                        st.error("❌ 모델 없음")
            except Exception as e:
                st.error(f"❌ 오류: {e}")
        else:
            st.error("⚠️ API 키 필요")

# AI 답변 표시
if st.session_state.ai_response:
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 2])
    
    with col1:
        if st.button("🗑️ 삭제", key="del", use_container_width=True):
            st.session_state.ai_response = None
            st.session_state.model_name = None
            st.session_state.uploaded_image = None
            st.session_state.audio_playing = False
            st.rerun()
    
    with col2:
        voice = st.selectbox(
            "목소리",
            [("ko-KR-SunHiNeural", "👩 여자"), ("ko-KR-InJoonNeural", "👨 남자")],
            format_func=lambda x: x[1],
            key="voice"
        )
        st.session_state.selected_voice = voice[0]
    
    with col3:
        if st.button("🔊 음성 듣기", key="tts", use_container_width=True):
            with st.spinner("음성 생성 중..."):
                clean = clean_text_for_tts(st.session_state.ai_response)
                audio = text_to_speech(clean, st.session_state.selected_voice)
                
                if audio:
                    st.session_state.audio_playing = True
                    st.success("✅ 준비 완료!")
    
    if st.session_state.audio_playing:
        st.markdown("### 🎧 음성 재생")
        
        clean = clean_text_for_tts(st.session_state.ai_response)
        audio = text_to_speech(clean, st.session_state.selected_voice)
        
        if audio:
            audio_b64 = base64.b64encode(audio).decode()
            st.markdown(f"""
            <audio controls autoplay style="width: 100%;">
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)
            
            if st.button("⏹️ 정지", use_container_width=True):
                st.session_state.audio_playing = False
                st.rerun()
        
        st.markdown("---")
    
    if st.session_state.uploaded_image:
        st.image(st.session_state.uploaded_image, caption="분석한 이미지", use_column_width=True)
    
    # 답변 표시
    response_text = st.session_state.ai_response
    response_text = format_youtube_links(response_text)
    response_text = add_search_links(response_text)
    
    st.markdown("### 💡 AI 답변")
    st.markdown(f'<div class="ai-response">{response_text}</div>', unsafe_allow_html=True)

st.divider()

# ========== 추천 채널 ==========
st.header("📺 추천 YouTube 채널 (광고 없음)")

col1, col2, col3 = st.columns(3)

channels = [
    ("기계달인", "전과목 강의"),
    ("에듀윌", "핵심 요약"),
    ("메가파이", "자격증 꿀팁"),
    ("한솔아카데미", "기출 해설"),
    ("공밀레", "개념 이해"),
    ("Learn Engineering", "영문/애니메이션")
]

for i, (name, desc) in enumerate(channels):
    url = f"https://yewtu.be/search?q={urllib.parse.quote(name + ' 일반기계기사')}"
    
    with [col1, col2, col3][i % 3]:
        st.markdown(f"""
        <div class="info-card">
            <h4 style="margin: 0 0 5px 0;">👉 <a href="{url}" target="_blank">{name}</a></h4>
            <p style="margin: 0; color: #666; font-size: 0.9rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ========== 과목별 강의 ==========
st.header("🔍 과목별 핵심 강의")

subjects = {
    "1️⃣ 재료역학": [
        ("기초 강의", "재료역학+기초"),
        ("SFD/BMD", "SFD+BMD"),
        ("보의 처짐", "재료역학+처짐"),
        ("모어원", "모어원"),
        ("좌굴", "좌굴+공식")
    ],
    "2️⃣ 열역학": [
        ("열역학 법칙", "열역학+법칙"),
        ("사이클", "열역학+사이클"),
        ("엔트로피", "엔트로피"),
        ("냉동 사이클", "냉동사이클")
    ],
    "3️⃣ 유체역학": [
        ("유체 성질", "유체역학+점성"),
        ("베르누이", "베르누이+방정식"),
        ("관로 마찰", "달시+바이스바흐"),
        ("운동량", "유체역학+운동량")
    ],
    "4️⃣ 기계요소설계": [
        ("기어/베어링", "기어+베어링"),
        ("나사/볼트", "나사+효율"),
        ("파손 이론", "파손이론"),
        ("축/커플링", "축+설계")
    ]
}

for subject, topics in subjects.items():
    with st.expander(subject):
        for topic, keyword in topics:
            url = f"https://yewtu.be/search?q={urllib.parse.quote(keyword + ' 일반기계기사')}"
            st.markdown(f"- [{topic} 📺]({url})")

st.divider()

# ========== 실기 대비 ==========
st.header("🎯 실기 대비")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="info-card">
        <h3>📝 필답형</h3>
        <p><a href="https://yewtu.be/search?q=일반기계기사+필답형+요약" target="_blank">📖 요약 정리</a></p>
        <p><a href="https://yewtu.be/search?q=일반기계기사+필답형+기출" target="_blank">✍️ 기출 풀이</a></p>
        <p><a href="https://yewtu.be/search?q=일반기계기사+필답형+공식" target="_blank">🎯 공식 정리</a></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h3>💻 작업형</h3>
        <p><a href="https://yewtu.be/search?q=일반기계기사+인벤터" target="_blank">🖱️ 인벤터 기초</a></p>
        <p><a href="https://yewtu.be/search?q=일반기계기사+투상" target="_blank">📐 투상 연습</a></p>
        <p><a href="https://yewtu.be/search?q=일반기계기사+거칠기+공차" target="_blank">📏 거칠기/공차</a></p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ========== 푸터 ==========
st.markdown("""
<div style='text-align: center; color: #666; padding: 40px 20px;'>
    <h2 style='color: #667eea; margin-bottom: 20px;'>🔥 일반기계기사 합격을 응원합니다! 🔥</h2>
    <p style='font-size: 1.1rem; margin: 15px 0;'>
        💡 AI 튜터에게 🎤 음성으로 질문하고 🔊 음성으로 답변을 들어보세요!
    </p>
    <p style='font-size: 1rem; color: #10b981; font-weight: bold; margin: 15px 0;'>
        ✅ 모든 유튜브 영상 광고 100% 차단! (Invidious 제공)
    </p>
    <p style='font-size: 0.9rem; margin: 30px 0 10px 0;'>
        Made with ❤️ by AI<br>
        Powered by Gemini AI + Edge TTS + Invidious + Web Speech API
    </p>
    <p style='font-size: 0.8rem; color: #999;'>
        Invidious는 AGPL-3.0 오픈소스 프로젝트입니다
    </p>
</div>
""", unsafe_allow_html=True)
