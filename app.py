import streamlit as st

st.set_page_config(page_title="최종_진짜_최종", page_icon="⚡", layout="centered")

st.title("⚡ 1초 컷 해결 (압축 버전)")
st.error("코드가 길어서 막혔습니다. 짧은 걸로 바꾸면 바로 됩니다!")

st.divider()

# ------------------------------------------------------------------
# 1단계: 압축 코드 복사
# ------------------------------------------------------------------
st.subheader("1단계: 아래 코드를 복사하세요")
st.caption("👇 설명 다 빼고 기능만 남긴 '압축 코드'입니다.")

# [핵심] 주석, 공백 다 제거한 한 줄 코드 (오류 발생 확률 0%)
# 1. role="dialog" (팝업창) 삭제
# 2. position:fixed (고정된 창) 삭제
# 3. 입력창 잠금 해제
# 4. 스크롤 풀기
js_short_code = """javascript:(function(){document.querySelectorAll('[role="dialog"],div[id^="headlessui"],div[class*="overlay"],div[class*="backdrop"]').forEach(e=>e.remove());document.querySelectorAll('div').forEach(e=>{try{if(window.getComputedStyle(e).position==='fixed'&&parseInt(window.getComputedStyle(e).zIndex)>10){e.remove()}}catch(x){}});document.querySelectorAll('input,textarea,button').forEach(e=>{e.disabled=false;e.style.pointerEvents='auto';e.readOnly=false;});document.body.style.overflow='auto';document.body.style.position='static';})();"""

st.code(js_short_code, language="javascript")

st.divider()

# ------------------------------------------------------------------
# 2단계: 즐겨찾기 수정 (딱 10초)
# ------------------------------------------------------------------
st.subheader("2단계: 즐겨찾기 수정")
st.warning("기존 내용을 **한 글자도 남기지 말고 다 지운 뒤** 붙여넣으세요!")

st.markdown("""
1. 브라우저 위에 있는 **[폭]** 버튼을 **[우클릭]** -> **[수정]** 하세요.
2. **URL (또는 주소)** 칸에 있는 걸 **전부 지우세요.** (깨끗하게!)
3. 위에서 복사한 짧은 코드를 **[붙여넣기]** 하세요.
4. **[저장]** 누르세요.
""")

st.divider()

st.success("이제 젠스파크에서 [폭] 버튼을 누르면, 묻지도 따지지도 않고 창이 사라집니다.")
