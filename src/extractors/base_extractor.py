#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Extractor - Base Extractor
Base class cho extraction engine với core functionality.

Author: MiniMax Agent
Date: 2025-09-13
Version: 2.1
"""

import re
import logging
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime

from ..config.constants import (
    ExtractionMethod, StructureType, METHOD_WEIGHTS, 
    STRUCTURE_THRESHOLDS, PROCESSING_LIMITS
)
from ..config.data_models import HTMLAnalysis, ExtractionResult
from ..config.patterns import FieldPatternsConfig, NormalizationMappingsConfig


class BaseExtractor:
    """Base extractor với core extraction functionality"""
    
    def __init__(self):
        """Initialize base extractor"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.field_patterns = FieldPatternsConfig.get_optimized_patterns()
        self.normalization_maps = NormalizationMappingsConfig.get_normalization_maps()
        
    def analyze_html_structure(self, soup: BeautifulSoup) -> HTMLAnalysis:
        """Analyze HTML structure để optimize extraction strategy"""
        try:
            table_count = len(soup.find_all('table'))
            form_count = len(soup.find_all('form'))
            div_count = len(soup.find_all('div'))
            
            structure_type = self._determine_structure_type(table_count, form_count, div_count)
            
            return HTMLAnalysis(
                total_elements=len(soup.find_all()),
                table_count=table_count,
                div_count=div_count,
                span_count=len(soup.find_all('span')),
                form_count=form_count,
                input_count=len(soup.find_all('input')),
                has_json_script=bool(soup.find_all('script', string=re.compile(r'\{.*\}'))),
                text_length=len(soup.get_text()),
                structure_type=structure_type
            )
        except Exception as e:
            self.logger.error(f"Error analyzing HTML structure: {e}")
            return HTMLAnalysis(
                total_elements=0, table_count=0, div_count=0, span_count=0,
                form_count=0, input_count=0, has_json_script=False,
                text_length=0, structure_type=StructureType.MIXED_STRUCTURE.value
            )

    def _determine_structure_type(self, table_count: int, form_count: int, div_count: int) -> str:
        """Determine HTML structure type để chọn strategy phù hợp"""
        if table_count > STRUCTURE_THRESHOLDS['table_count_for_table_based']:
            return StructureType.TABLE_BASED.value
        elif form_count > 0:
            return StructureType.FORM_BASED.value
        elif div_count > STRUCTURE_THRESHOLDS['div_count_for_div_based']:
            return StructureType.DIV_BASED.value
        else:
            return StructureType.MIXED_STRUCTURE.value

    def extract_by_css_selectors(self, soup: BeautifulSoup, field_name: str, selectors: List[str]) -> Optional[str]:
        """Extract using CSS selectors với enhanced logic"""
        for selector in selectors:
            try:
                elements = soup.select(selector)
                
                # Special handling for thong_tin_thanh_vien - aggregate multiple elements
                if field_name == 'thong_tin_thanh_vien' and elements:
                    return self._handle_multiple_member_elements(elements)
                
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

    def _handle_multiple_member_elements(self, elements: List) -> Optional[str]:
        """Handle multiple member elements for family info extraction"""
        if len(elements) > 1:
            # Multiple elements found - combine them
            combined_text = []
            for element in elements:
                text = element.get_text().strip()
                if text and len(text) > 0:
                    # Skip header rows or irrelevant content
                    skip_headers = ['họ tên', 'quan hệ', 'năm sinh', 'name', 'relationship']
                    if not any(header in text.lower() for header in skip_headers):
                        combined_text.append(text)
            
            if combined_text:
                return ' | '.join(combined_text)  # Use separator to distinguish between members
        
        # Single element or fallback
        for element in elements:
            text = element.get_text().strip()
            if text and len(text) > 0:
                return text
        
        return None

    def extract_by_regex(self, html_content: str, field_name: str, patterns: List[str]) -> Optional[str]:
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

    def extract_by_context(self, soup: BeautifulSoup, field_name: str, keywords: List[str]) -> Optional[str]:
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

    def extract_by_xpath_simulation(self, soup: BeautifulSoup, field_name: str, xpath_patterns: List[str]) -> Optional[str]:
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

    def extract_by_fallback(self, html_content: str, field_name: str, fallback_patterns: List[str]) -> Optional[str]:
        """Extract using fallback patterns when main methods fail"""
        for pattern in fallback_patterns:
            try:
                matches = re.findall(pattern, html_content)
                if matches:
                    # Return first reasonable match
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        if match and len(match.strip()) > PROCESSING_LIMITS['min_text_length_for_processing']:
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

    def calculate_confidence_score(self, base_confidence: float, validation_errors: List[str], method: str) -> float:
        """Calculate final confidence score"""
        try:
            # Start with base confidence
            confidence = base_confidence
            
            # Adjust for validation errors
            from ..config.constants import ERROR_PENALTIES
            error_penalty = len(validation_errors) * ERROR_PENALTIES['validation_error_penalty']
            confidence -= error_penalty
            
            # Adjust for extraction method
            method_weight = METHOD_WEIGHTS.get(method, 0.5)
            confidence *= method_weight
            
            # Ensure confidence stays in [0, 1] range
            return max(0.0, min(1.0, confidence))
            
        except Exception:
            return 0.5  # Default confidence

    def determine_quality_level(self, confidence: float):
        """Determine quality level based on confidence score"""
        from ..config.constants import ExtractionQuality
        
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

    def get_normalization_applied(self, field_name: str, original: str, normalized: Any) -> List[str]:
        """Get list of normalization steps applied"""
        applied = []
        
        if not original:
            return applied
        
        if str(original) != str(normalized):
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
