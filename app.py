import streamlit as st
import urllib.parse
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="GenSpark Secret Link", page_icon="🕵️‍♂️", layout="centered")

# 2. 언어 설정 (간소화)
if 'lang' not in st.session_state:
    st.session_state.lang = 'ko'

# 3. 데이터
text_data = {
    'ko': {
        'title': "🕵️‍♂️ GenSpark 시크릿 접속기",
        'subtitle': "로그인 없이 검색하는 두 가지 방법!",
        'tab_simple': "1️⃣ 간편 방법 (시크릿모드)",
        'tab_advanced': "2️⃣ 영구 차단 (PC 전용)",
        'adv_title': "🛠️ 확장 프로그램으로 로그인 창 없애기",
        'adv_desc': """
        이 방법은 PC에서 **한 번만 설정하면**, 앞으로 시크릿 모드를 안 써도 로그인 창이 안 뜹니다.
        (Tampermonkey 확장 프로그램이 필요합니다.)
        """,
        'step1': "1. 브라우저에 **Tampermonkey** 확장 프로그램을 설치하세요.",
        'step2': "2. 아래 **스크립트 코드**를 복사하세요.",
        'step3': "3. Tampermonkey에서 [새 스크립트 만들기] -> 붙여넣기 -> 저장하세요.",
        'script_code': """
// ==UserScript==
// @name         GenSpark Login Remover
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  GenSpark 로그인 팝업 강제 삭제
// @author       You
// @match        https://www.genspark.ai/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    // 1초마다 로그인 팝업 감지 후 삭제
    setInterval(() => {
        const loginModal = document.querySelector('div[class*="AuthModal"]'); // 로그인 창 클래스명 감지
        const backdrop = document.querySelector('div[class*="backdrop"]'); // 배경 어둡게 하는 것

        if (loginModal) {
            loginModal.remove();
            console.log("로그인 창 삭제됨");
        }
        if (backdrop) {
            backdrop.remove();
        }
        // 스크롤 막힘 풀기
        document.body.style.overflow = 'auto';
    }, 1000);
})();
        """,
        'input_ph': "검색어를 입력하세요",
        'btn_search': "🔍 '{query}' 검색하기"
    }
}
t = text_data['ko'] # 한국어 예시

st.title(t['title'])
st.write(t['subtitle'])

# 탭 구분
tab1, tab2 = st.tabs([t['tab_simple'], t['tab_advanced']])

# --- 탭 1: 기존 시크릿 모드 방식 (모바일/PC 공용) ---
with tab1:
    st.info("설치 없이 바로 쓸 수 있는 가장 쉬운 방법입니다.")
    st.markdown("""
    1. 아래 검색창에 질문 입력
    2. 생성된 버튼을 **우클릭(PC)**하거나 **꾹 누르기(모바일)**
    3. **[시크릿 창에서 열기]** 선택
    """)
    
    query = st.text_input("질문 입력", placeholder=t['input_ph'])
    
    if query:
        encoded_query = urllib.parse.quote(query)
        target_url = f"https://www.genspark.ai/search?query={encoded_query}"
        btn_text = t['btn_search'].replace("{query}", query)
        
        # 버튼 영역
        st.link_button(label=btn_text, url=target_url, type="primary", use_container_width=True)
        
        # 주소 복사 버튼 (자바스크립트)
        copy_html = f"""
        <input type="text" value="{target_url}" id="myInput" style="position: absolute; left: -9999px;">
        <button onclick="copyFunction()" style="width:100%; padding:8px; cursor:pointer; margin-top:5px; border-radius:5px; border:1px solid #ccc;">📋 주소 복사하기 (직접 붙여넣기용)</button>
        <script>
        function copyFunction() {{
            var copyText = document.getElementById("myInput");
            copyText.select();
            copyText.setSelectionRange(0, 99999);
            navigator.clipboard.writeText(copyText.value).then(function() {{ alert("복사완료! 시크릿창에 붙여넣으세요."); }});
        }}
        </script>
        """
        components.html(copy_html, height=50)

# --- 탭 2: 확장 프로그램/스크립트 방식 (캡처 내용 반영) ---
with tab2:
    st.warning("⚠️ 이 방법은 PC(크롬, 엣지 등)에서만 가능합니다.", icon="💻")
    st.markdown(f"### {t['adv_title']}")
    st.markdown(t['adv_desc'])
    
    st.divider()
    
    st.markdown(f"**{t['step1']}**")
    st.link_button("Tampermonkey 설치하러 가기 (Chrome 웹스토어)", "https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo")
    
    st.divider()
    
    st.markdown(f"**{t['step2']}**")
    st.code(t['script_code'], language='javascript')
    st.caption("▲ 오른쪽 위 복사 버튼을 누르세요.")
    
    st.divider()
    st.markdown(f"**{t['step3']}**")
    st.success("설정이 완료되면, 일반 모드에서도 로그인 창이 자동으로 사라집니다!")
