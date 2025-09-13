#!/usr/bin/env python3
"""
VSS Performance Optimizer
Concurrent requests, connection pooling, caching strategies

Author: MiniMax Agent
Date: 2025-09-12
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, Any, List, Optional, Callable, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import hashlib
import json
from pathlib import Path
import weakref
from functools import wraps
import psutil
import queue


@dataclass
class PerformanceMetrics:
    """Performance metrics structure"""
    request_count: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    concurrent_requests_peak: int = 0
    memory_usage_peak: float = 0.0
    cpu_usage_peak: float = 0.0
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time"""
        return self.total_response_time / max(self.request_count, 1)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        return (self.successful_requests / max(self.request_count, 1)) * 100
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total_cache_requests = self.cache_hits + self.cache_misses
        return (self.cache_hits / max(total_cache_requests, 1)) * 100


@dataclass
class RequestConfig:
    """Request configuration"""
    url: str
    method: str = 'GET'
    headers: Dict[str, str] = None
    data: Any = None
    timeout: float = 30.0
    retry_count: int = 3
    priority: int = 1  # 1 = high, 5 = low
    cache_ttl: Optional[int] = None
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.metadata is None:
            self.metadata = {}


class CacheManager:
    """Intelligent caching system"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.access_times = {}
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        
        # Cache statistics
        self.hits = 0
        self.misses = 0
        
    def _generate_key(self, url: str, method: str, data: Any = None) -> str:
        """Generate cache key"""
        key_data = f"{method}:{url}"
        if data:
            key_data += f":{json.dumps(data, sort_keys=True)}"
        return hashlib.sha256(key_data.encode('utf-8')).hexdigest()
    
    def get(self, url: str, method: str = 'GET', data: Any = None) -> Optional[Any]:
        """Get cached response"""
        key = self._generate_key(url, method, data)
        
        with self.lock:
            if key in self.cache:
                cached_item = self.cache[key]
                
                # Check if expired
                if cached_item['expires_at'] > time.time():
                    self.access_times[key] = time.time()
                    self.hits += 1
                    self.logger.debug(f"Cache hit for {url}")
                    return cached_item['data']
                else:
                    # Remove expired item
                    del self.cache[key]
                    del self.access_times[key]
            
            self.misses += 1
            return None
    
    def set(self, url: str, data: Any, method: str = 'GET', 
           request_data: Any = None, ttl: Optional[int] = None):
        """Cache response data"""
        key = self._generate_key(url, method, request_data)
        ttl = ttl or self.default_ttl
        
        with self.lock:
            # Evict old items if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            self.cache[key] = {
                'data': data,
                'created_at': time.time(),
                'expires_at': time.time() + ttl,
                'access_count': 1
            }
            self.access_times[key] = time.time()
            
            self.logger.debug(f"Cached response for {url} (TTL: {ttl}s)")
    
    def _evict_lru(self):
        """Evict least recently used items"""
        if not self.access_times:
            return
            
        # Find oldest accessed item
        oldest_key = min(self.access_times.keys(), 
                        key=lambda k: self.access_times[k])
        
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
        
        self.logger.debug(f"Evicted LRU cache item: {oldest_key[:16]}...")
    
    def clear(self):
        """Clear all cached items"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.hits = 0
            self.misses = 0
            
        self.logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / max(total_requests, 1)) * 100
            
            return {
                'cache_size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'memory_usage': len(json.dumps(self.cache).encode('utf-8'))
            }


