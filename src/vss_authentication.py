#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Authentication & CAPTCHA Handling Module
============================================

Module này cung cấp hệ thống authentication và CAPTCHA handling toàn diện cho VSS Portal.

Tính năng chính:
- Login flow với username/password  
- CAPTCHA detection và solving (OCR + manual input)
- Session management và cookie persistence
- Authentication failures và retry logic
- Multiple authentication strategies
- Security measures và anti-detection

Tác giả: MiniMax Agent
Ngày tạo: 13/09/2025
"""

import os
import sys
import time
import json
import pickle
import logging
import requests
import base64
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
import random
import hashlib
from datetime import datetime, timedelta
import threading
import queue

try:
    from PIL import Image
    import cv2
    import numpy as np
    import pytesseract
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    logging.warning("Vision libraries không khả dụng. CAPTCHA OCR sẽ không hoạt động.")

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium không khả dụng. Browser automation sẽ không hoạt động.")


@dataclass
class AuthConfig:
    """Cấu hình authentication"""
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


@dataclass
class LoginCredentials:
    """Thông tin đăng nhập"""
    username: str
    password: str
    captcha_solution: Optional[str] = None
    additional_fields: Optional[Dict[str, str]] = None


@dataclass
class AuthSession:
    """Session authentication"""
    session_id: str
    cookies: Dict[str, str]
    csrf_token: Optional[str]
    created_at: datetime
    expires_at: datetime
    is_valid: bool = True
    user_agent: str = ""
    proxy_used: Optional[str] = None


@dataclass
class CaptchaChallenge:
    """CAPTCHA challenge information"""
    image_data: bytes
    image_url: Optional[str]
    challenge_type: str  # "text", "math", "image_selection"
    difficulty: str  # "easy", "medium", "hard"
    attempts_left: int = 3
    solution: Optional[str] = None


class CaptchaSolver:
    """CAPTCHA solver với multiple strategies"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.CaptchaSolver")
        
    def detect_captcha(self, html_content: str) -> Optional[CaptchaChallenge]:
        """Phát hiện CAPTCHA trong HTML content"""
        self.logger.info("🔍 Phát hiện CAPTCHA trong trang...")
        
        # Patterns for CAPTCHA detection
        captcha_patterns = [
            r'<img[^>]*captcha[^>]*src=["\']([^"\']+)["\']',
            r'<input[^>]*captcha[^>]*',
            r'data-captcha[^>]*',
            r'recaptcha',
            r'hcaptcha'
        ]
        
        import re
        for pattern in captcha_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                self.logger.info(f"✅ Phát hiện CAPTCHA pattern: {pattern}")
                
                # Tạo CaptchaChallenge object
                challenge = CaptchaChallenge(
                    image_data=b"",  # Sẽ được load sau
                    image_url=matches[0] if matches else None,
                    challenge_type="text",  # Default
                    difficulty="medium",
                    attempts_left=3
                )
                
                return challenge
        
        self.logger.info("❌ Không phát hiện CAPTCHA")
        return None
    
    def download_captcha_image(self, challenge: CaptchaChallenge, session: requests.Session) -> bool:
        """Download CAPTCHA image"""
        if not challenge.image_url:
            return False
            
        try:
            self.logger.info(f"📥 Downloading CAPTCHA image: {challenge.image_url}")
            
            # Handle relative URLs
            if challenge.image_url.startswith('/'):
                challenge.image_url = urljoin(self.config.base_url, challenge.image_url)
            
            response = session.get(challenge.image_url, timeout=self.config.timeout)
            response.raise_for_status()
            
            challenge.image_data = response.content
            self.logger.info(f"✅ Downloaded CAPTCHA image ({len(challenge.image_data)} bytes)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi download CAPTCHA image: {e}")
            return False
    
    def solve_with_ocr(self, challenge: CaptchaChallenge) -> Optional[str]:
        """Giải CAPTCHA bằng OCR"""
        if not VISION_AVAILABLE:
            self.logger.warning("⚠️ Vision libraries không khả dụng cho OCR")
            return None
            
        if not challenge.image_data:
            self.logger.error("❌ Không có image data để OCR")
            return None
            
        try:
            self.logger.info("🔤 Giải CAPTCHA bằng OCR...")
            
            # Load image
            image = Image.open(BytesIO(challenge.image_data))
            
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance image for better OCR
            image_array = np.array(image)
            
            # Apply filters to improve OCR accuracy
            # Threshold
            _, image_array = cv2.threshold(image_array, 127, 255, cv2.THRESH_BINARY)
            
            # Noise reduction
            image_array = cv2.medianBlur(image_array, 3)
            
            # Convert back to PIL Image
            enhanced_image = Image.fromarray(image_array)
            
            # Save for debugging
            debug_path = "/workspace/tmp/captcha_debug.png"
            os.makedirs(os.path.dirname(debug_path), exist_ok=True)
            enhanced_image.save(debug_path)
            self.logger.info(f"💾 Đã lưu CAPTCHA debug image: {debug_path}")
            
            # OCR with different configurations
            configs = [
                '--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                '--psm 7 -c tessedit_char_whitelist=0123456789',
                '--psm 6',
                '--psm 8'
            ]
            
            for config in configs:
                try:
                    text = pytesseract.image_to_string(enhanced_image, config=config).strip()
                    if text and len(text) >= 3:  # Minimum reasonable length
                        self.logger.info(f"✅ OCR result với config '{config}': '{text}'")
                        challenge.solution = text
                        return text
                except Exception as e:
                    self.logger.debug(f"OCR config failed: {config} - {e}")
                    continue
            
            self.logger.warning("⚠️ OCR không thể đọc được CAPTCHA")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi OCR CAPTCHA: {e}")
            return None
    
    def solve_manually(self, challenge: CaptchaChallenge) -> Optional[str]:
        """Giải CAPTCHA thủ công (manual input)"""
        try:
            self.logger.info("👤 Yêu cầu giải CAPTCHA thủ công...")
            
            # Save CAPTCHA image for user to see
            if challenge.image_data:
                manual_path = "/workspace/tmp/captcha_manual.png"
                os.makedirs(os.path.dirname(manual_path), exist_ok=True)
                
                with open(manual_path, 'wb') as f:
                    f.write(challenge.image_data)
                
                self.logger.info(f"💾 CAPTCHA image đã lưu tại: {manual_path}")
                print(f"\n🖼️  CAPTCHA image đã lưu tại: {manual_path}")
                print("📂 Vui lòng mở file để xem CAPTCHA")
            
            # Manual input with timeout
            print(f"\n⏰ Bạn có {self.config.captcha_timeout} giây để nhập CAPTCHA...")
            print("🔤 Nhập solution CAPTCHA (hoặc 'skip' để bỏ qua): ", end="", flush=True)
            
            # Use threading for timeout
            result_queue = queue.Queue()
            
            def get_input():
                try:
                    user_input = input().strip()
                    result_queue.put(user_input)
                except:
                    result_queue.put("")
            
            input_thread = threading.Thread(target=get_input, daemon=True)
            input_thread.start()
            input_thread.join(timeout=self.config.captcha_timeout)
            
            if not result_queue.empty():
                solution = result_queue.get()
                if solution.lower() == 'skip':
                    self.logger.info("👤 User đã skip CAPTCHA")
                    return None
                elif solution:
                    self.logger.info(f"👤 User nhập CAPTCHA: '{solution}'")
                    challenge.solution = solution
                    return solution
            
            self.logger.warning("⏰ Timeout manual CAPTCHA input")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi manual CAPTCHA solving: {e}")
            return None
    
    def solve(self, challenge: CaptchaChallenge, session: requests.Session) -> Optional[str]:
        """Giải CAPTCHA với multiple strategies"""
        self.logger.info("🧩 Bắt đầu giải CAPTCHA...")
        
        # Download image if needed
        if challenge.image_url and not challenge.image_data:
            if not self.download_captcha_image(challenge, session):
                self.logger.error("❌ Không thể download CAPTCHA image")
                return None
        
        # Try OCR first
        if VISION_AVAILABLE:
            ocr_solution = self.solve_with_ocr(challenge)
            if ocr_solution:
                return ocr_solution
        
        # Fallback to manual input
        manual_solution = self.solve_manually(challenge)
        if manual_solution:
            return manual_solution
        
        self.logger.error("❌ Không thể giải CAPTCHA")
        return None


