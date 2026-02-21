import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="최종 해결", page_icon="🔓", layout="centered")

st.title("🔓 젠스파크 먹통 해결사")
st.success("이제 검색 버튼이 안 눌리는 문제까지 해결됩니다!")
st.info("👇 아래 검은 박스에 있는 코드를 복사해서 즐겨찾기를 수정하세요.")

st.divider()

# ------------------------------------------------------------------
# [핵심] 1단계: 복사할 코드 (검색창 잠금 해제 기능 포함)
# ------------------------------------------------------------------
st.subheader("1단계: 아래 코드를 복사하세요")
st.caption("오른쪽 위에 있는 📄(복사) 아이콘을 누르면 한 번에 복사됩니다.")

# 이 코드는 로그인 창 삭제 + 얼어붙은 검색 버튼 녹이기 기능이 들어있습니다.
final_js_code = """javascript:(function(){
    /* 1. 화면 가리는 창(로그인/배경) 삭제 */
    var selectors = [
        '[role="dialog"]',
        'div[class*="backdrop"]',
        'div[class*="overlay"]',
        'div[id^="headlessui-portal"]',
        'div[class*="fixed"]'
    ];
    selectors.forEach(function(sel) {
        document.querySelectorAll(sel).forEach(function(el) {
            /* 'Sign in' 글자가 있거나 화면 전체를 덮는 투명창이면 삭제 */
            if(el.innerText.includes('Sign in') || el.innerText.includes('Google') || el.clientWidth >= window.innerWidth) {
                el.remove();
            }
        });
    });

    /* 2. [중요] 먹통된 검색창 & 버튼 강제 활성화 */
    var frozen = document.querySelectorAll('textarea, input, button, div[role="button"]');
    frozen.forEach(function(el){
        el.disabled = false;               /* 사용 금지 해제 */
        el.readOnly = false;               /* 읽기 전용 해제 */
        el.style.pointerEvents = 'auto';   /* 마우스 클릭 허용 */
        el.style.cursor = 'text';          /* 커서 모양 복구 */
    });

    /* 3. 스크롤 풀기 */
    document.body.style.overflow = 'auto';
    document.body.style.position = 'static';

    /* 4. 검색창에 커서 넣고 클릭 신호 보내기 */
    var searchBox = document.querySelector('textarea');
    if(searchBox) {
        searchBox.focus();
        searchBox.click();
    }
})();"""

# 화면에 코드 표시 (복사 버튼 포함)
st.code(final_js_code, language="javascript")

st.divider()

# ------------------------------------------------------------------
# 2단계: 즐겨찾기 수정 방법
# ------------------------------------------------------------------
st.subheader("2단계: 즐겨찾기 주소 수정하기")
st.markdown("""
1. 브라우저 맨 위에 있는 **즐겨찾기 버튼**에 마우스를 올리세요.
2. 마우스 **[우클릭]** -> **[수정]**을 누르세요.
3. **URL (또는 주소)** 칸에 있는 내용을 **전부 지우세요.**
4. 방금 복사한 코드를 **[붙여넣기]** (Ctrl+V) 하세요.
5. **[저장]** 누르면 끝!
""")

st.divider()

st.link_button("🚀 젠스파크 접속해서 테스트", "https://www.genspark.ai/", type="primary", use_container_width=True)
