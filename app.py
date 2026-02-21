import streamlit as st

# 페이지 설정
st.set_page_config(page_title="로그인 해결사", page_icon="💊", layout="centered")

st.title("💊 젠스파크 로그인 해결사")
st.success("이제 앱이 정상적으로 실행될 겁니다!")
st.info("👇 아래 순서대로 '즐겨찾기'만 수정하면 끝납니다.")

st.divider()

# ------------------------------------------------------------------
# 여기가 진짜 자바스크립트 코드 (즐겨찾기용)
# ------------------------------------------------------------------
st.subheader("1단계: 아래 코드를 복사하세요")
st.caption("오른쪽 위에 있는 📄(복사) 버튼을 누르세요.")

# 젠스파크 로그인 창 강제 삭제 코드
js_code = """javascript:(function(){
    /* 1. 대화상자, 팝업, 배경 제거 */
    const selectors = [
        '[role="dialog"]',
        'div[class*="backdrop"]',
        'div[class*="overlay"]',
        'div[id^="headlessui-portal"]'
    ];
    selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => el.remove());
    });

    /* 2. 글자로 확인사살 ('Sign in' 포함된 고정창 삭제) */
    document.querySelectorAll('div').forEach(div => {
        try {
            if(window.getComputedStyle(div).position === 'fixed') {
                if(div.innerText.includes('Sign in') || div.innerText.includes('Google')) {
                    div.remove();
                }
            }
        } catch(e) {}
    });

    /* 3. 스크롤 잠금 해제 & 검색창 잠금 해제 */
    document.body.style.overflow = 'auto';
    document.body.style.position = 'static';
    
    /* 4. 잠긴 입력창 풀기 */
    const inputs = document.querySelectorAll('textarea, input');
    inputs.forEach(el => {
        el.disabled = false;
        el.style.pointerEvents = 'auto';
    });
})();"""

# 코드를 화면에 보여줌
st.code(js_code, language="javascript")

st.divider()

# ------------------------------------------------------------------
# 즐겨찾기 수정 방법
# ------------------------------------------------------------------
st.subheader("2단계: 즐겨찾기 주소 수정하기")
st.markdown("""
1. 브라우저 맨 위에 만들어둔 **즐겨찾기 버튼** 위에 마우스를 올리세요.
2. 마우스 **[우클릭]** -> **[수정]**을 누르세요.
3. **URL (또는 주소)** 칸에 있는 내용을 **싹 지우세요.**
4. 방금 복사한 코드를 **[붙여넣기]** 하세요.
5. **[저장]** 누르면 끝!
""")

st.divider()

st.link_button("🚀 젠스파크 접속해서 테스트", "https://www.genspark.ai/", type="primary", use_container_width=True)
