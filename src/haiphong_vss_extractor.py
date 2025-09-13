#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hệ thống trích xuất dữ liệu VSS cho Hải Phòng
Dựa trên kinh nghiệm thành công từ thu thập dữ liệu Hải Châu
"""

import pandas as pd
import requests
import time
import json
import random
from datetime import datetime
import concurrent.futures
import os

class HaiPhongVSSExtractor:
    def __init__(self):
        self.proxy_config = {
            'http': 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301',
            'https': 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301'
        }
        
        self.session = requests.Session()
        self.session.proxies.update(self.proxy_config)
        
        self.vss_url = "https://dichvucong.vss.gov.vn/pub-page/ws/getCongDanInfo"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://dichvucong.vss.gov.vn/pub-page/tra-cuu-thong-tin-tham-gia-bhxh'
        }
        
        # Thống kê
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'no_data': 0,
            'active_bhxh': 0,
            'start_time': None
        }
        
        # Lưu trữ kết quả
        self.results = []
        
    def extract_single_cccd(self, cccd):
        """Trích xuất thông tin từ 1 CCCD"""
        try:
            payload = {
                "cccd": cccd,
                "pageSize": 10,
                "pageNumber": 1
            }
            
            response = self.session.post(
                self.vss_url, 
                json=payload, 
                headers=self.headers, 
                timeout=30
            )
            
            self.stats['total_processed'] += 1
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success' and data.get('data'):
                    bhxh_records = data.get('data', [])
                    
                    # Lọc chỉ lấy tình trạng "Đang đóng"
                    active_records = [
                        record for record in bhxh_records 
                        if record.get('trangThai') == 'Đang đóng'
                    ]
                    
                    if active_records:
                        # Lấy thông tin từ record đầu tiên
                        record = active_records[0]
                        
                        result = {
                            'cccd': cccd,
                            'ho_ten': record.get('hoVaTen', ''),
                            'gioi_tinh': record.get('gioiTinh', ''),
                            'ngay_sinh': record.get('ngaySinh', ''),
                            'sdt': record.get('soDienThoai', ''),
                            'dia_chi': record.get('diaChi', ''),
                            'so_bhxh': record.get('soBHXH', ''),
                            'tinh_trang_bhxh': record.get('trangThai', ''),
                            'don_vi': record.get('donVi', ''),
                            'ghi_chu': f"Hải Phòng - {len(active_records)} record(s)"
                        }
                        
                        self.stats['successful'] += 1
                        self.stats['active_bhxh'] += 1
                        
                        return result
                    else:
                        self.stats['no_data'] += 1
                        return None
                        
                else:
                    self.stats['no_data'] += 1
                    return None
                    
            else:
                self.stats['failed'] += 1
                return None
                
        except Exception as e:
            self.stats['failed'] += 1
            print(f"❌ Lỗi xử lý {cccd}: {str(e)[:50]}...")
            return None
    
    def extract_batch(self, cccd_list, batch_name="batch"):
        """Trích xuất một batch CCCD"""
        
        print(f"\n🔄 Bắt đầu xử lý {batch_name}: {len(cccd_list)} CCCD")
        self.stats['start_time'] = time.time()
        
        batch_results = []
        
        # Xử lý tuần tự với delay để tránh rate limiting
        for i, cccd in enumerate(cccd_list, 1):
            print(f"   📍 {i}/{len(cccd_list)}: {cccd}", end=" ")
            
            result = self.extract_single_cccd(cccd)
            
            if result:
                batch_results.append(result)
                self.results.append(result)
                print("✅")
            else:
                print("❌")
            
            # Delay giữa các request
            if i < len(cccd_list):  # Không delay ở request cuối
                time.sleep(random.uniform(1.0, 2.0))
        
        elapsed = time.time() - self.stats['start_time']
        
        print(f"\n📊 Kết quả {batch_name}:")
        print(f"   ✅ Thành công: {len(batch_results)}/{len(cccd_list)}")
        print(f"   ⏱️  Thời gian: {elapsed:.1f}s")
        print(f"   📈 Tốc độ: {len(cccd_list)/elapsed*60:.1f} CCCD/phút")
        
        return batch_results
    
    def save_batch_results(self, results, batch_name):
        """Lưu kết quả batch"""
        if not results:
            print(f"⚠️  {batch_name}: Không có dữ liệu để lưu")
            return None
            
        # Chuyển đổi sang DataFrame
        df = pd.DataFrame(results)
        
        # Sắp xếp lại cột
        column_order = [
            'cccd', 'ho_ten', 'gioi_tinh', 'ngay_sinh', 
            'sdt', 'dia_chi', 'so_bhxh', 'tinh_trang_bhxh',
            'don_vi', 'ghi_chu'
        ]
        
        df = df.reindex(columns=column_order)
        
        # Lưu file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"haiphong_{batch_name}_results_{timestamp}.xlsx"
        df.to_excel(filename, index=False)
        
        print(f"💾 Đã lưu {batch_name}: {filename}")
        return filename
    
    def generate_batch_report(self, batch_name):
        """Tạo báo cáo cho batch"""
        if not self.stats['start_time']:
            return None
            
        elapsed = time.time() - self.stats['start_time']
        
        report = {
            'batch_info': {
                'name': batch_name,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'processing_time': f"{elapsed:.1f} seconds"
            },
            'statistics': {
                'total_processed': self.stats['total_processed'],
                'successful_extractions': self.stats['successful'],
                'failed_requests': self.stats['failed'],
                'no_data_found': self.stats['no_data'],
                'active_bhxh_records': self.stats['active_bhxh'],
                'success_rate': f"{(self.stats['successful'] / max(self.stats['total_processed'], 1) * 100):.1f}%"
            },
            'performance': {
                'requests_per_minute': f"{(self.stats['total_processed'] / max(elapsed/60, 0.1)):.1f}",
                'avg_response_time': f"{(elapsed / max(self.stats['total_processed'], 1)):.2f}s"
            }
        }
        
        return report

def main():
    print("🚀 HỆ THỐNG TRÍCH XUẤT VSS - HẢI PHÒNG")
    print("=" * 50)
    
    # Khởi tạo extractor
    extractor = HaiPhongVSSExtractor()
    
    # Test connection trước
    print("🔗 Kiểm tra kết nối VSS...")
    test_cccd = "031173005014"  # CCCD Hải Phòng mẫu
    test_result = extractor.extract_single_cccd(test_cccd)
    
    if test_result:
        print("✅ Kết nối VSS thành công!")
        print(f"📋 Test result: {test_result['ho_ten']} - {test_result['tinh_trang_bhxh']}")
    else:
        print("⚠️  Không thể kết nối VSS hoặc không có dữ liệu test")
    
    print(f"\n📊 Thống kê ban đầu:")
    print(f"   Processed: {extractor.stats['total_processed']}")
    print(f"   Success: {extractor.stats['successful']}")
    print(f"   Failed: {extractor.stats['failed']}")
    
    return extractor

if __name__ == "__main__":
    extractor = main()
