#!/usr/bin/env python3
"""
VSS Progress Monitor
Real-time progress tracking, error reporting, performance metrics, audit trails

Author: MiniMax Agent
Date: 2025-09-12
"""

import asyncio
import threading
import time
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import queue
import psutil
from collections import defaultdict, deque
from contextlib import contextmanager


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class ProgressLevel(Enum):
    """Progress reporting levels"""
    PROVINCE = "province"
    DISTRICT = "district"
    WARD = "ward"
    HOSPITAL = "hospital"
    CLAIM = "claim"
    BATCH = "batch"


@dataclass
class TaskProgress:
    """Individual task progress tracking"""
    task_id: str
    name: str
    status: TaskStatus
    progress_level: ProgressLevel
    total_items: int
    completed_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    last_update: Optional[datetime] = None
    error_messages: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.total_items == 0:
            return 100.0
        return (self.completed_items / self.total_items) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        processed_items = self.completed_items + self.failed_items
        if processed_items == 0:
            return 100.0
        return (self.completed_items / processed_items) * 100
    
    @property
    def elapsed_time(self) -> Optional[timedelta]:
        """Calculate elapsed time"""
        if self.start_time is None:
            return None
        end_time = self.end_time or datetime.now()
        return end_time - self.start_time
    
    @property
    def estimated_remaining_time(self) -> Optional[timedelta]:
        """Estimate remaining time based on current progress"""
        if self.start_time is None or self.completed_items == 0:
            return None
        
        elapsed = self.elapsed_time
        if elapsed is None:
            return None
        
        remaining_items = self.total_items - self.completed_items
        if remaining_items <= 0:
            return timedelta(0)
        
        time_per_item = elapsed.total_seconds() / self.completed_items
        estimated_seconds = time_per_item * remaining_items
        
        return timedelta(seconds=estimated_seconds)


@dataclass
class SystemMetrics:
    """System resource metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    active_threads: int
    network_io_sent: int = 0
    network_io_recv: int = 0


@dataclass
class PerformanceSnapshot:
    """Performance snapshot at a point in time"""
    timestamp: datetime
    total_tasks: int
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_completion_rate: float
    requests_per_minute: float
    error_rate: float
    system_metrics: SystemMetrics


class ProgressReporter:
    """Real-time progress reporting"""
    
    def __init__(self, update_interval: float = 5.0):
        self.update_interval = update_interval
        self.callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add progress update callback"""
        self.callbacks.append(callback)
    
    def report_progress(self, progress_data: Dict[str, Any]):
        """Report progress to all callbacks"""
        for callback in self.callbacks:
            try:
                callback(progress_data)
            except Exception as e:
                self.logger.error(f"Error in progress callback: {e}")
    
    def console_callback(self, progress_data: Dict[str, Any]):
        """Default console progress callback"""
        if 'overall_progress' in progress_data:
            overall = progress_data['overall_progress']
            print(f"\rProgress: {overall['completion_percentage']:.1f}% "
                  f"({overall['completed_tasks']}/{overall['total_tasks']} tasks) "
                  f"ETA: {overall.get('estimated_remaining_time', 'Unknown')}", end='', flush=True)


