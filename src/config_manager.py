#!/usr/bin/env python3
"""
VSS Configuration Manager
Environment-based configuration system với security best practices

Author: MiniMax Agent
Date: 2025-09-12
"""

import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from dataclasses import dataclass, asdict


@dataclass
class ProxyConfig:
    """Proxy configuration structure"""
    host: str
    port: int
    username: str
    password: str
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to requests proxy format"""
        if not self.enabled:
            return {}
        
        proxy_url = f"http://{self.username}:{self.password}@{self.host}:{self.port}"
        return {
            'http': proxy_url,
            'https': proxy_url
        }


@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str
    path: str
    backup_enabled: bool = True
    backup_interval: int = 3600  # seconds
    

@dataclass
class ApiConfig:
    """API configuration"""
    base_url: str
    timeout: int = 30
    max_retries: int = 5
    rate_limit: int = 60  # requests per minute
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {
                'User-Agent': 'VSS-DataCollector/1.0',
                'Accept': 'application/json,text/html,application/xhtml+xml',
                'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
                'Connection': 'keep-alive'
            }


@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    max_concurrent_requests: int = 10
    connection_pool_size: int = 20
    cache_enabled: bool = True
    cache_ttl: int = 3600
    batch_size: int = 50
    

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = 'INFO'
    file_path: str = 'logs/vss_collector.log'
    max_file_size: str = '10MB'
    backup_count: int = 5
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    

class VSSConfigManager:
    """Comprehensive configuration manager cho VSS automation system"""
    
    def __init__(self, config_file: str = "config/vss_config.yaml"):
        """Initialize configuration manager"""
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        
        # Default configurations
        self._default_config = self._get_default_config()
        
        # Load configuration
        self.config = self._load_config()
        
        # Environment overrides
        self._apply_environment_overrides()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'proxy': asdict(ProxyConfig(
                host='ip.mproxy.vn',
                port=12301,
                username='beba111',
                password='tDV5tkMchYUBMD',
                enabled=True
            )),
            'api': asdict(ApiConfig(
                base_url='http://vssapp.teca.vn:8088/'
            )),
            'database': asdict(DatabaseConfig(
                type='sqlite',
                path='data/vss_data.db'
            )),
            'performance': asdict(PerformanceConfig()),
            'logging': asdict(LoggingConfig()),
            'data_storage': {
                'formats': ['json', 'csv', 'sqlite'],
                'directory': 'data/collected',
                'backup_enabled': True,
                'compression': True
            },
            'validation': {
                'enabled': True,
                'strict_mode': False,
                'schema_path': 'config/data_schema.json'
            },
            'monitoring': {
                'progress_updates': True,
                'metrics_enabled': True,
                'real_time_stats': True,
                'dashboard_port': 8080
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f)
                    
                # Merge với default config
                config = self._deep_merge(self._default_config, file_config)
                self.logger.info(f"Configuration loaded from {self.config_file}")
                return config
            else:
                self.logger.warning(f"Config file {self.config_file} not found, using defaults")
                return self._default_config.copy()
                
        except Exception as e:
            self.logger.error(f"Error loading config file: {e}")
            return self._default_config.copy()
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides"""
        env_mappings = {
            'VSS_PROXY_HOST': ('proxy', 'host'),
            'VSS_PROXY_PORT': ('proxy', 'port'),
            'VSS_PROXY_USER': ('proxy', 'username'),
            'VSS_PROXY_PASS': ('proxy', 'password'),
            'VSS_BASE_URL': ('api', 'base_url'),
            'VSS_DB_PATH': ('database', 'path'),
            'VSS_LOG_LEVEL': ('logging', 'level'),
            'VSS_MAX_CONCURRENT': ('performance', 'max_concurrent_requests'),
            'VSS_RATE_LIMIT': ('api', 'rate_limit')
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                if section not in self.config:
                    self.config[section] = {}
                    
                # Type conversion
                if key in ['port', 'max_concurrent_requests', 'rate_limit']:
                    value = int(value)
                elif key in ['enabled', 'backup_enabled']:
                    value = value.lower() in ['true', '1', 'yes']
                    
                self.config[section][key] = value
                self.logger.info(f"Applied environment override: {env_var}")
    
    def get_proxy_config(self) -> ProxyConfig:
        """Get proxy configuration object"""
        proxy_data = self.config.get('proxy', {})
        return ProxyConfig(**proxy_data)
    
    def get_api_config(self) -> ApiConfig:
        """Get API configuration object"""
        api_data = self.config.get('api', {})
        return ApiConfig(**api_data)
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration object"""
        db_data = self.config.get('database', {})
        return DatabaseConfig(**db_data)
    
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration object"""
        perf_data = self.config.get('performance', {})
        return PerformanceConfig(**perf_data)
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration object"""
        log_data = self.config.get('logging', {})
        return LoggingConfig(**log_data)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value với dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
    
    def save_config(self, file_path: Optional[str] = None):
        """Save current configuration to file"""
        save_path = Path(file_path) if file_path else self.config_file
        
        try:
            # Create directory if not exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
                         
            self.logger.info(f"Configuration saved to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            raise
    
    def validate_config(self) -> bool:
        """Validate configuration completeness"""
        required_sections = ['proxy', 'api', 'database', 'performance', 'logging']
        
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"Missing required config section: {section}")
                return False
                
        # Validate proxy config
        proxy_config = self.get_proxy_config()
        if proxy_config.enabled and not all([proxy_config.host, proxy_config.username, proxy_config.password]):
            self.logger.error("Incomplete proxy configuration")
            return False
            
        # Validate API config
        api_config = self.get_api_config()
        if not api_config.base_url:
            self.logger.error("Missing API base URL")
            return False
            
        self.logger.info("Configuration validation passed")
        return True
    
    def get_secrets_masked(self) -> Dict[str, Any]:
        """Get configuration với sensitive data masked"""
        masked_config = self.config.copy()
        
        # Mask sensitive fields
        if 'proxy' in masked_config:
            if 'password' in masked_config['proxy']:
                masked_config['proxy']['password'] = '***masked***'
            if 'username' in masked_config['proxy']:
                masked_config['proxy']['username'] = '***masked***'
                
        return masked_config
    
    def setup_logging(self):
        """Setup logging based on configuration"""
        log_config = self.get_logging_config()
        
        # Create logs directory
        log_path = Path(log_config.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_config.level.upper()),
            format=log_config.format,
            handlers=[
                logging.FileHandler(log_config.file_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        # Set up file rotation if needed
        if hasattr(logging.handlers, 'RotatingFileHandler'):
            file_handler = logging.handlers.RotatingFileHandler(
                log_config.file_path,
                maxBytes=self._parse_size(log_config.max_file_size),
                backupCount=log_config.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(logging.Formatter(log_config.format))
            
            # Replace file handler
            logger = logging.getLogger()
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    logger.removeHandler(handler)
            logger.addHandler(file_handler)
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes"""
        size_str = size_str.upper().strip()
        
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)


if __name__ == "__main__":
    # Example usage
    config_manager = VSSConfigManager()
    config_manager.setup_logging()
    
    if config_manager.validate_config():
        print("Configuration is valid")
        print(f"Proxy enabled: {config_manager.get_proxy_config().enabled}")
        print(f"API base URL: {config_manager.get_api_config().base_url}")
    else:
        print("Configuration validation failed")