class ConnectionPool:
    """HTTP connection pool manager"""
    
    def __init__(self, max_connections: int = 100, max_connections_per_host: int = 30):
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self.logger = logging.getLogger(__name__)
        
        # Connection pool configuration
        self.connector_config = {
            'limit': max_connections,
            'limit_per_host': max_connections_per_host,
            'ttl_dns_cache': 300,
            'use_dns_cache': True,
            'keepalive_timeout': 30,
            'enable_cleanup_closed': True
        }
        
        self._session = None
        self._session_lock = threading.Lock()
    
    async def get_session(self, proxy_config: Optional[Dict[str, str]] = None) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self._session is None or self._session.closed:
            with self._session_lock:
                if self._session is None or self._session.closed:
                    connector = aiohttp.TCPConnector(**self.connector_config)
                    
                    timeout = aiohttp.ClientTimeout(total=30, connect=10)
                    
                    self._session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=timeout,
                        trust_env=True
                    )
                    
                    self.logger.info("Created new HTTP session với connection pool")
        
        return self._session
    
    async def close(self):
        """Close connection pool"""
        if self._session and not self._session.closed:
            await self._session.close()
            self.logger.info("Closed HTTP connection pool")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        if self._session and not self._session.closed:
            connector = self._session.connector
            return {
                'max_connections': self.max_connections,
                'max_connections_per_host': self.max_connections_per_host,
                'active_connections': len(connector._conns),
                'acquired_connections': len(connector._acquired),
                'session_closed': self._session.closed
            }
        else:
            return {
                'max_connections': self.max_connections,
                'max_connections_per_host': self.max_connections_per_host,
                'active_connections': 0,
                'acquired_connections': 0,
                'session_closed': True
            }


class RequestQueue:
    """Priority-based request queue"""
    
    def __init__(self, max_size: int = 1000):
        self.queue = queue.PriorityQueue(maxsize=max_size)
        self.pending_requests = set()
        self.completed_requests = 0
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def add_request(self, request_config: RequestConfig) -> bool:
        """Add request to queue"""
        try:
            # Create priority tuple (priority, timestamp, request)
            priority_item = (
                request_config.priority,
                time.time(),
                request_config
            )
            
            self.queue.put_nowait(priority_item)
            
            with self.lock:
                self.pending_requests.add(id(request_config))
            
            self.logger.debug(f"Added request to queue: {request_config.url}")
            return True
            
        except queue.Full:
            self.logger.warning(f"Request queue is full, dropping request: {request_config.url}")
            return False
    
    def get_request(self, timeout: Optional[float] = None) -> Optional[RequestConfig]:
        """Get next request from queue"""
        try:
            priority, timestamp, request_config = self.queue.get(timeout=timeout)
            
            with self.lock:
                self.pending_requests.discard(id(request_config))
            
            return request_config
            
        except queue.Empty:
            return None
    
    def mark_completed(self):
        """Mark request as completed"""
        with self.lock:
            self.completed_requests += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            return {
                'queue_size': self.queue.qsize(),
                'pending_requests': len(self.pending_requests),
                'completed_requests': self.completed_requests,
                'queue_full': self.queue.full()
            }


