#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Extractor - Field Validators
Chứa các validator classes cho validation logic.

Author: MiniMax Agent
Date: 2025-09-13
Version: 2.1
"""

import re
import logging
from typing import List, Dict, Any
from ..config.data_models import ValidationResult, NormalizedIncome, NormalizedBank, MemberInfo
from ..config.constants import VALIDATION_RANGES
from ..config.patterns import NormalizationMappingsConfig


class BaseValidator:
    """Base validator class"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.normalization_maps = NormalizationMappingsConfig.get_normalization_maps()
    
    def validate(self, value: Any) -> ValidationResult:
        """Override in subclasses"""
        raise NotImplementedError


class PhoneValidator(BaseValidator):
    """Phone number validator"""
    
    def validate(self, phone: str) -> ValidationResult:
        """Validate phone number"""
        errors = []
        warnings = []
        
        if not phone:
            errors.append("Phone number is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Check Vietnam phone format
        if not re.match(r'^0[1-9][0-9]{8,9}$', phone):
            errors.append("Invalid Vietnam phone number format")
        
        # Check length
        if len(phone) < VALIDATION_RANGES['phone_min_length'] or len(phone) > VALIDATION_RANGES['phone_max_length']:
            errors.append(f"Phone number length should be between {VALIDATION_RANGES['phone_min_length']} and {VALIDATION_RANGES['phone_max_length']} digits")
        
        # Check known prefixes
        if len(phone) >= 3:
            prefix = phone[:3]
            if prefix not in self.normalization_maps['phone_prefixes']:
                warnings.append(f"Unknown phone prefix: {prefix}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class IncomeValidator(BaseValidator):
    """Income validator"""
    
    def validate(self, income: NormalizedIncome) -> ValidationResult:
        """Validate income value"""
        errors = []
        warnings = []
        
        if not income:
            errors.append("Income data is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        if not income.parsing_successful:
            errors.append("Income parsing failed")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Reasonable range check
        if income.amount < VALIDATION_RANGES['income_min']:
            errors.append(f"Income seems too low (< {VALIDATION_RANGES['income_min']:,} VND)")
        elif income.amount > VALIDATION_RANGES['income_max']:
            errors.append(f"Income seems too high (> {VALIDATION_RANGES['income_max']:,} VND)")
        
        # Check if reasonable
        if not income.is_reasonable:
            warnings.append("Income amount may be outside reasonable range")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class BankValidator(BaseValidator):
    """Bank validator"""
    
    def validate(self, bank: NormalizedBank) -> ValidationResult:
        """Validate bank information"""
        errors = []
        warnings = []
        
        if not bank:
            errors.append("Bank data is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        if bank.match_type == "unknown":
            warnings.append("Bank not found in known banks list")
        elif bank.match_type == "error":
            errors.append("Error occurred during bank normalization")
        
        if bank.confidence < 0.5:
            warnings.append(f"Low confidence in bank matching: {bank.confidence:.2f}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class HouseholdCodeValidator(BaseValidator):
    """Household code validator"""
    
    def validate(self, code: str) -> ValidationResult:
        """Validate household code"""
        errors = []
        warnings = []
        
        if not code:
            errors.append("Household code is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Check format
        if not re.match(r'^[A-Z0-9]{8,15}$', code):
            errors.append("Invalid household code format (should be 8-15 alphanumeric characters)")
        
        # Check length
        if len(code) < VALIDATION_RANGES['household_code_min_length']:
            errors.append(f"Household code too short (minimum {VALIDATION_RANGES['household_code_min_length']} characters)")
        elif len(code) > VALIDATION_RANGES['household_code_max_length']:
            errors.append(f"Household code too long (maximum {VALIDATION_RANGES['household_code_max_length']} characters)")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class MemberInfoValidator(BaseValidator):
    """Member information validator"""
    
    def validate(self, members: List[MemberInfo]) -> ValidationResult:
        """Validate member information"""
        errors = []
        warnings = []
        
        if not members:
            errors.append("No member information found")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        valid_relationships = set(self.normalization_maps['relationships'].values())
        
        for i, member in enumerate(members):
            member_prefix = f"Member {i+1}"
            
            # Check required fields
            if not member.name or not member.name.strip():
                errors.append(f"{member_prefix}: Missing name")
            
            if not member.relationship or not member.relationship.strip():
                errors.append(f"{member_prefix}: Missing relationship")
            
            # Validate relationship
            if member.relationship and member.relationship not in valid_relationships:
                warnings.append(f"{member_prefix}: Unknown relationship type '{member.relationship}'")
            
            # Validate birth year if provided
            if member.birth_year:
                try:
                    year = int(member.birth_year)
                    current_year = 2025  # Using current time reference
                    if year < 1900 or year > current_year:
                        warnings.append(f"{member_prefix}: Birth year {year} seems unreasonable")
                except ValueError:
                    warnings.append(f"{member_prefix}: Invalid birth year format '{member.birth_year}'")
            
            # Check completeness
            if not member.is_complete:
                warnings.append(f"{member_prefix}: Incomplete information")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class CrossValidator:
    """Cross-validator for comparing extracted values with input data"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_field_consistency(self, field_name: str, extracted_value: Any, input_data: Dict) -> Dict[str, Any]:
        """Validate consistency of một field với input data"""
        try:
            # Map field names to potential input keys
            field_mappings = {
                'so_dien_thoai': ['phone', 'dien_thoai', 'sdt'],
                'thu_nhap': ['income', 'salary', 'luong', 'thu_nhap'],
                'ngan_hang': ['bank', 'ngan_hang'],
                'ma_ho_gia_dinh': ['household_code', 'ma_ho', 'hgd'],
                'thong_tin_thanh_vien': ['members', 'thanh_vien', 'family']
            }
            
            possible_keys = field_mappings.get(field_name, [])
            
            for key in possible_keys:
                if key in input_data:
                    input_value = input_data[key]
                    consistency = self._compare_values(field_name, extracted_value, input_value)
                    
                    return {
                        'is_consistent': consistency['match'],
                        'input_key': key,
                        'input_value': input_value,
                        'extracted_value': extracted_value,
                        'similarity_score': consistency['similarity'],
                        'comparison_notes': consistency['notes']
                    }
            
            return {
                'is_consistent': True,  # No input to compare with
                'input_key': None,
                'note': 'No corresponding input data found'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _compare_values(self, field_name: str, extracted: Any, input_val: Any) -> Dict[str, Any]:
        """Compare extracted value với input value"""
        try:
            if field_name == 'so_dien_thoai':
                return self._compare_phone_values(extracted, input_val)
            elif field_name == 'thu_nhap':
                return self._compare_income_values(extracted, input_val)
            else:
                return self._compare_generic_values(extracted, input_val)
            
        except Exception as e:
            return {'match': False, 'similarity': 0.0, 'notes': f"Comparison error: {str(e)}"}
    
    def _compare_phone_values(self, extracted: str, input_val: str) -> Dict[str, Any]:
        """Compare phone numbers"""
        from ..normalizers.field_normalizers import PhoneNormalizer
        normalizer = PhoneNormalizer()
        
        norm_extracted = normalizer.normalize(str(extracted))
        norm_input = normalizer.normalize(str(input_val))
        
        match = norm_extracted == norm_input
        similarity = 1.0 if match else 0.0
        
        return {
            'match': match,
            'similarity': similarity,
            'notes': f"Normalized: {norm_extracted} vs {norm_input}"
        }
    
    def _compare_income_values(self, extracted: Any, input_val: Any) -> Dict[str, Any]:
        """Compare income values"""
        try:
            if isinstance(extracted, NormalizedIncome):
                extracted_amount = extracted.amount
            else:
                extracted_amount = extracted
            
            input_amount = float(str(input_val).replace(',', ''))
            extracted_amount = float(str(extracted_amount).replace(',', ''))
            
            diff_percent = abs(extracted_amount - input_amount) / max(input_amount, 1) * 100
            match = diff_percent < 10  # Allow 10% difference
            similarity = max(0, 1 - diff_percent / 100)
            
            return {
                'match': match,
                'similarity': similarity,
                'notes': f"Difference: {diff_percent:.1f}%"
            }
        except ValueError:
            return {'match': False, 'similarity': 0.0, 'notes': 'Cannot compare as numbers'}
    
    def _compare_generic_values(self, extracted: Any, input_val: Any) -> Dict[str, Any]:
        """Generic string comparison"""
        str_extracted = str(extracted).lower().strip()
        str_input = str(input_val).lower().strip()
        
        match = str_extracted == str_input
        
        # Calculate similarity (simple)
        if match:
            similarity = 1.0
        elif str_extracted in str_input or str_input in str_extracted:
            similarity = 0.7
        else:
            similarity = 0.0
        
        return {
            'match': match,
            'similarity': similarity,
            'notes': f"String comparison: '{str_extracted}' vs '{str_input}'"
        }


class ValidatorFactory:
    """Factory for creating validators"""
    
    _validators = {
        'so_dien_thoai': PhoneValidator,
        'thu_nhap': IncomeValidator,
        'ngan_hang': BankValidator,
        'ma_ho_gia_dinh': HouseholdCodeValidator,
        'thong_tin_thanh_vien': MemberInfoValidator
    }
    
    @classmethod
    def get_validator(cls, field_name: str) -> BaseValidator:
        """Get validator for field"""
        validator_class = cls._validators.get(field_name)
        if validator_class:
            return validator_class()
        else:
            return BaseValidator()
    
    @classmethod
    def register_validator(cls, field_name: str, validator_class: type):
        """Register custom validator"""
        cls._validators[field_name] = validator_class
    
    @classmethod
    def get_cross_validator(cls) -> CrossValidator:
        """Get cross-validator instance"""
        return CrossValidator()
