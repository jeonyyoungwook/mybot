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

# ========== 프리미엄 CSS 스타일 ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;900&display=swap');

    * {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .main .block-container {
        padding: 1.5rem 1rem;
        max-width: 1200px;
    }

    /* ===== 히어로 섹션 ===== */
    .hero-section {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        border-radius: 24px;
        padding: 50px 40px;
        margin: 0 0 30px 0;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102,126,234,0.1) 0%, transparent 50%);
        animation: heroGlow 8s ease-in-out infinite;
    }

    @keyframes heroGlow {
        0%, 100% { transform: translate(0, 0); }
        50% { transform: translate(30px, -30px); }
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 30%, #f093fb 60%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 15px 0;
        position: relative;
        z-index: 1;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        color: rgba(255,255,255,0.8);
        font-size: 1.15rem;
        font-weight: 400;
        margin: 0 0 10px 0;
        position: relative;
        z-index: 1;
        line-height: 1.8;
    }

    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 8px 24px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 15px;
        position: relative;
        z-index: 1;
        letter-spacing: 1px;
    }

    /* ===== 섹션 헤더 ===== */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 35px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid #eef2ff;
    }

    .section-header h2 {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
        color: #1e1b4b;
    }

    .section-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
    }

    .section-icon.ai { background: linear-gradient(135deg, #667eea, #764ba2); }
    .section-icon.youtube { background: linear-gradient(135deg, #ff0000, #cc0000); }
    .section-icon.study { background: linear-gradient(135deg, #10b981, #059669); }
    .section-icon.exam { background: linear-gradient(135deg, #f59e0b, #d97706); }

    /* ===== 카드 시스템 ===== */
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        padding: 28px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        box-shadow: 0 12px 40px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    .gradient-card {
        border-radius: 20px;
        padding: 28px;
        margin: 15px 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.12);
        color: white;
        position: relative;
        overflow: hidden;
    }

    .gradient-card::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 150px;
        height: 150px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
        transform: translate(30%, -30%);
    }

    .gradient-card.purple { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .gradient-card.pink { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .gradient-card.green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .gradient-card.orange { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .gradient-card.dark { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }

    /* ===== YouTube 카드 ===== */
    .youtube-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 24px;
        margin: 15px 0;
        box-shadow: 0 10px 40px rgba(102,126,234,0.3);
        color: white;
        position: relative;
        overflow: hidden;
    }

    .youtube-card::after {
        content: '';
        position: absolute;
        top: -30px;
        right: -30px;
        width: 120px;
        height: 120px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }

    .youtube-card h3 {
        color: white;
        margin: 0 0 15px 0;
        font-size: 1.2rem;
        font-weight: 700;
        position: relative;
        z-index: 1;
    }

    .youtube-thumbnail {
        width: 100%;
        border-radius: 14px;
        margin: 12px 0;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }

    .youtube-thumbnail:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 35px rgba(0,0,0,0.4);
    }

    .play-button {
        display: block;
        background: white;
        color: #667eea;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        text-decoration: none;
        margin: 12px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        transition: all 0.3s;
        position: relative;
        z-index: 1;
        font-size: 1rem;
    }

    .play-button:hover {
        background: #f8f9ff;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        text-decoration: none;
        color: #667eea;
    }

    .server-links {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
        position: relative;
        z-index: 1;
    }

    .server-btn {
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s;
        border: 1px solid rgba(255,255,255,0.2);
        font-size: 0.85rem;
    }

    .server-btn:hover {
        background: rgba(255,255,255,0.25);
        transform: translateY(-1px);
        color: white;
        text-decoration: none;
    }

    /* ===== 음성 인식 ===== */
    .voice-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 30px;
        margin: 15px 0;
        box-shadow: 0 10px 40px rgba(102,126,234,0.3);
        position: relative;
        overflow: hidden;
    }

    .voice-container::before {
        content: '';
        position: absolute;
        top: -50px;
        right: -50px;
        width: 150px;
        height: 150px;
        background: rgba(255,255,255,0.06);
        border-radius: 50%;
    }

    #voiceBtn {
        background: white;
        color: #667eea;
        border: none;
        padding: 18px 30px;
        font-size: 1.15rem;
        border-radius: 14px;
        cursor: pointer;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        transition: all 0.3s;
        font-weight: 700;
        width: 100%;
        min-height: 60px;
        position: relative;
        z-index: 1;
        letter-spacing: 0.5px;
    }

    #voiceBtn:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }

    #voiceBtn.recording {
        background: linear-gradient(135deg, #ff3d00, #ff6e40);
        color: white;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(255,61,0,0.5); }
        50% { box-shadow: 0 0 0 18px rgba(255,61,0,0); }
    }

    #status {
        color: rgba(255,255,255,0.9);
        text-align: center;
        font-size: 0.95rem;
        margin-top: 15px;
        min-height: 30px;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }

    #result-box {
        display: none;
        background: white;
        color: #333;
        padding: 20px;
        border-radius: 14px;
        margin-top: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }

    #result-box.show {
        display: block;
    }

    #finalResult {
        font-size: 1.05rem;
        line-height: 1.7;
        margin-bottom: 12px;
        padding: 15px;
        background: #f5f3ff;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        color: #1e1b4b;
        font-weight: 500;
    }

    .copy-btn {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 14px 24px;
        border-radius: 10px;
        cursor: pointer;
        font-weight: 700;
        width: 100%;
        margin-top: 8px;
        min-height: 48px;
        font-size: 1rem;
        transition: all 0.3s;
        letter-spacing: 0.5px;
    }

    .copy-btn:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(102,126,234,0.4);
    }

    /* ===== AI 응답 ===== */
    .ai-response {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.06);
        border: 1px solid #eef2ff;
        line-height: 1.9;
        font-size: 1rem;
        color: #1e1b4b;
    }

    .ai-response h1, .ai-response h2, .ai-response h3 {
        color: #4338ca;
        margin-top: 20px;
    }

    .ai-response code {
        background: #f5f3ff;
        padding: 2px 8px;
        border-radius: 6px;
        color: #7c3aed;
        font-size: 0.9em;
    }

    .ai-response pre {
        background: #1e1b4b;
        color: #e0e7ff;
        padding: 20px;
        border-radius: 12px;
        overflow-x: auto;
    }

    .ai-response ul, .ai-response ol {
        padding-left: 24px;
    }

    .ai-response li {
        margin: 8px 0;
    }

    .ai-response strong {
        color: #4338ca;
    }

    .ai-response blockquote {
        border-left: 4px solid #667eea;
        padding: 12px 20px;
        margin: 15px 0;
        background: #f5f3ff;
        border-radius: 0 10px 10px 0;
    }

    /* ===== 채널/정보 카드 ===== */
    .channel-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 8px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eef2ff;
        transition: all 0.3s;
    }

    .channel-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transform: translateY(-2px);
        border-color: #c7d2fe;
    }

    .channel-card h4 {
        margin: 0 0 6px 0;
        font-size: 1rem;
        font-weight: 700;
        color: #1e1b4b;
    }

    .channel-card p {
        margin: 0;
        color: #6b7280;
        font-size: 0.88rem;
    }

    .channel-card a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
    }

    .channel-card a:hover {
        color: #4338ca;
        text-decoration: underline;
    }

    .info-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eef2ff;
        transition: all 0.3s;
    }

    .info-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    .info-card h3 {
        color: #1e1b4b;
        margin: 0 0 15px 0;
        font-weight: 700;
        font-size: 1.15rem;
    }

    .info-card p {
        margin: 8px 0;
        font-size: 0.95rem;
    }

    .info-card a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.2s;
    }

    .info-card a:hover {
        color: #4338ca;
        text-decoration: underline;
    }

    /* ===== 탭 스타일 ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f5f3ff;
        padding: 5px;
        border-radius: 14px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 12px 24px;
        background: transparent;
        font-weight: 600;
        color: #6b7280;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102,126,234,0.4);
    }

    /* ===== 버튼 스타일 ===== */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 10px 24px;
        transition: all 0.3s;
        border: none;
        min-height: 48px;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }

    /* ===== 인풋 스타일 ===== */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e0e7ff;
        padding: 14px 18px;
        font-size: 1rem;
        transition: all 0.3s;
        background: #fafaff;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.15);
        background: white;
    }

    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        border-radius: 12px;
        background: #f5f3ff;
        font-weight: 600;
        color: #1e1b4b;
    }

    /* ===== 오디오 ===== */
    audio {
        width: 100%;
        border-radius: 12px;
        margin: 10px 0;
    }

    /* ===== 디바이더 ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #c7d2fe, transparent);
        margin: 30px 0;
    }

    /* ===== 푸터 ===== */
    .footer-section {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        border-radius: 24px;
        padding: 50px 40px;
        margin: 40px 0 0 0;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .footer-section::before {
        content: '';
        position: absolute;
        bottom: -50px;
        left: -50px;
        width: 200px;
        height: 200px;
        background: rgba(102,126,234,0.1);
        border-radius: 50%;
    }

    /* ===== 반응형 ===== */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.8rem 0.5rem;
        }
        .hero-section {
            padding: 30px 20px;
            border-radius: 18px;
        }
        .hero-title {
            font-size: 1.8rem !important;
        }
        .hero-subtitle {
            font-size: 0.95rem;
        }
        h2 { font-size: 1.4rem !important; }
        h3 { font-size: 1.2rem !important; }
        button { min-height: 48px !important; }
        input, textarea { font-size: 16px !important; }
        .glass-card, .gradient-card, .ai-response {
            padding: 18px;
            border-radius: 16px;
        }
        .voice-container {
            padding: 20px;
        }
    }

    /* ===== 스크롤바 ===== */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #f5f3ff;
    }
    ::-webkit-scrollbar-thumb {
        background: #c7d2fe;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ========== 유틸리티 함수 ==========
def create_youtube_player(video_id: str, title: str = "YouTube 영상") -> str:
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
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.2);">
            <p style="margin: 0 0 8px 0; font-size: 0.85rem; opacity: 0.8;">🌐 다른 서버:</p>
            <div class="server-links">
                {server_links}
                <a href="https://www.youtube.com/watch?v={video_id}" target="_blank" class="server-btn">📱 YouTube</a>
            </div>
        </div>
    </div>
    """

def format_youtube_links(text: str) -> str:
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
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[*_~`#]+', '', text)
    emojis = {'✅':'체크','❌':'주의','💡':'팁','📺':'영상','🔥':'중요','⚠️':'경고','📌':'참고'}
    for emoji, word in emojis.items():
        text = text.replace(emoji, word)
    text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:3000] if len(text) > 3000 else text

# ========== 음성 인식 컴포넌트 (질문창 자동 이동) ==========
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
        <button class="copy-btn" onclick="copyAndPaste()">📋 질문창에 붙여넣기</button>
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
                    status.innerHTML = '❌ 음성 인식 시작 실패. 다시 시도하세요.';
                }
            }
        });

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
                status.innerHTML = '인식 중: "' + interimTranscript + '"';
            }
            if (finalTranscript) {
                recognizedText = finalTranscript.trim();
                status.innerHTML = '✅ 인식 완료! 질문창으로 이동합니다...';
                finalResult.textContent = '"' + recognizedText + '"';
                resultBox.classList.add('show');
                setTimeout(function() {
                    scrollToInputAndFill(recognizedText);
                }, 300);
            }
        };

        recognition.onerror = function(event) {
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
            status.innerHTML = errorMessages[event.error] || '❌ 오류: ' + event.error;
        };

        recognition.onend = function() {
            isRecording = false;
            voiceBtn.classList.remove('recording');
            btnText.textContent = '음성으로 질문하기';
            micIcon.textContent = '🎤';
        };

        function scrollToInputAndFill(text) {
            try {
                const parentDoc = window.parent.document;
                const inputs = parentDoc.querySelectorAll('input[type="text"], textarea');
                let filled = false;

                for (let input of inputs) {
                    const placeholder = input.placeholder || '';
                    if (placeholder.includes('질문') || placeholder.includes('예:') || placeholder.includes('입력')) {
                        // 스크롤 이동
                        input.scrollIntoView({ behavior: 'smooth', block: 'center' });

                        // React 방식으로 값 설정
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.parent.HTMLInputElement.prototype, 'value'
                        ).set;
                        nativeInputValueSetter.call(input, text);

                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));

                        setTimeout(function() {
                            input.focus();
                            input.select();
                        }, 500);

                        status.innerHTML = '✅ 질문창에 입력 완료! 🔍 질문하기를 눌러주세요';
                        filled = true;
                        break;
                    }
                }

                if (!filled) {
                    // 텍스트 입력창 못 찾은 경우: 클립보드 복사 + 안내
                    if (navigator.clipboard) {
                        navigator.clipboard.writeText(text);
                    }
                    status.innerHTML = '📋 복사 완료! 아래 질문창에 붙여넣기(Ctrl+V) 하세요';

                    // 첫번째 인풋으로 스크롤
                    if (inputs.length > 0) {
                        inputs[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                        setTimeout(function() { inputs[0].focus(); }, 500);
                    }
                }
            } catch(e) {
                status.innerHTML = '📋 아래 복사 버튼을 눌러주세요';
            }
        }

        window.copyAndPaste = function() {
            if (!recognizedText) {
                alert('인식된 텍스트가 없습니다.');
                return;
            }
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(recognizedText).then(function() {
                    scrollToInputAndFill(recognizedText);
                });
            } else {
                const textArea = document.createElement('textarea');
                textArea.value = recognizedText;
                textArea.style.position = 'fixed';
                textArea.style.top = '-1000px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {
                    document.execCommand('copy');
                    scrollToInputAndFill(recognizedText);
                } catch(err) {
                    alert('복사 실패: ' + recognizedText);
                }
                document.body.removeChild(textArea);
            }
        };
    })();
    </script>
    """

