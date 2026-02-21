import streamlit as st
import streamlit.components.v1 as components

# 1. 화면 설정 (제목, 아이콘)
st.set_page_config(page_title="GenSpark 마법사", page_icon="🧙‍♂️", layout="centered")

# 2. 제목 (크고 쉽게)
st.markdown("""
<h1 style='text-align: center;'>🧙‍♂️ GenSpark 로그인 없애는 마법</h1>
<p style='text-align: center; font-size: 18px;'>
    확장 프로그램? 복잡한 설정? <b>다 필요 없어요!</b><br>
    마우스로 <b>끌어다 놓으면</b> 끝납니다.
</p>
""", unsafe_allow_html=True)

st.divider()

# --------------------------------------------------------------------------------
# 1단계: 즐겨찾기 바 켜기
# --------------------------------------------------------------------------------
st.markdown("### 1단계: 즐겨찾기 칸 만들기")
st.info("키보드에서 **[Ctrl] + [Shift] + [B]** 키를 동시에 눌러보세요.\n\n주소창 밑에 빈 칸(즐겨찾기 바)이 생겼나요? 이미 있으면 통과!")

# --------------------------------------------------------------------------------
# 2단계: 마법 버튼 만들기 (HTML 컴포넌트 안전하게 구현)
# --------------------------------------------------------------------------------
st.markdown("### 2단계: 아래 빨간 버튼을 위로 끌고 가세요!")

# 자바스크립트 (로그인 창 삭제 코드)
js_code = """javascript:(function(){var m=document.querySelectorAll('div[class*="AuthModal"],div[class*="backdrop"]');if(m.length>0){m.forEach(e=>e.remove());document.body.style.overflow='auto';}else{alert('로그인 창이 없어요! 😄');}})();"""

# 버튼 디자인 (초등학생도 알아보기 쉽게 큰 글씨, 점선 테두리)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{
        margin: 0;
        padding: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
        background-color: transparent;
    }}
    .magic-btn {{
        background-color: #FF4B4B; /* 빨간색 */
        color: white;
        padding: 15px 30px;
        font-size: 20px;
        font-weight: bold;
        text-decoration: none;
        border-radius: 15px;
        border: 3px dashed #FFFFFF;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        font-family: "Malgun Gothic", sans-serif;
        cursor: grab; /* 손모양 커서 */
    }}
    .magic-btn:hover {{
        background-color: #FF2E2E;
        transform: scale(1.05);
    }}
    .magic-btn:active {{
        cursor: grabbing; /* 꽉 쥔 손모양 */
    }}
</style>
</head>
<body>
    <!-- 핵심: href에 자바스크립트 코드를 넣고 드래그하게 함 -->
    <a href='{js_code}' class="magic-btn" onclick="return false;">
        🖱️ 나를 잡고 즐겨찾기 칸에 놓으세요!
    </a>
</body>
</html>
"""

# Streamlit 화면에 HTML 버튼 그리기
components.html(html_code, height=120)

st.caption("▲ 위 빨간 버튼을 **마우스 왼쪽 버튼으로 꾹 누른 채**로, 브라우저 맨 위 즐겨찾기 빈 칸에 놓으세요.")

st.divider()

# --------------------------------------------------------------------------------
# 3단계: 테스트 하기
# --------------------------------------------------------------------------------
st.markdown("### 3단계: 이제 끝! 테스트 해볼까요?")

st.markdown("""
1. 아래 버튼을 눌러 **GenSpark** 사이트로 가세요.
2. 질문을 막 입력하다가 **로그인 창**이 화면을 가리면?
3. 아까 즐겨찾기에 넣어둔 **[🖱️ 나를 잡고...]** 버튼을 클릭하세요.
4. **펑!** 하고 로그인 창이 사라집니다. 🪄
""")

st.link_button("🚀 GenSpark 사이트 열기 (클릭)", "https://www.genspark.ai/", type="primary", use_container_width=True)
