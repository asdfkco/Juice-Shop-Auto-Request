import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class JuiceShopFullTester:
    def __init__(self, base_url, email, password):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.password = password
        
        chrome_options = Options()
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)

    def dismiss_popups(self):
        time.sleep(2)
        try:
            dismiss_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close Welcome Banner']")
            dismiss_btn.click()
        except: pass
        try:
            cookie_btn = self.driver.find_element(By.CLASS_NAME, "cc-dismiss")
            cookie_btn.click()
        except: pass

    def login(self):
        print(f"[*] 로그인 시도 중... ({self.email})")
        self.driver.get(f"{self.base_url}/#/login")
        self.dismiss_popups()

        try:
            self.wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(self.email)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            
            login_btn = self.driver.find_element(By.ID, "loginButton")
            self.driver.execute_script("arguments[0].click();", login_btn)
            
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mat-mdc-button-touch-target")))
            print("[SUCCESS] 로그인 성공!")
            time.sleep(2)
        except Exception as e:
            print(f"[ERROR] 로그인 실패: {e}")
            raise e

    def add_item_to_cart(self):
        print("[*] 상품 담기 시도 중...")
        try:
            self.driver.get(f"{self.base_url}/#/search")
            time.sleep(2)
            
            add_btns = self.driver.find_elements(By.ClassName, "btn-basket")
            if add_btns:
                self.driver.execute_script("arguments[0].click();", add_btns[0])
                print("[SUCCESS] 장바구니에 상품 담기 성공")
            else:
                print("[WARNING] 담을 상품을 찾지 못했습니다.")
                
        except Exception as e:
            print(f"[ERROR] 상품 담기 중 오류: {e}")

    def visit_pages(self):
        pages = [
            ("메인/IP저장", "/#/search"),
            ("프로필/Whoami", "/#/profile"),
            ("장바구니", "/#/basket"),
            ("배송 방법 (BasketItems)", "/#/delivery-method"), 
            ("결제 수단 (Cards)", "/#/saved-payment-methods"),
            ("주문/Checkout", "/#/payment"),
            ("트래킹/Track", "/#/track-result"),
        ]

        print("\n" + "="*50)
        for desc, route in pages:
            target_url = self.base_url + route
            print(f"이동 -> {desc}")
            
            self.driver.get(target_url)
            
            time.sleep(3)
            
            current_url = self.driver.current_url
            if route not in current_url:
                print(f"   [!] 리다이렉트 발생됨: {current_url}")
            else:
                print(f"   [OK] 정상 진입: {current_url}")
                
        print("="*50 + "\n")

    def keep_open(self):
        input("엔터 키를 누르면 브라우저를 종료합니다...")
        self.driver.quit()

if __name__ == "__main__":
    TARGET_URL = "http://localhost:3000" # Insert your Juice Shop URL here
    USER_EMAIL = "admin@juice-sh.op"
    USER_PW = "admin123"

    tester = JuiceShopFullTester(TARGET_URL, USER_EMAIL, USER_PW)
    
    try:
        tester.login()           
        tester.add_item_to_cart() 
        tester.visit_pages()      
        tester.keep_open()        
    except Exception as e:
        print(f"오류: {e}")
        tester.driver.quit()
