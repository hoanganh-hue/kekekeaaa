#!/usr/bin/env python3
"""
Ví dụ sử dụng cơ bản - Trích xuất dữ liệu VSS cho một CCCD
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vss_auto_collector import VSSAutoCollector
from src.config_manager import ConfigManager
import asyncio

async def basic_single_lookup():
    """Tra cứu một CCCD đơn lẻ"""
    
    # Khởi tạo config
    config = ConfigManager()
    
    # Khởi tạo collector
    collector = VSSAutoCollector(config)
    
    # CCCD cần tra cứu (thay bằng CCCD thực tế)
    cccd = "031173005014"
    
    try:
        print(f"🔍 Đang tra cứu CCCD: {cccd}")
        
        # Thực hiện tra cứu
        result = await collector.lookup_single_cccd(cccd)
        
        if result:
            print("✅ Tra cứu thành công!")
            print(f"📋 Kết quả:")
            print(f"   - Họ tên: {result.get('ho_ten', 'N/A')}")
            print(f"   - Mã BHXH: {result.get('ma_bhxh', 'N/A')}")
            print(f"   - Nơi cấp: {result.get('noi_cap', 'N/A')}")
            print(f"   - Trạng thái: {result.get('trang_thai', 'N/A')}")
        else:
            print("❌ Không tìm thấy thông tin BHXH")
            
    except Exception as e:
        print(f"💥 Lỗi: {str(e)}")
    
    finally:
        await collector.close()

async def basic_batch_lookup():
    """Tra cứu batch nhiều CCCD"""
    
    # Danh sách CCCD cần tra cứu
    cccd_list = [
        "031173005014",
        "031174006025", 
        "031175007036"
    ]
    
    config = ConfigManager()
    collector = VSSAutoCollector(config)
    
    try:
        print(f"🔍 Đang tra cứu {len(cccd_list)} CCCD...")
        
        results = await collector.lookup_batch_cccd(cccd_list)
        
        print(f"✅ Hoàn thành! Tìm thấy {len(results)} kết quả:")
        
        for cccd, data in results.items():
            if data:
                print(f"📋 {cccd}: {data.get('ho_ten', 'N/A')}")
            else:
                print(f"❌ {cccd}: Không tìm thấy")
                
    except Exception as e:
        print(f"💥 Lỗi: {str(e)}")
        
    finally:
        await collector.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ví dụ sử dụng cơ bản VSS")
    parser.add_argument("--mode", choices=["single", "batch"], default="single",
                       help="Chế độ tra cứu: single hoặc batch")
    
    args = parser.parse_args()
    
    if args.mode == "single":
        asyncio.run(basic_single_lookup())
    else:
        asyncio.run(basic_batch_lookup())
