import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="로그인 파괴왕", page_icon="💣", layout="centered")

st.title("💣 로그인 핵폭탄 (진짜_최종)")
st.error("기존 즐겨찾기는 삭제하세요! 이게 진짜입니다.")

st.divider()

# ------------------------------------------------------------------
# 강력해진 자바스크립트 (이름 상관없이 화면 가리면 삭제)
# ------------------------------------------------------------------
st.subheader("1단계: 아래 버튼을 다시 위로 끌고 가세요")

# 1. role="dialog" (대화상자) 무조건 삭제
# 2. position: fixed (화면에 고정된 창) 중에서 'Sign in' 글자 있으면 삭제
# 3. headlessui (젠스파크가 쓰는 기술) ID가 있으면 삭제
js_code = """javascript:(function(){
    var count = 0;
    
    /* 1. 대화상자(Dialog) 속성 가진 놈 다 찾기 */
    var dialogs = document.querySelectorAll('[role="dialog"]');
    dialogs.forEach(function(e){ e.remove(); count++; });

    /* 2. 젠스파크 전용 팝업 코드 찾기 (headlessui) */
    var portals = document.querySelectorAll('div[id^="headlessui-portal"]');
    portals.forEach(function(e){ e.remove(); count++; });

    /* 3. 화면 고정된 놈들 중에 'Sign in' 글자 포함되면 강제 삭제 */
    var divs = document.querySelectorAll('div');
    divs.forEach(function(div){
        var style = window.getComputedStyle(div);
        if(style.position === 'fixed' && style.zIndex > 10) {
            if(div.innerText.includes('Sign in') || div.innerText.includes('Google')) {
                div.remove();
                count++;
            }
        }
    });

    /* 4. 스크롤 락 풀기 */
    document.body.style.overflow = 'auto';
    document.body.style.position = 'static';

    /* 결과 알림 */
    if(count > 0) { 
        console.log('로그인 창 삭제 완료'); 
    } else {
        /* 만약 아무것도 안 지워졌으면, 백그라운드 강제 삭제 시도 */
        document.querySelectorAll('div[class*="backdrop"]').forEach(e => e.remove());
        document.querySelectorAll('div[class*="overlay"]').forEach(e => e.remove());
    }
})();"""

# 따옴표 충돌 방지를 위해 HTML을 조심스럽게 작성
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    .nuke-btn {{
        display: block;
        width: 100%;
        background-color: #000000; /* 검은색 (핵폭탄 느낌) */
        color: #ff0000; /* 빨간 글씨 */
        text-align: center;
        padding: 20px 0;
        text-decoration: none;
        font-family: sans-serif;
        font-weight: 900;
        font-size: 24px;
        border-radius: 15px;
        border: 5px solid #ff0000;
        cursor: grab;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }}
    .nuke-btn:active {{
        transform: scale(0.98);
        cursor: grabbing;
    }}
    .desc {{
        text-align: center;
        margin-top: 10px;
        font-weight: bold;
        color: #333;
    }}
</style>
</head>
<body>
    <a class="nuke-btn" onclick="return false;" href='{js_code}'>
        ☢️ 로그인창 폭파시키기 (드래그)
    </a>
    <div class="desc">▲ 1. 이 검은 버튼을 마우스로 잡으세요.<br>2. 즐겨찾기 바에 다시 놓으세요.</div>
</body>
</html>
"""

components.html(html_content, height=140)

st.divider()

st.subheader("2단계: 확인 사살")
st.markdown("""
1. 브라우저 즐겨찾기에 있는 **기존 빨간 버튼은 지우세요.** (우클릭 -> 삭제)
2. 방금 올린 **검은색 [☢️ 로그인창 폭파...] 버튼**을 쓰셔야 합니다.
3. 젠스파크 로그인 창이 뜨면? **검은 버튼**을 누르세요.
""")

st.link_button("🚀 젠스파크 다시 접속", "https://www.genspark.ai/", type="primary", use_container_width=True)
