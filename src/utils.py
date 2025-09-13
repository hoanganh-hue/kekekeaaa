#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Extractor - Utilities
Chứa các utility functions và helper methods.

Author: MiniMax Agent
Date: 2025-09-13
Version: 2.1
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
from pathlib import Path

from .config.data_models import ExtractionResult, ExtractionSummary
from .config.constants import ExtractionQuality


class ExtractionLogger:
    """Enhanced logging for extraction operations"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.logger = logging.getLogger('VSS_ExtractorLogger')
        
        if log_file:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_extraction_start(self, field_count: int, html_size: int):
        """Log start of extraction"""
        self.logger.info(f"Starting extraction for {field_count} fields, HTML size: {html_size} chars")
    
    def log_field_extraction(self, field_name: str, result: ExtractionResult):
        """Log individual field extraction result"""
        status = "SUCCESS" if result.is_successful else "FAILED"
        self.logger.info(
            f"Field '{field_name}': {status} | "
            f"Confidence: {result.confidence_score:.2f} | "
            f"Method: {result.extraction_method} | "
            f"Quality: {result.quality_level.value}"
        )
        
        if result.validation_errors:
            self.logger.warning(f"Validation errors for '{field_name}': {result.validation_errors}")
    
    def log_extraction_summary(self, summary: ExtractionSummary):
        """Log extraction summary"""
        self.logger.info(
            f"Extraction completed: {summary.successful_extractions}/{summary.total_fields} successful "
            f"({summary.success_rate:.1%}) | Overall quality: {summary.overall_quality_score:.2f} ({summary.status})"
        )


class PerformanceMonitor:
    """Monitor extraction performance"""
    
    def __init__(self):
        self.start_time = None
        self.timings = {}
        self.memory_usage = {}
    
    def start_timing(self, operation: str):
        """Start timing an operation"""
        self.timings[operation] = {'start': datetime.now()}
    
    def end_timing(self, operation: str):
        """End timing an operation"""
        if operation in self.timings:
            self.timings[operation]['end'] = datetime.now()
            self.timings[operation]['duration'] = (
                self.timings[operation]['end'] - self.timings[operation]['start']
            ).total_seconds()
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report"""
        return {
            'timings': {
                op: data.get('duration', 0) 
                for op, data in self.timings.items()
            },
            'total_operations': len(self.timings),
            'average_time': sum(
                data.get('duration', 0) for data in self.timings.values()
            ) / len(self.timings) if self.timings else 0
        }


class ResultExporter:
    """Export extraction results to various formats"""
    
    @staticmethod
    def to_json(results: Dict[str, Any], file_path: str = None) -> str:
        """Export results to JSON"""
        # Convert dataclasses to dictionaries for JSON serialization
        json_results = ResultExporter._convert_to_serializable(results)
        
        json_str = json.dumps(json_results, indent=2, ensure_ascii=False)
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str
    
    @staticmethod
    def to_csv(extracted_fields: Dict[str, ExtractionResult], file_path: str):
        """Export extracted fields to CSV"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'field_name', 'extracted_value', 'confidence_score', 
                'quality_level', 'extraction_method', 'fallback_used',
                'validation_errors', 'normalization_applied'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for field_name, result in extracted_fields.items():
                writer.writerow({
                    'field_name': result.field_name,
                    'extracted_value': str(result.extracted_value),
                    'confidence_score': result.confidence_score,
                    'quality_level': result.quality_level.value,
                    'extraction_method': result.extraction_method,
                    'fallback_used': result.fallback_used,
                    'validation_errors': '; '.join(result.validation_errors),
                    'normalization_applied': '; '.join(result.normalization_applied)
                })
    
    @staticmethod
    def to_excel(results: Dict[str, Any], file_path: str):
        """Export results to Excel"""
        try:
            import pandas as pd
            
            # Extract fields data
            fields_data = []
            for field_name, result in results.get('extracted_fields', {}).items():
                fields_data.append({
                    'Field Name': result.field_name,
                    'Extracted Value': str(result.extracted_value),
                    'Confidence Score': result.confidence_score,
                    'Quality Level': result.quality_level.value,
                    'Extraction Method': result.extraction_method,
                    'Fallback Used': result.fallback_used,
                    'Validation Errors': '; '.join(result.validation_errors),
                    'Normalization Applied': '; '.join(result.normalization_applied)
                })
            
            # Create Excel file with multiple sheets
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Fields sheet
                fields_df = pd.DataFrame(fields_data)
                fields_df.to_excel(writer, sheet_name='Extracted Fields', index=False)
                
                # Summary sheet
                summary = results.get('extraction_summary', {})
                if summary:
                    summary_data = [
                        ['Total Fields', summary.total_fields],
                        ['Successful Extractions', summary.successful_extractions],
                        ['Failed Extractions', summary.failed_extractions],
                        ['Success Rate', f"{summary.success_rate:.1%}"],
                        ['High Quality Count', summary.high_quality_count],
                        ['Overall Quality Score', f"{summary.overall_quality_score:.2f}"],
                        ['Status', summary.status]
                    ]
                    summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
        except ImportError:
            raise ImportError("pandas and openpyxl are required for Excel export")
    
    @staticmethod
    def _convert_to_serializable(obj, _seen=None):
        """Convert dataclasses and enums to serializable format"""
        if _seen is None:
            _seen = set()
        
        # Check for JSON-serializable basic types first
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        
        # Check for functions, methods, or other non-serializable types
        if callable(obj) or isinstance(obj, type):
            return f"<{type(obj).__name__}: not serializable>"
        
        # Prevent infinite recursion
        obj_id = id(obj)
        if obj_id in _seen:
            return f"<circular reference to {type(obj).__name__}>"
        
        if hasattr(obj, '__dict__'):
            _seen.add(obj_id)
            result = {}
            try:
                for key, value in obj.__dict__.items():
                    # Skip private attributes and methods
                    if not key.startswith('_') and not callable(value):
                        result[key] = ResultExporter._convert_to_serializable(value, _seen)
            finally:
                _seen.remove(obj_id)
            return result
        elif isinstance(obj, dict):
            return {key: ResultExporter._convert_to_serializable(value, _seen) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [ResultExporter._convert_to_serializable(item, _seen) for item in obj]
        elif hasattr(obj, 'value'):  # Enum
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            # For any other type, try to convert to string
            try:
                return str(obj)
            except:
                return f"<{type(obj).__name__}: conversion failed>"


class ConfigManager:
    """Manage configuration and settings"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_cache = {}
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_name in self.config_cache:
            return self.config_cache[config_name]
        
        config_file = self.config_dir / f"{config_name}.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.config_cache[config_name] = config
                return config
        else:
            return {}
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]):
        """Save configuration to file"""
        self.config_dir.mkdir(exist_ok=True)
        config_file = self.config_dir / f"{config_name}.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        self.config_cache[config_name] = config_data


