#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Extractor - Main Extractor (Refactored)
Enhanced Fields Extraction Engine với improved architecture.

Author: MiniMax Agent
Date: 2025-09-13
Version: 2.1
"""

import logging
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime

from .config.constants import ExtractionQuality, FIELD_NAMES, ERROR_PENALTIES
from .config.data_models import (
    ExtractionResult, HTMLAnalysis, QualityMetrics, 
    CrossValidationResult, ExtractionSummary
)
from .extractors.base_extractor import BaseExtractor
from .normalizers.field_normalizers import NormalizerFactory
from .validators.field_validators import ValidatorFactory


class VSS_EnhancedExtractor(BaseExtractor):
    """
    Enhanced Fields Extraction Engine cho VSS (Refactored Version)
    Robust extraction cho 5 enhanced fields với improved architecture
    """
    
    def __init__(self):
        """Initialize enhanced extractor"""
        super().__init__()
        self.extraction_results = []
        self.quality_metrics = {}
        
        # Initialize normalizers and validators
        self.normalizer_factory = NormalizerFactory()
        self.validator_factory = ValidatorFactory()
        self.cross_validator = self.validator_factory.get_cross_validator()
        
        self.logger.info("VSS Enhanced Extractor v2.1 initialized")

    def extract_enhanced_fields(self, html_content: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main extraction method cho tất cả enhanced fields
        
        Args:
            html_content: HTML response từ VSS
            input_data: Original input data cho cross-validation
            
        Returns:
            Dictionary chứa extracted data với quality metrics
        """
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Initialize results container
            extraction_results = self._initialize_results_container(soup, input_data)
            
            # Extract từng field
            for field_name in self.field_patterns.keys():
                self.logger.info(f"Extracting field: {field_name}")
                
                field_result = self._extract_single_field(
                    soup, field_name, html_content, input_data
                )
                
                extraction_results['extracted_fields'][field_name] = field_result
                extraction_results['quality_metrics'][field_name] = self._calculate_quality_metrics(field_result)
            
            # Perform cross-validation if input data available
            if input_data:
                extraction_results['cross_validation'] = self._perform_cross_validation(
                    extraction_results['extracted_fields'], input_data
                )
            
            # Generate extraction summary
            extraction_results['extraction_summary'] = self._generate_extraction_summary(
                extraction_results['extracted_fields']
            )
            
            return extraction_results
            
        except Exception as e:
            self.logger.error(f"Error in extract_enhanced_fields: {e}")
            return self._create_error_response(str(e))

    def _initialize_results_container(self, soup: BeautifulSoup, input_data: Dict = None) -> Dict[str, Any]:
        """Initialize results container with metadata"""
        html_analysis = self.analyze_html_structure(soup)
        
        return {
            'extraction_timestamp': datetime.now().isoformat(),
            'extraction_engine': 'VSS_EnhancedExtractor_v2.1',
            'input_data_provided': input_data is not None,
            'html_analysis': html_analysis,
            'extracted_fields': {},
            'quality_metrics': {},
            'cross_validation': {},
            'extraction_summary': {}
        }

    def _extract_single_field(self, soup: BeautifulSoup, field_name: str, 
                            html_content: str, input_data: Dict = None) -> ExtractionResult:
        """Extract một field với multiple strategies và fallback"""
        
        pattern = self.field_patterns[field_name]
        extraction_attempts = []
        
        try:
            # Strategy 1: CSS Selectors
            css_result = self.extract_by_css_selectors(soup, field_name, pattern.css_selectors)
            if css_result:
                extraction_attempts.append(('css_selector', css_result, 0.9))
            
            # Strategy 2: Regex patterns
            regex_result = self.extract_by_regex(html_content, field_name, pattern.regex_patterns)
            if regex_result:
                extraction_attempts.append(('regex_pattern', regex_result, 0.8))
            
            # Strategy 3: Context-based search
            context_result = self.extract_by_context(soup, field_name, pattern.context_keywords)
            if context_result:
                extraction_attempts.append(('context_search', context_result, 0.7))
            
            # Strategy 4: XPath selectors (simulated)
            xpath_result = self.extract_by_xpath_simulation(soup, field_name, pattern.xpath_selectors)
            if xpath_result:
                extraction_attempts.append(('xpath_simulation', xpath_result, 0.8))
            
            # Strategy 5: Fallback patterns
            if not extraction_attempts:
                fallback_result = self.extract_by_fallback(html_content, field_name, pattern.fallback_patterns)
                if fallback_result:
                    extraction_attempts.append(('fallback_pattern', fallback_result, 0.5))
            
            # Select best result with enhanced logic
            if extraction_attempts:
                best_method, best_value, base_confidence = self._select_best_extraction_result(
                    field_name, extraction_attempts
                )
                
                # Normalize result
                normalized_value = self._normalize_field_value(field_name, best_value)
                
                # Validate result
                validation_result = self._validate_field_value(field_name, normalized_value, input_data)
                
                # Calculate final confidence
                final_confidence = self.calculate_confidence_score(
                    base_confidence, validation_result.errors, best_method
                )
                
                return ExtractionResult(
                    field_name=field_name,
                    extracted_value=normalized_value,
                    confidence_score=final_confidence,
                    quality_level=self.determine_quality_level(final_confidence),
                    extraction_method=best_method,
                    fallback_used=('fallback' in best_method),
                    validation_errors=validation_result.errors,
                    normalization_applied=self.get_normalization_applied(field_name, best_value, normalized_value)
                )
            else:
                # No extraction successful
                return self._create_failed_extraction_result(field_name, "No extraction pattern matched")
                
        except Exception as e:
            self.logger.error(f"Error extracting field {field_name}: {e}")
            return self._create_failed_extraction_result(field_name, f"Extraction error: {str(e)}")

    def _select_best_extraction_result(self, field_name: str, extraction_attempts: List) -> tuple:
        """Select best extraction result with enhanced logic for thong_tin_thanh_vien"""
        
        # Special handling for thong_tin_thanh_vien - prioritize results with actual data
        if field_name == 'thong_tin_thanh_vien':
            valid_attempts = []
            
            for method, value, base_conf in extraction_attempts:
                test_normalized = self._normalize_field_value(field_name, value)
                if test_normalized and len(test_normalized) > 0:
                    # Has actual normalized data
                    adjusted_confidence = base_conf + ERROR_PENALTIES['data_quality_bonus']
                    valid_attempts.append((method, value, adjusted_confidence, test_normalized))
            
            if valid_attempts:
                # Pick the attempt with actual data and highest confidence
                best_method, best_value, base_confidence, _ = max(valid_attempts, key=lambda x: x[2])
                return best_method, best_value, base_confidence
        
        # Standard logic for other fields
        return max(extraction_attempts, key=lambda x: x[2])

    def _normalize_field_value(self, field_name: str, value: str) -> Any:
        """Normalize extracted value using appropriate normalizer"""
        if not value:
            return None
            
        try:
            normalizer = self.normalizer_factory.get_normalizer(field_name)
            return normalizer.normalize(value)
        except Exception as e:
            self.logger.error(f"Error normalizing {field_name}: {e}")
            return value

    def _validate_field_value(self, field_name: str, value: Any, input_data: Dict = None):
        """Validate extracted field value using appropriate validator"""
        try:
            validator = self.validator_factory.get_validator(field_name)
            validation_result = validator.validate(value)
            
            # Add cross-validation if input data available
            if input_data:
                cross_validation = self.cross_validator.validate_field_consistency(
                    field_name, value, input_data
                )
                if not cross_validation.get('is_consistent', True):
                    validation_result.errors.append(
                        f"Cross-validation failed: {cross_validation.get('comparison_notes', 'Unknown issue')}"
                    )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating {field_name}: {e}")
            from config.data_models import ValidationResult
            return ValidationResult(is_valid=False, errors=[f"Validation error: {str(e)}"])

    def _calculate_quality_metrics(self, result: ExtractionResult) -> QualityMetrics:
        """Calculate detailed quality metrics for extraction result"""
        try:
            overall_score = self._calculate_overall_score(result)
            
            return QualityMetrics(
                confidence_score=result.confidence_score,
                quality_level=result.quality_level.value,
                extraction_method=result.extraction_method,
                fallback_used=result.fallback_used,
                validation_error_count=len(result.validation_errors),
                normalization_steps=len(result.normalization_applied),
                data_completeness=1.0 if result.extracted_value else 0.0,
                overall_score=overall_score
            )
        except Exception as e:
            self.logger.error(f"Error calculating quality metrics: {e}")
            return QualityMetrics(
                confidence_score=0.0, quality_level="error", extraction_method="error",
                fallback_used=False, validation_error_count=999, normalization_steps=0,
                data_completeness=0.0, overall_score=0.0
            )

    def _calculate_overall_score(self, result: ExtractionResult) -> float:
        """Calculate overall quality score"""
        try:
            # Weighted combination of factors
            factors = {
                'confidence': result.confidence_score * 0.4,
                'completeness': (1.0 if result.extracted_value else 0.0) * 0.3,
                'validation': max(0, 1.0 - len(result.validation_errors) * 0.2) * 0.2,
                'method_reliability': (0.8 if not result.fallback_used else 0.4) * 0.1
            }
            
            return sum(factors.values())
        except Exception:
            return 0.0

    def _perform_cross_validation(self, extracted_fields: Dict, input_data: Dict) -> CrossValidationResult:
        """Perform comprehensive cross-validation"""
        try:
            field_validations = {}
            inconsistencies = []
            total_score = 0
            valid_fields = 0
            
            for field_name, result in extracted_fields.items():
                if result.extracted_value:
                    field_validation = self.cross_validator.validate_field_consistency(
                        field_name, result.extracted_value, input_data
                    )
                    field_validations[field_name] = field_validation
                    
                    if field_validation.get('is_consistent', True):
                        total_score += 1
                    else:
                        inconsistencies.append(f"{field_name}: {field_validation.get('comparison_notes', 'Inconsistent')}")
                    
                    valid_fields += 1
            
            overall_consistency = total_score / valid_fields if valid_fields > 0 else 0.0
            
            return CrossValidationResult(
                input_data_keys=list(input_data.keys()),
                extracted_fields_keys=list(extracted_fields.keys()),
                field_validations=field_validations,
                overall_consistency=overall_consistency,
                inconsistencies=inconsistencies
            )
            
        except Exception as e:
            self.logger.error(f"Error in cross-validation: {e}")
            return CrossValidationResult(
                input_data_keys=[], extracted_fields_keys=[], field_validations={},
                overall_consistency=0.0, inconsistencies=[f"Cross-validation error: {str(e)}"]
            )

    def _generate_extraction_summary(self, extracted_fields: Dict) -> ExtractionSummary:
        """Generate summary of extraction results"""
        try:
            total_fields = len(extracted_fields)
            successful_extractions = 0
            failed_extractions = 0
            moderate_quality = 0
            high_quality = 0
            
            for field_name, result in extracted_fields.items():
                if result.extracted_value:
                    successful_extractions += 1
                    
                    if result.quality_level in [ExtractionQuality.EXCELLENT, ExtractionQuality.GOOD]:
                        high_quality += 1
                    elif result.quality_level == ExtractionQuality.MODERATE:
                        moderate_quality += 1
                else:
                    failed_extractions += 1
            
            success_rate = successful_extractions / total_fields if total_fields > 0 else 0
            quality_score = (high_quality * 1.0 + moderate_quality * 0.5) / total_fields if total_fields > 0 else 0
            
            # Determine status
            if quality_score > 0.8:
                status = 'excellent'
            elif quality_score > 0.6:
                status = 'good'
            elif quality_score > 0.3:
                status = 'moderate'
            else:
                status = 'poor'
            
            return ExtractionSummary(
                total_fields=total_fields,
                successful_extractions=successful_extractions,
                failed_extractions=failed_extractions,
                success_rate=success_rate,
                high_quality_count=high_quality,
                moderate_quality_count=moderate_quality,
                overall_quality_score=quality_score,
                status=status
            )
            
        except Exception as e:
            self.logger.error(f"Error generating extraction summary: {e}")
            return ExtractionSummary(
                total_fields=0, successful_extractions=0, failed_extractions=0,
                success_rate=0.0, high_quality_count=0, moderate_quality_count=0,
                overall_quality_score=0.0, status='error'
            )

    def _create_failed_extraction_result(self, field_name: str, error_message: str) -> ExtractionResult:
        """Create failed extraction result"""
        return ExtractionResult(
            field_name=field_name,
            extracted_value=None,
            confidence_score=0.0,
            quality_level=ExtractionQuality.FAILED,
            extraction_method='none',
            validation_errors=[error_message]
        )

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'extraction_success': False,
            'extraction_error': error_message,
            'extraction_timestamp': datetime.now().isoformat(),
            'extraction_engine': 'VSS_EnhancedExtractor_v2.1'
        }

    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get extraction statistics"""
        return {
            'total_extractions': len(self.extraction_results),
            'average_quality': sum(r.confidence_score for r in self.extraction_results) / len(self.extraction_results) if self.extraction_results else 0,
            'success_rate': sum(1 for r in self.extraction_results if r.is_successful) / len(self.extraction_results) if self.extraction_results else 0,
            'field_performance': {
                field_name: {
                    'attempts': len([r for r in self.extraction_results if r.field_name == field_name]),
                    'successes': len([r for r in self.extraction_results if r.field_name == field_name and r.is_successful]),
                    'avg_confidence': sum(r.confidence_score for r in self.extraction_results if r.field_name == field_name) / len([r for r in self.extraction_results if r.field_name == field_name]) if [r for r in self.extraction_results if r.field_name == field_name] else 0
                }
                for field_name in FIELD_NAMES.values()
            }
        }
