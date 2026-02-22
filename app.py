"""
Genspark Secret Search Bot
--------------------------
Genspark AI 검색 서비스를 시크릿 모드로 자동화하여 검색 결과를 캡처하는 봇입니다.

Usage:
    python app.py "검색할 키워드" [--headless]
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
    def __init__(self, headless=False, output_dir="output"):
        self.driver = None
        self.headless = headless
        self.output_dir = output_dir
        
        # 결과 저장 폴더 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        print("🔧 드라이버 설정 중...")
        
        chrome_options = Options()
        
        # 헤드리스 모드 (화면 표시 여부)
        if self.headless:
            chrome_options.add_argument('--headless=new')
            
        # 기본 설정
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 시크릿 모드 및 탐지 회피
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            # 브라우저 드라이버 자동 설치 및 로드
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ 브라우저 실행 성공")
            return True
        except Exception as e:
            print(f"❌ 드라이버 초기화 실패: {e}")
            return False

    def search(self, query, wait_time=15):
        """Genspark 검색 수행"""
        if not self.driver:
            return

        try:
            url = "https://www.genspark.ai/"
            print(f"\n🌍 {url} 접속 중...")
            self.driver.get(url)

            wait = WebDriverWait(self.driver, 20)
            
            # 페이지 로딩 확인
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            self._take_screenshot("home")

            print(f"🔍 검색어 입력: '{query}'")
            
            # 다양한 검색창 선택자 시도
            search_selectors = [
                (By.XPATH, "//textarea"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.CSS_SELECTOR, "[placeholder*='search' i]"),
                (By.CSS_SELECTOR, "[placeholder*='ask' i]"),
            ]
            
            search_box = None
            for by, selector in search_selectors:
                try:
                    search_box = wait.until(EC.presence_of_element_located((by, selector)))
                    break
                except:
                    continue
            
            if not search_box:
                raise Exception("검색창을 찾을 수 없습니다.")

            search_box.clear()
            search_box.send_keys(query)
            time.sleep(1)
            search_box.send_keys(Keys.RETURN)

            print(f"⏳ 답변 생성 대기 중... ({wait_time}초)")
            time.sleep(wait_time)
            
            filename = self._take_screenshot("result")
            print(f"✅ 완료! 결과 저장됨: {filename}")

        except Exception as e:
            print(f"❌ 실행 중 오류 발생: {e}")
            self._take_screenshot("error")
        finally:
            self.close()

    def _take_screenshot(self, name):
        """스크린샷 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/{name}_{timestamp}.png"
        if self.driver:
            self.driver.save_screenshot(filename)
        return filename

    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            print("👋 브라우저 종료")

if __name__ == "__main__":
    # 커맨드 라인 인자 파싱
    parser = argparse.ArgumentParser(description="Genspark Auto Search Bot")
    parser.add_argument("query", type=str, nargs='?', default="What is Python?", help="검색할 질문 내용")
    parser.add_argument("--headless", action="store_true", help="브라우저 화면 없이 실행")
    
    args = parser.parse_args()

    # 봇 실행
    bot = GensparkBot(headless=args.headless)
    if bot.setup_driver():
        bot.search(args.query)
