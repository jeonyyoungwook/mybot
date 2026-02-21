import streamlit as st
import urllib.parse

# 1. 페이지 설정
st.set_page_config(page_title="GenSpark 시크릿 접속", page_icon="🕵️", layout="centered")

# 2. 아주 큰 경고문 (사용자가 그냥 클릭하지 않도록)
st.markdown("""
<style>
    .warning-box {
        background-color: #ffe8e8;
        border: 2px solid #ff4b4b;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .big-text {
        font-size: 24px;
        font-weight: bold;
        color: #d80000;
    }
</style>
<div class="warning-box">
    <div class="big-text">🛑 잠깐! 그냥 클릭 금지!</div>
    <p>보안상 자동으로 시크릿 창을 띄울 수 없습니다.<br>
    반드시 <b>[마우스 오른쪽 버튼]</b>을 써야 합니다.</p>
</div>
""", unsafe_allow_html=True)

# 3. 검색어 입력
st.subheader("1️⃣ 검색어 입력")
query = st.text_input("질문", placeholder="예: 오늘 주식 시장 어때?", label_visibility="collapsed")

# 링크 생성
if query:
    encoded_query = urllib.parse.quote(query)
    target_url = f"https://www.genspark.ai/search?query={encoded_query}"
    btn_label = f"🖱️ 여기를 우클릭 하세요! ('{query}')"
else:
    target_url = "https://www.genspark.ai/"
    btn_label = "🖱️ 여기를 우클릭 하세요! (홈페이지)"

st.divider()

# 4. 버튼 및 설명
st.subheader("2️⃣ 버튼 우클릭 → 3번째 메뉴 선택")

# 버튼 (Link Button)
st.link_button(label=btn_label, url=target_url, type="primary", use_container_width=True)

# 상세 설명 (이미지 대신 텍스트로 확실하게)
st.info("""
👆 위 빨간 버튼 위에서 **마우스 오른쪽 버튼**을 누르세요.
메뉴가 뜨면 **[시크릿 창에서 링크 열기]** (또는 InPrivate 창)를 클릭하세요.
""")

st.caption("※ 이렇게 해야 로그인 없이 시크릿 모드로 접속됩니다.")
