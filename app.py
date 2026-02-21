import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="로그인 파괴왕", page_icon="🔨", layout="centered")

st.title("🔨 로그인 창 깨부수기 (수정완료)")
st.error("오류를 수정했습니다! 이제 버튼이 제대로 보일 거예요.")

st.divider()

# ------------------------------------------------------------------
# 1단계: 버튼 만들기
# ------------------------------------------------------------------
st.subheader("1단계: 아래 빨간 버튼을 위로 끌고 가세요")

# 자바스크립트 코드 (따옴표 충돌 방지를 위해 아주 단순하게 변경)
# 복잡한 문자열 결합 없이 HTML 안에 직접 넣었습니다.
html_content = """
<!DOCTYPE html>
<html>
<head>
<style>
    .drag-btn {
        display: block;
        width: 100%;
        background-color: #ff2b2b; /* 진한 빨강 */
        color: white;
        text-align: center;
        padding: 20px 0;
        text-decoration: none;
        font-family: sans-serif;
        font-weight: 900;
        font-size: 20px;
        border-radius: 12px;
        border: 4px dashed #ffe600; /* 노란 점선 테두리 */
        cursor: grab;
    }
    .drag-btn:active {
        cursor: grabbing;
    }
</style>
</head>
<body>
    <!-- href 안에 자바스크립트를 안전하게 넣었습니다 (따옴표 문제 해결) -->
    <a class="drag-btn" onclick="return false;" href="javascript:(function(){const m=document.querySelectorAll('div[class*=\'AuthModal\'],div[class*=\'backdrop\']');if(m.length>0){m.forEach(e=>e.remove());document.body.style.overflow='auto';}else{alert('로그인 창이 안 보여요! 😅');}})();">
        💣 이 버튼을 잡고 위로 끌고 가세요! (드래그)
    </a>
</body>
</html>
"""

# 화면에 그리기
components.html(html_content, height=100)

st.info("▲ 위 빨간 버튼을 마우스로 꾹~ 잡아서, 브라우저 주소창 밑(즐겨찾기 바)에 놓으세요.")

st.divider()

# ------------------------------------------------------------------
# 2단계: 실전 사용법
# ------------------------------------------------------------------
st.subheader("2단계: 사용하는 법")
st.markdown("""
1. 아래 **[🚀 젠스파크 열기]** 버튼을 누르세요.
2. 검색하다가 **로그인 창**이 뜨면?
3. 방금 즐겨찾기에 넣어둔 **[💣 이 버튼을...]** 을 누르세요.
4. 로그인 창이 **펑!** 하고 사라집니다.
""")

st.link_button("🚀 젠스파크 열기", "https://www.genspark.ai/", type="primary", use_container_width=True)
