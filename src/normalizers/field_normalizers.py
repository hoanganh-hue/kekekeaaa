#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Enhanced Extractor - Field Normalizers
Chứa các normalizer classes cho từng loại field.

Author: MiniMax Agent
Date: 2025-09-13
Version: 2.1
"""

import re
import logging
from typing import Any, List, Dict, Optional
from ..config.data_models import MemberInfo, NormalizedIncome, NormalizedBank
from ..config.patterns import NormalizationMappingsConfig


class BaseNormalizer:
    """Base normalizer class"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.normalization_maps = NormalizationMappingsConfig.get_normalization_maps()
    
    def normalize(self, value: Any) -> Any:
        """Override in subclasses"""
        raise NotImplementedError


class PhoneNormalizer(BaseNormalizer):
    """Phone number normalizer"""
    
    def normalize(self, phone: str) -> str:
        """Normalize Vietnam phone number"""
        if not phone:
            return ""
        
        try:
            # Remove all non-digits
            digits = re.sub(r'\D', '', phone)
            
            # Handle +84 prefix
            if digits.startswith('84') and len(digits) >= 10:
                digits = '0' + digits[2:]
            
            # Validate Vietnam phone format
            if re.match(r'^0[1-9][0-9]{8,9}$', digits):
                return digits
            
            return phone  # Return original if can't normalize
            
        except Exception as e:
            self.logger.error(f"Error normalizing phone: {e}")
            return phone


class IncomeNormalizer(BaseNormalizer):
    """Income normalizer"""
    
    def normalize(self, income: str) -> NormalizedIncome:
        """Normalize income value"""
        if not income:
            return None
        
        try:
            # Extract numeric value
            numeric_str = re.sub(r'[^\d,.]', '', income)
            numeric_str = numeric_str.replace(',', '').replace('.', '')
            
            if numeric_str:
                amount = int(numeric_str)
                
                # Detect currency unit and apply multiplier
                currency = 'VND'
                multiplier_applied = None
                
                for unit, multiplier in self.normalization_maps['currency_multipliers'].items():
                    if unit in income.lower():
                        amount *= multiplier
                        multiplier_applied = unit
                        break
                
                return NormalizedIncome(
                    amount=amount,
                    currency=currency,
                    formatted=f"{amount:,} {currency}",
                    original=income,
                    parsing_successful=True,
                    multiplier_applied=multiplier_applied
                )
            
            return NormalizedIncome(
                amount=0,
                currency='VND',
                formatted=income,
                original=income,
                parsing_successful=False
            )
            
        except Exception as e:
            self.logger.error(f"Error normalizing income: {e}")
            return NormalizedIncome(
                amount=0,
                currency='VND',
                formatted=income,
                original=income,
                parsing_successful=False
            )


class BankNormalizer(BaseNormalizer):
    """Bank name normalizer"""
    
    def normalize(self, bank: str) -> NormalizedBank:
        """Normalize bank name"""
        if not bank:
            return None
        
        try:
            bank_upper = bank.upper().strip()
            
            # Check exact matches in mapping
            for code, full_name in self.normalization_maps['banks'].items():
                if code in bank_upper or code.lower() in bank.lower():
                    return NormalizedBank(
                        code=code,
                        full_name=full_name,
                        original=bank,
                        match_type="exact",
                        confidence=1.0
                    )
            
            # Check partial matches
            for code, full_name in self.normalization_maps['banks'].items():
                if any(word in bank_upper for word in code.split()):
                    return NormalizedBank(
                        code=code,
                        full_name=full_name,
                        original=bank,
                        match_type="partial",
                        confidence=0.8
                    )
            
            return NormalizedBank(
                code=None,
                full_name=bank.title(),
                original=bank,
                match_type="unknown",
                confidence=0.5
            )
            
        except Exception as e:
            self.logger.error(f"Error normalizing bank: {e}")
            return NormalizedBank(
                code=None,
                full_name=bank,
                original=bank,
                match_type="error",
                confidence=0.0
            )


