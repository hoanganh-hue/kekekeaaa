#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Authentication Real-World Example
====================================

Ví dụ thực tế về cách tích hợp authentication system vào ứng dụng VSS.
"""

import sys
import time
import logging
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, '/workspace/src')

from vss_authentication import (
    VSSAuthenticator, 
    AuthConfig, 
    LoginCredentials
)

def setup_production_logging():
    """Setup logging cho production environment"""
    log_dir = "/workspace/logs"
    import os
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{log_dir}/vss_app.log"),
            logging.StreamHandler()
        ]
    )

class VSSDataCollector:
    """Ví dụ ứng dụng sử dụng VSS Authentication"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Production configuration
        self.config = AuthConfig(
            base_url="http://vssapp.teca.vn:8088",
            use_proxy=True,
            max_retries=3,
            retry_delay=2.0,
            timeout=30,
            session_timeout=1800  # 30 minutes
        )
        
        self.authenticator = VSSAuthenticator(self.config)
        self.current_session = None
        
    def authenticate(self, credentials=None):
        """Authenticate với VSS Portal"""
        self.logger.info("🔐 Bắt đầu authentication...")
        
        try:
            # Thử reuse existing session trước
            if self.current_session and self.authenticator.verify_session(self.current_session):
                self.logger.info("✅ Reusing existing session")
                return True
            
            # Authentication mới
            self.current_session = self.authenticator.login(credentials)
            
            if self.current_session:
                self.logger.info(f"✅ Authentication thành công! Session: {self.current_session.session_id}")
                return True
            else:
                self.logger.error("❌ Authentication thất bại")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Lỗi authentication: {e}")
            return False
    
    def make_authenticated_request(self, endpoint, method='GET', data=None):
        """Make authenticated request tới VSS API"""
        if not self.current_session:
            self.logger.error("❌ Chưa authenticate, không thể make request")
            return None
        
        try:
            # Verify session vẫn còn valid
            if not self.authenticator.verify_session(self.current_session):
                self.logger.warning("⚠️ Session expired, re-authenticating...")
                if not self.authenticate():
                    return None
            
            # Get authenticated session
            http_session = self.authenticator.get_authenticated_session(self.current_session)
            if not http_session:
                self.logger.error("❌ Không thể tạo HTTP session")
                return None
            
            # Make request
            url = f"{self.config.base_url}{endpoint}"
            self.logger.info(f"📡 Making {method} request to: {endpoint}")
            
            if method.upper() == 'GET':
                response = http_session.get(url, timeout=self.config.timeout)
            elif method.upper() == 'POST':
                response = http_session.post(url, data=data, timeout=self.config.timeout)
            else:
                response = http_session.request(method, url, data=data, timeout=self.config.timeout)
            
            self.logger.info(f"✅ Response: {response.status_code} ({len(response.content)} bytes)")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi making request: {e}")
            return None
    
    def collect_province_data(self, province_code):
        """Collect data cho một tỉnh cụ thể"""
        self.logger.info(f"📊 Thu thập dữ liệu tỉnh: {province_code}")
        
        # Mock endpoint - thay bằng real VSS API
        endpoint = f"/api/province/{province_code}"
        
        response = self.make_authenticated_request(endpoint)
        if response and response.status_code == 200:
            self.logger.info(f"✅ Thu thập thành công dữ liệu tỉnh {province_code}")
            return response.json() if response.content else {}
        else:
            self.logger.warning(f"⚠️ Không thể thu thập dữ liệu tỉnh {province_code}")
            return None
    
    def batch_collect_data(self, province_codes):
        """Thu thập dữ liệu cho nhiều tỉnh"""
        self.logger.info(f"🔄 Bắt đầu batch collection cho {len(province_codes)} tỉnh")
        
        results = {}
        successful = 0
        failed = 0
        
        for i, province_code in enumerate(province_codes):
            self.logger.info(f"📍 Processing {i+1}/{len(province_codes)}: {province_code}")
            
            data = self.collect_province_data(province_code)
            if data:
                results[province_code] = data
                successful += 1
            else:
                failed += 1
            
            # Rate limiting để tránh bị block
            if i < len(province_codes) - 1:  # Don't delay after last item
                time.sleep(1)  # 1 second delay between requests
        
        self.logger.info(f"📈 Batch collection hoàn thành: {successful} thành công, {failed} thất bại")
        return results
    
    def save_results(self, results, filename):
        """Lưu kết quả ra file"""
        try:
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Kết quả đã lưu: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi lưu file: {e}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        if self.current_session:
            self.logger.info("🧹 Cleaning up session...")
            self.authenticator.logout(self.current_session)
            self.current_session = None

