import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

st.set_page_config(page_title="최종 해결", page_icon="🧟‍♂️", layout="centered")

st.title("🧟‍♂️ 로그인 창 추적 파괴")
st.error("기존 버튼은 삭제하세요! '글자'를 보고 찾는 방식입니다.")

st.divider()

st.subheader("👇 아래 초록색 버튼을 드래그하세요")

# --------------------------------------------------------------------------------
# [로직 설명]
# ID나 Class 이름은 무시합니다.
# 화면에 있는 모든 요소를 뒤져서 "Sign in" 또는 "Google" 이라는 글자가 있고,
# 화면에 고정(fixed)되어 떠있는 창이라면 무조건 삭제합니다.
# --------------------------------------------------------------------------------
raw_js_code = """
(function(){
    var count = 0;
    
    // 1. 모든 div 태그를 다 가져옵니다.
    var allDivs = document.getElementsByTagName('div');
    
    for(var i=0; i<allDivs.length; i++){
        var el = allDivs[i];
        
        // 2. 글자 내용을 확인합니다. (Sign in or sign up)
        if(el.innerText && (el.innerText.includes('Sign in or sign up') || el.innerText.includes('Continue with Google'))) {
            
            // 3. 글자가 발견되면, 그 요소가 화면에 고정된(fixed) 팝업인지 확인합니다.
            var style = window.getComputedStyle(el);
            // 팝업이거나, 팝업의 부모 요소라면
            if(style.position === 'fixed' || style.zIndex > 50) {
                el.remove(); // 삭제!
                count++;
            }
            // 혹시 모르니 그 부모(껍데기)도 찾아서 지웁니다.
            var parent = el.closest('[role="dialog"]');
            if(parent) { parent.remove(); count++; }
        }
    }

    // 4. 배경 어둡게 하는 막(Backdrop) 제거 (화면 전체를 덮는 투명/검은 창)
    // 이름표 없이, 크기가 화면만큼 큰 fixed 요소를 찾습니다.
    for(var i=0; i<allDivs.length; i++){
        var el = allDivs[i];
        var style = window.getComputedStyle(el);
        if(style.position === 'fixed' && el.offsetWidth >= window.innerWidth) {
            // 단, 메뉴바(헤더)는 지우면 안되니까 z-index가 높은것만
            if(style.zIndex > 10) {
                el.remove();
            }
        }
    }

    // 5. 스크롤 락 풀기
    document.body.style.overflow = 'auto'; 

    if(count > 0) {
        // 성공했으면 조용히 삭제
    } else {
        // 실패했으면 강제로 알림
        console.log("글자를 못 찾았지만 배경은 지웠을 수 있습니다.");
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
    .zombie-btn {{
        display: block;
        width: 100%;
        background-color: #10b981; /* 초록색 */
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
    .zombie-btn:active {{
        cursor: grabbing;
        background-color: #059669;
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
    <a class="zombie-btn" onclick="return false;" href="{safe_url}">
        🧟‍♂️ 로그인창 추적 삭제 (드래그)
    </a>
    <div class="desc">▲ 파란 버튼은 지우고, 이 초록 버튼을 넣으세요!</div>
</body>
</html>
"""

components.html(html_content, height=140)

st.divider()

st.link_button("🚀 젠스파크 다시 접속", "https://www.genspark.ai/", type="primary", use_container_width=True)
