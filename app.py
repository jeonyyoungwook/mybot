import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

st.set_page_config(page_title="로그인 파괴왕", page_icon="💣", layout="centered")

st.title("💣 로그인 파괴왕 (글자 추적)")
st.error("기존 즐겨찾기는 삭제하고 다시 등록해주세요!")

st.divider()

st.subheader("1단계: 아래 버튼을 다시 위로 끌고 가세요")

# --------------------------------------------------------------------------------
# [강력해진 로직]
# 1. 화면에 "Sign in"이나 "Google" 글자가 들어간 고정된 창(Fixed)이 있으면 무조건 삭제
# 2. '대화상자' 역할을 하는 모든 요소 삭제
# 3. 화면 덮고 있는 배경(Backdrop) 삭제
# --------------------------------------------------------------------------------
raw_js = """
(function(){
    var count = 0;
    
    // 1. 글자로 찾아서 지우기 (Sign in 글자가 포함된 팝업 찾기)
    var all = document.getElementsByTagName('*');
    for (var i=0; i<all.length; i++) {
        var e = all[i];
        if(e.innerText && (e.innerText.includes('Sign in or sign up') || e.innerText.includes('Continue with Google'))) {
            // 글자를 찾으면, 그 부모 중 고정된(Fixed) 창을 찾아서 삭제
            var parent = e.closest('[style*="fixed"]') || e.closest('[role="dialog"]') || e.closest('.fixed');
            if(parent) { parent.remove(); count++; }
        }
    }

    // 2. 대화상자(Dialog) 속성 가진 놈 강제 삭제
    var dialogs = document.querySelectorAll('[role="dialog"]');
    dialogs.forEach(function(e){ e.remove(); count++; });

    // 3. 화면 덮는 배경(검은색 투명 배경) 삭제
    var divs = document.querySelectorAll('div');
    divs.forEach(function(div){
        var style = window.getComputedStyle(div);
        // 화면에 고정되어 있고(fixed), 전체 화면을 덮는(width>90%) 요소 삭제
        if(style.position === 'fixed' && style.zIndex > 10 && div.clientWidth > window.innerWidth * 0.9) {
            div.remove();
            count++;
        }
    });

    // 4. 스크롤 락 풀기
    document.body.style.overflow = 'auto';
    
    if(count === 0) {
        alert("이미 삭제되었거나 찾을 수 없습니다. (스크롤은 풀렸습니다)");
    }
})();
"""

# 자바스크립트를 URL 주소로 변환 (오류 방지 100%)
safe_js_code = "javascript:" + urllib.parse.quote(raw_js)

html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    .nuke-btn {{
        display: block;
        width: 100%;
        background-color: #ff0000;
        color: white;
        text-align: center;
        padding: 20px 0;
        text-decoration: none;
        font-family: sans-serif;
        font-weight: 900;
        font-size: 24px;
        border-radius: 15px;
        border: 4px dashed yellow;
        cursor: grab;
        box-shadow: 0 5px 0 #8B0000;
    }}
    .nuke-btn:active {{
        box-shadow: none;
        transform: translateY(5px);
        cursor: grabbing;
    }}
    .instruction {{
        text-align: center;
        margin-top: 10px;
        font-weight: bold;
        color: #333;
    }}
</style>
</head>
<body>
    <a class="nuke-btn" onclick="return false;" href="{safe_js_code}">
        ☢️ 이것을 드래그하세요 (NEW)
    </a>
    <div class="instruction">▲ 기존 즐겨찾기는 지우고, 이걸 새로 넣으세요!</div>
</body>
</html>
"""

components.html(html_content, height=140)

st.divider()

st.link_button("🚀 젠스파크 다시 접속", "https://www.genspark.ai/", type="primary", use_container_width=True)
