import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# 페이지 설정
st.set_page_config(page_title="GenSpark 시크릿 질문기", layout="wide")

# 제목
st.title("🕵️‍♂️ GenSpark 시크릿 질문기")
st.write("서버 상태에 따라 실행까지 시간이 조금 걸릴 수 있습니다.")

# 1. 입력창 글씨 수정 (4개 국어 반영)
# 한글 / 영어 / 일본어 / 중국어
placeholder_text = "[질문 하는 곳입니다 / Type your question / 質問を入力してください / 请输入您的问题]"

query = st.text_input(
    "검색어 입력:", 
    placeholder=placeholder_text
)

if st.button("🚀 질문 실행하기"):
    if query:
        status_area = st.empty()
        status_area.info("🤖 봇: 보안 벽을 뚫고 접속을 시도합니다...")

        # 크롬 옵션 설정 (사람인 척 위장하기 위한 설정)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 화면 없이 실행
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--incognito") # 시크릿 모드
        
        # 2. 봇 탐지 회피를 위한 강력한 설정 추가
        # "나 자동화된 로봇 아니야!" 라고 브라우저 속성 숨기기
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # 일반 사람의 브라우저 정보(User-Agent)로 위장
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # GenSpark 접속
            url = f"https://www.genspark.ai/search?query={query}"
            driver.get(url)
            
            # 페이지 로딩 및 보안 점검 통과 대기
            status_area.info("⏳ 페이지 로딩 중... (보안 점검 우회 시도 중)")
            
            # 보안 창이 뜰 수 있으므로 넉넉하게 기다림
            time.sleep(8) 

            # 3. 로그인 팝업 등 방해 요소 닫기 시도
            try:
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(1)
            except:
                pass

            # 결과 화면이 뜰 때까지 조금 더 대기
            time.sleep(3)

            # 스크린샷 찍기
            screenshot = driver.get_screenshot_as_png()
            st.image(screenshot, caption="결과 화면", use_container_width=True)

            status_area.success("✅ 완료!")

        except Exception as e:
            st.error(f"에러가 발생했습니다: {e}")
        
        finally:
            # 브라우저 종료
            if 'driver' in locals():
                driver.quit()
    else:
        st.warning("질문 내용을 입력해주세요.")
