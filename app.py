import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="로그인 파괴왕", page_icon="💣", layout="centered")

st.title("💣 로그인 파괴왕 (완벽 수정판)")
st.error("오류 수정 완료! 이제 코드가 튀어나오지 않습니다.")

st.divider()

# ------------------------------------------------------------------
# 1단계: 버튼 만들기 (코드 튀어나옴 방지 처리)
# ------------------------------------------------------------------
st.subheader("1단계: 아래 검은 버튼을 즐겨찾기로 옮기세요")

# [중요] 자바스크립트 코드를 한 줄로 깔끔하게 압축 (에러 방지)
# 이름이 뭐든 간에 '대화상자'나 '배경' 역할을 하는 건 다 지워버리는 코드입니다.
js_code = "javascript:(function(){document.querySelectorAll('div[class*=\"AuthModal\"],div[class*=\"backdrop\"],div[role=\"dialog\"],div[class*=\"overlay\"]').forEach(e=>e.remove());document.body.style.overflow='auto';})();"

# [중요] HTML과 CSS를 파이썬 f-string과 섞이지 않게 분리해서 작성
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    /* CSS 스타일: 검은색 버튼에 빨간 글씨 */
    .nuke-btn {{
        display: block;
        width: 100%;
        background-color: #000000;
        color: #ff4b4b;
        text-align: center;
        padding: 20px 0;
        text-decoration: none;
        font-family: sans-serif;
        font-weight: 900;
        font-size: 22px;
        border-radius: 15px;
        border: 4px dashed #ff4b4b;
        cursor: grab;
        box-shadow: 0 8px 15px rgba(0,0,0,0.3);
    }}
    .nuke-btn:active {{
        transform: scale(0.98);
        cursor: grabbing;
    }}
    .instruction {{
        text-align: center;
        margin-top: 10px;
        color: #555;
        font-weight: bold;
    }}
</style>
</head>
<body>
    <!-- 버튼 링크에 자바스크립트를 안전하게 넣음 -->
    <a class="nuke-btn" onclick="return false;" href="{js_code}">
        ☢️ 로그인창 폭파 (여기를 드래그!)
    </a>
    <div class="instruction">▲ 클릭하지 말고, 마우스로 꾹~ 잡아서 위로 옮기세요.</div>
</body>
</html>
"""

# 화면에 그리기
components.html(html_content, height=140)

st.divider()

# ------------------------------------------------------------------
# 2단계: 사용하는 법
# ------------------------------------------------------------------
st.subheader("2단계: 실전 테스트")
st.markdown("""
1. 기존에 잘못 만들어진 즐겨찾기는 **삭제**하세요. (우클릭 -> 삭제)
2. 위 **검은색 버튼**을 즐겨찾기 바로 드래그하세요.
3. 젠스파크 로그인 창이 뜨면? **새로 만든 버튼**을 누르세요.
""")

st.link_button("🚀 젠스파크 다시 접속", "https://www.genspark.ai/", type="primary", use_container_width=True)