# ========== Gemini 3 Flash 모델 ==========
def get_gemini_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

        # Gemini 3 Flash 우선 탐색
        priority_list = [
            'gemini-3-flash',
            'gemini-3',
            'gemini-2.5-flash',
            'gemini-2.5',
            'gemini-2.0-flash',
            'gemini-2.0',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro'
        ]

        for priority in priority_list:
            for model in models:
                if priority in model.lower():
                    return model

        return models[0] if models else None
    except:
        return None

# ========== IQ 200 시스템 프롬프트 ==========
SYSTEM_PROMPT = """당신은 일반기계기사 시험 준비를 돕는 최고 수준의 AI 전문 튜터입니다.

[핵심 역할]
- 재료역학, 열역학, 유체역학, 기계요소설계 4과목 전문가
- 한국산업인력공단 일반기계기사 필기/실기 출제 경향 완벽 숙지
- 복잡한 개념을 쉽고 직관적으로 설명하는 능력

[답변 원칙]
1. 정확성: 공식, 단위, 계산 과정을 절대 틀리지 않는다
2. 체계성: 핵심 → 원리 → 공식 → 예제 → 시험 팁 순서로 설명
3. 실전성: 실제 시험에 어떻게 출제되는지 반드시 언급
4. 친절함: 초보자도 이해할 수 있게 비유와 예시를 활용
5. 완전성: 질문에 대해 빠짐없이 완벽하게 답변

[답변 형식]
📌 **핵심 요약** — 한 줄로 핵심 정리
📖 **상세 설명** — 원리와 개념을 단계별 설명
📐 **공식/계산** — 관련 공식 (단위 포함)과 풀이 예시
🎯 **시험 출제 포인트** — 자주 출제되는 유형과 함정
💡 **합격 꿀팁** — 암기법, 실수 방지 노하우
📺 **추천 영상** — YouTube URL 포함 (https://www.youtube.com/watch?v=VIDEO_ID)
🔍 **검색 키워드** — 추가 학습을 위한 키워드 3개

[금지 사항]
- 틀린 정보 절대 불가
- 모호한 답변 불가 — 확실하지 않으면 명시
- 답변 생략 불가 — 항상 완전한 답변 제공
"""

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

