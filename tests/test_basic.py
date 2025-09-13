#!/usr/bin/env python3
"""
Test cases cơ bản cho hệ thống VSS
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_manager import ConfigManager
from src.data_validator import DataValidator

class TestVSSBasics(unittest.TestCase):
    """Test cases cơ bản"""
    
    def setUp(self):
        """Setup test"""
        self.config = ConfigManager()
        self.validator = DataValidator()
    
    def test_cccd_validation(self):
        """Test validation CCCD"""
        # CCCD hợp lệ
        valid_cccd = "031173005014"
        self.assertTrue(self.validator.is_valid_cccd(valid_cccd))
        
        # CCCD không hợp lệ
        invalid_cccd = "123"
        self.assertFalse(self.validator.is_valid_cccd(invalid_cccd))
        
        # CCCD có ký tự đặc biệt
        special_cccd = "031-173-005-014"
        self.assertFalse(self.validator.is_valid_cccd(special_cccd))
    
    def test_config_loading(self):
        """Test loading configuration"""
        self.assertIsNotNone(self.config)
        self.assertTrue(hasattr(self.config, 'vss_config'))
    
    def test_haiphong_cccd_detection(self):
        """Test detection CCCD Hải Phòng"""
        haiphong_cccd = "031173005014"
        self.assertTrue(self.validator.is_haiphong_cccd(haiphong_cccd))
        
        hanoi_cccd = "001173005014"
        self.assertFalse(self.validator.is_haiphong_cccd(hanoi_cccd))
    
    def test_data_structure_validation(self):
        """Test validation cấu trúc dữ liệu"""
        valid_data = {
            'cccd': '031173005014',
            'ho_ten': 'NGUYỄN VĂN A',
            'ma_bhxh': 'DN-031173005014',
            'trang_thai': 'Đang tham gia'
        }
        
        self.assertTrue(self.validator.validate_bhxh_data(valid_data))
        
        # Dữ liệu thiếu field
        invalid_data = {
            'cccd': '031173005014'
        }
        
        self.assertFalse(self.validator.validate_bhxh_data(invalid_data))

class TestVSSIntegration(unittest.TestCase):
    """Test integration với VSS"""
    
    def test_vss_url_access(self):
        """Test kết nối đến VSS URL"""
        import requests
        
        try:
            response = requests.get('https://baohiemxahoi.gov.vn', timeout=10)
            self.assertEqual(response.status_code, 200)
        except requests.RequestException:
            self.skipTest("Cannot connect to VSS website")
    
    def test_lookup_url_format(self):
        """Test format URL tra cứu"""
        base_url = "https://baohiemxahoi.gov.vn"
        lookup_path = "/tracuu/Pages/tra-cuu-dong-bhxh.aspx"
        
        full_url = base_url + lookup_path
        self.assertTrue(full_url.startswith("https://"))
        self.assertIn("tracuu", full_url)

if __name__ == '__main__':
    # Chạy tất cả test cases
    unittest.main(verbosity=2)
