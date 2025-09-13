#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Extractor - Constants
Chứa tất cả constants, enums và cấu hình cốt lõi của extraction engine.

Author: MiniMax Agent
Date: 2025-09-13
Version: 2.1
"""

from enum import Enum
from typing import Dict, List


class ExtractionQuality(Enum):
    """Quality levels for extractions"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    FAILED = "failed"


class ExtractionMethod(Enum):
    """Available extraction methods"""
    CSS_SELECTOR = "css_selector"
    REGEX_PATTERN = "regex_pattern"
    XPATH_SIMULATION = "xpath_simulation"
    CONTEXT_SEARCH = "context_search"
    FALLBACK_PATTERN = "fallback_pattern"


class StructureType(Enum):
    """HTML structure types"""
    TABLE_BASED = "table_based"
    FORM_BASED = "form_based"
    DIV_BASED = "div_based"
    MIXED_STRUCTURE = "mixed_structure"


# Quality scoring weights
QUALITY_WEIGHTS = {
    'pattern_match_confidence': 0.3,
    'data_structure_score': 0.2,
    'validation_score': 0.25,
    'normalization_success': 0.15,
    'context_relevance': 0.1
}

# Method confidence weights
METHOD_WEIGHTS = {
    ExtractionMethod.CSS_SELECTOR.value: 1.0,
    ExtractionMethod.REGEX_PATTERN.value: 0.9,
    ExtractionMethod.XPATH_SIMULATION.value: 0.9,
    ExtractionMethod.CONTEXT_SEARCH.value: 0.8,
    ExtractionMethod.FALLBACK_PATTERN.value: 0.5
}

# Structure type thresholds
STRUCTURE_THRESHOLDS = {
    'table_count_for_table_based': 3,
    'div_count_for_div_based': 10
}

# Field names
FIELD_NAMES = {
    'PHONE': 'so_dien_thoai',
    'INCOME': 'thu_nhap',
    'BANK': 'ngan_hang', 
    'HOUSEHOLD_CODE': 'ma_ho_gia_dinh',
    'MEMBER_INFO': 'thong_tin_thanh_vien'
}

# Validation ranges
VALIDATION_RANGES = {
    'income_min': 100000,      # 100k VND minimum
    'income_max': 100000000,   # 100M VND maximum
    'household_code_min_length': 8,
    'household_code_max_length': 15,
    'phone_min_length': 9,
    'phone_max_length': 11
}

# Error penalty rates
ERROR_PENALTIES = {
    'validation_error_penalty': 0.1,
    'fallback_confidence_multiplier': 0.5,
    'data_quality_bonus': 0.2
}

# Processing limits
PROCESSING_LIMITS = {
    'max_extraction_attempts': 5,
    'max_normalization_steps': 10,
    'min_text_length_for_processing': 3
}
