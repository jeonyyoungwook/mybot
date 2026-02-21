import streamlit as st
import urllib.parse

# 페이지 설정
st.set_page_config(page_title="GenSpark 시크릿 접속기", layout="centered")

# 제목
st.title("🕵️‍♂️ GenSpark 시크릿 접속기")
st.write("로그인 없이 검색하려면 아래 방법을 꼭 따라해주세요!")

# --- 1. 질문 입력하는 곳 ---
st.markdown("### 1️⃣ 질문 입력")
query = st.text_input(
    "무엇을 검색할까요?", 
    placeholder="예: 오늘 날씨, 맛집 추천 (비워두면 홈으로 이동)"
)

# --- 2. 링크 생성 로직 ---
if query:
    # 한글 검색어를 인터넷 주소용으로 변환
    encoded_query = urllib.parse.quote(query)
    target_url = f"https://www.genspark.ai/search?query={encoded_query}"
    button_text = f"🔍 '{query}' 검색 결과 열기"
else:
    # 질문이 없으면 그냥 홈페이지
    target_url = "https://www.genspark.ai/"
    button_text = "🏠 GenSpark 홈페이지 열기"

# --- 3. 접속 버튼 (여기가 핵심) ---
st.markdown("### 2️⃣ 접속 버튼")
st.caption("👇 아래 버튼을 이용해 시크릿 모드로 들어가세요.")

# 빨간색 강조 버튼
st.link_button(
    label=button_text, 
    url=target_url,
    type="primary", # 빨간색
    use_container_width=True # 버튼 꽉 차게
)

st.divider() # 구분선

# --- 4. 시크릿 모드 사용법 (상세 설명) ---
st.markdown("### 💡 시크릿 모드로 여는 방법")

# 탭을 나눠서 깔끔하게 보여줌
tab1, tab2 = st.tabs(["💻 컴퓨터(PC) 사용법", "📱 핸드폰(모바일) 사용법"])

with tab1:
    st.info("마우스가 있다면 이 방법을 쓰세요!")
    st.markdown("""
    1. 위 **빨간색 버튼** 위로 마우스를 가져가세요.
    2. 버튼 위에서 마우스 **오른쪽 버튼(우클릭)**을 한 번 누르세요.
    3. 메뉴가 뜨면 세 번째 쯤에 있는 **[시크릿 창에서 링크 열기]**를 클릭하세요.
       *(엣지 브라우저는 'InPrivate 창에서 링크 열기' 라고 써있습니다)*
    """)
    # 이해를 돕기 위한 이모티콘 예시
    st.text("🖱️ 우클릭 → 🕶️ 시크릿 창 열기")

with tab2:
    st.success("스마트폰이라면 이 방법을 쓰세요!")
    st.markdown("""
    1. 위 **빨간색 버튼**을 손가락으로 **1초 동안 꾹~ 누르고 계세요.** (떼지 마세요!)
    2. 폰 화면에 메뉴창이 뜹니다.
    3. 메뉴 중에서 **[시크릿 탭에서 열기]** 또는 **[새 시크릿 탭에서 열기]**를 터치하세요.
       *(삼성 인터넷은 '비밀 모드에서 열기' 라고 써있습니다)*
    """)
    # 이해를 돕기 위한 이모티콘 예시
    st.text("👆 꾹 누르기 → 🕶️ 시크릿 탭 열기")
