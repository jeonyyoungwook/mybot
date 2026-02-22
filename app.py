"""
Genspark Secret Bot (Windows/Mac Visible Version)
-------------------------------------------------
내 컴퓨터에서 브라우저가 뜨는 것을 직접 확인할 수 있는 버전입니다.
"""

import os
import time
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GensparkBot:
    def __init__(self, output_dir="output"):
        self.driver = None
        self.output_dir = output_dir
        
        # 결과 저장 폴더 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def setup_driver(self):
        """Chrome 드라이버 설정 (화면 보이게 설정)"""
        print("🔧 브라우저 켜는 중...")
        
        chrome_options = Options()
        
        # [중요] 화면이 보이도록 헤드리스 모드 제거!
        # chrome_options.add_argument('--headless=new')  <-- 이걸 지웠습니다.
        
        # 윈도우에서 안전하게 실행되도록 설정
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 시크릿 모드 (로그인 정보 안 남음)
        chrome_options.add_argument('--incognito')
        
        # "자동화된 소프트웨어입니다" 알림 숨기기
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            # 내 컴퓨터에 깔린 크롬 버전에 맞춰 드라이버 자동 설치
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ 브라우저 실행 성공!")
            return True
        except Exception as e:
            print(f"❌ 드라이버 초기화 실패: {e}")
            print("👉 크롬 브라우저가 켜져 있다면 모두 끄고 다시 시도해보세요.")
            return False

    def search(self, query):
        """검색 수행"""
        if not self.driver:
            return

        try:
            url = "https://www.genspark.ai/"
            print(f"\n🌍 Genspark 접속 중... ({url})")
            self.driver.get(url)

            wait = WebDriverWait(self.driver, 20)
            
            # 로딩 대기
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            
            print(f"🔍 검색어 입력: '{query}'")
            
            # 검색창 찾기
            search_selectors = [
                (By.XPATH, "//textarea"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.CSS_SELECTOR, "[placeholder*='search' i]"),
            ]
            
            search_box = None
            for by, selector in search_selectors:
                try:
                    search_box = wait.until(EC.presence_of_element_located((by, selector)))
                    break
                except:
                    continue
            
            if not search_box:
                raise Exception("검색창을 못 찾았습니다.")

            search_box.clear()
            search_box.send_keys(query)
            time.sleep(1)
            search_box.send_keys(Keys.RETURN)

            print("⏳ 봇이 검색 결과를 보고 있습니다... (20초 대기)")
            
            # 화면을 볼 수 있게 충분히 대기
            time.sleep(20) 
            
            # 스크린샷 저장
            self._take_screenshot("result")
            print("📸 결과 저장 완료!")

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        finally:
            self.close()

    def _take_screenshot(self, name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/{name}_{timestamp}.png"
        if self.driver:
            self.driver.save_screenshot(filename)
        return filename

    def close(self):
        """종료 전 사용자 확인"""
        print("\n✅ 작업이 끝났습니다.")
        # 바로 꺼지면 아쉬우니까 엔터 누르면 꺼지게 설정
        input("👉 브라우저를 닫으려면 엔터(Enter) 키를 누르세요...")
        
        if self.driver:
            self.driver.quit()
            print("👋 브라우저 종료")

if __name__ == "__main__":
    # 여기서 검색어를 바꾸세요
    my_query = "요즘 뜨는 한국 넷플릭스 드라마 추천해줘"
    
    bot = GensparkBot()
    if bot.setup_driver():
        bot.search(my_query)
