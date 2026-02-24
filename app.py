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

    .stApp {
        background: linear-gradient(180deg, #f8f9fe 0%, #eef1f8 50%, #e8ecf4 100%);
    }

    .main .block-container {
        padding: 1.5rem 1rem;
        max-width: 1200px;
    }

    /* ===== 히어로 섹션 ===== */
    .hero-section {
        background: linear-gradient(135deg, #e8f4f8 0%, #d4e5f7 50%, #c9daf8 100%);
        border-radius: 28px;
        padding: 55px 45px;
        margin: 0 0 35px 0;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 15px 50px rgba(100,120,180,0.12);
        border: 1px solid rgba(255,255,255,0.8);
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: -100px;
        right: -100px;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.6) 0%, transparent 70%);
        border-radius: 50%;
    }

    .hero-section::after {
        content: '';
        position: absolute;
        bottom: -50px;
        left: -50px;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(147,197,253,0.3) 0%, transparent 70%);
        border-radius: 50%;
    }

    .hero-title {
        font-size: 2.6rem;
        font-weight: 900;
        color: #1e3a5f;
        margin: 0 0 18px 0;
        position: relative;
        z-index: 1;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    .hero-subtitle {
        color: #4a6d8c;
        font-size: 1.12rem;
        font-weight: 500;
        margin: 0 0 12px 0;
        position: relative;
        z-index: 1;
        line-height: 1.9;
    }

    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, #7c3aed, #c026d3);
        color: white;
        padding: 10px 28px;
        border-radius: 50px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-top: 18px;
        position: relative;
        z-index: 1;
        letter-spacing: 1.5px;
        box-shadow: 0 4px 15px rgba(124,58,237,0.4);
        animation: badge-glow 2s ease-in-out infinite alternate;
    }

    @keyframes badge-glow {
        from { box-shadow: 0 4px 15px rgba(124,58,237,0.4); }
        to { box-shadow: 0 4px 25px rgba(192,38,211,0.6); }
    }

    /* ===== 섹션 헤더 ===== */
    .section-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 40px 0 22px 0;
        padding-bottom: 14px;
        border-bottom: 2px solid rgba(99,102,241,0.15);
    }

    .section-header h2 {
        margin: 0;
        font-size: 1.55rem;
        font-weight: 800;
        color: #1e3a5f;
    }

    .section-icon {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .section-icon.ai { background: linear-gradient(135deg, #7c3aed, #c026d3); }
    .section-icon.youtube { background: linear-gradient(135deg, #ef4444, #dc2626); }
    .section-icon.study { background: linear-gradient(135deg, #10b981, #059669); }
    .section-icon.exam { background: linear-gradient(135deg, #f59e0b, #d97706); }

    /* ===== 프리미엄 음성 인식 ===== */
    .voice-premium-container {
        background: linear-gradient(145deg, #ffffff 0%, #f8faff 100%);
        border-radius: 24px;
        padding: 35px;
        margin: 20px 0;
        box-shadow: 
            0 20px 60px rgba(124,58,237,0.1),
            0 1px 3px rgba(0,0,0,0.05),
            inset 0 1px 0 rgba(255,255,255,0.9);
        border: 1px solid rgba(124,58,237,0.1);
        position: relative;
        overflow: hidden;
    }

    .voice-premium-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #7c3aed, #c026d3, #ec4899);
    }

    .voice-premium-container::after {
        content: '';
        position: absolute;
        top: -80px;
        right: -80px;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(124,58,237,0.05) 0%, transparent 70%);
        border-radius: 50%;
    }

    .voice-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 25px;
        position: relative;
        z-index: 1;
    }

    .voice-icon-wrapper {
        width: 52px;
        height: 52px;
        background: linear-gradient(135deg, #7c3aed, #c026d3);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        box-shadow: 0 8px 20px rgba(124,58,237,0.3);
    }

    .voice-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #1e293b;
        margin: 0;
    }

    .voice-subtitle {
        font-size: 0.85rem;
        color: #64748b;
        margin: 3px 0 0 0;
    }

    #voiceBtn {
        background: linear-gradient(135deg, #7c3aed 0%, #c026d3 100%);
        color: white;
        border: none;
        padding: 22px 35px;
        font-size: 1.15rem;
        border-radius: 16px;
        cursor: pointer;
        box-shadow: 
            0 10px 30px rgba(124,58,237,0.35),
            0 2px 4px rgba(124,58,237,0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 700;
        width: 100%;
        min-height: 68px;
        position: relative;
        z-index: 1;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    }

    #voiceBtn:hover {
        transform: translateY(-3px);
        box-shadow: 
            0 15px 40px rgba(124,58,237,0.4),
            0 5px 10px rgba(124,58,237,0.2);
    }

    #voiceBtn:active {
        transform: translateY(-1px);
    }

    #voiceBtn.recording {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        box-shadow: 
            0 10px 30px rgba(239,68,68,0.4),
            0 0 0 4px rgba(239,68,68,0.2);
        animation: recording-pulse 2s ease-in-out infinite;
    }

    @keyframes recording-pulse {
        0%, 100% { 
            box-shadow: 
                0 10px 30px rgba(239,68,68,0.4),
                0 0 0 4px rgba(239,68,68,0.2);
        }
        50% { 
            box-shadow: 
                0 10px 30px rgba(239,68,68,0.5),
                0 0 0 12px rgba(239,68,68,0.1);
        }
    }

    #micIcon {
        font-size: 1.5rem;
    }

    #status {
        color: #475569;
        text-align: center;
        font-size: 0.95rem;
        margin-top: 18px;
        min-height: 28px;
        font-weight: 600;
        position: relative;
        z-index: 1;
        padding: 12px;
        background: rgba(124,58,237,0.05);
        border-radius: 12px;
    }

    #result-box {
        display: none;
        background: linear-gradient(145deg, #f0fdf4 0%, #ecfdf5 100%);
        color: #166534;
        padding: 22px;
        border-radius: 16px;
        margin-top: 18px;
        box-shadow: 
            0 8px 25px rgba(16,185,129,0.1),
            inset 0 1px 0 rgba(255,255,255,0.8);
        border: 1px solid rgba(16,185,129,0.2);
        position: relative;
        z-index: 1;
    }

    #result-box.show {
        display: block;
        animation: slideUp 0.3s ease-out;
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    #finalResult {
        font-size: 1.1rem;
        line-height: 1.7;
        margin-bottom: 15px;
        padding: 18px;
        background: white;
        border-radius: 12px;
        border-left: 4px solid #10b981;
        color: #1e293b;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .copy-btn {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        border: none;
        padding: 16px 28px;
        border-radius: 12px;
        cursor: pointer;
        font-weight: 700;
        width: 100%;
        margin-top: 10px;
        min-height: 52px;
        font-size: 1rem;
        transition: all 0.3s;
        letter-spacing: 0.5px;
        box-shadow: 0 6px 20px rgba(16,185,129,0.3);
    }

    .copy-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(16,185,129,0.4);
    }

    /* ===== 카드 시스템 ===== */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.5);
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

    /* ===== YouTube 카드 ===== */
    .youtube-card {
        background: linear-gradient(135deg, #7c3aed 0%, #c026d3 100%);
        border-radius: 20px;
        padding: 24px;
        margin: 15px 0;
        box-shadow: 0 12px 40px rgba(124,58,237,0.25);
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
        background: rgba(255,255,255,0.1);
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
        color: #7c3aed;
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
        color: #7c3aed;
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

    /* ===== AI 응답 (Ultra 버전) ===== */
    .ai-response {
        background: white;
        border-radius: 20px;
        padding: 32px;
        margin: 20px 0;
        box-shadow: 
            0 10px 40px rgba(0,0,0,0.06),
            0 1px 3px rgba(0,0,0,0.03);
        border: 1px solid rgba(124,58,237,0.1);
        line-height: 2;
        font-size: 1.02rem;
        color: #1e293b;
        position: relative;
    }

    .ai-response::before {
        content: '🎓 ULTRA AI';
        position: absolute;
        top: -12px;
        left: 20px;
        background: linear-gradient(135deg, #7c3aed, #c026d3);
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .ai-response h1, .ai-response h2, .ai-response h3 {
        color: #7c3aed;
        margin-top: 24px;
        font-weight: 700;
    }

    .ai-response h1 { font-size: 1.5rem; }
    .ai-response h2 { font-size: 1.3rem; }
    .ai-response h3 { font-size: 1.15rem; }

    .ai-response code {
        background: #faf5ff;
        padding: 3px 10px;
        border-radius: 6px;
        color: #7c3aed;
        font-size: 0.92em;
        font-weight: 500;
    }

    .ai-response pre {
        background: #1e293b;
        color: #e2e8f0;
        padding: 22px;
        border-radius: 14px;
        overflow-x: auto;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    .ai-response ul, .ai-response ol {
        padding-left: 26px;
    }

    .ai-response li {
        margin: 10px 0;
    }

    .ai-response strong {
        color: #7c3aed;
        font-weight: 700;
    }

    .ai-response blockquote {
        border-left: 4px solid #c026d3;
        padding: 15px 22px;
        margin: 18px 0;
        background: #fdf4ff;
        border-radius: 0 12px 12px 0;
        font-style: normal;
    }

    .ai-response table {
        width: 100%;
        border-collapse: collapse;
        margin: 18px 0;
    }

    .ai-response th, .ai-response td {
        border: 1px solid #e2e8f0;
        padding: 12px 15px;
        text-align: left;
    }

    .ai-response th {
        background: #faf5ff;
        font-weight: 700;
        color: #7c3aed;
    }

    /* ===== 채널/정보 카드 ===== */
    .channel-card {
        background: white;
        border-radius: 16px;
        padding: 22px;
        margin: 8px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.04);
        transition: all 0.3s;
    }

    .channel-card:hover {
        box-shadow: 0 8px 30px rgba(124,58,237,0.12);
        transform: translateY(-3px);
        border-color: rgba(124,58,237,0.2);
    }

    .channel-card h4 {
        margin: 0 0 8px 0;
        font-size: 1.05rem;
        font-weight: 700;
        color: #1e293b;
    }

    .channel-card p {
        margin: 0;
        color: #64748b;
        font-size: 0.9rem;
    }

    .channel-card a {
        color: #7c3aed;
        text-decoration: none;
        font-weight: 700;
    }

    .channel-card a:hover {
        color: #6d28d9;
        text-decoration: underline;
    }

    .info-card {
        background: white;
        border-radius: 18px;
        padding: 26px;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.04);
        transition: all 0.3s;
    }

    .info-card:hover {
        box-shadow: 0 10px 35px rgba(124,58,237,0.1);
        transform: translateY(-2px);
    }

    .info-card h3 {
        color: #1e293b;
        margin: 0 0 18px 0;
        font-weight: 800;
        font-size: 1.18rem;
    }

    .info-card p {
        margin: 10px 0;
        font-size: 0.98rem;
    }

    .info-card a {
        color: #7c3aed;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.2s;
    }

    .info-card a:hover {
        color: #6d28d9;
        text-decoration: underline;
    }

    /* ===== 탭 스타일 ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #f1f5f9;
        padding: 6px;
        border-radius: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 14px 28px;
        background: transparent;
        font-weight: 600;
        color: #64748b;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7c3aed 0%, #c026d3 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(124,58,237,0.35);
    }

    /* ===== 버튼 스타일 ===== */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 12px 26px;
        transition: all 0.3s;
        border: none;
        min-height: 50px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }

    /* ===== 인풋 스타일 ===== */
    .stTextInput > div > div > input {
        border-radius: 14px;
        border: 2px solid #e2e8f0;
        padding: 16px 20px;
        font-size: 1rem;
        transition: all 0.3s;
        background: white;
    }

    .stTextInput > div > div > input:focus {
        border-color: #7c3aed;
        box-shadow: 0 0 0 4px rgba(124,58,237,0.1);
    }

    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        border-radius: 14px;
        background: #f8fafc;
        font-weight: 700;
        color: #1e293b;
        padding: 12px 16px;
    }

    /* ===== 오디오 ===== */
    audio {
        width: 100%;
        border-radius: 14px;
        margin: 12px 0;
    }

    /* ===== 디바이더 ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(124,58,237,0.2), transparent);
        margin: 35px 0;
    }

    /* ===== 푸터 ===== */
    .footer-section {
        background: linear-gradient(135deg, #e8f4f8 0%, #d4e5f7 50%, #c9daf8 100%);
        border-radius: 28px;
        padding: 55px 45px;
        margin: 45px 0 0 0;
        text-align: center;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.8);
        box-shadow: 0 15px 50px rgba(100,120,180,0.1);
    }

    .footer-section::before {
        content: '';
        position: absolute;
        bottom: -60px;
        left: -60px;
        width: 180px;
        height: 180px;
        background: rgba(124,58,237,0.06);
        border-radius: 50%;
    }

    .footer-section h2 {
        color: #1e3a5f;
        margin: 0 0 18px 0;
        font-size: 1.9rem;
        font-weight: 800;
        position: relative;
        z-index: 1;
    }

    .footer-section p {
        position: relative;
        z-index: 1;
    }

    /* ===== 반응형 ===== */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.8rem 0.5rem;
        }
        .hero-section {
            padding: 35px 22px;
            border-radius: 20px;
        }
        .hero-title {
            font-size: 1.7rem !important;
        }
        .hero-subtitle {
            font-size: 0.95rem;
        }
        .voice-premium-container {
            padding: 25px 20px;
        }
        h2 { font-size: 1.35rem !important; }
        h3 { font-size: 1.15rem !important; }
        button { min-height: 48px !important; }
        input, textarea { font-size: 16px !important; }
        .glass-card, .ai-response {
            padding: 20px;
            border-radius: 16px;
        }
    }

    /* ===== 스크롤바 ===== */
    ::-webkit-scrollbar {
        width: 7px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    ::-webkit-scrollbar-thumb {
        background: #ddd6fe;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #7c3aed;
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
    emojis = {'✅':'체크','❌':'주의','💡':'팁','📺':'영상','🔥':'중요','⚠️':'경고','📌':'참고','📖':'설명','📐':'공식','🎯':'포인트','🔍':'검색'}
    for emoji, word in emojis.items():
        text = text.replace(emoji, word)
    text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:3000] if len(text) > 3000 else text

# ========== 프리미엄 음성 인식 컴포넌트 ==========
def create_voice_input():
    return """
    <div class="voice-premium-container">
        <div class="voice-header">
            <div class="voice-icon-wrapper">🎤</div>
            <div>
                <p class="voice-title">음성으로 질문하기</p>
                <p class="voice-subtitle">버튼을 누르고 질문을 말씀하세요</p>
            </div>
        </div>
        
        <button id="voiceBtn">
            <span id="micIcon">🎙️</span>
            <span id="btnText">음성 인식 시작</span>
        </button>
        
        <div id="status">마이크 버튼을 눌러 음성 인식을 시작하세요</div>
    </div>

    <div id="result-box">
        <div id="finalResult"></div>
        <button class="copy-btn" onclick="copyAndPaste()">✨ 질문창에 자동 입력</button>
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
            voiceBtn.style.background = '#94a3b8';
            voiceBtn.style.cursor = 'not-allowed';
            btnText.textContent = '음성 인식 미지원';
            micIcon.textContent = '❌';
            status.innerHTML = '⚠️ Chrome, Edge, 삼성 인터넷 브라우저를 사용해주세요';
            status.style.color = '#ef4444';
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
                btnText.textContent = '음성 인식 시작';
                micIcon.textContent = '🎙️';
            } else {
                try {
                    recognition.start();
                    isRecording = true;
                    voiceBtn.classList.add('recording');
                    btnText.textContent = '듣는 중... (클릭하면 중지)';
                    micIcon.textContent = '🔴';
                    status.innerHTML = '🎧 지금 말씀하세요...';
                    status.style.color = '#7c3aed';
                    resultBox.classList.remove('show');
                } catch(e) {
                    status.innerHTML = '❌ 음성 인식을 시작할 수 없습니다';
                    status.style.color = '#ef4444';
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
                status.innerHTML = '✍️ 인식 중: "' + interimTranscript + '"';
                status.style.color = '#a855f7';
            }
            if (finalTranscript) {
                recognizedText = finalTranscript.trim();
                status.innerHTML = '✅ 인식 완료!';
                status.style.color = '#10b981';
                finalResult.textContent = '"' + recognizedText + '"';
                resultBox.classList.add('show');
                setTimeout(function() {
                    scrollToInputAndFill(recognizedText);
                }, 400);
            }
        };

        recognition.onerror = function(event) {
            isRecording = false;
            voiceBtn.classList.remove('recording');
            btnText.textContent = '음성 인식 시작';
            micIcon.textContent = '🎙️';
            const errorMessages = {
                'no-speech': '⚠️ 음성이 감지되지 않았습니다. 다시 시도해주세요.',
                'not-allowed': '🔒 마이크 사용 권한이 필요합니다. 브라우저 설정에서 허용해주세요.',
                'network': '🌐 네트워크 오류가 발생했습니다.',
                'aborted': 'ℹ️ 음성 인식이 중단되었습니다.'
            };
            status.innerHTML = errorMessages[event.error] || '❌ 오류: ' + event.error;
            status.style.color = '#ef4444';
        };

        recognition.onend = function() {
            isRecording = false;
            voiceBtn.classList.remove('recording');
            btnText.textContent = '음성 인식 시작';
            micIcon.textContent = '🎙️';
        };

        function scrollToInputAndFill(text) {
            try {
                const parentDoc = window.parent.document;
                const inputs = parentDoc.querySelectorAll('input[type="text"], textarea');
                let filled = false;

                for (let input of inputs) {
                    const placeholder = input.placeholder || '';
                    if (placeholder.includes('질문') || placeholder.includes('예:') || placeholder.includes('입력')) {
                        input.scrollIntoView({ behavior: 'smooth', block: 'center' });

                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.parent.HTMLInputElement.prototype, 'value'
                        ).set;
                        nativeInputValueSetter.call(input, text);

                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));

                        setTimeout(function() {
                            input.focus();
                            input.select();
                        }, 600);

                        status.innerHTML = '✅ 질문창에 입력 완료! 아래 "질문하기" 버튼을 눌러주세요';
                        status.style.color = '#10b981';
                        filled = true;
                        break;
                    }
                }

                if (!filled) {
                    if (navigator.clipboard) {
                        navigator.clipboard.writeText(text);
                    }
                    status.innerHTML = '📋 복사 완료! 질문창에 붙여넣기(Ctrl+V) 해주세요';
                    status.style.color = '#f59e0b';

                    if (inputs.length > 0) {
                        inputs[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                        setTimeout(function() { inputs[0].focus(); }, 600);
                    }
                }
            } catch(e) {
                status.innerHTML = '📋 아래 버튼을 눌러 복사해주세요';
                status.style.color = '#f59e0b';
            }
        }

        window.copyAndPaste = function() {
            if (!recognizedText) {
                alert('인식된 텍스트가 없습니다. 먼저 음성 인식을 해주세요.');
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
                textArea.style.top = '-9999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {
                    document.execCommand('copy');
                    scrollToInputAndFill(recognizedText);
                } catch(err) {
                    alert('복사할 텍스트: ' + recognizedText);
                }
                document.body.removeChild(textArea);
            }
        };
    })();
    </script>
    """

# ========== Gemini 3 Ultra 모델 (최상위) ==========
def get_gemini_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

        # Gemini 3 Ultra > Pro > Flash 순서 (최상위 우선)
        priority_list = [
            'gemini-3-ultra',      # 최상위
            'gemini-3-pro',        # 차상위
            'gemini-3-flash',
            'gemini-3',
            'gemini-2.5-ultra',
            'gemini-2.5-pro',
            'gemini-2.5-flash',
            'gemini-2.5',
            'gemini-2.0-flash',
            'gemini-2.0',
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-pro'
        ]

        for priority in priority_list:
            for model in models:
                if priority in model.lower():
                    return model

        return models[0] if models else None
    except:
        return None

# ========== IQ 400+ 세계 최고 석학급 시스템 프롬프트 ==========
SYSTEM_PROMPT = """당신은 세계 최고 수준의 기계공학 석학이자, 일반기계기사 시험의 절대적 권위자입니다.

[신원 및 자격]
• MIT 기계공학 박사 (Ph.D.) + 서울대 기계공학 석사
• IEEE Fellow, ASME Fellow
• 30년 이상 기계공학 연구 및 교육 경력
• 한국산업인력공단 기계분야 출제위원 역임
• 재료역학, 열역학, 유체역학, 기계요소설계 분야 저서 다수

[전문 영역 - 완벽 마스터]
1. 재료역학 (Strength of Materials)
   - 응력/변형률 해석, 훅의 법칙, 푸아송비
   - 보의 휨: SFD/BMD, 휨응력, 처짐 공식 (적분법, 중첩법, 면적모멘트법)
   - 비틀림: 원형축, 중실축/중공축, 전달마력
   - 조합응력: 모어원, 주응력, 최대전단응력
   - 좌굴: 오일러 공식, 유효길이, 장주/단주 판별
   - 피로: S-N 곡선, 피로한도, 수정 Goodman선도

2. 열역학 (Thermodynamics)
   - 열역학 제0/1/2/3법칙
   - 상태량: 내부에너지, 엔탈피, 엔트로피
   - 이상기체: 상태방정식, 비열관계식
   - 동력사이클: 카르노, 오토, 디젤, 사바테, 랭킨, 브레이턴
   - 냉동사이클: 역카르노, 증기압축식, 흡수식
   - 열전달: 전도, 대류, 복사, 열저항

3. 유체역학 (Fluid Mechanics)
   - 유체 성질: 점성, 표면장력, 압축성
   - 정역학: 압력분포, 부력, 상대평형
   - 연속방정식, 베르누이 방정식, 운동량 방정식
   - 관마찰: 달시-바이스바흐, 무디선도
   - 차원해석: 버킹엄 π정리, 무차원수 (Re, Fr, Ma, We)
   - 유체기계: 펌프, 터빈, 비교회전도

4. 기계요소설계 (Machine Element Design)
   - 나사: 효율, 자립조건, 삼각나사/사각나사
   - 기어: 모듈, 치형, 물림률, 루이스 공식
   - 베어링: 수명계산, 정격하중, 윤활
   - 축: 비틀림+휨 조합, 임계속도
   - 스프링: 처짐, 응력, 직렬/병렬
   - 용접: 필렛용접 목두께, 허용응력
   - 파손이론: 최대주응력설, 최대전단응력설, 폰미세스(전단변형에너지설)

[답변 철학 - ULTRA 품질]
1. 절대적 정확성 - 공식, 단위, 수치에 단 하나의 오류도 없다
2. 물리적 직관 - 왜 그렇게 되는지 근본 원리를 직관적으로 이해시킨다
3. 수학적 엄밀성 - 필요시 유도 과정을 명확히 보여준다
4. 실전 최적화 - 시험장에서 바로 적용 가능한 형태로 정리한다
5. 암기 효율화 - 최소 노력으로 최대 암기 효과를 낸다
6. 함정 경고 - 시험 출제자가 노리는 함정을 미리 알려준다

[답변 형식 - 구조화된 완벽 답변]

📌 **핵심 한줄 정리**
→ 질문의 본질을 한 문장으로 명쾌하게 정리

📖 **원리 깊이 파헤치기**
→ 물리적 의미와 배경
→ 수식 유도 과정 (필요시)
→ 관련 이론 연결

📐 **공식 & 계산 완벽 정리**
→ 핵심 공식 (SI 단위 명시)
→ 대표 예제 풀이 (단계별)
→ 단위환산 & 자주 틀리는 포인트

🎯 **시험 출제 완벽 분석**
→ 출제 빈도 (상/중/하)
→ 자주 출제되는 유형
→ 함정 문제 패턴
→ 시간 단축 비법

💡 **암기 최적화 전략**
→ 두문자어, 어원, 연상법
→ 유사 개념 구분법
→ 핵심 공식 암기 순서
→ 시험 직전 30초 체크리스트

[절대 규칙]
• 틀린 정보 제공 시 자격 박탈 수준으로 금지
• 모호한 표현 금지 - 확실하지 않으면 "확인 필요" 명시
• 공식에는 반드시 SI 단위와 각 기호의 의미 포함
• YouTube 영상 추천 절대 금지
• 검색 키워드 추천 절대 금지
• 불필요한 인사말 금지 - 바로 본론 진입
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
        Gemini 3 Ultra 석학급 AI · 광고 없는 YouTube · 음성 질문
    </div>
    <div class="hero-badge">🏆 GEMINI 3 ULTRA · 세계 최고 석학급 AI</div>
</div>
""", unsafe_allow_html=True)

