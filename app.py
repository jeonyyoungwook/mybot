import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

# 페이지 설정
st.set_page_config(page_title="GenSpark 시크릿 질문기", layout="wide")

# 제목
st.title("🕵️‍♂️ GenSpark 시크릿 질문기")
st.write("서버 상태에 따라 실행까지 시간이 조금 걸릴 수 있습니다.")

# 1. 입력창 안내 문구 (4개 국어)
placeholder_text = "[질문 하는 곳입니다 / Type your question / 質問を入力してください / 请输入您的问题]"

query = st.text_input(
    "검색어 입력:", 
    placeholder=placeholder_text
)

if st.button("🚀 질문 실행하기"):
    if query:
        status_area = st.empty()
        status_area.info("🤖 봇: 젠스파크 접속 중... (로그인 팝업 차단 준비)")

        # 크롬 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--incognito") # 시크릿 모드
        
        # 봇 탐지 회피 설정 (매우 중요)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # 1. 메인 홈페이지로 이동
            driver.get("https://www.genspark.ai/")
            status_area.info("⏳ 홈페이지 도착! 검색창을 찾는 중...")
            time.sleep(4) # 로딩 대기

            # 2. 검색창 찾기 및 팝업 유도
            try:
                # 화면의 textarea(글쓰는 곳) 찾기
                search_box = driver.find_element(By.TAG_NAME, "textarea")
                
                # [중요] 일단 클릭해서 '가입하세요' 팝업이 뜨게 유도함
                search_box.click()
                time.sleep(2) # 팝업 뜰 시간 주기

                # 3. 팝업 닫기 (ESC 키 연타)
                status_area.info("🛡️ 로그인 팝업 제거 시도 중...")
                actions = ActionChains(driver)
                actions.send_keys(Keys.ESCAPE).perform() # 1차 시도
                time.sleep(1)
                actions.send_keys(Keys.ESCAPE).perform() # 2차 시도 (혹시 몰라서 한번 더)
                time.sleep(1)

                # 4. 다시 검색창 클릭하고 글씨 쓰기
                search_box.click() 
                time.sleep(0.5)
                search_box.send_keys(query) # 질문 입력
                time.sleep(0.5)
                search_box.send_keys(Keys.ENTER) # 엔터
                
                status_area.info("📝 질문 입력 완료! AI 답변 생성 중...")
                
            except Exception as e:
                st.error(f"검색창 조작 중 문제 발생: {e}")

            # 5. 답변 생성 대기 (시간 넉넉하게)
            time.sleep(8) 

            # 6. 스크린샷 찍기
            screenshot = driver.get_screenshot_as_png()
            st.image(screenshot, caption="결과 화면", use_container_width=True)

            status_area.success("✅ 완료!")

        except Exception as e:
            st.error(f"에러가 발생했습니다: {e}")
        
        finally:
            if driver:
                driver.quit()
    else:
        st.warning("질문 내용을 입력해주세요.")
