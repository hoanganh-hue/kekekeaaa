#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Browser Automation Framework
================================

Production-ready browser automation framework cho VSS integration
Hỗ trợ anti-detection, user agent rotation, headless mode và error handling.

Author: VSS Integration Team
Created: 2025-09-13
"""

import os
import sys
import json
import time
import random
import logging
import traceback
from typing import Optional, Dict, List, Any, Union
from pathlib import Path
from datetime import datetime, timedelta

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementClickInterceptedException,
    ElementNotInteractableException
)

# Third-party imports
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from fake_useragent import UserAgent


class VSSBrowserAutomationError(Exception):
    """Custom exception cho VSS Browser Automation"""
    pass


class BrowserConfig:
    """Configuration class cho browser settings"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "/workspace/config/vss_config.yaml"
        self.load_config()
    
    def load_config(self):
        """Load configuration từ file"""
        default_config = {
            'browser': {
                'type': 'chrome',  # chrome hoặc firefox
                'headless': True,
                'window_size': [1366, 768],
                'timeout': 30,
                'page_load_timeout': 60,
                'implicit_wait': 10
            },
            'anti_detection': {
                'enable_user_agent_rotation': True,
                'enable_viewport_rotation': True,
                'enable_random_delays': True,
                'min_delay': 1,
                'max_delay': 3
            },
            'vss': {
                'base_url': 'https://bhxh.vssid.vn',
                'login_url': 'https://bhxh.vssid.vn/login',
                'lookup_url': 'https://bhxh.vssid.vn/tracuu'
            },
            'screenshot': {
                'enabled': True,
                'path': '/workspace/browser/screenshots',
                'format': 'png',
                'quality': 95
            },
            'logging': {
                'level': 'INFO',
                'file': '/workspace/logs/browser_automation.log'
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                import yaml
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    # Merge với default config
                    self.config = self._merge_config(default_config, config)
            else:
                self.config = default_config
        except Exception as e:
            logging.warning(f"Không thể load config từ {self.config_path}: {e}")
            self.config = default_config
    
    def _merge_config(self, default: dict, user: dict) -> dict:
        """Merge user config với default config"""
        result = default.copy()
        for key, value in user.items():
            if isinstance(value, dict) and key in result:
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default=None):
        """Get config value bằng dot notation"""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default


class VSSBrowserAutomation:
    """
    Production-ready Browser Automation Framework cho VSS Integration
    
    Features:
    - Anti-detection mechanisms 
    - User agent rotation
    - Headless mode support
    - Screenshot capturing
    - Comprehensive error handling
    - Network timeout management
    """
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        """
        Initialize VSS Browser Automation
        
        Args:
            config: BrowserConfig instance hoặc None để sử dụng default
        """
        self.config = config or BrowserConfig()
        self.driver: Optional[webdriver.Chrome] = None
        self.user_agents = []
        self.session_id = None
        self.start_time = None
        
        # Setup logging
        self._setup_logging()
        
        # Load user agents
        self._load_user_agents()
        
        # Ensure screenshot directory exists
        os.makedirs(self.config.get('screenshot.path'), exist_ok=True)
        
        self.logger.info("VSS Browser Automation Framework initialized")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('logging.level', 'INFO'))
        log_file = self.config.get('logging.file')
        
        # Ensure log directory exists
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file) if log_file else logging.NullHandler(),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _load_user_agents(self):
        """Load danh sách user agents cho rotation"""
        try:
            ua = UserAgent()
            # Tạo danh sách user agents đa dạng
            self.user_agents = [
                ua.chrome,
                ua.firefox,
                ua.safari,
                ua.edge
            ]
        except Exception as e:
            self.logger.warning(f"Không thể load user agents động: {e}")
            # Fallback user agents
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
            ]
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent để tránh detection"""
        return random.choice(self.user_agents)
    
    def _get_chrome_options(self) -> ChromeOptions:
        """Tạo Chrome options với anti-detection features"""
        options = ChromeOptions()
        
        # Basic options
        if self.config.get('browser.headless'):
            options.add_argument('--headless')
        
        # Window size
        window_size = self.config.get('browser.window_size', [1366, 768])
        options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')
        
        # Essential options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # User agent rotation
        if self.config.get('anti_detection.enable_user_agent_rotation'):
            user_agent = self._get_random_user_agent()
            options.add_argument(f'--user-agent={user_agent}')
            self.logger.debug(f"Using User Agent: {user_agent}")
        
        return options
    
    def _get_firefox_options(self) -> FirefoxOptions:
        """Tạo Firefox options với anti-detection features"""
        options = FirefoxOptions()
        
        if self.config.get('browser.headless'):
            options.add_argument('--headless')
        
        # User agent rotation
        if self.config.get('anti_detection.enable_user_agent_rotation'):
            user_agent = self._get_random_user_agent()
            options.set_preference("general.useragent.override", user_agent)
        
        # Additional preferences
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)
        
        return options
    
    def start_browser(self, browser_type: Optional[str] = None) -> bool:
        """
        Khởi động browser với configuration đã setup
        
        Args:
            browser_type: 'chrome' hoặc 'firefox', nếu None sẽ dùng từ config
            
        Returns:
            bool: True nếu khởi động thành công
        """
        try:
            browser_type = browser_type or self.config.get('browser.type', 'chrome')
            
            if browser_type.lower() == 'chrome':
                self._start_chrome()
            elif browser_type.lower() == 'firefox':
                self._start_firefox()
            else:
                raise VSSBrowserAutomationError(f"Unsupported browser type: {browser_type}")
            
            # Set timeouts
            self.driver.set_page_load_timeout(self.config.get('browser.page_load_timeout', 60))
            self.driver.implicitly_wait(self.config.get('browser.implicit_wait', 10))
            
            # Execute stealth scripts
            self._execute_stealth_scripts()
            
            self.session_id = self.driver.session_id
            self.start_time = datetime.now()
            
            self.logger.info(f"Browser {browser_type} started successfully. Session ID: {self.session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start browser: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _start_chrome(self):
        """Start Chrome browser với undetected-chromedriver"""
        try:
            options = self._get_chrome_options()
            
            # Set Chrome binary path to chromium
            options.binary_location = "/usr/bin/chromium"
            
            # Try với undetected-chromedriver trước
            try:
                self.driver = uc.Chrome(options=options, version_main=None)
                self.logger.info("Using undetected-chromedriver")
            except Exception as e:
                self.logger.warning(f"Undetected Chrome failed: {e}, fallback to regular Chrome")
                # Fallback to regular ChromeDriver
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                
        except Exception as e:
            raise VSSBrowserAutomationError(f"Failed to start Chrome: {str(e)}")
    
    def _start_firefox(self):
        """Start Firefox browser"""
        try:
            options = self._get_firefox_options()
            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
            
        except Exception as e:
            raise VSSBrowserAutomationError(f"Failed to start Firefox: {str(e)}")
    
    def _execute_stealth_scripts(self):
        """Execute JavaScript để ẩn dấu vết automation"""
        stealth_scripts = [
            # Ẩn webdriver property
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
            
            # Fake chrome object
            """
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            """,
            
            # Override permissions
            """
            const originalQuery = window.navigator.permissions.query;
            return window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """,
            
            # Mock plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            """
        ]
        
        for script in stealth_scripts:
            try:
                self.driver.execute_script(script)
            except Exception as e:
                self.logger.debug(f"Failed to execute stealth script: {e}")
    
    def navigate_to(self, url: str, timeout: Optional[int] = None) -> bool:
        """
        Navigate đến URL với error handling
        
        Args:
            url: URL để navigate
            timeout: Custom timeout, nếu None sẽ dùng từ config
            
        Returns:
            bool: True nếu navigate thành công
        """
        if not self.driver:
            self.logger.error("Browser not started. Call start_browser() first.")
            return False
        
        try:
            timeout = timeout or self.config.get('browser.timeout', 30)
            
            self.logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Random delay để tránh detection
            if self.config.get('anti_detection.enable_random_delays'):
                self._random_delay()
            
            self.logger.info(f"Successfully navigated to: {url}")
            return True
            
        except TimeoutException:
            self.logger.error(f"Timeout navigating to {url}")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to {url}: {str(e)}")
            return False
    
    def find_element(self, by: By, value: str, timeout: Optional[int] = None) -> Optional[Any]:
        """
        Tìm element với explicit wait
        
        Args:
            by: By locator type
            value: Locator value
            timeout: Wait timeout
            
        Returns:
            WebElement hoặc None nếu không tìm thấy
        """
        if not self.driver:
            self.logger.error("Browser not started")
            return None
        
        try:
            timeout = timeout or self.config.get('browser.timeout', 30)
            
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            
            self.logger.debug(f"Found element: {by}='{value}'")
            return element
            
        except TimeoutException:
            self.logger.error(f"Element not found within {timeout}s: {by}='{value}'")
            return None
        except Exception as e:
            self.logger.error(f"Error finding element {by}='{value}': {str(e)}")
            return None
    
    def find_elements(self, by: By, value: str, timeout: Optional[int] = None) -> List[Any]:
        """
        Tìm multiple elements
        
        Args:
            by: By locator type
            value: Locator value
            timeout: Wait timeout
            
        Returns:
            List of WebElements
        """
        if not self.driver:
            self.logger.error("Browser not started")
            return []
        
        try:
            timeout = timeout or self.config.get('browser.timeout', 30)
            
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            
            elements = self.driver.find_elements(by, value)
            self.logger.debug(f"Found {len(elements)} elements: {by}='{value}'")
            return elements
            
        except TimeoutException:
            self.logger.warning(f"No elements found within {timeout}s: {by}='{value}'")
            return []
        except Exception as e:
            self.logger.error(f"Error finding elements {by}='{value}': {str(e)}")
            return []
    
    def click_element(self, by: By, value: str, timeout: Optional[int] = None) -> bool:
        """
        Click element với retry logic
        
        Args:
            by: By locator type
            value: Locator value 
            timeout: Wait timeout
            
        Returns:
            bool: True nếu click thành công
        """
        element = self.find_element(by, value, timeout)
        if not element:
            return False
        
        try:
            # Wait for element to be clickable
            timeout = timeout or self.config.get('browser.timeout', 30)
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            
            # Try normal click first
            element.click()
            
            self.logger.debug(f"Clicked element: {by}='{value}'")
            self._random_delay()
            return True
            
        except ElementClickInterceptedException:
            try:
                # Try JavaScript click if normal click fails
                self.driver.execute_script("arguments[0].click();", element)
                self.logger.debug(f"JavaScript clicked element: {by}='{value}'")
                self._random_delay()
                return True
            except Exception as e:
                self.logger.error(f"JavaScript click failed: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error clicking element {by}='{value}': {str(e)}")
            return False
    
    def fill_form_field(self, by: By, value: str, text: str, clear_first: bool = True, timeout: Optional[int] = None) -> bool:
        """
        Điền text vào form field
        
        Args:
            by: By locator type
            value: Locator value
            text: Text để điền
            clear_first: Clear field trước khi điền
            timeout: Wait timeout
            
        Returns:
            bool: True nếu điền thành công
        """
        element = self.find_element(by, value, timeout)
        if not element:
            return False
        
        try:
            # Wait for element to be interactable
            timeout = timeout or self.config.get('browser.timeout', 30)
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            
            if clear_first:
                element.clear()
            
            # Simulate human typing
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))  # Random typing speed
            
            self.logger.debug(f"Filled form field {by}='{value}' with text: '{text[:20]}...'")
            self._random_delay()
            return True
            
        except Exception as e:
            self.logger.error(f"Error filling form field {by}='{value}': {str(e)}")
            return False
    
    def submit_form(self, by: By, value: str, timeout: Optional[int] = None) -> bool:
        """
        Submit form
        
        Args:
            by: By locator type for form hoặc submit button
            value: Locator value
            timeout: Wait timeout
            
        Returns:
            bool: True nếu submit thành công
        """
        element = self.find_element(by, value, timeout)
        if not element:
            return False
        
        try:
            # Try submit method first
            if element.tag_name.lower() == 'form':
                element.submit()
            else:
                # If not form, try click (for submit buttons)
                element.click()
            
            self.logger.debug(f"Submitted form: {by}='{value}'")
            self._random_delay()
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting form {by}='{value}': {str(e)}")
            return False
    
    def select_dropdown_option(self, by: By, value: str, option_text: Optional[str] = None, 
                             option_value: Optional[str] = None, option_index: Optional[int] = None,
                             timeout: Optional[int] = None) -> bool:
        """
        Select option từ dropdown
        
        Args:
            by: By locator type
            value: Locator value
            option_text: Text của option
            option_value: Value của option  
            option_index: Index của option
            timeout: Wait timeout
            
        Returns:
            bool: True nếu select thành công
        """
        element = self.find_element(by, value, timeout)
        if not element:
            return False
        
        try:
            select = Select(element)
            
            if option_text:
                select.select_by_visible_text(option_text)
                self.logger.debug(f"Selected by text: {option_text}")
            elif option_value:
                select.select_by_value(option_value)
                self.logger.debug(f"Selected by value: {option_value}")
            elif option_index is not None:
                select.select_by_index(option_index)
                self.logger.debug(f"Selected by index: {option_index}")
            else:
                self.logger.error("No selection criteria provided")
                return False
            
            self._random_delay()
            return True
            
        except Exception as e:
            self.logger.error(f"Error selecting dropdown option: {str(e)}")
            return False
    
    def wait_for_element(self, by: By, value: str, condition: str = 'presence', 
                        timeout: Optional[int] = None) -> bool:
        """
        Wait cho element với different conditions
        
        Args:
            by: By locator type
            value: Locator value
            condition: 'presence', 'visible', 'clickable', 'invisible'
            timeout: Wait timeout
            
        Returns:
            bool: True nếu condition được thỏa mãn
        """
        if not self.driver:
            return False
        
        try:
            timeout = timeout or self.config.get('browser.timeout', 30)
            
            if condition == 'presence':
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
            elif condition == 'visible':
                WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by, value))
                )
            elif condition == 'clickable':
                WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, value))
                )
            elif condition == 'invisible':
                WebDriverWait(self.driver, timeout).until(
                    EC.invisibility_of_element_located((by, value))
                )
            else:
                self.logger.error(f"Unknown condition: {condition}")
                return False
            
            self.logger.debug(f"Element condition '{condition}' met: {by}='{value}'")
            return True
            
        except TimeoutException:
            self.logger.error(f"Timeout waiting for element {condition}: {by}='{value}'")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for element: {str(e)}")
            return False
    
    def take_screenshot(self, filename: Optional[str] = None, element: Any = None) -> Optional[str]:
        """
        Chụp screenshot cho debugging
        
        Args:
            filename: Custom filename, nếu None sẽ auto-generate
            element: WebElement to screenshot (nếu None sẽ chụp full page)
            
        Returns:
            str: Path to screenshot file hoặc None nếu failed
        """
        if not self.driver:
            self.logger.error("Browser not started")
            return None
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"vss_screenshot_{timestamp}.png"
            
            if not filename.endswith('.png'):
                filename += '.png'
            
            screenshot_path = os.path.join(self.config.get('screenshot.path'), filename)
            
            if element:
                # Screenshot specific element
                element.screenshot(screenshot_path)
            else:
                # Full page screenshot
                self.driver.save_screenshot(screenshot_path)
            
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return None
    
    def get_page_source(self) -> Optional[str]:
        """
        Get page source HTML
        
        Returns:
            str: HTML source hoặc None nếu failed
        """
        if not self.driver:
            return None
        
        try:
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Error getting page source: {str(e)}")
            return None
    
    def execute_javascript(self, script: str, *args) -> Any:
        """
        Execute JavaScript code
        
        Args:
            script: JavaScript code
            *args: Arguments cho script
            
        Returns:
            Result của JavaScript execution
        """
        if not self.driver:
            return None
        
        try:
            result = self.driver.execute_script(script, *args)
            self.logger.debug(f"Executed JavaScript: {script[:100]}...")
            return result
        except Exception as e:
            self.logger.error(f"Error executing JavaScript: {str(e)}")
            return None
    
    def check_network_connectivity(self) -> bool:
        """
        Check network connectivity
        
        Returns:
            bool: True nếu có kết nối
        """
        try:
            # Try to navigate to a simple page
            self.driver.get("data:text/html,<html><body>Network test</body></html>")
            return True
        except Exception as e:
            self.logger.error(f"Network connectivity check failed: {str(e)}")
            return False
    
    def test_vss_connection(self) -> Dict[str, Any]:
        """
        Test basic connection tới VSS website
        
        Returns:
            dict: Test results với status và metrics
        """
        test_results = {
            'success': False,
            'url': self.config.get('vss.base_url'),
            'response_time': None,
            'status_code': None,
            'page_title': None,
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }
        
        if not self.driver:
            test_results['errors'].append('Browser not started')
            return test_results
        
        try:
            start_time = time.time()
            
            # Navigate to VSS base URL
            vss_url = self.config.get('vss.base_url')
            self.logger.info(f"Testing connection to VSS: {vss_url}")
            
            if not self.navigate_to(vss_url):
                test_results['errors'].append('Failed to navigate to VSS URL')
                return test_results
            
            # Calculate response time
            response_time = time.time() - start_time
            test_results['response_time'] = round(response_time, 2)
            
            # Get page title
            test_results['page_title'] = self.driver.title
            
            # Check for common VSS elements
            vss_indicators = [
                (By.PARTIAL_LINK_TEXT, "Bảo hiểm xã hội"),
                (By.PARTIAL_LINK_TEXT, "VSS"),
                (By.ID, "main"),
                (By.CLASS_NAME, "header")
            ]
            
            found_indicators = 0
            for by, value in vss_indicators:
                if self.find_element(by, value, timeout=5):
                    found_indicators += 1
            
            # Take screenshot for debugging
            screenshot_path = self.take_screenshot("vss_connection_test.png")
            if screenshot_path:
                test_results['screenshot'] = screenshot_path
            
            # Success criteria
            if found_indicators >= 1 and response_time < 30:
                test_results['success'] = True
                self.logger.info(f"VSS connection test successful. Response time: {response_time}s")
            else:
                test_results['errors'].append(f"Failed success criteria. Indicators: {found_indicators}, Response time: {response_time}")
            
        except Exception as e:
            test_results['errors'].append(f"Connection test error: {str(e)}")
            self.logger.error(f"VSS connection test failed: {str(e)}")
        
        return test_results
    
    def _random_delay(self):
        """Random delay để mimic human behavior"""
        if self.config.get('anti_detection.enable_random_delays'):
            min_delay = self.config.get('anti_detection.min_delay', 1)
            max_delay = self.config.get('anti_detection.max_delay', 3)
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get thông tin session hiện tại
        
        Returns:
            dict: Session information
        """
        info = {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': None,
            'current_url': None,
            'window_handles': None,
            'browser_version': None
        }
        
        if self.driver:
            try:
                if self.start_time:
                    uptime = datetime.now() - self.start_time
                    info['uptime'] = str(uptime)
                
                info['current_url'] = self.driver.current_url
                info['window_handles'] = len(self.driver.window_handles)
                
                # Get browser capabilities
                caps = self.driver.capabilities
                info['browser_version'] = caps.get('browserVersion', 'Unknown')
                
            except Exception as e:
                self.logger.error(f"Error getting session info: {str(e)}")
        
        return info
    
    def close_browser(self):
        """
        Safely close browser và clean up resources
        """
        if self.driver:
            try:
                session_info = self.get_session_info()
                self.logger.info(f"Closing browser session: {session_info}")
                
                self.driver.quit()
                self.driver = None
                self.session_id = None
                self.start_time = None
                
                self.logger.info("Browser closed successfully")
                
            except Exception as e:
                self.logger.error(f"Error closing browser: {str(e)}")
    
    def __enter__(self):
        """Context manager enter"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_browser()


def main():
    """
    Main function for testing framework
    """
    print("=== VSS Browser Automation Framework Test ===")
    
    try:
        # Initialize với default config
        config = BrowserConfig()
        
        with VSSBrowserAutomation(config) as automation:
            # Start browser
            print("Khởi động browser...")
            if not automation.start_browser():
                print("❌ Failed to start browser")
                return
            
            print("✅ Browser started successfully")
            
            # Test VSS connection
            print("\nTesting VSS connection...")
            test_results = automation.test_vss_connection()
            
            print(f"Test Results:")
            print(f"  Success: {'✅' if test_results['success'] else '❌'}")
            print(f"  Response Time: {test_results['response_time']}s")
            print(f"  Page Title: {test_results['page_title']}")
            
            if test_results['errors']:
                print(f"  Errors: {', '.join(test_results['errors'])}")
            
            # Session info
            print(f"\nSession Info:")
            session_info = automation.get_session_info()
            for key, value in session_info.items():
                print(f"  {key}: {value}")
    
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
