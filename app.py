import streamlit as st

# 페이지 설정
st.set_page_config(page_title="GenSpark 시크릿 접속기", layout="centered")

# 스타일 설정 (버튼 예쁘게 꾸미기)
st.markdown("""
    <style>
    .big-button {
        display: block;
        width: 100%;
        padding: 20px;
        font-size: 24px;
        font-weight: bold;
        color: white !important;
        background-color: #FF4B4B;
        text-align: center;
        text-decoration: none;
        border-radius: 12px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    .big-button:hover {
        background-color: #FF2E2E;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.2);
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# 제목
st.title("🕵️‍♂️ GenSpark 시크릿 접속기")

# 안내 문구
st.markdown("""
<div class="info-box">
    <b>💡 사용 방법 (필독!)</b><br><br>
    웹 보안상 자동으로 '시크릿 모드'를 켜는 것은 불가능합니다.<br>
    대신 아래 <b>빨간 버튼</b>을 이용해서 한 번에 들어갈 수 있습니다.<br><br>
    1. 아래 빨간 버튼에 <b>마우스 오른쪽 클릭</b>을 하세요.<br>
    2. <b>[시크릿 창에서 링크 열기]</b>를 클릭하세요.<br>
       (크롬: 시크릿 창 / 엣지: InPrivate 창)
</div>
""", unsafe_allow_html=True)

# 젠스파크 바로가기 버튼 (우클릭 유도)
st.markdown("""
    <a href="https://www.genspark.ai/" class="big-button" target="_blank">
        🚀 GenSpark 접속 버튼 (여기서 우클릭!)
    </a>
""", unsafe_allow_html=True)

st.write("")
st.write("")
st.caption("※ 이 페이지를 즐겨찾기 해두시면 언제든 편하게 접속할 수 있습니다.")
