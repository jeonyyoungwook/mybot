import streamlit as st
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# --- 페이지 설정 ---
st.set_page_config(page_title="젠스파크 시크릿 봇", page_icon="🕵️")

st.title("🕵️ GenSpark 시크릿 질문기")
st.caption("서버 상태에 따라 실행까지 20~30초 정도 걸릴 수 있습니다.")

# --- 질문 입력 ---
question = st.text_input("질문할 내용을 입력하세요:", "오늘 서울 날씨 어때?")

# --- 실행 버튼 ---
if st.button("🚀 질문 실행하기"):
    st.info("🤖 봇: 작업을 시작합니다. 잠시만 기다려주세요...")
    
    status_text = st.empty() # 진행상황 표시용
    status_text.text("⚙️ 브라우저 설정 중...")

    # [1] 서버용 크롬 옵션 설정
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--incognito") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    driver = None
    
    try:
        # [2] 드라이버 설치 및 실행 (에러 방지 로직 추가)
        status_text.text("⚙️ 크롬 드라이버 설치 및 실행 중...")
        
        # 방법 A: webdriver_manager 사용
        try:
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            driver = webdriver.Chrome(service=service, options=options)
        except:
            # 방법 B: 설치 실패 시 시스템 경로 강제 지정 (비상용)
            options.binary_location = "/usr/bin/chromium"
            service = Service("/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=options)

        # [3] 사이트 접속
        status_text.text("🌐 젠스파크(GenSpark) 접속 중...")
        driver.get("https://www.genspark.ai/")
        time.sleep(5) # 로딩 대기 넉넉하게

        # [4] 질문 입력
        status_text.text(f"✍️ 질문 입력 중: {question}")
        
        try:
            # 텍스트 박스 찾기 (여러가지 방법 시도)
            input_box = None
            try:
                input_box = driver.find_element("tag name", "textarea")
            except:
                # 못 찾으면 input 태그 시도
                input_box = driver.find_element("tag name", "input")
            
            if input_box:
                input_box.clear()
                input_box.send_keys(question)
                time.sleep(1)
                
                # 엔터키 입력
                from selenium.webdriver.common.keys import Keys
                input_box.send_keys(Keys.RETURN)
                
                status_text.text("✅ 질문 전송 완료! 답변 기다리는 중 (15초)...")
                time.sleep(15) # 답변 생성 대기
                
                # [5] 스크린샷
                status_text.text("📸 화면 캡처 중...")
                driver.save_screenshot("result.png")
                st.image("result.png", caption="결과 화면")
                st.success("완료되었습니다!")
            else:
                st.error("입력창을 찾을 수 없습니다.")
                driver.save_screenshot("error.png")
                st.image("error.png", caption="에러 당시 화면")

        except Exception as e:
            st.error(f"질문 입력 중 에러 발생: {e}")

    except Exception as e:
        st.error(f"브라우저 실행 실패: {e}")
        # 로그 확인용 힌트
        st.help("Manage app -> Logs를 확인해보세요.")

    finally:
        if driver:
            driver.quit()
            status_text.text("🚪 브라우저 종료 완료.")
