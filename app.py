import streamlit as st
import urllib.parse

st.set_page_config(page_title="GenSpark 마법 접속기", page_icon="🪄", layout="centered")

st.title("🪄 GenSpark 로그인 제거기")
st.markdown("확장 프로그램 없이, **즐겨찾기(북마크)**를 이용해 로그인 창을 뚫는 방법입니다.")

st.divider()

# --- 1단계: 검색 기능 ---
st.subheader("Step 1. 검색하고 접속하기")
query = st.text_input("질문 입력", placeholder="예: 최신 AI 트렌드 알려줘")

if query:
    encoded_query = urllib.parse.quote(query)
    target_url = f"https://www.genspark.ai/search?query={encoded_query}"
else:
    target_url = "https://www.genspark.ai/"

st.link_button("🚀 GenSpark 접속 (새창)", target_url, type="primary", use_container_width=True)

st.divider()

# --- 2단계: 북마크 만들기 (핵심) ---
st.subheader("Step 2. '로그인 제거' 버튼 만들기")
st.info("이 설정은 딱 한 번만 하면 평생 쓸 수 있습니다!")

st.markdown("""
**👇 아래 순서대로 따라하세요:**

1. 브라우저 상단 주소창 아래 빈 곳에 마우스를 대고 **우클릭** 하세요.
2. **[페이지 추가]** 또는 **[바로가기 추가]**를 누르세요.
3. **이름** 칸에는: `로그인 제거` 라고 쓰세요.
4. **URL(주소)** 칸에는: 아래 **검은 박스 안의 코드**를 복사해서 붙여넣으세요.
""")

# 자바스크립트 코드 (한 줄로 압축)
js_code = """javascript:(function(){const m=document.querySelectorAll('div[class*="AuthModal"],div[class*="backdrop"]');if(m.length>0){m.forEach(e=>e.remove());document.body.style.overflow='auto';}else{alert('로그인 창이 안 보입니다!');}})();"""

# 코드 복사하기 쉽게 보여주기
st.code(js_code, language="javascript")
st.caption("▲ 위 코드를 복사해서 북마크의 'URL' 또는 '주소' 칸에 넣으세요.")

st.divider()

# --- 3단계: 사용법 ---
st.subheader("Step 3. 사용하는 법")
st.success("""
1. GenSpark에서 검색하다가 **로그인 창**이 화면을 가리면?
2. 방금 만든 **[로그인 제거] 북마크**를 클릭하세요.
3. 로그인 창이 즉시 사라집니다! 🎉
""")

with st.expander("동작 원리가 뭔가요?"):
    st.write("""
    이 코드는 '북마크릿(Bookmarklet)'이라고 부릅니다. 
    북마크를 누르는 순간, 페이지에 있는 '로그인 팝업(AuthModal)' 요소를 찾아서 
    강제로 삭제(remove)하는 자바스크립트 명령을 내리는 원리입니다.
    """)
