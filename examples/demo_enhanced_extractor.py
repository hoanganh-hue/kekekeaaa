#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Extractor - Demo Script
Demonstration của các tính năng chính và use cases
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.vss_enhanced_extractor_v2 import VSS_EnhancedExtractor
import json

def demo_basic_extraction():
    """Demo basic extraction functionality"""
    print("=" * 60)
    print("DEMO 1: BASIC EXTRACTION FUNCTIONALITY")
    print("=" * 60)
    
    # Sample VSS HTML response
    html_content = """
    <html>
    <body>
        <table class="citizen-info">
            <tr><td>Họ và tên:</td><td>NGUYỄN VĂN ANH</td></tr>
            <tr><td>Số điện thoại:</td><td>0912345678</td></tr>
            <tr><td>Thu nhập hàng tháng:</td><td>25,500,000 VND</td></tr>
            <tr><td>Ngân hàng:</td><td>Vietcombank (VCB)</td></tr>
            <tr><td>Mã hộ gia đình:</td><td>HGD123456789</td></tr>
        </table>
        
        <div class="family-section">
            <h3>Thành viên hộ gia đình</h3>
            <p>Trần Thị Bình - Vợ - 1987</p>
            <p>Nguyễn Văn Cường - Con - 2015</p>
        </div>
    </body>
    </html>
    """
    
    # Initialize extractor
    extractor = VSS_EnhancedExtractor()
    
    # Extract fields
    result = extractor.extract_enhanced_fields(html_content)
    
    # Display results
    print("Extraction Results:")
    print("-" * 40)
    
    summary = result.get('extraction_summary', {})
    print(f"✅ Status: {summary.get('status', 'unknown').upper()}")
    print(f"📊 Success Rate: {summary.get('success_rate', 0):.1%}")
    print(f"🎯 Quality Score: {summary.get('overall_quality_score', 0):.2f}")
    print(f"📋 Fields Extracted: {summary.get('successful_extractions', 0)}/{summary.get('total_fields', 0)}")
    
    print("\nDetailed Field Results:")
    extracted_fields = result.get('extracted_fields', {})
    for field_name, extraction_result in extracted_fields.items():
        status = "✅" if extraction_result.extracted_value else "❌"
        print(f"{status} {field_name.replace('_', ' ').title()}: {extraction_result.extracted_value}")
        print(f"    Confidence: {extraction_result.confidence_score:.2f} | Method: {extraction_result.extraction_method}")

def demo_multiple_structures():
    """Demo handling of multiple HTML structures"""
    print("\n" + "=" * 60)
    print("DEMO 2: MULTIPLE HTML STRUCTURES HANDLING")
    print("=" * 60)
    
    extractor = VSS_EnhancedExtractor()
    
    # Test cases với different structures
    test_cases = {
        "Table Structure": """
        <table>
            <tr><td>SĐT:</td><td>0987654321</td></tr>
            <tr><td>Lương:</td><td>18,000,000 đồng</td></tr>
        </table>
        """,
        
        "Div Structure": """
        <div class="info">
            <div class="phone">Phone: +84 908 123 456</div>
            <div class="income">Thu nhập: 22 triệu VND</div>
            <div class="bank">Bank: ACB</div>
        </div>
        """,
        
        "Form Structure": """
        <form>
            <input name="phone" value="0123456789" />
            <input name="salary" value="20000000" />
            <select name="bank">
                <option value="TCB" selected>Techcombank</option>
            </select>
        </form>
        """,
        
        "Mixed Text": """
        <p>Liên hệ: 0932111222, Thu nhập: 15.5 triệu VNĐ, NH: BIDV, Mã HGD: HGD567890123</p>
        """
    }
    
    for structure_name, html in test_cases.items():
        print(f"\n--- {structure_name} ---")
        full_html = f"<html><body>{html}</body></html>"
        result = extractor.extract_enhanced_fields(full_html)
        
        extracted_fields = result.get('extracted_fields', {})
        successful = sum(1 for r in extracted_fields.values() if r.extracted_value)
        total = len(extracted_fields)
        
        print(f"Success: {successful}/{total} fields extracted")
        
        for field_name, extraction_result in extracted_fields.items():
            if extraction_result.extracted_value:
                print(f"  ✅ {field_name}: {extraction_result.extracted_value} (method: {extraction_result.extraction_method})")

