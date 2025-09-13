#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script cho VSS Enhanced Fields Extraction Engine
Kiểm tra tất cả tính năng extraction với multiple HTML structures
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.vss_enhanced_extractor_v2 import VSS_EnhancedExtractor, create_sample_html_responses

def create_comprehensive_test_samples():
    """Tạo comprehensive test samples với different structures"""
    
    samples = {
        # Sample 1: Table-based VSS response (realistic)
        'table_based_vss': """
        <!DOCTYPE html>
        <html>
        <head><title>VSS Lookup Result</title></head>
        <body>
            <div class="content">
                <h2>Thông tin BHXH</h2>
                <table class="info-table">
                    <tr><td class="label">Họ và tên:</td><td class="value">NGUYỄN VĂN ANH</td></tr>
                    <tr><td class="label">Ngày sinh:</td><td class="value">15/03/1985</td></tr>
                    <tr><td class="label">Số BHXH:</td><td class="value">123456789012</td></tr>
                    <tr><td class="label">Điện thoại liên hệ:</td><td class="value">0912345678</td></tr>
                    <tr><td class="label">Thu nhập hàng tháng:</td><td class="value">25,500,000 VND</td></tr>
                    <tr><td class="label">Ngân hàng nhận lương:</td><td class="value">Vietcombank (VCB)</td></tr>
                    <tr><td class="label">Mã hộ gia đình:</td><td class="value">HGD202301234</td></tr>
                    <tr><td class="label">Đơn vị công tác:</td><td class="value">Công ty TNHH ABC</td></tr>
                </table>
                
                <h3>Thành viên hộ gia đình</h3>
                <table class="family-table">
                    <thead>
                        <tr><th>Họ tên</th><th>Quan hệ</th><th>Năm sinh</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>Trần Thị Bình</td><td>Vợ</td><td>1987</td></tr>
                        <tr><td>Nguyễn Văn Cường</td><td>Con</td><td>2015</td></tr>
                        <tr><td>Nguyễn Thị Dung</td><td>Con</td><td>2018</td></tr>
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """,
        
        # Sample 2: Div-based modern structure
        'div_based_modern': """
        <html>
        <body>
            <div class="profile-container">
                <div class="personal-info">
                    <div class="field" data-field="name">
                        <label>Họ tên:</label>
                        <span class="value">LÊ THỊ HOA</span>
                    </div>
                    <div class="field contact-info" data-field="phone">
                        <label>SĐT:</label>
                        <span class="phone-value">+84 987 654 321</span>
                    </div>
                    <div class="field income-info">
                        <label>Mức lương:</label>
                        <span class="salary">18 triệu VND/tháng</span>
                    </div>
                    <div class="banking-info">
                        <span class="bank-label">NH:</span>
                        <span class="bank-name">Techcombank</span>
                    </div>
                </div>
                
                <div class="household-section">
                    <div class="household-code">
                        <strong>Mã HGĐ: HGD456789012</strong>
                    </div>
                    <div class="family-members">
                        <h4>Thành viên gia đình</h4>
                        <div class="member">Phạm Văn Nam - Chồng - 1983</div>
                        <div class="member">Lê Văn Minh - Con - 2012</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """,
        
        # Sample 3: Form-based với JSON embedded
        'form_based_with_json': """
        <html>
        <head>
            <script type="application/json" id="user-data">
            {
                "citizen_info": {
                    "name": "HOÀNG VĂN ĐỨC",
                    "phone": "0123456789",
                    "income": "30000000",
                    "bank_code": "ACB",
                    "household_id": "HGD789012345"
                },
                "family_members": [
                    {"name": "Nguyễn Thị Lan", "relation": "Vợ", "birth_year": "1990"},
                    {"name": "Hoàng Văn Quang", "relation": "Con", "birth_year": "2016"}
                ]
            }
            </script>
        </head>
        <body>
            <form class="citizen-form">
                <div class="form-group">
                    <label>Điện thoại:</label>
                    <input type="tel" name="phone" value="0123456789" readonly>
                </div>
                <div class="form-group">
                    <label>Thu nhập:</label>
                    <input type="text" name="income" value="30,000,000 VNĐ" readonly>
                </div>
                <div class="form-group">
                    <label>Ngân hàng:</label>
                    <select name="bank" disabled>
                        <option value="">-- Chọn ngân hàng --</option>
                        <option value="ACB" selected>Á Châu (ACB)</option>
                        <option value="VCB">Vietcombank</option>
                    </select>
                </div>
                <div class="household-info">
                    <p>Mã hộ: <strong>HGD789012345</strong></p>
                    <div class="members">
                        <p>Vợ: Nguyễn Thị Lan (1990)</p>
                        <p>Con: Hoàng Văn Quang (2016)</p>
                    </div>
                </div>
            </form>
        </body>
        </html>
        """,
        
        # Sample 4: Complex mixed structure
        'complex_mixed': """
        <html>
        <body>
            <!-- Header info -->
            <div id="citizen-header">
                <h1>Tra cứu BHXH: PHAN THỊ MAI</h1>
                <p class="contact-info">Liên hệ: 0908.123.456 | Email: mai@example.com</p>
            </div>
            
            <!-- Main content in mixed format -->
            <div class="main-content">
                <div class="left-panel">
                    <table class="basic-info">
                        <tr><td>Thu nhập cơ bản:</td><td>22,800,000 đồng</td></tr>
                        <tr><td>Phụ cấp:</td><td>2,200,000 đồng</td></tr>
                        <tr><td>Tổng thu nhập:</td><td>25,000,000 VND</td></tr>
                    </table>
                </div>
                
                <div class="right-panel">
                    <div class="banking-details">
                        <span>Tài khoản ngân hàng:</span>
                        <div class="bank-info">
                            <div>Tên NH: BIDV</div>
                            <div>Mã NH: BID</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Footer with household info -->
            <div class="household-footer">
                <div class="hgd-info">
                    <span class="label">Hộ gia đình:</span>
                    <span class="code">HGD567890123</span>
                </div>
                
                <!-- Family members in paragraph format -->
                <div class="family-text">
                    Thành viên: Lê Văn Tuấn (Chồng, 1982), Phan Thị Oanh (Con, 2014), Phan Văn Tùng (Con, 2017)
                </div>
            </div>
            
            <!-- Hidden data for testing fallbacks -->
            <div style="display:none">
                Alternative phone: 84908123456
                Backup income: 25.0 triệu
                Bank alt: TMCP Đầu tư và Phát triển Việt Nam
            </div>
        </body>
        </html>
        """,
        
        # Sample 5: Minimal/poor structure (edge case)
        'minimal_structure': """
        <html>
        <body>
            <p>TRẦN VĂN BÌNH - SĐT: 0932.111.222</p>
            <p>Lương: 18000000 VND, Bank: VIB</p>
            <p>HGD012345678</p>
            <p>Gia đình: Vợ - Nguyễn Thị Cẩm, Con - Trần Minh Khôi (2019)</p>
        </body>
        </html>
        """
    }
    
    return samples

