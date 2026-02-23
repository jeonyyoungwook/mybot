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
from pathlib import Path
import tempfile

# ========== 1. 페이지 기본 설정 (모바일 최적화) ==========
st.set_page_config(
    page_title="일반기계기사 학습 가이드",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"  # 모바일에서 사이드바 자동 닫기
)

# ========== 🎨 모바일 최적화 CSS (완전 새로 작성) ==========
st.markdown("""
<style>
    /* ========== 모바일 뷰포트 완벽 대응 ========== */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        height: 100%;
        min-height: 100vh;
        min-height: -webkit-fill-available;
        min-height: 100dvh; /* 2025년 표준 */
        overflow-x: hidden;
        margin: 0;
        padding: 0;
    }
    
    /* ========== Streamlit 기본 패딩 제거 (모바일 공간 확보) ========== */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    /* ========== 모바일 텍스트 크기 최적화 ========== */
    @media (max-width: 768px) {
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        p, li, div { font-size: 0.95rem !important; line-height: 1.6 !important; }
        
        /* 버튼 터치 영역 확대 */
        button, [data-testid="stButton"] button {
            min-height: 48px !important;
            padding: 12px 20px !important;
            font-size: 1rem !important;
        }
        
        /* 입력창 터치 최적화 */
        input, textarea {
            font-size: 16px !important; /* iOS 자동 줌 방지 */
            min-height: 48px !important;
        }
        
        /* 컬럼 모바일 대응 */
        [data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: 1rem !important;
        }
    }
    
    /* ========== 이미지 반응형 처리 ========== */
    img {
        max-width: 100% !important;
        height: auto !important;
        border-radius: 8px;
    }
    
    /* ========== 탭 모바일 최적화 ========== */
    [data-testid="stTabs"] {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    /* ========== expander 터치 영역 확대 ========== */
    [data-testid="stExpander"] summary {
        min-height: 48px !important;
        padding: 12px !important;
        font-size: 1rem !important;
    }
    
    /* ========== 링크 터치 최적화 ========== */
    a {
        padding: 8px 4px !important;
        display: inline-block;
        min-height: 44px;
        line-height: 28px;
    }
    
    /* ========== 음성 버튼 모바일 최적화 ========== */
    .voice-container {
        position: relative;
        width: 100%;
        max-width: 100%;
        overflow: hidden;
    }
    
    @media (max-width: 768px) {
        .voice-container {
            flex-direction: column;
            gap: 10px !important;
        }
        
        #voiceBtn {
            width: 100% !important;
            min-height: 56px !important;
            font-size: 1.1rem !important;
        }
        
        #status {
            text-align: center;
            width: 100%;
        }
        
        #result-box {
            font-size: 0.95rem !important;
            padding: 15px !important;
        }
    }
    
    /* ========== 아이폰 노치/홈바 대응 ========== */
    @supports (padding: max(0px)) {
        .main .block-container {
            padding-top: max(2rem, env(safe-area-inset-top)) !important;
            padding-bottom: max(2rem, env(safe-area-inset-bottom)) !important;
            padding-left: max(1rem, env(safe-area-inset-left)) !important;
            padding-right: max(1rem, env(safe-area-inset-right)) !important;
        }
    }
    
    /* ========== 오디오 플레이어 반응형 ========== */
    audio {
        width: 100% !important;
        max-width: 100% !important;
        min-height: 48px;
    }
    
    /* ========== 스크롤바 디자인 (모바일 친화적) ========== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(0,0,0,0.2);
        border-radius: 4px;
    }
    
    /* ========== 로딩 스피너 중앙 정렬 ========== */
    [data-testid="stSpinner"] {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 9999;
    }
</style>
""", unsafe_allow_html=True)

# ========== 🎤 TTS 기능 (음성 출력) ==========
async def text_to_speech_async(text, voice="ko-KR-SunHiNeural"):
    """Edge TTS 음성 생성"""
    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_data = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        audio_data.seek(0)
        return audio_data.getvalue()
    except Exception as e:
        st.error(f"음성 생성 실패: {e}")
        return None

