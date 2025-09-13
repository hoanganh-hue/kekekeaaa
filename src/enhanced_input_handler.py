#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Input Handler for VSS System
Xử lý đầu vào mở rộng cho hệ thống VSS với cấu trúc Excel mới
Author: MiniMax Agent
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import os
import json

class EnhancedInputHandler:
    """Class xử lý đầu vào mở rộng cho hệ thống VSS"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Định nghĩa cấu trúc cột mới
        self.new_required_columns = [
            'Họ và tên',
            'Số CCCD', 
            'Tỉnh, thành phố',
            'Số bảo hiểm xã hội',
            'Năm sinh'
        ]
        
        # Mapping với cấu trúc cũ (backward compatibility)
        self.legacy_column_mapping = {
            'Số ĐIện Thoại': 'Số điện thoại (input)',
            'Số CCCD': 'Số CCCD',
            'HỌ VÀ TÊN ': 'Họ và tên',
            'ĐỊA CHỈ': 'Địa chỉ (input)'
        }
        
        # Validation rules
        self.validation_rules = {
            'Số CCCD': {'type': 'str', 'length': 12, 'pattern': r'^\d{12}$'},
            'Số bảo hiểm xã hội': {'type': 'str', 'length': 10, 'pattern': r'^\d{10}$'},
            'Năm sinh': {'type': 'int', 'min': 1950, 'max': 2010}
        }
        
        self.processed_records = []
        self.validation_errors = []
        
    def detect_input_format(self, file_path: str) -> str:
        """Tự động phát hiện định dạng file đầu vào"""
        try:
            df = pd.read_excel(file_path)
            columns = list(df.columns)
            
            # Kiểm tra định dạng mới
            new_format_match = sum(1 for col in self.new_required_columns if col in columns)
            
            # Kiểm tra định dạng cũ
            legacy_format_match = sum(1 for col in self.legacy_column_mapping.keys() if col in columns)
            
            if new_format_match >= 4:  # Ít nhất 4/5 cột khớp
                return 'new_format'
            elif legacy_format_match >= 3:  # Ít nhất 3/4 cột khớp
                return 'legacy_format'
            else:
                return 'unknown_format'
                
        except Exception as e:
            self.logger.error(f"Lỗi phát hiện format: {e}")
            return 'error'
    
    def read_enhanced_input(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Đọc file Excel với cấu trúc mới (5 cột)
        Returns: List of dictionaries với thông tin đầy đủ
        """
        try:
            # Phát hiện format
            input_format = self.detect_input_format(file_path)
            self.logger.info(f"Phát hiện định dạng: {input_format}")
            
            df = pd.read_excel(file_path)
            
            if input_format == 'new_format':
                return self._process_new_format(df)
            elif input_format == 'legacy_format':
                return self._process_legacy_format(df)
            else:
                raise ValueError(f"Định dạng file không được hỗ trợ: {list(df.columns)}")
                
        except Exception as e:
            self.logger.error(f"Lỗi đọc file đầu vào: {e}")
            raise
    
    def _process_new_format(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Xử lý định dạng mới với 5 cột"""
        records = []
        
        for index, row in df.iterrows():
            try:
                # Tạo record chuẩn hóa
                record = {
                    'ho_ten': self._clean_text(row.get('Họ và tên', '')),
                    'cccd': self._clean_cccd(row.get('Số CCCD', '')),
                    'tinh_thanh_pho': self._clean_text(row.get('Tỉnh, thành phố', '')),
                    'so_bhxh_input': self._clean_bhxh(row.get('Số bảo hiểm xã hội', '')),
                    'nam_sinh_input': self._clean_year(row.get('Năm sinh', 0)),
                    
                    # Metadata
                    'input_row_index': index + 1,
                    'input_format': 'new_format',
                    'processing_timestamp': datetime.now().isoformat(),
                    'validation_status': 'pending'
                }
                
                # Validation
                validation_result = self._validate_record(record)
                record['validation_status'] = 'valid' if validation_result['is_valid'] else 'invalid'
                record['validation_errors'] = validation_result['errors']
                
                records.append(record)
                
            except Exception as e:
                self.logger.error(f"Lỗi xử lý dòng {index + 1}: {e}")
                self.validation_errors.append({
                    'row': index + 1,
                    'error': str(e),
                    'data': row.to_dict()
                })
        
        self.logger.info(f"Đã xử lý {len(records)} bản ghi định dạng mới")
        return records
    
    def _process_legacy_format(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Xử lý định dạng cũ với backward compatibility"""
        records = []
        
        for index, row in df.iterrows():
            try:
                # Mapping từ cấu trúc cũ sang mới
                record = {
                    'ho_ten': self._clean_text(row.get('HỌ VÀ TÊN ', '') or row.get('HỌ VÀ TÊN', '')),
                    'cccd': self._clean_cccd(row.get('Số CCCD', '')),
                    'tinh_thanh_pho': self._extract_province_from_address(row.get('ĐỊA CHỈ', '')),
                    'so_dien_thoai_input': self._clean_phone(row.get('Số ĐIện Thoại', '')),
                    'dia_chi_input': self._clean_text(row.get('ĐỊA CHỈ', '')),
                    
                    # Trường chưa có trong format cũ
                    'so_bhxh_input': '',  # Sẽ được trích xuất từ VSS
                    'nam_sinh_input': 0,  # Sẽ được trích xuất từ VSS
                    
                    # Metadata
                    'input_row_index': index + 1,
                    'input_format': 'legacy_format',
                    'processing_timestamp': datetime.now().isoformat(),
                    'validation_status': 'partial'  # Thiếu một số trường
                }
                
                records.append(record)
                
            except Exception as e:
                self.logger.error(f"Lỗi xử lý dòng legacy {index + 1}: {e}")
                self.validation_errors.append({
                    'row': index + 1,
                    'error': str(e),
                    'data': row.to_dict()
                })
        
        self.logger.info(f"Đã xử lý {len(records)} bản ghi định dạng legacy")
        return records
    
    def _validate_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate một record theo rules"""
        errors = []
        is_valid = True
        
        # Validate CCCD
        cccd = record.get('cccd', '')
        if not cccd or len(cccd) != 12 or not cccd.isdigit():
            errors.append("CCCD phải có đúng 12 số")
            is_valid = False
        
        # Validate họ tên
        ho_ten = record.get('ho_ten', '').strip()
        if not ho_ten or len(ho_ten) < 2:
            errors.append("Họ tên không hợp lệ")
            is_valid = False
        
        # Validate năm sinh
        nam_sinh = record.get('nam_sinh_input', 0)
        if nam_sinh and (nam_sinh < 1950 or nam_sinh > 2010):
            errors.append("Năm sinh phải từ 1950-2010")
            is_valid = False
        
        # Validate số BHXH (nếu có) - cho phép linh hoạt hơn
        so_bhxh = record.get('so_bhxh_input', '')
        if so_bhxh and len(so_bhxh) >= 8 and not so_bhxh.isdigit():
            errors.append("Số BHXH phải là số")
            is_valid = False
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'score': 1.0 if is_valid else max(0.0, 1.0 - len(errors) * 0.2)
        }
    
    def _clean_text(self, text: Any) -> str:
        """Chuẩn hóa text"""
        if pd.isna(text):
            return ''
        return str(text).strip()
    
    def _clean_cccd(self, cccd: Any) -> str:
        """Chuẩn hóa số CCCD"""
        if pd.isna(cccd):
            return ''
        cccd_str = str(cccd).replace(' ', '').replace('-', '').replace('.', '')
        return cccd_str.zfill(12) if cccd_str.isdigit() else cccd_str
    
    def _clean_bhxh(self, bhxh: Any) -> str:
        """Chuẩn hóa số BHXH"""
        if pd.isna(bhxh):
            return ''
        bhxh_str = str(int(bhxh)).replace(' ', '').replace('-', '').replace('.', '') if isinstance(bhxh, float) else str(bhxh).replace(' ', '').replace('-', '').replace('.', '')
        return bhxh_str.zfill(10) if bhxh_str.isdigit() else bhxh_str
    
    def _clean_phone(self, phone: Any) -> str:
        """Chuẩn hóa số điện thoại"""
        if pd.isna(phone):
            return ''
        phone_str = str(phone).replace(' ', '').replace('-', '').replace('+84', '0')
        return phone_str if phone_str.isdigit() else ''
    
    def _clean_year(self, year: Any) -> int:
        """Chuẩn hóa năm sinh"""
        if pd.isna(year):
            return 0
        try:
            return int(year)
        except (ValueError, TypeError):
            return 0
    
    def _extract_province_from_address(self, address: str) -> str:
        """Trích xuất tỉnh/thành phố từ địa chỉ"""
        if not address:
            return ''
        
        # Mapping các tỉnh/thành phố phổ biến
        province_mapping = {
            'hà nội': 'Hà Nội',
            'hồ chí minh': 'TP. Hồ Chí Minh',
            'hải phòng': 'Hải Phòng',
            'đà nẵng': 'Đà Nẵng',
            'cần thơ': 'Cần Thơ',
            'hải dương': 'Hải Dương',
            'nam định': 'Nam Định',
            'thái bình': 'Thái Bình',
            'hưng yên': 'Hưng Yên',
            'vĩnh phúc': 'Vĩnh Phúc'
        }
        
        address_lower = address.lower()
        for key, value in province_mapping.items():
            if key in address_lower:
                return value
        
        return address.split(',')[-1].strip() if ',' in address else ''
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Lấy thống kê xử lý"""
        total_records = len(self.processed_records)
        valid_records = sum(1 for r in self.processed_records if r.get('validation_status') == 'valid')
        
        return {
            'total_processed': total_records,
            'valid_records': valid_records,
            'invalid_records': total_records - valid_records,
            'validation_errors': len(self.validation_errors),
            'success_rate': (valid_records / max(total_records, 1)) * 100,
            'processing_timestamp': datetime.now().isoformat()
        }
    
    def save_processing_report(self, output_path: str):
        """Lưu báo cáo xử lý đầu vào"""
        report = {
            'summary': self.get_processing_summary(),
            'processed_records': self.processed_records,
            'validation_errors': self.validation_errors
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Đã lưu báo cáo xử lý: {output_path}")

# Convenience functions để sử dụng dễ dàng
def read_input_excel(file_path: str) -> List[Dict[str, Any]]:
    """Function wrapper để đọc file Excel đầu vào"""
    handler = EnhancedInputHandler()
    return handler.read_enhanced_input(file_path)

def validate_input_data(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Function wrapper để validate dữ liệu"""
    handler = EnhancedInputHandler()
    handler.processed_records = records
    return handler.get_processing_summary()
