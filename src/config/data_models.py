#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Extractor - Data Models
Chứa các data classes và models cho extraction engine.

Author: MiniMax Agent
Date: 2025-09-13
Version: 2.1
"""

from dataclasses import dataclass, field
from typing import List, Any, Optional, Dict
from datetime import datetime
from .constants import ExtractionQuality


@dataclass
class ExtractionResult:
    """Container for extraction results with quality metrics"""
    field_name: str
    extracted_value: Any
    confidence_score: float
    quality_level: ExtractionQuality
    extraction_method: str
    fallback_used: bool = False
    validation_errors: List[str] = field(default_factory=list)
    normalization_applied: List[str] = field(default_factory=list)
    extraction_timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Initialize timestamp if not provided"""
        if self.extraction_timestamp is None:
            self.extraction_timestamp = datetime.now()

    @property
    def is_successful(self) -> bool:
        """Check if extraction was successful"""
        return self.extracted_value is not None and self.quality_level != ExtractionQuality.FAILED

    @property
    def is_high_quality(self) -> bool:
        """Check if extraction is high quality"""
        return self.quality_level in [ExtractionQuality.EXCELLENT, ExtractionQuality.GOOD]


@dataclass
class FieldPattern:
    """Enhanced pattern definition for field extraction"""
    css_selectors: List[str]
    xpath_selectors: List[str]
    regex_patterns: List[str]
    context_keywords: List[str]
    validation_rules: List[str]
    normalization_functions: List[str]
    fallback_patterns: List[str]

    def get_total_patterns(self) -> int:
        """Get total number of patterns available"""
        return (len(self.css_selectors) + len(self.xpath_selectors) + 
                len(self.regex_patterns) + len(self.context_keywords) + 
                len(self.fallback_patterns))


@dataclass
class HTMLAnalysis:
    """HTML structure analysis result"""
    total_elements: int
    table_count: int
    div_count: int
    span_count: int
    form_count: int
    input_count: int
    has_json_script: bool
    text_length: int
    structure_type: str
    analysis_timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_table_heavy(self) -> bool:
        """Check if HTML is table-heavy structure"""
        return self.table_count > 3

    @property
    def is_form_based(self) -> bool:
        """Check if HTML is form-based"""
        return self.form_count > 0

    @property
    def is_div_heavy(self) -> bool:
        """Check if HTML is div-heavy structure"""
        return self.div_count > 10


@dataclass
class QualityMetrics:
    """Quality metrics for extraction result"""
    confidence_score: float
    quality_level: str
    extraction_method: str
    fallback_used: bool
    validation_error_count: int
    normalization_steps: int
    data_completeness: float
    overall_score: float

    @property
    def is_excellent(self) -> bool:
        """Check if quality is excellent"""
        return self.overall_score >= 0.9

    @property
    def is_acceptable(self) -> bool:
        """Check if quality is acceptable"""
        return self.overall_score >= 0.5


@dataclass
class CrossValidationResult:
    """Cross-validation result between extracted and input data"""
    input_data_keys: List[str]
    extracted_fields_keys: List[str]
    field_validations: Dict[str, Any]
    overall_consistency: float
    inconsistencies: List[str]
    validation_timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_consistent(self) -> bool:
        """Check if validation passed"""
        return self.overall_consistency >= 0.8


@dataclass
class ExtractionSummary:
    """Summary of extraction results"""
    total_fields: int
    successful_extractions: int
    failed_extractions: int
    success_rate: float
    high_quality_count: int
    moderate_quality_count: int
    overall_quality_score: float
    status: str
    summary_timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_successful_run(self) -> bool:
        """Check if extraction run was successful"""
        return self.success_rate >= 0.8

    @property
    def performance_grade(self) -> str:
        """Get performance grade"""
        if self.overall_quality_score > 0.8:
            return "A"
        elif self.overall_quality_score > 0.6:
            return "B"
        elif self.overall_quality_score > 0.4:
            return "C"
        else:
            return "D"


@dataclass
class MemberInfo:
    """Individual family member information"""
    name: str
    relationship: str
    birth_year: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None

    @property
    def is_complete(self) -> bool:
        """Check if member info is complete"""
        return bool(self.name and self.relationship)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'name': self.name,
            'relationship': self.relationship
        }
        if self.birth_year:
            result['birth_year'] = self.birth_year
        if self.additional_info:
            result.update(self.additional_info)
        return result


@dataclass
class NormalizedIncome:
    """Normalized income information"""
    amount: int
    currency: str
    formatted: str
    original: str
    parsing_successful: bool = True
    multiplier_applied: Optional[str] = None

    @property
    def is_reasonable(self) -> bool:
        """Check if income amount is reasonable"""
        return 100000 <= self.amount <= 100000000


@dataclass
class NormalizedBank:
    """Normalized bank information"""
    code: Optional[str]
    full_name: Optional[str]
    original: str
    match_type: str = "exact"
    confidence: float = 1.0

    @property
    def is_known_bank(self) -> bool:
        """Check if bank is in known banks list"""
        return self.match_type != "unknown"


@dataclass
class ValidationResult:
    """Result of field validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str] = field(default_factory=list)
    validation_timestamp: datetime = field(default_factory=datetime.now)

    @property
    def has_errors(self) -> bool:
        """Check if validation has errors"""
        return len(self.errors) > 0

    @property
    def error_count(self) -> int:
        """Get error count"""
        return len(self.errors)