def text_to_speech(text, voice="ko-KR-SunHiNeural"):
    """동기 래퍼"""
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
    """HTML5 오디오 플레이어"""
    audio_base64 = base64.b64encode(audio_bytes).decode()
    return f"""
    <audio controls autoplay style="width: 100%; max-width: 100%; min-height: 48px; border-radius: 8px;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        브라우저가 오디오를 지원하지 않습니다.
    </audio>
    """

def clean_text_for_tts(text):
    """TTS용 텍스트 정제"""
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[*_~`]+', '', text)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    
    emoji_map = {
        '✅': '체크', '❌': '주의', '⚠️': '경고', '💡': '팁',
        '📺': '영상', '🔍': '검색', '📝': '노트', '🎯': '목표',
        '🔥': '중요', '📚': '학습', '⚙️': '기계', '🎬': '동영상'
    }
    
    for emoji, desc in emoji_map.items():
        text = text.replace(emoji, f' {desc} ')
    
    text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
    text = re.sub(r'\s+', ' ', text)
    
    if len(text) > 3000:
        text = text[:3000] + "... 이하 생략됩니다."
    
    return text.strip()

# ========== 🎤 음성 인식 컴포넌트 (완전 재작성 - 모바일 최적화) ==========
def create_voice_input_component():
    """모바일 완벽 대응 음성 인식"""
    return """
    <style>
        .voice-container {
            display: flex;
            flex-direction: column;
            align-items: stretch;
            gap: 12px;
            padding: 20px 15px;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            border-radius: 16px;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        #voiceBtn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 18px 24px;
            font-size: 1.1rem;
            border-radius: 12px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            min-height: 56px;
            -webkit-tap-highlight-color: transparent;
        }
        
        #voiceBtn:active {
            transform: scale(0.98);
        }
        
        #voiceBtn.recording {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(245, 87, 108, 0.7); }
            70% { box-shadow: 0 0 0 15px rgba(245, 87, 108, 0); }
            100% { box-shadow: 0 0 0 0 rgba(245, 87, 108, 0); }
        }
        
        #voiceBtn:disabled {
            background: #ccc;
            cursor: not-allowed;
            box-shadow: none;
        }
        
        #status {
            font-size: 0.95rem;
            color: #666;
            text-align: center;
            padding: 8px;
            min-height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        #result-box {
            display: none;
            background: white;
            padding: 15px;
            border-radius: 12px;
            border: 2px solid #667eea;
            margin-top: 5px;
            font-size: 1rem;
            word-break: keep-all;
            line-height: 1.6;
        }
        
        #result-box.show {
            display: block;
        }
        
        .copy-btn {
            background: #10b981;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 0.95rem;
            margin-top: 10px;
            width: 100%;
            min-height: 48px;
            font-weight: bold;
            -webkit-tap-highlight-color: transparent;
        }
        
        .copy-btn:active {
            background: #059669;
            transform: scale(0.98);
        }
        
        @media (max-width: 768px) {
            .voice-container { padding: 15px; }
            #voiceBtn { font-size: 1rem; padding: 16px 20px; }
            #status { font-size: 0.9rem; }
            #result-box { font-size: 0.95rem; padding: 12px; }
        }
    </style>
    
    <div class="voice-container">
        <button id="voiceBtn">
            <span id="micIcon">🎤</span>
            <span id="btnText">음성으로 질문하기</span>
        </button>
        <div id="status">버튼을 클릭하고 말씀해주세요</div>
    </div>
    
    <div id="result-box">
        <div id="finalResult"></div>
        <button class="copy-btn" onclick="copyAndFill()">📋 입력창에 복사</button>
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
        micIcon.textContent = '❌';
        status.innerHTML = '<span style="color: #ef4444;">Chrome/Edge/삼성 인터넷 브라우저를 사용해주세요</span>';
    } else {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'ko-KR';
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;

        voiceBtn.addEventListener('click', () => {
            if (voiceBtn.classList.contains('recording')) {
                recognition.stop();
                return;
            }
            
            try {
                recognition.start();
                voiceBtn.classList.add('recording');
                btnText.textContent = '듣는 중... (클릭하면 중지)';
                micIcon.textContent = '🔴';
                status.innerHTML = '<span style="color: #f5576c; font-weight: bold;">🎧 말씀해주세요...</span>';
                resultBox.classList.remove('show');
            } catch (e) {
                console.error('음성 인식 시작 실패:', e);
            }
        });

        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            if (interimTranscript) {
                status.innerHTML = '<span style="color: #667eea;">인식 중: "' + interimTranscript + '"</span>';
            }
            
            if (finalTranscript) {
                recognizedText = finalTranscript;
                status.innerHTML = '<span style="color: #10b981; font-weight: bold;">✅ 인식 완료!</span>';
                finalResult.textContent = '"' + finalTranscript + '"';
                resultBox.classList.add('show');
                
                setTimeout(() => fillInputField(finalTranscript), 300);
            }
        };

        recognition.onerror = (event) => {
            console.error('음성 인식 오류:', event.error);
            voiceBtn.classList.remove('recording');
            btnText.textContent = '음성으로 질문하기';
            micIcon.textContent = '🎤';
            
            const errorMessages = {
                'no-speech': '⚠️ 음성이 감지되지 않았어요',
                'not-allowed': '❌ 마이크 권한을 허용해주세요',
                'network': '❌ 네트워크 오류',
                'aborted': 'ℹ️ 음성 인식이 중단되었습니다'
            };
            
            status.innerHTML = '<span style="color: #ef4444;">' + 
                (errorMessages[event.error] || '❌ 오류: ' + event.error) + '</span>';
        };

        recognition.onend = () => {
            voiceBtn.classList.remove('recording');
            btnText.textContent = '음성으로 질문하기';
            micIcon.textContent = '🎤';
        };
    }
    
    function fillInputField(text) {
        try {
            const parentDoc = window.parent.document;
            const inputs = parentDoc.querySelectorAll('input[type="text"], textarea');
            
            for (let input of inputs) {
                if (!input.value || input.placeholder?.includes('질문') || input.placeholder?.includes('예:')) {
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    ).set;
                    nativeInputValueSetter.call(input, text);
                    
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    input.focus();
                    
                    status.innerHTML = '<span style="color: #10b981; font-weight: bold;">✅ 입력창에 복사 완료!</span>';
                    return true;
                }
            }
        } catch (e) {
            console.log('자동 입력 실패:', e);
        }
        return false;
    }
    
    function copyAndFill() {
        if (recognizedText) {
            navigator.clipboard.writeText(recognizedText).then(() => {
                status.innerHTML = '<span style="color: #10b981; font-weight: bold;">📋 복사됨! 붙여넣기(Ctrl+V)하세요</span>';
            }).catch(() => {
                fillInputField(recognizedText);
            });
            
            fillInputField(recognizedText);
        }
    }
    </script>
    """

# ========== 유틸리티 함수들 ==========
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
<div style="border: 2px solid #ff0000; border-radius: 12px; padding: 15px; margin: 15px 0; background-color: #fff5f5;">
    <h4 style="color: #ff0000; margin-top: 0;">📺 추천 영상</h4>
    <a href="{full_url}" target="_blank" rel="noopener noreferrer">
        <img src="https://img.youtube.com/vi/{video_id}/mqdefault.jpg" 
             style="width: 100%; max-width: 100%; height: auto; border-radius: 8px; margin: 10px 0;">
    </a>
    <a href="{full_url}" target="_blank" rel="noopener noreferrer" 
       style="display: block; background-color: #ff0000; color: white; padding: 14px 20px; 
              border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center; 
              min-height: 48px; line-height: 20px;">
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
        
        priority_order = ['gemini-3', 'gemini-2.5', 'gemini-2.0', 'gemini-1.5', 'gemini-pro']
        
        for priority in priority_order:
            for model_name in available_models:
                if priority in model_name.lower():
                    return model_name
        
        return available_models[0] if available_models else None
        
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

# ========== 세션 스테이트 초기화 ==========
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

# ========== 페이지 제목 ==========
st.title("⚙️ 일반기계기사 독학 가이드 🎬")
st.markdown("""
영욱이와 설매의 합격을 기원합니다.  
유튜브 무료 강의와 핵심 기출 풀이 영상 모음입니다.
""")

st.divider()

# ========== AI 튜터 섹션 ==========
with st.container():
    st.markdown("### 🤖 AI 튜터에게 질문하기")
    st.caption("궁금한 개념을 **🎤 음성, 📝 텍스트 또는 📸 이미지**로 질문하세요!")
    
    # 🎤 음성 입력
    st.markdown("#### 🎤 음성으로 질문하기")
    components.html(create_voice_input_component(), height=200, scrolling=False)
    
    st.markdown("---")

    tab1, tab2 = st.tabs(["📝 텍스트 질문", "📸 이미지 질문"])
    
    # 텍스트 질문
    with tab1:
        with st.form(key="text_question_form", clear_on_submit=True):
            query = st.text_input(
                "질문 입력", 
                placeholder="예: 재료역학 공부 순서 알려줘",
                label_visibility="collapsed"
            )
            
            text_submit_btn = st.form_submit_button("🔍 질문하기", use_container_width=True)

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
1. 핵심 개념 설명
2. 공식이나 계산 방법 (있다면)
3. 시험 출제 경향
4. 📺 추천 채널 (채널명, 특징, 추천 영상)
5. 유튜브 검색 키워드 3개
"""
                            
                            response = model.generate_content(enhanced_query)
                            
                            st.session_state.ai_response = response.text
                            st.session_state.model_name = model_name
                            st.session_state.uploaded_image = None
                        else:
                            st.error("❌ 사용 가능한 Gemini 모델을 찾을 수 없습니다.")
                else:
                    st.error("⚠️ API 키가 설정되지 않았습니다.")
                    
            except Exception as e:
                st.error(f"❌ 에러 발생: {e}")
                if "429" in str(e):
                    st.warning("⏰ API 사용량 제한. 잠시 후 다시 시도하세요.")
    
    # 이미지 질문
    with tab2:
        st.markdown("📌 **문제 사진, 도면, 공식 스크린샷** 등을 업로드하세요!")
        
        uploaded_file = st.file_uploader(
            "이미지 업로드", 
            type=['jpg', 'jpeg', 'png'],
            help="문제 사진이나 스크린샷을 올려주세요",
            key=f"uploader_{st.session_state.uploader_key}",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="업로드된 이미지", use_column_width=True)
            
            if st.button("🖼️ 이미지 삭제", key="delete_image", use_container_width=True):
                st.session_state.uploader_key += 1
                st.session_state.uploaded_image = None
                st.rerun()
        
        with st.form(key="image_question_form", clear_on_submit=True):
            image_query = st.text_input(
                "이미지에 대한 질문", 
                placeholder="예: 이 문제 풀이 과정 설명해줘",
                label_visibility="collapsed"
            )
            
            image_submit_btn = st.form_submit_button("🔍 이미지 질문", use_container_width=True)
        
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
                            
                            prompt = f"""
이미지를 분석하고 {'다음 질문에 답해주세요: ' + image_query if image_query else '설명해주세요'}

답변 형식:
1. 이미지 내용 분석
2. 문제라면 단계별 풀이
3. 관련 개념 및 공식
4. 📺 추천 영상
5. 검색 키워드
"""
                            
                            response = model.generate_content([prompt, image])
                            
                            st.session_state.ai_response = response.text
                            st.session_state.model_name = model_name
                            st.session_state.uploaded_image = image
                        else:
                            st.error("❌ 모델을 찾을 수 없습니다.")
                else:
                    st.error("⚠️ API 키가 설정되지 않았습니다.")
                    
            except Exception as e:
                st.error(f"❌ 에러 발생: {e}")

    # ✅ 답변 표시 + TTS
    st.markdown("")
    if st.session_state.ai_response:
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
                "🎙️ 목소리",
                options=[
                    ("ko-KR-SunHiNeural", "👩 여자"),
                    ("ko-KR-InJoonNeural", "👨 남자")
                ],
                format_func=lambda x: x[1],
                key="voice_selector"
            )
            st.session_state.selected_voice = voice_option[0]
        
        with col_tts:
            if st.button("🔊 음성으로 듣기", key="tts_button", use_container_width=True):
                with st.spinner("🎤 음성 생성 중..."):
                    clean_text = clean_text_for_tts(st.session_state.ai_response)
                    audio_bytes = text_to_speech(clean_text, st.session_state.selected_voice)
                    
                    if audio_bytes:
                        st.session_state.audio_playing = True
                        st.success("✅ 음성 준비 완료!")
        
        # 오디오 플레이어
        if st.session_state.audio_playing:
            st.markdown("---")
            st.markdown("### 🎧 음성 재생")
            
            clean_text = clean_text_for_tts(st.session_state.ai_response)
            audio_bytes = text_to_speech(clean_text, st.session_state.selected_voice)
            
            if audio_bytes:
                audio_html = create_audio_player(audio_bytes)
                st.markdown(audio_html, unsafe_allow_html=True)
                
                if st.button("⏹️ 음성 정지", key="stop_audio", use_container_width=True):
                    st.session_state.audio_playing = False
                    st.rerun()
            
            st.markdown("---")
        
        # 이미지 표시
        if st.session_state.uploaded_image:
            st.image(st.session_state.uploaded_image, caption="질문한 이미지", use_column_width=True)
        
        # AI 답변
        response_text = st.session_state.ai_response
        response_text = format_youtube_links(response_text)
        response_text = add_youtube_search_links(response_text)
        response_text = make_links_clickable(response_text)
        
        st.markdown("---")
        st.markdown("### 💡 AI 답변")
        st.markdown(response_text, unsafe_allow_html=True)
        
        # 모델 정보
        display_name = get_model_display_name(st.session_state.model_name)
        
        with st.expander("🤖 AI 모델 정보", expanded=False):
            st.markdown(f"""
**모델:** {display_name}  
**ID:** `{st.session_state.model_name}`

**지원 기능:**
- ✅ 텍스트 생성
- ✅ 이미지 분석
- ✅ 음성 출력 (TTS)
- ✅ 음성 입력 (STT)
""")

st.divider()

# ========== 유튜브 채널 추천 ==========
st.header("📺 1. 추천 유튜브 채널")

col_ch1, col_ch2, col_ch3 = st.columns(3)

with col_ch1:
    st.markdown("""
👉 [**기계달인**](https://www.youtube.com/results?search_query=기계달인+일반기계기사)  
(전과목 강의)

👉 [**에듀윌**](https://www.youtube.com/results?search_query=에듀윌+일반기계기사)  
(핵심 요약)
""")

with col_ch2:
    st.markdown("""
👉 [**메가파이**](https://www.youtube.com/results?search_query=메가파이+일반기계기사)  
(자격증 꿀팁)

👉 [**한솔아카데미**](https://www.youtube.com/results?search_query=한솔아카데미+일반기계기사)  
(기출 해설)
""")

with col_ch3:
    st.markdown("""
👉 [**공밀레**](https://www.youtube.com/results?search_query=공밀레+재료역학)  
(개념 이해)

👉 [**Learn Engineering**](https://www.youtube.com/results?search_query=Learn+Engineering)  
(영문/애니메이션)
""")

st.markdown("")

# ========== 과목별 강의 ==========
st.header("🔍 2. 과목별 핵심 강의")

with st.expander("1️⃣ 재료역학 - 펼쳐보기", expanded=False):
    st.markdown("""
- [🧱 기초 강의](https://www.youtube.com/results?search_query=재료역학+기초+강의)
- [📉 SFD/BMD 그리기](https://www.youtube.com/results?search_query=SFD+BMD+그리는법)
- [➰ 보의 처짐](https://www.youtube.com/results?search_query=재료역학+보의+처짐)
- [🌀 모어원](https://www.youtube.com/results?search_query=재료역학+모어원)
- [🏛️ 좌굴 공식](https://www.youtube.com/results?search_query=재료역학+좌굴+공식)
- [📝 기출문제](https://www.youtube.com/results?search_query=일반기계기사+재료역학+기출문제)
""")

with st.expander("2️⃣ 기계열역학 - 펼쳐보기"):
    st.markdown("""
- [🔥 열역학 법칙](https://www.youtube.com/results?search_query=열역학+법칙+설명)
- [🔄 사이클 정리](https://www.youtube.com/results?search_query=열역학+사이클+정리)
- [🌡️ 엔트로피](https://www.youtube.com/results?search_query=열역학+엔트로피)
- [💨 냉동 사이클](https://www.youtube.com/results?search_query=일반기계기사+냉동사이클)
- [📝 기출문제](https://www.youtube.com/results?search_query=일반기계기사+열역학+기출)
""")

with st.expander("3️⃣ 기계유체역학 - 펼쳐보기"):
    st.markdown("""
- [💧 유체 성질](https://www.youtube.com/results?search_query=유체역학+점성계수)
- [🌪️ 베르누이 방정식](https://www.youtube.com/results?search_query=베르누이+방정식+문제풀이)
- [📏 관로 마찰](https://www.youtube.com/results?search_query=달시+바이스바흐+공식)
- [⚡ 운동량 방정식](https://www.youtube.com/results?search_query=유체역학+운동량방정식)
- [📝 기출문제](https://www.youtube.com/results?search_query=일반기계기사+유체역학+기출)
""")

with st.expander("4️⃣ 기계요소설계 - 펼쳐보기"):
    st.markdown("""
- [⚙️ 기어/베어링](https://www.youtube.com/results?search_query=기계요소설계+기어+베어링)
- [🔩 나사/볼트](https://www.youtube.com/results?search_query=기계요소설계+나사+효율)
- [🛡️ 파손 이론](https://www.youtube.com/results?search_query=기계설계+파손이론)
- [🔗 축/커플링](https://www.youtube.com/results?search_query=기계요소설계+축+설계)
- [📝 기출문제](https://www.youtube.com/results?search_query=일반기계기사+기계요소설계+기출)
""")

st.markdown("")

# ========== 실기 대비 ==========
st.header("🎯 3. 실기 대비")

col_prac1, col_prac2 = st.columns(2)

with col_prac1:
    st.subheader("📝 필답형")
    st.markdown("""
- [📖 요약 정리](https://www.youtube.com/results?search_query=일반기계기사+필답형+요약)
- [✍️ 기출 풀이](https://www.youtube.com/results?search_query=일반기계기사+필답형+기출)
- [🎯 공식 정리](https://www.youtube.com/results?search_query=일반기계기사+필답형+공식)
""")

with col_prac2:
    st.subheader("💻 작업형")
    st.markdown("""
- [🖱️ 인벤터 기초](https://www.youtube.com/results?search_query=일반기계기사+인벤터+기초)
- [📐 투상 연습](https://www.youtube.com/results?search_query=일반기계기사+투상+연습)
- [📏 거칠기/공차](https://www.youtube.com/results?search_query=일반기계기사+거칠기+기하공차)
- [⚡ 기출 실습](https://www.youtube.com/results?search_query=일반기계기사+작업형+기출)
""")

st.divider()

# ========== 학습 팁 ==========
st.header("📚 4. 학습 팁")

with st.expander("💡 효율적인 학습 방법", expanded=False):
    st.markdown("""
### 📌 필기 전략
1. **과목별 배점**: 과목당 40점 이상, 전체 60점 이상
2. **학습 순서**: 재료역학 → 열역학 → 유체역학 → 기계요소설계
3. **기출 중심**: 최근 10개년 3회독 이상
4. **과락 방지** 최우선

### 📌 실기 전략
1. **필답형**: 공식 암기 + 단위 환산
2. **작업형**: 인벤터 20시간 이상
3. **시간 배분**: 필답 40분, 작업 80분
4. **기하공차/거칠기** 실전 연습
""")

with st.expander("📖 추천 자료", expanded=False):
    st.markdown("""
### 📚 교재
- SD에듀 / 예문사 / 성안당 기출문제집

### 🌐 사이트
- [큐넷](https://www.q-net.or.kr) - 시험 접수
- [기계기술사 카페](https://cafe.naver.com/mechanicalengineer) - 커뮤니티
- [공학용 계산기](https://www.youtube.com/results?search_query=공학용계산기+사용법)
""")

st.divider()

# ========== 푸터 ==========
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px 10px;'>
    <p style='font-size: 1.1rem; font-weight: bold;'>🔥 일반기계기사 합격을 응원합니다! 🔥</p>
    <p style='font-size: 0.9rem; margin-top: 10px;'>
        💡 TIP: AI 튜터에게 🎤 음성으로 질문하고 🔊 음성으로 답변을 들어보세요!
    </p>
    <p style='font-size: 0.8rem; margin-top: 15px; color: #999;'>
        Made with ❤️ | Powered by Gemini AI + Edge TTS + Web Speech API
    </p>
</div>
""", unsafe_allow_html=True)
