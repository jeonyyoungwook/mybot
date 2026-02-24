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
import requests
from typing import List, Tuple

# ========== 1. 페이지 기본 설정 ==========
st.set_page_config(
    page_title="일반기계기사 학습 가이드",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== 🌐 Invidious 서버 자동 체크 ==========
@st.cache_data(ttl=300)
def get_working_invidious_instances() -> List[Tuple[str, str]]:
    """살아있는 Invidious 서버를 자동으로 찾아서 반환"""
    try:
        api_url = "https://api.invidious.io/instances.json"
        response = requests.get(api_url, timeout=10)
        instances_data = response.json()
        
        working_instances = []
        
        for instance in instances_data:
            try:
                domain = instance[0]
                info = instance[1]
                
                if (info.get('type') == 'https' and 
                    info.get('api') == True and
                    info.get('monitor', {}).get('statusClass') in ['success', 'warning']):
                    
                    test_url = f"https://{domain}/api/v1/videos/jNQXAC9IVRw"
                    
                    try:
                        test_response = requests.head(test_url, timeout=3, allow_redirects=True)
                        if test_response.status_code < 500:
                            working_instances.append((domain, f"서버 {len(working_instances)+1}"))
                            
                            if len(working_instances) >= 10:
                                break
                    except:
                        continue
                        
            except Exception:
                continue
        
        if not working_instances:
            fallback_instances = [
                ("inv.tux.pizza", "독일 서버"),
                ("invidious.privacyredirect.com", "미국 서버"),
                ("iv.nboeck.de", "독일 서버2"),
                ("yt.artemislena.eu", "루마니아 서버"),
                ("invidious.fdn.fr", "프랑스 서버")
            ]
            
            for domain, name in fallback_instances:
                try:
                    test_url = f"https://{domain}/api/v1/videos/jNQXAC9IVRw"
                    test_response = requests.head(test_url, timeout=3)
                    if test_response.status_code < 500:
                        working_instances.append((domain, name))
                except:
                    continue
        
        return working_instances if working_instances else []
        
    except Exception:
        return []

# ========== 🎬 YouTube 플레이어 (안정화 버전) ==========
def create_ad_free_youtube_player(video_id: str, title: str = "YouTube 영상") -> str:
    """YouTube Nocookie 임베드 + Invidious 대체 링크 제공"""
    
    youtube_nocookie_embed = f"https://www.youtube-nocookie.com/embed/{video_id}"
    thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    
    invidious_instances = get_working_invidious_instances()
    
    invidious_links = ""
    if invidious_instances:
        for i, (instance, name) in enumerate(invidious_instances[:5], 1):
            watch_url = f"https://{instance}/watch?v={video_id}"
            invidious_links += f'''
                <a href="{watch_url}" target="_blank" class="server-btn">
                    🎬 {name} (광고 0개)
                </a>
            '''
    
    return f"""
    <div class="youtube-card">
        <h4>🎬 {title}</h4>
        
        <div class="adfree-youtube-container">
            <iframe 
                src="{youtube_nocookie_embed}"
                allowfullscreen
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                loading="lazy"
                frameborder="0"
                title="{title}"
            ></iframe>
        </div>
        
        <p style="font-size: 0.85rem; color: #666; margin: 10px 0; text-align: center;">
            ▲ YouTube 임베드 (추적 최소화) | 
            <a href="https://www.youtube.com/watch?v={video_id}" target="_blank" style="color: #ff0000;">
                YouTube에서 보기 →
            </a>
        </p>
        
        {f'''
        <details style="margin-top: 10px;">
            <summary style="cursor: pointer; color: #10b981; font-size: 0.85rem; padding: 8px; background: #f0fdf4; border-radius: 6px; font-weight: bold;">
                ✅ 광고 100% 차단 서버로 보기 (Invidious)
            </summary>
            <div class="server-selector">
                <p style="font-size: 0.85rem; color: #666; margin: 5px 0;">아래 서버는 광고가 전혀 없습니다:</p>
                {invidious_links}
            </div>
        </details>
        ''' if invidious_links else '''
        <p style="font-size: 0.85rem; color: #f59e0b; margin: 10px 0; text-align: center;">
            ⚠️ 광고 차단 서버(Invidious)를 현재 사용할 수 없습니다.
        </p>
        '''}
    </div>
    """

# ========== 🎨 모바일 최적화 CSS ==========
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        height: 100%;
        min-height: 100vh;
        overflow-x: hidden;
        margin: 0;
        padding: 0;
    }
    
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    @media (max-width: 768px) {
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        p, li, div { font-size: 0.95rem !important; line-height: 1.6 !important; }
        
        button, [data-testid="stButton"] button {
            min-height: 48px !important;
            padding: 12px 20px !important;
            font-size: 1rem !important;
        }
        
        input, textarea {
            font-size: 16px !important;
            min-height: 48px !important;
        }
    }
    
    img {
        max-width: 100% !important;
        height: auto !important;
        border-radius: 8px;
    }
    
    .youtube-card {
        border: 2px solid #ff0000;
        border-radius: 12px;
        padding: 15px;
        margin: 20px 0;
        background: linear-gradient(135deg, #fff5f5 0%, #ffe5e5 100%);
    }
    
    .youtube-card h4 {
        color: #ff0000;
        margin: 0 0 15px 0;
    }
    
    .adfree-youtube-container {
        position: relative;
        width: 100%;
        padding-bottom: 56.25%;
        margin: 20px 0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        background: #000;
    }
    
    .adfree-youtube-container iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border: none;
    }
    
    .youtube-thumbnail {
        width: 100%;
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        margin: 10px 0;
        cursor: pointer;
        transition: transform 0.2s;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .youtube-thumbnail:hover {
        transform: scale(1.02);
    }
    
    .play-button {
        display: inline-block;
        background-color: #ff0000;
        color: white;
        padding: 14px 24px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
        width: 100%;
        box-sizing: border-box;
        min-height: 48px;
        line-height: 20px;
        transition: background-color 0.2s;
        margin-top: 10px;
    }
    
    .play-button:hover {
        background-color: #cc0000;
        color: white;
        text-decoration: none;
    }
    
    .adfree-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-left: 8px;
    }
    
    .server-selector {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 10px;
        margin-top: 10px;
    }
    
    .server-btn {
        display: inline-block;
        background: #3b82f6;
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 0.85rem;
        margin: 4px;
        transition: background-color 0.2s;
    }
    
    .server-btn:hover {
        background: #2563eb;
        color: white;
        text-decoration: none;
    }
    
    audio {
        width: 100% !important;
        max-width: 100% !important;
        min-height: 48px;
    }
    
    .voice-container {
        position: relative;
        width: 100%;
        max-width: 100%;
        overflow: hidden;
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
    }
    
    .copy-btn:active {
        background: #059669;
        transform: scale(0.98);
    }