class HouseholdCodeNormalizer(BaseNormalizer):
    """Household code normalizer"""
    
    def normalize(self, code: str) -> str:
        """Normalize household code"""
        if not code:
            return ""
        
        try:
            # Remove spaces and convert to uppercase
            normalized = re.sub(r'\s+', '', code.upper())
            
            # Validate format
            if re.match(r'^[A-Z0-9]{8,15}$', normalized):
                return normalized
            
            return code  # Return original if doesn't match expected format
            
        except Exception as e:
            self.logger.error(f"Error normalizing household code: {e}")
            return code


class MemberInfoNormalizer(BaseNormalizer):
    """Member information normalizer"""
    
    def normalize(self, member_text: str) -> List[MemberInfo]:
        """Normalize member information với enhanced logic cho multiple formats"""
        if not member_text:
            return []
        
        try:
            members = []
            
            # Handle different formats
            members.extend(self._extract_from_table_rows(member_text))
            if not members:
                members.extend(self._extract_from_json(member_text))
            if not members:
                members.extend(self._extract_from_structured_text(member_text))
            if not members:
                members.extend(self._extract_from_delimited_text(member_text))
            
            # Remove duplicates and return
            return self._remove_duplicates(members)
            
        except Exception as e:
            self.logger.error(f"Error normalizing member info: {e}")
            return [MemberInfo(name="Error", relationship="Error", additional_info={"error": str(e)})]

    def _extract_from_table_rows(self, text: str) -> List[MemberInfo]:
        """Extract from table row format"""
        members = []
        
        if '<tr>' in text.lower():
            tr_pattern = r'<tr>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*</tr>'
            tr_matches = re.findall(tr_pattern, text, re.IGNORECASE)
            
            for match in tr_matches:
                name, relationship, birth_year = [part.strip() for part in match]
                if name and relationship:
                    members.append(MemberInfo(
                        name=name,
                        relationship=self._normalize_relationship(relationship),
                        birth_year=birth_year if birth_year.isdigit() else None
                    ))
        
        return members

    def _extract_from_json(self, text: str) -> List[MemberInfo]:
        """Extract from JSON format"""
        members = []
        
        if '"name"' in text and '"relation' in text:
            json_pattern = r'"name":\s*"([^"]+)"[^}]*"relation":\s*"([^"]+)"[^}]*"birth_year":\s*"([^"]+)"'
            json_matches = re.findall(json_pattern, text)
            
            for match in json_matches:
                name, relationship, birth_year = match
                members.append(MemberInfo(
                    name=name.strip(),
                    relationship=self._normalize_relationship(relationship),
                    birth_year=birth_year.strip() if birth_year.isdigit() else None
                ))
        
        return members

    def _extract_from_structured_text(self, text: str) -> List[MemberInfo]:
        """Extract from structured text patterns"""
        members = []
        
        # Pattern 1: "Name - Relationship - Year"
        pattern1 = r'([A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+)\s*-\s*(Vợ|Chồng|Con|Cha|Mẹ|Anh|Chị|Em)\s*-\s*([0-9]{4})'
        matches1 = re.findall(pattern1, text, re.IGNORECASE)
        
        for match in matches1:
            name, relationship, birth_year = [part.strip() for part in match]
            members.append(MemberInfo(
                name=name,
                relationship=self._normalize_relationship(relationship),
                birth_year=birth_year
            ))
        
        # Pattern 2: "Relationship: Name (Year)" or "Relationship - Name (Year)"
        pattern2 = r'(Vợ|Chồng|Con|Cha|Mẹ|Anh|Chị|Em)[:\s-]*([A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+?)(?:\s*\(([0-9]{4})\))?'
        matches2 = re.findall(pattern2, text, re.IGNORECASE)
        
        for match in matches2:
            relationship, name, birth_year = match
            name = name.strip().rstrip(',').rstrip('(').strip()
            members.append(MemberInfo(
                name=name,
                relationship=self._normalize_relationship(relationship),
                birth_year=birth_year if birth_year else None
            ))
        
        # Pattern 3: "Name: Relationship"
        pattern3 = r'([A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+)(?:\s*:\s*)?(Vợ|Chồng|Con|Cha|Mẹ|Anh|Chị|Em)'
        matches3 = re.findall(pattern3, text, re.IGNORECASE)
        
        for match in matches3:
            name, relationship = [part.strip() for part in match]
            # Look for birth year nearby
            birth_year = None
            year_pattern = r'\b(19|20)\d{2}\b'
            year_match = re.search(year_pattern, text[text.find(name):text.find(name)+100])
            if year_match:
                birth_year = year_match.group(0)
            
            members.append(MemberInfo(
                name=name,
                relationship=self._normalize_relationship(relationship),
                birth_year=birth_year
            ))
        
        return members

    def _extract_from_delimited_text(self, text: str) -> List[MemberInfo]:
        """Extract from delimited text when structured patterns fail"""
        members = []
        
        # Handle pipe-separated data
        if '|' in text:
            segments = text.split('|')
        else:
            # Split by commas, semicolons, or newlines
            segments = re.split(r'[,;\n\r]', text)
        
        for segment in segments:
            segment = segment.strip()
            if not segment or len(segment) < 5:
                continue
            
            # Look for any relationship keywords
            relationships = ['vợ', 'chồng', 'con', 'cha', 'mẹ', 'anh', 'chị', 'em']
            if any(rel in segment.lower() for rel in relationships):
                member = {}
                
                # Try to extract name and relationship from the segment
                rel_pattern = r'([A-ZÀÁẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạâấầẩẫậăắằẳẵặèéẻẽẹêếềểễệíìỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+).*?(Vợ|Chồng|Con|Cha|Mẹ|Anh|Chị|Em)'
                rel_match = re.search(rel_pattern, segment, re.IGNORECASE)
                
                if rel_match:
                    name_part = rel_match.group(1).strip()
                    relationship_part = rel_match.group(2).strip()
                    
                    # Clean up name part
                    name_part = re.sub(r'[:-]', '', name_part).strip()
                    
                    # Look for birth year in the segment
                    birth_year = None
                    year_match = re.search(r'\b(19|20)\d{2}\b', segment)
                    if year_match:
                        birth_year = year_match.group(0)
                    
                    if name_part:
                        members.append(MemberInfo(
                            name=name_part,
                            relationship=self._normalize_relationship(relationship_part),
                            birth_year=birth_year
                        ))
        
        return members

    def _normalize_relationship(self, relationship: str) -> str:
        """Normalize family relationship"""
        if not relationship:
            return ""
        
        rel_lower = relationship.lower().strip()
        
        # Check in mapping
        for key, normalized in self.normalization_maps['relationships'].items():
            if key in rel_lower:
                return normalized
        
        return relationship.title()

    def _remove_duplicates(self, members: List[MemberInfo]) -> List[MemberInfo]:
        """Remove duplicate members based on name and relationship"""
        unique_members = []
        seen = set()
        
        for member in members:
            key = f"{member.name.lower().strip()}_{member.relationship.lower().strip()}"
            if key not in seen and member.name and member.relationship:
                seen.add(key)
                unique_members.append(member)
        
        return unique_members


class NormalizerFactory:
    """Factory for creating normalizers"""
    
    _normalizers = {
        'so_dien_thoai': PhoneNormalizer,
        'thu_nhap': IncomeNormalizer,
        'ngan_hang': BankNormalizer,
        'ma_ho_gia_dinh': HouseholdCodeNormalizer,
        'thong_tin_thanh_vien': MemberInfoNormalizer
    }
    
    @classmethod
    def get_normalizer(cls, field_name: str) -> BaseNormalizer:
        """Get normalizer for field"""
        normalizer_class = cls._normalizers.get(field_name)
        if normalizer_class:
            return normalizer_class()
        else:
            return BaseNormalizer()
    
    @classmethod
    def register_normalizer(cls, field_name: str, normalizer_class: type):
        """Register custom normalizer"""
        cls._normalizers[field_name] = normalizer_class
