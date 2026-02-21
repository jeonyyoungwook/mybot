import streamlit as st

st.set_page_config(page_title="진짜_최종_해결", page_icon="🔓", layout="centered")

st.title("🔓 젠스파크 강제 잠금해제")
st.error("반응이 없다면 '붙여넣기' 할 때 앞글자가 지워진 겁니다!")

st.divider()

# ------------------------------------------------------------------
# 1단계: 코드 복사 (가장 강력한 한 줄 코드)
# ------------------------------------------------------------------
st.subheader("1단계: 아래 코드를 복사하세요")
st.caption("👇 오른쪽 위 📄 아이콘 클릭")

# [원리]
# 1. CSS를 강제로 주입해서 모든 클릭 방지(pointer-events: none)를 무력화함 (* {pointer-events: auto !important})
# 2. 'Sign in' 글자가 포함된 팝업창을 찾아서 삭제함
# 3. 스크롤 락을 품
js_final = """javascript:(function(){var s=document.createElement('style');s.innerHTML='* { pointer-events: auto !important; user-select: auto !important; cursor: auto !important; } body { overflow: auto !important; }';document.head.appendChild(s);var all=document.getElementsByTagName('*');for(var i=0;i<all.length;i++){if(all[i].innerText&&(all[i].innerText.includes('Sign in')||all[i].innerText.includes('Unlock'))){var p=all[i].closest('[style*="fixed"]')||all[i].closest('.fixed')||all[i].closest('[role="dialog"]');if(p)p.remove();}}document.querySelectorAll('div[class*="backdrop"],div[class*="overlay"]').forEach(e=>e.remove());})();"""

st.code(js_final, language="javascript")

st.divider()

# ------------------------------------------------------------------
# 2단계: 즐겨찾기 수정 (여기가 제일 중요!!!)
# ------------------------------------------------------------------
st.subheader("2단계: 즐겨찾기 수정 (실수하기 쉬운 곳)")
st.warning("🚨 붙여넣기 후, 맨 앞을 꼭 확인해야 합니다!")

st.markdown("""
1. 브라우저 위 **[폭]** 버튼(또는 기존 버튼)에 대고 **[우클릭]** -> **[수정]** 누르세요.
2. **URL (또는 주소)** 칸에 있는 걸 **전부 지우세요.**
3. 방금 복사한 코드를 **[붙여넣기]** (Ctrl+V) 하세요.
4. **🔴 [확인 필수] 맨 앞에 `javascript:` 글자가 있나요?**
   - 만약 `(function...` 으로 시작한다면? -> **지워진 겁니다!**
   - 맨 앞에 직접 `javascript:` 라고 타이핑해서 적어주세요.
5. **[저장]** 누르세요.
""")

st.divider()

st.success("이제 젠스파크에서 버튼을 누르면, 화면이 깜빡하면서 클릭이 될 겁니다.")