</style>
""", unsafe_allow_html=True)

# ========== 🎤 TTS 기능 ==========
async def text_to_speech_async(text, voice="ko-KR-SunHiNeural"):
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
    audio_base64 = base64.b64encode(audio_bytes).decode()
    return f"""
    <audio controls autoplay style="width: 100%; max-width: 100%; min-height: 48px; border-radius: 8px;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        브라우저가 오디오를 지원하지 않습니다.
    </audio>
    """

def clean_text_for_tts(text):
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

# ========== 🎤 음성 인식 컴포넌트 ==========
def create_voice_input_component():
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
    """YouTube 링크를 플레이어로 변환"""
    youtube_patterns = [
        (r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', '유튜브 영상'),
        (r'https?://(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]+)', 'YouTube Shorts'),
        (r'https?://youtu\.be/([a-zA-Z0-9_-]+)', '공유 링크')
    ]
    
    formatted_text = text
    for pattern, label in youtube_patterns:
        matches = list(re.finditer(pattern, formatted_text))
        for match in reversed(matches):
            video_id = match.group(1)
            player_html = create_ad_free_youtube_player(video_id, label)
            formatted_text = formatted_text[:match.start()] + player_html + formatted_text[match.end():]
    
    return formatted_text

def make_links_clickable(text):
    """일반 URL 클릭 가능하게"""
    url_pattern = r'(https?://(?!(?:www\.)?youtube\.com|youtu\.be|invidious\.|inv\.|iv\.|yt\.)[^\s\)]+)'
    
    def replace_url(match):
        url = match.group(1).rstrip('.,;:!?')
        return f'[🔗 링크]({url})'
    
    return re.sub(url_pattern, replace_url, text)

def add_youtube_search_links(text):
    """키워드에 검색 링크 추가"""
    instances = get_working_invidious_instances()
    search_instance = instances[0][0] if instances else "youtube.com"
    
    keywords = [
        "재료역학", "열역학", "유체역학", "기계요소설계",
        "SFD", "BMD", "베르누이", "모어원", "좌굴", "엔트로피",
        "랭킨 사이클", "오토 사이클", "디젤 사이클",
        "레이놀즈 수", "기어", "베어링", "나사"
    ]
    
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
    
    for keyword in keywords:
        if keyword in modified_text and keyword not in used_keywords:
            search_query = urllib.parse.quote(f"{keyword} 일반기계기사")
            
            if search_instance != "youtube.com":
                search_url = f"https://{search_instance}/search?q={search_query}"
            else:
                search_url = f"https://www.youtube.com/results?search_query={search_query}"
            
            pattern = rf'\b({re.escape(keyword)})\b'
            
            if re.search(pattern, modified_text):
                replacement = f'[\\1 📺]({search_url})'
                modified_text = re.sub(pattern, replacement, modified_text, count=1)
                used_keywords.add(keyword)
    
    for placeholder, original in placeholders:
        modified_text = modified_text.replace(placeholder, original)
    
    return modified_text

def get_best_gemini_model():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        priority_order = ['gemini-2.0-flash-exp', 'gemini-exp', 'gemini-2.0', 'gemini-1.5', 'gemini-pro']
        
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
        'gemini-2.0-flash-exp': 'Gemini 2.0 Flash (실험)',
        'gemini-exp': 'Gemini Experimental',
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
**✅ YouTube 임베드 + 광고 차단 옵션** 제공
""")

# 🌐 서버 상태 표시
with st.expander("🌐 광고 차단 서버 상태 (Invidious)", expanded=False):
    with st.spinner("서버 확인 중..."):
        working_instances = get_working_invidious_instances()
        
        if working_instances:
            st.success(f"✅ 광고 차단 서버: **{len(working_instances)}개** 사용 가능")
            
            for i, (domain, name) in enumerate(working_instances[:5], 1):
                st.markdown(f"{i}. **{domain}** ({name})")
        else:
            st.warning("⚠️ 광고 차단 서버를 현재 사용할 수 없습니다. YouTube 원본을 사용하세요.")

st.divider()

# ========== AI 튜터 섹션 (이하 동일) ==========
# (나머지 코드는 이전과 동일하므로 생략 - 너무 길어서)
# ... AI 튜터, 채널 추천, 과목별 강의 등 모두 동일 ...
