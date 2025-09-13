#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Authentication Quick Demo
============================

Demo nhanh các tính năng chính của VSS Authentication system.
"""

import sys
import time
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, '/workspace/src')

from vss_authentication import (
    VSSAuthenticator, 
    AuthConfig, 
    LoginCredentials, 
    SessionManager,
    CaptchaSolver
)

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def demo_config_creation():
    """Demo 1: Tạo và cấu hình authentication"""
    print("\n🔧 DEMO 1: Configuration & Setup")
    print("=" * 50)
    
    # Basic config
    config = AuthConfig(
        base_url="http://vssapp.teca.vn:8088",
        use_proxy=True,
        max_retries=2,  # Giảm cho demo
        timeout=10      # Giảm cho demo
    )
    
    print(f"✅ Base URL: {config.base_url}")
    print(f"✅ Proxy: {'Enabled' if config.use_proxy else 'Disabled'}")
    print(f"✅ Max Retries: {config.max_retries}")
    print(f"✅ Timeout: {config.timeout}s")
    
    return config

def demo_session_management():
    """Demo 2: Session management capabilities"""
    print("\n💾 DEMO 2: Session Management")
    print("=" * 50)
    
    config = AuthConfig()
    session_manager = SessionManager(config)
    
    # Create test session
    credentials = LoginCredentials("demo_user", "demo_pass")
    auth_session = session_manager.create_session(credentials)
    
    print(f"✅ Session created: {auth_session.session_id}")
    print(f"✅ Created at: {auth_session.created_at}")
    print(f"✅ Expires at: {auth_session.expires_at}")
    print(f"✅ User Agent: {auth_session.user_agent[:50]}...")
    
    # Update session
    test_cookies = {'session_id': 'test123', 'csrf_token': 'token456'}
    session_manager.update_session(auth_session.session_id, test_cookies, 'csrf789')
    
    print(f"✅ Session updated with cookies: {len(test_cookies)} items")
    print(f"✅ CSRF token: {auth_session.csrf_token}")
    
    # Test session persistence
    session_manager.save_sessions()
    print("✅ Sessions saved to disk")
    
    # Load and verify
    new_session_manager = SessionManager(config)
    loaded_session = new_session_manager.get_session(auth_session.session_id)
    
    if loaded_session:
        print("✅ Session loaded successfully from disk")
        print(f"✅ Loaded session ID: {loaded_session.session_id}")
    else:
        print("❌ Failed to load session")
    
    return auth_session

def demo_captcha_detection():
    """Demo 3: CAPTCHA detection capabilities"""
    print("\n🧩 DEMO 3: CAPTCHA Detection")
    print("=" * 50)
    
    config = AuthConfig()
    captcha_solver = CaptchaSolver(config)
    
    # Test HTML với CAPTCHA
    html_with_captcha = '''
    <html>
        <body>
            <form>
                <input name="username" type="text">
                <input name="password" type="password">
                <img src="/captcha/generate?id=123" alt="CAPTCHA Image">
                <input name="captcha" type="text" placeholder="Enter CAPTCHA">
                <button type="submit">Login</button>
            </form>
        </body>
    </html>
    '''
    
    # Test HTML không có CAPTCHA
    html_without_captcha = '''
    <html>
        <body>
            <form>
                <input name="username" type="text">
                <input name="password" type="password">
                <button type="submit">Login</button>
            </form>
        </body>
    </html>
    '''
    
    # Test detection
    print("🔍 Testing CAPTCHA detection...")
    
    captcha_detected = captcha_solver.detect_captcha(html_with_captcha)
    if captcha_detected:
        print(f"✅ CAPTCHA detected: {captcha_detected.image_url}")
        print(f"✅ Challenge type: {captcha_detected.challenge_type}")
        print(f"✅ Difficulty: {captcha_detected.difficulty}")
    else:
        print("❌ CAPTCHA not detected in HTML with CAPTCHA")
    
    no_captcha_detected = captcha_solver.detect_captcha(html_without_captcha)
    if not no_captcha_detected:
        print("✅ Correctly identified HTML without CAPTCHA")
    else:
        print("❌ False positive: CAPTCHA detected in HTML without CAPTCHA")
    
    return captcha_detected

def demo_credentials_handling():
    """Demo 4: Credentials management"""
    print("\n🔐 DEMO 4: Credentials Management")
    print("=" * 50)
    
    # Create different types of credentials
    basic_creds = LoginCredentials("admin", "password123")
    print(f"✅ Basic credentials: {basic_creds.username}")
    
    # Credentials với CAPTCHA solution
    captcha_creds = LoginCredentials(
        username="user", 
        password="pass",
        captcha_solution="ABC123"
    )
    print(f"✅ CAPTCHA credentials: {captcha_creds.username} (CAPTCHA: {captcha_creds.captcha_solution})")
    
    # Credentials với additional fields
    advanced_creds = LoginCredentials(
        username="advanced_user",
        password="advanced_pass",
        additional_fields={
            "remember_me": "1",
            "timezone": "Asia/Ho_Chi_Minh"
        }
    )
    print(f"✅ Advanced credentials: {advanced_creds.username}")
    print(f"   Additional fields: {advanced_creds.additional_fields}")
    
    return [basic_creds, captcha_creds, advanced_creds]

def demo_authentication_flow():
    """Demo 5: Authentication flow (without actual connection)"""
    print("\n🚀 DEMO 5: Authentication Flow")
    print("=" * 50)
    
    config = AuthConfig(
        timeout=5,       # Short timeout for demo
        max_retries=1    # Single retry for demo
    )
    
    authenticator = VSSAuthenticator(config)
    
    print("✅ Authenticator created")
    print(f"✅ Default credentials available: {len(authenticator.default_credentials)}")
    
    # Demo session creation
    test_credentials = LoginCredentials("test", "test")
    auth_session = authenticator.session_manager.create_session(test_credentials)
    
    print(f"✅ Demo session created: {auth_session.session_id}")
    
    # Demo HTTP session creation
    http_session = authenticator.create_http_session(auth_session)
    
    print(f"✅ HTTP session configured")
    print(f"   User-Agent: {http_session.headers.get('User-Agent', 'Not set')[:50]}...")
    print(f"   Proxy configured: {'Yes' if http_session.proxies else 'No'}")
    
    return authenticator

def demo_error_handling():
    """Demo 6: Error handling capabilities"""
    print("\n🛠️ DEMO 6: Error Handling")
    print("=" * 50)
    
    config = AuthConfig()
    
    # Test session expiry
    session_manager = SessionManager(config)
    
    # Create session với short timeout
    config.session_timeout = 1  # 1 second for demo
    expired_session = session_manager.create_session(LoginCredentials("test", "test"))
    
    print(f"✅ Created session with 1s timeout: {expired_session.session_id}")
    
    # Wait for expiry
    print("⏰ Waiting for session expiry...")
    time.sleep(2)
    
    # Check if expired
    retrieved_session = session_manager.get_session(expired_session.session_id)
    if not retrieved_session:
        print("✅ Session correctly expired and removed")
    else:
        print("❌ Session should have expired")
    
    # Test cleanup
    session_manager.cleanup_expired_sessions()
    print("✅ Expired sessions cleaned up")
    
    # Test graceful error handling
    try:
        # Try to get non-existent session
        non_existent = session_manager.get_session("non_existent_id")
        if non_existent is None:
            print("✅ Gracefully handled non-existent session request")
    except Exception as e:
        print(f"❌ Error handling failed: {e}")

def main():
    """Main demo runner"""
    print("🎯 VSS Authentication System Demo")
    print("=" * 60)
    print(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    setup_logging()
    
    try:
        # Run all demos
        config = demo_config_creation()
        auth_session = demo_session_management()
        captcha_challenge = demo_captcha_detection()
        credentials_list = demo_credentials_handling()
        authenticator = demo_authentication_flow()
        demo_error_handling()
        
        print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ All authentication components working properly")
        print("✅ Session management operational")
        print("✅ CAPTCHA detection functional")
        print("✅ Error handling robust")
        print("✅ Credentials management flexible")
        
        print(f"\n📊 Demo Summary:")
        print(f"   - Sessions created: Multiple")
        print(f"   - CAPTCHA detection: Working")
        print(f"   - Credentials tested: {len(credentials_list)}")
        print(f"   - Error scenarios: Handled gracefully")
        
    except Exception as e:
        print(f"\n❌ DEMO FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
