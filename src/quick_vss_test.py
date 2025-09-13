#!/usr/bin/env python3
"""
Quick VSS Endpoint Tester - Focused testing for key patterns

Author: MiniMax Agent  
Date: 2025-09-12
"""

import requests
import json
import time
from datetime import datetime
import os

class QuickVSSTest:
    def __init__(self):
        self.base_url = "http://vssapp.teca.vn:8088/"
        self.proxy_config = {
            'http': 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301',
            'https': 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301'
        }
        
        self.session = requests.Session()
        self.session.proxies.update(self.proxy_config)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.results = []
        
    def test_endpoint(self, method, path, description=""):
        """Quick endpoint test"""
        url = f"{self.base_url}{path}"
        try:
            start_time = time.time()
            response = self.session.request(method, url, timeout=10)
            response_time = time.time() - start_time
            
            result = {
                'method': method,
                'url': url,
                'path': path,
                'description': description,
                'status_code': response.status_code,
                'response_time': response_time,
                'content_length': len(response.content) if response.content else 0,
                'content_type': response.headers.get('Content-Type', ''),
                'server': response.headers.get('Server', ''),
                'accessible': response.status_code == 200,
                'protected': response.status_code in [401, 403],
                'error': response.status_code >= 400,
                'interesting': response.status_code not in [200, 404],
                'preview': response.text[:100] if response.text else ""
            }
            
            self.results.append(result)
            print(f"{method:6} {path:40} -> {response.status_code:3} ({response_time:.2f}s) - {description}")
            return result
            
        except Exception as e:
            result = {
                'method': method, 'url': url, 'path': path, 'description': description,
                'status_code': 0, 'response_time': 0, 'content_length': 0,
                'content_type': '', 'server': '', 'accessible': False,
                'protected': False, 'error': True, 'interesting': True,
                'preview': f"ERROR: {e}"
            }
            self.results.append(result)
            print(f"{method:6} {path:40} -> ERR ({str(e)[:30]}) - {description}")
            return result

    def run_focused_tests(self):
        """Run focused endpoint tests"""
        print("="*80)
        print("VSS ENDPOINT QUICK TESTING")
        print("="*80)
        
        # 1. Basic pages
        print("\n1. BASIC PAGES:")
        self.test_endpoint('GET', '', 'Main page')
        self.test_endpoint('GET', 'login', 'Login page')
        self.test_endpoint('GET', 'logout', 'Logout')
        
        # 2. Geographic API patterns (RESTful)
        print("\n2. GEOGRAPHIC API ENDPOINTS:")
        self.test_endpoint('GET', 'api/provinces', 'All provinces')
        self.test_endpoint('GET', 'api/provinces/001', 'Hà Nội province')
        self.test_endpoint('GET', 'api/provinces/031', 'Hải Phòng province')  
        self.test_endpoint('GET', 'api/provinces/079', 'TP.HCM province')
        self.test_endpoint('GET', 'api/districts', 'All districts')
        self.test_endpoint('GET', 'api/districts/001', 'Hà Nội districts')
        self.test_endpoint('GET', 'api/wards', 'All wards')
        self.test_endpoint('GET', 'api/hospitals', 'All hospitals')
        
        # 3. Authentication endpoints
        print("\n3. AUTHENTICATION ENDPOINTS:")
        self.test_endpoint('GET', 'api/user', 'Current user')
        self.test_endpoint('GET', 'api/me', 'Me endpoint')
        self.test_endpoint('GET', 'sanctum/csrf-cookie', 'CSRF cookie')
        self.test_endpoint('POST', 'api/login', 'API login')
        
        # 4. Administrative endpoints  
        print("\n4. ADMINISTRATIVE ENDPOINTS:")
        self.test_endpoint('GET', 'api/hospitals/001', 'Hospitals in Hà Nội')
        self.test_endpoint('GET', 'api/claims/001', 'Claims in Hà Nội')
        self.test_endpoint('GET', 'api/users', 'User management')
        self.test_endpoint('GET', 'api/roles', 'Role management')
        
        # 5. Non-RESTful patterns
        print("\n5. NON-RESTFUL ENDPOINTS:")
        self.test_endpoint('GET', 'admin/provinces', 'Admin provinces')
        self.test_endpoint('GET', 'dashboard', 'Dashboard') 
        self.test_endpoint('GET', 'dashboard/data', 'Dashboard data')
        self.test_endpoint('GET', 'reports/province/001', 'Hà Nội reports')
        
        # 6. Known files from previous discovery
        print("\n6. KNOWN FILES (Previous Discovery):")
        self.test_endpoint('GET', 'test.php', 'Test file')
        self.test_endpoint('GET', 'test1.php', 'Database schema file')
        
        # 7. Potential security files
        print("\n7. POTENTIAL SECURITY FILES:")  
        self.test_endpoint('GET', 'phpinfo.php', 'PHP info')
        self.test_endpoint('GET', '.env', 'Environment file')
        self.test_endpoint('GET', 'composer.json', 'Composer config')
        
    def analyze_results(self):
        """Analyze test results"""
        analysis = {
            'total_tests': len(self.results),
            'accessible': [r for r in self.results if r['accessible']],
            'protected': [r for r in self.results if r['protected']], 
            'not_found': [r for r in self.results if r['status_code'] == 404],
            'server_errors': [r for r in self.results if r['status_code'] == 500],
            'interesting': [r for r in self.results if r['interesting']],
            'status_distribution': {}
        }
        
        # Status code distribution
        for result in self.results:
            code = result['status_code']
            analysis['status_distribution'][code] = analysis['status_distribution'].get(code, 0) + 1
        
        return analysis
    
    def save_results(self):
        """Save results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        os.makedirs('data', exist_ok=True)
        
        # Save detailed results
        with open(f'data/quick_test_results_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Save analysis
        analysis = self.analyze_results()
        with open(f'data/quick_analysis_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        
        return analysis

if __name__ == "__main__":
    tester = QuickVSSTest()
    tester.run_focused_tests()
    
    print("\n" + "="*80)
    print("ANALYZING RESULTS...")
    analysis = tester.save_results()
    
    print("\nSUMMARY:")
    print(f"Total Tests: {analysis['total_tests']}")
    print(f"Accessible (200): {len(analysis['accessible'])}")
    print(f"Protected (401/403): {len(analysis['protected'])}")
    print(f"Not Found (404): {len(analysis['not_found'])}")
    print(f"Server Errors (500): {len(analysis['server_errors'])}")
    print(f"Status Distribution: {analysis['status_distribution']}")
    
    print("\nACCESSIBLE ENDPOINTS:")
    for endpoint in analysis['accessible']:
        print(f"  {endpoint['method']:6} {endpoint['path']:30} ({endpoint['content_length']} bytes)")
    
    print("\nINTERESTING RESPONSES:")
    for endpoint in analysis['interesting'][:10]:  # Top 10
        print(f"  {endpoint['method']:6} {endpoint['path']:30} -> {endpoint['status_code']} ({endpoint['description']})")
    
    print("="*80)
