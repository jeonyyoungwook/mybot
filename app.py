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
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 1200px;
    }
    
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
    
    .youtube-thumbnail {
        width: 100%;
        border-radius: 12px;
        margin: 15px 0;
        cursor: pointer;
        transition: transform 0.3s;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    .youtube-thumbnail:hover {
        transform: scale(1.02);
    }
    
    .play-button {
        display: block;
        background: white;
        color: #667eea;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        text-decoration: none;
        margin: 15px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transition: all 0.3s;
    }
    
    .play-button:hover {
        background: #f0f2f6;
        color: #667eea;
        text-decoration: none;
        transform: translateY(-2px);
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
        font-size: 0.9rem;
    }
    
    .server-btn:hover {
        background: rgba(255,255,255,0.3);
        transform: translateY(-2px);
        color: white;
        text-decoration: none;
    }
    
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
        font-weight: 500;
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
    
    #finalResult {
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 15px;
        padding: 15px;
        background: #f0f2f6;
        border-radius: 8px;
        border-left: 4px solid #667eea;
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
        font-size: 1rem;
        transition: all 0.3s;
    }
    
    .copy-btn:hover {
        background: #059669;
        transform: scale(1.02);
    }
    
    .ai-response {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 16px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    a {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    
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
    
    audio {
        width: 100%;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== 유틸리티 함수 ==========
def create_youtube_player(video_id: str, title: str = "YouTube 영상") -> str:
    """안전한 썸네일 + 링크 방식"""
    
    # 안정적인 Invidious 서버들
    servers = [
        ("inv.nadeko.net", "🇯🇵 일본"),
        ("iv.nboeck.de", "🇩🇪 독일"),
        ("inv.tux.pizza", "🇩🇪 독일2"),
        ("yt.artemislena.eu", "🇷🇴 루마니아"),
        ("invidious.privacyredirect.com", "🇺🇸 미국")
    ]
    
    thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    main_server = servers[0][0]
    main_url = f"https://{main_server}/watch?v={video_id}"
    
    server_links = ""
    for domain, name in servers:
        watch_url = f"https://{domain}/watch?v={video_id}"
        server_links += f'<a href="{watch_url}" target="_blank" class="server-btn">{name}</a>'
    
    return f"""
    <div class="youtube-card">
        <h3>📺 {title}</h3>
        
        <a href="{main_url}" target="_blank">
            <img src="{thumbnail}" class="youtube-thumbnail" alt="{title}">
        </a>
        
        <a href="{main_url}" target="_blank" class="play-button">
            ▶️ {main_server}에서 보기 (광고 없음)
        </a>
        
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.3);">
            <p style="margin: 0 0 10px 0; font-size: 0.9rem;">다른 서버 선택:</p>
            <div class="server-links">
                {server_links}
                <a href="https://www.youtube.com/watch?v={video_id}" target="_blank" class="server-btn">📱 YouTube</a>
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
            player = create_youtube_player(video_id, "추천 영상")
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
            search_url = f"https://inv.nadeko.net/search?q={urllib.parse.quote(keyword + ' 일반기계기사')}"
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
    except:
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

# ========== 음성 인식 컴포넌트 (완전히 새로 만듦) ==========
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
        <button class="copy-btn" onclick="copyAndPaste()">📋 복사 후 붙여넣기</button>
    </div>
    
    <script>
    (function() {
        const voiceBtn = document.getElementById('voiceBtn');
        const btnText = document.getElementById('btnText');
        const micIcon = document.getElementById('micIcon');
        const status = document.getElementById('status');
        const resultBox = document.getElementById('result-box');
        const finalResult = document.getElementById('finalResult');
        
        let recognizedText = '';
        let isRecording = false;
        
        // 음성 인식 지원 확인
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            voiceBtn.disabled = true;
            btnText.textContent = '음성 인식 미지원';
            micIcon.textContent = '❌';
            status.innerHTML = '❌ Chrome, Edge, 삼성 인터넷 브라우저를 사용하세요';
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'ko-KR';
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;
        
        // 녹음 시작/중지
        voiceBtn.addEventListener('click', function() {
            if (isRecording) {
                recognition.stop();
                isRecording = false;
                voiceBtn.classList.remove('recording');
                btnText.textContent = '음성으로 질문하기';
                micIcon.textContent = '🎤';
            } else {
                try {
                    recognition.start();
                    isRecording = true;
                    voiceBtn.classList.add('recording');
                    btnText.textContent = '듣는 중... (클릭하면 중지)';
                    micIcon.textContent = '🔴';
                    status.innerHTML = '🎧 말씀하세요...';
                    resultBox.classList.remove('show');
                } catch(e) {
                    console.error('음성 인식 시작 실패:', e);
                    status.innerHTML = '❌ 음성 인식 시작 실패. 다시 시도하세요.';
                }
            }
        });
        
        // 음성 인식 결과
        recognition.onresult = function(event) {
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
                status.innerHTML = '<span style="color: #fff;">인식 중: "' + interimTranscript + '"</span>';
            }
            
            if (finalTranscript) {
                recognizedText = finalTranscript.trim();
                status.innerHTML = '<span style="color: #fff; font-weight: bold;">✅ 인식 완료!</span>';
                finalResult.textContent = '"' + recognizedText + '"';
                resultBox.classList.add('show');
                
                // 자동으로 입력창에 넣기 시도
                setTimeout(function() {
                    autoFillInput(recognizedText);
                }, 500);
            }
        };
        
        // 에러 처리
        recognition.onerror = function(event) {
            console.error('음성 인식 오류:', event.error);
            isRecording = false;
            voiceBtn.classList.remove('recording');
            btnText.textContent = '음성으로 질문하기';
            micIcon.textContent = '🎤';
            
            const errorMessages = {
                'no-speech': '⚠️ 음성이 감지되지 않았습니다',
                'not-allowed': '❌ 마이크 권한을 허용해주세요',
                'network': '❌ 네트워크 오류',
                'aborted': 'ℹ️ 음성 인식이 중단되었습니다'
            };
            
            status.innerHTML = '<span style="color: #ffe0e0;">' + 
                (errorMessages[event.error] || '❌ 오류: ' + event.error) + '</span>';
        };
        
        // 인식 종료
        recognition.onend = function() {
            isRecording = false;
            voiceBtn.classList.remove('recording');
            btnText.textContent = '음성으로 질문하기';
            micIcon.textContent = '🎤';
        };
        
        // 자동으로 입력창에 넣기
        function autoFillInput(text) {
            try {
                // Streamlit의 부모 문서에서 입력창 찾기
                const parentDoc = window.parent.document;
                const inputs = parentDoc.querySelectorAll('input[type="text"], textarea');
                
                let filled = false;
                
                for (let input of inputs) {
                    // 빈 입력창이거나 플레이스홀더에 '질문'이 포함된 경우
                    if (!input.value || 
                        (input.placeholder && input.placeholder.includes('질문'))) {
                        
                        // 값 설정
                        input.value = text;
                        
                        // 이벤트 발생 (Streamlit이 인식하도록)
                        const inputEvent = new Event('input', { bubbles: true, cancelable: true });
                        const changeEvent = new Event('change', { bubbles: true, cancelable: true });
                        
                        input.dispatchEvent(inputEvent);
                        input.dispatchEvent(changeEvent);
                        
                        // 포커스
                        input.focus();
                        input.select();
                        
                        status.innerHTML = '<span style="color: #fff; font-weight: bold;">✅ 입력창에 자동 입력 완료!</span>';
                        filled = true;
                        break;
                    }
                }
                
                if (!filled) {
                    status.innerHTML = '<span style="color: #ffe0e0;">⚠️ 아래 복사 버튼을 눌러주세요</span>';
                }
            } catch(e) {
                console.error('자동 입력 실패:', e);
                status.innerHTML = '<span style="color: #ffe0e0;">⚠️ 아래 복사 버튼을 눌러주세요</span>';
            }
        }
        
        // 복사 및 붙여넣기 함수
        window.copyAndPaste = function() {
            if (!recognizedText) {
                alert('인식된 텍스트가 없습니다.');
                return;
            }
            
            // 클립보드에 복사
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(recognizedText).then(function() {
                    status.innerHTML = '<span style="color: #fff; font-weight: bold;">📋 복사 완료! 입력창에 붙여넣기(Ctrl+V) 하세요</span>';
                    
                    // 복사 후 자동 입력 재시도
                    autoFillInput(recognizedText);
                }).catch(function(err) {
                    console.error('복사 실패:', err);
                    alert('복사 실패: ' + recognizedText);
                });
            } else {
                // 구형 브라우저 대응
                const textArea = document.createElement('textarea');
                textArea.value = recognizedText;
                textArea.style.position = 'fixed';
                textArea.style.top = '-1000px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                try {
                    document.execCommand('copy');
                    status.innerHTML = '<span style="color: #fff; font-weight: bold;">📋 복사 완료! 입력창에 붙여넣기(Ctrl+V) 하세요</span>';
                    autoFillInput(recognizedText);
                } catch(err) {
                    alert('복사 실패: ' + recognizedText);
                }
                
                document.body.removeChild(textArea);
            }
        };
    })();
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

st.markdown("### 🎤 음성으로 질문")
st.caption("Chrome, Edge, 삼성 인터넷 브라우저 권장 | 마이크 권한 필요")
components.html(create_voice_input(), height=280, scrolling=False)

st.markdown("---")

tab1, tab2 = st.tabs(["📝 텍스트 질문", "📸 이미지 질문"])

with tab1:
    with st.form("text_form", clear_on_submit=True):
        query = st.text_input(
            "질문을 입력하세요",
            placeholder="예: 재료역학 공부 순서 알려줘",
            label_visibility="collapsed",
            key="text_query"
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
다음 질문에 일반기계기사 시험 준비생 관점에서 친절하게 답변해주세요:

{query}

답변 형식:
1. 핵심 개념 설명
2. 공식/계산 방법 (있다면)
3. 시험 출제 경향
4. 📺 추천 YouTube 영상 (URL 포함 - https://www.youtube.com/watch?v=VIDEO_ID 형식으로)
5. 검색 키워드 3개
"""
                        
                        response = model.generate_content(prompt)
                        st.session_state.ai_response = response.text
                        st.session_state.model_name = model_name
                        st.session_state.uploaded_image = None
                    else:
                        st.error("❌ 사용 가능한 AI 모델이 없습니다")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")
        else:
            st.error("⚠️ Streamlit Secrets에 GOOGLE_API_KEY를 설정하세요")

with tab2:
    uploaded_file = st.file_uploader(
        "문제 사진, 도면, 공식 스크린샷 등을 업로드하세요",
        type=['jpg', 'jpeg', 'png'],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이미지", use_column_width=True)
        
        if st.button("🗑️ 이미지 삭제", use_container_width=True):
            st.session_state.uploaded_image = None
            st.rerun()
    
    with st.form("image_form", clear_on_submit=True):
        image_query = st.text_input(
            "이미지에 대한 질문 (선택사항)",
            placeholder="예: 이 문제 풀이 과정 설명해줘",
            label_visibility="collapsed"
        )
        image_submit = st.form_submit_button("🔍 이미지 분석", use_container_width=True)
    
    if image_submit and uploaded_file:
        if "GOOGLE_API_KEY" in st.secrets:
            try:
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                
                with st.spinner("🖼️ AI가 이미지를 분석 중입니다..."):
                    model_name = get_gemini_model()
                    
                    if model_name:
                        model = genai.GenerativeModel(model_name)
                        image = Image.open(uploaded_file)
                        
                        prompt = f"""
이미지를 분석하고 {f'다음 질문에 답하세요: {image_query}' if image_query else '자세히 설명하세요'}

답변 형식:
1. 이미지 내용 분석
2. 문제라면 단계별 풀이 과정
3. 관련 개념 및 공식
4. 📺 추천 YouTube 영상 (URL 포함)
5. 추가 학습 자료
"""
                        
                        response = model.generate_content([prompt, image])
                        st.session_state.ai_response = response.text
                        st.session_state.model_name = model_name
                        st.session_state.uploaded_image = image
                    else:
                        st.error("❌ 사용 가능한 AI 모델이 없습니다")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")
        else:
            st.error("⚠️ API 키를 설정하세요")

# AI 답변 표시
if st.session_state.ai_response:
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 2])
    
    with col1:
        if st.button("🗑️ 답변 삭제", key="del", use_container_width=True):
            st.session_state.ai_response = None
            st.session_state.model_name = None
            st.session_state.uploaded_image = None
            st.session_state.audio_playing = False
            st.rerun()
    
    with col2:
        voice = st.selectbox(
            "🎙️ 목소리 선택",
            [("ko-KR-SunHiNeural", "👩 여자 목소리"), ("ko-KR-InJoonNeural", "👨 남자 목소리")],
            format_func=lambda x: x[1],
            key="voice"
        )
        st.session_state.selected_voice = voice[0]
    
    with col3:
        if st.button("🔊 음성으로 듣기", key="tts", use_container_width=True):
            with st.spinner("🎤 음성 생성 중..."):
                clean = clean_text_for_tts(st.session_state.ai_response)
                audio = text_to_speech(clean, st.session_state.selected_voice)
                
                if audio:
                    st.session_state.audio_playing = True
                    st.success("✅ 음성 준비 완료!")
                else:
                    st.error("❌ 음성 생성 실패")
    
    if st.session_state.audio_playing:
        st.markdown("### 🎧 음성 재생")
        
        clean = clean_text_for_tts(st.session_state.ai_response)
        audio = text_to_speech(clean, st.session_state.selected_voice)
        
        if audio:
            audio_b64 = base64.b64encode(audio).decode()
            st.markdown(f"""
            <audio controls autoplay style="width: 100%; border-radius: 8px;">
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                브라우저가 오디오를 지원하지 않습니다.
            </audio>
            """, unsafe_allow_html=True)
            
            if st.button("⏹️ 음성 정지", use_container_width=True):
                st.session_state.audio_playing = False
                st.rerun()
        
        st.markdown("---")
    
    if st.session_state.uploaded_image:
        st.image(st.session_state.uploaded_image, caption="분석한 이미지", use_column_width=True)
    
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
    ("기계달인", "전과목 강의", "inv.nadeko.net"),
    ("에듀윌", "핵심 요약", "inv.nadeko.net"),
    ("메가파이", "자격증 꿀팁", "inv.nadeko.net"),
    ("한솔아카데미", "기출 해설", "inv.nadeko.net"),
    ("공밀레", "개념 이해", "inv.nadeko.net"),
    ("Learn Engineering", "영문/애니메이션", "inv.nadeko.net")
]

for i, (name, desc, server) in enumerate(channels):
    url = f"https://{server}/search?q={urllib.parse.quote(name + ' 일반기계기사')}"
    
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
            url = f"https://inv.nadeko.net/search?q={urllib.parse.quote(keyword + ' 일반기계기사')}"
            st.markdown(f"- [{topic} 📺]({url})")

st.divider()

# ========== 실기 대비 ==========
st.header("🎯 실기 대비")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="info-card">
        <h3>📝 필답형</h3>
        <p><a href="https://inv.nadeko.net/search?q=일반기계기사+필답형+요약" target="_blank">📖 요약 정리</a></p>
        <p><a href="https://inv.nadeko.net/search?q=일반기계기사+필답형+기출" target="_blank">✍️ 기출 풀이</a></p>
        <p><a href="https://inv.nadeko.net/search?q=일반기계기사+필답형+공식" target="_blank">🎯 공식 정리</a></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h3>💻 작업형</h3>
        <p><a href="https://inv.nadeko.net/search?q=일반기계기사+인벤터" target="_blank">🖱️ 인벤터 기초</a></p>
        <p><a href="https://inv.nadeko.net/search?q=일반기계기사+투상" target="_blank">📐 투상 연습</a></p>
        <p><a href="https://inv.nadeko.net/search?q=일반기계기사+거칠기+공차" target="_blank">📏 거칠기/공차</a></p>
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
        💬 음성 인식은 Chrome, Edge, 삼성 인터넷 브라우저에서만 작동합니다
    </p>
</div>
""", unsafe_allow_html=True)