def demo_normalization_features():
    """Demo data normalization capabilities"""
    print("\n" + "=" * 60)
    print("DEMO 3: DATA NORMALIZATION FEATURES")
    print("=" * 60)
    
    extractor = VSS_EnhancedExtractor()
    
    # Test normalization với different formats
    normalization_tests = {
        "Phone Numbers": [
            "<p>Phone: +84 912 345 678</p>",
            "<p>SĐT: 0912.345.678</p>", 
            "<p>Tel: 84912345678</p>"
        ],
        "Income Values": [
            "<p>Lương: 25,500,000 VND</p>",
            "<p>Thu nhập: 18 triệu đồng</p>",
            "<p>Income: 22000000</p>"
        ],
        "Bank Names": [
            "<p>Bank: VCB</p>",
            "<p>NH: Techcombank</p>",
            "<p>Ngân hàng: ACB</p>"
        ]
    }
    
    for category, test_htmls in normalization_tests.items():
        print(f"\n--- {category} ---")
        
        for i, html in enumerate(test_htmls, 1):
            full_html = f"<html><body>{html}</body></html>"
            result = extractor.extract_enhanced_fields(full_html)
            
            # Find the relevant field result
            extracted_fields = result.get('extracted_fields', {})
            for field_name, extraction_result in extracted_fields.items():
                if extraction_result.extracted_value:
                    normalizations = ", ".join(extraction_result.normalization_applied) if extraction_result.normalization_applied else "None"
                    print(f"  Test {i}: {extraction_result.extracted_value} (normalizations: {normalizations})")
                    break

def demo_cross_validation():
    """Demo cross-validation features"""
    print("\n" + "=" * 60)
    print("DEMO 4: CROSS-VALIDATION FEATURES")
    print("=" * 60)
    
    extractor = VSS_EnhancedExtractor()
    
    html_content = """
    <table>
        <tr><td>Điện thoại:</td><td>0912345678</td></tr>
        <tr><td>Thu nhập:</td><td>25,000,000 VND</td></tr>
        <tr><td>Ngân hàng:</td><td>VCB</td></tr>
    </table>
    """
    
    # Test với matching input data
    matching_input = {
        'phone': '0912345678',
        'income': '25000000',
        'bank': 'VCB'
    }
    
    # Test với mismatched input data
    mismatched_input = {
        'phone': '0987654321',  # Different phone
        'income': '20000000',   # Different income
        'bank': 'ACB'          # Different bank
    }
    
    print("Cross-validation Test 1 - Matching Data:")
    result1 = extractor.extract_enhanced_fields(html_content, matching_input)
    cross_val1 = result1.get('cross_validation', {})
    print(f"  Consistency Score: {cross_val1.get('overall_consistency', 0):.2f}")
    
    print("\nCross-validation Test 2 - Mismatched Data:")
    result2 = extractor.extract_enhanced_fields(html_content, mismatched_input)
    cross_val2 = result2.get('cross_validation', {})
    print(f"  Consistency Score: {cross_val2.get('overall_consistency', 0):.2f}")
    
    # Show field-level validation
    field_validations = cross_val2.get('field_validations', {})
    for field_name, validation in field_validations.items():
        if 'is_consistent' in validation:
            status = "✅" if validation['is_consistent'] else "❌"
            print(f"  {status} {field_name}: {validation.get('comparison_notes', 'N/A')}")

