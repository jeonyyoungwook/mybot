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

# 1. 입력창 안내 문구
placeholder_text = "[질문 하는 곳입니다 / Type your question / 質問を入力してください / 请输入您的问题]"

query = st.text_input(
    "검색어 입력:", 
    placeholder=placeholder_text
)

if st.button("🚀 질문 실행하기"):
    if query:
        status_area = st.empty()
        status_area.info("🤖 봇: 젠스파크에 접속해서 질문을 입력하는 중입니다...")

        # 크롬 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--incognito")
        
        # 봇 탐지 회피 설정
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # 1. 메인 홈페이지로 이동 (검색 결과 페이지 X)
            driver.get("https://www.genspark.ai/")
            
            status_area.info("⏳ 홈페이지 도착! 검색창을 찾는 중...")
            time.sleep(5) # 페이지 로딩 대기

            # 2. 검색창(textarea) 찾아서 입력하기
            # 화면에 보이는 'Ask anything' 칸을 찾습니다.
            try:
                search_box = driver.find_element(By.TAG_NAME, "textarea")
                search_box.click()
                time.sleep(1)
                search_box.send_keys(query) # 질문 입력
                time.sleep(1)
                search_box.send_keys(Keys.ENTER) # 엔터 치기
                
                status_area.info("📝 질문 입력 완료! 답변을 기다리는 중...")
            except Exception as e:
                st.error(f"검색창을 찾지 못했습니다: {e}")

            # 3. 답변 생성 대기 (AI가 생각할 시간)
            time.sleep(10) 

            # 4. 스크린샷 찍기
            screenshot = driver.get_screenshot_as_png()
            st.image(screenshot, caption="AI 답변 결과", use_container_width=True)

            status_area.success("✅ 완료!")

        except Exception as e:
            st.error(f"에러가 발생했습니다: {e}")
        
        finally:
            if 'driver' in locals():
                driver.quit()
    else:
        st.warning("질문 내용을 입력해주세요.")
