import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 페이지 설정
st.set_page_config(page_title="GenSpark 시크릿 질문기", layout="wide")

# 제목
st.title("🕵️‍♂️ GenSpark 시크릿 질문기")
st.write("서버 상태에 따라 실행까지 20~30초 정도 걸릴 수 있습니다.")

# 1. 입력창 글씨 수정 부분
query = st.text_input(
    "질문할 내용을 입력하세요:", 
    placeholder="[질문 하는곳입니다  한글 영어 일본어 중국어]"
)

if st.button("🚀 질문 실행하기"):
    if query:
        status_area = st.empty()
        status_area.info("🤖 봇: 작업을 시작합니다. 잠시만 기다려주세요...")

        # 크롬 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 화면 없이 실행
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--incognito")  # 2. 시크릿 모드 추가

        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # GenSpark 접속
            url = f"https://www.genspark.ai/search?query={query}"
            driver.get(url)
            
            # 페이지 로딩 대기
            status_area.info("⏳ 페이지 로딩 중... (로그인 팝업 처리 중)")
            time.sleep(5) # 기본 로딩 대기

            # 3. 로그인 팝업(Sign in) 닫기 시도
            try:
                # 방법 1: ESC 키를 눌러서 팝업 닫기 시도
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(1)
            except:
                pass

            # 추가 대기 (결과가 생성될 때까지)
            time.sleep(5)

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
