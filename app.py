import streamlit as st

st.set_page_config(page_title="최종 해결", page_icon="🚨", layout="centered")

st.title("🚨 반응이 없을 때 해결법")
st.error("버튼을 눌러도 아무 반응이 없다면, '주소'가 잘못 들어간 겁니다!")

st.divider()

# ------------------------------------------------------------------
# 1단계: 코드 복사 (알림창 기능 추가)
# ------------------------------------------------------------------
st.subheader("1단계: 아래 코드를 복사하세요")
st.caption("👇 오른쪽 위 📄(복사) 버튼 클릭")

# 이 코드는 실행되자마자 알림창을 띄웁니다.
js_code = """javascript:(function(){
    /* 1. 작동 확인용 알림 (이게 안 뜨면 주소 등록 잘못된 것) */
    alert("⚡ 작동 시작! (확인을 누르면 삭제됩니다)");

    /* 2. 화면 가리는 모든 요소(로그인, 배경) 강제 삭제 */
    var delCount = 0;
    var elements = document.querySelectorAll('body *');
    
    for(var i=0; i<elements.length; i++) {
        var el = elements[i];
        var style = window.getComputedStyle(el);
        
        // 화면에 고정되어 있고(fixed), 'Sign in' 글자가 있거나 화면 전체를 덮는 요소
        if(style.position === 'fixed' && style.zIndex > 10) {
            if(el.innerText.includes('Sign in') || el.innerText.includes('Google') || el.innerText.includes('Apple')) {
                el.remove();
                delCount++;
            }
            // 투명 배경 삭제
            else if(el.clientWidth >= window.innerWidth && el.clientHeight >= window.innerHeight) {
                el.remove();
                delCount++;
            }
        }
    }

    /* 3. 젠스파크 전용 팝업 삭제 (추가) */
    var selectors = ['[role="dialog"]', 'div[id^="headlessui"]'];
    selectors.forEach(function(sel){
        document.querySelectorAll(sel).forEach(function(e){ e.remove(); delCount++; });
    });

    /* 4. 스크롤 및 입력창 잠금 해제 */
    document.body.style.overflow = 'auto';
    var inputs = document.querySelectorAll('textarea, input');
    inputs.forEach(function(el){
        el.disabled = false;
        el.readOnly = false;
        el.style.pointerEvents = 'auto';
    });
    
    /* 5. 결과 알림 */
    if(delCount === 0) {
        alert("⚠️ 삭제할 창을 못 찾았습니다. (이미 지워졌거나 코드가 막힘)");
    }
})();"""

st.code(js_code, language="javascript")

st.divider()

# ------------------------------------------------------------------
# 2단계: 즐겨찾기 수정 (가장 중요!!!)
# ------------------------------------------------------------------
st.subheader("2단계: 즐겨찾기 수정 (필독 ⚠️)")
st.warning("아래 내용을 꼭 확인하세요. 여기가 틀리면 반응이 없습니다.")

st.markdown("""
1. 브라우저 맨 위 **즐겨찾기 버튼(폭파)**에 마우스를 대고 **[우클릭]** -> **[수정]** 누르세요.
2. **URL (또는 주소)** 칸에 있는 걸 **싹 다 지우세요.** (한 글자도 남기지 마세요!)
3. 방금 복사한 코드를 **[붙여넣기]** 하세요.
4. **🔴 중요:** 붙여넣은 맨 앞에 `javascript:` 라는 글자가 잘 있는지 꼭 확인하세요!
   *(가끔 크롬이 보안 때문에 이 글자만 쏙 빼고 붙여넣기 할 때가 있습니다)*
5. **[저장]** 누르세요.
""")

st.divider()

st.success("테스트 방법: 젠스파크에서 버튼을 눌렀을 때 **'⚡ 작동 시작!'** 알림창이 뜨면 성공입니다!")