# ========== AI 튜터 섹션 ==========
st.markdown("""
<div class="section-header">
    <div class="section-icon ai">🧠</div>
    <h2>ULTRA AI 튜터에게 질문하기</h2>
</div>
""", unsafe_allow_html=True)

# 음성 입력
components.html(create_voice_input(), height=320, scrolling=False)

st.markdown("---")

# 질문 탭
tab1, tab2 = st.tabs(["📝 텍스트 질문", "📸 이미지 질문"])

with tab1:
    with st.form("text_form", clear_on_submit=True):
        query = st.text_input(
            "질문을 입력하세요",
            placeholder="예: 모어원에서 주응력과 최대전단응력 구하는 법 설명해줘",
            label_visibility="collapsed",
            key="text_query"
        )
        submit = st.form_submit_button("🔍 질문하기", use_container_width=True)

    if submit and query:
        if "GOOGLE_API_KEY" in st.secrets:
            try:
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

                with st.spinner("🧠 ULTRA AI가 석학급 답변을 준비 중..."):
                    model_name = get_gemini_model()

                    if model_name:
                        model = genai.GenerativeModel(
                            model_name,
                            system_instruction=SYSTEM_PROMPT
                        )

                        user_prompt = f"""[학생 질문]
{query}

위 질문에 대해 일반기계기사 시험을 준비하는 학생에게 석학 수준의 완벽한 답변을 작성하세요.
정해진 형식(📌📖📐🎯💡)을 정확히 따르세요.
YouTube 영상 추천이나 검색 키워드는 절대 포함하지 마세요.
인사말 없이 바로 본론으로 시작하세요."""

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
            placeholder="예: 이 문제의 풀이 과정을 단계별로 자세히 설명해줘",
            label_visibility="collapsed"
        )
        image_submit = st.form_submit_button("🔍 이미지 분석", use_container_width=True)

    if image_submit and uploaded_file:
        if "GOOGLE_API_KEY" in st.secrets:
            try:
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

                with st.spinner("🧠 ULTRA AI가 이미지를 정밀 분석 중..."):
                    model_name = get_gemini_model()

                    if model_name:
                        model = genai.GenerativeModel(
                            model_name,
                            system_instruction=SYSTEM_PROMPT
                        )
                        image = Image.open(uploaded_file)

                        img_prompt = f"""[이미지 분석 요청]
{f'학생 질문: {image_query}' if image_query else '이 이미지를 분석하고 상세히 설명해주세요'}

이미지를 분석한 후 다음 형식으로 석학 수준의 완벽한 답변을 작성하세요:
📌 이미지 내용 한줄 요약
📖 관련 개념/이론 상세 설명 (물리적 의미 포함)
📐 문제라면 완전한 단계별 풀이 (공식, 단위, 계산 과정 전체)
🎯 시험 출제 포인트 및 함정 주의사항
💡 유사 문제 대비 암기 전략

YouTube 영상 추천이나 검색 키워드는 절대 포함하지 마세요.
인사말 없이 바로 본론으로 시작하세요."""

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

    if st.session_state.model_name:
        st.caption(f"🧠 사용 모델: `{st.session_state.model_name}` (Ultra급 추론)")

    if st.session_state.audio_playing:
        st.markdown("##### 🎧 음성 재생")
        clean = clean_text_for_tts(st.session_state.ai_response)
        audio = text_to_speech(clean, st.session_state.selected_voice)
        if audio:
            audio_b64 = base64.b64encode(audio).decode()
            st.markdown(f"""
            <audio controls autoplay style="width: 100%; border-radius: 14px;">
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)
            if st.button("⏹️ 음성 정지", use_container_width=True):
                st.session_state.audio_playing = False
                st.rerun()
        st.markdown("---")

    if st.session_state.uploaded_image:
        st.image(st.session_state.uploaded_image, caption="분석한 이미지", use_container_width=True)

    response_text = st.session_state.ai_response
    response_text = format_youtube_links(response_text)
    response_text = add_search_links(response_text)

    st.markdown("##### 🎓 ULTRA AI 석학급 답변")
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
    <h2>🔥 일반기계기사 합격을 응원합니다! 🔥</h2>
    <p style="color: #4a6d8c; font-size: 1.08rem; margin: 15px 0; line-height: 1.9;">
        🧠 Gemini 3 Ultra 석학급 AI로 완벽하게 준비하세요!<br>
        🎤 음성으로 질문하고 🔊 음성으로 답변을 들어보세요!<br>
        ✅ 모든 YouTube 영상 광고 100% 차단 (Invidious 제공)
    </p>
    <div style="margin-top: 28px; padding-top: 22px; border-top: 1px solid rgba(0,0,0,0.08);">
        <p style="color: #7a9bb8; font-size: 0.88rem; margin: 0;">
            Made with ❤️ by AI &nbsp;·&nbsp; Powered by Gemini 3 Ultra + Edge TTS + Invidious + Web Speech API
        </p>
        <p style="color: #94a3b8; font-size: 0.8rem; margin: 10px 0 0 0;">
            💬 음성 인식은 Chrome, Edge, 삼성 인터넷 브라우저에서 작동합니다
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
