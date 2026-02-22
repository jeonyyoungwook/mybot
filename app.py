import streamlit as st
import google.generativeai as genai

# 페이지 기본 설정
st.set_page_config(
    page_title="일반기계기사 학습 가이드",
    page_icon="⚙️",
    layout="centered"
)

# 제목 및 소개
st.title("⚙️ 일반기계기사 독학 가이드 🎬")

# --------------------------------------------------------------------------------
# [Gemini AI 검색 기능 추가]
# --------------------------------------------------------------------------------
st.markdown("### 🤖 AI 튜터에게 질문하기")
st.caption("궁금한 기계 용어나 개념을 입력하면 AI가 설명해줍니다.")

# 1. API 키 입력 받기 (토글 형태로 숨김)
with st.expander("🔑 Google Gemini API 키 입력 (클릭해서 열기)", expanded=False):
    api_key = st.text_input("API Key를 입력하세요", type="password")
    st.markdown("※ API Key는 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료로 발급받을 수 있습니다.")

# 2. 질문 입력창
query = st.text_input("예: 베르누이 방정식이 뭐야? 또는 재료역학 공부 순서 알려줘")

# 3. 답변 생성 로직
if query:
    if not api_key:
        st.warning("⚠️ 먼저 위에서 API Key를 입력해주세요.")
    else:
        try:
            # Gemini 설정 및 호출
            genai.configure(api_key=api_key)
            model = 
