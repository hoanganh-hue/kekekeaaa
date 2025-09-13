#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Extractor - Compatibility Layer
Provides backward compatibility với version 2.0 interface

This file maintains compatibility with existing code while using the new v2.1 architecture.

Author: MiniMax Agent
Date: 2025-09-13
Version: 2.1 (Compatibility Layer)
"""

import warnings
from src.vss_enhanced_extractor_v2 import VSS_EnhancedExtractor as _VSS_EnhancedExtractor_V2
from src.config.constants import ExtractionQuality
from src.config.data_models import ExtractionResult, FieldPattern


class VSS_EnhancedExtractor(_VSS_EnhancedExtractor_V2):
    """
    Compatibility wrapper for VSS Enhanced Extractor v2.1
    
    This class provides the same interface as v2.0 while using the new modular architecture.
    """
    
    def __init__(self):
        """Initialize với compatibility warning"""
        warnings.warn(
            "You are using the compatibility layer for VSS Enhanced Extractor. "
            "Consider migrating to the new modular API for better performance and features. "
            "Import from 'src.vss_enhanced_extractor_v2' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__()
    
    # Maintain old method names for compatibility
    def _initialize_enhanced_patterns(self):
        """Legacy method name - redirects to new implementation"""
        return self.field_patterns
    
    def _get_optimized_patterns(self):
        """Legacy method name - redirects to new implementation"""
        return self.field_patterns
    
    def _initialize_normalization_maps(self):
        """Legacy method name - redirects to new implementation"""
        return self.normalization_maps


# Export legacy classes and constants for compatibility
__all__ = [
    'VSS_EnhancedExtractor',
    'ExtractionQuality', 
    'ExtractionResult',
    'FieldPattern'
]

# Legacy demo function
def run_enhanced_extraction_demo():
    """Legacy demo function"""
    print("=== VSS Enhanced Fields Extraction Engine Demo (Compatibility Mode) ===\n")
    print("Note: You are using the compatibility layer. Consider upgrading to v2.1 API.\n")
    
    # Use new implementation
    from src.utils import quick_extract
    
    # Sample HTML for demo
    samples = [
        '<html><body><table><tr><td>Điện thoại</td><td>9876543210</td></tr><tr><td>Thu nhập</td><td>15,000,000 VND</td></tr><tr><td>Ngân hàng</td><td>VCB</td></tr></table></body></html>'
    ]
    
    for i, html_content in enumerate(samples, 1):
        print(f"--- Testing Sample {i} ---")
        
        result = quick_extract(html_content)
        
        print("Extraction Results:")
        print(f"  Status: {result.get('extraction_summary', {}).get('status', 'unknown')}")
        print(f"  Success Rate: {result.get('extraction_summary', {}).get('success_rate', 0):.2%}")
        
        for field_name, extraction_result in result.get('extracted_fields', {}).items():
            print(f"  {field_name}:")
            print(f"    Value: {extraction_result.extracted_value}")
            print(f"    Confidence: {extraction_result.confidence_score:.2f}")
            print(f"    Quality: {extraction_result.quality_level.value}")
        
        print()
    
    print("=== Demo completed (Compatibility Mode) ===")


if __name__ == "__main__":
    run_enhanced_extraction_demo()
