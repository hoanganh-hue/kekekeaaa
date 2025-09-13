#!/usr/bin/env python3
"""
VSS API Client
Chuyên dụng xử lý kết nối và giao tiếp với VSS system

Author: MiniMax Agent
Date: 2025-09-13
Version: 2.0
"""

import asyncio
import aiohttp
import requests
import logging
import json
import time
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import asynccontextmanager
import urllib.parse
import ssl
import certifi

# Import configuration classes
from .config_manager import ApiConfig, ProxyConfig


class VSSApiClient:
    """
    Chuyên dụng API client để giao tiếp với VSS system
    Hỗ trợ cả synchronous và asynchronous requests
    """
    
    def __init__(self, 
                 api_config: ApiConfig, 
                 proxy_config: Optional[ProxyConfig] = None,
                 session_timeout: int = 30,
                 max_concurrent: int = 10):
        """
        Initialize VSS API Client
        
        Args:
            api_config: Cấu hình API endpoints và headers
            proxy_config: Cấu hình proxy (optional)
            session_timeout: Timeout cho mỗi request (seconds)
            max_concurrent: Số lượng request đồng thời tối đa
        """
        self.api_config = api_config
        self.proxy_config = proxy_config
        self.session_timeout = session_timeout
        self.max_concurrent = max_concurrent
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Session management
        self._aiohttp_session: Optional[aiohttp.ClientSession] = None
        self._requests_session: Optional[requests.Session] = None
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
        # Connection pooling và caching
        self._connection_pool_size = 20
        self._response_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Statistics tracking
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cached_responses': 0,
            'average_response_time': 0.0,
            'last_request_time': None
        }
        
        self.logger.info("VSS API Client initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_aiohttp_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    def __enter__(self):
        """Sync context manager entry"""
        self._ensure_requests_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit"""
        self.close_sync()
    
    async def _ensure_aiohttp_session(self):
        """Đảm bảo aiohttp session được khởi tạo"""
        if not self._aiohttp_session or self._aiohttp_session.closed:
            # SSL context với certificate verification
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            
            # Connection configuration
            connector = aiohttp.TCPConnector(
                limit=self._connection_pool_size,
                limit_per_host=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
                ssl=ssl_context,
                enable_cleanup_closed=True
            )
            
            # Request timeout configuration
            timeout = aiohttp.ClientTimeout(
                total=self.session_timeout,
                connect=10,
                sock_read=self.session_timeout
            )
            
            # Proxy configuration nếu có
            proxy_url = None
            if self.proxy_config and self.proxy_config.enabled:
                if self.proxy_config.username and self.proxy_config.password:
                    proxy_url = f"http://{self.proxy_config.username}:{self.proxy_config.password}@{self.proxy_config.host}:{self.proxy_config.port}"
                else:
                    proxy_url = f"http://{self.proxy_config.host}:{self.proxy_config.port}"
            
            self._aiohttp_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.api_config.headers,
                trust_env=True
            )
            
            self.logger.debug("AioHTTP session initialized")
    
    def _ensure_requests_session(self):
        """Đảm bảo requests session được khởi tạo"""
        if not self._requests_session:
            self._requests_session = requests.Session()
            
            # Update headers
            self._requests_session.headers.update(self.api_config.headers)
            
            # Proxy configuration
            if self.proxy_config and self.proxy_config.enabled:
                if self.proxy_config.username and self.proxy_config.password:
                    proxy_url = f"http://{self.proxy_config.username}:{self.proxy_config.password}@{self.proxy_config.host}:{self.proxy_config.port}"
                else:
                    proxy_url = f"http://{self.proxy_config.host}:{self.proxy_config.port}"
                
                self._requests_session.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            
            # SSL verification
            self._requests_session.verify = True
            
            self.logger.debug("Requests session initialized")
    
    def _build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Xây dựng URL đầy đủ từ endpoint và parameters
        
        Args:
            endpoint: API endpoint (có thể có hoặc không có leading slash)
            params: Query parameters
            
        Returns:
            URL đầy đủ
        """
        # Đảm bảo endpoint bắt đầu bằng /
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        base_url = self.api_config.base_url.rstrip('/')
        full_url = base_url + endpoint
        
        if params:
            # Encode parameters
            query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            full_url += '?' + query_string
        
        return full_url
    
    def _get_cache_key(self, method: str, url: str, params: Optional[Dict] = None) -> str:
        """Tạo cache key cho request"""
        key_parts = [method.upper(), url]
        if params:
            key_parts.append(json.dumps(params, sort_keys=True))
        return "|".join(key_parts)
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Kiểm tra cache entry còn hợp lệ không"""
        if 'timestamp' not in cache_entry:
            return False
        
        cache_time = cache_entry['timestamp']
        current_time = time.time()
        return (current_time - cache_time) < self._cache_ttl
    
    def _update_stats(self, success: bool, response_time: float):
        """Cập nhật thống kê requests"""
        self.stats['total_requests'] += 1
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
        
        # Update average response time
        current_avg = self.stats['average_response_time']
        total_requests = self.stats['total_requests']
        self.stats['average_response_time'] = (current_avg * (total_requests - 1) + response_time) / total_requests
        self.stats['last_request_time'] = datetime.now().isoformat()
    
    # =============================================================================
    # ASYNC METHODS
    # =============================================================================
    
    async def get_async(self, 
                       endpoint: str, 
                       params: Optional[Dict[str, Any]] = None,
                       headers: Optional[Dict[str, str]] = None,
                       use_cache: bool = True,
                       timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Async GET request
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            use_cache: Sử dụng cache response
            timeout: Custom timeout
            
        Returns:
            Response data hoặc None nếu lỗi
        """
        return await self._make_async_request(
            method='GET',
            endpoint=endpoint,
            params=params,
            headers=headers,
            use_cache=use_cache,
            timeout=timeout
        )
    
    async def post_async(self,
                        endpoint: str,
                        data: Optional[Dict[str, Any]] = None,
                        json_data: Optional[Dict[str, Any]] = None,
                        headers: Optional[Dict[str, str]] = None,
                        timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Async POST request
        
        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON data
            headers: Additional headers
            timeout: Custom timeout
            
        Returns:
            Response data hoặc None nếu lỗi
        """
        return await self._make_async_request(
            method='POST',
            endpoint=endpoint,
            data=data,
            json_data=json_data,
            headers=headers,
            timeout=timeout
        )
    
    async def _make_async_request(self,
                                 method: str,
                                 endpoint: str,
                                 params: Optional[Dict[str, Any]] = None,
                                 data: Optional[Dict[str, Any]] = None,
                                 json_data: Optional[Dict[str, Any]] = None,
                                 headers: Optional[Dict[str, str]] = None,
                                 use_cache: bool = False,
                                 timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Core async request method với error handling và caching
        """
        await self._ensure_aiohttp_session()
        
        # Build URL
        url = self._build_url(endpoint, params)
        
        # Check cache for GET requests
        cache_key = None
        if method.upper() == 'GET' and use_cache:
            cache_key = self._get_cache_key(method, url, params)
            if cache_key in self._response_cache:
                cache_entry = self._response_cache[cache_key]
                if self._is_cache_valid(cache_entry):
                    self.stats['cached_responses'] += 1
                    self.logger.debug(f"Cache hit for {url}")
                    return cache_entry['data']
        
        # Acquire semaphore for concurrency control
        async with self._semaphore:
            start_time = time.time()
            
            try:
                # Prepare request kwargs
                request_kwargs = {
                    'url': url,
                    'method': method.upper()
                }
                
                # Add headers
                if headers:
                    request_kwargs['headers'] = headers
                
                # Add data
                if json_data:
                    request_kwargs['json'] = json_data
                elif data:
                    request_kwargs['data'] = data
                
                # Custom timeout
                if timeout:
                    request_kwargs['timeout'] = aiohttp.ClientTimeout(total=timeout)
                
                # Make request
                async with self._aiohttp_session.request(**request_kwargs) as response:
                    # Log request
                    self.logger.debug(f"{method.upper()} {url} - Status: {response.status}")
                    
                    # Check status
                    if response.status == 200:
                        try:
                            response_data = await response.json()
                            
                            # Cache successful GET responses
                            if method.upper() == 'GET' and use_cache and cache_key:
                                self._response_cache[cache_key] = {
                                    'data': response_data,
                                    'timestamp': time.time()
                                }
                            
                            response_time = time.time() - start_time
                            self._update_stats(True, response_time)
                            
                            return response_data
                            
                        except aiohttp.ContentTypeError:
                            # Response không phải JSON
                            text_response = await response.text()
                            self.logger.warning(f"Non-JSON response from {url}: {text_response[:200]}")
                            
                            response_time = time.time() - start_time
                            self._update_stats(False, response_time)
                            return None
                    
                    elif response.status == 404:
                        self.logger.warning(f"Resource not found: {url}")
                        response_time = time.time() - start_time
                        self._update_stats(False, response_time)
                        return None
                    
                    else:
                        error_text = await response.text()
                        self.logger.error(f"HTTP {response.status} for {url}: {error_text[:200]}")
                        response_time = time.time() - start_time
                        self._update_stats(False, response_time)
                        return None
            
            except asyncio.TimeoutError:
                response_time = time.time() - start_time
                self.logger.error(f"Timeout for {url}")
                self._update_stats(False, response_time)
                return None
            
            except Exception as e:
                response_time = time.time() - start_time
                self.logger.error(f"Request error for {url}: {e}")
                self._update_stats(False, response_time)
                return None
    
    # =============================================================================
    # SYNC METHODS
    # =============================================================================
    
    def get(self, 
            endpoint: str, 
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Sync GET request
        
        Args:
            endpoint: API endpoint
            params: Query parameters  
            headers: Additional headers
            timeout: Custom timeout
            
        Returns:
            Response data hoặc None nếu lỗi
        """
        return self._make_sync_request(
            method='GET',
            endpoint=endpoint,
            params=params,
            headers=headers,
            timeout=timeout
        )
    
    def post(self,
             endpoint: str,
             data: Optional[Dict[str, Any]] = None,
             json_data: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None,
             timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Sync POST request
        
        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON data  
            headers: Additional headers
            timeout: Custom timeout
            
        Returns:
            Response data hoặc None nếu lỗi
        """
        return self._make_sync_request(
            method='POST',
            endpoint=endpoint,
            data=data,
            json_data=json_data,
            headers=headers,
            timeout=timeout
        )
    
    def _make_sync_request(self,
                          method: str,
                          endpoint: str,
                          params: Optional[Dict[str, Any]] = None,
                          data: Optional[Dict[str, Any]] = None,
                          json_data: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, str]] = None,
                          timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Core sync request method với error handling
        """
        self._ensure_requests_session()
        
        # Build URL
        url = self._build_url(endpoint, params)
        
        start_time = time.time()
        
        try:
            # Prepare request kwargs
            request_kwargs = {
                'timeout': timeout or self.session_timeout
            }
            
            # Add headers
            if headers:
                request_kwargs['headers'] = headers
            
            # Add data
            if json_data:
                request_kwargs['json'] = json_data
            elif data:
                request_kwargs['data'] = data
            
            # Make request
            response = self._requests_session.request(
                method=method.upper(),
                url=url,
                **request_kwargs
            )
            
            # Log request
            self.logger.debug(f"{method.upper()} {url} - Status: {response.status_code}")
            
            # Check status
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    response_time = time.time() - start_time
                    self._update_stats(True, response_time)
                    return response_data
                    
                except requests.exceptions.JSONDecodeError:
                    self.logger.warning(f"Non-JSON response from {url}: {response.text[:200]}")
                    response_time = time.time() - start_time
                    self._update_stats(False, response_time)
                    return None
            
            elif response.status_code == 404:
                self.logger.warning(f"Resource not found: {url}")
                response_time = time.time() - start_time
                self._update_stats(False, response_time)
                return None
            
            else:
                self.logger.error(f"HTTP {response.status_code} for {url}: {response.text[:200]}")
                response_time = time.time() - start_time
                self._update_stats(False, response_time)
                return None
        
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            self.logger.error(f"Timeout for {url}")
            self._update_stats(False, response_time)
            return None
        
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.error(f"Request error for {url}: {e}")
            self._update_stats(False, response_time)
            return None
    
    # =============================================================================
    # VSS SPECIFIC METHODS
    # =============================================================================
    
    async def get_province_data_async(self, province_code: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin tỉnh thành theo mã"""
        endpoint = f"/api/provinces/{province_code}"
        return await self.get_async(endpoint, use_cache=True)
    
    async def get_districts_async(self, province_code: str) -> Optional[List[Dict[str, Any]]]:
        """Lấy danh sách quận/huyện theo tỉnh"""
        endpoint = f"/api/provinces/{province_code}/districts"
        response = await self.get_async(endpoint, use_cache=True)
        return response.get('districts', []) if response else None
    
    async def get_wards_async(self, province_code: str) -> Optional[List[Dict[str, Any]]]:
        """Lấy danh sách phường/xã theo tỉnh"""
        endpoint = f"/api/provinces/{province_code}/wards"
        response = await self.get_async(endpoint, use_cache=True)
        return response.get('wards', []) if response else None
    
    async def get_hospitals_async(self, province_code: str) -> Optional[List[Dict[str, Any]]]:
        """Lấy danh sách bệnh viện theo tỉnh"""
        endpoint = f"/api/hospitals/{province_code}"
        response = await self.get_async(endpoint, use_cache=True)
        return response.get('hospitals', []) if response else None
    
    def get_province_data(self, province_code: str) -> Optional[Dict[str, Any]]:
        """Sync version: Lấy thông tin tỉnh thành theo mã"""
        endpoint = f"/api/provinces/{province_code}"
        return self.get(endpoint)
    
    def get_districts(self, province_code: str) -> Optional[List[Dict[str, Any]]]:
        """Sync version: Lấy danh sách quận/huyện theo tỉnh"""
        endpoint = f"/api/provinces/{province_code}/districts"
        response = self.get(endpoint)
        return response.get('districts', []) if response else None
    
    def get_wards(self, province_code: str) -> Optional[List[Dict[str, Any]]]:
        """Sync version: Lấy danh sách phường/xã theo tỉnh"""
        endpoint = f"/api/provinces/{province_code}/wards"
        response = self.get(endpoint)
        return response.get('wards', []) if response else None
    
    def get_hospitals(self, province_code: str) -> Optional[List[Dict[str, Any]]]:
        """Sync version: Lấy danh sách bệnh viện theo tỉnh"""
        endpoint = f"/api/hospitals/{province_code}"
        response = self.get(endpoint)
        return response.get('hospitals', []) if response else None
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def clear_cache(self):
        """Xóa cache"""
        self._response_cache.clear()
        self.logger.info("Response cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê performance"""
        return self.stats.copy()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Lấy thông tin cache"""
        valid_entries = 0
        expired_entries = 0
        
        for cache_entry in self._response_cache.values():
            if self._is_cache_valid(cache_entry):
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self._response_cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_ttl_seconds': self._cache_ttl
        }
    
    def cleanup_expired_cache(self):
        """Dọn dẹp cache entries đã hết hạn"""
        before_count = len(self._response_cache)
        
        expired_keys = []
        for key, cache_entry in self._response_cache.items():
            if not self._is_cache_valid(cache_entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._response_cache[key]
        
        after_count = len(self._response_cache)
        removed_count = before_count - after_count
        
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} expired cache entries")
    
    # =============================================================================
    # CLEANUP METHODS
    # =============================================================================
    
    async def close(self):
        """Đóng async session"""
        if self._aiohttp_session and not self._aiohttp_session.closed:
            await self._aiohttp_session.close()
            self.logger.debug("AioHTTP session closed")
    
    def close_sync(self):
        """Đóng sync session"""
        if self._requests_session:
            self._requests_session.close()
            self.logger.debug("Requests session closed")
    
    async def health_check(self) -> bool:
        """
        Kiểm tra kết nối tới VSS system
        
        Returns:
            True nếu kết nối thành công
        """
        try:
            # Try a simple endpoint
            result = await self.get_async("/api/health", timeout=10)
            return result is not None
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def __repr__(self):
        return f"VSSApiClient(base_url='{self.api_config.base_url}', stats={self.stats})"
