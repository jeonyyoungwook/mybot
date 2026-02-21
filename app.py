import streamlit as st
import urllib.parse
import streamlit.components.v1 as components

st.set_page_config(page_title="GenSpark 마법 접속기", page_icon="🪄", layout="centered")

# --- 스타일 설정 ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .highlight { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

st.title("🪄 GenSpark 로그인 제거 마법")
st.caption("확장 프로그램 설치? 필요 없습니다! 즐겨찾기 버튼 하나면 끝.")

st.divider()

# 1. 검색어 입력
st.subheader("1단계: 검색할 내용 입력")
query = st.text_input("질문", placeholder="예: 최신 AI 뉴스 요약해줘", label_visibility="collapsed")

# URL 생성
if query:
    encoded_query = urllib.parse.quote(query)
    target_url = f"https://www.genspark.ai/search?query={encoded_query}"
else:
    target_url = "https://www.genspark.ai/"

# 접속 버튼
st.link_button(f"🚀 GenSpark로 접속하기 (클릭)", target_url, type="primary", use_container_width=True)

st.divider()

# 2. 북마크릿 (핵심 기능)
st.subheader("2단계: 로그인 창이 뜨면?")
st.write("아래 **파란색 버튼**을 마우스로 끌어서, 브라우저 상단 **즐겨찾기(북마크) 바**에 놓으세요.")

# 자바스크립트 코드 (로그인 창 삭제용)
js_code = """javascript:(function(){
    var m = document.querySelectorAll('div[class*="AuthModal"], div[class*="backdrop"]');
    if(m.length > 0){
        m.forEach(e => e.remove());
        document.body.style.overflow = 'auto';
        alert('로그인 창을 삭제했습니다! 🕵️‍♂️');
    } else {
        alert('로그인 창이 감지되지 않았습니다.');
    }
})();"""

# HTML 컴포넌트로 드래그 가능한 링크 생성
# 주의: Streamlit 보안상 markdown으로는 javascript: 링크가 안 먹힐 수 있어 html 컴포넌트 사용
html_content = f"""
<style>
    .bookmarklet {{
        display: block;
        width: 100%;
        background-color: #0068c9;
        color: white;
        text-align: center;
        padding: 15px 0;
        text-decoration: none;
        font-family: sans-serif;
        font-weight: bold;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        cursor: grab;
    }}
    .bookmarklet:hover {{
        background-color: #0053a0;
    }}
    .desc {{
        text-align: center;
        font-size: 12px;
        color: #666;
        margin-top: 5px;
    }}
</style>

<!-- 이 링크를 드래그하게 만드는 것이 핵심 -->
<a href='{js_code}' class="bookmarklet" onclick="return false;">
    🚫 로그인 제거 (이 버튼을 즐겨찾기 바에 드래그!)
</a>
<div class="desc">▲ 클릭하지 말고 마우스로 끌어서 브라우저 상단 주소창 아래에 놓으세요.</div>
"""

components.html(html_content, height=100)

# 3. 사용법 설명 이미지/텍스트
with st.expander("❓ 어떻게 쓰는지 모르겠어요 (사용법 보기)"):
    st.markdown("""
    #### 1️⃣ 세팅하기 (딱 한 번만!)
    1. 브라우저 주소창 아래에 **즐겨찾기 바**가 보이게 하세요. (안 보이면 `Ctrl + Shift + B` 누르기)
    2. 위에 있는 **파란색 [🚫 로그인 제거] 버튼**을 마우스로 클릭한 상태로 끌어서 **즐겨찾기 바**에 놓으세요.
    
    #### 2️⃣ 사용하기
    1. GenSpark에 접속해서 검색하다가 **로그인 창**이 뜨면?
    2. 방금 추가한 즐겨찾기 버튼(**🚫 로그인 제거**)을 클릭하세요.
    3. 펑! 하고 로그인 창이 사라집니다. 🪄
    """)

st.info("💡 꿀팁: 이 방법은 시크릿 모드를 켜지 않아도 작동합니다!")
