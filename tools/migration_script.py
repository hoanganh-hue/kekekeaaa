#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Extractor - Migration Script
Migrate từ version 2.0 (monolithic) sang version 2.1 (modular)

Author: MiniMax Agent
Date: 2025-09-13
Version: 2.1
"""

import sys
import os
import shutil
import warnings
from pathlib import Path
import logging

# Add src to path để import được modules
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def migrate_to_v2():
    """Migrate existing codebase to version 2.1"""
    
    logger.info("Starting migration from VSS Enhanced Extractor v2.0 to v2.1")
    
    # Step 1: Backup old version
    backup_old_version()
    
    # Step 2: Test new version compatibility
    test_new_version()
    
    # Step 3: Update imports in existing scripts
    update_existing_scripts()
    
    # Step 4: Create compatibility layer
    create_compatibility_layer()
    
    logger.info("Migration completed successfully!")


def backup_old_version():
    """Create backup of old version"""
    logger.info("Creating backup of old version...")
    
    workspace_path = Path(__file__).parent
    old_extractor = workspace_path / "vss_enhanced_extractor.py"
    backup_dir = workspace_path / "backups" / "v2.0"
    
    # Create backup directory
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup old extractor if exists
    if old_extractor.exists():
        backup_path = backup_dir / "vss_enhanced_extractor_v2.0_backup.py"
        shutil.copy2(old_extractor, backup_path)
        logger.info(f"Backed up old extractor to: {backup_path}")
    
    # Backup any existing config files
    for config_file in workspace_path.glob("*config*.py"):
        if config_file.name != "migration_script.py":
            backup_path = backup_dir / config_file.name
            shutil.copy2(config_file, backup_path)
            logger.info(f"Backed up config file to: {backup_path}")


def test_new_version():
    """Test new version functionality"""
    logger.info("Testing new version compatibility...")
    
    try:
        # Import new version
        from vss_enhanced_extractor_v2 import VSS_EnhancedExtractor
        from config.constants import ExtractionQuality, FIELD_NAMES
        from utils import quick_extract
        
        # Test basic functionality
        extractor = VSS_EnhancedExtractor()
        
        # Test with sample HTML
        sample_html = """
        <html>
        <body>
            <table>
                <tr><td>Điện thoại</td><td>9876543210</td></tr>
                <tr><td>Thu nhập</td><td>15,000,000 VND</td></tr>
            </table>
        </body>
        </html>
        """
        
        results = extractor.extract_enhanced_fields(sample_html)
        
        # Verify results structure
        assert 'extracted_fields' in results
        assert 'extraction_summary' in results
        assert 'quality_metrics' in results
        
        logger.info("✅ New version passes compatibility tests")
        
    except Exception as e:
        logger.error(f"❌ New version compatibility test failed: {e}")
        raise


def update_existing_scripts():
    """Update existing scripts to use new version"""
    logger.info("Updating existing scripts...")
    
    workspace_path = Path(__file__).parent
    
    # Find existing scripts that might use old version
    script_patterns = ["*collector*.py", "*test*.py", "*demo*.py", "*run*.py"]
    
    for pattern in script_patterns:
        for script_file in workspace_path.glob(pattern):
            if script_file.name != "migration_script.py":
                update_script_imports(script_file)


def update_script_imports(script_file: Path):
    """Update imports in a specific script file"""
    logger.info(f"Checking script: {script_file.name}")
    
    try:
        with open(script_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if script uses old import
        if 'from vss_enhanced_extractor import' in content or 'import vss_enhanced_extractor' in content:
            logger.info(f"Updating imports in: {script_file.name}")
            
            # Create backup
            backup_path = script_file.with_suffix('.py.backup')
            shutil.copy2(script_file, backup_path)
            
            # Update imports
            updated_content = content.replace(
                'from vss_enhanced_extractor import VSS_EnhancedExtractor',
                'from src.vss_enhanced_extractor_v2 import VSS_EnhancedExtractor'
            )
            updated_content = updated_content.replace(
                'import vss_enhanced_extractor',
                'import src.vss_enhanced_extractor_v2 as vss_enhanced_extractor'
            )
            
            # Write updated content
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info(f"✅ Updated imports in: {script_file.name}")
        
    except Exception as e:
        logger.warning(f"⚠️ Could not update {script_file.name}: {e}")


def create_compatibility_layer():
    """Create compatibility layer for backward compatibility"""
    logger.info("Creating compatibility layer...")
    
    workspace_path = Path(__file__).parent
    compat_file = workspace_path / "vss_enhanced_extractor.py"
    
    compatibility_code = '''#!/usr/bin/env python3
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
    print("=== VSS Enhanced Fields Extraction Engine Demo (Compatibility Mode) ===\\n")
    print("Note: You are using the compatibility layer. Consider upgrading to v2.1 API.\\n")
    
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
'''
    
    # Write compatibility layer
    with open(compat_file, 'w', encoding='utf-8') as f:
        f.write(compatibility_code)
    
    logger.info(f"✅ Created compatibility layer: {compat_file}")


def validate_migration():
    """Validate that migration was successful"""
    logger.info("Validating migration...")
    
    try:
        # Test old interface through compatibility layer
        from vss_enhanced_extractor import VSS_EnhancedExtractor
        
        extractor = VSS_EnhancedExtractor()
        
        sample_html = "<html><body><table><tr><td>Điện thoại</td><td>9876543210</td></tr></table></body></html>"
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            results = extractor.extract_enhanced_fields(sample_html)
        
        assert 'extracted_fields' in results
        logger.info("✅ Compatibility layer working correctly")
        
        # Test new interface directly
        from src.vss_enhanced_extractor_v2 import VSS_EnhancedExtractor as NewExtractor
        
        new_extractor = NewExtractor()
        new_results = new_extractor.extract_enhanced_fields(sample_html)
        
        assert 'extracted_fields' in new_results
        logger.info("✅ New version working correctly")
        
        logger.info("🎉 Migration validation passed!")
        
    except Exception as e:
        logger.error(f"❌ Migration validation failed: {e}")
        raise


def print_migration_summary():
    """Print migration summary and next steps"""
    
    summary = """
