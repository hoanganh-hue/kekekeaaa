#!/usr/bin/env python3
"""
VSS Data Validator
Schema validation, completeness checks, duplicate detection

Author: MiniMax Agent
Date: 2025-09-12
"""

import json
import jsonschema
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import hashlib
import re
from abc import ABC, abstractmethod


@dataclass
class ValidationResult:
    """Validation result structure"""
    is_valid: bool
    score: float  # 0.0 - 1.0
    errors: List[str]
    warnings: List[str]
    missing_fields: List[str]
    invalid_fields: List[str]
    duplicate_indicators: List[str]
    completeness_percentage: float
    data_quality_metrics: Dict[str, Any]
    

@dataclass
class ValidationConfig:
    """Validation configuration"""
    strict_mode: bool = False
    required_fields_weight: float = 0.4
    data_type_weight: float = 0.3
    format_weight: float = 0.2
    completeness_weight: float = 0.1
    min_acceptable_score: float = 0.7
    

class ValidationRule(ABC):
    """Abstract validation rule"""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
    
    @abstractmethod
    def validate(self, data: Any, context: Dict[str, Any]) -> ValidationResult:
        """Validate data according to rule"""
        pass


class SchemaValidationRule(ValidationRule):
    """JSON Schema validation rule"""
    
    def __init__(self, name: str, schema: Dict[str, Any], weight: float = 1.0):
        super().__init__(name, weight)
        self.schema = schema
        self.validator = jsonschema.Draft7Validator(schema)
    
    def validate(self, data: Any, context: Dict[str, Any]) -> ValidationResult:
        """Validate against JSON schema"""
        errors = []
        warnings = []
        
        try:
            # Perform schema validation
            validation_errors = list(self.validator.iter_errors(data))
            
            for error in validation_errors:
                error_path = ' -> '.join(str(p) for p in error.absolute_path)
                error_message = f"{error_path}: {error.message}" if error_path else error.message
                errors.append(f"Schema validation: {error_message}")
            
            is_valid = len(validation_errors) == 0
            score = 1.0 if is_valid else max(0.0, 1.0 - (len(validation_errors) * 0.1))
            
        except Exception as e:
            errors.append(f"Schema validation error: {str(e)}")
            is_valid = False
            score = 0.0
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            errors=errors,
            warnings=warnings,
            missing_fields=[],
            invalid_fields=[],
            duplicate_indicators=[],
            completeness_percentage=100.0 if is_valid else 0.0,
            data_quality_metrics={'schema_errors': len(errors)}
        )


class CompletenessValidationRule(ValidationRule):
    """Data completeness validation rule"""
    
    def __init__(self, name: str, required_fields: List[str], 
                 optional_fields: List[str] = None, weight: float = 1.0):
        super().__init__(name, weight)
        self.required_fields = required_fields
        self.optional_fields = optional_fields or []
    
    def validate(self, data: Any, context: Dict[str, Any]) -> ValidationResult:
        """Validate data completeness"""
        errors = []
        warnings = []
        missing_fields = []
        
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary for completeness validation")
            return ValidationResult(
                is_valid=False,
                score=0.0,
                errors=errors,
                warnings=warnings,
                missing_fields=[],
                invalid_fields=[],
                duplicate_indicators=[],
                completeness_percentage=0.0,
                data_quality_metrics={}
            )
        
        # Check required fields
        for field in self.required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
                errors.append(f"Required field missing: {field}")
            elif isinstance(data[field], str) and not data[field].strip():
                missing_fields.append(field)
                errors.append(f"Required field empty: {field}")
        
        # Check optional fields (warnings only)
        for field in self.optional_fields:
            if field not in data or data[field] is None:
                warnings.append(f"Optional field missing: {field}")
        
        # Calculate completeness percentage
        total_fields = len(self.required_fields) + len(self.optional_fields)
        present_fields = sum(1 for field in self.required_fields + self.optional_fields 
                           if field in data and data[field] is not None)
        
        completeness_percentage = (present_fields / total_fields * 100) if total_fields > 0 else 100.0
        
        # Calculate score
        required_score = (len(self.required_fields) - len(missing_fields)) / len(self.required_fields) \
                        if self.required_fields else 1.0
        
        optional_score = (len([f for f in self.optional_fields if f in data]) / len(self.optional_fields)) \
                        if self.optional_fields else 1.0
        
        # Weighted score (required fields are more important)
        score = (required_score * 0.8) + (optional_score * 0.2)
        
        return ValidationResult(
            is_valid=len(missing_fields) == 0,
            score=score,
            errors=errors,
            warnings=warnings,
            missing_fields=missing_fields,
            invalid_fields=[],
            duplicate_indicators=[],
            completeness_percentage=completeness_percentage,
            data_quality_metrics={
                'required_fields_missing': len(missing_fields),
                'optional_fields_present': len([f for f in self.optional_fields if f in data])
            }
        )


