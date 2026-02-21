import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="로그인 파괴왕", page_icon="💣", layout="centered")

st.title("💣 로그인 파괴왕 (오류 해결)")
st.success("이제 코드가 튀어나오지 않습니다. 깔끔한 버튼이 나옵니다!")

st.divider()

# ------------------------------------------------------------------
# 1단계: 버튼 만들기 (따옴표 충돌 완벽 해결)
# ------------------------------------------------------------------
st.subheader("1단계: 아래 검은 버튼을 즐겨찾기로 옮기세요")

# [핵심 수정] 자바스크립트 안에 큰따옴표(")를 아예 없애고, 작은따옴표(')만 사용했습니다.
# 이렇게 하면 HTML의 href="..." 와 충돌하지 않습니다.
js_code = "javascript:(function(){var m=document.querySelectorAll('div[class*=\\'AuthModal\\'],div[class*=\\'backdrop\\'],div[role=\\'dialog\\']');if(m.length>0){m.forEach(e=>e.remove());document.body.style.overflow=\\'auto\\';}else{alert(\\'로그인 창이 안 보여요!\\');}})();"

# HTML 코드를 파이썬 f-string 대신, 단순 문자열로 작성하여 {} 오류도 방지합니다.
html_content = """
<!DOCTYPE html>
<html>
<head>
<style>
    .nuke-btn {
        display: block;
        width: 100%;
        background-color: #000000;
        color: #ff4b4b;
        text-align: center;
        padding: 20px 0;
        text-decoration: none;
        font-family: sans-serif;
        font-weight: 900;
        font-size: 20px;
        border-radius: 15px;
        border: 4px dashed #ff4b4b;
        cursor: grab;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .nuke-btn:active {
        transform: scale(0.98);
        cursor: grabbing;
    }
    .instruction {
        text-align: center;
        margin-top: 10px;
        color: #555;
        font-weight: bold;
    }
</style>
</head>
<body>
    <!-- href 안에 위에서 만든 js_code를 넣습니다. -->
    <a class="nuke-btn" onclick="return false;" href="JS_CODE_HERE">
        ☢️ 로그인창 폭파 (여기를 드래그!)
    </a>
    <div class="instruction">▲ 클릭하지 말고, 마우스로 꾹~ 잡아서 즐겨찾기 바에 놓으세요.</div>
</body>
</html>
"""

# 문자열 치환으로 코드 삽입 (가장 안전한 방법)
html_content = html_content.replace("JS_CODE_HERE", js_code)

# 화면에 그리기
components.html(html_content, height=140)

st.divider()

# ------------------------------------------------------------------
# 2단계: 사용법
# ------------------------------------------------------------------
st.subheader("2단계: 사용법")
st.markdown("""
1. 기존에 잘못된 즐겨찾기 버튼은 **우클릭해서 삭제**하세요.
2. 위 **검은 버튼**을 즐겨찾기 바로 드래그하세요.
3. 젠스파크 로그인 창이 뜨면 **새로 만든 버튼**을 누르세요.
""")

st.link_button("🚀 젠스파크 다시 접속", "https://www.genspark.ai/", type="primary", use_container_width=True)