def test_individual_sample(extractor, sample_name, html_content, input_data=None):
    """Test một sample và return kết quả"""
    print(f"\n{'='*60}")
    print(f"TESTING: {sample_name}")
    print('='*60)
    
    try:
        # Extract fields
        result = extractor.extract_enhanced_fields(html_content, input_data)
        
        # Print summary
        summary = result.get('extraction_summary', {})
        print(f"Extraction Status: {summary.get('status', 'unknown').upper()}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1%}")
        print(f"Quality Score: {summary.get('overall_quality_score', 0):.2f}")
        print(f"Successful Fields: {summary.get('successful_extractions', 0)}/{summary.get('total_fields', 0)}")
        
        # Print detailed results
        print("\nFIELD EXTRACTION RESULTS:")
        print("-" * 40)
        
        extracted_fields = result.get('extracted_fields', {})
        for field_name, extraction_result in extracted_fields.items():
            print(f"\n{field_name.upper().replace('_', ' ')}:")
            print(f"  ✓ Value: {extraction_result.extracted_value}")
            print(f"  ✓ Confidence: {extraction_result.confidence_score:.2f}")
            print(f"  ✓ Quality: {extraction_result.quality_level.value}")
            print(f"  ✓ Method: {extraction_result.extraction_method}")
            
            if extraction_result.validation_errors:
                print(f"  ⚠ Validation Errors: {len(extraction_result.validation_errors)}")
                for error in extraction_result.validation_errors[:3]:  # Show max 3
                    print(f"    - {error}")
            
            if extraction_result.normalization_applied:
                print(f"  🔄 Normalizations: {', '.join(extraction_result.normalization_applied)}")
        
        # Cross-validation results
        cross_val = result.get('cross_validation', {})
        if cross_val and input_data:
            print(f"\nCROSS-VALIDATION:")
            print(f"  Overall Consistency: {cross_val.get('overall_consistency', 0):.2f}")
            if cross_val.get('inconsistencies'):
                print(f"  Inconsistencies Found: {len(cross_val['inconsistencies'])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing sample: {e}")
        return None