class SessionManager:
    """Quản lý session và cookies"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.SessionManager")
        self.sessions: Dict[str, AuthSession] = {}
        self.session_file = "/workspace/tmp/vss_sessions.pkl"
        
        # Load existing sessions
        self.load_sessions()
    
    def generate_session_id(self) -> str:
        """Tạo session ID unique"""
        timestamp = str(int(time.time()))
        random_data = str(random.randint(100000, 999999))
        return hashlib.md5(f"{timestamp}_{random_data}".encode()).hexdigest()
    
    def create_session(self, credentials: LoginCredentials) -> AuthSession:
        """Tạo session mới"""
        session_id = self.generate_session_id()
        now = datetime.now()
        expires_at = now + timedelta(seconds=self.config.session_timeout)
        
        auth_session = AuthSession(
            session_id=session_id,
            cookies={},
            csrf_token=None,
            created_at=now,
            expires_at=expires_at,
            is_valid=True,
            user_agent=self.generate_user_agent(),
            proxy_used=f"{self.config.proxy_host}:{self.config.proxy_port}" if self.config.use_proxy else None
        )
        
        self.sessions[session_id] = auth_session
        self.logger.info(f"✅ Tạo session mới: {session_id}")
        
        return auth_session
    
    def get_session(self, session_id: str) -> Optional[AuthSession]:
        """Lấy session theo ID"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        # Check expiry
        if datetime.now() > session.expires_at:
            self.logger.warning(f"⏰ Session {session_id} đã hết hạn")
            session.is_valid = False
            return None
        
        return session
    
    def update_session(self, session_id: str, cookies: Dict[str, str], csrf_token: Optional[str] = None):
        """Cập nhật session với cookies và token mới"""
        session = self.sessions.get(session_id)
        if session:
            session.cookies.update(cookies)
            if csrf_token:
                session.csrf_token = csrf_token
            self.logger.info(f"🔄 Cập nhật session {session_id}")
    
    def invalidate_session(self, session_id: str):
        """Vô hiệu hóa session"""
        session = self.sessions.get(session_id)
        if session:
            session.is_valid = False
            self.logger.info(f"❌ Vô hiệu hóa session {session_id}")
    
    def cleanup_expired_sessions(self):
        """Dọn dẹp sessions đã hết hạn"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if now > session.expires_at:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            self.logger.info(f"🗑️ Đã xóa expired session: {session_id}")
    
    def save_sessions(self):
        """Lưu sessions ra file"""
        try:
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            with open(self.session_file, 'wb') as f:
                pickle.dump(self.sessions, f)
            self.logger.debug("💾 Đã lưu sessions")
        except Exception as e:
            self.logger.error(f"❌ Lỗi lưu sessions: {e}")
    
    def load_sessions(self):
        """Load sessions từ file"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'rb') as f:
                    self.sessions = pickle.load(f)
                self.logger.debug("📂 Đã load sessions")
                
                # Cleanup expired sessions
                self.cleanup_expired_sessions()
        except Exception as e:
            self.logger.error(f"❌ Lỗi load sessions: {e}")
            self.sessions = {}
    
    def generate_user_agent(self) -> str:
        """Tạo User-Agent ngẫu nhiên để chống detection"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
        ]
        return random.choice(user_agents)


class VSSAuthenticator:
    """Main authentication class cho VSS Portal"""
    
    def __init__(self, config: Optional[AuthConfig] = None):
        self.config = config or AuthConfig()
        self.session_manager = SessionManager(self.config)
        self.captcha_solver = CaptchaSolver(self.config)
        self.logger = logging.getLogger(f"{__name__}.VSSAuthenticator")
        
        # Setup logging
        self.setup_logging()
        
        # Default credentials để thử
        self.default_credentials = [
            LoginCredentials("admin", "admin"),
            LoginCredentials("admin", "admin123"),
            LoginCredentials("administrator", "admin123"),
            LoginCredentials("user", "user123"),
            LoginCredentials("vss", "vss123"),
            LoginCredentials("bhxh", "bhxh123"),
            LoginCredentials("demo", "demo"),
            LoginCredentials("test", "test123")
        ]
    
    def setup_logging(self):
        """Setup logging cho authentication"""
        log_dir = "/workspace/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(f"{log_dir}/vss_auth.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)
    
    def create_http_session(self, auth_session: AuthSession) -> requests.Session:
        """Tạo HTTP session với cấu hình proxy và headers"""
        session = requests.Session()
        
        # Set user agent
        session.headers.update({
            'User-Agent': auth_session.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Set proxy if enabled
        if self.config.use_proxy:
            proxy_url = f"http://{self.config.proxy_user}:{self.config.proxy_pass}@{self.config.proxy_host}:{self.config.proxy_port}"
            session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            self.logger.info("🌐 Sử dụng proxy cho session")
        
        # Set cookies if available
        if auth_session.cookies:
            for name, value in auth_session.cookies.items():
                session.cookies.set(name, value)
        
        return session
    
    def extract_csrf_token(self, html_content: str) -> Optional[str]:
        """Trích xuất CSRF token từ HTML"""
        import re
        
        # Common CSRF token patterns
        patterns = [
            r'<meta\s+name=["\']csrf-token["\']\s+content=["\']([^"\']+)["\']',
            r'<input[^>]*name=["\']_token["\'][^>]*value=["\']([^"\']+)["\']',
            r'_token["\s]*[:=]["\s]*["\']([^"\']+)["\']',
            r'csrf_token["\s]*[:=]["\s]*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                token = matches[0]
                self.logger.info(f"🔑 Tìm thấy CSRF token: {token[:20]}...")
                return token
        
        self.logger.warning("⚠️ Không tìm thấy CSRF token")
        return None
    
    def get_login_page(self, auth_session: AuthSession) -> Tuple[Optional[str], Optional[str]]:
        """Lấy trang login và extract thông tin cần thiết"""
        session = self.create_http_session(auth_session)
        login_url = urljoin(self.config.base_url, self.config.login_endpoint)
        
        try:
            self.logger.info(f"📥 Lấy trang login: {login_url}")
            
            response = session.get(login_url, timeout=self.config.timeout)
            response.raise_for_status()
            
            self.logger.info(f"✅ Trang login OK (Status: {response.status_code}, Size: {len(response.content)})")
            
            # Extract CSRF token
            csrf_token = self.extract_csrf_token(response.text)
            
            # Update session cookies
            cookies = {cookie.name: cookie.value for cookie in response.cookies}
            self.session_manager.update_session(auth_session.session_id, cookies, csrf_token)
            
            return response.text, csrf_token
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi lấy trang login: {e}")
            return None, None
    
    def attempt_login(self, credentials: LoginCredentials, auth_session: AuthSession, csrf_token: Optional[str]) -> bool:
        """Thử đăng nhập với credentials"""
        session = self.create_http_session(auth_session)
        login_url = urljoin(self.config.base_url, self.config.login_endpoint)
        
        try:
            self.logger.info(f"🔐 Thử đăng nhập: {credentials.username} / {credentials.password}")
            
            # Prepare form data
            form_data = {
                'username': credentials.username,
                'password': credentials.password
            }
            
            # Add CSRF token if available
            if csrf_token:
                form_data['_token'] = csrf_token
            
            # Add CAPTCHA solution if available
            if credentials.captcha_solution:
                form_data['captcha'] = credentials.captcha_solution
                self.logger.info(f"🧩 Sử dụng CAPTCHA solution: {credentials.captcha_solution}")
            
            # Add additional fields
            if credentials.additional_fields:
                form_data.update(credentials.additional_fields)
            
            # Set headers
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': login_url,
                'Origin': self.config.base_url
            }
            
            # Make login request
            response = session.post(
                login_url,
                data=form_data,
                headers=headers,
                timeout=self.config.timeout,
                allow_redirects=True
            )
            
            self.logger.info(f"📊 Login response: Status {response.status_code}, Size {len(response.content)}")
            
            # Analyze response to determine success/failure
            success = self.analyze_login_response(response.text, response.url)
            
            if success:
                self.logger.info("🎉 ĐĂNG NHẬP THÀNH CÔNG!")
                
                # Update session với cookies mới
                cookies = {cookie.name: cookie.value for cookie in response.cookies}
                self.session_manager.update_session(auth_session.session_id, cookies)
                
                # Save successful response for analysis
                self.save_login_response(response.text, credentials.username, "success")
                
                return True
            else:
                self.logger.warning("❌ Đăng nhập thất bại")
                self.save_login_response(response.text, credentials.username, "failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Lỗi trong quá trình đăng nhập: {e}")
            return False
    
    def analyze_login_response(self, html_content: str, final_url: str) -> bool:
        """Phân tích response để xác định đăng nhập thành công hay thất bại"""
        content_lower = html_content.lower()
        
        # Success indicators
        success_indicators = [
            'dashboard', 'trang chủ', 'welcome', 'xin chào',
            'logout', 'đăng xuất', 'profile', 'hồ sơ',
            'menu', 'navigation', 'user-menu', 'settings',
            'cài đặt', 'thông tin cá nhân'
        ]
        
        # Failure indicators
        failure_indicators = [
            'error', 'lỗi', 'invalid', 'sai', 'wrong', 'failed',
            'incorrect', 'không đúng', 'thất bại', 'đăng nhập',
            'login', 'sign in', 'authentication failed'
        ]
        
        # Check for success indicators
        success_count = sum(1 for indicator in success_indicators if indicator in content_lower)
        failure_count = sum(1 for indicator in failure_indicators if indicator in content_lower)
        
        self.logger.debug(f"🔍 Success indicators: {success_count}, Failure indicators: {failure_count}")
        
        # URL-based analysis
        url_indicates_success = not any(x in final_url.lower() for x in ['login', 'sign-in', 'auth'])
        
        # Decision logic
        if success_count > 0 and success_count > failure_count:
            return True
        elif url_indicates_success and failure_count == 0:
            return True
        elif 'đăng nhập' in content_lower and len(html_content) < 10000:
            return False  # Likely redirected back to login
        else:
            return False
    
    def save_login_response(self, html_content: str, username: str, status: str):
        """Lưu response để debug và analysis"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/workspace/tmp/login_response_{username}_{status}_{timestamp}.html"
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"💾 Đã lưu login response: {filename}")
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi lưu login response: {e}")
    
    def login_with_retry(self, credentials: LoginCredentials, max_retries: Optional[int] = None) -> Optional[AuthSession]:
        """Đăng nhập với retry logic"""
        max_retries = max_retries or self.config.max_retries
        
        for attempt in range(max_retries):
            self.logger.info(f"🔄 Lần thử {attempt + 1}/{max_retries}")
            
            # Create new session for each attempt
            auth_session = self.session_manager.create_session(credentials)
            
            try:
                # Get login page
                html_content, csrf_token = self.get_login_page(auth_session)
                if not html_content:
                    self.logger.error("❌ Không thể lấy trang login")
                    continue
                
                # Check for CAPTCHA
                captcha_challenge = self.captcha_solver.detect_captcha(html_content)
                if captcha_challenge:
                    self.logger.info("🧩 Phát hiện CAPTCHA, đang giải...")
                    
                    session = self.create_http_session(auth_session)
                    captcha_solution = self.captcha_solver.solve(captcha_challenge, session)
                    
                    if not captcha_solution:
                        self.logger.warning("❌ Không thể giải CAPTCHA, skip attempt này")
                        continue
                    
                    credentials.captcha_solution = captcha_solution
                
                # Attempt login
                success = self.attempt_login(credentials, auth_session, csrf_token)
                
                if success:
                    self.session_manager.save_sessions()
                    return auth_session
                else:
                    self.session_manager.invalidate_session(auth_session.session_id)
                
            except Exception as e:
                self.logger.error(f"❌ Lỗi trong lần thử {attempt + 1}: {e}")
            
            # Wait before retry
            if attempt < max_retries - 1:
                delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                self.logger.info(f"⏱️ Chờ {delay:.1f}s trước khi thử lại...")
                time.sleep(delay)
        
        self.logger.error(f"❌ Đăng nhập thất bại sau {max_retries} lần thử")
        return None
    
    def try_default_credentials(self) -> Optional[AuthSession]:
        """Thử đăng nhập với các credentials mặc định"""
        self.logger.info("🔑 Thử đăng nhập với credentials mặc định...")
        
        for i, credentials in enumerate(self.default_credentials):
            self.logger.info(f"🔐 Thử credentials {i + 1}/{len(self.default_credentials)}: {credentials.username}")
            
            auth_session = self.login_with_retry(credentials)
            if auth_session:
                self.logger.info(f"🎉 THÀNH CÔNG với credentials: {credentials.username}/{credentials.password}")
                return auth_session
        
        self.logger.warning("❌ Tất cả default credentials đều thất bại")
        return None
    
    def login(self, credentials: Optional[LoginCredentials] = None) -> Optional[AuthSession]:
        """Main login method"""
        self.logger.info("🚀 BẮT ĐẦU QUÁ TRÌNH AUTHENTICATION VSS")
        
        if credentials:
            self.logger.info(f"🔐 Sử dụng credentials được cung cấp: {credentials.username}")
            return self.login_with_retry(credentials)
        else:
            self.logger.info("🔍 Thử các credentials mặc định...")
            return self.try_default_credentials()
    
    def verify_session(self, auth_session: AuthSession) -> bool:
        """Xác minh session còn hoạt động"""
        try:
            session = self.create_http_session(auth_session)
            
            # Try to access a protected page
            protected_url = urljoin(self.config.base_url, "/dashboard")
            response = session.get(protected_url, timeout=self.config.timeout)
            
            # Analyze response to check if still logged in
            is_authenticated = self.analyze_login_response(response.text, response.url)
            
            if is_authenticated:
                self.logger.info(f"✅ Session {auth_session.session_id} vẫn hoạt động")
                return True
            else:
                self.logger.warning(f"❌ Session {auth_session.session_id} đã hết hạn")
                self.session_manager.invalidate_session(auth_session.session_id)
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Lỗi verify session: {e}")
            return False
    
    def logout(self, auth_session: AuthSession) -> bool:
        """Đăng xuất"""
        try:
            session = self.create_http_session(auth_session)
            logout_url = urljoin(self.config.base_url, "/logout")
            
            response = session.get(logout_url, timeout=self.config.timeout)
            
            # Invalidate session
            self.session_manager.invalidate_session(auth_session.session_id)
            self.session_manager.save_sessions()
            
            self.logger.info(f"👋 Đã đăng xuất session {auth_session.session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi đăng xuất: {e}")
            return False
    
    def get_authenticated_session(self, auth_session: AuthSession) -> Optional[requests.Session]:
        """Lấy HTTP session đã authenticated để sử dụng cho các requests khác"""
        if not self.verify_session(auth_session):
            return None
        
        return self.create_http_session(auth_session)


def main():
    """Test function"""
    print("🔐 VSS Authentication Module Test")
    print("=" * 50)
    
    # Create authenticator
    config = AuthConfig()
    authenticator = VSSAuthenticator(config)
    
    # Test login
    auth_session = authenticator.login()
    
    if auth_session:
        print(f"✅ Đăng nhập thành công! Session ID: {auth_session.session_id}")
        
        # Test session verification
        if authenticator.verify_session(auth_session):
            print("✅ Session verification thành công")
        
        # Test logout
        if authenticator.logout(auth_session):
            print("✅ Đăng xuất thành công")
    else:
        print("❌ Đăng nhập thất bại")


if __name__ == "__main__":
    main()