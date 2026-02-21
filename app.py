import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

st.set_page_config(page_title="최종 해결", page_icon="🔮", layout="centered")

st.title("🔮 잠금 해제 + 로그인 파괴")
st.error("기존 버튼은 지우세요! 검색창 '잠금'까지 푸는 버전입니다.")

st.divider()

st.subheader("👇 아래 보라색 버튼을 드래그하세요")

# --------------------------------------------------------------------------------
# [로직 설명]
# 1. 'Sign in' 창 삭제 (기존 기능)
# 2. 화면 전체를 막고 있는 투명한 막(Overlay) 삭제
# 3. 비활성화(disabled)된 검색창을 강제로 활성화(enabled)
# 4. 마우스 클릭 금지(pointer-events: none) 걸린 걸 강제로 해제
# --------------------------------------------------------------------------------
raw_js_code = """
(function(){
    // 1. 로그인 창(Sign in) 찾아서 삭제
    var allDivs = document.querySelectorAll('div, section');
    allDivs.forEach(function(el){
        if(el.innerText && (el.innerText.includes('Sign in or sign up') || el.innerText.includes('Continue with Google'))) {
            var parent = el.closest('[style*="fixed"]') || el.closest('[role="dialog"]');
            if(parent) parent.remove();
        }
    });

    // 2. 화면 가리는 투명 막(Backdrop) 무조건 삭제
    var backdrops = document.querySelectorAll('div[class*="backdrop"], div[class*="overlay"]');
    backdrops.forEach(e => e.remove());

    // 3. [핵심] 잠겨있는 검색창(textarea) 강제 잠금 해제
    var inputs = document.querySelectorAll('textarea, input, button');
    inputs.forEach(function(el){
        el.disabled = false;               // 사용 금지 해제
        el.style.pointerEvents = 'auto';   // 클릭 금지 해제
        el.readOnly = false;               // 읽기 전용 해제
    });

    // 4. 스크롤 락 풀기
    document.body.style.overflow = 'auto';
    document.body.style.position = 'static';

    // 5. 검색창에 강제로 커서 갖다 놓기 (바로 엔터 칠 수 있게)
    var mainInput = document.querySelector('textarea');
    if(mainInput) {
        mainInput.focus();
        mainInput.click();
    }
})();
"""

# 안전하게 URL 변환
safe_url = "javascript:" + urllib.parse.quote(raw_js_code)

# HTML 버튼
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    .magic-btn {{
        display: block;
        width: 100%;
        background-color: #8b5cf6; /* 보라색 */
        color: white;
        text-align: center;
        padding: 20px 0;
        text-decoration: none;
        font-family: sans-serif;
        font-weight: 900;
        font-size: 22px;
        border-radius: 12px;
        border: 4px dashed #ffffff;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        cursor: grab;
    }}
    .magic-btn:active {{
        cursor: grabbing;
        background-color: #7c3aed;
    }}
    .desc {{
        text-align: center;
        margin-top: 10px;
        color: #333;
        font-weight: bold;
    }}
</style>
</head>
<body>
    <a class="magic-btn" onclick="return false;" href="{safe_url}">
        🔮 잠금해제 & 폭파 (드래그)
    </a>
    <div class="desc">▲ 초록 버튼은 지우고, 이 보라색 버튼을 쓰세요!</div>
</body>
</html>
"""

components.html(html_content, height=140)

st.divider()

st.link_button("🚀 젠스파크 다시 접속", "https://www.genspark.ai/", type="primary", use_container_width=True)
