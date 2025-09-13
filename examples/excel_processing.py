#!/usr/bin/env python3
"""
Ví dụ xử lý file Excel - Đọc CCCD từ Excel và ghi kết quả ra Excel
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import asyncio
from datetime import datetime
from src.vss_auto_collector import VSSAutoCollector
from src.config_manager import ConfigManager

async def process_excel_file():
    """Xử lý file Excel với danh sách CCCD"""
    
    # Đường dẫn file input và output
    input_file = "data/data-input.xlsx"
    output_file = f"data/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    try:
        # Đọc file Excel
        print(f"📖 Đọc file: {input_file}")
        df = pd.read_excel(input_file)
        
        # Kiểm tra cột CCCD
        if 'Số CCCD' not in df.columns and 'CCCD' not in df.columns:
            print("❌ Không tìm thấy cột 'Số CCCD' hoặc 'CCCD' trong file Excel")
            return
            
        cccd_column = 'Số CCCD' if 'Số CCCD' in df.columns else 'CCCD'
        cccd_list = df[cccd_column].astype(str).tolist()
        
        print(f"📋 Tìm thấy {len(cccd_list)} CCCD cần xử lý")
        
        # Khởi tạo collector
        config = ConfigManager()
        collector = VSSAutoCollector(config)
        
        results = []
        
        try:
            # Xử lý từng CCCD
            for idx, cccd in enumerate(cccd_list, 1):
                print(f"🔍 [{idx}/{len(cccd_list)}] Xử lý CCCD: {cccd}")
                
                try:
                    result = await collector.lookup_single_cccd(cccd)
                    
                    if result:
                        results.append({
                            'CCCD': cccd,
                            'Họ và tên': result.get('ho_ten', ''),
                            'Mã BHXH': result.get('ma_bhxh', ''),
                            'Ngày cấp': result.get('ngay_cap', ''),
                            'Nơi cấp': result.get('noi_cap', ''),
                            'Trạng thái': result.get('trang_thai', ''),
                            'Đơn vị làm việc': result.get('don_vi_lam_viec', ''),
                            'Mức lương': result.get('muc_luong', ''),
                            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'Trạng thái xử lý': 'Thành công'
                        })
                        print(f"   ✅ Thành công: {result.get('ho_ten', 'N/A')}")
                    else:
                        results.append({
                            'CCCD': cccd,
                            'Họ và tên': '',
                            'Mã BHXH': '',
                            'Ngày cấp': '',
                            'Nơi cấp': '',
                            'Trạng thái': '',
                            'Đơn vị làm việc': '',
                            'Mức lương': '',
                            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'Trạng thái xử lý': 'Không tìm thấy'
                        })
                        print(f"   ❌ Không tìm thấy thông tin")
                        
                except Exception as e:
                    results.append({
                        'CCCD': cccd,
                        'Họ và tên': '',
                        'Mã BHXH': '',
                        'Ngày cấp': '',
                        'Nơi cấp': '',
                        'Trạng thái': '',
                        'Đơn vị làm việc': '',
                        'Mức lương': '',
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Trạng thái xử lý': f'Lỗi: {str(e)}'
                    })
                    print(f"   💥 Lỗi: {str(e)}")
                
                # Delay giữa các request
                await asyncio.sleep(2)
                
        finally:
            await collector.close()
        
        # Ghi kết quả ra file Excel
        if results:
            results_df = pd.DataFrame(results)
            results_df.to_excel(output_file, index=False)
            print(f"💾 Đã lưu kết quả vào: {output_file}")
            
            # Tóm tắt
            successful = len([r for r in results if r['Trạng thái xử lý'] == 'Thành công'])
            not_found = len([r for r in results if r['Trạng thái xử lý'] == 'Không tìm thấy'])
            errors = len([r for r in results if r['Trạng thái xử lý'].startswith('Lỗi')])
            
            print("\n📊 TỔNG KẾT:")
            print(f"   ✅ Thành công: {successful}")
            print(f"   ❌ Không tìm thấy: {not_found}")
            print(f"   💥 Lỗi: {errors}")
            print(f"   📋 Tổng cộng: {len(results)}")
        
    except Exception as e:
        print(f"💥 Lỗi xử lý file: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Xử lý file Excel CCCD")
    parser.add_argument("--input", default="data/data-input.xlsx",
                       help="File Excel đầu vào")
    parser.add_argument("--output", 
                       help="File Excel đầu ra (tự động tạo nếu không chỉ định)")
    
    args = parser.parse_args()
    
    asyncio.run(process_excel_file())
