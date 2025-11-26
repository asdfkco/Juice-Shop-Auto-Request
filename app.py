import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class JuiceShopSwaggerTester:
    def __init__(self, base_url, email, password):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.password = password
        
        opts = Options()
        opts.add_argument("--ignore-certificate-errors")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        self.wait = WebDriverWait(self.driver, 15)

    def log(self, msg):
        print(f"[Log] {msg}")

    def initial_setup(self):
        self.driver.get(f"{self.base_url}/#/search")
        self.log(f"메인 페이지 접속 ({self.base_url})")
        time.sleep(2)
        
        try:
            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close Welcome Banner']").click()
        except: pass
        try:
            self.driver.find_element(By.CLASS_NAME, "cc-dismiss").click()
        except: pass

    def perform_login(self):
        """로그인 수행 (GET /rest/user/whoami 트리거)"""
        self.log("로그인 시도...")
        self.driver.get(f"{self.base_url}/#/login")
        
        try:
            self.wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(self.email)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            self.driver.find_element(By.ID, "loginButton").click()
            
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mat-mdc-button-touch-target")))
            self.log("로그인 성공!")
            time.sleep(2)
        except Exception as e:
            self.log(f"로그인 실패 (계정 정보를 확인하세요): {e}")
            self.driver.quit()
            exit()

    def generate_api_traffic(self):
        """Swagger 명세 기반 API 호출 시나리오"""

        urls = [
            ("/#/contact", "Contact Page (Captcha API)"),
            ("/#/photo-wall", "Photo Wall (Memories API)"),
            ("/#/track-result", "Track Order (Track API)")
        ]
        for route, name in urls:
            self.driver.get(self.base_url + route)
            self.log(f"이동 -> {name}")
            time.sleep(2)

        self.driver.get(f"{self.base_url}/#/search")
        time.sleep(2)
        self.log("상품 담기 시도 (POST /api/BasketItems/)...")
        try:
            add_btn = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-basket")))
            add_btn.click()
            self.log(" -> 상품 담기 완료")
            time.sleep(2) 
        except Exception as e:
            self.log(f"상품 담기 실패: {e}")

        self.driver.get(f"{self.base_url}/#/basket")
        self.log("장바구니 이동 -> Checkout 버튼 클릭")
        time.sleep(2)
        try:
            checkout_btn = self.driver.find_element(By.ID, "checkoutButton")
            checkout_btn.click()
        except:
            self.log("Checkout 버튼을 찾을 수 없습니다. (장바구니가 비었을 수 있음)")
            return

        self.log("STEP 1: 주소 선택 (GET /api/Addresss)")
        time.sleep(2)
        try:
            self.driver.find_element(By.CSS_SELECTOR, "mat-radio-button").click()
            time.sleep(1)
            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Proceed to payment selection']").click()
        except:
            self.log(" [!] 저장된 주소가 없거나 선택 실패. 주소를 먼저 등록해주세요.")

        self.log("STEP 2: 배송 방법 선택 (GET /api/Deliverys)")
        time.sleep(2)
        try:
            self.driver.find_element(By.CSS_SELECTOR, "mat-radio-button").click()
            time.sleep(1)
            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Proceed to delivery method selection']").click()
        except:
             self.log(" [!] 배송 방법 선택 실패.")

        self.log("STEP 3: 지불 방법 선택 (GET /api/Cards)")
        time.sleep(2)
        try:
            self.driver.find_element(By.CSS_SELECTOR, "mat-radio-button").click()
            time.sleep(1)
            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Proceed to review']").click()
        except:
            self.log(" [!] 저장된 카드가 없거나 선택 실패. 카드를 먼저 등록해주세요.")

        self.log("STEP 4: 최종 주문 (POST /rest/basket/.../checkout)")
        time.sleep(2)
        try:
            pay_btn = self.driver.find_element(By.ID, "checkoutButton")
            pay_btn.click()
            self.log(" -> [SUCCESS] 결제 버튼 클릭 완료! (API 호출됨)")
            time.sleep(5) 
        except:
            self.log(" [!] 최종 결제 버튼 클릭 실패.")

    def close(self):
        input("\n[엔터] 키를 누르면 브라우저를 종료합니다...")
        self.driver.quit()

if __name__ == "__main__":
    TARGET_URL = "http://devopssong.nginxstore.kr"
    
    USER_EMAIL = "admin@juice-sh.op" 
    USER_PW = "admin123" 

    tester = JuiceShopSwaggerTester(TARGET_URL, USER_EMAIL, USER_PW)
    
    try:
        while(100):
            tester.initial_setup()      
            tester.perform_login()      
            tester.generate_api_traffic() 
    except Exception as e:
        print(f"[Critical Error] {e}")
    finally:
        tester.close()
