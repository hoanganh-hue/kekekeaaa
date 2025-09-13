#!/usr/bin/env python3
"""
VSS Error Handler
Multi-tier error handling với exponential backoff và intelligent retry logic

Author: MiniMax Agent
Date: 2025-09-12
"""

import asyncio
import time
import random
import logging
from typing import Dict, Any, Optional, Callable, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path
import traceback
from datetime import datetime, timedelta


class ErrorType(Enum):
    """Error type classification"""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    RATE_LIMITING = "rate_limiting"
    DATA_VALIDATION = "data_validation"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    PROXY = "proxy"
    UNKNOWN = "unknown"


class BackoffStrategy(Enum):
    """Backoff strategy types"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIBONACCI = "fibonacci"
    POLYNOMIAL = "polynomial"
    JITTERED = "jittered"
    DECORRELATED = "decorrelated"


class RetryAction(Enum):
    """Retry action types"""
    RETRY = "retry"
    SKIP = "skip"
    ABORT = "abort"
    REFRESH_AUTH = "refresh_auth"
    ROTATE_PROXY = "rotate_proxy"
    ALTERNATIVE_ENDPOINT = "alternative_endpoint"


@dataclass
class ErrorConfig:
    """Error handling configuration"""
    error_type: ErrorType
    error_code: str
    retry: bool
    backoff_strategy: BackoffStrategy
    max_retries: int
    base_delay: float
    max_delay: float
    action: RetryAction
    jitter: bool = True
    

@dataclass
class ErrorContext:
    """Error context information"""
    url: str
    method: str
    province_code: Optional[str]
    attempt: int
    total_attempts: int
    error_message: str
    status_code: Optional[int]
    response_headers: Dict[str, str]
    timestamp: str
    processing_time: float
    

@dataclass  
class RetryResult:
    """Retry operation result"""
    success: bool
    action_taken: RetryAction
    delay_applied: float
    attempts_made: int
    final_error: Optional[str]
    recovery_data: Optional[Dict[str, Any]]
    

class VSSErrorHandler:
    """Comprehensive error handler với intelligent retry mechanisms"""
    
    def __init__(self, config_path: str = "config/error_config.json"):
        """Initialize error handler"""
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Error configurations
        self.error_configs = self._load_error_configs()
        
        # Error statistics
        self.error_stats = {
            'total_errors': 0,
            'by_type': {error_type.value: 0 for error_type in ErrorType},
            'by_status_code': {},
            'retry_attempts': 0,
            'successful_recoveries': 0,
            'permanent_failures': 0
        }
        
        # Recovery state
        self.recovery_state = {
            'auth_token': None,
            'proxy_rotation_index': 0,
            'rate_limit_reset_time': None,
            'circuit_breaker_state': 'closed'  # closed, open, half-open
        }
        
        # Fibonacci sequence for fibonacci backoff
        self.fibonacci_sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        
    def _load_error_configs(self) -> Dict[str, ErrorConfig]:
        """Load error handling configurations"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return self._parse_error_configs(config_data)
            else:
                self.logger.warning(f"Error config file not found: {self.config_path}")
                return self._get_default_error_configs()
                
        except Exception as e:
            self.logger.error(f"Error loading error configs: {e}")
            return self._get_default_error_configs()
    
    def _get_default_error_configs(self) -> Dict[str, ErrorConfig]:
        """Get default error handling configurations"""
        configs = {
            # Network errors
            'connection_timeout': ErrorConfig(
                error_type=ErrorType.NETWORK,
                error_code='connection_timeout',
                retry=True,
                backoff_strategy=BackoffStrategy.EXPONENTIAL,
                max_retries=5,
                base_delay=1.0,
                max_delay=300.0,
                action=RetryAction.RETRY
            ),
            'connection_refused': ErrorConfig(
                error_type=ErrorType.NETWORK,
                error_code='connection_refused',
                retry=True,
                backoff_strategy=BackoffStrategy.LINEAR,
                max_retries=3,
                base_delay=2.0,
                max_delay=60.0,
                action=RetryAction.RETRY
            ),
            'dns_failure': ErrorConfig(
                error_type=ErrorType.NETWORK,
                error_code='dns_failure',
                retry=True,
                backoff_strategy=BackoffStrategy.EXPONENTIAL,
                max_retries=2,
                base_delay=5.0,
                max_delay=120.0,
                action=RetryAction.RETRY
            ),
            
            # Authentication errors
            'invalid_credentials': ErrorConfig(
                error_type=ErrorType.AUTHENTICATION,
                error_code='invalid_credentials',
                retry=False,
                backoff_strategy=BackoffStrategy.LINEAR,
                max_retries=0,
                base_delay=0.0,
                max_delay=0.0,
                action=RetryAction.REFRESH_AUTH
            ),
            'token_expired': ErrorConfig(
                error_type=ErrorType.AUTHENTICATION,
                error_code='token_expired',
                retry=True,
                backoff_strategy=BackoffStrategy.LINEAR,
                max_retries=1,
                base_delay=1.0,
                max_delay=5.0,
                action=RetryAction.REFRESH_AUTH
            ),
            'session_timeout': ErrorConfig(
                error_type=ErrorType.AUTHENTICATION,
                error_code='session_timeout',
                retry=True,
                backoff_strategy=BackoffStrategy.LINEAR,
                max_retries=2,
                base_delay=2.0,
                max_delay=10.0,
                action=RetryAction.REFRESH_AUTH
            ),
            
            # Rate limiting errors
            'too_many_requests': ErrorConfig(
                error_type=ErrorType.RATE_LIMITING,
                error_code='too_many_requests',
                retry=True,
                backoff_strategy=BackoffStrategy.EXPONENTIAL,
                max_retries=10,
                base_delay=5.0,
                max_delay=900.0,
                action=RetryAction.RETRY
            ),
            'daily_limit_exceeded': ErrorConfig(
                error_type=ErrorType.RATE_LIMITING,
                error_code='daily_limit_exceeded',
                retry=False,
                backoff_strategy=BackoffStrategy.LINEAR,
                max_retries=0,
                base_delay=0.0,
                max_delay=0.0,
                action=RetryAction.ABORT
            ),
            
            # Server errors
            '500_internal_error': ErrorConfig(
                error_type=ErrorType.SERVER_ERROR,
                error_code='500_internal_error',
                retry=True,
                backoff_strategy=BackoffStrategy.EXPONENTIAL,
                max_retries=3,
                base_delay=2.0,
                max_delay=180.0,
                action=RetryAction.RETRY
            ),
            '502_bad_gateway': ErrorConfig(
                error_type=ErrorType.SERVER_ERROR,
                error_code='502_bad_gateway',
                retry=True,
                backoff_strategy=BackoffStrategy.LINEAR,
                max_retries=5,
                base_delay=3.0,
                max_delay=300.0,
                action=RetryAction.RETRY
            ),
            '503_service_unavailable': ErrorConfig(
                error_type=ErrorType.SERVER_ERROR,
                error_code='503_service_unavailable',
                retry=True,
                backoff_strategy=BackoffStrategy.EXPONENTIAL,
                max_retries=8,
                base_delay=5.0,
                max_delay=600.0,
                action=RetryAction.RETRY
            ),
            
            # Proxy errors
            'proxy_connection_failed': ErrorConfig(
                error_type=ErrorType.PROXY,
                error_code='proxy_connection_failed',
                retry=True,
                backoff_strategy=BackoffStrategy.LINEAR,
                max_retries=2,
                base_delay=1.0,
                max_delay=10.0,
                action=RetryAction.ROTATE_PROXY
            )
        }
        
        return configs
    
    def _parse_error_configs(self, config_data: Dict) -> Dict[str, ErrorConfig]:
        """Parse error configurations from JSON data"""
        configs = {}
        
        for key, config in config_data.items():
            configs[key] = ErrorConfig(
                error_type=ErrorType(config['error_type']),
                error_code=config['error_code'],
                retry=config['retry'],
                backoff_strategy=BackoffStrategy(config['backoff_strategy']),
                max_retries=config['max_retries'],
                base_delay=config['base_delay'],
                max_delay=config['max_delay'],
                action=RetryAction(config['action']),
                jitter=config.get('jitter', True)
            )
            
        return configs
    
    def classify_error(self, exception: Exception, status_code: Optional[int] = None, 
                      response_headers: Optional[Dict[str, str]] = None) -> Tuple[ErrorType, str]:
        """Classify error type và determine error code"""
        error_str = str(exception).lower()
        
        # Network errors
        if any(keyword in error_str for keyword in ['timeout', 'timed out']):
            return ErrorType.TIMEOUT, 'connection_timeout'
        elif any(keyword in error_str for keyword in ['connection refused', 'connection error']):
            return ErrorType.NETWORK, 'connection_refused'
        elif any(keyword in error_str for keyword in ['dns', 'name resolution']):
            return ErrorType.NETWORK, 'dns_failure'
        elif any(keyword in error_str for keyword in ['proxy', 'tunnel']):
            return ErrorType.PROXY, 'proxy_connection_failed'
        
        # Status code based classification
        if status_code:
            if status_code == 401:
                return ErrorType.AUTHENTICATION, 'invalid_credentials'
            elif status_code == 403:
                return ErrorType.AUTHENTICATION, 'token_expired'
            elif status_code == 429:
                return ErrorType.RATE_LIMITING, 'too_many_requests'
            elif status_code == 500:
                return ErrorType.SERVER_ERROR, '500_internal_error'
            elif status_code == 502:
                return ErrorType.SERVER_ERROR, '502_bad_gateway'
            elif status_code == 503:
                return ErrorType.SERVER_ERROR, '503_service_unavailable'
            elif status_code == 504:
                return ErrorType.TIMEOUT, 'gateway_timeout'
        
        # Response header analysis
        if response_headers:
            if 'retry-after' in response_headers:
                return ErrorType.RATE_LIMITING, 'too_many_requests'
        
        return ErrorType.UNKNOWN, 'unknown_error'
    
    def calculate_delay(self, config: ErrorConfig, attempt: int) -> float:
        """Calculate delay based on backoff strategy"""
        base_delay = config.base_delay
        
        if config.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = base_delay * (2 ** (attempt - 1))
        elif config.backoff_strategy == BackoffStrategy.LINEAR:
            delay = base_delay * attempt
        elif config.backoff_strategy == BackoffStrategy.FIBONACCI:
            fib_index = min(attempt - 1, len(self.fibonacci_sequence) - 1)
            delay = base_delay * self.fibonacci_sequence[fib_index]
        elif config.backoff_strategy == BackoffStrategy.POLYNOMIAL:
            delay = base_delay * (attempt ** 2)
        elif config.backoff_strategy == BackoffStrategy.JITTERED:
            exponential_delay = base_delay * (2 ** (attempt - 1))
            jitter = random.uniform(0.5, 1.5)
            delay = exponential_delay * jitter
        elif config.backoff_strategy == BackoffStrategy.DECORRELATED:
            if attempt == 1:
                delay = base_delay
            else:
                # Decorrelated jitter formula
                prev_delay = base_delay * (2 ** (attempt - 2))
                delay = random.uniform(base_delay, prev_delay * 3)
        else:
            delay = base_delay
        
        # Apply jitter if enabled
        if config.jitter and config.backoff_strategy not in [BackoffStrategy.JITTERED, BackoffStrategy.DECORRELATED]:
            jitter_factor = random.uniform(0.8, 1.2)
            delay *= jitter_factor
        
        # Respect max delay
        return min(delay, config.max_delay)
    
    async def handle_error_async(self, exception: Exception, context: ErrorContext, 
                           retry_callback: Optional[Callable] = None) -> RetryResult:
        """Handle error asynchronously với intelligent retry logic"""
        error_type, error_code = self.classify_error(
            exception, context.status_code, context.response_headers
        )
        
        # Update statistics
        self._update_error_stats(error_type, context.status_code)
        
        # Get error configuration
        config = self.error_configs.get(error_code, self._get_fallback_config(error_type))
        
        self.logger.warning(
            f"Error handling {error_code} for {context.province_code}: {exception}"
        )
        
        # Check if retry is allowed
        if not config.retry or context.attempt >= config.max_retries:
            return RetryResult(
                success=False,
                action_taken=RetryAction.ABORT,
                delay_applied=0.0,
                attempts_made=context.attempt,
                final_error=str(exception),
                recovery_data=None
            )
        
        # Execute recovery action
        recovery_data = await self._execute_recovery_action(config.action, context)
        
        # Calculate delay
        delay = self.calculate_delay(config, context.attempt)
        
        self.logger.info(
            f"Retrying {context.province_code} after {delay:.2f}s (attempt {context.attempt}/{config.max_retries})"
        )
        
        # Apply delay
        await asyncio.sleep(delay)
        
        # Execute retry if callback provided
        if retry_callback:
            try:
                result = await retry_callback()
                return RetryResult(
                    success=True,
                    action_taken=config.action,
                    delay_applied=delay,
                    attempts_made=context.attempt,
                    final_error=None,
                    recovery_data=recovery_data
                )
            except Exception as retry_error:
                # Recursive retry handling
                new_context = ErrorContext(
                    url=context.url,
                    method=context.method,
                    province_code=context.province_code,
                    attempt=context.attempt + 1,
                    total_attempts=context.total_attempts,
                    error_message=str(retry_error),
                    status_code=getattr(retry_error, 'status_code', None),
                    response_headers=getattr(retry_error, 'response_headers', {}),
                    timestamp=datetime.now().isoformat(),
                    processing_time=0.0
                )
                
                return await self.handle_error_async(retry_error, new_context, retry_callback)
        
        return RetryResult(
            success=False,
            action_taken=config.action,
            delay_applied=delay,
            attempts_made=context.attempt,
            final_error=str(exception),
            recovery_data=recovery_data
        )
    
    def handle_error_sync(self, exception: Exception, context: ErrorContext) -> RetryResult:
        """Synchronous error handling wrapper"""
        return asyncio.run(self.handle_error_async(exception, context))
    
    async def _execute_recovery_action(self, action: RetryAction, context: ErrorContext) -> Optional[Dict[str, Any]]:
        """Execute recovery action based on error type"""
        recovery_data = {}
        
        try:
            if action == RetryAction.REFRESH_AUTH:
                recovery_data = await self._refresh_authentication(context)
            elif action == RetryAction.ROTATE_PROXY:
                recovery_data = await self._rotate_proxy(context)
            elif action == RetryAction.ALTERNATIVE_ENDPOINT:
                recovery_data = await self._find_alternative_endpoint(context)
            elif action == RetryAction.RETRY:
                # No special action needed, just retry
                pass
            elif action == RetryAction.SKIP:
                self.logger.info(f"Skipping {context.province_code} due to error")
            elif action == RetryAction.ABORT:
                self.logger.error(f"Aborting processing for {context.province_code}")
            
            return recovery_data
            
        except Exception as e:
            self.logger.error(f"Recovery action {action} failed: {e}")
            return None
    
    async def _refresh_authentication(self, context: ErrorContext) -> Dict[str, Any]:
        """Refresh authentication credentials"""
        self.logger.info("Refreshing authentication credentials")
        
        # Implementation sẽ depend on authentication mechanism
        # For now, return placeholder
        return {
            'action': 'auth_refresh',
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
    
    async def _rotate_proxy(self, context: ErrorContext) -> Dict[str, Any]:
        """Rotate proxy configuration"""
        self.logger.info("Rotating proxy configuration")
        
        self.recovery_state['proxy_rotation_index'] += 1
        
        return {
            'action': 'proxy_rotation',
            'rotation_index': self.recovery_state['proxy_rotation_index'],
            'timestamp': datetime.now().isoformat()
        }
    
    async def _find_alternative_endpoint(self, context: ErrorContext) -> Dict[str, Any]:
        """Find alternative endpoint for request"""
        self.logger.info(f"Finding alternative endpoint for {context.url}")
        
        # Placeholder implementation
        return {
            'action': 'alternative_endpoint',
            'original_url': context.url,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_fallback_config(self, error_type: ErrorType) -> ErrorConfig:
        """Get fallback configuration for unknown error codes"""
        return ErrorConfig(
            error_type=error_type,
            error_code='fallback',
            retry=True,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            max_retries=3,
            base_delay=1.0,
            max_delay=60.0,
            action=RetryAction.RETRY
        )
    
    def _update_error_stats(self, error_type: ErrorType, status_code: Optional[int]):
        """Update error statistics"""
        self.error_stats['total_errors'] += 1
        self.error_stats['by_type'][error_type.value] += 1
        
        if status_code:
            self.error_stats['by_status_code'][status_code] = \
                self.error_stats['by_status_code'].get(status_code, 0) + 1
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        stats = self.error_stats.copy()
        
        # Calculate rates
        total_errors = stats['total_errors']
        if total_errors > 0:
            stats['error_rates'] = {
                error_type: (count / total_errors) * 100
                for error_type, count in stats['by_type'].items()
            }
            
            stats['recovery_rate'] = (stats['successful_recoveries'] / total_errors) * 100
        
        return stats
    
    def reset_statistics(self):
        """Reset error statistics"""
        self.error_stats = {
            'total_errors': 0,
            'by_type': {error_type.value: 0 for error_type in ErrorType},
            'by_status_code': {},
            'retry_attempts': 0,
            'successful_recoveries': 0,
            'permanent_failures': 0
        }
        
        self.logger.info("Error statistics reset")
    
    def save_error_config(self, file_path: Optional[str] = None):
        """Save error configuration to file"""
        save_path = Path(file_path) if file_path else self.config_path
        
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert configs to serializable format
            config_data = {}
            for key, config in self.error_configs.items():
                config_data[key] = {
                    'error_type': config.error_type.value,
                    'error_code': config.error_code,
                    'retry': config.retry,
                    'backoff_strategy': config.backoff_strategy.value,
                    'max_retries': config.max_retries,
                    'base_delay': config.base_delay,
                    'max_delay': config.max_delay,
                    'action': config.action.value,
                    'jitter': config.jitter
                }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
                
            self.logger.info(f"Error configuration saved to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving error configuration: {e}")
            raise


if __name__ == "__main__":
    # Example usage
    error_handler = VSSErrorHandler()
    
    # Test error classification
    import requests
    try:
        # This will fail và trigger error handling
        requests.get("http://nonexistent.url", timeout=1)
    except Exception as e:
        error_type, error_code = error_handler.classify_error(e)
        print(f"Error classified as: {error_type.value} - {error_code}")
    
    # Display statistics
    print("\nError Statistics:")
    stats = error_handler.get_error_statistics()
    print(json.dumps(stats, indent=2))
