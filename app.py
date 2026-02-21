import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

st.set_page_config(page_title="최종 해결", page_icon="🚑", layout="centered")

st.title("🚑 로그인 창 강제 삭제")
st.error("기존 즐겨찾기는 삭제하세요! 안 되는 버튼입니다.")

st.divider()

st.subheader("👇 아래 파란 버튼을 다시 드래그하세요")

# --------------------------------------------------------------------------------
# 자바스크립트 로직 (젠스파크 전용 'headlessui' ID 찾기)
# --------------------------------------------------------------------------------
raw_js_code = """
(function(){
    // 1. 작동 확인용 알림 (이게 안 뜨면 즐겨찾기 등록이 잘못된 것)
    alert("삭제를 시작합니다! (확인 누르면 삭제됨)");

    var count = 0;

    // [핵심] 젠스파크는 'headlessui-portal-root'라는 ID를 씁니다. 이걸 찾아서 통째로 날립니다.
    var roots = document.querySelectorAll('div[id^="headlessui-portal-root"]');
    roots.forEach(function(r){ r.remove(); count++; });

    // [보조] 혹시 몰라 'dialog' 역할하는 놈들도 다 날립니다.
    var dialogs = document.querySelectorAll('[role="dialog"]');
    dialogs.forEach(function(d){ d.remove(); count++; });

    // [마무리] 스크롤 락 풀기
    document.body.style.overflow = 'auto'; 
    document.body.style.position = 'static';

    if(count === 0) {
        alert("⚠️ 삭제할 대상을 못 찾았습니다. 코드가 막힌 것 같습니다.");
    } else {
        console.log("삭제 완료");
    }
})();
"""

# 코드를 URL 형식으로 완벽하게 변환 (오류 방지)
safe_url = "javascript:" + urllib.parse.quote(raw_js_code)

# HTML 버튼
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    .final-btn {{
        display: block;
        width: 100%;
        background-color: #2563eb; /* 진한 파랑 */
        color: white;
        text-align: center;
        padding: 20px 0;
        text-decoration: none;
        font-family: sans-serif;
        font-weight: 900;
        font-size: 22px;
        border-radius: 12px;
        border: 4px solid #ffffff;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        cursor: grab;
    }}
    .final-btn:active {{
        cursor: grabbing;
        background-color: #1d4ed8;
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
    <a class="final-btn" onclick="return false;" href="{safe_url}">
        💉 로그인창 뿌리 뽑기 (드래그)
    </a>
    <div class="desc">▲ 기존 버튼은 지우고, 이 파란 버튼을 새로 넣으세요!</div>
</body>
</html>
"""

components.html(html_content, height=140)

st.divider()

st.info("""
**[테스트 방법]**
1. 젠스파크 로그인 창이 뜬 상태에서
2. 방금 옮긴 **파란색 즐겨찾기 버튼**을 누르세요.
3. 화면 중앙에 **"삭제를 시작합니다!"** 라는 알림창이 뜰 겁니다.
4. [확인]을 누르면 로그인 창이 사라집니다.
""")

st.link_button("🚀 젠스파크 다시 접속", "https://www.genspark.ai/", type="primary", use_container_width=True)