def demo_quality_scoring():
    """Demo quality scoring system"""
    print("\n" + "=" * 60)
    print("DEMO 5: QUALITY SCORING SYSTEM")
    print("=" * 60)
    
    extractor = VSS_EnhancedExtractor()
    
    # Test samples với different quality levels
    quality_tests = {
        "High Quality (Table)": """
        <table>
            <tr><td>Điện thoại:</td><td>0912345678</td></tr>
            <tr><td>Thu nhập:</td><td>25,000,000 VND</td></tr>
            <tr><td>Ngân hàng:</td><td>VCB</td></tr>
            <tr><td>Mã hộ gia đình:</td><td>HGD123456789</td></tr>
        </table>
        """,
        
        "Medium Quality (Mixed)": """
        <div>
            Phone: 0987654321, Income: 18000000, Bank: ACB
        </div>
        """,
        
        "Low Quality (Minimal)": """
        <p>SĐT: 0123456789</p>
        <p>Some bank info</p>
        """
    }
    
    for test_name, html in quality_tests.items():
        print(f"\n--- {test_name} ---")
        full_html = f"<html><body>{html}</body></html>"
        result = extractor.extract_enhanced_fields(full_html)
        
        summary = result.get('extraction_summary', {})
        quality_metrics = result.get('quality_metrics', {})
        
        print(f"  Overall Status: {summary.get('status', 'unknown').upper()}")
        print(f"  Success Rate: {summary.get('success_rate', 0):.1%}")
        print(f"  Quality Score: {summary.get('overall_quality_score', 0):.2f}")
        
        # Show field-level quality
        extracted_fields = result.get('extracted_fields', {})
        for field_name, extraction_result in extracted_fields.items():
            if extraction_result.extracted_value:
                print(f"    {field_name}: {extraction_result.quality_level.value} (confidence: {extraction_result.confidence_score:.2f})")

def demo_error_handling():
    """Demo error handling và fallback mechanisms"""
    print("\n" + "=" * 60)
    print("DEMO 6: ERROR HANDLING & FALLBACK MECHANISMS")
    print("=" * 60)
    
    extractor = VSS_EnhancedExtractor()
    
    # Test với problematic HTML
    error_tests = {
        "Invalid HTML": "<html><body><p>Incomplete",
        "No Relevant Data": "<html><body><p>This is just random text</p></body></html>",
        "Malformed Data": "<html><body><p>Phone: invalid_phone_number</p></body></html>",
        "Empty Content": "<html><body></body></html>"
    }
    
    for test_name, html in error_tests.items():
        print(f"\n--- {test_name} ---")
        
        try:
            result = extractor.extract_enhanced_fields(html)
            
            if result.get('extraction_success', True):
                summary = result.get('extraction_summary', {})
                print(f"  Status: {summary.get('status', 'unknown')}")
                print(f"  Success Rate: {summary.get('success_rate', 0):.1%}")
                
                # Show errors
                extracted_fields = result.get('extracted_fields', {})
                for field_name, extraction_result in extracted_fields.items():
                    if extraction_result.validation_errors:
                        print(f"  ⚠️  {field_name} errors: {len(extraction_result.validation_errors)}")
                        for error in extraction_result.validation_errors[:2]:  # Show first 2 errors
                            print(f"      - {error}")
            else:
                print(f"  ❌ Extraction failed: {result.get('extraction_error', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ❌ Exception caught: {e}")

def main():
    """Main demo function"""
    print("VSS ENHANCED FIELDS EXTRACTION ENGINE")
    print("🚀 COMPREHENSIVE FEATURE DEMONSTRATION")
    print("=" * 80)
    
    try:
        # Run all demos
        demo_basic_extraction()
        demo_multiple_structures()
        demo_normalization_features()
        demo_cross_validation()
        demo_quality_scoring()
        demo_error_handling()
        
        print("\n" + "=" * 80)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("📖 For detailed documentation, see: /workspace/docs/VSS_Enhanced_Extractor_Documentation.md")
        print("🧪 For comprehensive testing, run: python test_enhanced_extractor.py")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
