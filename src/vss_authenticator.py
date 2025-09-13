"""
VSS Authentication Module
Module xác thực và quản lý session cho website VSS
"""
import logging
import time
import random
import json
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import hrequests
from config import VSSConfig

class VSSAuthenticator:
    """VSS Authentication và Session Management"""
    
    def __init__(self, use_proxy=True, headless=True):
        self.config = VSSConfig()
        self.use_proxy = use_proxy
        self.headless = headless
        self.session = None
        self.driver = None
        self.csrf_token = None
        self.cookies = {}
        self.ua = UserAgent()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if not exists
        VSSConfig.ensure_directories()
        
        # Setup file handler
        log_handler = logging.FileHandler(
            VSSConfig.LOGGING_CONFIG["file"], 
            encoding='utf-8'
        )
        log_handler.setFormatter(
            logging.Formatter(VSSConfig.LOGGING_CONFIG["format"])
        )
        self.logger.addHandler(log_handler)
        
    def _get_random_user_agent(self):
        """Get random user agent"""
        try:
            return self.ua.random
        except:
            return random.choice(VSSConfig.USER_AGENTS)
    
    def _setup_session(self):
        """Setup requests session với proxy và headers"""
        self.session = hrequests.Session()
        
        # Set user agent
        user_agent = self._get_random_user_agent()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })
        
        # Configure proxy if enabled
        if self.use_proxy and VSSConfig.PROXY_CONFIG["enabled"]:
            self.session.proxies.update(VSSConfig.PROXY_CONFIG)
            self.logger.info("Đã cấu hình proxy: %s", VSSConfig.PROXY_CONFIG["http"])
        
        # Configure SSL verification
        if not VSSConfig.REQUEST_CONFIG["verify_ssl"]:
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
        self.logger.info("Đã setup session với User-Agent: %s", user_agent[:50] + "...")
    
    def _setup_chrome_driver(self):
        """Setup undetected Chrome driver"""
        try:
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            # Anti-detection options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--exclude-switches=["enable-automation"]')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            
            # Set window size
            width, height = VSSConfig.BROWSER_CONFIG["window_size"]
            options.add_argument(f'--window-size={width},{height}')
            
            # Set user agent
            user_agent = self._get_random_user_agent()
            options.add_argument(f'--user-agent={user_agent}')
            
            # Proxy configuration
            if self.use_proxy and VSSConfig.PROXY_CONFIG["enabled"]:
                proxy_host = VSSConfig.PROXY_CONFIG["http"].replace("http://", "")
                options.add_argument(f'--proxy-server={proxy_host}')
                
            self.driver = uc.Chrome(options=options)
            self.logger.info("Đã khởi tạo Chrome driver thành công")
            
            # Execute script to hide automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            self.logger.error("Lỗi khởi tạo Chrome driver: %s", str(e))
            return False
    
    def _extract_csrf_token(self, html_content):
        """Extract CSRF token from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find CSRF token in meta tag
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                self.csrf_token = csrf_meta.get('content')
                self.logger.info("Đã extract CSRF token từ meta tag")
                return self.csrf_token
            
            # Find CSRF token in hidden input
            csrf_input = soup.find('input', {'name': '_token'})
            if csrf_input:
                self.csrf_token = csrf_input.get('value')
                self.logger.info("Đã extract CSRF token từ hidden input")
                return self.csrf_token
            
            # Try to find in script tags
            for script in soup.find_all('script'):
                if script.string and 'csrf' in script.string.lower():
                    # Extract token using regex or string parsing
                    import re
                    token_match = re.search(r'["\']?csrf["\']?\s*:\s*["\']([^"\']+)["\']', script.string, re.IGNORECASE)
                    if token_match:
                        self.csrf_token = token_match.group(1)
                        self.logger.info("Đã extract CSRF token từ script tag")
                        return self.csrf_token
                        
            self.logger.warning("Không tìm thấy CSRF token")
            return None
            
        except Exception as e:
            self.logger.error("Lỗi extract CSRF token: %s", str(e))
            return None
    
    def connect_to_vss(self):
        """Kết nối đến website VSS và lấy session"""
        try:
            self.logger.info("Bắt đầu kết nối đến VSS...")
            
            # Setup session
            self._setup_session()
            
            # Make initial request to get cookies and CSRF token
            response = self.session.get(
                VSSConfig.LOGIN_URL,
                timeout=VSSConfig.REQUEST_CONFIG["timeout"]
            )
            
            if response.status_code == 200:
                self.logger.info("Kết nối VSS thành công - Status: %d", response.status_code)
                
                # Extract CSRF token
                self._extract_csrf_token(response.text)
                
                # Update cookies
                self.cookies.update(dict(response.cookies))
                
                # Update session headers with referrer
                self.session.headers.update({
                    'Referer': VSSConfig.LOGIN_URL
                })
                
                return True
                
            else:
                self.logger.error("Kết nối VSS thất bại - Status: %d", response.status_code)
                return False
                
        except Exception as e:
            self.logger.error("Lỗi kết nối VSS: %s", str(e))
            return False
    
    def connect_with_browser(self):
        """Kết nối sử dụng browser để handle JavaScript"""
        try:
            self.logger.info("Bắt đầu kết nối VSS bằng browser...")
            
            if not self._setup_chrome_driver():
                return False
            
            # Navigate to VSS login page
            self.driver.get(VSSConfig.LOGIN_URL)
            
            # Wait for page load
            wait = WebDriverWait(self.driver, 30)
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            
            # Extract CSRF token from page source
            self._extract_csrf_token(self.driver.page_source)
            
            # Get cookies from browser
            browser_cookies = self.driver.get_cookies()
            for cookie in browser_cookies:
                self.cookies[cookie['name']] = cookie['value']
            
            self.logger.info("Kết nối VSS bằng browser thành công")
            return True
            
        except Exception as e:
            self.logger.error("Lỗi kết nối VSS bằng browser: %s", str(e))
            return False
    
    def authenticate(self, username=None, password=None):
        """
        Authenticate with VSS system
        For now, we focus on accessing public BHXH lookup functionality
        """
        try:
            self.logger.info("Bắt đầu quá trình xác thực...")
            
            # First try with session
            if self.connect_to_vss():
                # Test access to BHXH lookup page
                lookup_response = self.session.get(
                    VSSConfig.BHXH_LOOKUP_URL,
                    timeout=VSSConfig.REQUEST_CONFIG["timeout"]
                )
                
                if lookup_response.status_code == 200:
                    self.logger.info("Truy cập trang tra cứu BHXH thành công")
                    return True
                else:
                    self.logger.warning("Không thể truy cập trang tra cứu - thử với browser")
                    
            # Fallback to browser method
            if self.connect_with_browser():
                try:
                    self.driver.get(VSSConfig.BHXH_LOOKUP_URL)
                    WebDriverWait(self.driver, 30).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    self.logger.info("Truy cập trang tra cứu BHXH bằng browser thành công")
                    return True
                except TimeoutException:
                    self.logger.error("Timeout khi truy cập trang tra cứu")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error("Lỗi trong quá trình xác thực: %s", str(e))
            return False
    
    def test_connection(self):
        """Test connection to VSS"""
        try:
            self.logger.info("Testing kết nối đến VSS...")
            
            # Test basic connectivity
            test_response = requests.get(
                VSSConfig.BASE_URL,
                timeout=10,
                proxies=VSSConfig.PROXY_CONFIG if self.use_proxy else None,
                verify=VSSConfig.REQUEST_CONFIG["verify_ssl"]
            )
            
            if test_response.status_code == 200:
                self.logger.info("Test kết nối VSS thành công")
                return True
            else:
                self.logger.error("Test kết nối thất bại - Status: %d", test_response.status_code)
                return False
                
        except Exception as e:
            self.logger.error("Lỗi test kết nối: %s", str(e))
            return False
    
    def get_session_info(self):
        """Get current session information"""
        return {
            "csrf_token": self.csrf_token,
            "cookies": self.cookies,
            "has_browser": self.driver is not None,
            "has_session": self.session is not None,
            "proxy_enabled": self.use_proxy
        }
    
    def close(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("Đã đóng Chrome driver")
                
            if self.session:
                self.session.close()
                self.logger.info("Đã đóng session")
                
        except Exception as e:
            self.logger.error("Lỗi khi đóng resources: %s", str(e))

# Test authentication if run directly
if __name__ == "__main__":
    # Setup logging to console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    auth = VSSAuthenticator(use_proxy=True, headless=True)
    
    # Test connection
    if auth.test_connection():
        print("✅ Test kết nối thành công")
    else:
        print("❌ Test kết nối thất bại")
    
    # Test authentication
    if auth.authenticate():
        print("✅ Xác thực thành công")
        session_info = auth.get_session_info()
        print(f"📊 Session info: {json.dumps(session_info, indent=2)}")
    else:
        print("❌ Xác thực thất bại")
    
    # Cleanup
    auth.close()
