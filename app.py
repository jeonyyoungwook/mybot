import streamlit as st

st.set_page_config(page_title="필살기", page_icon="⚡", layout="centered")

st.title("⚡ 최후의 필살기 (F12)")
st.error("즐겨찾기가 안 되면, 직접 명령을 내리면 됩니다. 이건 무조건 뚫립니다.")

st.divider()

# ------------------------------------------------------------------
# 1단계: 명령 코드 복사
# ------------------------------------------------------------------
st.subheader("1단계: 아래 코드를 복사하세요")
st.caption("👇 오른쪽 위 📄(복사) 버튼 클릭")

# 이 코드는 젠스파크의 방어막을 강제로 해제하는 자바스크립트 명령어입니다.
# 앞뒤에 javascript: 같은 거 필요 없습니다. 그냥 순수 코드입니다.
console_code = """
document.querySelectorAll('[role="dialog"],div[class*="backdrop"],div[class*="overlay"],div[id^="headlessui"]').forEach(e=>e.remove());
document.querySelectorAll('input,textarea,button').forEach(e=>{e.disabled=false;e.style.pointerEvents='auto';e.readOnly=false;});
document.body.style.overflow='auto';
"""

st.code(console_code, language="javascript")

st.divider()

# ------------------------------------------------------------------
# 2단계: F12 개발자 도구 사용법
# ------------------------------------------------------------------
st.subheader("2단계: 젠스파크 화면에서 따라하세요")
st.info("설치 같은 거 없습니다. 키보드만 있으면 됩니다.")

st.markdown("""
1. **젠스파크 접속:** 로그인 창이 떠서 멈춘 화면으로 가세요.
2. **키보드 [F12] 키 누르기:**
   - 화면 오른쪽에 이상한 영어창(개발자 도구)이 뜹니다.
   - (노트북이면 `Fn + F12` 일 수도 있습니다)
3. **[Console] 탭 클릭:**
   - 영어창 맨 위에 `Elements`, `Console`, `Sources`... 메뉴가 있습니다.
   - 그 중에서 **[Console] (또는 콘솔)** 을 클릭하세요.
4. **붙여넣기 후 엔터:**
   - 커서가 깜빡이는 곳에 **방금 복사한 코드**를 붙여넣기(`Ctrl+V`) 하세요.
   - **[Enter]** 키를 치세요.
5. **끝!**
   - 로그인 창이 즉시 사라지고 검색이 됩니다.
""")

st.divider()

st.link_button("🚀 젠스파크 열고 F12 눌러보기", "https://www.genspark.ai/", type="primary", use_container_width=True)
