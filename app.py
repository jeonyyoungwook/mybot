import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="GenSpark 초간단 해제기", page_icon="⚡", layout="centered")

st.title("⚡ GenSpark 로그인 해제 (초간단)")
st.caption("복잡한 설정? 다 필요 없습니다. 마우스로 끌어다 놓으세요!")

st.divider()

# ------------------------------------------------------------
# 1단계: 준비물 (즐겨찾기 바 켜기)
# ------------------------------------------------------------
st.subheader("1단계: 키보드에서 [Ctrl] + [Shift] + [B] 누르기")
st.info("브라우저 상단에 '즐겨찾기 바(북마크 바)'가 나타나야 합니다. 이미 있으면 패스!")

# ------------------------------------------------------------
# 2단계: 드래그 앤 드롭 버튼 (핵심 기술)
# ------------------------------------------------------------
st.subheader("2단계: 아래 파란 버튼을 위로 끌어다 놓으세요")

# 자바스크립트 코드 (로그인 창 삭제 + 스크롤 풀기)
js_code = """javascript:(function(){
    var m = document.querySelectorAll('div[class*="AuthModal"], div[class*="backdrop"]');
    if(m.length > 0){
        m.forEach(e => e.remove());
        document.body.style.overflow = 'auto';
    } else {
        alert('삭제할 로그인 창이 없습니다.');
    }
})();"""

# HTML/CSS로 '드래그 전용 버튼' 만들기
# onclick="return false;"를 넣어서 클릭해도 아무 반응 없게 만듦 (오직 드래그만 가능하도록)
html_content = f"""
<style>
    .drag-btn {{
        display: block;
        width: 100%;
        background-color: #3b82f6; /* 밝은 파란색 */
        color: white;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-radius: 12px;
        text-decoration: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        cursor: grab; /* 마우스 커서를 손모양으로 */
        border: 2px dashed #ffffff;
    }}
    .drag-btn:active {{
        cursor: grabbing;
        background-color: #2563eb;
    }}
    .instruction {{
        text-align: center;
        margin-top: 10px;
        color: #666;
        font-size: 14px;
    }}
</style>

<a href='{js_code}' class="drag-btn" onclick="return false;">
    🖱️ 이 버튼을 잡고, 즐겨찾기 바에 놓으세요!
</a>
<div class="instruction">⚠️ 클릭하지 마세요! <b>마우스 왼쪽 버튼을 꾹 누른 채로</b> 위로 끌고 가세요.</div>
"""

components.html(html_content, height=120)

st.divider()

# ------------------------------------------------------------
# 3단계: 테스트 및 사용
# ------------------------------------------------------------
st.subheader("3단계: 이제 사용해볼까요?")

st.markdown("""
1. 아래 버튼을 눌러 **GenSpark**에 접속하세요.
2. 검색하다가 **로그인 창**이 뜨면?
3. 방금 즐겨찾기 바에 가져다 놓은 **[🖱️ 이 버튼을 잡고...]** 버튼을 누르세요.
4. 로그인 창이 **펑!** 하고 사라집니다.
""")

st.link_button("🚀 GenSpark 접속해서 테스트하기", "https://www.genspark.ai/", type="primary", use_container_width=True)
