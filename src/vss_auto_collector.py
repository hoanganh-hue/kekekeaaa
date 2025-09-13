#!/usr/bin/env python3
"""
VSS Automatic Data Collector
Comprehensive automation script thu thập dữ liệu từ VSS system

Author: MiniMax Agent
Date: 2025-09-12
Version: 1.0
"""

import asyncio
import aiohttp
import logging
import time
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
import signal
import sys
from contextlib import asynccontextmanager

# Import supporting modules
from .config_manager import VSSConfigManager, ApiConfig, ProxyConfig
from .province_iterator import ProvinceIterator, ProvinceInfo, ProgressLevel
from .error_handler import VSSErrorHandler, ErrorContext, RetryResult
from .data_storage import VSSDataStorage
from .data_validator import VSSDataValidator, ValidationResult
from .performance_optimizer import VSSPerformanceOptimizer, RequestConfig
from .progress_monitor import VSSProgressMonitor, TaskStatus, ProgressLevel as MonitorLevel
from .vss_api_client import VSSApiClient
from contextlib import contextmanager


class VSSDataCollector:
    """Main automation class cho comprehensive data collection từ VSS system"""
    
    def __init__(self, config_path: str = "config/vss_config.yaml"):
        """Initialize VSS Data Collector với comprehensive configuration"""
        
        # Initialize configuration manager
        self.config_manager = VSSConfigManager(config_path)
        self.config_manager.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Validate configuration
        if not self.config_manager.validate_config():
            raise ValueError("Invalid configuration - check config file")
        
        self.logger.info("Initializing VSS Data Collector v1.0")
        
        # Get configurations
        self.api_config = self.config_manager.get_api_config()
        self.proxy_config = self.config_manager.get_proxy_config()
        self.performance_config = self.config_manager.get_performance_config()
        
        # Initialize core components
        self._initialize_components()
        
        # Collection state
        self.is_running = False
        self.collection_session_id = None
        self.start_time = None
        self.stop_requested = False
        
        # Statistics tracking
        self.collection_stats = {
            'provinces_processed': 0,
            'districts_collected': 0,
            'wards_collected': 0,
            'hospitals_collected': 0,
            'total_requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'data_validation_passed': 0,
            'data_validation_failed': 0,
            'total_data_size_mb': 0.0
        }
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        self.logger.info("VSS Data Collector initialized successfully")
    
    def _initialize_components(self):
        """Initialize all supporting components"""
        try:
            # Province iterator
            self.province_iterator = ProvinceIterator("config/provinces.json")
            
            # Error handler
            self.error_handler = VSSErrorHandler("config/error_config.json")
            
            # Data storage
            storage_config = self.config_manager.get('data_storage', {})
            self.data_storage = VSSDataStorage(
                base_directory=storage_config.get('directory', 'data/collected'),
                formats=storage_config.get('formats', ['json', 'csv', 'sqlite']),
                compression=storage_config.get('compression', True),
                backup_enabled=storage_config.get('backup_enabled', True)
            )
            
            # Data validator
            validation_config = self.config_manager.get('validation', {})
            self.data_validator = VSSDataValidator(
                validation_config.get('schema_path', 'config/validation_config.json')
            )
            
            # Performance optimizer
            self.performance_optimizer = VSSPerformanceOptimizer(
                max_concurrent_requests=self.performance_config.max_concurrent_requests,
                connection_pool_size=self.performance_config.connection_pool_size,
                cache_size=self.performance_config.cache_ttl,
                cache_ttl=self.performance_config.cache_ttl
            )
            
            # Progress monitor
            monitoring_config = self.config_manager.get('monitoring', {})
            self.progress_monitor = VSSProgressMonitor(
                enable_real_time=monitoring_config.get('real_time_stats', True),
                metrics_interval=30.0,
                auto_save_interval=300.0
            )
            
            # VSS API Client - NEW
            self.api_client = VSSApiClient(
                api_config=self.api_config,
                proxy_config=self.proxy_config,
                session_timeout=self.api_config.timeout,
                max_concurrent=self.performance_config.max_concurrent_requests
            )
            
            self.logger.info("All components initialized successfully, including VSS API Client")
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Setup signal handlers cho graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.stop_requested = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start_collection(self, collection_strategy: str = "priority_first",
                             province_filter: Optional[List[str]] = None,
                             data_types: Optional[List[str]] = None) -> bool:
        """Start comprehensive data collection process"""
        
        if self.is_running:
            self.logger.warning("Collection is already running")
            return False
        
        try:
            self.is_running = True
            self.start_time = datetime.now()
            self.collection_session_id = f"session_{int(self.start_time.timestamp())}"
            
            self.logger.info(f"Starting VSS data collection - Session: {self.collection_session_id}")
            
            # Start monitoring
            self.progress_monitor.start_monitoring()
            
            # Start performance optimizer workers
            await self.performance_optimizer.start_workers()
            
            # Get provinces to process
            provinces_to_process = self._get_provinces_to_process(
                collection_strategy, province_filter
            )
            
            if not provinces_to_process:
                self.logger.error("No provinces to process")
                return False
            
            self.logger.info(f"Processing {len(provinces_to_process)} provinces với strategy: {collection_strategy}")
            
            # Create main collection task
            with self.progress_monitor.track_task(
                task_id="main_collection",
                name="VSS Data Collection",
                progress_level=MonitorLevel.BATCH,
                total_items=len(provinces_to_process),
                metadata={'session_id': self.collection_session_id}
            ) as main_task:
                
                # Process provinces
                success = await self._process_provinces_batch(
                    provinces_to_process, data_types or ['provinces', 'districts', 'wards', 'hospitals']
                )
            
            # Generate final reports
            await self._generate_final_reports()
            
            self.logger.info(f"Data collection completed - Success: {success}")
            return success
            
        except Exception as e:
            self.logger.error(f"Error in data collection: {e}")
            return False
            
        finally:
            await self._cleanup_collection()
    
    def _get_provinces_to_process(self, strategy: str, 
                                 province_filter: Optional[List[str]]) -> List[ProvinceInfo]:
        """Get list of provinces to process based on strategy và filter"""
        all_provinces = self.province_iterator.get_processing_order(strategy)
        
        if province_filter:
            # Filter by specified province codes
            filtered_provinces = []
            for province in all_provinces:
                if province.code in province_filter:
                    filtered_provinces.append(province)
            return filtered_provinces
        
        return all_provinces
    
    async def _process_provinces_batch(self, provinces: List[ProvinceInfo], 
                                     data_types: List[str]) -> bool:
        """Process batch of provinces với concurrent processing"""
        
        total_success = True
        processed_count = 0
        
        # Process provinces in smaller batches for better resource management
        batch_size = min(self.performance_config.batch_size, len(provinces))
        
        for i in range(0, len(provinces), batch_size):
            if self.stop_requested:
                self.logger.info("Stop requested, halting province processing")
                break
            
            batch = provinces[i:i + batch_size]
            self.logger.info(f"Processing province batch {i//batch_size + 1}: {[p.code for p in batch]}")
            
            # Process batch concurrently
            batch_tasks = []
            for province in batch:
                task = asyncio.create_task(
                    self._process_single_province(province, data_types)
                )
                batch_tasks.append(task)
            
            # Wait for batch completion
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process results
            for j, result in enumerate(batch_results):
                province = batch[j]
                if isinstance(result, Exception):
                    self.logger.error(f"Error processing province {province.code}: {result}")
                    total_success = False
                    self.province_iterator.update_processing_stats(province.code, False)
                elif result:
                    self.logger.info(f"Successfully processed province {province.code}")
                    processed_count += 1
                    self.province_iterator.update_processing_stats(province.code, True)
                else:
                    self.logger.warning(f"Failed to process province {province.code}")
                    total_success = False
                    self.province_iterator.update_processing_stats(province.code, False)
            
            # Update progress
            self.progress_monitor.update_task_progress(
                "main_collection",
                completed_items=processed_count
            )
            
            # Brief pause between batches
            if i + batch_size < len(provinces):
                await asyncio.sleep(1.0)
        
        self.collection_stats['provinces_processed'] = processed_count
        return total_success
    
    async def _process_single_province(self, province: ProvinceInfo, 
                                     data_types: List[str]) -> bool:
        """Process single province với comprehensive data collection"""
        
        province_task_id = f"province_{province.code}"
        
        with self.progress_monitor.track_task(
            task_id=province_task_id,
            name=f"Process {province.name} ({province.code})",
            progress_level=MonitorLevel.PROVINCE,
            total_items=len(data_types),
            parent_task_id="main_collection",
            metadata={'province_code': province.code, 'province_name': province.name}
        ) as province_task:
            
            try:
                success_count = 0
                
                for data_type in data_types:
                    if self.stop_requested:
                        break
                    
                    try:
                        # Collect data for this type
                        data = await self._collect_province_data(province, data_type)
                        
                        if data:
                            # Validate data
                            validation_result = self.data_validator.validate_data(
                                data, data_type, {'province_code': province.code}
                            )
                            
                            if validation_result.is_valid or not self.config_manager.get('validation.strict_mode', False):
                                # Save data
                                save_success = self.data_storage.save_province_data(
                                    province_code=province.code,
                                    data_type=data_type,
                                    data=data,
                                    metadata={
                                        'collection_timestamp': datetime.now().isoformat(),
                                        'session_id': self.collection_session_id,
                                        'validation_score': validation_result.score,
                                        'validation_passed': validation_result.is_valid
                                    }
                                )
                                
                                if save_success:
                                    success_count += 1
                                    self.collection_stats['successful_requests'] += 1
                                    if validation_result.is_valid:
                                        self.collection_stats['data_validation_passed'] += 1
                                    else:
                                        self.collection_stats['data_validation_failed'] += 1
                                else:
                                    self.logger.error(f"Failed to save {data_type} data for {province.code}")
                            else:
                                self.logger.warning(f"Data validation failed for {province.code} {data_type}: Score={validation_result.score:.2f}")
                                self.collection_stats['data_validation_failed'] += 1
                        
                        # Update progress
                        self.progress_monitor.update_task_progress(
                            province_task_id,
                            completed_items=success_count
                        )
                        
                    except Exception as e:
                        self.logger.error(f"Error collecting {data_type} for {province.code}: {e}")
                        self.collection_stats['failed_requests'] += 1
                
                return success_count > 0
                
            except Exception as e:
                self.logger.error(f"Error processing province {province.code}: {e}")
                return False
    
    async def _collect_province_data(self, province: ProvinceInfo, 
                                   data_type: str) -> Optional[Dict[str, Any]]:
        """Collect specific data type cho province using VSS API Client"""
        
        try:
            # Use specific API client methods based on data type
            response_data = None
            
            if data_type == 'provinces':
                response_data = await self.api_client.get_province_data_async(province.code)
            elif data_type == 'districts':
                districts_list = await self.api_client.get_districts_async(province.code)
                if districts_list is not None:
                    response_data = {'districts': districts_list}
            elif data_type == 'wards':
                wards_list = await self.api_client.get_wards_async(province.code)
                if wards_list is not None:
                    response_data = {'wards': wards_list}
            elif data_type == 'hospitals':
                hospitals_list = await self.api_client.get_hospitals_async(province.code)
                if hospitals_list is not None:
                    response_data = {'hospitals': hospitals_list}
            elif data_type == 'claims':
                # Custom endpoint for claims
                endpoint = f"/api/claims/{province.code}"
                response_data = await self.api_client.get_async(endpoint, use_cache=True)
            else:
                self.logger.warning(f"Unknown data type: {data_type}")
                return None
            
            if response_data:
                self.collection_stats['total_requests_made'] += 1
                
                # Calculate data size
                data_size = len(json.dumps(response_data).encode('utf-8')) / (1024 * 1024)  # MB
                self.collection_stats['total_data_size_mb'] += data_size
                
                self.logger.debug(f"Collected {data_type} data for {province.code}: {data_size:.2f}MB")
                return response_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error collecting {data_type} for {province.code}: {e}")
            self.collection_stats['failed_requests'] += 1
            return None
    
    async def _make_optimized_request(self, request_config: RequestConfig) -> Optional[Any]:
        """Make HTTP request using performance optimizer với error handling"""
        
        # Add callback for request completion
        response_data = None
        response_event = asyncio.Event()
        
        def request_callback(data: Any, config: RequestConfig):
            nonlocal response_data
            response_data = data
            response_event.set()
        
        request_config.callback = request_callback
        
        # Add request to optimizer queue
        if self.performance_optimizer.add_request(request_config):
            # Wait for completion với timeout
            try:
                await asyncio.wait_for(response_event.wait(), timeout=request_config.timeout + 10)
                return response_data
            except asyncio.TimeoutError:
                self.logger.error(f"Request timeout for {request_config.url}")
                return None
        else:
            self.logger.error(f"Failed to queue request for {request_config.url}")
            return None
    
    async def _generate_final_reports(self):
        """Generate comprehensive final reports"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            reports_dir = Path('reports') / self.collection_session_id
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Progress report
            progress_report_path = reports_dir / f'progress_report_{timestamp}.json'
            self.progress_monitor.save_progress_report(str(progress_report_path))
            
            # Performance report
            performance_report_path = reports_dir / f'performance_report_{timestamp}.json'
            self.performance_optimizer.save_performance_report(str(performance_report_path))
            
            # Validation report
            validation_report_path = reports_dir / f'validation_report_{timestamp}.json'
            # Note: This would need batch validation results to be meaningful
            
            # Collection summary report
            summary_report = {
                'session_info': {
                    'session_id': self.collection_session_id,
                    'start_time': self.start_time.isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'duration': str(datetime.now() - self.start_time)
                },
                'collection_statistics': self.collection_stats,
                'province_statistics': self.province_iterator.get_processing_statistics(),
                'performance_metrics': self.performance_optimizer.get_performance_metrics(),
                'storage_statistics': self.data_storage.get_storage_statistics(),
                'validation_statistics': self.data_validator.get_validation_statistics()
            }
            
            summary_report_path = reports_dir / f'collection_summary_{timestamp}.json'
            with open(summary_report_path, 'w', encoding='utf-8') as f:
                json.dump(summary_report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Final reports generated in {reports_dir}")
            
        except Exception as e:
            self.logger.error(f"Error generating final reports: {e}")
    
    async def _cleanup_collection(self):
        """Cleanup resources after collection"""
        try:
            self.is_running = False
            
            # Stop performance optimizer
            if hasattr(self, 'performance_optimizer'):
                await self.performance_optimizer.stop_workers()
            
            # Stop progress monitoring
            if hasattr(self, 'progress_monitor'):
                self.progress_monitor.stop_monitoring()
            
            # Save final configuration state
            if hasattr(self, 'province_iterator'):
                self.province_iterator.save_provinces_config()
            
            # Cleanup old backups
            if hasattr(self, 'data_storage'):
                self.data_storage.cleanup_old_backups(retention_days=30)
            
            self.logger.info("Collection cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    async def stop_collection(self):
        """Gracefully stop ongoing collection"""
        self.logger.info("Stopping data collection...")
        self.stop_requested = True
        
        # Wait for current operations to complete
        max_wait_time = 30  # seconds
        start_wait = time.time()
        
        while self.is_running and (time.time() - start_wait) < max_wait_time:
            await asyncio.sleep(1.0)
        
        if self.is_running:
            self.logger.warning("Forced collection stop after timeout")
        else:
            self.logger.info("Collection stopped gracefully")
    
    def get_collection_status(self) -> Dict[str, Any]:
        """Get current collection status"""
        if not self.is_running:
            return {
                'status': 'stopped',
                'message': 'Data collection is not running'
            }
        
        elapsed_time = datetime.now() - self.start_time if self.start_time else timedelta(0)
        
        return {
            'status': 'running',
            'session_id': self.collection_session_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'elapsed_time': str(elapsed_time),
            'statistics': self.collection_stats,
            'performance_metrics': self.performance_optimizer.get_performance_metrics() if hasattr(self, 'performance_optimizer') else {},
            'province_progress': self.province_iterator.get_processing_statistics() if hasattr(self, 'province_iterator') else {}
        }
    
    @asynccontextmanager
    async def collection_session(self, **kwargs):
        """Context manager cho automatic collection lifecycle management"""
        try:
            success = await self.start_collection(**kwargs)
            yield success
        finally:
            if self.is_running:
                await self.stop_collection()


async def main():
    """Main entry point cho VSS Data Collector"""
    
    # Parse command line arguments (simplified)
    import argparse
    
    parser = argparse.ArgumentParser(description='VSS Automatic Data Collector')
    parser.add_argument('--config', default='config/vss_config.yaml', help='Configuration file path')
    parser.add_argument('--strategy', default='priority_first', 
                       choices=['priority_first', 'geographic', 'size_based', 'random'],
                       help='Collection strategy')
    parser.add_argument('--provinces', nargs='*', help='Specific province codes to collect')
    parser.add_argument('--data-types', nargs='*', 
                       default=['provinces', 'districts', 'wards', 'hospitals'],
                       help='Data types to collect')
    parser.add_argument('--dry-run', action='store_true', help='Validate configuration without running collection')
    
    args = parser.parse_args()
    
    try:
        # Initialize collector
        collector = VSSDataCollector(config_path=args.config)
        
        if args.dry_run:
            print("Configuration validation completed successfully")
            status = collector.get_collection_status()
            print(json.dumps(status, indent=2, default=str))
            return
        
        # Start collection
        print(f"Starting VSS data collection với strategy: {args.strategy}")
        if args.provinces:
            print(f"Target provinces: {args.provinces}")
        
        async with collector.collection_session(
            collection_strategy=args.strategy,
            province_filter=args.provinces,
            data_types=args.data_types
        ) as success:
            if success:
                print("\nData collection completed successfully!")
            else:
                print("\nData collection completed với some errors")
        
        # Display final statistics
        final_status = collector.get_collection_status()
        print("\nFinal Statistics:")
        print(json.dumps(final_status.get('statistics', {}), indent=2))
        
    except KeyboardInterrupt:
        print("\nCollection interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        logging.error(f"Fatal error in main: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    # Run main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


    async def _cleanup_collection(self):
        """Clean up resources after collection"""
        self.logger.info("Cleaning up collection resources...")
        self.is_running = False
        
        # Stop monitoring and performance workers
        self.progress_monitor.stop_monitoring()
        await self.performance_optimizer.stop_workers()
        
        # Save final progress report
        self.progress_monitor.save_progress_report("final_report.json")
        
        # Close data storage connections
        self.data_storage.close()
        
        self.logger.info("Cleanup complete")

    async def _generate_final_reports(self):
        """Generate final summary and performance reports"""
        self.logger.info("Generating final reports...")
        
        # Performance report
        performance_metrics = self.performance_optimizer.get_metrics()
        report_path = self.progress_monitor.report_directory / "performance_report.json"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(performance_metrics, f, indent=2, default=str)
            self.logger.info(f"Performance report saved to {report_path}")
        except Exception as e:
            self.logger.error(f"Error saving performance report: {e}")

if __name__ == "__main__":
    async def main():
        try:
            collector = VSSDataCollector()
            success = await collector.start_collection(
                collection_strategy="priority_first",
                # province_filter=["001"], # Example filter
                data_types=["provinces", "districts", "hospitals"]
            )
            if success:
                print("Data collection completed successfully.")
            else:
                print("Data collection finished with errors.")
        except Exception as e:
            logging.getLogger(__name__).critical(f"Critical error starting collector: {e}", exc_info=True)
            sys.exit(1)

    # Run the main async function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCollection interrupted by user.")


