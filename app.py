import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="로그인 파괴왕", page_icon="🔨", layout="centered")

# CSS로 스타일 꾸미기
st.markdown("""
<style>
    .instruction { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }
    .step-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

st.title("🔨 로그인 창 깨부수기")
st.error("젠스파크가 시크릿 모드도 막았습니다! 이제 '깨부수는 버튼'이 필요합니다.")

st.divider()

# ------------------------------------------------------------------
# 1단계: 버튼 만들기 (드래그 앤 드롭)
# ------------------------------------------------------------------
st.markdown("### 1단계: 아래 빨간 버튼을 '즐겨찾기 바'로 끌고 가세요!")
st.info("※ 클릭하지 마세요! 마우스로 꾹 잡아서 위로 옮기세요.")

# 자바스크립트 코드 (로그인 창 삭제 + 배경 흐림 삭제 + 스크롤 풀기)
js_code = """javascript:(function(){
    var targets = document.querySelectorAll('div[class*="AuthModal"], div[class*="backdrop"], div[class*="Modal"]');
    if(targets.length > 0){
        targets.forEach(e => e.remove());
        document.body.style.overflow = 'auto';
    } else {
        alert('삭제할 창이 안 보여요! (이미 지워졌거나 없음)');
    }
})();"""

# HTML 버튼 생성 (드래그 가능하도록)
html_content = f"""
<!DOCTYPE html>
<html>
<body style="margin:0; padding:0; display:flex; justify-content:center;">
    <a href='{js_code}' onclick="return false;" style="
        display: block;
        width: 100%;
        background-color: #FF0000;
        color: white;
        text-align: center;
        padding: 15px;
        text-decoration: none;
        font-family: sans-serif;
        font-weight: 900;
        font-size: 22px;
        border-radius: 10px;
        border: 4px dashed yellow;
        cursor: grab;
    ">
        💣 이 버튼을 잡고 위로 올리세요! (드래그)
    </a>
</body>
</html>
"""

components.html(html_content, height=80)

st.caption("▲ 이 빨간 버튼을 마우스로 잡아서, 브라우저 주소창 밑(즐겨찾기 바)에 놓으세요.")

st.divider()

# ------------------------------------------------------------------
# 2단계: 사용하는 법 (중요)
# ------------------------------------------------------------------
st.markdown("### 2단계: 실전 사용법 (중요!)")

st.markdown("""
1. 아래 **[🚀 젠스파크 열기]** 버튼을 눌러 접속하세요. (우클릭 -> 시크릿 창)
2. 검색하다가 **로그인 창이 화면을 가리면?** 🤬
3. 아까 위에 옮겨둔 **[💣 이 버튼을 잡고...]** 즐겨찾기 버튼을 클릭하세요.
4. **로그인 창이 박살나면서 사라집니다.**
""")

# 접속 버튼
st.link_button("🚀 젠스파크 접속하기 (우클릭 필수)", "https://www.genspark.ai/", type="primary", use_container_width=True)