class FormatValidationRule(ValidationRule):
    """Data format validation rule"""
    
    def __init__(self, name: str, format_patterns: Dict[str, str], weight: float = 1.0):
        super().__init__(name, weight)
        self.format_patterns = {field: re.compile(pattern) for field, pattern in format_patterns.items()}
    
    def validate(self, data: Any, context: Dict[str, Any]) -> ValidationResult:
        """Validate data formats"""
        errors = []
        warnings = []
        invalid_fields = []
        
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary for format validation")
            return ValidationResult(
                is_valid=False,
                score=0.0,
                errors=errors,
                warnings=warnings,
                missing_fields=[],
                invalid_fields=[],
                duplicate_indicators=[],
                completeness_percentage=0.0,
                data_quality_metrics={}
            )
        
        # Validate formats
        for field, pattern in self.format_patterns.items():
            if field in data and data[field] is not None:
                value = str(data[field])
                if not pattern.match(value):
                    invalid_fields.append(field)
                    errors.append(f"Invalid format for field '{field}': {value}")
        
        # Calculate score
        checked_fields = [field for field in self.format_patterns.keys() if field in data]
        if checked_fields:
            valid_fields = len(checked_fields) - len(invalid_fields)
            score = valid_fields / len(checked_fields)
        else:
            score = 1.0  # No fields to validate
        
        return ValidationResult(
            is_valid=len(invalid_fields) == 0,
            score=score,
            errors=errors,
            warnings=warnings,
            missing_fields=[],
            invalid_fields=invalid_fields,
            duplicate_indicators=[],
            completeness_percentage=100.0 if len(invalid_fields) == 0 else 0.0,
            data_quality_metrics={
                'format_violations': len(invalid_fields),
                'fields_checked': len(checked_fields)
            }
        )


class DuplicateDetectionRule(ValidationRule):
    """Duplicate detection rule"""
    
    def __init__(self, name: str, key_fields: List[str], weight: float = 1.0):
        super().__init__(name, weight)
        self.key_fields = key_fields
        self.seen_records = set()
    
    def validate(self, data: Any, context: Dict[str, Any]) -> ValidationResult:
        """Check for duplicates"""
        errors = []
        warnings = []
        duplicate_indicators = []
        
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary for duplicate detection")
            return ValidationResult(
                is_valid=False,
                score=0.0,
                errors=errors,
                warnings=warnings,
                missing_fields=[],
                invalid_fields=[],
                duplicate_indicators=[],
                completeness_percentage=0.0,
                data_quality_metrics={}
            )
        
        # Create composite key for duplicate detection
        key_values = []
        for field in self.key_fields:
            if field in data and data[field] is not None:
                key_values.append(str(data[field]))
            else:
                key_values.append('')  # Empty string for missing fields
        
        composite_key = '|'.join(key_values)
        key_hash = hashlib.md5(composite_key.encode('utf-8')).hexdigest()
        
        # Check if we've seen this record before
        is_duplicate = key_hash in self.seen_records
        
        if is_duplicate:
            duplicate_indicators = self.key_fields.copy()
            errors.append(f"Duplicate record detected with key: {composite_key[:50]}...")
        else:
            self.seen_records.add(key_hash)
        
        return ValidationResult(
            is_valid=not is_duplicate,
            score=0.0 if is_duplicate else 1.0,
            errors=errors,
            warnings=warnings,
            missing_fields=[],
            invalid_fields=[],
            duplicate_indicators=duplicate_indicators,
            completeness_percentage=100.0,
            data_quality_metrics={
                'is_duplicate': is_duplicate,
                'composite_key': composite_key
            }
        )
    
    def reset(self):
        """Reset duplicate tracking"""
        self.seen_records.clear()


