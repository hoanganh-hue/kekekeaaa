#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Refactored VSS Enhanced Extractor với real data
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.vss_enhanced_extractor_v2 import VSS_EnhancedExtractor
from src.utils import validate_and_export, ExtractionLogger

def test_with_sample_data():
    """Test với sample data có sẵn"""
    
    # Initialize logger
    logger = ExtractionLogger()
    
    # Initialize extractor
    print("🔧 Initializing VSS Enhanced Extractor v2.1...")
    extractor = VSS_EnhancedExtractor()
    
    # Load sample HTML
    sample_file = Path("vss_data_sample.html")
    if not sample_file.exists():
        print("❌ Sample file not found. Creating dummy data...")
        sample_html = """
        <html>
        <body>
            <div class="household-footer">
                <div class="family-text">Trần Thị Bình - Vợ - 1987</div>
            </div>
            <table>
                <tr><td>Điện thoại</td><td>0987654321</td></tr>
                <tr><td>Thu nhập</td><td>15,000,000 VND</td></tr>
                <tr><td>Ngân hàng</td><td>VCB</td></tr>
                <tr><td>Mã hộ gia đình</td><td>HGD123456789</td></tr>
            </table>
        </body>
        </html>
        """
    else:
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_html = f.read()
        print(f"✅ Loaded sample data from {sample_file}")
    
    # Test extraction
    print("\n🧪 Testing extraction...")
    logger.log_extraction_start(5, len(sample_html))
    
    results = extractor.extract_enhanced_fields(sample_html)
    
    # Log results
    for field_name, result in results['extracted_fields'].items():
        logger.log_field_extraction(field_name, result)
    
    logger.log_extraction_summary(results['extraction_summary'])
    
    # Print summary
    print("\n📊 Extraction Summary:")
    summary = results['extraction_summary']
    print(f"  • Total Fields: {summary.total_fields}")
    print(f"  • Successful: {summary.successful_extractions}")
    print(f"  • Success Rate: {summary.success_rate:.1%}")
    print(f"  • Overall Quality: {summary.overall_quality_score:.2f}")
    print(f"  • Status: {summary.status}")
    
    # Export results
    print("\n💾 Exporting results...")
    exports = validate_and_export(results, "test_output")
    print(f"  • JSON: {exports['json_export']}")
    print(f"  • CSV: {exports['csv_export']}")
    print(f"  • Report: {exports['validation_report']}")
    
    # Show field details
    print("\n🔍 Field Details:")
    for field_name, result in results['extracted_fields'].items():
        status = "✅" if result.is_successful else "❌"
        print(f"  {status} {field_name}: {result.extracted_value} (confidence: {result.confidence_score:.2f})")
    
    print("\n🎉 Test completed successfully!")
    return results

if __name__ == "__main__":
    test_with_sample_data()
