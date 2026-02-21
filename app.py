import streamlit as st
import streamlit.components.v1 as components

# 1. 화면 설정
st.set_page_config(page_title="GenSpark 마법사", page_icon="🧙‍♂️", layout="centered")

# 2. 제목 (아주 쉽게)
st.title("🧙‍♂️ 로그인 없애는 마법")
st.markdown("### 👇 아래 순서대로 3가지만 따라하세요. 10초면 끝!")

st.divider()

# ----------------------------------------------------------------------
# 1단계: 즐겨찾기 바 켜기
# ----------------------------------------------------------------------
st.subheader("1단계: 키보드 누르기")
st.info("키보드에서 **[Ctrl] + [Shift] + [B]** 를 동시에 누르세요.")
st.caption("👉 주소창 밑에 '빈 줄(즐겨찾기 바)'이 생기면 성공!")

# ----------------------------------------------------------------------
# 2단계: 드래그 버튼 (오류 수정됨)
# ----------------------------------------------------------------------
st.subheader("2단계: 빨간 버튼을 위로 끌고 가기")

# 자바스크립트 코드를 안전하게 넣기 위해 f-string 대신 직접 문자열 결합을 사용합니다.
# 이렇게 하면 화면에 코드가 글로 나오는 오류가 사라집니다.
html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
<style>
    .magic-button {
        display: block;
        width: 100%;
        background-color: #ff2b2b;
        color: white;
        text-align: center;
        padding: 15px 0;
        font-family: 'Malgun Gothic', sans-serif;
        font-size: 20px;
        font-weight: 900;
        text-decoration: none;
        border-radius: 12px;
        border: 4px dashed yellow;
        cursor: grab;
        box-shadow: 0 5px 0 #b30000;
    }
    .magic-button:active {
        box-shadow: none;
        transform: translateY(5px);
        cursor: grabbing;
    }
    p {
        text-align: center;
        color: #555;
        margin-top: 5px;
        font-size: 14px;
        font-weight: bold;
    }
</style>
</head>
<body>
    <!-- 여기가 핵심: href 안에 자바스크립트를 한 줄로 넣음 -->
    <a class="magic-button" onclick="return false;" href="javascript:(function(){const m=document.querySelectorAll('div[class*=\'AuthModal\'],div[class*=\'backdrop\']');if(m.length>0){m.forEach(e=>e.remove());document.body.style.overflow='auto';}else{alert('지금은 로그인 창이 없어요! 😅');}})();">
        🖱️ 나를 잡고 즐겨찾기 바에 놓으세요!
    </a>
    <p>▲ 클릭하지 말고, 마우스로 꾹~ 잡아서 위로 옮기세요!</p>
</body>
</html>
"""

# 높이를 충분히 주어 잘리지 않게 함
components.html(html_code, height=120)

st.divider()

# ----------------------------------------------------------------------
# 3단계: 테스트
# ----------------------------------------------------------------------
st.subheader("3단계: 이제 끝! 테스트 해보세요")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    1. 아래 버튼을 눌러 **GenSpark**에 들어갑니다.
    2. 질문을 하다가 **로그인 창**이 뜨면?
    3. 아까 옮겨둔 **[🖱️ 나를 잡고...]** 버튼을 누르세요.
    4. **펑!** 하고 로그인 창이 사라집니다. 🪄
    """)

with col2:
    st.link_button("🚀 GenSpark 열기", "https://www.genspark.ai/", type="primary", use_container_width=True)