class VSSDataValidator:
    """Comprehensive data validator cho VSS system"""
    
    def __init__(self, config_path: str = "config/validation_config.json"):
        """Initialize data validator"""
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize validation rules
        self.rules = self._initialize_rules()
        
        # Validation statistics
        self.validation_stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'average_score': 0.0,
            'common_errors': {},
            'field_quality_scores': {}
        }
    
    def _load_config(self) -> ValidationConfig:
        """Load validation configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return ValidationConfig(**config_data)
            else:
                self.logger.warning(f"Validation config not found: {self.config_path}")
                return ValidationConfig()
        except Exception as e:
            self.logger.error(f"Error loading validation config: {e}")
            return ValidationConfig()
    
    def _initialize_rules(self) -> List[ValidationRule]:
        """Initialize validation rules"""
        rules = []
        
        # Province data schema
        province_schema = {
            "type": "object",
            "properties": {
                "ma": {"type": "string", "pattern": "^\\d{3}$"},
                "ten": {"type": "string", "minLength": 1},
                "ma_tra_cuu": {"type": ["string", "null"]}
            },
            "required": ["ma", "ten"]
        }
        
        # District data schema
        district_schema = {
            "type": "object",
            "properties": {
                "ma": {"type": "string", "pattern": "^\\d{6}$"},
                "ten": {"type": "string", "minLength": 1},
                "ma_tinh": {"type": "string", "pattern": "^\\d{3}$"}
            },
            "required": ["ma", "ten", "ma_tinh"]
        }
        
        # Hospital data schema
        hospital_schema = {
            "type": "object",
            "properties": {
                "ma": {"type": "string", "minLength": 1},
                "ten": {"type": "string", "minLength": 1},
                "dia_chi": {"type": "string"},
                "dien_thoai": {"type": ["string", "null"]},
                "ma_tinh": {"type": "string", "pattern": "^\\d{3}$"}
            },
            "required": ["ma", "ten", "ma_tinh"]
        }
        
        # Add schema validation rules
        rules.append(SchemaValidationRule("province_schema", province_schema, 1.0))
        rules.append(SchemaValidationRule("district_schema", district_schema, 1.0))
        rules.append(SchemaValidationRule("hospital_schema", hospital_schema, 1.0))
        
        # Add completeness validation rules
        rules.append(CompletenessValidationRule(
            "province_completeness",
            required_fields=["ma", "ten"],
            optional_fields=["ma_tra_cuu"],
            weight=0.8
        ))
        
        rules.append(CompletenessValidationRule(
            "district_completeness",
            required_fields=["ma", "ten", "ma_tinh"],
            optional_fields=[],
            weight=0.8
        ))
        
        rules.append(CompletenessValidationRule(
            "hospital_completeness",
            required_fields=["ma", "ten", "ma_tinh"],
            optional_fields=["dia_chi", "dien_thoai"],
            weight=0.8
        ))
        
        # Add format validation rules
        province_formats = {
            "ma": r"^\d{3}$",  # 3-digit province code
            "ten": r".{2,}",   # At least 2 characters for name
        }
        
        district_formats = {
            "ma": r"^\d{6}$",      # 6-digit district code
            "ma_tinh": r"^\d{3}$", # 3-digit province code
            "ten": r".{2,}",       # At least 2 characters
        }
        
        hospital_formats = {
            "ma_tinh": r"^\d{3}$",                    # 3-digit province code
            "dien_thoai": r"^[\d\s\-\(\)\+]{0,20}$", # Phone number pattern
            "ten": r".{3,}",                          # At least 3 characters
        }
        
        rules.append(FormatValidationRule("province_formats", province_formats, 0.7))
        rules.append(FormatValidationRule("district_formats", district_formats, 0.7))
        rules.append(FormatValidationRule("hospital_formats", hospital_formats, 0.7))
        
        # Add duplicate detection rules
        rules.append(DuplicateDetectionRule(
            "province_duplicates", 
            key_fields=["ma"], 
            weight=1.0
        ))
        
        rules.append(DuplicateDetectionRule(
            "district_duplicates", 
            key_fields=["ma", "ma_tinh"], 
            weight=1.0
        ))
        
        rules.append(DuplicateDetectionRule(
            "hospital_duplicates", 
            key_fields=["ma", "ma_tinh"], 
            weight=0.8
        ))
        
        return rules
    
    def validate_data(self, data: Any, data_type: str, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate data using appropriate rules"""
        context = context or {}
        context['data_type'] = data_type
        
        # Select applicable rules based on data type
        applicable_rules = self._get_applicable_rules(data_type)
        
        if not applicable_rules:
            self.logger.warning(f"No validation rules found for data type: {data_type}")
            return ValidationResult(
                is_valid=True,
                score=1.0,
                errors=[],
                warnings=[f"No validation rules for data type: {data_type}"],
                missing_fields=[],
                invalid_fields=[],
                duplicate_indicators=[],
                completeness_percentage=100.0,
                data_quality_metrics={}
            )
        
        # Execute validation rules
        all_results = []
        for rule in applicable_rules:
            try:
                result = rule.validate(data, context)
                all_results.append((rule, result))
            except Exception as e:
                self.logger.error(f"Error in validation rule {rule.name}: {e}")
                # Create error result
                error_result = ValidationResult(
                    is_valid=False,
                    score=0.0,
                    errors=[f"Validation rule error: {str(e)}"],
                    warnings=[],
                    missing_fields=[],
                    invalid_fields=[],
                    duplicate_indicators=[],
                    completeness_percentage=0.0,
                    data_quality_metrics={}
                )
                all_results.append((rule, error_result))
        
        # Combine results
        combined_result = self._combine_validation_results(all_results)
        
        # Update statistics
        self._update_validation_stats(combined_result, data_type)
        
        return combined_result
    
    def _get_applicable_rules(self, data_type: str) -> List[ValidationRule]:
        """Get validation rules applicable to data type"""
        applicable_rules = []
        
        for rule in self.rules:
            # Match rules by naming convention
            if data_type in rule.name or data_type == 'province' and 'province' in rule.name:
                applicable_rules.append(rule)
            elif data_type == 'district' and 'district' in rule.name:
                applicable_rules.append(rule)
            elif data_type == 'hospital' and 'hospital' in rule.name:
                applicable_rules.append(rule)
            elif data_type == 'ward' and 'ward' in rule.name:
                applicable_rules.append(rule)
        
        return applicable_rules
    
    def _combine_validation_results(self, results: List[Tuple[ValidationRule, ValidationResult]]) -> ValidationResult:
        """Combine multiple validation results into single result"""
        all_errors = []
        all_warnings = []
        all_missing_fields = []
        all_invalid_fields = []
        all_duplicate_indicators = []
        all_metrics = {}
        
        total_weight = 0.0
        weighted_score = 0.0
        overall_valid = True
        completeness_sum = 0.0
        
        for rule, result in results:
            # Aggregate errors and warnings
            all_errors.extend([f"{rule.name}: {error}" for error in result.errors])
            all_warnings.extend([f"{rule.name}: {warning}" for warning in result.warnings])
            
            # Aggregate field issues
            all_missing_fields.extend(result.missing_fields)
            all_invalid_fields.extend(result.invalid_fields)
            all_duplicate_indicators.extend(result.duplicate_indicators)
            
            # Aggregate metrics
            all_metrics[rule.name] = result.data_quality_metrics
            
            # Calculate weighted score
            weighted_score += result.score * rule.weight
            total_weight += rule.weight
            completeness_sum += result.completeness_percentage
            
            # Overall validity
            if not result.is_valid:
                overall_valid = False
        
        # Calculate final score
        final_score = (weighted_score / total_weight) if total_weight > 0 else 0.0
        avg_completeness = (completeness_sum / len(results)) if results else 0.0
        
        # Remove duplicates from field lists
        all_missing_fields = list(set(all_missing_fields))
        all_invalid_fields = list(set(all_invalid_fields))
        all_duplicate_indicators = list(set(all_duplicate_indicators))
        
        return ValidationResult(
            is_valid=overall_valid and final_score >= self.config.min_acceptable_score,
            score=final_score,
            errors=all_errors,
            warnings=all_warnings,
            missing_fields=all_missing_fields,
            invalid_fields=all_invalid_fields,
            duplicate_indicators=all_duplicate_indicators,
            completeness_percentage=avg_completeness,
            data_quality_metrics=all_metrics
        )
    
    def validate_batch(self, data_list: List[Any], data_type: str, 
                      context: Dict[str, Any] = None) -> List[ValidationResult]:
        """Validate batch of data items"""
        results = []
        
        for i, data_item in enumerate(data_list):
            item_context = context.copy() if context else {}
            item_context['batch_index'] = i
            
            result = self.validate_data(data_item, data_type, item_context)
            results.append(result)
        
        return results
    
    def get_batch_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Get summary of batch validation results"""
        if not results:
            return {'message': 'No validation results to summarize'}
        
        valid_count = sum(1 for r in results if r.is_valid)
        total_count = len(results)
        
        avg_score = sum(r.score for r in results) / total_count
        avg_completeness = sum(r.completeness_percentage for r in results) / total_count
        
        all_errors = [error for r in results for error in r.errors]
        all_warnings = [warning for r in results for warning in r.warnings]
        
        # Count common errors
        error_counts = {}
        for error in all_errors:
            error_type = error.split(':')[0] if ':' in error else error
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return {
            'total_items': total_count,
            'valid_items': valid_count,
            'invalid_items': total_count - valid_count,
            'validation_rate': (valid_count / total_count) * 100,
            'average_score': avg_score,
            'average_completeness': avg_completeness,
            'total_errors': len(all_errors),
            'total_warnings': len(all_warnings),
            'common_errors': dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            'score_distribution': {
                'excellent': sum(1 for r in results if r.score >= 0.9),
                'good': sum(1 for r in results if 0.7 <= r.score < 0.9),
                'fair': sum(1 for r in results if 0.5 <= r.score < 0.7),
                'poor': sum(1 for r in results if r.score < 0.5)
            }
        }
    
    def _update_validation_stats(self, result: ValidationResult, data_type: str):
        """Update validation statistics"""
        self.validation_stats['total_validations'] += 1
        
        if result.is_valid:
            self.validation_stats['successful_validations'] += 1
        else:
            self.validation_stats['failed_validations'] += 1
        
        # Update rolling average score
        total = self.validation_stats['total_validations']
        current_avg = self.validation_stats['average_score']
        self.validation_stats['average_score'] = ((current_avg * (total - 1)) + result.score) / total
        
        # Track common errors
        for error in result.errors:
            error_type = error.split(':')[0] if ':' in error else error
            self.validation_stats['common_errors'][error_type] = \
                self.validation_stats['common_errors'].get(error_type, 0) + 1
    
    def reset_duplicate_tracking(self):
        """Reset duplicate tracking for all duplicate detection rules"""
        for rule in self.rules:
            if isinstance(rule, DuplicateDetectionRule):
                rule.reset()
        
        self.logger.info("Reset duplicate tracking for all rules")
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive validation statistics"""
        stats = self.validation_stats.copy()
        
        if stats['total_validations'] > 0:
            stats['success_rate'] = (stats['successful_validations'] / stats['total_validations']) * 100
            stats['failure_rate'] = (stats['failed_validations'] / stats['total_validations']) * 100
        else:
            stats['success_rate'] = 0.0
            stats['failure_rate'] = 0.0
        
        return stats
    
    def save_validation_report(self, results: List[ValidationResult], output_path: str):
        """Save detailed validation report"""
        try:
            report = {
                'validation_timestamp': datetime.now().isoformat(),
                'total_items': len(results),
                'batch_summary': self.get_batch_summary(results),
                'validation_statistics': self.get_validation_statistics(),
                'detailed_results': [asdict(result) for result in results]
            }
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Validation report saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving validation report: {e}")
            raise


if __name__ == "__main__":
    # Example usage
    validator = VSSDataValidator()
    
    # Test province data
    province_data = {
        'ma': '001',
        'ten': 'Hà Nội',
        'ma_tra_cuu': None
    }
    
    result = validator.validate_data(province_data, 'province')
    print(f"Validation result: Valid={result.is_valid}, Score={result.score:.2f}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
    
    # Test batch validation
    batch_data = [
        {'ma': '001', 'ten': 'Hà Nội'},
        {'ma': '031', 'ten': 'Hải Phòng'},
        {'ma': '048', 'ten': 'Đà Nẵng'},
        {'ma': 'invalid', 'ten': ''}  # Invalid data
    ]
    
    batch_results = validator.validate_batch(batch_data, 'province')
    summary = validator.get_batch_summary(batch_results)
    print(f"\nBatch validation summary: {json.dumps(summary, indent=2)}")
