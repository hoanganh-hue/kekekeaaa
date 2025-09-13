#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Fields Extraction Engine
Advanced extraction engine cho 5 enhanced fields từ VSS với robust pattern matching,
data normalization, quality scoring và cross-validation.

Author: MiniMax Agent
Date: 2025-09-13
Version: 2.0
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExtractionQuality(Enum):
    """Quality levels for extractions"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    FAILED = "failed"

@dataclass
class ExtractionResult:
    """Container for extraction results with quality metrics"""
    field_name: str
    extracted_value: Any
    confidence_score: float
    quality_level: ExtractionQuality
    extraction_method: str
    fallback_used: bool = False
    validation_errors: List[str] = field(default_factory=list)
    normalization_applied: List[str] = field(default_factory=list)

@dataclass
class FieldPattern:
    """Enhanced pattern definition for field extraction"""
    css_selectors: List[str]
    xpath_selectors: List[str]
    regex_patterns: List[str]
    context_keywords: List[str]
    validation_rules: List[str]
    normalization_functions: List[str]
    fallback_patterns: List[str]

class VSS_EnhancedExtractor:
    """
    Enhanced Fields Extraction Engine cho VSS
    Robust extraction cho 5 enhanced fields với advanced patterns và validation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.extraction_results = []
        self.quality_metrics = {}
        
        # Advanced extraction patterns cho 5 enhanced fields (optimized)
        self.field_patterns = self._initialize_enhanced_patterns()
        
        # Normalization maps
        self.normalization_maps = self._initialize_normalization_maps()
        
        # Quality scoring weights
        self.quality_weights = {
            'pattern_match_confidence': 0.3,
            'data_structure_score': 0.2,
            'validation_score': 0.25,
            'normalization_success': 0.15,
            'context_relevance': 0.1
        }

    def _initialize_enhanced_patterns(self) -> Dict[str, FieldPattern]:
        """Initialize enhanced extraction patterns cho 5 fields"""
        return self._get_optimized_patterns()
    
    def _get_optimized_patterns(self) -> Dict[str, FieldPattern]:
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
                context_keywords=['điện thoại', 'sđt', 'phone', 'mobile', 'tel', 'contact', 'hotline'],
                validation_rules=['vietnam_phone_format', 'length_check', 'digit_validation'],
                normalization_functions=['normalize_vietnam_phone', 'remove_formatting'],
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
                context_keywords=['thu nhập', 'lương', 'income', 'salary', 'wage', 'mức lương', 'tiền lương'],
                validation_rules=['positive_number', 'reasonable_income_range', 'currency_format'],
                normalization_functions=['normalize_currency', 'convert_to_number'],
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
                context_keywords=['ngân hàng', 'bank', 'nh', 'banking', 'tài khoản', 'account'],
                validation_rules=['known_bank_list', 'bank_code_format'],
                normalization_functions=['normalize_bank_name', 'standardize_bank_code'],
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
                context_keywords=['mã hộ', 'hộ gia đình', 'household', 'family', 'hgd', 'family code'],
                validation_rules=['alphanumeric_check', 'length_validation', 'prefix_check'],
                normalization_functions=['uppercase_code', 'remove_spaces'],
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
                validation_rules=['structured_data_check', 'relationship_validation'],
                normalization_functions=['parse_member_structure', 'standardize_relationships'],
                fallback_patterns=[
                    r'[A-Za-z\s]+[0-9]{4}',  # Name + birth year pattern
                    r'(?:Con|Vợ|Chồng|Cha|Mẹ)[^,\n<>]+',  # Relationship patterns
                    r'(?:Vợ|Chồng|Con|Cha|Mẹ):\s*[^,\n<>]+',  # Relationship with colon
                    r'[A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+\s*[-:]\s*(?:Vợ|Chồng|Con|Cha|Mẹ)'
                ]
            )
        }

    def _initialize_normalization_maps(self) -> Dict[str, Dict]:
        """Initialize normalization mappings"""
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
            }
        }

    def extract_enhanced_fields(self, html_content: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main extraction method cho tất cả enhanced fields
        
        Args:
            html_content: HTML response từ VSS
            input_data: Original input data cho cross-validation
            
        Returns:
            Dictionary chứa extracted data với quality metrics
        """
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Initialize results container
            extraction_results = {
                'extraction_timestamp': datetime.now().isoformat(),
                'extraction_engine': 'VSS_EnhancedExtractor_v2.0',
                'input_data_provided': input_data is not None,
                'html_analysis': self._analyze_html_structure(soup),
                'extracted_fields': {},
                'quality_metrics': {},
                'cross_validation': {},
                'extraction_summary': {}
            }
            
            # Extract từng field
            for field_name in self.field_patterns.keys():
                self.logger.info(f"Extracting field: {field_name}")
                
                field_result = self._extract_single_field(
                    soup, field_name, html_content, input_data
                )
                
                extraction_results['extracted_fields'][field_name] = field_result
                extraction_results['quality_metrics'][field_name] = self._calculate_quality_score(field_result)
            
            # Cross-validation với input data
            if input_data:
                extraction_results['cross_validation'] = self._perform_cross_validation(
                    extraction_results['extracted_fields'], input_data
                )
            
            # Generate extraction summary
            extraction_results['extraction_summary'] = self._generate_extraction_summary(
                extraction_results['extracted_fields']
            )
            
            return extraction_results
            
        except Exception as e:
            self.logger.error(f"Error in extract_enhanced_fields: {e}")
            return {
                'extraction_success': False,
                'extraction_error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }

    def _analyze_html_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze HTML structure để optimize extraction strategy"""
        try:
            return {
                'total_elements': len(soup.find_all()),
                'table_count': len(soup.find_all('table')),
                'div_count': len(soup.find_all('div')),
                'span_count': len(soup.find_all('span')),
                'form_count': len(soup.find_all('form')),
                'input_count': len(soup.find_all('input')),
                'has_json_script': bool(soup.find_all('script', string=re.compile(r'\{.*\}'))),
                'text_length': len(soup.get_text()),
                'structure_type': self._determine_structure_type(soup)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing HTML structure: {e}")
            return {'analysis_error': str(e)}

    def _determine_structure_type(self, soup: BeautifulSoup) -> str:
        """Determine HTML structure type để chọn strategy phù hợp"""
        table_count = len(soup.find_all('table'))
        form_count = len(soup.find_all('form'))
        div_count = len(soup.find_all('div'))
        
        if table_count > 3:
            return 'table_based'
        elif form_count > 0:
            return 'form_based'
        elif div_count > 10:
            return 'div_based'
        else:
            return 'mixed_structure'

    def _extract_single_field(self, soup: BeautifulSoup, field_name: str, 
                            html_content: str, input_data: Dict = None) -> ExtractionResult:
        """Extract một field với multiple strategies và fallback"""
        
        pattern = self.field_patterns[field_name]
        extraction_attempts = []
        
        try:
            # Strategy 1: CSS Selectors
            css_result = self._extract_by_css_selectors(soup, field_name, pattern.css_selectors)
            if css_result:
                extraction_attempts.append(('css_selector', css_result, 0.9))
            
            # Strategy 2: Regex patterns
            regex_result = self._extract_by_regex(html_content, field_name, pattern.regex_patterns)
            if regex_result:
                extraction_attempts.append(('regex_pattern', regex_result, 0.8))
            
            # Strategy 3: Context-based search
            context_result = self._extract_by_context(soup, field_name, pattern.context_keywords)
            if context_result:
                extraction_attempts.append(('context_search', context_result, 0.7))
            
            # Strategy 4: XPath selectors (simulated)
            xpath_result = self._extract_by_xpath_simulation(soup, field_name, pattern.xpath_selectors)
            if xpath_result:
                extraction_attempts.append(('xpath_simulation', xpath_result, 0.8))
            
            # Strategy 5: Fallback patterns
            if not extraction_attempts:
                fallback_result = self._extract_by_fallback(html_content, field_name, pattern.fallback_patterns)
                if fallback_result:
                    extraction_attempts.append(('fallback_pattern', fallback_result, 0.5))
            
            # Select best result with enhanced logic for thong_tin_thanh_vien
            if extraction_attempts:
                # Special handling for thong_tin_thanh_vien - prioritize results with actual data
                if field_name == 'thong_tin_thanh_vien':
                    # Test normalization for each attempt and pick the best one with data
                    valid_attempts = []
                    
                    for method, value, base_conf in extraction_attempts:
                        test_normalized = self._normalize_field_value(field_name, value)
                        if test_normalized and len(test_normalized) > 0:
                            # Has actual normalized data
                            data_quality_bonus = 0.2  # Bonus for having actual data
                            adjusted_confidence = base_conf + data_quality_bonus
                            valid_attempts.append((method, value, adjusted_confidence, test_normalized))
                    
                    if valid_attempts:
                        # Pick the attempt with actual data and highest confidence
                        best_method, best_value, base_confidence, pre_normalized = max(valid_attempts, key=lambda x: x[2])
                        normalized_value = pre_normalized  # Use pre-computed normalization
                    else:
                        # Fallback to original logic if no valid attempts
                        best_method, best_value, base_confidence = max(extraction_attempts, key=lambda x: x[2])
                        normalized_value = self._normalize_field_value(field_name, best_value)
                else:
                    # Standard logic for other fields
                    best_method, best_value, base_confidence = max(extraction_attempts, key=lambda x: x[2])
                    normalized_value = self._normalize_field_value(field_name, best_value)
                
                # Validate result
                validation_errors = self._validate_field_value(field_name, normalized_value, input_data)
                
                # Calculate final confidence
                final_confidence = self._calculate_confidence_score(
                    base_confidence, validation_errors, best_method
                )
                
                return ExtractionResult(
                    field_name=field_name,
                    extracted_value=normalized_value,
                    confidence_score=final_confidence,
                    quality_level=self._determine_quality_level(final_confidence),
                    extraction_method=best_method,
                    fallback_used=('fallback' in best_method),
                    validation_errors=validation_errors,
                    normalization_applied=self._get_normalization_applied(field_name, best_value, normalized_value)
                )
            else:
                # No extraction successful
                return ExtractionResult(
                    field_name=field_name,
                    extracted_value=None,
                    confidence_score=0.0,
                    quality_level=ExtractionQuality.FAILED,
                    extraction_method='none',
                    validation_errors=['No extraction pattern matched']
                )
                
        except Exception as e:
            self.logger.error(f"Error extracting field {field_name}: {e}")
            return ExtractionResult(
                field_name=field_name,
                extracted_value=None,
                confidence_score=0.0,
                quality_level=ExtractionQuality.FAILED,
                extraction_method='error',
                validation_errors=[f"Extraction error: {str(e)}"]
            )

    def _extract_by_css_selectors(self, soup: BeautifulSoup, field_name: str, selectors: List[str]) -> Optional[str]:
        """Extract using CSS selectors with enhanced logic for thong_tin_thanh_vien"""
        for selector in selectors:
            try:
                elements = soup.select(selector)
                
                # Special handling for thong_tin_thanh_vien - aggregate multiple elements
                if field_name == 'thong_tin_thanh_vien' and elements:
                    if len(elements) > 1:
                        # Multiple elements found - combine them
                        combined_text = []
                        for element in elements:
                            text = element.get_text().strip()
                            if text and len(text) > 0:
                                # Skip header rows or irrelevant content
                                if not any(header in text.lower() for header in ['họ tên', 'quan hệ', 'năm sinh', 'name', 'relationship']):
                                    combined_text.append(text)
                        
                        if combined_text:
                            return ' | '.join(combined_text)  # Use separator to distinguish between members
                    
                    # Single element or fallback
                    for element in elements:
                        text = element.get_text().strip()
                        if text and len(text) > 0:
                            return text
                
                # Standard handling for other fields
                else:
                    for element in elements:
                        text = element.get_text().strip()
                        if text and len(text) > 0:
                            return text
                            
            except Exception as e:
                self.logger.debug(f"CSS selector {selector} failed: {e}")
                continue
        return None

    def _extract_by_regex(self, html_content: str, field_name: str, patterns: List[str]) -> Optional[str]:
        """Extract using regex patterns"""
        for pattern in patterns:
            try:
                matches = re.findall(pattern, html_content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    # Return first non-empty match
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        if match and len(match.strip()) > 0:
                            return match.strip()
            except Exception as e:
                self.logger.debug(f"Regex pattern {pattern} failed: {e}")
                continue
        return None

    def _extract_by_context(self, soup: BeautifulSoup, field_name: str, keywords: List[str]) -> Optional[str]:
        """Extract by searching context keywords"""
        for keyword in keywords:
            try:
                # Find elements containing keyword
                elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
                
                for element in elements:
                    parent = element.parent
                    if parent:
                        # Look for value in siblings or children
                        value = self._find_value_near_keyword(parent, keyword)
                        if value:
                            return value
            except Exception as e:
                self.logger.debug(f"Context search for {keyword} failed: {e}")
                continue
        return None

    def _extract_by_xpath_simulation(self, soup: BeautifulSoup, field_name: str, xpath_patterns: List[str]) -> Optional[str]:
        """Simulate XPath functionality with BeautifulSoup"""
        for xpath in xpath_patterns:
            try:
                # Convert simple XPath to BeautifulSoup equivalent
                if '//td[contains(text(),' in xpath:
                    # Extract search text
                    search_match = re.search(r'contains\(text\(\),"([^"]+)"\)', xpath)
                    if search_match:
                        search_text = search_match.group(1)
                        # Find td containing text
                        tds = soup.find_all('td', string=re.compile(search_text, re.IGNORECASE))
                        for td in tds:
                            # Look for following sibling
                            next_td = td.find_next_sibling('td')
                            if next_td:
                                text = next_td.get_text().strip()
                                if text:
                                    return text
            except Exception as e:
                self.logger.debug(f"XPath simulation {xpath} failed: {e}")
                continue
        return None

    def _extract_by_fallback(self, html_content: str, field_name: str, fallback_patterns: List[str]) -> Optional[str]:
        """Extract using fallback patterns when main methods fail"""
        for pattern in fallback_patterns:
            try:
                matches = re.findall(pattern, html_content)
                if matches:
                    # Return first reasonable match
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        if match and len(match.strip()) > 2:  # At least 3 characters
                            return match.strip()
            except Exception as e:
                self.logger.debug(f"Fallback pattern {pattern} failed: {e}")
                continue
        return None

    def _find_value_near_keyword(self, element, keyword: str) -> Optional[str]:
        """Find value near keyword element"""
        try:
            # Check siblings
            for sibling in element.find_next_siblings():
                text = sibling.get_text().strip()
                if text and len(text) > 0 and text.lower() != keyword.lower():
                    return text
            
            # Check parent's other children
            if element.parent:
                for child in element.parent.find_all():
                    if child != element:
                        text = child.get_text().strip()
                        if text and len(text) > 0 and keyword.lower() not in text.lower():
                            return text
            
            return None
        except Exception:
            return None

    def _normalize_field_value(self, field_name: str, value: str) -> Any:
        """Normalize extracted value theo field type"""
        if not value:
            return None
            
        try:
            if field_name == 'so_dien_thoai':
                return self._normalize_phone_number(value)
            elif field_name == 'thu_nhap':
                return self._normalize_income(value)
            elif field_name == 'ngan_hang':
                return self._normalize_bank_name(value)
            elif field_name == 'ma_ho_gia_dinh':
                return self._normalize_household_code(value)
            elif field_name == 'thong_tin_thanh_vien':
                return self._normalize_member_info(value)
            else:
                return value.strip()
        except Exception as e:
            self.logger.error(f"Error normalizing {field_name}: {e}")
            return value

    def _normalize_phone_number(self, phone: str) -> str:
        """Normalize Vietnam phone number"""
        if not phone:
            return ""
        
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        
        # Handle +84 prefix
        if digits.startswith('84') and len(digits) >= 10:
            digits = '0' + digits[2:]
        
        # Validate Vietnam phone format
        if re.match(r'^0[1-9][0-9]{8,9}$', digits):
            return digits
        
        return phone  # Return original if can't normalize

    def _normalize_income(self, income: str) -> Dict[str, Any]:
        """Normalize income value"""
        if not income:
            return None
        
        try:
            # Extract numeric value
            numeric_str = re.sub(r'[^\d,.]', '', income)
            numeric_str = numeric_str.replace(',', '').replace('.', '')
            
            if numeric_str:
                amount = int(numeric_str)
                
                # Detect currency unit
                currency = 'VND'
                if any(unit in income.lower() for unit in ['triệu', 'million']):
                    amount *= 1000000
                elif any(unit in income.lower() for unit in ['nghìn', 'thousand', 'k']):
                    amount *= 1000
                
                return {
                    'amount': amount,
                    'currency': currency,
                    'formatted': f"{amount:,} {currency}",
                    'original': income
                }
            
            return {'original': income, 'parsed': False}
            
        except Exception as e:
            self.logger.error(f"Error normalizing income: {e}")
            return {'original': income, 'error': str(e)}

    def _normalize_bank_name(self, bank: str) -> Dict[str, str]:
        """Normalize bank name"""
        if not bank:
            return None
        
        bank_upper = bank.upper().strip()
        
        # Check trong mapping
        for code, full_name in self.normalization_maps['banks'].items():
            if code in bank_upper or code.lower() in bank.lower():
                return {
                    'code': code,
                    'full_name': full_name,
                    'original': bank
                }
        
        # Check partial matches
        for code, full_name in self.normalization_maps['banks'].items():
            if any(word in bank_upper for word in code.split()):
                return {
                    'code': code,
                    'full_name': full_name,
                    'original': bank,
                    'match_type': 'partial'
                }
        
        return {
            'original': bank,
            'normalized': bank.title(),
            'match_type': 'unknown'
        }

    def _normalize_household_code(self, code: str) -> str:
        """Normalize household code"""
        if not code:
            return ""
        
        # Remove spaces and convert to uppercase
        normalized = re.sub(r'\s+', '', code.upper())
        
        # Validate format
        if re.match(r'^[A-Z0-9]{8,15}$', normalized):
            return normalized
        
        return code  # Return original if doesn't match expected format

    def _normalize_member_info(self, member_text: str) -> List[Dict[str, str]]:
        """Normalize member information với enhanced logic cho multiple formats"""
        if not member_text:
            return []
        
        try:
            members = []
            
            # Handle table row format (multiple <tr> data)
            if '<tr>' in member_text.lower():
                # Extract from table rows
                tr_pattern = r'<tr>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*</tr>'
                tr_matches = re.findall(tr_pattern, member_text, re.IGNORECASE)
                
                for match in tr_matches:
                    name, relationship, birth_year = [part.strip() for part in match]
                    if name and relationship:
                        member = {
                            'name': name,
                            'relationship': self._normalize_relationship(relationship),
                            'birth_year': birth_year if birth_year.isdigit() else None
                        }
                        members.append(member)
                
                if members:
                    return members
            
            # Handle JSON format
            if '"name"' in member_text and '"relation' in member_text:
                json_pattern = r'"name":\s*"([^"]+)"[^}]*"relation":\s*"([^"]+)"[^}]*"birth_year":\s*"([^"]+)"'
                json_matches = re.findall(json_pattern, member_text)
                
                for match in json_matches:
                    name, relationship, birth_year = match
                    member = {
                        'name': name.strip(),
                        'relationship': self._normalize_relationship(relationship),
                        'birth_year': birth_year.strip() if birth_year.isdigit() else None
                    }
                    members.append(member)
                
                if members:
                    return members
            
            # Handle structured text patterns
            # Pattern 1: "Name - Relationship - Year"
            pattern1 = r'([A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+)\s*-\s*(Vợ|Chồng|Con|Cha|Mẹ|Anh|Chị|Em)\s*-\s*([0-9]{4})'
            matches1 = re.findall(pattern1, member_text, re.IGNORECASE)
            
            for match in matches1:
                name, relationship, birth_year = [part.strip() for part in match]
                member = {
                    'name': name,
                    'relationship': self._normalize_relationship(relationship),
                    'birth_year': birth_year
                }
                members.append(member)
            
            # Pattern 2: "Relationship: Name (Year)" or "Relationship - Name (Year)"
            pattern2 = r'(Vợ|Chồng|Con|Cha|Mẹ|Anh|Chị|Em)[:\s-]*([A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+?)(?:\s*\(([0-9]{4})\))?'
            matches2 = re.findall(pattern2, member_text, re.IGNORECASE)
            
            for match in matches2:
                relationship, name, birth_year = match
                name = name.strip().rstrip(',').rstrip('(').strip()
                member = {
                    'name': name,
                    'relationship': self._normalize_relationship(relationship),
                    'birth_year': birth_year if birth_year else None
                }
                members.append(member)
            
            # Pattern 3: "Name: Relationship" 
            pattern3 = r'([A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+)(?:\s*:\s*)?(Vợ|Chồng|Con|Cha|Mẹ|Anh|Chị|Em)'
            matches3 = re.findall(pattern3, member_text, re.IGNORECASE)
            
            for match in matches3:
                name, relationship = [part.strip() for part in match]
                # Look for birth year nearby
                birth_year = None
                year_pattern = r'\b(19|20)\d{2}\b'
                year_match = re.search(year_pattern, member_text[member_text.find(name):member_text.find(name)+100])
                if year_match:
                    birth_year = year_match.group(0)
                
                member = {
                    'name': name,
                    'relationship': self._normalize_relationship(relationship),
                    'birth_year': birth_year
                }
                members.append(member)
            
            # If no structured patterns worked, try splitting by common delimiters
            if not members:
                # Split by commas, semicolons, pipes, or newlines
                lines = re.split(r'[,;|\n\r]', member_text)
                
                for line in lines:
                    line = line.strip()
                    if not line or len(line) < 5:
                        continue
                    
                    # Look for any relationship keywords
                    if any(rel in line.lower() for rel in ['vợ', 'chồng', 'con', 'cha', 'mẹ', 'anh', 'chị', 'em']):
                        member = {}
                        
                        # Try to extract name and relationship from the line
                        # Pattern: "Anything with relationship keyword"
                        rel_pattern = r'([A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+).*?(Vợ|Chồng|Con|Cha|Mẹ|Anh|Chị|Em)'
                        rel_match = re.search(rel_pattern, line, re.IGNORECASE)
                        
                        if rel_match:
                            name_part = rel_match.group(1).strip()
                            relationship_part = rel_match.group(2).strip()
                            
                            # Clean up name part
                            name_part = re.sub(r'[:-]', '', name_part).strip()
                            
                            member['name'] = name_part
                            member['relationship'] = self._normalize_relationship(relationship_part)
                            
                            # Look for birth year in the line
                            year_match = re.search(r'\b(19|20)\d{2}\b', line)
                            if year_match:
                                member['birth_year'] = year_match.group(0)
                            
                            if member.get('name'):
                                members.append(member)
            
            # Remove duplicates based on name and relationship
            unique_members = []
            seen = set()
            
            for member in members:
                key = f"{member.get('name', '').lower().strip()}_{member.get('relationship', '').lower().strip()}"
                if key not in seen and member.get('name') and member.get('relationship'):
                    seen.add(key)
                    unique_members.append(member)
            
            return unique_members
            
        except Exception as e:
            self.logger.error(f"Error normalizing member info: {e}")
            return [{'original': member_text, 'error': str(e)}]

    def _normalize_relationship(self, relationship: str) -> str:
        """Normalize family relationship"""
        if not relationship:
            return ""
        
        rel_lower = relationship.lower().strip()
        
        # Check in mapping
        for key, normalized in self.normalization_maps['relationships'].items():
            if key in rel_lower:
                return normalized
        
        return relationship.title()

    def _validate_field_value(self, field_name: str, value: Any, input_data: Dict = None) -> List[str]:
        """Validate extracted field value"""
        errors = []
        
        try:
            if field_name == 'so_dien_thoai':
                errors.extend(self._validate_phone_number(value))
            elif field_name == 'thu_nhap':
                errors.extend(self._validate_income(value))
            elif field_name == 'ngan_hang':
                errors.extend(self._validate_bank(value))
            elif field_name == 'ma_ho_gia_dinh':
                errors.extend(self._validate_household_code(value))
            elif field_name == 'thong_tin_thanh_vien':
                errors.extend(self._validate_member_info(value))
            
            # Cross-validation với input data
            if input_data:
                errors.extend(self._cross_validate_field(field_name, value, input_data))
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return errors

    def _validate_phone_number(self, phone: str) -> List[str]:
        """Validate phone number"""
        errors = []
        
        if not phone:
            errors.append("Phone number is empty")
            return errors
        
        # Check Vietnam phone format
        if not re.match(r'^0[1-9][0-9]{8,9}$', phone):
            errors.append("Invalid Vietnam phone number format")
        
        # Check known prefixes
        if len(phone) >= 3:
            prefix = phone[:3]
            if prefix not in self.normalization_maps['phone_prefixes']:
                errors.append(f"Unknown phone prefix: {prefix}")
        
        return errors

    def _validate_income(self, income: Dict) -> List[str]:
        """Validate income value"""
        errors = []
        
        if not income:
            errors.append("Income data is empty")
            return errors
        
        if isinstance(income, dict) and 'amount' in income:
            amount = income['amount']
            
            # Reasonable range check (100k - 100M VND)
            if amount < 100000:
                errors.append("Income seems too low (< 100,000 VND)")
            elif amount > 100000000:
                errors.append("Income seems too high (> 100,000,000 VND)")
        
        return errors

    def _validate_bank(self, bank: Dict) -> List[str]:
        """Validate bank information"""
        errors = []
        
        if not bank:
            errors.append("Bank data is empty")
            return errors
        
        if isinstance(bank, dict):
            if 'match_type' in bank and bank['match_type'] == 'unknown':
                errors.append("Bank not found in known banks list")
        
        return errors

    def _validate_household_code(self, code: str) -> List[str]:
        """Validate household code"""
        errors = []
        
        if not code:
            errors.append("Household code is empty")
            return errors
        
        if not re.match(r'^[A-Z0-9]{8,15}$', code):
            errors.append("Invalid household code format")
        
        return errors

    def _validate_member_info(self, members: List[Dict]) -> List[str]:
        """Validate member information"""
        errors = []
        
        if not members:
            errors.append("No member information found")
            return errors
        
        for i, member in enumerate(members):
            if not member.get('name'):
                errors.append(f"Member {i+1}: Missing name")
            if not member.get('relationship'):
                errors.append(f"Member {i+1}: Missing relationship")
        
        return errors

    def _cross_validate_field(self, field_name: str, extracted_value: Any, input_data: Dict) -> List[str]:
        """Cross-validate extracted value với input data"""
        errors = []
        
        try:
            # Implementation cho specific cross-validation rules
            if field_name == 'so_dien_thoai' and 'phone' in input_data:
                input_phone = input_data['phone']
                if input_phone and extracted_value != input_phone:
                    errors.append(f"Phone mismatch: extracted='{extracted_value}' vs input='{input_phone}'")
            
            # Add more cross-validation rules as needed
            
        except Exception as e:
            errors.append(f"Cross-validation error: {str(e)}")
        
        return errors

    def _calculate_confidence_score(self, base_confidence: float, validation_errors: List[str], method: str) -> float:
        """Calculate final confidence score"""
        try:
            # Start with base confidence
            confidence = base_confidence
            
            # Adjust for validation errors
            error_penalty = len(validation_errors) * 0.1
            confidence -= error_penalty
            
            # Adjust for extraction method
            method_weights = {
                'css_selector': 1.0,
                'regex_pattern': 0.9,
                'xpath_simulation': 0.9,
                'context_search': 0.8,
                'fallback_pattern': 0.5
            }
            
            method_weight = method_weights.get(method, 0.5)
            confidence *= method_weight
            
            # Ensure confidence stays in [0, 1] range
            return max(0.0, min(1.0, confidence))
            
        except Exception:
            return 0.5  # Default confidence

    def _determine_quality_level(self, confidence: float) -> ExtractionQuality:
        """Determine quality level based on confidence score"""
        if confidence >= 0.9:
            return ExtractionQuality.EXCELLENT
        elif confidence >= 0.7:
            return ExtractionQuality.GOOD
        elif confidence >= 0.5:
            return ExtractionQuality.MODERATE
        elif confidence > 0.0:
            return ExtractionQuality.POOR
        else:
            return ExtractionQuality.FAILED

    def _get_normalization_applied(self, field_name: str, original: str, normalized: Any) -> List[str]:
        """Get list of normalization steps applied"""
        applied = []
        
        if not original:
            return applied
        
        if original != normalized:
            applied.append('value_changed')
            
            if field_name == 'so_dien_thoai':
                if '+84' in original or '84' in original:
                    applied.append('international_prefix_converted')
                if any(char in original for char in ['-', '(', ')', ' ']):
                    applied.append('formatting_removed')
            
            elif field_name == 'thu_nhap':
                applied.append('currency_parsed')
                if 'triệu' in original.lower():
                    applied.append('million_multiplier_applied')
            
            elif field_name == 'ngan_hang':
                applied.append('bank_name_standardized')
            
            elif field_name == 'ma_ho_gia_dinh':
                applied.append('uppercase_conversion')
                if ' ' in original:
                    applied.append('spaces_removed')
        
        return applied

    def _calculate_quality_score(self, result: ExtractionResult) -> Dict[str, Any]:
        """Calculate detailed quality metrics for extraction result"""
        try:
            return {
                'confidence_score': result.confidence_score,
                'quality_level': result.quality_level.value,
                'extraction_method': result.extraction_method,
                'fallback_used': result.fallback_used,
                'validation_error_count': len(result.validation_errors),
                'normalization_steps': len(result.normalization_applied),
                'data_completeness': 1.0 if result.extracted_value else 0.0,
                'overall_score': self._calculate_overall_score(result)
            }
        except Exception as e:
            return {'error': str(e)}

    def _calculate_overall_score(self, result: ExtractionResult) -> float:
        """Calculate overall quality score"""
        try:
            # Weighted combination of factors
            factors = {
                'confidence': result.confidence_score * 0.4,
                'completeness': (1.0 if result.extracted_value else 0.0) * 0.3,
                'validation': max(0, 1.0 - len(result.validation_errors) * 0.2) * 0.2,
                'method_reliability': (0.8 if not result.fallback_used else 0.4) * 0.1
            }
            
            return sum(factors.values())
        except Exception:
            return 0.0

    def _perform_cross_validation(self, extracted_fields: Dict, input_data: Dict) -> Dict[str, Any]:
        """Perform comprehensive cross-validation"""
        try:
            validation_results = {
                'input_data_keys': list(input_data.keys()),
                'extracted_fields_keys': list(extracted_fields.keys()),
                'field_validations': {},
                'overall_consistency': 0.0,
                'inconsistencies': []
            }
            
            # Validate each field
            total_score = 0
            valid_fields = 0
            
            for field_name, result in extracted_fields.items():
                if result.extracted_value:
                    field_validation = self._validate_field_consistency(
                        field_name, result.extracted_value, input_data
                    )
                    validation_results['field_validations'][field_name] = field_validation
                    
                    if field_validation['is_consistent']:
                        total_score += 1
                    valid_fields += 1
            
            # Calculate overall consistency
            if valid_fields > 0:
                validation_results['overall_consistency'] = total_score / valid_fields
            
            return validation_results
            
        except Exception as e:
            return {'error': str(e)}

    def _validate_field_consistency(self, field_name: str, extracted_value: Any, input_data: Dict) -> Dict[str, Any]:
        """Validate consistency of một field với input data"""
        try:
            # Map field names to potential input keys
            field_mappings = {
                'so_dien_thoai': ['phone', 'dien_thoai', 'sdt'],
                'thu_nhap': ['income', 'salary', 'luong', 'thu_nhap'],
                'ngan_hang': ['bank', 'ngan_hang'],
                'ma_ho_gia_dinh': ['household_code', 'ma_ho', 'hgd'],
                'thong_tin_thanh_vien': ['members', 'thanh_vien', 'family']
            }
            
            possible_keys = field_mappings.get(field_name, [])
            
            for key in possible_keys:
                if key in input_data:
                    input_value = input_data[key]
                    consistency = self._compare_values(field_name, extracted_value, input_value)
                    
                    return {
                        'is_consistent': consistency['match'],
                        'input_key': key,
                        'input_value': input_value,
                        'extracted_value': extracted_value,
                        'similarity_score': consistency['similarity'],
                        'comparison_notes': consistency['notes']
                    }
            
            return {
                'is_consistent': True,  # No input to compare with
                'input_key': None,
                'note': 'No corresponding input data found'
            }
            
        except Exception as e:
            return {'error': str(e)}

    def _compare_values(self, field_name: str, extracted: Any, input_val: Any) -> Dict[str, Any]:
        """Compare extracted value với input value"""
        try:
            if field_name == 'so_dien_thoai':
                # Normalize cả hai số
                norm_extracted = self._normalize_phone_number(str(extracted))
                norm_input = self._normalize_phone_number(str(input_val))
                
                match = norm_extracted == norm_input
                similarity = 1.0 if match else 0.0
                
                return {
                    'match': match,
                    'similarity': similarity,
                    'notes': f"Normalized: {norm_extracted} vs {norm_input}"
                }
            
            elif field_name == 'thu_nhap':
                # So sánh numeric values
                if isinstance(extracted, dict) and 'amount' in extracted:
                    extracted_amount = extracted['amount']
                else:
                    extracted_amount = extracted
                
                try:
                    input_amount = float(str(input_val).replace(',', ''))
                    extracted_amount = float(str(extracted_amount).replace(',', ''))
                    
                    diff_percent = abs(extracted_amount - input_amount) / max(input_amount, 1) * 100
                    match = diff_percent < 10  # Allow 10% difference
                    similarity = max(0, 1 - diff_percent / 100)
                    
                    return {
                        'match': match,
                        'similarity': similarity,
                        'notes': f"Difference: {diff_percent:.1f}%"
                    }
                except ValueError:
                    return {'match': False, 'similarity': 0.0, 'notes': 'Cannot compare as numbers'}
            
            else:
                # Generic string comparison
                str_extracted = str(extracted).lower().strip()
                str_input = str(input_val).lower().strip()
                
                match = str_extracted == str_input
                
                # Calculate similarity (simple)
                if match:
                    similarity = 1.0
                elif str_extracted in str_input or str_input in str_extracted:
                    similarity = 0.7
                else:
                    similarity = 0.0
                
                return {
                    'match': match,
                    'similarity': similarity,
                    'notes': f"String comparison: '{str_extracted}' vs '{str_input}'"
                }
            
        except Exception as e:
            return {'match': False, 'similarity': 0.0, 'notes': f"Comparison error: {str(e)}"}

    def _generate_extraction_summary(self, extracted_fields: Dict) -> Dict[str, Any]:
        """Generate summary of extraction results"""
        try:
            total_fields = len(extracted_fields)
            successful_extractions = 0
            failed_extractions = 0
            moderate_quality = 0
            high_quality = 0
            
            for field_name, result in extracted_fields.items():
                if result.extracted_value:
                    successful_extractions += 1
                    
                    if result.quality_level in [ExtractionQuality.EXCELLENT, ExtractionQuality.GOOD]:
                        high_quality += 1
                    elif result.quality_level == ExtractionQuality.MODERATE:
                        moderate_quality += 1
                else:
                    failed_extractions += 1
            
            success_rate = successful_extractions / total_fields if total_fields > 0 else 0
            quality_score = (high_quality * 1.0 + moderate_quality * 0.5) / total_fields if total_fields > 0 else 0
            
            return {
                'total_fields': total_fields,
                'successful_extractions': successful_extractions,
                'failed_extractions': failed_extractions,
                'success_rate': success_rate,
                'high_quality_count': high_quality,
                'moderate_quality_count': moderate_quality,
                'overall_quality_score': quality_score,
                'status': 'excellent' if quality_score > 0.8 else 'good' if quality_score > 0.6 else 'moderate' if quality_score > 0.3 else 'poor'
            }
            
        except Exception as e:
            return {'error': str(e)}

    def test_with_sample_html(self, sample_html_files: List[str]) -> Dict[str, Any]:
        """Test extraction engine với sample HTML responses"""
        test_results = {
            'test_timestamp': datetime.now().isoformat(),
            'total_samples': len(sample_html_files),
            'test_results': {},
            'summary_statistics': {}
        }
        
        try:
            for i, html_file in enumerate(sample_html_files):
                self.logger.info(f"Testing with sample {i+1}: {html_file}")
                
                try:
                    # Read HTML file
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Extract fields
                    extraction_result = self.extract_enhanced_fields(html_content)
                    
                    test_results['test_results'][f'sample_{i+1}'] = {
                        'file': html_file,
                        'extraction_result': extraction_result,
                        'test_status': 'success'
                    }
                    
                except Exception as e:
                    test_results['test_results'][f'sample_{i+1}'] = {
                        'file': html_file,
                        'error': str(e),
                        'test_status': 'failed'
                    }
            
            # Generate summary statistics
            test_results['summary_statistics'] = self._calculate_test_statistics(test_results['test_results'])
            
            return test_results
            
        except Exception as e:
            test_results['error'] = str(e)
            return test_results

    def _calculate_test_statistics(self, test_results: Dict) -> Dict[str, Any]:
        """Calculate statistics from test results"""
        try:
            total_tests = len(test_results)
            successful_tests = sum(1 for result in test_results.values() if result.get('test_status') == 'success')
            
            # Field-level statistics
            field_stats = {}
            for field_name in self.field_patterns.keys():
                field_stats[field_name] = {
                    'successful_extractions': 0,
                    'total_attempts': 0,
                    'average_confidence': 0.0,
                    'quality_distribution': {level.value: 0 for level in ExtractionQuality}
                }
            
            total_confidence = 0
            confidence_count = 0
            
            for test_result in test_results.values():
                if test_result.get('test_status') == 'success':
                    extraction_result = test_result.get('extraction_result', {})
                    extracted_fields = extraction_result.get('extracted_fields', {})
                    
                    for field_name, result in extracted_fields.items():
                        if field_name in field_stats:
                            field_stats[field_name]['total_attempts'] += 1
                            
                            if result.extracted_value:
                                field_stats[field_name]['successful_extractions'] += 1
                                total_confidence += result.confidence_score
                                confidence_count += 1
                            
                            field_stats[field_name]['quality_distribution'][result.quality_level.value] += 1
            
            # Calculate averages
            for field_name in field_stats:
                stats = field_stats[field_name]
                if stats['total_attempts'] > 0:
                    stats['success_rate'] = stats['successful_extractions'] / stats['total_attempts']
                else:
                    stats['success_rate'] = 0.0
            
            overall_confidence = total_confidence / confidence_count if confidence_count > 0 else 0.0
            
            return {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'test_success_rate': successful_tests / total_tests if total_tests > 0 else 0.0,
                'overall_average_confidence': overall_confidence,
                'field_statistics': field_stats
            }
            
        except Exception as e:
            return {'error': str(e)}

# Utility functions for testing
def create_sample_html_responses() -> List[str]:
    """Create sample HTML responses for testing"""
    samples = []
    
    # Sample 1: Table-based structure
    sample1 = """
    <html>
    <body>
        <table>
            <tr><td>Họ tên</td><td>Nguyễn Văn A</td></tr>
            <tr><td>Điện thoại</td><td>0123456789</td></tr>
            <tr><td>Thu nhập</td><td>15,000,000 VND</td></tr>
            <tr><td>Ngân hàng</td><td>VCB</td></tr>
            <tr><td>Mã hộ gia đình</td><td>HGD123456789</td></tr>
        </table>
        <div>
            <h3>Thành viên hộ gia đình</h3>
            <p>Nguyễn Thị B - Vợ - 1985</p>
            <p>Nguyễn Văn C - Con - 2010</p>
        </div>
    </body>
    </html>
    """
    
    # Sample 2: Div-based structure  
    sample2 = """
    <html>
    <body>
        <div class="profile">
            <div class="field-phone">Phone: +84987654321</div>
            <div class="field-salary">Income: 20 triệu VND</div>
            <div class="field-bank">Bank: ACB</div>
            <div class="field-household">Household Code: HGD987654321</div>
        </div>
        <div class="family-members">
            <div class="member">Nguyễn Thị D: Mẹ</div>
            <div class="member">Nguyễn Văn E: Anh</div>
        </div>
    </body>
    </html>
    """
    
    # Sample 3: Mixed structure với JSON
    sample3 = """
    <html>
    <body>
        <form>
            <input name="phone" value="0909123456" />
            <input name="salary" value="18000000" />
            <select name="bank">
                <option value="TCB" selected>Techcombank</option>
            </select>
        </form>
        <script>
            var data = {
                "household_code": "HGD456789123",
                "members": [
                    {"name": "Nguyễn Văn F", "relationship": "Chồng"},
                    {"name": "Nguyễn Thị G", "relationship": "Vợ"}
                ]
            };
        </script>
    </body>
    </html>
    """
    
    return [sample1, sample2, sample3]

def run_enhanced_extraction_demo():
    """Demo function để test enhanced extractor"""
    print("=== VSS Enhanced Fields Extraction Engine Demo ===\n")
    
    # Initialize extractor
    extractor = VSS_EnhancedExtractor()
    
    # Create sample HTML responses
    samples = create_sample_html_responses()
    
    # Test với từng sample
    for i, html_content in enumerate(samples, 1):
        print(f"--- Testing Sample {i} ---")
        
        # Mock input data for cross-validation
        input_data = {
            'phone': '0123456789' if i == 1 else '0987654321' if i == 2 else '0909123456',
            'expected_income': 15000000 if i == 1 else 20000000 if i == 2 else 18000000
        }
        
        # Extract fields
        result = extractor.extract_enhanced_fields(html_content, input_data)
        
        # Print results
        print("Extraction Results:")
        print(f"  Success: {result.get('extraction_summary', {}).get('status', 'unknown')}")
        print(f"  Success Rate: {result.get('extraction_summary', {}).get('success_rate', 0):.2%}")
        
        for field_name, extraction_result in result.get('extracted_fields', {}).items():
            print(f"  {field_name}:")
            print(f"    Value: {extraction_result.extracted_value}")
            print(f"    Confidence: {extraction_result.confidence_score:.2f}")
            print(f"    Quality: {extraction_result.quality_level.value}")
            print(f"    Method: {extraction_result.extraction_method}")
        
        print()
    
    print("=== Demo completed ===")

if __name__ == "__main__":
    run_enhanced_extraction_demo()
