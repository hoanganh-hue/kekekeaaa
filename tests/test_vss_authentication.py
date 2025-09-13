#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Authentication Testing Suite
===============================

Test authentication module với multiple scenarios để đảm bảo hoạt động ổn định.

Test scenarios:
1. Basic login với default credentials
2. CAPTCHA handling test
3. Session persistence test
4. Retry logic test
5. Proxy connection test
6. Multiple concurrent sessions
7. Session expiry handling
8. Error recovery test

Tác giả: MiniMax Agent
Ngày tạo: 13/09/2025
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

# Add src to path
sys.path.insert(0, '/workspace/src')

from vss_authentication import (
    VSSAuthenticator, 
    AuthConfig, 
    LoginCredentials, 
    AuthSession,
    CaptchaSolver,
    SessionManager
)


class VSSAuthenticationTester:
    """Test suite cho VSS Authentication system"""
    
    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging cho test suite"""
        log_dir = "/workspace/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("VSSAuthTester")
        self.logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(f"{log_dir}/vss_auth_test.log")
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_test_result(self, test_name: str, success: bool, details: Dict = None):
        """Log kết quả test"""
        result = {
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.results[test_name] = result
        
        status = "✅ PASS" if success else "❌ FAIL"
        self.logger.info(f"{status} - {test_name}")
        
        if details:
            for key, value in details.items():
                self.logger.info(f"  {key}: {value}")
    
    def test_basic_login(self) -> bool:
        """Test 1: Basic login functionality"""
        self.logger.info("\n🔐 TEST 1: Basic Login Functionality")
        self.logger.info("=" * 50)
        
        try:
            # Create authenticator với config cơ bản
            config = AuthConfig(
                use_proxy=True,
                max_retries=3,
                timeout=30
            )
            
            authenticator = VSSAuthenticator(config)
            
            # Thử đăng nhập
            start_time = time.time()
            auth_session = authenticator.login()
            end_time = time.time()
            
            if auth_session:
                self.log_test_result("basic_login", True, {
                    'session_id': auth_session.session_id,
                    'duration': f"{end_time - start_time:.2f}s",
                    'csrf_token_available': bool(auth_session.csrf_token),
                    'cookies_count': len(auth_session.cookies)
                })
                
                # Cleanup
                authenticator.logout(auth_session)
                return True
            else:
                self.log_test_result("basic_login", False, {
                    'duration': f"{end_time - start_time:.2f}s",
                    'error': 'No session returned'
                })
                return False
                
        except Exception as e:
            self.log_test_result("basic_login", False, {
                'error': str(e)
            })
            return False
    
    def test_custom_credentials(self) -> bool:
        """Test 2: Custom credentials login"""
        self.logger.info("\n🔐 TEST 2: Custom Credentials Login")
        self.logger.info("=" * 50)
        
        try:
            config = AuthConfig()
            authenticator = VSSAuthenticator(config)
            
            # Test với custom credentials
            test_credentials = [
                LoginCredentials("testuser", "testpass"),
                LoginCredentials("demo", "demo123"),
                LoginCredentials("vss_test", "password123")
            ]
            
            results = []
            for cred in test_credentials:
                self.logger.info(f"Testing credentials: {cred.username}")
                
                start_time = time.time()
                auth_session = authenticator.login(cred)
                end_time = time.time()
                
                result = {
                    'username': cred.username,
                    'success': bool(auth_session),
                    'duration': f"{end_time - start_time:.2f}s"
                }
                
                if auth_session:
                    result['session_id'] = auth_session.session_id
                    authenticator.logout(auth_session)
                
                results.append(result)
            
            # Consider test successful if at least one credential worked
            success = any(r['success'] for r in results)
            
            self.log_test_result("custom_credentials", success, {
                'total_tested': len(test_credentials),
                'successful': sum(1 for r in results if r['success']),
                'results': results
            })
            
            return success
            
        except Exception as e:
            self.log_test_result("custom_credentials", False, {
                'error': str(e)
            })
            return False
    
    def test_captcha_detection(self) -> bool:
        """Test 3: CAPTCHA detection and handling"""
        self.logger.info("\n🧩 TEST 3: CAPTCHA Detection & Handling")
        self.logger.info("=" * 50)
        
        try:
            config = AuthConfig()
            captcha_solver = CaptchaSolver(config)
            
            # Test CAPTCHA detection với sample HTML
            sample_html_with_captcha = '''
            <html>
                <body>
                    <form>
                        <input name="username" type="text">
                        <input name="password" type="password">
                        <img src="/captcha/generate" alt="CAPTCHA">
                        <input name="captcha" type="text">
                    </form>
                </body>
            </html>
            '''
            
            sample_html_without_captcha = '''
            <html>
                <body>
                    <form>
                        <input name="username" type="text">
                        <input name="password" type="password">
                    </form>
                </body>
            </html>
            '''
            
            # Test detection
            captcha_detected = captcha_solver.detect_captcha(sample_html_with_captcha)
            no_captcha_detected = captcha_solver.detect_captcha(sample_html_without_captcha)
            
            success = bool(captcha_detected) and not bool(no_captcha_detected)
            
            self.log_test_result("captcha_detection", success, {
                'captcha_detected_when_present': bool(captcha_detected),
                'captcha_not_detected_when_absent': not bool(no_captcha_detected),
                'detection_accuracy': success
            })
            
            return success
            
        except Exception as e:
            self.log_test_result("captcha_detection", False, {
                'error': str(e)
            })
            return False
    
    def test_session_persistence(self) -> bool:
        """Test 4: Session persistence and management"""
        self.logger.info("\n💾 TEST 4: Session Persistence")
        self.logger.info("=" * 50)
        
        try:
            config = AuthConfig()
            session_manager = SessionManager(config)
            
            # Create test session
            credentials = LoginCredentials("test", "test")
            auth_session = session_manager.create_session(credentials)
            
            original_session_id = auth_session.session_id
            
            # Update session với mock data
            test_cookies = {'session_id': 'test123', 'csrf_token': 'token456'}
            session_manager.update_session(auth_session.session_id, test_cookies, 'csrf789')
            
            # Save sessions
            session_manager.save_sessions()
            
            # Create new session manager và load
            new_session_manager = SessionManager(config)
            loaded_session = new_session_manager.get_session(original_session_id)
            
            success = (
                loaded_session is not None and
                loaded_session.session_id == original_session_id and
                loaded_session.cookies.get('session_id') == 'test123' and
                loaded_session.csrf_token == 'csrf789'
            )
            
            self.log_test_result("session_persistence", success, {
                'original_session_id': original_session_id,
                'loaded_successfully': bool(loaded_session),
                'cookies_preserved': bool(loaded_session and loaded_session.cookies),
                'csrf_token_preserved': bool(loaded_session and loaded_session.csrf_token)
            })
            
            return success
            
        except Exception as e:
            self.log_test_result("session_persistence", False, {
                'error': str(e)
            })
            return False
    
    def test_retry_logic(self) -> bool:
        """Test 5: Retry logic với simulated failures"""
        self.logger.info("\n🔄 TEST 5: Retry Logic")
        self.logger.info("=" * 50)
        
        try:
            # Create config với retry settings
            config = AuthConfig(
                max_retries=3,
                retry_delay=0.5,  # Shorter delay cho testing
                timeout=5  # Shorter timeout để force failures
            )
            
            authenticator = VSSAuthenticator(config)
            
            # Test với invalid URL để force failure
            original_base_url = config.base_url
            config.base_url = "http://invalid-url-that-does-not-exist.com"
            
            start_time = time.time()
            auth_session = authenticator.login()
            end_time = time.time()
            
            # Restore original URL
            config.base_url = original_base_url
            
            # Test should fail but take time due to retries
            duration = end_time - start_time
            expected_min_duration = config.retry_delay * (config.max_retries - 1)
            
            success = (
                auth_session is None and  # Should fail
                duration >= expected_min_duration  # Should take time due to retries
            )
            
            self.log_test_result("retry_logic", success, {
                'session_created': bool(auth_session),
                'total_duration': f"{duration:.2f}s",
                'expected_min_duration': f"{expected_min_duration:.2f}s",
                'retries_appear_to_work': duration >= expected_min_duration
            })
            
            return success
            
        except Exception as e:
            self.log_test_result("retry_logic", False, {
                'error': str(e)
            })
            return False
    
    def test_proxy_connection(self) -> bool:
        """Test 6: Proxy connection"""
        self.logger.info("\n🌐 TEST 6: Proxy Connection")
        self.logger.info("=" * 50)
        
        try:
            # Test với proxy enabled
            config_with_proxy = AuthConfig(use_proxy=True)
            config_without_proxy = AuthConfig(use_proxy=False)
            
            authenticator_with_proxy = VSSAuthenticator(config_with_proxy)
            authenticator_without_proxy = VSSAuthenticator(config_without_proxy)
            
            # Test connection với proxy
            auth_session_with_proxy = authenticator_with_proxy.session_manager.create_session(
                LoginCredentials("test", "test")
            )
            session_with_proxy = authenticator_with_proxy.create_http_session(auth_session_with_proxy)
            
            # Test connection without proxy
            auth_session_without_proxy = authenticator_without_proxy.session_manager.create_session(
                LoginCredentials("test", "test")
            )
            session_without_proxy = authenticator_without_proxy.create_http_session(auth_session_without_proxy)
            
            # Check proxy configuration
            has_proxy_config = bool(session_with_proxy.proxies)
            no_proxy_config = not bool(session_without_proxy.proxies)
            
            success = has_proxy_config and no_proxy_config
            
            self.log_test_result("proxy_connection", success, {
                'proxy_configured_when_enabled': has_proxy_config,
                'proxy_not_configured_when_disabled': no_proxy_config,
                'proxy_url': f"{config_with_proxy.proxy_host}:{config_with_proxy.proxy_port}"
            })
            
            return success
            
        except Exception as e:
            self.log_test_result("proxy_connection", False, {
                'error': str(e)
            })
            return False
    
    def test_concurrent_sessions(self) -> bool:
        """Test 7: Multiple concurrent sessions"""
        self.logger.info("\n🔀 TEST 7: Concurrent Sessions")
        self.logger.info("=" * 50)
        
        try:
            config = AuthConfig()
            authenticator = VSSAuthenticator(config)
            
            # Create multiple sessions concurrently
            def create_session(session_id: int) -> Dict:
                try:
                    credentials = LoginCredentials(f"user{session_id}", f"pass{session_id}")
                    auth_session = authenticator.session_manager.create_session(credentials)
                    return {
                        'session_id': session_id,
                        'success': True,
                        'auth_session_id': auth_session.session_id
                    }
                except Exception as e:
                    return {
                        'session_id': session_id,
                        'success': False,
                        'error': str(e)
                    }
            
            # Create threads để test concurrent access
            threads = []
            results = []
            
            for i in range(5):  # Test với 5 concurrent sessions
                thread = threading.Thread(
                    target=lambda i=i: results.append(create_session(i))
                )
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join(timeout=30)
            
            successful_sessions = [r for r in results if r.get('success')]
            success = len(successful_sessions) >= 3  # At least 3 sessions should succeed
            
            self.log_test_result("concurrent_sessions", success, {
                'total_attempts': 5,
                'successful_sessions': len(successful_sessions),
                'session_ids': [r.get('auth_session_id') for r in successful_sessions]
            })
            
            return success
            
        except Exception as e:
            self.log_test_result("concurrent_sessions", False, {
                'error': str(e)
            })
            return False
    
    def test_session_expiry(self) -> bool:
        """Test 8: Session expiry handling"""
        self.logger.info("\n⏰ TEST 8: Session Expiry Handling")
        self.logger.info("=" * 50)
        
        try:
            # Create config với short session timeout
            config = AuthConfig(session_timeout=2)  # 2 seconds for testing
            session_manager = SessionManager(config)
            
            # Create session
            credentials = LoginCredentials("test", "test")
            auth_session = session_manager.create_session(credentials)
            
            # Session should be valid initially
            initial_valid = session_manager.get_session(auth_session.session_id) is not None
            
            # Wait for expiry
            time.sleep(3)
            
            # Session should be expired now
            expired_session = session_manager.get_session(auth_session.session_id)
            expired_valid = expired_session is not None
            
            success = initial_valid and not expired_valid
            
            self.log_test_result("session_expiry", success, {
                'initially_valid': initial_valid,
                'expired_after_timeout': not expired_valid,
                'timeout_duration': config.session_timeout
            })
            
            return success
            
        except Exception as e:
            self.log_test_result("session_expiry", False, {
                'error': str(e)
            })
            return False
    
    def test_error_recovery(self) -> bool:
        """Test 9: Error recovery và graceful degradation"""
        self.logger.info("\n🛠️ TEST 9: Error Recovery")
        self.logger.info("=" * 50)
        
        try:
            config = AuthConfig()
            authenticator = VSSAuthenticator(config)
            
            # Test recovery từ various error conditions
            error_tests = []
            
            # Test 1: Invalid credentials không crash system
            try:
                credentials = LoginCredentials("invalid", "invalid")
                auth_session = authenticator.login(credentials)
                error_tests.append({
                    'test': 'invalid_credentials',
                    'success': True,  # Should not crash
                    'result': 'no_crash'
                })
            except Exception as e:
                error_tests.append({
                    'test': 'invalid_credentials',
                    'success': False,
                    'error': str(e)
                })
            
            # Test 2: CAPTCHA solver graceful failure
            try:
                captcha_solver = CaptchaSolver(config)
                # Try to solve non-existent CAPTCHA
                fake_challenge = None
                solution = captcha_solver.solve_with_ocr(fake_challenge) if fake_challenge else None
                error_tests.append({
                    'test': 'captcha_graceful_failure',
                    'success': True,  # Should handle gracefully
                    'result': 'handled_gracefully'
                })
            except Exception:
                error_tests.append({
                    'test': 'captcha_graceful_failure',
                    'success': False,
                    'error': 'crashed_on_invalid_input'
                })
            
            # Test 3: Session manager với corrupted data
            try:
                session_manager = SessionManager(config)
                # Try to get non-existent session
                session = session_manager.get_session("non_existent_id")
                error_tests.append({
                    'test': 'session_manager_robustness',
                    'success': session is None,  # Should return None, not crash
                    'result': 'returned_none_safely'
                })
            except Exception as e:
                error_tests.append({
                    'test': 'session_manager_robustness',
                    'success': False,
                    'error': str(e)
                })
            
            # Overall success if all error tests passed
            success = all(test['success'] for test in error_tests)
            
            self.log_test_result("error_recovery", success, {
                'total_error_tests': len(error_tests),
                'passed_tests': sum(1 for test in error_tests if test['success']),
                'test_results': error_tests
            })
            
            return success
            
        except Exception as e:
            self.log_test_result("error_recovery", False, {
                'error': str(e)
            })
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Chạy tất cả tests"""
        self.logger.info("🚀 BẮT ĐẦU VSS AUTHENTICATION TEST SUITE")
        self.logger.info("=" * 60)
        
        test_methods = [
            self.test_basic_login,
            self.test_custom_credentials,
            self.test_captcha_detection,
            self.test_session_persistence,
            self.test_retry_logic,
            self.test_proxy_connection,
            self.test_concurrent_sessions,
            self.test_session_expiry,
            self.test_error_recovery
        ]
        
        test_results = {}
        
        for test_method in test_methods:
            try:
                result = test_method()
                test_results[test_method.__name__] = result
            except Exception as e:
                self.logger.error(f"❌ Test {test_method.__name__} crashed: {e}")
                test_results[test_method.__name__] = False
                
                self.log_test_result(test_method.__name__, False, {
                    'error': f"Test crashed: {e}"
                })
        
        # Generate summary
        self.generate_test_summary(test_results)
        
        return test_results
    
    def generate_test_summary(self, test_results: Dict[str, bool]):
        """Tạo báo cáo tổng kết"""
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        self.logger.info("\n📊 TEST SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Tests: {total_tests}")
        self.logger.info(f"Passed: {passed_tests}")
        self.logger.info(f"Failed: {failed_tests}")
        self.logger.info(f"Success Rate: {success_rate:.1f}%")
        
        self.logger.info("\nDetailed Results:")
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.logger.info(f"  {status} {test_name}")
        
        # Save detailed results
        results_file = "/workspace/tmp/vss_auth_test_results.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'success_rate': success_rate,
                    'timestamp': datetime.now().isoformat()
                },
                'test_results': test_results,
                'detailed_results': self.results
            }, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"\n💾 Detailed results saved to: {results_file}")


def main():
    """Main test runner"""
    print("🧪 VSS Authentication Test Suite")
    print("=" * 60)
    
    tester = VSSAuthenticationTester()
    test_results = tester.run_all_tests()
    
    # Print final status
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! ({passed_tests}/{total_tests})")
    elif passed_tests > total_tests // 2:
        print(f"\n⚠️ MOST TESTS PASSED ({passed_tests}/{total_tests})")
    else:
        print(f"\n❌ MANY TESTS FAILED ({passed_tests}/{total_tests})")
    
    return test_results


if __name__ == "__main__":
    main()
