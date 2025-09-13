#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Extractor - Field Patterns Configuration
Chứa tất cả extraction patterns và normalization mappings.

Author: MiniMax Agent
Date: 2025-09-13
Version: 2.1
"""

from typing import Dict
from .data_models import FieldPattern


class FieldPatternsConfig:
    """Configuration class for field extraction patterns"""
    
    @staticmethod
    def get_optimized_patterns() -> Dict[str, FieldPattern]:
        """Get optimized patterns với improved success rates"""
        return {
            'so_dien_thoai': FieldPattern(
                css_selectors=[
                    'td:contains("Điện thoại") + td',
                    'td:contains("SĐT") + td',
                    'span[class*="phone"]',
                    'div[class*="contact"] .phone',
                    '.field-phone .value',
                    '[data-field="phone"]',
                    'input[name*="phone"]',
                    'td:has-text("Phone") + td'
                ],
                xpath_selectors=[
                    '//td[contains(text(),"Điện thoại")]/following-sibling::td[1]',
                    '//td[contains(text(),"SĐT")]/following-sibling::td[1]',
                    '//span[@class and contains(@class,"phone")]/text()',
                    '//div[contains(@class,"contact")]//text()[contains(.,"0")]',
                    '//input[@name and contains(@name,"phone")]/@value'
                ],
                regex_patterns=[
                    r'(?:Điện\s*thoại|SĐT|Phone|Mobile|Tel)[:\s]*([0-9+\-\s\(\)]{9,15})',
                    r'(?:0|\+84|84)[1-9][0-9\s\-\.]{7,10}',
                    r'\b(0[1-9][0-9]{8,9})\b',
                    r'\b(\+84[1-9][0-9]{8,9})\b',
                    r'(?:DT|Tel)[:\s]*([0-9\-\s\+]{9,15})',
                    r'Contact[:\s]*([0-9\-\s\+]{9,15})'
                ],
                context_keywords=[
                    'điện thoại', 'sđt', 'phone', 'mobile', 'tel', 
                    'contact', 'hotline'
                ],
                validation_rules=[
                    'vietnam_phone_format', 'length_check', 'digit_validation'
                ],
                normalization_functions=[
                    'normalize_vietnam_phone', 'remove_formatting'
                ],
                fallback_patterns=[
                    r'[0-9]{10,11}',  # Simple digit pattern
                    r'[\+0-9\-\s\(\)]{9,15}'  # Any phone-like pattern
                ]
            ),
            
            'thu_nhap': FieldPattern(
                css_selectors=[
                    'td:contains("Thu nhập") + td',
                    'td:contains("Lương") + td', 
                    'td:contains("Income") + td',
                    'span[class*="salary"]',
                    'div[class*="income"] .amount',
                    '.field-salary .value',
                    '[data-field="income"]',
                    'input[name*="salary"]'
                ],
                xpath_selectors=[
                    '//td[contains(text(),"Thu nhập")]/following-sibling::td[1]',
                    '//td[contains(text(),"Lương")]/following-sibling::td[1]',
                    '//span[@class and contains(@class,"salary")]/text()',
                    '//div[contains(@class,"income")]//text()[contains(.,"VND") or contains(.,"đồng")]'
                ],
                regex_patterns=[
                    r'(?:Thu\s*nhập|Lương|Income|Salary)[:\s]*([0-9,.]+)\s*(?:VND|đồng|VNĐ)',
                    r'(?:Mức\s*lương|Tiền\s*lương)[:\s]*([0-9,.]+)',
                    r'([0-9]{1,3}(?:[,.][0-9]{3})*)\s*(?:VND|đồng|VNĐ)',
                    r'Income[:\s]*([0-9,.]+)',
                    r'Salary[:\s]*([0-9,.]+)',
                    r'([0-9]+(?:[,.][0-9]{3})*)\s*(?:triệu|million)'
                ],
                context_keywords=[
                    'thu nhập', 'lương', 'income', 'salary', 'wage', 
                    'mức lương', 'tiền lương'
                ],
                validation_rules=[
                    'positive_number', 'reasonable_income_range', 'currency_format'
                ],
                normalization_functions=[
                    'normalize_currency', 'convert_to_number'
                ],
                fallback_patterns=[
                    r'[0-9,.]+\s*(?:VND|đồng)',
                    r'[0-9]+(?:[,.][0-9]{3})*'
                ]
            ),
            
            'ngan_hang': FieldPattern(
                css_selectors=[
                    'td:contains("Ngân hàng") + td',
                    'td:contains("Bank") + td',
                    'span[class*="bank"]',
                    'div[class*="banking"] .name',
                    '.field-bank .value',
                    '[data-field="bank"]',
                    'select[name*="bank"] option[selected]'
                ],
                xpath_selectors=[
                    '//td[contains(text(),"Ngân hàng")]/following-sibling::td[1]',
                    '//td[contains(text(),"Bank")]/following-sibling::td[1]',
                    '//span[@class and contains(@class,"bank")]/text()',
                    '//select[@name and contains(@name,"bank")]//option[@selected]/text()'
                ],
                regex_patterns=[
                    r'(?:Ngân\s*hàng|Bank)[:\s]*([A-Za-z\s]{3,50})',
                    r'\b(ACB|VCB|TCB|CTG|MBB|VTB|SHB|EIB|OCB|TPB|HDB|LPB|VAB|PGB|NVB|KLB|MSB|SEA|VIB|BID|BIDV)\b',
                    r'(?:NH|Bank)\s*([A-Za-z\s]{2,30})',
                    r'Bank\s*Code[:\s]*([A-Z]{3,10})',
                    r'(?:Vietcombank|Techcombank|ACB|BIDV|VietinBank|MB\s*Bank)',
                    r'(?:Sacombank|Eximbank|HDBank|TPBank|VIB|SeABank)'
                ],
                context_keywords=[
                    'ngân hàng', 'bank', 'nh', 'banking', 'tài khoản', 'account'
                ],
                validation_rules=[
                    'known_bank_list', 'bank_code_format'
                ],
                normalization_functions=[
                    'normalize_bank_name', 'standardize_bank_code'
                ],
                fallback_patterns=[
                    r'[A-Z]{2,10}',  # Bank codes
                    r'[A-Za-z\s]{3,30}'  # Bank names
                ]
            ),
            
            'ma_ho_gia_dinh': FieldPattern(
                css_selectors=[
                    'td:contains("Mã hộ") + td',
                    'td:contains("Hộ gia đình") + td',
                    'td:contains("Household") + td',
                    'span[class*="household"]',
                    'div[class*="family"] .code',
                    '.field-household .value',
                    '[data-field="household_code"]'
                ],
                xpath_selectors=[
                    '//td[contains(text(),"Mã hộ")]/following-sibling::td[1]',
                    '//td[contains(text(),"Hộ gia đình")]/following-sibling::td[1]',
                    '//span[@class and contains(@class,"household")]/text()',
                    '//div[contains(@class,"family")]//text()[string-length(.) >= 8]'
                ],
                regex_patterns=[
                    r'(?:Mã\s*hộ|Hộ\s*gia\s*đình|Household)[:\s]*([A-Z0-9]{8,15})',
                    r'HGD[:\s]*([A-Z0-9]{8,15})',
                    r'Family[:\s]*([A-Z0-9]{8,15})',
                    r'(?:Household\s*Code|HH\s*Code)[:\s]*([A-Z0-9]{8,15})',
                    r'\b([A-Z]{2,3}[0-9]{6,12})\b',
                    r'\b(HGD[0-9A-Z]{5,12})\b'
                ],
                context_keywords=[
                    'mã hộ', 'hộ gia đình', 'household', 'family', 
                    'hgd', 'family code'
                ],
                validation_rules=[
                    'alphanumeric_check', 'length_validation', 'prefix_check'
                ],
                normalization_functions=[
                    'uppercase_code', 'remove_spaces'
                ],
                fallback_patterns=[
                    r'[A-Z0-9]{8,15}',
                    r'[A-Z]{2,3}[0-9]{5,12}'
                ]
            ),
            
            'thong_tin_thanh_vien': FieldPattern(
                css_selectors=[
                    # Original patterns
                    'table:contains("Thành viên") tbody tr',
                    'table:contains("Hộ gia đình") tbody tr',
                    'div[class*="members"] .member',
                    '.family-members .member-row',
                    '[data-section="family_members"] tr',
                    # Enhanced patterns
                    'table.family-table tbody tr',
                    'table:contains("Quan hệ") tbody tr',
                    'div.family-members .member',
                    'div:contains("Thành viên") .member',
                    'div:contains("gia đình") div[class*="member"]',
                    '.members p',
                    'div.members div',
                    '.family-text',
                    'div.household-footer .family-text'
                ],
                xpath_selectors=[
                    '//table[contains(.,"Thành viên")]//tbody//tr',
                    '//table[contains(.,"Hộ gia đình")]//tbody//tr[position()>1]',
                    '//div[@class and contains(@class,"members")]//div[@class and contains(@class,"member")]',
                    '//div[contains(.,"Thành viên")]//text()[contains(.,"Vợ") or contains(.,"Chồng") or contains(.,"Con")]',
                    '//p[contains(.,"Gia đình")]//text()'
                ],
                regex_patterns=[
                    # Original patterns
                    r'(?:Thành\s*viên|Member)[:\s]*([^\n\r]+)',
                    r'(?:Quan\s*hệ|Relationship)[:\s]*([^\n\r]+)',
                    r'(?:Họ\s*tên|Name)[:\s]*([^\n\r]+)',
                    r'(?:Năm\s*sinh|Birth\s*year)[:\s]*([0-9]{4})',
                    r'(?:Con|Vợ|Chồng|Cha|Mẹ|Anh|Chị|Em)[:\s]*([^\n\r]+)',
                    # Enhanced patterns for different structures
                    r'<tr>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*</tr>',
                    r'([A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+)\s*-\s*(Vợ|Chồng|Con|Cha|Mẹ|Anh|Chị|Em)\s*-\s*([0-9]{4})',
                    r'(Vợ|Chồng|Con|Cha|Mẹ)[:\s-]*([A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+)(?:\s*\(([0-9]{4})\))?',
                    r'([A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+)(?:\s*:\s*)?(Vợ|Chồng|Con|Cha|Mẹ)',
                    r'(?:Thành\s*viên|Gia\s*đình)[:\s]*(.+?)(?:\n|$|</)',
                    r'"name":\s*"([^"]+)"[^}]*"relation":\s*"([^"]+)"[^}]*"birth_year":\s*"([^"]+)"',
                    r'>([^<]*(?:Vợ|Chồng|Con|Cha|Mẹ)[^<]*)<',
                    r'<(?:div|p|span)[^>]*>([^<]*(?:Vợ|Chồng|Con|Cha|Mẹ)[^<]*)</(?:div|p|span)>'
                ],
                context_keywords=[
                    'thành viên', 'hộ gia đình', 'member', 'family', 'quan hệ', 'relationship',
                    'gia đình', 'family members', 'vợ', 'chồng', 'con', 'cha', 'mẹ', 'anh', 'chị', 'em',
                    'family-members', 'members', 'household'
                ],
                validation_rules=[
                    'structured_data_check', 'relationship_validation'
                ],
                normalization_functions=[
                    'parse_member_structure', 'standardize_relationships'
                ],
                fallback_patterns=[
                    r'[A-Za-z\s]+[0-9]{4}',  # Name + birth year pattern
                    r'(?:Con|Vợ|Chồng|Cha|Mẹ)[^,\n<>]+',  # Relationship patterns
                    r'(?:Vợ|Chồng|Con|Cha|Mẹ):\s*[^,\n<>]+',  # Relationship with colon
                    r'[A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+\s*[-:]\s*(?:Vợ|Chồng|Con|Cha|Mẹ)'
                ]
            )
        }


class NormalizationMappingsConfig:
    """Configuration class for normalization mappings"""
    
    @staticmethod
    def get_normalization_maps() -> Dict[str, Dict]:
        """Get normalization mappings"""
        return {
            'banks': {
                'ACB': 'Ngân hàng TMCP Á Châu (ACB)',
                'VCB': 'Ngân hàng TMCP Ngoại thương Việt Nam (Vietcombank)',
                'TCB': 'Ngân hàng TMCP Kỹ thương Việt Nam (Techcombank)',
                'CTG': 'Ngân hàng TMCP Công thương Việt Nam (VietinBank)',
                'MBB': 'Ngân hàng TMCP Quân đội (MB Bank)',
                'VTB': 'Ngân hàng TMCP Việt Nam Thịnh vượng (VPBank)',
                'SHB': 'Ngân hàng TMCP Sài Gòn - Hà Nội (SHB)',
                'EIB': 'Ngân hàng TMCP Xuất Nhập khẩu Việt Nam (Eximbank)',
                'OCB': 'Ngân hàng TMCP Phương Đông (OCB)',
                'TPB': 'Ngân hàng TMCP Tiên Phong (TPBank)',
                'HDB': 'Ngân hàng TMCP Phát triển nhà TPHCM (HDBank)',
                'BID': 'Ngân hàng TMCP Đầu tư và Phát triển Việt Nam (BIDV)',
                'VIB': 'Ngân hàng TMCP Quốc tế Việt Nam (VIB)',
                'SEA': 'Ngân hàng TMCP Đông Nam Á (SeABank)'
            },
            'phone_prefixes': {
                '032': 'Viettel', '033': 'Viettel', '034': 'Viettel', '035': 'Viettel',
                '036': 'Viettel', '037': 'Viettel', '038': 'Viettel', '039': 'Viettel',
                '070': 'Mobifone', '076': 'Mobifone', '077': 'Mobifone', '078': 'Mobifone', '079': 'Mobifone',
                '081': 'Vinaphone', '082': 'Vinaphone', '083': 'Vinaphone', '084': 'Vinaphone', '085': 'Vinaphone',
                '088': 'Vinaphone', '091': 'Vinaphone', '094': 'Vinaphone'
            },
            'relationships': {
                'con': 'Con', 'vo': 'Vợ', 'chong': 'Chồng', 'cha': 'Cha', 'me': 'Mẹ',
                'anh': 'Anh', 'chi': 'Chị', 'em': 'Em', 'ong': 'Ông', 'ba': 'Bà',
                'chu': 'Chú', 'co': 'Cô', 'bac': 'Bác', 'di': 'Dì', 'duong': 'Dượng'
            },
            'currency_multipliers': {
                'triệu': 1000000,
                'million': 1000000,
                'nghìn': 1000,
                'thousand': 1000,
                'k': 1000,
                'tỷ': 1000000000,
                'billion': 1000000000
            }
        }
