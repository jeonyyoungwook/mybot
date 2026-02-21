import streamlit as st
import urllib.parse

# 페이지 설정 (모바일 화면에 맞춤)
st.set_page_config(page_title="GenSpark 접속기", layout="centered")

# 제목
st.title("🚀 GenSpark 빠른 접속")
st.write("질문을 입력하고 버튼을 누르면 바로 이동합니다!")

# 1. 질문 입력창
query = st.text_input(
    "무엇을 검색할까요?", 
    placeholder="예: 오늘 서울 날씨 어때?"
)

# 2. 버튼 생성 로직
if query:
    # 질문이 있으면 -> 검색 결과 페이지로 바로 이동하는 링크 생성
    # 한글 검색어를 URL용 문자로 변환 (인코딩)
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.genspark.ai/search?query={encoded_query}"
    
    st.info("👇 아래 버튼을 누르면 검색 결과가 새 창으로 열립니다.")
    
    # 빨간색 큰 버튼 (질문 포함)
    st.link_button(
        label="🔍 검색 결과 바로 보기 (클릭)", 
        url=search_url,
        type="primary", # 빨간색 강조
        use_container_width=True # 모바일에서 버튼 꽉 차게
    )

else:
    # 질문이 없으면 -> 그냥 홈페이지로 가는 버튼 보여줌
    st.info("👇 질문을 입력하면 바로 검색할 수 있습니다.")
    
    # 회색 기본 버튼 (홈페이지 이동)
    st.link_button(
        label="🏠 GenSpark 홈페이지 열기", 
        url="https://www.genspark.ai/",
        use_container_width=True
    )

st.markdown("---")
st.markdown("""
### 💡 모바일 사용 팁
**시크릿 모드(기록 안 남기기)로 열고 싶다면?**
1. 위 버튼을 **꾹~ 길게 누르세요.**
2. 메뉴가 뜨면 **'시크릿 탭에서 열기'** 또는 **'새 비공개 탭에서 열기'**를 선택하세요.
""")
