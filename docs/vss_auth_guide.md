# VSS Authentication & CAPTCHA Handling Guide

**Hướng dẫn toàn diện cho hệ thống authentication và CAPTCHA handling của VSS Portal**

---

## 📋 Mục Lục

1. [Tổng Quan](#tổng-quan)
2. [Kiến Trúc Hệ Thống](#kiến-trúc-hệ-thống)
3. [Cài Đặt và Cấu Hình](#cài-đặt-và-cấu-hình)
4. [Sử Dụng Cơ Bản](#sử-dụng-cơ-bản)
5. [Tính Năng Nâng Cao](#tính-năng-nâng-cao)
6. [CAPTCHA Handling](#captcha-handling)
7. [Session Management](#session-management)
8. [Error Handling & Retry Logic](#error-handling--retry-logic)
9. [Security & Anti-Detection](#security--anti-detection)
10. [Testing & Debugging](#testing--debugging)
11. [Troubleshooting](#troubleshooting)
12. [API Reference](#api-reference)

---

## 🎯 Tổng Quan

### Mục Đích
Hệ thống authentication VSS được thiết kế để cung cấp giải pháp toàn diện cho việc đăng nhập và quản lý session trên VSS Portal, bao gồm:

- **Authentication flow** hoàn chỉnh với username/password
- **CAPTCHA detection và solving** tự động/thủ công
- **Session management** với cookie persistence
- **Retry logic** thông minh cho authentication failures
- **Security measures** chống detection và blocking

### Tính Năng Chính
- ✅ **Multi-strategy authentication** với fallback options
- ✅ **Intelligent CAPTCHA solving** (OCR + manual input)
- ✅ **Robust session persistence** với automatic expiry handling
- ✅ **Advanced retry logic** với exponential backoff
- ✅ **Proxy support** cho enhanced privacy
- ✅ **Comprehensive logging** cho debugging và monitoring
- ✅ **Anti-detection features** để tránh bị block

---

## 🏗️ Kiến Trúc Hệ Thống

### Core Components

```
VSS Authentication System
├── VSSAuthenticator (Main Controller)
├── SessionManager (Session & Cookie Management)
├── CaptchaSolver (CAPTCHA Detection & Solving)
├── AuthConfig (Configuration Management)
└── Data Classes (LoginCredentials, AuthSession, etc.)
```

### Component Responsibilities

#### 1. **VSSAuthenticator**
- Điều phối toàn bộ authentication flow
- Quản lý retry logic và error handling
- Tích hợp tất cả components khác

#### 2. **SessionManager**
- Tạo và quản lý authentication sessions
- Cookie persistence và recovery
- Session expiry handling

#### 3. **CaptchaSolver**
- Phát hiện CAPTCHA trong HTML content
- OCR-based automatic solving
- Manual input fallback

#### 4. **AuthConfig**
- Centralized configuration management
- Environment-specific settings
- Security and performance tuning

---

## ⚙️ Cài Đặt và Cấu Hình

### Dependencies Required

```bash
# Core dependencies
pip install requests
pip install selenium
pip install pillow

# OCR dependencies (optional cho CAPTCHA)
pip install opencv-python
pip install pytesseract

# Cài đặt Tesseract OCR
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# Windows: Download từ https://github.com/UB-Mannheim/tesseract/wiki
```

### Basic Configuration

```python
from vss_authentication import AuthConfig

# Cấu hình cơ bản
config = AuthConfig(
    base_url="http://vssapp.teca.vn:8088",
    use_proxy=True,
    proxy_host="ip.mproxy.vn",
    proxy_port=12301,
    proxy_user="your_username",
    proxy_pass="your_password",
    timeout=30,
    max_retries=5,
    session_timeout=3600
)
```

### Advanced Configuration

```python
# Cấu hình nâng cao cho production
config = AuthConfig(
    # Connection settings
    base_url="http://vssapp.teca.vn:8088",
    login_endpoint="/login",
    timeout=30,
    
    # Proxy settings
    use_proxy=True,
    proxy_host="ip.mproxy.vn",
    proxy_port=12301,
    proxy_user="beba111",
    proxy_pass="tDV5tkMchYUBMD",
    
    # Retry logic
    max_retries=5,
    retry_delay=2.0,
    
    # Session management
    session_timeout=3600,
    
    # CAPTCHA settings
    captcha_timeout=120,
    
    # Browser settings (for Selenium)
    headless=True
)
```

---

## 🚀 Sử Dụng Cơ Bản

### 1. Basic Authentication

```python
from vss_authentication import VSSAuthenticator, LoginCredentials

# Tạo authenticator
authenticator = VSSAuthenticator()

# Đăng nhập với default credentials
auth_session = authenticator.login()

if auth_session:
    print(f"✅ Đăng nhập thành công! Session: {auth_session.session_id}")
    
    # Sử dụng session để làm authenticated requests
    http_session = authenticator.get_authenticated_session(auth_session)
    
    # Đăng xuất khi hoàn thành
    authenticator.logout(auth_session)
else:
    print("❌ Đăng nhập thất bại")
```

### 2. Custom Credentials

```python
# Đăng nhập với credentials cụ thể
credentials = LoginCredentials(
    username="your_username",
    password="your_password"
)

auth_session = authenticator.login(credentials)
```

### 3. Session Reuse

```python
# Lưu session để sử dụng lại
session_id = auth_session.session_id

# Later...
# Khôi phục session
saved_session = authenticator.session_manager.get_session(session_id)

if saved_session and authenticator.verify_session(saved_session):
    print("✅ Session vẫn hoạt động")
    http_session = authenticator.get_authenticated_session(saved_session)
else:
    print("⚠️ Session đã hết hạn, cần đăng nhập lại")
```

---

## 🔧 Tính Năng Nâng Cao

### 1. Multiple Authentication Strategies

```python
# Strategy 1: Try default credentials first
authenticator = VSSAuthenticator()
auth_session = authenticator.try_default_credentials()

if not auth_session:
    # Strategy 2: Try custom credentials
    custom_credentials = [
        LoginCredentials("admin", "admin123"),
        LoginCredentials("user", "password"),
        # ... more credentials
    ]
    
    for cred in custom_credentials:
        auth_session = authenticator.login(cred)
        if auth_session:
            break

if not auth_session:
    # Strategy 3: Manual credential input
    username = input("Username: ")
    password = input("Password: ")
    auth_session = authenticator.login(LoginCredentials(username, password))
```

### 2. Concurrent Session Management

```python
import threading

def worker_with_auth(worker_id):
    # Mỗi worker có session riêng
    authenticator = VSSAuthenticator()
    auth_session = authenticator.login()
    
    if auth_session:
        try:
            # Thực hiện công việc với authenticated session
            http_session = authenticator.get_authenticated_session(auth_session)
            
            # Your work here...
            
        finally:
            # Cleanup
            authenticator.logout(auth_session)

# Tạo multiple workers
threads = []
for i in range(5):
    thread = threading.Thread(target=worker_with_auth, args=(i,))
    threads.append(thread)
    thread.start()

# Wait for completion
for thread in threads:
    thread.join()
```

### 3. Custom Authentication Flow

```python
class CustomVSSAuth(VSSAuthenticator):
    def custom_login_flow(self, credentials):
        """Custom authentication flow với additional steps"""
        
        # Step 1: Standard authentication
        auth_session = self.login(credentials)
        if not auth_session:
            return None
        
        # Step 2: Additional verification (if needed)
        if not self.perform_additional_verification(auth_session):
            self.logout(auth_session)
            return None
        
        # Step 3: Setup custom session data
        self.setup_custom_session_data(auth_session)
        
        return auth_session
    
    def perform_additional_verification(self, auth_session):
        """Thực hiện additional verification steps"""
        # Implementation specific to your needs
        return True
    
    def setup_custom_session_data(self, auth_session):
        """Setup custom data for session"""
        # Implementation specific to your needs
        pass
```

---

## 🧩 CAPTCHA Handling

### 1. Automatic CAPTCHA Detection

```python
from vss_authentication import CaptchaSolver

captcha_solver = CaptchaSolver(config)

# CAPTCHA được detect tự động trong login flow
html_content = get_login_page()
captcha_challenge = captcha_solver.detect_captcha(html_content)

if captcha_challenge:
    print("🧩 CAPTCHA detected!")
    print(f"Type: {captcha_challenge.challenge_type}")
    print(f"Difficulty: {captcha_challenge.difficulty}")
```

### 2. OCR-based Solving

```python
# OCR solving (requires vision libraries)
if captcha_challenge:
    solution = captcha_solver.solve_with_ocr(captcha_challenge)
    if solution:
        print(f"🔤 OCR solution: {solution}")
        credentials.captcha_solution = solution
```

### 3. Manual CAPTCHA Input

```python
# Manual solving fallback
if not solution:
    # CAPTCHA image sẽ được lưu tự động
    print("📂 CAPTCHA image saved to /workspace/tmp/captcha_manual.png")
    print("Please open the image and enter the solution:")
    
    manual_solution = captcha_solver.solve_manually(captcha_challenge)
    if manual_solution:
        credentials.captcha_solution = manual_solution
```

### 4. Custom CAPTCHA Solver

```python
class CustomCaptchaSolver(CaptchaSolver):
    def solve_with_custom_method(self, challenge):
        """Custom CAPTCHA solving method"""
        
        # Your custom logic here
        # Could integrate with external CAPTCHA solving services
        
        if challenge.challenge_type == "math":
            return self.solve_math_captcha(challenge)
        elif challenge.challenge_type == "image_selection":
            return self.solve_image_selection_captcha(challenge)
        else:
            return self.solve_with_ocr(challenge)
    
    def solve_math_captcha(self, challenge):
        """Solve mathematical CAPTCHA"""
        # Extract math expression from image
        # Calculate result
        pass
    
    def solve_image_selection_captcha(self, challenge):
        """Solve image selection CAPTCHA"""
        # Use computer vision to identify objects
        pass
```

---

## 💾 Session Management

### 1. Session Lifecycle

```python
# Tạo session
session_manager = SessionManager(config)
auth_session = session_manager.create_session(credentials)

# Cập nhật session với cookies mới
session_manager.update_session(
    auth_session.session_id, 
    new_cookies, 
    csrf_token
)

# Kiểm tra session validity
if session_manager.get_session(auth_session.session_id):
    print("Session vẫn hợp lệ")

# Vô hiệu hóa session
session_manager.invalidate_session(auth_session.session_id)
```

### 2. Session Persistence

```python
# Sessions được lưu tự động vào file
# /workspace/tmp/vss_sessions.pkl

# Manual save
session_manager.save_sessions()

# Manual load
session_manager.load_sessions()

# Cleanup expired sessions
session_manager.cleanup_expired_sessions()
```

### 3. Session Verification

```python
# Verify session còn active
is_valid = authenticator.verify_session(auth_session)

if not is_valid:
    print("Session expired, re-authenticating...")
    auth_session = authenticator.login(credentials)
```

### 4. Custom Session Data

```python
# Extend session với custom data
auth_session.additional_data = {
    'user_permissions': ['read', 'write'],
    'last_activity': datetime.now(),
    'custom_settings': {...}
}

# Save custom data
session_manager.save_sessions()
```

---

## 🔄 Error Handling & Retry Logic

### 1. Built-in Retry Logic

```python
# Retry configuration
config = AuthConfig(
    max_retries=5,           # Maximum retry attempts
    retry_delay=2.0,         # Base delay between retries
    timeout=30               # Request timeout
)

# Exponential backoff được apply tự động
# Retry 1: delay = 2.0s
# Retry 2: delay = 4.0s  
# Retry 3: delay = 8.0s
# etc.
```

### 2. Custom Error Handling

```python
class CustomAuthenticator(VSSAuthenticator):
    def login_with_custom_retry(self, credentials):
        """Login với custom retry logic"""
        
        for attempt in range(self.config.max_retries):
            try:
                auth_session = self.attempt_single_login(credentials)
                if auth_session:
                    return auth_session
                    
            except ConnectionError as e:
                self.logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < self.config.max_retries - 1:
                    self.wait_with_jitter(attempt)
                    
            except AuthenticationError as e:
                self.logger.error(f"Auth error: {e}")
                break  # Don't retry auth errors
                
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                
        return None
    
    def wait_with_jitter(self, attempt):
        """Wait với random jitter để avoid thundering herd"""
        base_delay = self.config.retry_delay * (2 ** attempt)
        jitter = random.uniform(0.1, 0.5)
        time.sleep(base_delay + jitter)
```

### 3. Error Recovery Strategies

```python
def resilient_authentication(credentials_list):
    """Authentication với multiple fallback strategies"""
    
    strategies = [
        # Strategy 1: Direct connection
        lambda: VSSAuthenticator(AuthConfig(use_proxy=False)),
        
        # Strategy 2: With proxy
        lambda: VSSAuthenticator(AuthConfig(use_proxy=True)),
        
        # Strategy 3: Different timeout
        lambda: VSSAuthenticator(AuthConfig(timeout=60)),
        
        # Strategy 4: Reduced retries
        lambda: VSSAuthenticator(AuthConfig(max_retries=2))
    ]
    
    for strategy in strategies:
        try:
            authenticator = strategy()
            for credentials in credentials_list:
                auth_session = authenticator.login(credentials)
                if auth_session:
                    return auth_session, authenticator
        except Exception as e:
            print(f"Strategy failed: {e}")
            continue
    
    return None, None
```

---

## 🔒 Security & Anti-Detection

### 1. User Agent Rotation

```python
# User agents được rotate tự động
# Có thể customize danh sách user agents

class SecurityEnhancedAuth(VSSAuthenticator):
    def __init__(self, config):
        super().__init__(config)
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...",
            # ... more user agents
        ]
    
    def get_random_user_agent(self):
        return random.choice(self.user_agents)
```

### 2. Request Timing & Rate Limiting

```python
import time
import random

class RateLimitedAuth(VSSAuthenticator):
    def __init__(self, config):
        super().__init__(config)
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
    
    def make_request_with_rate_limit(self, session, url, **kwargs):
        """Make request với rate limiting"""
        
        # Calculate wait time
        now = time.time()
        time_since_last = now - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            # Add random jitter
            wait_time += random.uniform(0.1, 0.5)
            time.sleep(wait_time)
        
        # Make request
        response = session.request(url=url, **kwargs)
        self.last_request_time = time.time()
        
        return response
```

### 3. Session Fingerprinting Avoidance

```python
class StealthAuthenticator(VSSAuthenticator):
    def create_http_session(self, auth_session):
        """Create session với stealth features"""
        session = super().create_http_session(auth_session)
        
        # Add realistic headers
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Random viewport size
        viewport_sizes = ['1920x1080', '1366x768', '1440x900', '1280x720']
        session.headers['Viewport'] = random.choice(viewport_sizes)
        
        return session
```

---

## 🧪 Testing & Debugging

### 1. Running Tests

```bash
# Chạy test suite đầy đủ
cd /workspace
python tests/test_vss_authentication.py

# Chạy specific test
python -c "
from tests.test_vss_authentication import VSSAuthenticationTester
tester = VSSAuthenticationTester()
tester.test_basic_login()
"
```

### 2. Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Run with detailed logging
config = AuthConfig()
authenticator = VSSAuthenticator(config)
auth_session = authenticator.login()
```

### 3. Manual Testing

```python
# Manual test với step-by-step verification
def manual_test():
    print("🧪 Manual Authentication Test")
    
    # Step 1: Create authenticator
    authenticator = VSSAuthenticator()
    print("✅ Authenticator created")
    
    # Step 2: Get login page
    auth_session = authenticator.session_manager.create_session(
        LoginCredentials("test", "test")
    )
    html_content, csrf_token = authenticator.get_login_page(auth_session)
    print(f"✅ Login page retrieved (CSRF: {bool(csrf_token)})")
    
    # Step 3: Check for CAPTCHA
    captcha_challenge = authenticator.captcha_solver.detect_captcha(html_content)
    print(f"✅ CAPTCHA check (Found: {bool(captcha_challenge)})")
    
    # Step 4: Attempt login
    credentials = LoginCredentials("admin", "admin")
    success = authenticator.attempt_login(credentials, auth_session, csrf_token)
    print(f"✅ Login attempt (Success: {success})")

manual_test()
```

### 4. Response Analysis

```python
# Analyze responses để debug login issues
def analyze_login_response(html_file):
    """Analyze saved login response"""
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Analyzing: {html_file}")
    print(f"📏 Content length: {len(content)}")
    
    # Check for common indicators
    indicators = {
        'success': ['dashboard', 'welcome', 'logout', 'menu'],
        'failure': ['error', 'invalid', 'wrong', 'failed'],
        'captcha': ['captcha', 'recaptcha', 'hcaptcha'],
        'csrf': ['_token', 'csrf']
    }
    
    for category, keywords in indicators.items():
        count = sum(content.lower().count(keyword) for keyword in keywords)
        print(f"🔍 {category.title()} indicators: {count}")

# Usage
analyze_login_response("/workspace/tmp/login_response_admin_failed_20250913_160530.html")
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. **"Connection refused" errors**

**Nguyên nhân:** VSS server không accessible hoặc proxy issues

**Giải pháp:**
```python
# Test connection without proxy
config = AuthConfig(use_proxy=False, timeout=60)
authenticator = VSSAuthenticator(config)

# Test với different base URL
config.base_url = "https://bhxh.vssid.vn"  # Try HTTPS version
```

#### 2. **"HTTP 500 Internal Server Error"**

**Nguyên nhân:** Server-side issues hoặc invalid request format

**Giải pháp:**
```python
# Check request format
config = AuthConfig()
config.max_retries = 1  # Reduce retries for faster debugging

# Enable detailed logging để see exact request được sent
import logging
logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)
```

#### 3. **"Session expired immediately"**

**Nguyên nhân:** Cookies không được persist đúng cách

**Giải pháp:**
```python
# Manual cookie debugging
def debug_cookies(auth_session):
    print("🍪 Session cookies:")
    for name, value in auth_session.cookies.items():
        print(f"  {name}: {value}")
    
    # Check cookie expiry
    print(f"📅 Session expires: {auth_session.expires_at}")
```

#### 4. **"CAPTCHA solving fails"**

**Nguyên nhân:** OCR không đọc được hoặc CAPTCHA too complex

**Giải pháp:**
```python
# Manual CAPTCHA debugging
captcha_solver = CaptchaSolver(config)

# Save CAPTCHA với better quality
challenge.image_data = download_captcha_with_better_quality()

# Try different OCR configs
for psm in [6, 7, 8, 13]:
    config = f'--psm {psm}'
    result = pytesseract.image_to_string(image, config=config)
    print(f"PSM {psm}: {result}")
```

#### 5. **"All default credentials fail"**

**Nguyên nhân:** VSS có authentication requirements khác

**Giải pháp:**
```python
# Analyze login page để understand requirements
html_content, _ = authenticator.get_login_page(auth_session)

# Look for hidden fields
import re
hidden_fields = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*>', html_content)
for field in hidden_fields:
    print(f"Hidden field: {field}")

# Check for additional form fields
form_fields = re.findall(r'<input[^>]*name=["\']([^"\']+)["\']', html_content)
print(f"Required fields: {form_fields}")
```

### Debug Tools

#### 1. **Response Saver**
```python
def save_all_responses(authenticator):
    """Intercept và save tất cả HTTP responses"""
    
    original_request = authenticator.create_http_session.request
    
    def logging_request(*args, **kwargs):
        response = original_request(*args, **kwargs)
        
        # Save response
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/workspace/tmp/debug_response_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"💾 Response saved: {filename}")
        return response
    
    authenticator.create_http_session.request = logging_request
```

#### 2. **Network Traffic Monitor**
```python
import requests
import sys

# Monitor all HTTP requests
def debug_requests():
    """Enable detailed HTTP request logging"""
    
    import logging
    import http.client as http_client
    
    http_client.HTTPConnection.debuglevel = 1
    
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

debug_requests()
```

---

## 📚 API Reference

### Core Classes

#### `VSSAuthenticator`

**Constructor:**
```python
VSSAuthenticator(config: Optional[AuthConfig] = None)
```

**Main Methods:**
- `login(credentials: Optional[LoginCredentials] = None) -> Optional[AuthSession]`
- `logout(auth_session: AuthSession) -> bool`
- `verify_session(auth_session: AuthSession) -> bool`
- `get_authenticated_session(auth_session: AuthSession) -> Optional[requests.Session]`

#### `SessionManager`

**Constructor:**
```python
SessionManager(config: AuthConfig)
```

**Methods:**
- `create_session(credentials: LoginCredentials) -> AuthSession`
- `get_session(session_id: str) -> Optional[AuthSession]`
- `update_session(session_id: str, cookies: Dict[str, str], csrf_token: Optional[str])`
- `invalidate_session(session_id: str)`
- `save_sessions()`
- `load_sessions()`

#### `CaptchaSolver`

**Constructor:**
```python
CaptchaSolver(config: AuthConfig)
```

**Methods:**
- `detect_captcha(html_content: str) -> Optional[CaptchaChallenge]`
- `solve(challenge: CaptchaChallenge, session: requests.Session) -> Optional[str]`
- `solve_with_ocr(challenge: CaptchaChallenge) -> Optional[str]`
- `solve_manually(challenge: CaptchaChallenge) -> Optional[str]`

### Data Classes

#### `AuthConfig`
```python
@dataclass
class AuthConfig:
    base_url: str = "http://vssapp.teca.vn:8088"
    login_endpoint: str = "/login"
    proxy_host: str = "ip.mproxy.vn"
    proxy_port: int = 12301
    proxy_user: str = "beba111"
    proxy_pass: str = "tDV5tkMchYUBMD"
    timeout: int = 30
    max_retries: int = 5
    retry_delay: float = 2.0
    session_timeout: int = 3600
    captcha_timeout: int = 120
    use_proxy: bool = True
    headless: bool = True
```

#### `LoginCredentials`
```python
@dataclass
class LoginCredentials:
    username: str
    password: str
    captcha_solution: Optional[str] = None
    additional_fields: Optional[Dict[str, str]] = None
```

#### `AuthSession`
```python
@dataclass
class AuthSession:
    session_id: str
    cookies: Dict[str, str]
    csrf_token: Optional[str]
    created_at: datetime
    expires_at: datetime
    is_valid: bool = True
    user_agent: str = ""
    proxy_used: Optional[str] = None
```

#### `CaptchaChallenge`
```python
@dataclass
class CaptchaChallenge:
    image_data: bytes
    image_url: Optional[str]
    challenge_type: str  # "text", "math", "image_selection"
    difficulty: str  # "easy", "medium", "hard"
    attempts_left: int = 3
    solution: Optional[str] = None
```

---

## 💡 Best Practices

### 1. **Authentication Strategy**
- Luôn sử dụng try-catch cho authentication calls
- Implement proper session verification trước khi sử dụng
- Có fallback plans cho authentication failures

### 2. **Resource Management**
- Luôn logout sessions khi hoàn thành
- Cleanup expired sessions định kỳ
- Monitor memory usage cho long-running applications

### 3. **Security**
- Không hard-code credentials trong source code
- Sử dụng environment variables cho sensitive config
- Enable proxy khi cần privacy protection

### 4. **Performance**
- Reuse sessions khi có thể
- Implement proper caching cho authentication tokens
- Monitor request rate để avoid being blocked

### 5. **Debugging**
- Enable logging trong development
- Save responses cho troubleshooting
- Use test suite để verify functionality

---

## 🔗 Related Resources

- **VSS Project Documentation**: `/workspace/docs/`
- **Configuration Files**: `/workspace/config/vss_config.yaml`
- **Test Suite**: `/workspace/tests/test_vss_authentication.py`
- **Log Files**: `/workspace/logs/vss_auth.log`
- **Session Storage**: `/workspace/tmp/vss_sessions.pkl`

---

**Phiên bản:** 1.0  
**Cập nhật cuối:** 13/09/2025  
**Tác giả:** MiniMax Agent  

---

*Để được hỗ trợ thêm hoặc báo cáo bugs, vui lòng tạo issue trong project repository.*