class AuditTrail:
    """Audit trail for tracking all operations"""
    
    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.entries = deque(maxlen=max_entries)
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def log_event(self, event_type: str, details: Dict[str, Any], 
                  task_id: Optional[str] = None, level: str = "INFO"):
        """Log audit event"""
        with self.lock:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'level': level,
                'task_id': task_id,
                'details': details,
                'thread_id': threading.get_ident(),
                'process_id': os.getpid() if 'os' in globals() else None
            }
            
            self.entries.append(entry)
            
            # Log to standard logger as well
            log_message = f"{event_type}: {details.get('message', 'No message')}"
            if task_id:
                log_message = f"[{task_id}] {log_message}"
            
            if level == "ERROR":
                self.logger.error(log_message)
            elif level == "WARNING":
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
    
    def get_events(self, event_type: Optional[str] = None, 
                   task_id: Optional[str] = None,
                   since: Optional[datetime] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get filtered audit events"""
        with self.lock:
            filtered_events = list(self.entries)
        
        # Apply filters
        if event_type:
            filtered_events = [e for e in filtered_events if e['event_type'] == event_type]
        
        if task_id:
            filtered_events = [e for e in filtered_events if e['task_id'] == task_id]
        
        if since:
            since_iso = since.isoformat()
            filtered_events = [e for e in filtered_events if e['timestamp'] >= since_iso]
        
        # Sort by timestamp (most recent first)
        filtered_events.sort(key=lambda e: e['timestamp'], reverse=True)
        
        # Apply limit
        if limit:
            filtered_events = filtered_events[:limit]
        
        return filtered_events
    
    def export_events(self, output_path: str, filters: Optional[Dict] = None):
        """Export audit events to file"""
        try:
            events = self.get_events(**(filters or {}))
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'export_timestamp': datetime.now().isoformat(),
                    'total_events': len(events),
                    'filters_applied': filters or {},
                    'events': events
                }, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(events)} audit events to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting audit events: {e}")
            raise


class VSSProgressMonitor:
    """Comprehensive progress monitoring system"""
    
    def __init__(self, enable_real_time: bool = True, 
                 metrics_interval: float = 30.0,
                 auto_save_interval: float = 300.0):
        """Initialize progress monitor"""
        self.enable_real_time = enable_real_time
        self.metrics_interval = metrics_interval
        self.auto_save_interval = auto_save_interval
        self.logger = logging.getLogger(__name__)
        
        # Task tracking
        self.tasks: Dict[str, TaskProgress] = {}
        self.task_hierarchy: Dict[str, List[str]] = defaultdict(list)  # parent_id -> [child_ids]
        self.tasks_lock = threading.RLock()
        
        # Progress reporting
        self.progress_reporter = ProgressReporter()
        if enable_real_time:
            self.progress_reporter.add_callback(self.progress_reporter.console_callback)
        
        # Audit trail
        self.audit_trail = AuditTrail()
        
        # Performance metrics
        self.performance_history: List[PerformanceSnapshot] = []
        self.metrics_lock = threading.Lock()
        
        # Background monitoring
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._last_auto_save = time.time()
        
        # Statistics
        self.session_stats = {
            'start_time': datetime.now(),
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'data_collected_mb': 0.0,
            'provinces_processed': set(),
            'errors_by_type': defaultdict(int)
        }
        
    def start_monitoring(self):
        """Start background monitoring"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitor_thread.start()
        
        self.logger.info("Started progress monitoring")
        self.audit_trail.log_event("MONITOR_STARTED", {'message': 'Progress monitoring started'})
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if not self._monitoring_active:
            return
        
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        
        self.logger.info("Stopped progress monitoring")
        self.audit_trail.log_event("MONITOR_STOPPED", {'message': 'Progress monitoring stopped'})
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self._monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Update real-time progress
                if self.enable_real_time:
                    progress_data = self._generate_progress_summary()
                    self.progress_reporter.report_progress(progress_data)
                
                # Auto-save progress
                if time.time() - self._last_auto_save > self.auto_save_interval:
                    self._auto_save_progress()
                    self._last_auto_save = time.time()
                
                time.sleep(self.metrics_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5.0)
    
    def create_task(self, task_id: str, name: str, progress_level: ProgressLevel,
                   total_items: int, parent_task_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> TaskProgress:
        """Create new task for monitoring"""
        with self.tasks_lock:
            task = TaskProgress(
                task_id=task_id,
                name=name,
                status=TaskStatus.PENDING,
                progress_level=progress_level,
                total_items=total_items,
                metadata=metadata or {}
            )
            
            self.tasks[task_id] = task
            
            # Handle hierarchy
            if parent_task_id:
                self.task_hierarchy[parent_task_id].append(task_id)
            
            self.audit_trail.log_event(
                "TASK_CREATED",
                {
                    'message': f'Created task: {name}',
                    'total_items': total_items,
                    'progress_level': progress_level.value,
                    'parent_task_id': parent_task_id
                },
                task_id=task_id
            )
            
            return task
    
    def start_task(self, task_id: str):
        """Mark task as started"""
        with self.tasks_lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = TaskStatus.RUNNING
                task.start_time = datetime.now()
                task.last_update = datetime.now()
                
                self.audit_trail.log_event(
                    "TASK_STARTED",
                    {'message': f'Started task: {task.name}'},
                    task_id=task_id
                )
    
    def update_task_progress(self, task_id: str, completed_items: Optional[int] = None,
                           failed_items: Optional[int] = None,
                           skipped_items: Optional[int] = None,
                           error_message: Optional[str] = None,
                           metadata_update: Optional[Dict[str, Any]] = None):
        """Update task progress"""
        with self.tasks_lock:
            if task_id not in self.tasks:
                self.logger.warning(f"Task {task_id} not found for progress update")
                return
            
            task = self.tasks[task_id]
            
            # Update counters
            if completed_items is not None:
                task.completed_items = completed_items
            if failed_items is not None:
                task.failed_items = failed_items
            if skipped_items is not None:
                task.skipped_items = skipped_items
            
            # Add error message
            if error_message:
                task.error_messages.append({
                    'timestamp': datetime.now().isoformat(),
                    'message': error_message
                })
            
            # Update metadata
            if metadata_update:
                task.metadata.update(metadata_update)
            
            task.last_update = datetime.now()
            
            # Log significant progress updates
            if completed_items is not None or error_message:
                self.audit_trail.log_event(
                    "TASK_PROGRESS_UPDATE",
                    {
                        'message': f'Progress update: {task.completion_percentage:.1f}% complete',
                        'completed_items': task.completed_items,
                        'total_items': task.total_items,
                        'error_message': error_message
                    },
                    task_id=task_id,
                    level="ERROR" if error_message else "INFO"
                )
    
    def complete_task(self, task_id: str, success: bool = True, 
                     final_message: Optional[str] = None):
        """Mark task as completed"""
        with self.tasks_lock:
            if task_id not in self.tasks:
                self.logger.warning(f"Task {task_id} not found for completion")
                return
            
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            task.end_time = datetime.now()
            task.last_update = datetime.now()
            
            if final_message:
                task.error_messages.append({
                    'timestamp': datetime.now().isoformat(),
                    'message': final_message
                })
            
            # Update session statistics
            if task.progress_level == ProgressLevel.PROVINCE:
                province_code = task.metadata.get('province_code')
                if province_code:
                    self.session_stats['provinces_processed'].add(province_code)
            
            self.audit_trail.log_event(
                "TASK_COMPLETED" if success else "TASK_FAILED",
                {
                    'message': f'Task {"completed" if success else "failed"}: {task.name}',
                    'completion_percentage': task.completion_percentage,
                    'success_rate': task.success_rate,
                    'elapsed_time': str(task.elapsed_time),
                    'final_message': final_message
                },
                task_id=task_id,
                level="INFO" if success else "ERROR"
            )
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O (if available)
            try:
                network = psutil.net_io_counters()
                network_sent = network.bytes_sent
                network_recv = network.bytes_recv
            except:
                network_sent = 0
                network_recv = 0
            
            system_metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.percent,
                active_threads=threading.active_count(),
                network_io_sent=network_sent,
                network_io_recv=network_recv
            )
            
            # Create performance snapshot
            with self.tasks_lock:
                total_tasks = len(self.tasks)
                active_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
                completed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
                failed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
            
            # Calculate rates
            avg_completion_rate = 0.0
            requests_per_minute = 0.0
            error_rate = 0.0
            
            if total_tasks > 0:
                avg_completion_rate = (completed_tasks / total_tasks) * 100
                error_rate = (failed_tasks / total_tasks) * 100
            
            # Calculate requests per minute from recent activity
            recent_requests = sum(t.completed_items + t.failed_items for t in self.tasks.values() 
                                if t.last_update and 
                                datetime.now() - t.last_update < timedelta(minutes=1))
            requests_per_minute = recent_requests
            
            snapshot = PerformanceSnapshot(
                timestamp=datetime.now(),
                total_tasks=total_tasks,
                active_tasks=active_tasks,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                average_completion_rate=avg_completion_rate,
                requests_per_minute=requests_per_minute,
                error_rate=error_rate,
                system_metrics=system_metrics
            )
            
            with self.metrics_lock:
                self.performance_history.append(snapshot)
                # Keep only last 1000 snapshots
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def _generate_progress_summary(self) -> Dict[str, Any]:
        """Generate comprehensive progress summary"""
        with self.tasks_lock:
            tasks = list(self.tasks.values())
        
        if not tasks:
            return {'overall_progress': {'message': 'No tasks found'}}
        
        # Overall statistics
        total_tasks = len(tasks)
        active_tasks = sum(1 for t in tasks if t.status == TaskStatus.RUNNING)
        completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for t in tasks if t.status == TaskStatus.FAILED)
        
        # Calculate overall completion percentage
        total_items = sum(t.total_items for t in tasks)
        completed_items = sum(t.completed_items for t in tasks)
        completion_percentage = (completed_items / max(total_items, 1)) * 100
        
        # Estimate remaining time
        running_tasks = [t for t in tasks if t.status == TaskStatus.RUNNING]
        estimated_remaining = None
        if running_tasks:
            avg_remaining = sum(t.estimated_remaining_time.total_seconds() 
                              for t in running_tasks 
                              if t.estimated_remaining_time) / len(running_tasks)
            estimated_remaining = str(timedelta(seconds=avg_remaining))
        
        # Progress by level
        progress_by_level = {}
        for level in ProgressLevel:
            level_tasks = [t for t in tasks if t.progress_level == level]
            if level_tasks:
                level_completed = sum(t.completed_items for t in level_tasks)
                level_total = sum(t.total_items for t in level_tasks)
                progress_by_level[level.value] = {
                    'completed': level_completed,
                    'total': level_total,
                    'percentage': (level_completed / max(level_total, 1)) * 100
                }
        
        # Recent errors
        recent_errors = []
        for task in tasks:
            if task.error_messages:
                recent_errors.extend(task.error_messages[-3:])  # Last 3 errors per task
        
        recent_errors.sort(key=lambda e: e['timestamp'], reverse=True)
        recent_errors = recent_errors[:10]  # Last 10 errors overall
        
        return {
            'overall_progress': {
                'total_tasks': total_tasks,
                'active_tasks': active_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'completion_percentage': completion_percentage,
                'estimated_remaining_time': estimated_remaining,
                'provinces_processed': len(self.session_stats['provinces_processed'])
            },
            'progress_by_level': progress_by_level,
            'recent_errors': recent_errors,
            'session_stats': {
                'start_time': self.session_stats['start_time'].isoformat(),
                'elapsed_time': str(datetime.now() - self.session_stats['start_time']),
                'provinces_processed': len(self.session_stats['provinces_processed'])
            }
        }
    
    def _auto_save_progress(self):
        """Auto-save progress data"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            progress_file = f"data/progress/progress_auto_save_{timestamp}.json"
            
            self.save_progress_report(progress_file)
            
            self.audit_trail.log_event(
                "AUTO_SAVE",
                {'message': f'Auto-saved progress to {progress_file}'}
            )
            
        except Exception as e:
            self.logger.error(f"Error in auto-save: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[TaskProgress]:
        """Get current status of a task"""
        with self.tasks_lock:
            return self.tasks.get(task_id)
    
    def get_all_tasks(self, status_filter: Optional[TaskStatus] = None) -> List[TaskProgress]:
        """Get all tasks, optionally filtered by status"""
        with self.tasks_lock:
            tasks = list(self.tasks.values())
        
        if status_filter:
            tasks = [t for t in tasks if t.status == status_filter]
        
        return tasks
    
    def get_performance_metrics(self, since: Optional[datetime] = None) -> List[PerformanceSnapshot]:
        """Get performance metrics history"""
        with self.metrics_lock:
            metrics = list(self.performance_history)
        
        if since:
            metrics = [m for m in metrics if m.timestamp >= since]
        
        return metrics
    
    def save_progress_report(self, output_path: str):
        """Save comprehensive progress report"""
        try:
            report = {
                'report_timestamp': datetime.now().isoformat(),
                'session_info': {
                    'start_time': self.session_stats['start_time'].isoformat(),
                    'elapsed_time': str(datetime.now() - self.session_stats['start_time']),
                    'provinces_processed': list(self.session_stats['provinces_processed'])
                },
                'overall_summary': self._generate_progress_summary(),
                'task_details': [asdict(task) for task in self.tasks.values()],
                'recent_performance': [asdict(snapshot) for snapshot in self.performance_history[-10:]],
                'recent_audit_events': self.audit_trail.get_events(limit=50),
                'statistics': {
                    'total_tasks': len(self.tasks),
                    'tasks_by_status': {
                        status.value: sum(1 for t in self.tasks.values() if t.status == status)
                        for status in TaskStatus
                    },
                    'tasks_by_level': {
                        level.value: sum(1 for t in self.tasks.values() if t.progress_level == level)
                        for level in ProgressLevel
                    }
                }
            }
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Progress report saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving progress report: {e}")
            raise
    
    @contextmanager
    def track_task(self, task_id: str, name: str, progress_level: ProgressLevel,
                   total_items: int, parent_task_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None):
        """Context manager for automatic task tracking"""
        task = self.create_task(task_id, name, progress_level, total_items, 
                               parent_task_id, metadata)
        self.start_task(task_id)
        
        try:
            yield task
            self.complete_task(task_id, success=True)
        except Exception as e:
            self.complete_task(task_id, success=False, final_message=str(e))
            raise


if __name__ == "__main__":
    # Example usage
    monitor = VSSProgressMonitor(enable_real_time=True)
    monitor.start_monitoring()
    
    # Create sample tasks
    with monitor.track_task("province_001", "Process Hà Nội", ProgressLevel.PROVINCE, 10) as task:
        for i in range(10):
            time.sleep(0.5)
            monitor.update_task_progress("province_001", completed_items=i+1)
    
    # Wait a bit for monitoring
    time.sleep(2)
    
    # Save report
    monitor.save_progress_report("test_progress_report.json")
    
    monitor.stop_monitoring()
    print("Progress monitoring example completed")