╔══════════════════════════════════════════════════════════════════════╗
║                    Migration Summary - v2.0 → v2.1                    ║
╚══════════════════════════════════════════════════════════════════════╝

✅ COMPLETED TASKS:
  • Backed up original v2.0 files
  • Created modular architecture with separate modules:
    - config/constants.py - Constants and enums
    - config/data_models.py - Data classes and models  
    - config/patterns.py - Extraction patterns and mappings
    - extractors/base_extractor.py - Base extraction logic
    - normalizers/field_normalizers.py - Field normalization
    - validators/field_validators.py - Field validation
    - vss_enhanced_extractor_v2.py - Main refactored extractor
    - utils.py - Utility functions and helpers
  • Created compatibility layer for backward compatibility
  • Updated existing scripts (where possible)
  • Validated migration success

📈 IMPROVEMENTS IN V2.1:
  • Modular architecture - easier to maintain and extend
  • Separated concerns - extraction, normalization, validation
  • Factory patterns for extensibility
  • Enhanced error handling and logging
  • Better type hints and documentation
  • Performance monitoring utilities
  • Multiple export formats support
  • Comprehensive validation reporting

🔄 NEXT STEPS:
  1. Review and test your existing scripts
  2. Consider migrating to new API for better features:
     ```python
     from src.vss_enhanced_extractor_v2 import VSS_EnhancedExtractor
     from src.utils import quick_extract, validate_and_export
     ```
  3. Run your tests to ensure everything works
  4. Update documentation and training materials

⚠️  COMPATIBILITY NOTES:
  • Old imports will work through compatibility layer
  • Some advanced features only available in new API
  • Deprecation warnings will guide you to new patterns
  • Performance improvements are most notable in new API

For questions or issues, refer to the migration documentation.
"""
    
    print(summary)


if __name__ == "__main__":
    try:
        migrate_to_v2()
        validate_migration()
        print_migration_summary()
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
