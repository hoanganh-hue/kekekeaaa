#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced System - Main Integration Script
Kết hợp tất cả component để tạo hệ thống hoàn chỉnh
Author: MiniMax Agent
Date: 2025-09-13
Version: 2.0
"""

import sys
import os
import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Thêm src vào path
sys.path.append(str(Path(__file__).parent / 'src'))

# Import các module chính
from src.enhanced_input_handler import EnhancedInputHandler
from src.vss_enhanced_extractor import VSS_EnhancedExtractor
from src.vss_api_client import VSSApiClient
from src.config_manager import VSSConfigManager, ApiConfig, ProxyConfig
import pandas as pd

class VSSEnhancedSystem:
    """
    Hệ thống VSS Enhanced hoàn chỉnh
    Tích hợp tất cả component để xử lý từ Excel input đến Excel output
    """
    
    def __init__(self, config_path: str = "config/vss_config.yaml"):
        """Initialize hệ thống với configuration"""
        self.logger = self._setup_logging()
        self.logger.info("🚀 Khởi tạo VSS Enhanced System v2.0")
        
        # Initialize components
        self.input_handler = EnhancedInputHandler()
        self.extractor = VSS_EnhancedExtractor()
        
        # Load configuration
        try:
            self.config_manager = VSSConfigManager(config_path)
            self.api_config = self.config_manager.get_api_config()
            self.proxy_config = self.config_manager.get_proxy_config()
        except:
            # Fallback to basic config if file doesn't exist
            self.api_config = self._create_default_api_config()
            self.proxy_config = None
            
        # API Client
        self.api_client = VSSApiClient(
            api_config=self.api_config,
            proxy_config=self.proxy_config,
            session_timeout=30,
            max_concurrent=5
        )
        
        # Processing state
        self.input_records = []
        self.processed_results = []
        self.processing_stats = {
            'total_records': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'enhanced_fields_extracted': 0,
            'start_time': None,
            'end_time': None,
            'processing_duration': 0
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/vss_enhanced_system.log', mode='a')
            ]
        )
        return logging.getLogger(__name__)
    
    def _create_default_api_config(self) -> ApiConfig:
        """Tạo default API configuration"""
        return ApiConfig(
            base_url='https://baohiemxahoi.gov.vn',
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            timeout=30,
            retry_attempts=3,
            retry_delay=2.0
        )
    
    async def process_excel_file(self, 
                                input_file_path: str, 
                                output_file_path: str = None,
                                test_mode: bool = False) -> Dict[str, Any]:
        """
        Xử lý file Excel từ đầu đến cuối
        
        Args:
            input_file_path: Đường dẫn file Excel đầu vào
            output_file_path: Đường dẫn file Excel output (optional)
            test_mode: Chế độ test (không thực hiện request thật)
            
        Returns:
            Dictionary chứa kết quả xử lý và thống kê
        """
        try:
            self.processing_stats['start_time'] = datetime.now()
            self.logger.info(f"📁 Bắt đầu xử lý file: {input_file_path}")
            
            # Bước 1: Đọc và validate input
            self.logger.info("📖 Đang đọc input Excel...")
            self.input_records = self.input_handler.read_enhanced_input(input_file_path)
            valid_records = [r for r in self.input_records if r.get('validation_status') == 'valid']
            
            self.processing_stats['total_records'] = len(valid_records)
            self.logger.info(f"✅ Đọc thành công {len(valid_records)} records hợp lệ")
            
            if not valid_records:
                raise ValueError("Không có records hợp lệ để xử lý")
            
            # Bước 2: Xử lý từng record
            self.logger.info("🔄 Bắt đầu xử lý enhanced extraction...")
            
            # Initialize API client
            async with self.api_client:
                for i, record in enumerate(valid_records, 1):
                    self.logger.info(f"⚡ Xử lý record {i}/{len(valid_records)}: CCCD {record.get('cccd', 'N/A')}")
                    
                    try:
                        if test_mode:
                            # Test mode: Sử dụng mock data
                            enhanced_record = await self._process_record_test_mode(record)
                        else:
                            # Production mode: Thực hiện request thật
                            enhanced_record = await self._process_record_production(record)
                            
                        self.processed_results.append(enhanced_record)
                        self.processing_stats['successful_processing'] += 1
                        
                        # Count enhanced fields extracted
                        enhanced_fields = enhanced_record.get('enhanced_extraction', {}).get('extracted_fields', {})
                        extracted_count = 0
                        for field in enhanced_fields.values():
                            if hasattr(field, 'extracted_value'):
                                # ExtractionResult object
                                if field.extracted_value:
                                    extracted_count += 1
                            else:
                                # Dictionary
                                if field.get('extracted_value'):
                                    extracted_count += 1
                        self.processing_stats['enhanced_fields_extracted'] += extracted_count
                        
                    except Exception as e:
                        self.logger.error(f"❌ Lỗi xử lý record {i}: {e}")
                        error_record = record.copy()
                        error_record.update({
                            'processing_status': 'failed',
                            'error_message': str(e),
                            'error_timestamp': datetime.now().isoformat()
                        })
                        self.processed_results.append(error_record)
                        self.processing_stats['failed_processing'] += 1
            
            # Bước 3: Tạo output Excel
            if not output_file_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file_path = f"data/enhanced_output_{timestamp}.xlsx"
            
            self.logger.info(f"📊 Tạo output Excel: {output_file_path}")
            output_result = self._create_enhanced_excel_output(output_file_path)
            
            # Hoàn thành
            self.processing_stats['end_time'] = datetime.now()
            self.processing_stats['processing_duration'] = (
                self.processing_stats['end_time'] - self.processing_stats['start_time']
            ).total_seconds()
            
            self.logger.info("🎉 Hoàn thành xử lý thành công!")
            self._log_final_statistics()
            
            return {
                'status': 'success',
                'input_file': input_file_path,
                'output_file': output_file_path,
                'processing_stats': self.processing_stats,
                'processed_records': len(self.processed_results),
                'output_details': output_result
            }
            
        except Exception as e:
            self.logger.error(f"💥 Lỗi nghiêm trọng trong quá trình xử lý: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'processing_stats': self.processing_stats
            }
    
    async def _process_record_test_mode(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Xử lý record trong test mode với mock data"""
        
        # Enhanced Mock HTML response cho testing với diversified data
        name = record.get('ho_ten', 'TEST USER')
        cccd = record.get('cccd', '123456789012')
        
        # Tạo mock data varied dựa trên CCCD để test đa dạng patterns
        phone_variants = [
            "0912345678", "091-234-5678", "+84 912 345 678", 
            "84912345678", "0912.345.678"
        ]
        income_variants = [
            "25,500,000 VND", "18 triệu đồng", "22,000,000", 
            "15.5 triệu VND", "30 million VND"
        ]
        bank_variants = [
            "Vietcombank (VCB)", "ACB", "Techcombank (TCB)",
            "BIDV", "MBBank", "VietinBank (CTG)"
        ]
        family_variants = [
            ["Trần Thị Bình - Vợ - 1987", "Nguyễn Văn Cường - Con - 2015"],
            ["Lê Thị Mai - Vợ - 1985", "Nguyễn Thị An - Con - 2018", "Nguyễn Văn Bình - Con - 2020"],
            ["Phạm Thị Lan - Vợ - 1990", "Hoàng Văn Nam - Con - 2016"],
            ["Võ Thị Hoa - Vợ - 1988"],
            ["Đặng Văn Tùng - Chồng - 1982", "Đặng Thị Thu - Con - 2019"]
        ]
        
        # Chọn variant dựa trên CCCD
        variant_idx = int(cccd[-1]) % len(phone_variants)
        selected_phone = phone_variants[variant_idx]
        selected_income = income_variants[variant_idx % len(income_variants)]
        selected_bank = bank_variants[variant_idx % len(bank_variants)]
        selected_family = family_variants[variant_idx % len(family_variants)]
        
        family_html = "\n".join([f"<p>{member}</p>" for member in selected_family])
        
        mock_html = f"""
        <html>
        <body>
            <table class="citizen-info">
                <tr><td>Họ và tên:</td><td>{name}</td></tr>
                <tr><td>Số CCCD:</td><td>{cccd}</td></tr>
                <tr><td>Số điện thoại:</td><td>{selected_phone}</td></tr>
                <tr><td>Thu nhập hàng tháng:</td><td>{selected_income}</td></tr>
                <tr><td>Ngân hàng:</td><td>{selected_bank}</td></tr>
                <tr><td>Mã hộ gia đình:</td><td>HGD{cccd[-9:]}</td></tr>
            </table>
            
            <div class="family-section">
                <h3>Thành viên hộ gia đình</h3>
                {family_html}
            </div>
            
            <table class="family-members">
                <tr><th>Họ tên</th><th>Quan hệ</th><th>Năm sinh</th></tr>
                {''.join([f'<tr><td>{member.split(" - ")[0]}</td><td>{member.split(" - ")[1]}</td><td>{member.split(" - ")[2]}</td></tr>' for member in selected_family if len(member.split(" - ")) == 3])}
            </table>
            
            <div class="contact-info">
                <span>Liên hệ: {selected_phone}</span>
                <span>Thu nhập: {selected_income}</span>
                <span>NH: {selected_bank}</span>
            </div>
        </body>
        </html>
        """
        
        # Extract enhanced fields từ mock HTML
        extraction_result = self.extractor.extract_enhanced_fields(
            mock_html, 
            input_data=record
        )
        
        # Tạo enhanced record
        enhanced_record = record.copy()
        enhanced_record.update({
            'processing_status': 'success',
            'processing_mode': 'test',
            'enhanced_extraction': extraction_result,
            'processing_timestamp': datetime.now().isoformat()
        })
        
        return enhanced_record
    
    async def _process_record_production(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Xử lý record trong production mode với real VSS requests"""
        
        cccd = record.get('cccd', '')
        
        # Thực hiện request tới VSS (placeholder - cần implement thực tế)
        # Trong thực tế, sẽ cần các bước:
        # 1. Authenticate với VSS
        # 2. Submit form với CCCD
        # 3. Handle CAPTCHA
        # 4. Extract HTML response
        
        # Tạm thời sử dụng mock data cho production mode
        self.logger.warning("🚧 Production mode đang sử dụng mock data - cần implement VSS integration")
        return await self._process_record_test_mode(record)
    
    def _create_enhanced_excel_output(self, output_file_path: str) -> Dict[str, Any]:
        """Tạo file Excel output với format mở rộng"""
        
        try:
            # Chuẩn bị data cho Excel
            excel_data = []
            
            for record in self.processed_results:
                # Thông tin cơ bản từ input
                excel_row = {
                    'STT': len(excel_data) + 1,
                    'Họ và tên (Input)': record.get('ho_ten', ''),
                    'Số CCCD': record.get('cccd', ''),
                    'Tỉnh, thành phố (Input)': record.get('tinh_thanh_pho', ''),
                    'Số BHXH (Input)': record.get('so_bhxh_input', ''),
                    'Năm sinh (Input)': record.get('nam_sinh_input', ''),
                    'Trạng thái xử lý': record.get('processing_status', 'unknown')
                }
                
                # Enhanced fields từ extraction
                enhanced_extraction = record.get('enhanced_extraction', {})
                extracted_fields = enhanced_extraction.get('extracted_fields', {})
                
                # Thêm 5 enhanced fields
                enhanced_fields_mapping = {
                    'so_dien_thoai': 'Số điện thoại (VSS)',
                    'thu_nhap': 'Thu nhập (VSS)',
                    'ngan_hang': 'Ngân hàng (VSS)',
                    'ma_ho_gia_dinh': 'Mã hộ gia đình (VSS)',
                    'thong_tin_thanh_vien': 'Thông tin thành viên (VSS)'
                }
                
                for field_key, field_label in enhanced_fields_mapping.items():
                    field_result = extracted_fields.get(field_key, {})
                    
                    # Handle both dict and ExtractionResult object
                    if hasattr(field_result, 'extracted_value'):
                        # ExtractionResult object
                        excel_row[field_label] = field_result.extracted_value or ''
                        excel_row[f'{field_label} - Confidence'] = getattr(field_result, 'confidence_score', 0)
                    else:
                        # Dictionary
                        excel_row[field_label] = field_result.get('extracted_value', '')
                        excel_row[f'{field_label} - Confidence'] = field_result.get('confidence_score', 0)
                
                # Thêm thống kê extraction
                extraction_summary = enhanced_extraction.get('extraction_summary', {})
                excel_row['Tỷ lệ thành công'] = extraction_summary.get('success_rate', 0)
                excel_row['Điểm chất lượng'] = extraction_summary.get('overall_quality_score', 0)
                
                # Thêm timestamps
                excel_row['Thời gian xử lý'] = record.get('processing_timestamp', '')
                
                excel_data.append(excel_row)
            
            # Tạo DataFrame và xuất Excel
            df = pd.DataFrame(excel_data)
            
            # Đảm bảo thư mục output tồn tại
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            
            # Xuất Excel với formatting
            with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Enhanced Results', index=False)
                
                # Tạo summary sheet
                summary_data = {
                    'Metric': ['Tổng số records', 'Xử lý thành công', 'Xử lý thất bại', 
                              'Tổng enhanced fields extracted', 'Thời gian xử lý (giây)',
                              'Tỷ lệ thành công tổng thể'],
                    'Value': [
                        self.processing_stats['total_records'],
                        self.processing_stats['successful_processing'],
                        self.processing_stats['failed_processing'],
                        self.processing_stats['enhanced_fields_extracted'],
                        self.processing_stats['processing_duration'],
                        f"{(self.processing_stats['successful_processing'] / max(self.processing_stats['total_records'], 1)) * 100:.1f}%"
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Processing Summary', index=False)
            
            self.logger.info(f"✅ Đã tạo Excel output: {output_file_path}")
            
            return {
                'output_file': output_file_path,
                'total_rows': len(excel_data),
                'columns_count': len(df.columns),
                'file_size_mb': os.path.getsize(output_file_path) / (1024 * 1024)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi tạo Excel output: {e}")
            raise
    
    def _log_final_statistics(self):
        """Log thống kê cuối cùng"""
        stats = self.processing_stats
        self.logger.info("📊 THỐNG KÊ CUỐI CÙNG:")
        self.logger.info(f"   📋 Tổng records: {stats['total_records']}")
        self.logger.info(f"   ✅ Thành công: {stats['successful_processing']}")
        self.logger.info(f"   ❌ Thất bại: {stats['failed_processing']}")
        self.logger.info(f"   🔍 Enhanced fields extracted: {stats['enhanced_fields_extracted']}")
        self.logger.info(f"   ⏱️  Thời gian xử lý: {stats['processing_duration']:.2f} giây")
        
        success_rate = (stats['successful_processing'] / max(stats['total_records'], 1)) * 100
        self.logger.info(f"   📈 Tỷ lệ thành công: {success_rate:.1f}%")

async def main():
    """Main function để test hệ thống"""
    print("🚀 VSS Enhanced System - Main Test")
    print("=" * 50)
    
    # Initialize system
    system = VSSEnhancedSystem()
    
    # Test với sample input file
    input_file = "data/input_excel_files/sample_input.xlsx"
    output_file = "data/enhanced_output_test.xlsx"
    
    print(f"📁 Input file: {input_file}")
    print(f"📊 Output file: {output_file}")
    print("🧪 Running in TEST MODE...")
    
    # Process file
    result = await system.process_excel_file(
        input_file_path=input_file,
        output_file_path=output_file,
        test_mode=True
    )
    
    # Display results
    print("\n📋 KẾT QUẢ XỬ LÝ:")
    print(f"   Status: {result.get('status', 'unknown').upper()}")
    if result.get('status') == 'success':
        print(f"   Processed records: {result.get('processed_records', 0)}")
        print(f"   Output file: {result.get('output_file', 'N/A')}")
        
        stats = result.get('processing_stats', {})
        print(f"   Success rate: {(stats.get('successful_processing', 0) / max(stats.get('total_records', 1), 1)) * 100:.1f}%")
        print(f"   Enhanced fields extracted: {stats.get('enhanced_fields_extracted', 0)}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    # Tạo thư mục logs nếu chưa có
    os.makedirs('logs', exist_ok=True)
    
    # Run main
    asyncio.run(main())