def run_comprehensive_test():
    """Run comprehensive test với tất cả samples"""
    print("VSS ENHANCED FIELDS EXTRACTION ENGINE - COMPREHENSIVE TEST")
    print("="*80)
    
    # Initialize extractor
    extractor = VSS_EnhancedExtractor()
    
    # Get test samples
    samples = create_comprehensive_test_samples()
    
    # Input data cho cross-validation testing
    test_input_data = {
        'table_based_vss': {
            'phone': '0912345678',
            'expected_income': 25500000,
            'bank': 'VCB'
        },
        'div_based_modern': {
            'phone': '0987654321',
            'expected_income': 18000000
        },
        'form_based_with_json': {
            'phone': '0123456789',
            'expected_income': 30000000,
            'bank': 'ACB'
        },
        'complex_mixed': {
            'phone': '0908123456',
            'expected_income': 25000000
        },
        'minimal_structure': {
            'phone': '0932111222',
            'expected_income': 18000000
        }
    }
    
    # Test results collector
    all_results = {}
    
    # Test từng sample
    for sample_name, html_content in samples.items():
        input_data = test_input_data.get(sample_name)
        result = test_individual_sample(extractor, sample_name, html_content, input_data)
        all_results[sample_name] = result
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("COMPREHENSIVE TEST SUMMARY")
    print('='*80)
    
    # Overall statistics
    total_samples = len(samples)
    successful_samples = sum(1 for r in all_results.values() 
                           if r and r.get('extraction_summary', {}).get('status') not in ['poor', 'failed'])
    
    print(f"Total Samples Tested: {total_samples}")
    print(f"Successful Extractions: {successful_samples}")
    print(f"Overall Success Rate: {successful_samples/total_samples:.1%}")
    
    # Field-level statistics
    field_success_stats = {}
    field_confidence_stats = {}
    
    for sample_name, result in all_results.items():
        if result:
            extracted_fields = result.get('extracted_fields', {})
            for field_name, extraction_result in extracted_fields.items():
                if field_name not in field_success_stats:
                    field_success_stats[field_name] = {'success': 0, 'total': 0}
                    field_confidence_stats[field_name] = []
                
                field_success_stats[field_name]['total'] += 1
                if extraction_result.extracted_value:
                    field_success_stats[field_name]['success'] += 1
                    field_confidence_stats[field_name].append(extraction_result.confidence_score)
    
    print("\nFIELD-LEVEL PERFORMANCE:")
    print("-" * 40)
    for field_name, stats in field_success_stats.items():
        success_rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0
        avg_confidence = sum(field_confidence_stats[field_name]) / len(field_confidence_stats[field_name]) \
                        if field_confidence_stats[field_name] else 0
        
        print(f"{field_name.replace('_', ' ').title():<20}: "
              f"{success_rate:>6.1%} success, "
              f"avg confidence {avg_confidence:>4.2f}")
    
    # Save detailed results
    try:
        output_file = "/workspace/test_results_enhanced_extractor.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convert ExtractionQuality enums to strings for JSON serialization
            json_results = {}
            for sample_name, result in all_results.items():
                if result:
                    json_result = result.copy()
                    # Convert enum values to strings
                    if 'extracted_fields' in json_result:
                        for field_name, extraction_result in json_result['extracted_fields'].items():
                            extraction_result.quality_level = extraction_result.quality_level.value
                    json_results[sample_name] = json_result
                    
            json.dump(json_results, f, ensure_ascii=False, indent=2)
        print(f"\n📁 Detailed results saved to: {output_file}")
    except Exception as e:
        print(f"⚠️  Could not save results file: {e}")
    
    print("\n✅ Comprehensive test completed!")
    
    return all_results

