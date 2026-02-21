%%writefile app.py
import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 1. 화면 구성
st.set_page_config(page_title="젠스파크 시크릿 봇", page_icon="🕵️")
st.title("🕵️ GenSpark 시크릿 질문기")
st.write("이 프로그램은 서버에서 **시크릿 창**을 몰래 열어 질문하고 결과를 보여줍니다.")

# 2. 사용자 입력
question = st.text_input("질문할 내용을 입력하세요:", "오늘 저녁 메뉴 추천해줘")

# 3. 버튼 클릭 시 실행
if st.button("🚀 질문 실행하기"):
    st.info("🤖 봇: 시크릿 모드로 브라우저를 켜는 중입니다... (약 10초 소요)")

    # --- [중요] 서버용 크롬 설정 ---
    options = Options()
    options.add_argument("--headless")  # 눈에 보이지 않게 실행 (서버 전용)
    options.add_argument("--incognito") # ★시크릿 모드★
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # 봇 탐지 방지 (사람인 척하기)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    driver = None
    try:
        # 크롬 드라이버 설치 및 실행
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 1) 사이트 접속
        st.write("🌐 1. GenSpark.ai 접속 중...")
        driver.get("https://www.genspark.ai/")
        time.sleep(3) 

        # 2) 질문 입력
        st.write(f"✍️ 2. 질문 입력: '{question}'")
        
        # 입력창 찾기 (GenSpark는 보통 textarea 사용)
        try:
            input_box = driver.find_element(By.TAG_NAME, "textarea")
            input_box.clear()
            input_box.send_keys(question)
            time.sleep(1)
            input_box.send_keys(Keys.RETURN) # 엔터키
            
            st.success("✅ 질문 전송 완료! 답변을 기다립니다...")
            
            # 3) 답변 대기 (충분히 기다려야 함)
            with st.spinner("답변 생성 중 (15초 대기)..."):
                time.sleep(15)
            
            # 4) 결과 스크린샷
            st.write("📸 3. 결과 화면 캡처:")
            driver.save_screenshot("result.png")
            st.image("result.png", caption="서버가 실행한 화면")
            
        except Exception as e:
            st.error(f"입력창을 찾을 수 없어요. 사이트 구조가 바뀌었을 수 있습니다. ({e})")

    except Exception as e:
        st.error(f"브라우저 실행 중 오류가 발생했습니다: {e}")

    finally:
        # 5) 종료
        if driver:
            driver.quit()
            st.success("🚪 시크릿 브라우저를 완전히 닫았습니다. 기록이 남지 않습니다.")