class VSSPerformanceOptimizer:
    """Comprehensive performance optimizer cho VSS data collection"""
    
    def __init__(self, max_concurrent_requests: int = 10, 
                 connection_pool_size: int = 50,
                 cache_size: int = 1000, cache_ttl: int = 3600):
        """Initialize performance optimizer"""
        self.max_concurrent_requests = max_concurrent_requests
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.cache_manager = CacheManager(max_size=cache_size, default_ttl=cache_ttl)
        self.connection_pool = ConnectionPool(
            max_connections=connection_pool_size,
            max_connections_per_host=connection_pool_size // 3
        )
        self.request_queue = RequestQueue(max_size=max_concurrent_requests * 10)
        
        # Performance metrics
        self.metrics = PerformanceMetrics()
        self.active_requests = set()
        self.metrics_lock = threading.Lock()
        
        # Rate limiting
        self.rate_limiter = {
            'requests_per_minute': 60,
            'request_timestamps': [],
            'lock': threading.Lock()
        }
        
        # Adaptive performance tuning
        self.adaptive_config = {
            'enabled': True,
            'adjustment_interval': 60,  # seconds
            'last_adjustment': time.time(),
            'performance_history': []
        }
        
        # Background tasks
        self._running = False
        self._worker_tasks = []
        
    async def start_workers(self):
        """Start background worker tasks"""
        self._running = True
        
        # Start request workers
        for i in range(self.max_concurrent_requests):
            task = asyncio.create_task(self._request_worker(f"worker-{i}"))
            self._worker_tasks.append(task)
        
        # Start monitoring task
        monitor_task = asyncio.create_task(self._performance_monitor())
        self._worker_tasks.append(monitor_task)
        
        self.logger.info(f"Started {len(self._worker_tasks)} worker tasks")
    
    async def stop_workers(self):
        """Stop background worker tasks"""
        self._running = False
        
        # Cancel all tasks
        for task in self._worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        
        # Close connection pool
        await self.connection_pool.close()
        
        self._worker_tasks.clear()
        self.logger.info("Stopped all worker tasks")
    
    async def _request_worker(self, worker_name: str):
        """Background request worker"""
        self.logger.info(f"Started request worker: {worker_name}")
        
        while self._running:
            try:
                # Get request from queue
                request_config = self.request_queue.get_request(timeout=1.0)
                
                if request_config is None:
                    continue
                
                # Process request
                await self._process_request(request_config, worker_name)
                
            except Exception as e:
                self.logger.error(f"Error in request worker {worker_name}: {e}")
                await asyncio.sleep(1.0)
        
        self.logger.info(f"Stopped request worker: {worker_name}")
    
    async def _process_request(self, request_config: RequestConfig, worker_name: str):
        """Process single request"""
        start_time = time.time()
        request_id = id(request_config)
        
        with self.metrics_lock:
            self.active_requests.add(request_id)
            self.metrics.concurrent_requests_peak = max(
                self.metrics.concurrent_requests_peak,
                len(self.active_requests)
            )
        
        try:
            # Check rate limiting
            if not self._check_rate_limit():
                self.logger.warning(f"Rate limit exceeded, delaying request: {request_config.url}")
                await asyncio.sleep(1.0)
            
            # Check cache first
            cached_response = self.cache_manager.get(
                request_config.url, 
                request_config.method, 
                request_config.data
            )
            
            if cached_response is not None:
                with self.metrics_lock:
                    self.metrics.cache_hits += 1
                
                # Execute callback if provided
                if request_config.callback:
                    await self._execute_callback(request_config.callback, cached_response, request_config)
                
                return cached_response
            
            # Make HTTP request
            response_data = await self._make_http_request(request_config)
            
            # Cache response if successful
            if response_data is not None:
                self.cache_manager.set(
                    request_config.url,
                    response_data,
                    request_config.method,
                    request_config.data,
                    request_config.cache_ttl
                )
                
                with self.metrics_lock:
                    self.metrics.cache_misses += 1
                    self.metrics.successful_requests += 1
                
                # Execute callback if provided
                if request_config.callback:
                    await self._execute_callback(request_config.callback, response_data, request_config)
            else:
                with self.metrics_lock:
                    self.metrics.failed_requests += 1
            
        except Exception as e:
            self.logger.error(f"Error processing request {request_config.url}: {e}")
            with self.metrics_lock:
                self.metrics.failed_requests += 1
        
        finally:
            # Update metrics
            response_time = time.time() - start_time
            
            with self.metrics_lock:
                self.active_requests.discard(request_id)
                self.metrics.request_count += 1
                self.metrics.total_response_time += response_time
                self.metrics.min_response_time = min(self.metrics.min_response_time, response_time)
                self.metrics.max_response_time = max(self.metrics.max_response_time, response_time)
            
            self.request_queue.mark_completed()
            
            self.logger.debug(f"Completed request {request_config.url} in {response_time:.2f}s")
    
    async def _make_http_request(self, request_config: RequestConfig) -> Optional[Any]:
        """Make HTTP request với retry logic"""
        session = await self.connection_pool.get_session()
        
        for attempt in range(request_config.retry_count + 1):
            try:
                async with session.request(
                    method=request_config.method,
                    url=request_config.url,
                    headers=request_config.headers,
                    data=request_config.data,
                    timeout=aiohttp.ClientTimeout(total=request_config.timeout)
                ) as response:
                    
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        
                        if 'application/json' in content_type:
                            return await response.json()
                        else:
                            return await response.text()
                    
                    elif response.status in [429, 503]:  # Rate limited or service unavailable
                        retry_after = int(response.headers.get('retry-after', 5))
                        await asyncio.sleep(min(retry_after, 30))  # Cap at 30 seconds
                        continue
                    
                    else:
                        self.logger.warning(f"HTTP {response.status} for {request_config.url}")
                        if attempt < request_config.retry_count:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        else:
                            return None
            
            except asyncio.TimeoutError:
                if attempt < request_config.retry_count:
                    self.logger.warning(f"Timeout on attempt {attempt + 1} for {request_config.url}")
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    self.logger.error(f"Final timeout for {request_config.url}")
                    return None
            
            except Exception as e:
                if attempt < request_config.retry_count:
                    self.logger.warning(f"Request error on attempt {attempt + 1}: {e}")
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    self.logger.error(f"Final request error for {request_config.url}: {e}")
                    return None
        
        return None
    
    async def _execute_callback(self, callback: Callable, response_data: Any, request_config: RequestConfig):
        """Execute callback function safely"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(response_data, request_config)
            else:
                callback(response_data, request_config)
        except Exception as e:
            self.logger.error(f"Error in callback for {request_config.url}: {e}")
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        with self.rate_limiter['lock']:
            # Clean old timestamps
            cutoff_time = current_time - 60  # 1 minute ago
            self.rate_limiter['request_timestamps'] = [
                ts for ts in self.rate_limiter['request_timestamps'] 
                if ts > cutoff_time
            ]
            
            # Check rate limit
            if len(self.rate_limiter['request_timestamps']) >= self.rate_limiter['requests_per_minute']:
                return False
            
            # Add current request timestamp
            self.rate_limiter['request_timestamps'].append(current_time)
            return True
    
    async def _performance_monitor(self):
        """Monitor performance và adjust settings"""
        self.logger.info("Started performance monitor")
        
        while self._running:
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
                # Collect system metrics
                cpu_percent = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()
                
                with self.metrics_lock:
                    self.metrics.cpu_usage_peak = max(self.metrics.cpu_usage_peak, cpu_percent)
                    self.metrics.memory_usage_peak = max(self.metrics.memory_usage_peak, memory_info.percent)
                
                # Adaptive performance adjustment
                if self.adaptive_config['enabled']:
                    await self._adjust_performance_settings()
                
                # Log performance summary
                self.logger.info(
                    f"Performance: Requests={self.metrics.request_count}, "
                    f"Success={self.metrics.success_rate:.1f}%, "
                    f"Avg Response={self.metrics.average_response_time:.2f}s, "
                    f"Cache Hit={self.metrics.cache_hit_rate:.1f}%, "
                    f"CPU={cpu_percent:.1f}%, Memory={memory_info.percent:.1f}%"
                )
                
            except Exception as e:
                self.logger.error(f"Error in performance monitor: {e}")
        
        self.logger.info("Stopped performance monitor")
    
    async def _adjust_performance_settings(self):
        """Adaptively adjust performance settings"""
        current_time = time.time()
        
        # Only adjust every minute
        if current_time - self.adaptive_config['last_adjustment'] < self.adaptive_config['adjustment_interval']:
            return
        
        self.adaptive_config['last_adjustment'] = current_time
        
        # Analyze recent performance
        with self.metrics_lock:
            current_metrics = {
                'success_rate': self.metrics.success_rate,
                'avg_response_time': self.metrics.average_response_time,
                'cache_hit_rate': self.metrics.cache_hit_rate,
                'active_requests': len(self.active_requests)
            }
        
        self.adaptive_config['performance_history'].append(current_metrics)
        
        # Keep only last 10 measurements
        if len(self.adaptive_config['performance_history']) > 10:
            self.adaptive_config['performance_history'] = self.adaptive_config['performance_history'][-10:]
        
        # Adjust settings based on performance
        if len(self.adaptive_config['performance_history']) >= 3:
            recent_avg_response = sum(h['avg_response_time'] for h in self.adaptive_config['performance_history'][-3:]) / 3
            recent_success_rate = sum(h['success_rate'] for h in self.adaptive_config['performance_history'][-3:]) / 3
            
            # If response time is high and success rate is good, increase concurrency
            if recent_avg_response < 2.0 and recent_success_rate > 90:
                if self.max_concurrent_requests < 20:
                    self.max_concurrent_requests += 1
                    self.logger.info(f"Increased concurrency to {self.max_concurrent_requests}")
            
            # If success rate is low, decrease concurrency
            elif recent_success_rate < 70:
                if self.max_concurrent_requests > 5:
                    self.max_concurrent_requests -= 1
                    self.logger.info(f"Decreased concurrency to {self.max_concurrent_requests}")
    
    def add_request(self, request_config: RequestConfig) -> bool:
        """Add request to processing queue"""
        return self.request_queue.add_request(request_config)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        with self.metrics_lock:
            metrics_dict = asdict(self.metrics)
        
        # Add additional metrics
        queue_stats = self.request_queue.get_stats()
        cache_stats = self.cache_manager.get_stats()
        connection_stats = self.connection_pool.get_stats()
        
        return {
            'core_metrics': metrics_dict,
            'queue_stats': queue_stats,
            'cache_stats': cache_stats,
            'connection_stats': connection_stats,
            'rate_limiting': {
                'requests_per_minute': self.rate_limiter['requests_per_minute'],
                'current_minute_requests': len(self.rate_limiter['request_timestamps'])
            },
            'adaptive_config': {
                'max_concurrent_requests': self.max_concurrent_requests,
                'performance_history_length': len(self.adaptive_config['performance_history'])
            }
        }
    
    def reset_metrics(self):
        """Reset performance metrics"""
        with self.metrics_lock:
            self.metrics = PerformanceMetrics()
        
        self.cache_manager.clear()
        self.logger.info("Performance metrics reset")
    
    def save_performance_report(self, output_path: str):
        """Save detailed performance report"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'performance_metrics': self.get_performance_metrics(),
                'system_info': {
                    'cpu_count': psutil.cpu_count(),
                    'memory_total': psutil.virtual_memory().total,
                    'memory_available': psutil.virtual_memory().available
                }
            }
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Performance report saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving performance report: {e}")
            raise


if __name__ == "__main__":
    # Example usage
    async def main():
        optimizer = VSSPerformanceOptimizer(
            max_concurrent_requests=5,
            connection_pool_size=20,
            cache_size=100
        )
        
        await optimizer.start_workers()
        
        # Add some test requests
        test_requests = [
            RequestConfig(url="http://httpbin.org/delay/1", metadata={'test': 'request1'}),
            RequestConfig(url="http://httpbin.org/delay/2", metadata={'test': 'request2'}),
            RequestConfig(url="http://httpbin.org/json", cache_ttl=60)
        ]
        
        for req in test_requests:
            optimizer.add_request(req)
        
        # Wait for processing
        await asyncio.sleep(10)
        
        # Get metrics
        metrics = optimizer.get_performance_metrics()
        print(json.dumps(metrics, indent=2))
        
        await optimizer.stop_workers()
    
    # Run example
    # asyncio.run(main())
    print("VSSPerformanceOptimizer initialized successfully")