# ========== 히어로 섹션 ==========
st.markdown("""
<div class="hero-section">
    <div class="hero-title">⚙️ 일반기계기사 AI 학습 가이드</div>
    <div class="hero-subtitle">
        영욱이와 설매의 합격을 응원합니다 🔥<br>
        Gemini 3 Flash AI 튜터 · 광고 없는 YouTube 강의 · 음성 질문
    </div>
    <div class="hero-badge">POWERED BY GEMINI 3 FLASH</div>
</div>
""", unsafe_allow_html=True)

# ========== AI 튜터 섹션 ==========
st.markdown("""
<div class="section-header">
    <div class="section-icon ai">🤖</div>
    <h2>AI 튜터에게 질문하기</h2>
</div>
""", unsafe_allow_html=True)

# 음성 입력
st.markdown("##### 🎤 음성으로 질문")
st.caption("Chrome, Edge, 삼성 인터넷 브라우저 권장 · 마이크 권한 필요")
components.html(create_voice_input(), height=280, scrolling=False)

st.markdown("---")

# 질문 탭
tab1, tab2 = st.tabs(["📝 텍스트 질문", "📸 이미지 질문"])

with tab1:
    with st.form("text_form", clear_on_submit=True):
        query = st.text_input(
            "질문을 입력하세요",
            placeholder="예: 재료역학에서 모어원 쉽게 설명해줘",
            label_visibility="collapsed",
            key="text_query"
        )
        submit = st.form_submit_button("🔍 질문하기", use_container_width=True)

    if submit and query:
        if "GOOGLE_API_KEY" in st.secrets:
            try:
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

                with st.spinner("🤖 Gemini 3 Flash가 최고의 답변을 생성 중..."):
                    model_name = get_gemini_model()

                    if model_name:
                        model = genai.GenerativeModel(
                            model_name,
                            system_instruction=SYSTEM_PROMPT
                        )

                        user_prompt = f"""[학생 질문]
{query}

위 질문에 대해 일반기계기사 시험 준비생에게 완벽한 답변을 작성하세요.
반드시 정해진 형식(📌📖📐🎯💡📺🔍)을 따르세요.
YouTube 영상 추천 시 실제 존재하는 URL을 포함하세요."""

                        response = model.generate_content(user_prompt)
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
        st.image(image, caption="업로드된 이미지", use_container_width=True)

        if st.button("🗑️ 이미지 삭제", use_container_width=True):
            st.session_state.uploaded_image = None
            st.rerun()

    with st.form("image_form", clear_on_submit=True):
        image_query = st.text_input(
            "이미지에 대한 질문 (선택사항)",
            placeholder="예: 이 문제 풀이 과정을 단계별로 설명해줘",
            label_visibility="collapsed"
        )
        image_submit = st.form_submit_button("🔍 이미지 분석", use_container_width=True)

    if image_submit and uploaded_file:
        if "GOOGLE_API_KEY" in st.secrets:
            try:
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

                with st.spinner("🖼️ Gemini 3 Flash가 이미지를 정밀 분석 중..."):
                    model_name = get_gemini_model()

                    if model_name:
                        model = genai.GenerativeModel(
                            model_name,
                            system_instruction=SYSTEM_PROMPT
                        )
                        image = Image.open(uploaded_file)

                        img_prompt = f"""[이미지 분석 요청]
{f'학생 질문: {image_query}' if image_query else '이미지를 분석하고 상세히 설명하세요'}

이미지를 분석한 후 다음을 포함하여 답변하세요:
1. 📌 이미지 내용 파악
2. 📖 관련 개념/이론 설명
3. 📐 문제라면 완전한 단계별 풀이 (공식, 단위, 계산 포함)
4. 🎯 시험 출제 포인트
5. 💡 유사 문제 대비 팁
6. 📺 추천 YouTube 영상 (URL 포함)"""

                        response = model.generate_content([img_prompt, image])
                        st.session_state.ai_response = response.text
                        st.session_state.model_name = model_name
                        st.session_state.uploaded_image = image
                    else:
                        st.error("❌ 사용 가능한 AI 모델이 없습니다")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")
        else:
            st.error("⚠️ API 키를 설정하세요")