class ValidationReportGenerator:
    """Generate validation reports"""
    
    @staticmethod
    def generate_detailed_report(results: Dict[str, Any]) -> str:
        """Generate detailed validation report"""
        report = []
        report.append("=== VSS Enhanced Extractor - Validation Report ===\n")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Summary section
        summary = results.get('extraction_summary', {})
        if summary:
            report.append("## Extraction Summary")
            report.append(f"- Total Fields: {summary.total_fields}")
            report.append(f"- Successful Extractions: {summary.successful_extractions}")
            report.append(f"- Success Rate: {summary.success_rate:.1%}")
            report.append(f"- Overall Quality Score: {summary.overall_quality_score:.2f}")
            report.append(f"- Status: {summary.status}")
            report.append("")
        
        # Field details
        report.append("## Field Extraction Details")
        extracted_fields = results.get('extracted_fields', {})
        
        for field_name, result in extracted_fields.items():
            report.append(f"### {field_name}")
            report.append(f"- **Value**: {result.extracted_value}")
            report.append(f"- **Confidence**: {result.confidence_score:.2f}")
            report.append(f"- **Quality**: {result.quality_level.value}")
            report.append(f"- **Method**: {result.extraction_method}")
            report.append(f"- **Fallback Used**: {result.fallback_used}")
            
            if result.validation_errors:
                report.append(f"- **Validation Errors**: {', '.join(result.validation_errors)}")
            
            if result.normalization_applied:
                report.append(f"- **Normalization Applied**: {', '.join(result.normalization_applied)}")
            
            report.append("")
        
        # Cross-validation section
        cross_validation = results.get('cross_validation', {})
        if cross_validation:
            report.append("## Cross-Validation Results")
            report.append(f"- Overall Consistency: {cross_validation.overall_consistency:.2f}")
            
            if cross_validation.inconsistencies:
                report.append("- **Inconsistencies Found**:")
                for inconsistency in cross_validation.inconsistencies:
                    report.append(f"  - {inconsistency}")
            report.append("")
        
        return "\n".join(report)


class HashUtils:
    """Utility functions for hashing and checksums"""
    
    @staticmethod
    def hash_content(content: str) -> str:
        """Generate hash for content"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_extraction_result(result: ExtractionResult) -> str:
        """Generate hash for extraction result"""
        content = f"{result.field_name}_{result.extracted_value}_{result.confidence_score}"
        return HashUtils.hash_content(content)


class FileUtils:
    """File utility functions"""
    
    @staticmethod
    def ensure_directory(path: str):
        """Ensure directory exists"""
        Path(path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def backup_file(file_path: str, backup_dir: str = "backups"):
        """Create backup of file"""
        if Path(file_path).exists():
            FileUtils.ensure_directory(backup_dir)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = Path(backup_dir) / f"{Path(file_path).stem}_{timestamp}{Path(file_path).suffix}"
            
            import shutil
            shutil.copy2(file_path, backup_path)
            return str(backup_path)
        return None
    
    @staticmethod
    def clean_old_files(directory: str, max_age_days: int = 30):
        """Clean old files from directory"""
        from datetime import timedelta
        
        directory_path = Path(directory)
        if directory_path.exists():
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            
            for file_path in directory_path.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()


# Convenience functions for common operations
def quick_extract(html_content: str, field_names: List[str] = None) -> Dict[str, Any]:
    """Quick extraction function for basic use cases"""
    from .vss_enhanced_extractor_v2 import VSS_EnhancedExtractor
    
    extractor = VSS_EnhancedExtractor()
    results = extractor.extract_enhanced_fields(html_content)
    
    if field_names:
        # Filter results to only requested fields
        filtered_fields = {
            name: result for name, result in results.get('extracted_fields', {}).items()
            if name in field_names
        }
        results['extracted_fields'] = filtered_fields
    
    return results


def validate_and_export(results: Dict[str, Any], output_dir: str = "output"):
    """Validate results and export to multiple formats"""
    FileUtils.ensure_directory(output_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Export to JSON
    json_path = f"{output_dir}/extraction_results_{timestamp}.json"
    ResultExporter.to_json(results, json_path)
    
    # Export to CSV
    csv_path = f"{output_dir}/extraction_fields_{timestamp}.csv"
    if 'extracted_fields' in results:
        ResultExporter.to_csv(results['extracted_fields'], csv_path)
    
    # Generate validation report
    report_path = f"{output_dir}/validation_report_{timestamp}.md"
    report_content = ValidationReportGenerator.generate_detailed_report(results)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return {
        'json_export': json_path,
        'csv_export': csv_path,
        'validation_report': report_path
    }
