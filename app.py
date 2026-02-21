import streamlit as st

st.set_page_config(page_title="최종 해결", page_icon="🛑", layout="centered")

st.title("🛑 최후의 수단 (수동 등록)")
st.error("드래그 기능이 브라우저 보안에 막혔습니다. '복사+붙여넣기'만 살 길입니다.")

st.divider()

# ------------------------------------------------------------------
# 1단계: 코드 복사
# ------------------------------------------------------------------
st.subheader("1단계: 아래 코드를 복사하세요")
st.caption("👇 검은 박스 오른쪽 위 '복사 아이콘' 클릭")

# 이 코드는 젠스파크의 모든 잠금장치를 강제로 풉니다.
js_code = """javascript:(function(){
    /* 1. 알림창으로 작동 확인 */
    console.log("폭파 시작");

    /* 2. 대화상자, 팝업, 오버레이, 백드롭 등 모든 가림막 삭제 */
    var selectors = [
        '[role="dialog"]',
        'div[class*="backdrop"]',
        'div[class*="overlay"]',
        'div[id^="headlessui-portal"]',
        'div[class*="fixed"]'
    ];

    selectors.forEach(function(sel) {
        document.querySelectorAll(sel).forEach(function(el) {
            /* 3. 진짜 로그인 창인지 확인 (Sign in 글자 포함 또는 화면 전체 덮는 것) */
            if(el.innerText.includes('Sign in') || el.innerText.includes('Google') || el.clientWidth > window.innerWidth * 0.9) {
                el.remove();
            }
        });
    });

    /* 4. 잠긴 검색창 강제 해제 (클릭 가능하게 변경) */
    var inputs = document.querySelectorAll('textarea, input');
    inputs.forEach(function(el){
        el.disabled = false;
        el.readOnly = false;
        el.style.pointerEvents = 'auto';
    });
    
    /* 5. 스크롤 풀기 */
    document.body.style.overflow = 'auto';
})();"""

# 코드를 복사하기 좋게 표시
st.code(js_code, language="javascript")

st.divider()

# ------------------------------------------------------------------
# 2단계: 직접 만들기 (이게 100% 됩니다)
# ------------------------------------------------------------------
st.subheader("2단계: 즐겨찾기 직접 만들기 (필독!)")
st.info("이대로만 하시면 무조건 됩니다.")

st.markdown("""
1. 브라우저 맨 위 **즐겨찾기 바 빈 공간**에 마우스 **[우클릭]** 하세요.
2. **[페이지 추가]** (또는 바로가기 추가)를 누르세요.
3. 설정창이 나오면:
   - **이름:** `폭파` (맘대로)
   - **URL(주소):** 👆 위에서 복사한 코드를 **[붙여넣기]** (Ctrl+V) 하세요.
4. **[저장]** 누르세요.
""")

st.divider()

st.subheader("3단계: 테스트")
st.markdown("""
1. 아래 버튼으로 젠스파크 접속
2. 로그인 창 뜨면?
3. 방금 만든 **[폭파]** 즐겨찾기 클릭!
""")

st.link_button("🚀 젠스파크 접속", "https://www.genspark.ai/", type="primary", use_container_width=True)
