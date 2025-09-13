#!/usr/bin/env python3
"""
VSS System Deep Analysis Script
Thu thập chi tiết về hệ thống VSS để tìm real data endpoints
"""

import requests
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime

class VSSSystemAnalyzer:
    def __init__(self):
        # Proxy configuration từ thông tin đã có
        self.proxy_config = {
            'host': 'ip.mproxy.vn',
            'port': 12301,
            'username': 'beba111',
            'password': 'tDV5tkMchYUBMD'
        }
        
        # Setup proxy
        proxy_url = f"http://{self.proxy_config['username']}:{self.proxy_config['password']}@{self.proxy_config['host']}:{self.proxy_config['port']}"
        self.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        # Setup session with proper headers
        self.session = requests.Session()
        self.session.proxies.update(self.proxies)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.base_url = "http://vssapp.teca.vn:8088"
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'connectivity': {},
            'javascript_analysis': {},
            'form_analysis': {},
            'api_discovery': {},
            'session_management': {}
        }
    
    def test_connectivity(self):
        """Test basic connectivity với VSS server"""
        print("🔍 Testing connectivity to VSS server...")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            print(f"✅ Connection successful! Status: {response.status_code}")
            
            self.analysis_results['connectivity'] = {
                'status': 'success',
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'cookies': dict(response.cookies),
                'content_length': len(response.content),
                'response_time': response.elapsed.total_seconds()
            }
            
            return response
            
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            self.analysis_results['connectivity'] = {
                'status': 'failed',
                'error': str(e)
            }
            return None
    
    def analyze_html_structure(self, response):
        """Phân tích cấu trúc HTML và tìm các clues về system architecture"""
        print("🔍 Analyzing HTML structure...")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract JavaScript files
        js_files = []
        for script in soup.find_all('script', src=True):
            js_url = urljoin(self.base_url, script['src'])
            js_files.append(js_url)
        
        # Extract CSS files  
        css_files = []
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                css_url = urljoin(self.base_url, link['href'])
                css_files.append(css_url)
        
        # Extract forms
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action'),
                'method': form.get('method', 'GET'),
                'inputs': []
            }
            
            for input_field in form.find_all(['input', 'textarea', 'select']):
                input_info = {
                    'name': input_field.get('name'),
                    'type': input_field.get('type', 'text'),
                    'value': input_field.get('value'),
                    'required': input_field.has_attr('required'),
                    'id': input_field.get('id')
                }
                form_data['inputs'].append(input_info)
            
            forms.append(form_data)
        
        # Extract all links
        links = []
        for link in soup.find_all('a', href=True):
            link_url = urljoin(self.base_url, link['href'])
            links.append({
                'url': link_url,
                'text': link.get_text(strip=True)
            })
        
        self.analysis_results['form_analysis'] = {
            'forms': forms,
            'javascript_files': js_files,
            'css_files': css_files,
            'links': links,
            'title': soup.title.get_text() if soup.title else None
        }
        
        return js_files, css_files, forms
    
    def analyze_javascript_files(self, js_files):
        """Download và phân tích các JavaScript files để tìm API endpoints"""
        print("🔍 Analyzing JavaScript files for API endpoints...")
        
        api_patterns = [
            r'["\']/(api|data|info|admin|dashboard|report|statistics)/[^"\']*["\']',
            r'["\']https?://[^"\']*/(api|data|info)[^"\']*["\']',
            r'\.get\(["\']([^"\']+)["\']',
            r'\.post\(["\']([^"\']+)["\']',
            r'fetch\(["\']([^"\']+)["\']',
            r'ajax.*url[:\s]*["\']([^"\']+)["\']',
            r'endpoint[:\s]*["\']([^"\']+)["\']'
        ]
        
        discovered_endpoints = set()
        js_analysis = {}
        
        for js_url in js_files:
            try:
                print(f"  📄 Analyzing: {js_url}")
                response = self.session.get(js_url, timeout=15)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Tìm các potential API endpoints
                    for pattern in api_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                endpoint = match[0] if match[0] else match[1]
                            else:
                                endpoint = match
                            
                            if endpoint.startswith('/') or endpoint.startswith('http'):
                                discovered_endpoints.add(endpoint)
                    
                    js_analysis[js_url] = {
                        'status': 'success',
                        'size': len(content),
                        'endpoints_found': len([ep for ep in discovered_endpoints if js_url in content])
                    }
                else:
                    js_analysis[js_url] = {
                        'status': 'failed',
                        'status_code': response.status_code
                    }
                    
            except Exception as e:
                js_analysis[js_url] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        self.analysis_results['api_discovery'] = {
            'discovered_endpoints': list(discovered_endpoints),
            'js_file_analysis': js_analysis
        }
        
        return list(discovered_endpoints)
    
    def test_discovered_endpoints(self, endpoints):
        """Test các endpoints đã phát hiện"""
        print("🔍 Testing discovered endpoints...")
        
        endpoint_results = {}
        
        for endpoint in endpoints:
            if endpoint.startswith('/'):
                full_url = urljoin(self.base_url, endpoint)
            else:
                full_url = endpoint
                
            try:
                print(f"  🌐 Testing: {full_url}")
                response = self.session.get(full_url, timeout=10)
                
                endpoint_results[full_url] = {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'content_type': response.headers.get('content-type', ''),
                    'content_length': len(response.content),
                    'accessible': response.status_code < 400
                }
                
                # Nếu endpoint trả về JSON, parse nó
                if 'application/json' in response.headers.get('content-type', ''):
                    try:
                        endpoint_results[full_url]['json_data'] = response.json()
                    except:
                        pass
                        
            except Exception as e:
                endpoint_results[full_url] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        self.analysis_results['api_discovery']['endpoint_tests'] = endpoint_results
        return endpoint_results
    
    def analyze_authentication_mechanism(self, forms):
        """Phân tích cơ chế authentication"""
        print("🔍 Analyzing authentication mechanism...")
        
        login_form = None
        for form in forms:
            if form['action'] and 'login' in form['action'].lower():
                login_form = form
                break
        
        if login_form:
            # Extract CSRF token patterns
            csrf_tokens = []
            for input_field in login_form['inputs']:
                if (input_field['name'] and 
                    any(keyword in input_field['name'].lower() for keyword in ['token', 'csrf', '_token'])):
                    csrf_tokens.append(input_field)
            
            self.analysis_results['session_management'] = {
                'login_form_found': True,
                'login_action': login_form['action'],
                'login_method': login_form['method'],
                'csrf_tokens': csrf_tokens,
                'required_fields': [field for field in login_form['inputs'] if field['required']],
                'authentication_flow': 'form_based'
            }
        else:
            self.analysis_results['session_management'] = {
                'login_form_found': False
            }
    
    def save_analysis_results(self):
        """Lưu kết quả phân tích"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/vss_deep_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Analysis results saved to: {filename}")
        return filename
    
    def run_full_analysis(self):
        """Chạy full analysis pipeline"""
        print("🚀 Starting VSS System Deep Analysis...")
        print("=" * 60)
        
        # Step 1: Test connectivity
        response = self.test_connectivity()
        if not response:
            print("❌ Cannot proceed - connection failed")
            return self.save_analysis_results()
        
        # Step 2: Analyze HTML structure
        js_files, css_files, forms = self.analyze_html_structure(response)
        
        # Step 3: Analyze JavaScript for API endpoints
        discovered_endpoints = self.analyze_javascript_files(js_files)
        
        # Step 4: Test discovered endpoints
        if discovered_endpoints:
            self.test_discovered_endpoints(discovered_endpoints)
        
        # Step 5: Analyze authentication mechanism
        self.analyze_authentication_mechanism(forms)
        
        # Step 6: Save results
        results_file = self.save_analysis_results()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"✅ Connection Status: {self.analysis_results['connectivity']['status']}")
        print(f"📄 JavaScript Files Found: {len(js_files)}")
        print(f"🔗 Endpoints Discovered: {len(discovered_endpoints) if discovered_endpoints else 0}")
        print(f"📝 Forms Found: {len(forms)}")
        print(f"🔐 Login Form: {'Found' if self.analysis_results['session_management'].get('login_form_found') else 'Not Found'}")
        
        if discovered_endpoints:
            print(f"\n🌐 Discovered Endpoints:")
            for ep in discovered_endpoints[:10]:  # Show first 10
                print(f"   • {ep}")
        
        return results_file

if __name__ == "__main__":
    analyzer = VSSSystemAnalyzer()
    results_file = analyzer.run_full_analysis()
    print(f"\n🎯 Deep analysis completed! Results: {results_file}")
