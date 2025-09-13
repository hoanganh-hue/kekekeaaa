#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Data Extractor for VSS System
Mở rộng khả năng trích xuất dữ liệu từ VSS với các trường mới
Author: MiniMax Agent
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import asyncio

class EnhancedDataExtractor:
    """Class mở rộng trích xuất dữ liệu từ VSS"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Enhanced extraction patterns
        self.extraction_patterns = {
            'ma_ho_gia_dinh': {
                'selectors': [
                    'td:contains("Mã hộ")',
                    'td:contains("Hộ gia đình")', 
                    'span[class*="household"]',
                    'div[class*="ma-ho"]'
                ],
                'regex_patterns': [
                    r'Mã\s*hộ[:\s]*([A-Z0-9]{8,12})',
                    r'Household[:\s]*([A-Z0-9]{8,12})',
                    r'HGD[:\s]*([A-Z0-9]{8,12})'
                ]
            },
            'so_dien_thoai': {
                'selectors': [
                    'td:contains("Điện thoại")',
                    'td:contains("SĐT")',
                    'span[class*="phone"]',
                    'div[class*="contact"]'
                ],
                'regex_patterns': [
                    r'(?:Điện thoại|SĐT|Phone)[:\s]*((?:0|84|\+84)[1-9][0-9]{7,9})',
                    r'(?:Tel|Mobile)[:\s]*((?:0|84|\+84)[1-9][0-9]{7,9})',
                    r'\b((?:0|84|\+84)[1-9][0-9]{7,9})\b'
                ]
            },
            'thu_nhap': {
                'selectors': [
                    'td:contains("Thu nhập")',
                    'td:contains("Lương")',
                    'span[class*="salary"]',
                    'div[class*="income"]'
                ],
                'regex_patterns': [
                    r'(?:Thu nhập|Lương|Income)[:\s]*([0-9,.]+)\s*(?:VND|đồng)',
                    r'(?:Salary|Wage)[:\s]*([0-9,.]+)',
                    r'([0-9]{1,3}(?:,[0-9]{3})*)\s*(?:VND|đồng)'
                ]
            },
            'ngan_hang': {
                'selectors': [
                    'td:contains("Ngân hàng")',
                    'td:contains("Bank")',
                    'span[class*="bank"]',
                    'div[class*="banking"]'
                ],
                'regex_patterns': [
                    r'(?:Ngân hàng|Bank)[:\s]*([A-Z]{2,10})',
                    r'(?:ACB|VCB|TCB|CTG|MBB|VTB|SHB|EIB|OCB|TPB|HDB|LPB|VAB|PGB|NVB|KLB|MSB|SEA|VIB|BID)',
                    r'Bank\s*:\s*([A-Za-z\s]{3,30})'
                ]
            }
        }
        
        # Enhanced parsing strategies
        self.parsing_strategies = [
            'table_based_extraction',
            'div_based_extraction', 
            'json_embedded_extraction',
            'attribute_based_extraction'
        ]
        
        # Province/Bank mapping for normalization
        self.normalization_maps = {
            'banks': {
                'ACB': 'Á Châu (ACB)', 'VCB': 'Vietcombank', 'TCB': 'Techcombank',
                'CTG': 'VietinBank', 'MBB': 'MB Bank', 'VTB': 'Vietbank',
                'SHB': 'SHB', 'EIB': 'Eximbank', 'OCB': 'OCB', 'TPB': 'TPBank',
                'HDB': 'HDBank', 'LPB': 'LienVietPostBank', 'VAB': 'VietABank',
                'PGB': 'PGBank', 'NVB': 'NCB', 'KLB': 'KienLongBank',
                'MSB': 'MSB', 'SEA': 'SeABank', 'VIB': 'VIB', 'BID': 'BIDV'
            },
            'provinces': {
                'hn': 'Hà Nội', 'hcm': 'TP. Hồ Chí Minh', 'hp': 'Hải Phòng',
                'dn': 'Đà Nẵng', 'ct': 'Cần Thơ', 'hd': 'Hải Dương',
                'nd': 'Nam Định', 'tb': 'Thái Bình', 'hy': 'Hưng Yên'
            }
        }
        
    def parse_enhanced_bhxh_data(self, html_content: str, cccd: str = "", 
                                original_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Parse HTML response từ VSS để trích xuất dữ liệu mở rộng
        
        Args:
            html_content: HTML response từ VSS
            cccd: Số CCCD để validation
            original_data: Dữ liệu gốc từ input (nếu có)
            
        Returns:
            Dictionary chứa dữ liệu đã được trích xuất và mở rộng
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract basic data (từ logic cũ)
            basic_data = self._extract_basic_fields(soup, cccd)
            
            # Extract enhanced data (mới)
            enhanced_data = self._extract_enhanced_fields(soup)
            
            # Extract embedded JSON data (nếu có)
            json_data = self._extract_json_data(html_content)
            
            # Merge all data
            merged_data = self._merge_extracted_data(basic_data, enhanced_data, json_data, original_data)
            
            # Final validation và normalization
            validated_data = self._validate_and_normalize(merged_data, cccd)
            
            # Add extraction metadata
            validated_data.update({
                'extraction_timestamp': datetime.now().isoformat(),
                'extraction_method': 'enhanced_parser_v1.0',
                'html_length': len(html_content),
                'soup_elements_count': len(soup.find_all()),
                'extraction_success': True
            })
            
            return validated_data
            
        except Exception as e:
            self.logger.error(f"Lỗi parse enhanced BHXH data: {e}")
            return {
                'extraction_success': False,
                'extraction_error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }
    
    def _extract_basic_fields(self, soup: BeautifulSoup, cccd: str) -> Dict[str, Any]:
        """Trích xuất các trường cơ bản (từ logic hiện có)"""
        basic_data = {}
        
        try:
            # Tìm bảng dữ liệu chính
            main_tables = soup.find_all('table')
            
            for table in main_tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = self._normalize_text(cells[0].get_text())
                        value = self._normalize_text(cells[1].get_text())
                        
                        # Map các trường cơ bản
                        if any(term in key.lower() for term in ['họ', 'tên', 'name']):
                            basic_data['ho_ten'] = value
                        elif any(term in key.lower() for term in ['sinh', 'birth']):
                            basic_data['ngay_sinh'] = value
                        elif any(term in key.lower() for term in ['giới', 'gender', 'sex']):
                            basic_data['gioi_tinh'] = value
                        elif any(term in key.lower() for term in ['bhxh', 'social']):
                            basic_data['so_bhxh'] = value
                        elif any(term in key.lower() for term in ['trạng', 'status']):
                            basic_data['trang_thai'] = value
                        elif any(term in key.lower() for term in ['đơn vị', 'unit', 'company']):
                            basic_data['don_vi_lam_viec'] = value
                        elif any(term in key.lower() for term in ['lương', 'salary']):
                            basic_data['muc_luong'] = value
                        elif any(term in key.lower() for term in ['nơi cấp', 'issued']):
                            basic_data['noi_cap'] = value
                        elif any(term in key.lower() for term in ['ngày cấp', 'issue date']):
                            basic_data['ngay_cap'] = value
            
            return basic_data
            
        except Exception as e:
            self.logger.error(f"Lỗi extract basic fields: {e}")
            return {}
    
    def _extract_enhanced_fields(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Trích xuất các trường mở rộng mới"""
        enhanced_data = {}
        
        # Extract từng trường theo pattern
        for field_name, patterns in self.extraction_patterns.items():
            extracted_value = self._extract_field_by_patterns(soup, field_name, patterns)
            enhanced_data[field_name] = extracted_value
        
        # Thêm logic extraction đặc biệt
        enhanced_data.update(self._extract_special_fields(soup))
        
        return enhanced_data
    
    def _extract_field_by_patterns(self, soup: BeautifulSoup, field_name: str, 
                                 patterns: Dict[str, List]) -> Optional[str]:
        """Trích xuất 1 trường theo patterns định nghĩa"""
        try:
            # Strategy 1: CSS Selectors
            for selector in patterns.get('selectors', []):
                elements = soup.select(selector)
                for element in elements:
                    # Tìm giá trị trong element hiện tại hoặc element kế tiếp
                    value = self._extract_value_from_element(element, field_name)
                    if value:
                        return value
            
            # Strategy 2: Regex Patterns
            full_text = soup.get_text()
            for regex_pattern in patterns.get('regex_patterns', []):
                matches = re.findall(regex_pattern, full_text, re.IGNORECASE)
                if matches:
                    return matches[0] if isinstance(matches[0], str) else matches[0][0]
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Lỗi extract field {field_name}: {e}")
            return None
    
    def _extract_value_from_element(self, element, field_name: str) -> Optional[str]:
        """Trích xuất giá trị từ element"""
        try:
            # Kiểm tra trong element hiện tại
            text = element.get_text().strip()
            
            # Tìm value pattern
            if ':' in text:
                parts = text.split(':', 1)
                if len(parts) == 2:
                    return parts[1].strip()
            
            # Kiểm tra element kế tiếp (sibling)
            next_element = element.find_next_sibling()
            if next_element:
                next_text = next_element.get_text().strip()
                if next_text and len(next_text) > 0:
                    return next_text
            
            # Kiểm tra parent element
            parent = element.parent
            if parent:
                parent_text = parent.get_text().strip()
                # Extract value using field-specific logic
                if field_name == 'ma_ho_gia_dinh':
                    match = re.search(r'[A-Z0-9]{8,12}', parent_text)
                    return match.group(0) if match else None
                elif field_name == 'so_dien_thoai':
                    match = re.search(r'(?:0|84|\+84)[1-9][0-9]{7,9}', parent_text)
                    return match.group(0) if match else None
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Lỗi extract value from element: {e}")
            return None
    
    def _extract_special_fields(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Trích xuất các trường đặc biệt cần logic riêng"""
        special_data = {}
        
        try:
            # Thông tin thành viên hộ gia đình (cần logic đặc biệt)
            household_members = self._extract_household_members(soup)
            if household_members:
                special_data['thong_tin_thanh_vien_hgd'] = household_members
            
            # Address parsing để tìm thêm thông tin
            addresses = self._extract_addresses(soup)
            if addresses:
                special_data['dia_chi_chi_tiet'] = addresses
            
            # Employment information
            employment_info = self._extract_employment_info(soup)
            if employment_info:
                special_data['thong_tin_cong_viec'] = employment_info
            
            return special_data
            
        except Exception as e:
            self.logger.error(f"Lỗi extract special fields: {e}")
            return {}
    
    def _extract_household_members(self, soup: BeautifulSoup) -> Optional[List[Dict]]:
        """Trích xuất thông tin thành viên hộ gia đình"""
        try:
            members = []
            
            # Tìm các bảng có thể chứa thông tin thành viên
            tables = soup.find_all('table')
            
            for table in tables:
                # Tìm header chứa "thành viên", "hộ gia đình"
                headers = table.find_all(['th', 'td'])
                
                for header in headers:
                    header_text = header.get_text().lower()
                    if any(term in header_text for term in ['thành viên', 'hộ gia đình', 'member', 'family']):
                        # Tìm các dòng dữ liệu trong bảng này
                        rows = table.find_all('tr')[1:]  # Bỏ header row
                        
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 2:
                                member_info = {}
                                
                                # Parse thông tin thành viên
                                for i, cell in enumerate(cells):
                                    cell_text = cell.get_text().strip()
                                    if cell_text:
                                        if i == 0:
                                            member_info['ten'] = cell_text
                                        elif i == 1:
                                            member_info['quan_he'] = cell_text
                                        elif i == 2:
                                            member_info['nam_sinh'] = cell_text
                                
                                if member_info:
                                    members.append(member_info)
            
            return members if members else None
            
        except Exception as e:
            self.logger.debug(f"Lỗi extract household members: {e}")
            return None
    
    def _extract_addresses(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Trích xuất các địa chỉ chi tiết"""
        try:
            addresses = {}
            
            # Tìm các loại địa chỉ
            address_types = ['thường trú', 'tạm trú', 'hiện tại', 'liên hệ']
            
            for addr_type in address_types:
                # Tìm element chứa loại địa chỉ này
                elements = soup.find_all(text=re.compile(addr_type, re.IGNORECASE))
                
                for element in elements:
                    parent = element.parent
                    if parent:
                        # Tìm địa chỉ trong parent hoặc sibling
                        addr_text = self._find_address_text(parent)
                        if addr_text:
                            addresses[addr_type] = addr_text
                            break
            
            return addresses if addresses else None
            
        except Exception as e:
            self.logger.debug(f"Lỗi extract addresses: {e}")
            return None
    
    def _extract_employment_info(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Trích xuất thông tin công việc chi tiết"""
        try:
            employment = {}
            
            # Các thông tin liên quan đến việc làm
            employment_fields = {
                'chuc_vu': ['chức vụ', 'position', 'title'],
                'phong_ban': ['phòng ban', 'department', 'division'],
                'ma_don_vi': ['mã đơn vị', 'unit code', 'org code'],
                'ngay_bat_dau_lam_viec': ['ngày bắt đầu', 'start date', 'employment date'],
                'loai_hop_dong': ['loại hợp đồng', 'contract type'],
                'che_do_lam_viec': ['chế độ làm việc', 'work regime']
            }
            
            full_text = soup.get_text()
            
            for field, keywords in employment_fields.items():
                for keyword in keywords:
                    pattern = rf'{keyword}[:\s]*([^\n\r]+)'
                    match = re.search(pattern, full_text, re.IGNORECASE)
                    if match:
                        employment[field] = match.group(1).strip()
                        break
            
            return employment if employment else None
            
        except Exception as e:
            self.logger.debug(f"Lỗi extract employment info: {e}")
            return None
    
    def _extract_json_data(self, html_content: str) -> Dict[str, Any]:
        """Trích xuất dữ liệu từ JSON embedded trong HTML"""
        try:
            # Tìm JSON data trong script tags
            json_pattern = r'<script[^>]*>(.*?)</script>'
            script_matches = re.findall(json_pattern, html_content, re.DOTALL)
            
            for script_content in script_matches:
                # Tìm JSON objects
                json_objects = re.findall(r'\{[^{}]*\}', script_content)
                
                for json_str in json_objects:
                    try:
                        json_data = json.loads(json_str)
                        
                        # Kiểm tra có phải dữ liệu BHXH không
                        if any(key in json_data for key in ['bhxh', 'citizen', 'person', 'data']):
                            return json_data
                            
                    except json.JSONDecodeError:
                        continue
            
            return {}
            
        except Exception as e:
            self.logger.debug(f"Lỗi extract JSON data: {e}")
            return {}
    
    def _merge_extracted_data(self, basic_data: Dict, enhanced_data: Dict, 
                            json_data: Dict, original_data: Dict = None) -> Dict[str, Any]:
        """Merge tất cả dữ liệu đã trích xuất"""
        merged = {}
        
        # Merge basic data
        merged.update(basic_data)
        
        # Merge enhanced data with prefix
        for key, value in enhanced_data.items():
            if value:  # Chỉ thêm nếu có giá trị
                merged[f'enhanced_{key}'] = value
        
        # Merge JSON data
        if json_data:
            merged['json_extracted_data'] = json_data
        
        # Add original input data for comparison
        if original_data:
            merged['original_input_data'] = original_data
        
        return merged
    
    def _validate_and_normalize(self, data: Dict[str, Any], cccd: str) -> Dict[str, Any]:
        """Validation và normalization cuối cùng"""
        try:
            # Normalize phone numbers
            if 'enhanced_so_dien_thoai' in data:
                phone = data['enhanced_so_dien_thoai']
                data['enhanced_so_dien_thoai'] = self._normalize_phone(phone)
            
            # Normalize bank names
            if 'enhanced_ngan_hang' in data:
                bank = data['enhanced_ngan_hang']
                data['enhanced_ngan_hang'] = self._normalize_bank_name(bank)
            
            # Normalize income
            if 'enhanced_thu_nhap' in data:
                income = data['enhanced_thu_nhap']
                data['enhanced_thu_nhap'] = self._normalize_income(income)
            
            # Cross-validation với CCCD
            data['cccd_validation'] = self._validate_cccd_consistency(data, cccd)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Lỗi validate and normalize: {e}")
            data['validation_error'] = str(e)
            return data
    
    def _normalize_text(self, text: str) -> str:
        """Chuẩn hóa text"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def _normalize_phone(self, phone: str) -> str:
        """Chuẩn hóa số điện thoại"""
        if not phone:
            return ""
        
        # Remove all non-digits
        digits_only = re.sub(r'\D', '', phone)
        
        # Convert +84 to 0
        if digits_only.startswith('84') and len(digits_only) >= 10:
            digits_only = '0' + digits_only[2:]
        
        # Validate Vietnam phone format
        if re.match(r'^0[1-9][0-9]{7,9}$', digits_only):
            return digits_only
        
        return phone  # Return original if can't normalize
    
    def _normalize_bank_name(self, bank: str) -> str:
        """Chuẩn hóa tên ngân hàng"""
        if not bank:
            return ""
        
        bank_upper = bank.upper()
        
        # Check in mapping
        for code, full_name in self.normalization_maps['banks'].items():
            if code in bank_upper:
                return full_name
        
        return bank  # Return original if not found
    
    def _normalize_income(self, income: str) -> Optional[int]:
        """Chuẩn hóa thu nhập về số"""
        if not income:
            return None
        
        # Remove currency symbols and spaces
        digits_only = re.sub(r'[^\d,.]', '', income)
        digits_only = digits_only.replace(',', '').replace('.', '')
        
        try:
            return int(digits_only) if digits_only else None
        except ValueError:
            return None
    
    def _validate_cccd_consistency(self, data: Dict[str, Any], cccd: str) -> Dict[str, Any]:
        """Validate tính nhất quán của CCCD"""
        validation = {
            'input_cccd': cccd,
            'extracted_cccd_sources': [],
            'consistency_check': 'unknown'
        }
        
        # Tìm CCCD trong dữ liệu đã extract
        extracted_cccds = []
        
        if 'so_bhxh' in data and len(data['so_bhxh']) >= 12:
            extracted_cccd = data['so_bhxh'][:12]
            extracted_cccds.append(('bhxh_number', extracted_cccd))
        
        # So sánh
        if extracted_cccds:
            consistent = all(extracted_cccd == cccd for _, extracted_cccd in extracted_cccds)
            validation['consistency_check'] = 'consistent' if consistent else 'inconsistent'
            validation['extracted_cccd_sources'] = extracted_cccds
        
        return validation
    
    def _find_address_text(self, element) -> Optional[str]:
        """Tìm text địa chỉ từ element"""
        try:
            # Tìm trong element và siblings
            for sibling in element.find_next_siblings():
                text = sibling.get_text().strip()
                if len(text) > 10 and any(char in text for char in [',', 'tỉnh', 'thành phố', 'quận', 'huyện']):
                    return text
            
            # Tìm trong children
            for child in element.children:
                if hasattr(child, 'get_text'):
                    text = child.get_text().strip()
                    if len(text) > 10 and any(char in text for char in [',', 'tỉnh', 'thành phố', 'quận', 'huyện']):
                        return text
            
            return None
            
        except Exception:
            return None

# Integration với Enhanced BHXH Lookup.js
class EnhancedBHXHApiIntegrator:
    """
    Tích hợp với enhanced_bhxh_lookup.js để lấy mã hộ gia đình
    """
    
    def __init__(self, bearer_token: str = None):
        self.bearer_token = bearer_token or "DEMO_TOKEN"  # Placeholder
        self.base_url = 'https://api.quangbinh.gov.vn'
        self.logger = logging.getLogger(__name__)
    
    async def get_household_info_by_bhxh(self, ma_so_bhxh: str) -> Optional[Dict[str, Any]]:
        """
        API 1: Thu thập thông tin hộ gia đình từ mã BHXH
        (Tích hợp từ enhanced_bhxh_lookup.js)
        """
        try:
            # Placeholder implementation - cần tích hợp thực tế
            # Trong production, sẽ call API thực tế
            
            household_data = {
                'ma_ho_gia_dinh': f'HGD{ma_so_bhxh[:6]}',
                'ho_ten': 'Placeholder Name',
                'so_so_cu': f'SO{ma_so_bhxh[3:8]}',
                'ngay_sinh': '01/01/1973',
                'gioi_tinh': 'Nam',
                'dia_diem_khai_sinh': 'Hải Phòng',
                'trang_thai': 'Hoạt động',
                'api_source': 'enhanced_bhxh_lookup_api_1',
                'note': 'Đây là placeholder - cần implement API call thực tế'
            }
            
            self.logger.info(f"Placeholder: Lấy thông tin hộ gia đình cho BHXH {ma_so_bhxh}")
            return household_data
            
        except Exception as e:
            self.logger.error(f"Lỗi get household info: {e}")
            return None
    
    async def get_full_household_info(self, search_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        API 3: Thu thập thông tin hộ gia đình đầy đủ (bao gồm MÃ HỘ GIA ĐÌNH)
        (Tích hợp từ enhanced_bhxh_lookup.js)
        """
        try:
            # Placeholder implementation
            full_household_data = {
                'ma_ho': f'HGD{search_data.get("ho_ten", "")[:3].upper()}{datetime.now().year}',
                'ho_ten': search_data.get('ho_ten', ''),
                'ngay_sinh': search_data.get('ngay_sinh', ''),
                'gioi_tinh': 'Nam',
                'dia_chi': search_data.get('dia_chi', ''),
                'trang_thai': 'Hoạt động',
                'thanh_vien_ho_gia_dinh': [
                    {'ten': 'Thành viên 1', 'quan_he': 'Vợ/Chồng', 'nam_sinh': '1975'},
                    {'ten': 'Thành viên 2', 'quan_he': 'Con', 'nam_sinh': '2000'}
                ],
                'api_source': 'enhanced_bhxh_lookup_api_3',
                'note': 'Đây là placeholder - cần implement API call thực tế'
            }
            
            self.logger.info(f"Placeholder: Lấy thông tin hộ gia đình đầy đủ")
            return full_household_data
            
        except Exception as e:
            self.logger.error(f"Lỗi get full household info: {e}")
            return None

# Convenience function để sử dụng dễ dàng
def extract_enhanced_vss_data(html_content: str, cccd: str = "", 
                             original_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Function wrapper để extract dữ liệu mở rộng"""
    extractor = EnhancedDataExtractor()
    return extractor.parse_enhanced_bhxh_data(html_content, cccd, original_data)

async def integrate_household_data(ma_so_bhxh: str, search_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Function wrapper để tích hợp dữ liệu hộ gia đình"""
    integrator = EnhancedBHXHApiIntegrator()
    
    # Get household info by BHXH number
    household_info = await integrator.get_household_info_by_bhxh(ma_so_bhxh)
    
    # Get full household data
    if search_data:
        full_household_info = await integrator.get_full_household_info(search_data)
    else:
        full_household_info = None
    
    return {
        'household_basic': household_info,
        'household_full': full_household_info,
        'integration_timestamp': datetime.now().isoformat()
    }
