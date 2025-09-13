"""
Configuration file for VSS BHXH Data Collector
Cấu hình cho hệ thống thu thập dữ liệu BHXH từ VSS
"""
import os
from datetime import datetime

class VSSConfig:
    """Configuration class for VSS data collection"""
    
    # Base URLs và endpoints
    BASE_URL = "https://baohiemxahoi.gov.vn"
    LOGIN_URL = "https://baohiemxahoi.gov.vn"
    BHXH_LOOKUP_URL = "https://baohiemxahoi.gov.vn/tracuu/Pages/tra-cuu-dong-bhxh.aspx"
    
    # Proxy configuration
    PROXY_CONFIG = {
        "http": "http://ip.mproxy.vn:12301",
        "https": "http://ip.mproxy.vn:12301",
        "enabled": True
    }
    
    # Browser configuration
    BROWSER_CONFIG = {
        "headless": True,
        "disable_images": True,
        "disable_javascript": False,
        "window_size": (1920, 1080),
        "user_agent_rotation": True,
        "anti_detection": True
    }
    
    # Request configuration
    REQUEST_CONFIG = {
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 2,
        "exponential_backoff": True,
        "verify_ssl": False
    }
    
    # Data processing configuration
    DATA_CONFIG = {
        "encoding": "utf-8",
        "date_format": "%d/%m/%Y",
        "currency_format": "VND",
        "text_normalization": True,
        "validate_fields": True
    }
    
    # File paths
    PATHS = {
        "logs": "/workspace/logs",
        "data": "/workspace/data",
        "output": "/workspace/data",
        "config": "/workspace/config"
    }
    
    # Vietnamese provinces (mẫu test)
    TEST_PROVINCES = [
        {"name": "Hà Nội", "code": "01"},
        {"name": "Hồ Chí Minh", "code": "79"},
        {"name": "Đà Nẵng", "code": "48"},
        {"name": "Hải Phòng", "code": "31"},
        {"name": "Cần Thơ", "code": "92"}
    ]
    
    # Logging configuration
    LOGGING_CONFIG = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": f"{PATHS['logs']}/collection_log.txt",
        "max_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5
    }
    
    # Excel export configuration
    EXCEL_CONFIG = {
        "worksheet_names": {
            "summary": "Tổng quan",
            "detail": "Chi tiết",
            "metadata": "Thông tin thu thập"
        },
        "formatting": {
            "header_style": {
                "bold": True,
                "bg_color": "#4F81BD",
                "font_color": "#FFFFFF",
                "border": 1
            },
            "data_style": {
                "border": 1,
                "text_wrap": True
            }
        }
    }
    
    # User agents pool
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    # CSRF và session management
    SESSION_CONFIG = {
        "csrf_token_name": "_token",
        "session_cookie_name": "laravel_session",
        "maintain_session": True,
        "session_timeout": 3600  # 1 hour
    }
    
    @classmethod
    def get_timestamp(cls):
        """Get current timestamp for file naming"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @classmethod
    def get_output_filename(cls, province_name, file_type="xlsx"):
        """Generate output filename based on province and timestamp"""
        timestamp = cls.get_timestamp()
        clean_name = province_name.replace(" ", "_").lower()
        return f"bhxh_data_{clean_name}_{timestamp}.{file_type}"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for path in cls.PATHS.values():
            os.makedirs(path, exist_ok=True)

# Environment variables override
if os.getenv("VSS_PROXY_HOST"):
    VSSConfig.PROXY_CONFIG["http"] = f"http://{os.getenv('VSS_PROXY_HOST')}:{os.getenv('VSS_PROXY_PORT', '12301')}"
    VSSConfig.PROXY_CONFIG["https"] = f"http://{os.getenv('VSS_PROXY_HOST')}:{os.getenv('VSS_PROXY_PORT', '12301')}"

if os.getenv("VSS_HEADLESS") == "false":
    VSSConfig.BROWSER_CONFIG["headless"] = False
