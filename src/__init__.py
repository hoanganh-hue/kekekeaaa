#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Extractor Package (Refactored)
Version 2.1 - Improved architecture with modular design

Author: MiniMax Agent
Date: 2025-09-13
"""

from .vss_enhanced_extractor_v2 import VSS_EnhancedExtractor
from .config.constants import ExtractionQuality, ExtractionMethod, FIELD_NAMES
from .config.data_models import ExtractionResult, ExtractionSummary, MemberInfo
from .utils import quick_extract, validate_and_export, ExtractionLogger

__version__ = "2.1.0"
__author__ = "MiniMax Agent"

# Export main classes and functions
__all__ = [
    'VSS_EnhancedExtractor',
    'ExtractionQuality',
    'ExtractionMethod', 
    'ExtractionResult',
    'ExtractionSummary',
    'MemberInfo',
    'FIELD_NAMES',
    'quick_extract',
    'validate_and_export',
    'ExtractionLogger'
]

# Package metadata
PACKAGE_INFO = {
    'name': 'VSS Enhanced Extractor',
    'version': __version__,
    'description': 'Enhanced fields extraction engine for VSS with robust pattern matching and validation',
    'author': __author__,
    'features': [
        'Multi-strategy extraction (CSS, Regex, Context, XPath)',
        'Advanced normalization and validation',
        'Quality scoring and confidence metrics',
        'Cross-validation support',
        'Comprehensive logging and monitoring',
        'Multiple export formats (JSON, CSV, Excel)',
        'Modular architecture for easy extension'
    ],
    'supported_fields': list(FIELD_NAMES.values()),
    'architecture_version': '2.1'
}

def get_package_info():
    """Get package information"""
    return PACKAGE_INFO

def create_extractor(**kwargs):
    """Factory function to create extractor instance"""
    return VSS_EnhancedExtractor(**kwargs)