# ========== AI 답변 표시 ==========
if st.session_state.ai_response:
    st.markdown("---")

    # 상단 컨트롤
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
            "🎙️ 목소리",
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

    # 모델 정보 표시
    if st.session_state.model_name:
        st.caption(f"🤖 사용 모델: `{st.session_state.model_name}`")

    # 음성 재생
    if st.session_state.audio_playing:
        st.markdown("##### 🎧 음성 재생")
        clean = clean_text_for_tts(st.session_state.ai_response)
        audio = text_to_speech(clean, st.session_state.selected_voice)
        if audio:
            audio_b64 = base64.b64encode(audio).decode()
            st.markdown(f"""
            <audio controls autoplay style="width: 100%; border-radius: 12px;">
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)
            if st.button("⏹️ 음성 정지", use_container_width=True):
                st.session_state.audio_playing = False
                st.rerun()
        st.markdown("---")

    # 분석 이미지
    if st.session_state.uploaded_image:
        st.image(st.session_state.uploaded_image, caption="분석한 이미지", use_container_width=True)

    # 답변 렌더링
    response_text = st.session_state.ai_response
    response_text = format_youtube_links(response_text)
    response_text = add_search_links(response_text)

    st.markdown("##### 💡 AI 답변")
    st.markdown(f'<div class="ai-response">{response_text}</div>', unsafe_allow_html=True)

st.markdown("---")

# ========== 추천 채널 ==========
st.markdown("""
<div class="section-header">
    <div class="section-icon youtube">📺</div>
    <h2>추천 YouTube 채널 (광고 없음)</h2>
</div>
""", unsafe_allow_html=True)

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
        <div class="channel-card">
            <h4>👉 <a href="{url}" target="_blank">{name}</a></h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ========== 과목별 강의 ==========
st.markdown("""
<div class="section-header">
    <div class="section-icon study">📚</div>
    <h2>과목별 핵심 강의</h2>
</div>
""", unsafe_allow_html=True)

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

st.markdown("---")

# ========== 실기 대비 ==========
st.markdown("""
<div class="section-header">
    <div class="section-icon exam">🎯</div>
    <h2>실기 대비</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="info-card">
        <h3>📝 필답형</h3>
        <p>📖 <a href="https://inv.nadeko.net/search?q=일반기계기사+필답형+요약" target="_blank">요약 정리</a></p>
        <p>✍️ <a href="https://inv.nadeko.net/search?q=일반기계기사+필답형+기출" target="_blank">기출 풀이</a></p>
        <p>🎯 <a href="https://inv.nadeko.net/search?q=일반기계기사+필답형+공식" target="_blank">공식 정리</a></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h3>💻 작업형</h3>
        <p>🖱️ <a href="https://inv.nadeko.net/search?q=일반기계기사+인벤터" target="_blank">인벤터 기초</a></p>
        <p>📐 <a href="https://inv.nadeko.net/search?q=일반기계기사+투상" target="_blank">투상 연습</a></p>
        <p>📏 <a href="https://inv.nadeko.net/search?q=일반기계기사+거칠기+공차" target="_blank">거칠기/공차</a></p>
    </div>
    """, unsafe_allow_html=True)

# ========== 푸터 ==========
st.markdown("""
<div class="footer-section">
    <h2 style="color: #a5b4fc; margin: 0 0 15px 0; font-size: 1.8rem; font-weight: 700;">
        🔥 일반기계기사 합격을 응원합니다! 🔥
    </h2>
    <p style="color: rgba(255,255,255,0.75); font-size: 1.05rem; margin: 12px 0; line-height: 1.8;">
        🎤 음성으로 질문하고 🔊 음성으로 답변을 들어보세요!<br>
        ✅ 모든 YouTube 영상 광고 100% 차단 (Invidious 제공)
    </p>
    <div style="margin-top: 25px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
        <p style="color: rgba(255,255,255,0.4); font-size: 0.85rem; margin: 0;">
            Made with ❤️ by AI &nbsp;·&nbsp; Powered by Gemini 3 Flash + Edge TTS + Invidious + Web Speech API
        </p>
        <p style="color: rgba(255,255,255,0.3); font-size: 0.78rem; margin: 8px 0 0 0;">
            💬 음성 인식은 Chrome, Edge, 삼성 인터넷 브라우저에서 작동합니다
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
