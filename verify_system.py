#!/usr/bin/env python3
"""
VSS Enhanced Extractor - System Verification Script
Kiểm tra và xác thực tính toàn vẹn của hệ thống
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description=""):
    """Kiểm tra file tồn tại"""
    if Path(file_path).exists():
        print(f"✅ {file_path} - {description}")
        return True
    else:
        print(f"❌ {file_path} - {description} [MISSING]")
        return False

def check_directory_exists(dir_path, description=""):
    """Kiểm tra thư mục tồn tại"""
    if Path(dir_path).is_dir():
        file_count = len(list(Path(dir_path).glob("*")))
        print(f"✅ {dir_path}/ ({file_count} files) - {description}")
        return True
    else:
        print(f"❌ {dir_path}/ - {description} [MISSING]")
        return False

def verify_system():
    """Xác minh tính toàn vẹn của hệ thống"""
    print("=" * 60)
    print("VSS ENHANCED EXTRACTOR v2.1 - SYSTEM VERIFICATION")
    print("=" * 60)
    
    missing_files = []
    
    # Core files
    print("\n🔍 CORE APPLICATION FILES:")
    if not check_file_exists("vss_enhanced_extractor.py", "Main extractor (backward compatibility)"):
        missing_files.append("vss_enhanced_extractor.py")
    if not check_file_exists("requirements.txt", "Python dependencies"):
        missing_files.append("requirements.txt")
    
    # Source code structure
    print("\n🔍 MODULAR ARCHITECTURE (v2.1):")
    if not check_directory_exists("src", "Source code directory"):
        missing_files.append("src/")
    if not check_file_exists("src/vss_enhanced_extractor_v2.py", "New extractor v2.1"):
        missing_files.append("src/vss_enhanced_extractor_v2.py")
    if not check_directory_exists("src/config", "Configuration modules"):
        missing_files.append("src/config/")
    if not check_directory_exists("src/extractors", "Extractor modules"):
        missing_files.append("src/extractors/")
    if not check_directory_exists("src/normalizers", "Normalizer modules"):
        missing_files.append("src/normalizers/")
    if not check_directory_exists("src/validators", "Validator modules"):
        missing_files.append("src/validators/")
    
    # Configuration
    print("\n🔍 CONFIGURATION FILES:")
    if not check_directory_exists("config", "System configuration"):
        missing_files.append("config/")
    if not check_file_exists("config/vss_config.yaml", "Main configuration"):
        missing_files.append("config/vss_config.yaml")
    if not check_file_exists("config/provinces.json", "Province data"):
        missing_files.append("config/provinces.json")
    
    # Data files
    print("\n🔍 DATA FILES:")
    if not check_directory_exists("data", "Sample data files"):
        missing_files.append("data/")
    if not check_file_exists("data/data-input.xlsx", "Sample input file"):
        missing_files.append("data/data-input.xlsx")
    
    # Documentation
    print("\n🔍 DOCUMENTATION:")
    if not check_directory_exists("docs", "Documentation directory"):
        missing_files.append("docs/")
    if not check_file_exists("docs/ARCHITECTURE_V2.1.md", "Architecture documentation"):
        missing_files.append("docs/ARCHITECTURE_V2.1.md")
    if not check_file_exists("README_COMPREHENSIVE.md", "Comprehensive README"):
        missing_files.append("README_COMPREHENSIVE.md")
    if not check_file_exists("QUICK_START.md", "Quick start guide"):
        missing_files.append("QUICK_START.md")
    
    # Tests
    print("\n🔍 TEST FILES:")
    if not check_directory_exists("tests", "Test directory"):
        missing_files.append("tests/")
    if not check_file_exists("tests/test_refactored_extractor.py", "Refactored extractor test"):
        missing_files.append("tests/test_refactored_extractor.py")
    
    # Supporting files
    print("\n🔍 SUPPORTING FILES:")
    if not check_directory_exists("examples", "Usage examples"):
        missing_files.append("examples/")
    if not check_directory_exists("scripts", "Utility scripts"):
        missing_files.append("scripts/")
    if not check_directory_exists("charts", "Charts and visualizations"):
        missing_files.append("charts/")
    if not check_directory_exists("tools", "Migration and utility tools"):
        missing_files.append("tools/")
    
    # Summary
    print("\n" + "=" * 60)
    if missing_files:
        print(f"⚠️  CẢNH BÁO: Thiếu {len(missing_files)} file/thư mục:")
        for item in missing_files:
            print(f"   - {item}")
        print(f"\n❌ Hệ thống KHÔNG đầy đủ. Vui lòng kiểm tra lại!")
        return False
    else:
        print("🎉 HỆ THỐNG HOÀN CHỈNH!")
        print("✅ Tất cả file và thư mục cần thiết đều có.")
        print("📚 Đọc QUICK_START.md để bắt đầu sử dụng.")
        return True

def test_import():
    """Test import các module chính"""
    print("\n🔍 TESTING IMPORTS:")
    
    try:
        # Test Python path
        if 'src' not in sys.path:
            sys.path.insert(0, 'src')
        
        # Test import v2.1
        from vss_enhanced_extractor_v2 import VssEnhancedExtractorV2
        print("✅ Import VssEnhancedExtractorV2 thành công")
        
        # Test import config modules
        import config.constants
        print("✅ Import config.constants thành công")
        
        from config.patterns import EXTRACTION_PATTERNS
        print("✅ Import config.patterns thành công")
        
        from extractors.base_extractor import BaseExtractor
        print("✅ Import extractors.base_extractor thành công")
        
        print("🎉 TẤT CẢ IMPORT THÀNH CÔNG!")
        return True
        
    except ImportError as e:
        print(f"❌ Lỗi import: {e}")
        print("💡 Hãy chắc chắn rằng PYTHONPATH được thiết lập đúng:")
        print("   export PYTHONPATH=\"${PYTHONPATH}:$(pwd)/src\"")
        return False
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        return False

if __name__ == "__main__":
    print("Bắt đầu kiểm tra tính toàn vẹn hệ thống...")
    
    system_ok = verify_system()
    if system_ok:
        imports_ok = test_import()
        if imports_ok:
            print("\n" + "=" * 60)
            print("🚀 HỆ THỐNG SẴN SÀNG SỬ DỤNG!")
            print("📖 Tham khảo QUICK_START.md để bắt đầu")
            print("📚 Đọc README_COMPREHENSIVE.md để hiểu đầy đủ")
        else:
            print("\n❌ Có lỗi với imports. Kiểm tra lại cài đặt.")
            sys.exit(1)
    else:
        print("\n❌ Hệ thống không đầy đủ. Vui lòng kiểm tra lại!")
        sys.exit(1)