def main():
    """Main application example"""
    print("🏢 VSS Data Collector - Real World Example")
    print("=" * 60)
    
    setup_production_logging()
    
    # Create collector
    collector = VSSDataCollector()
    
    try:
        # Step 1: Authentication
        print("\n🔐 Step 1: Authentication")
        if not collector.authenticate():
            print("❌ Authentication failed, aborting...")
            return
        
        # Step 2: Test single request
        print("\n📡 Step 2: Test Single Request")
        response = collector.make_authenticated_request("/dashboard")
        if response:
            print(f"✅ Dashboard request successful: {response.status_code}")
        
        # Step 3: Collect data for sample provinces
        print("\n📊 Step 3: Sample Data Collection")
        sample_provinces = ['001', '031', '048', '079']  # Hà Nội, Hải Phòng, Đà Nẵng, TP.HCM
        
        results = collector.batch_collect_data(sample_provinces)
        
        # Step 4: Save results
        print("\n💾 Step 4: Save Results")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/workspace/data/vss_sample_collection_{timestamp}.json"
        
        if collector.save_results(results, filename):
            print(f"✅ Results saved to: {filename}")
        
        # Step 5: Generate summary
        print("\n📈 Step 5: Summary")
        print(f"   Total provinces processed: {len(sample_provinces)}")
        print(f"   Successful collections: {len(results)}")
        print(f"   Failed collections: {len(sample_provinces) - len(results)}")
        
        if results:
            print(f"   Sample data keys: {list(list(results.values())[0].keys()) if results else 'N/A'}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always cleanup
        print("\n🧹 Cleanup")
        collector.cleanup()
        print("✅ Application completed")

def demo_authentication_scenarios():
    """Demo các scenarios authentication khác nhau"""
    print("\n🎭 Authentication Scenarios Demo")
    print("=" * 50)
    
    authenticator = VSSAuthenticator()
    
    scenarios = [
        {
            'name': 'Default Credentials',
            'action': lambda: authenticator.try_default_credentials()
        },
        {
            'name': 'Custom Credentials',
            'action': lambda: authenticator.login(LoginCredentials("test_user", "test_pass"))
        },
        {
            'name': 'Invalid Credentials (Expected Failure)',
            'action': lambda: authenticator.login(LoginCredentials("invalid", "invalid"))
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎬 Scenario: {scenario['name']}")
        try:
            start_time = time.time()
            result = scenario['action']()
            end_time = time.time()
            
            if result:
                print(f"✅ Success - Session: {result.session_id}")
                print(f"   Duration: {end_time - start_time:.2f}s")
                authenticator.logout(result)
            else:
                print(f"❌ Failed (as expected for invalid credentials)")
                print(f"   Duration: {end_time - start_time:.2f}s")
                
        except Exception as e:
            print(f"⚠️ Exception: {e}")

if __name__ == "__main__":
    print("🚀 VSS Authentication Real-World Examples")
    print("=" * 60)
    
    # Run main example
    main()
    
    # Run authentication scenarios demo
    demo_authentication_scenarios()
    
    print("\n🎯 Example completed!")
    print("Check /workspace/logs/vss_app.log for detailed logs")