def demo_specific_field_testing():
    """Demo testing cho specific fields"""
    print("\n" + "="*60)
    print("SPECIFIC FIELD TESTING DEMO")
    print("="*60)
    
    extractor = VSS_EnhancedExtractor()
    
    # Test cases cho từng field
    field_test_cases = {
        'so_dien_thoai': [
            '<td>Điện thoại: 0912345678</td>',
            '<span class="phone">+84 987 654 321</span>',
            '<div>SĐT: 0123.456.789</div>',
            '<p>Phone: 84908123456</p>'
        ],
        'thu_nhap': [
            '<td>Thu nhập: 25,500,000 VND</td>',
            '<div>Lương: 18 triệu đồng</div>',
            '<span>Income: 30000000</span>',
            '<p>Salary: 22.5 triệu VNĐ</p>'
        ],
        'ngan_hang': [
            '<td>Ngân hàng: Vietcombank</td>',
            '<div>Bank: ACB</div>',
            '<span>NH: BIDV</span>',
            '<select><option selected>Techcombank (TCB)</option></select>'
        ],
        'ma_ho_gia_dinh': [
            '<td>Mã hộ gia đình: HGD123456789</td>',
            '<div>HGD: ABC789012345</div>',
            '<span>Household Code: HGD567890123</span>',
            '<p>Hộ gia đình: XYZ012345678</p>'
        ],
        'thong_tin_thanh_vien': [
            '<div>Thành viên: Nguyễn Văn A - Vợ - 1985, Nguyễn Thị B - Con - 2015</div>',
            '<table><tr><td>Trần Văn C</td><td>Chồng</td><td>1980</td></tr></table>',
            '<p>Gia đình: Mẹ - Nguyễn Thị D (1960), Em - Nguyễn Văn E (1995)</p>',
            '<ul><li>Lê Thị F: Vợ</li><li>Lê Văn G: Con (2018)</li></ul>'
        ]
    }
    
    for field_name, test_htmls in field_test_cases.items():
        print(f"\nTesting {field_name.upper().replace('_', ' ')}:")
        print("-" * 30)
        
        for i, html_snippet in enumerate(test_htmls, 1):
            full_html = f"<html><body>{html_snippet}</body></html>"
            result = extractor.extract_enhanced_fields(full_html)
            
            field_result = result.get('extracted_fields', {}).get(field_name)
            if field_result:
                print(f"  Test {i}: ✅ {field_result.extracted_value} "
                      f"(confidence: {field_result.confidence_score:.2f}, "
                      f"method: {field_result.extraction_method})")
            else:
                print(f"  Test {i}: ❌ No extraction")

if __name__ == "__main__":
    # Run comprehensive test
    results = run_comprehensive_test()
    
    # Run specific field testing demo
    demo_specific_field_testing()
    
    print(f"\n🎉 All tests completed! Check /workspace/test_results_enhanced_extractor.json for detailed results.")
