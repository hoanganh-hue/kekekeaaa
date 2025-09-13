#!/usr/bin/env python3
"""
VSS Province Iterator
Logic để query theo từng tỉnh trong 63 provinces với priority-based processing

Author: MiniMax Agent
Date: 2025-09-12
"""

import json
import logging
from typing import List, Dict, Iterator, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import random
from enum import Enum


class ProcessingPriority(Enum):
    """Processing priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Region(Enum):
    """Vietnamese regions"""
    NORTH = "north"
    CENTRAL = "central"
    SOUTH = "south"


@dataclass
class ProvinceInfo:
    """Province information structure"""
    code: str
    name: str
    region: Region
    priority: ProcessingPriority
    population: Optional[int] = None
    is_major_city: bool = False
    lookup_code: Optional[str] = None
    processing_order: int = 0
    estimated_data_volume: str = "medium"
    last_processed: Optional[str] = None
    success_rate: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        result['region'] = self.region.value
        result['priority'] = self.priority.value
        return result


class ProvinceIterator:
    """Intelligent province iterator với priority-based processing"""
    
    def __init__(self, config_path: str = "config/provinces.json"):
        """Initialize province iterator"""
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Load province data
        self.provinces = self._load_provinces()
        
        # Processing statistics
        self.processing_stats = {
            'total_provinces': len(self.provinces),
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        
    def _load_provinces(self) -> Dict[str, ProvinceInfo]:
        """Load province configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    provinces = {}
                    for code, info in data.items():
                        provinces[code] = ProvinceInfo(
                            code=code,
                            name=info['name'],
                            region=Region(info['region']),
                            priority=ProcessingPriority(info['priority']),
                            population=info.get('population'),
                            is_major_city=info.get('is_major_city', False),
                            lookup_code=info.get('lookup_code'),
                            processing_order=info.get('processing_order', 999),
                            estimated_data_volume=info.get('estimated_data_volume', 'medium'),
                            last_processed=info.get('last_processed'),
                            success_rate=info.get('success_rate', 0.0)
                        )
                    return provinces
            else:
                self.logger.warning(f"Province config file not found: {self.config_path}")
                return self._get_default_provinces()
                
        except Exception as e:
            self.logger.error(f"Error loading province config: {e}")
            return self._get_default_provinces()
    
    def _get_default_provinces(self) -> Dict[str, ProvinceInfo]:
        """Get default province configuration based on database schema analysis"""
        # Major cities với high priority
        major_cities = {
            '001': ('Hà Nội', Region.NORTH, True, 8500000),
            '079': ('TP. Hồ Chí Minh', Region.SOUTH, True, 9000000),
            '031': ('Hải Phòng', Region.NORTH, True, 2000000),
            '048': ('Đà Nẵng', Region.CENTRAL, True, 1200000),
            '092': ('Cần Thơ', Region.SOUTH, True, 1200000)
        }
        
        # Northern provinces (002-037, excluding major cities)
        northern_provinces = {
            '002': 'Hà Giang', '004': 'Cao Bằng', '006': 'Bắc Kạn', '008': 'Tuyên Quang',
            '010': 'Lào Cai', '011': 'Điện Biên', '012': 'Lai Châu', '014': 'Sơn La',
            '015': 'Yên Bái', '017': 'Hòa Bình', '019': 'Thái Nguyên', '020': 'Lạng Sơn',
            '022': 'Quảng Ninh', '024': 'Bắc Giang', '025': 'Phú Thọ', '026': 'Vĩnh Phúc',
            '027': 'Bắc Ninh', '030': 'Hà Nam', '033': 'Hưng Yên', '034': 'Thái Bình',
            '035': 'Hà Tây', '036': 'Ninh Bình', '037': 'Nam Định'
        }
        
        # Central provinces (038-068)
        central_provinces = {
            '038': 'Thanh Hóa', '040': 'Nghệ An', '042': 'Hà Tĩnh', '044': 'Quảng Bình',
            '045': 'Quảng Trị', '046': 'Thừa Thiên Huế', '049': 'Quảng Nam',
            '051': 'Quảng Ngãi', '052': 'Bình Định', '054': 'Phú Yên', '056': 'Khánh Hòa',
            '058': 'Ninh Thuận', '060': 'Bình Thuận', '062': 'Kon Tum', '064': 'Gia Lai',
            '066': 'Đắk Lắk', '067': 'Đắk Nông', '068': 'Lâm Đồng'
        }
        
        # Southern provinces (070-096, excluding major cities)
        southern_provinces = {
            '070': 'Bình Phước', '072': 'Tây Ninh', '074': 'Bình Dương', '075': 'Đồng Nai',
            '077': 'Bà Rịa - Vũng Tàu', '080': 'Long An', '082': 'Tiền Giang',
            '083': 'Bến Tre', '084': 'Trà Vinh', '086': 'Vĩnh Long', '087': 'Đồng Tháp',
            '089': 'An Giang', '091': 'Kiên Giang', '093': 'Hậu Giang',
            '094': 'Sóc Trăng', '095': 'Bạc Liêu', '096': 'Cà Mau'
        }
        
        provinces = {}
        
        # Add major cities với high priority
        for code, (name, region, is_major, population) in major_cities.items():
            provinces[code] = ProvinceInfo(
                code=code,
                name=name,
                region=region,
                priority=ProcessingPriority.HIGH,
                population=population,
                is_major_city=is_major,
                processing_order=int(code),
                estimated_data_volume="high"
            )
        
        # Add northern provinces với medium priority
        for code, name in northern_provinces.items():
            provinces[code] = ProvinceInfo(
                code=code,
                name=name,
                region=Region.NORTH,
                priority=ProcessingPriority.MEDIUM,
                processing_order=int(code),
                estimated_data_volume="medium"
            )
        
        # Add central provinces với medium priority
        for code, name in central_provinces.items():
            provinces[code] = ProvinceInfo(
                code=code,
                name=name,
                region=Region.CENTRAL,
                priority=ProcessingPriority.MEDIUM,
                processing_order=int(code),
                estimated_data_volume="medium"
            )
        
        # Add southern provinces với low priority (except major cities)
        for code, name in southern_provinces.items():
            provinces[code] = ProvinceInfo(
                code=code,
                name=name,
                region=Region.SOUTH,
                priority=ProcessingPriority.LOW,
                processing_order=int(code),
                estimated_data_volume="medium"
            )
        
        return provinces
    
    def get_processing_order(self, strategy: str = "priority_first") -> List[ProvinceInfo]:
        """Get provinces in optimal processing order"""
        if strategy == "priority_first":
            return self._priority_first_order()
        elif strategy == "geographic":
            return self._geographic_order()
        elif strategy == "size_based":
            return self._size_based_order()
        elif strategy == "success_rate":
            return self._success_rate_order()
        elif strategy == "random":
            return self._random_order()
        else:
            return self._priority_first_order()
    
    def _priority_first_order(self) -> List[ProvinceInfo]:
        """Order by priority: HIGH -> MEDIUM -> LOW"""
        ordered = []
        
        # High priority first (major cities)
        high_priority = [p for p in self.provinces.values() if p.priority == ProcessingPriority.HIGH]
        high_priority.sort(key=lambda x: x.processing_order)
        ordered.extend(high_priority)
        
        # Medium priority second  
        medium_priority = [p for p in self.provinces.values() if p.priority == ProcessingPriority.MEDIUM]
        medium_priority.sort(key=lambda x: x.processing_order)
        ordered.extend(medium_priority)
        
        # Low priority last
        low_priority = [p for p in self.provinces.values() if p.priority == ProcessingPriority.LOW]
        low_priority.sort(key=lambda x: x.processing_order)
        ordered.extend(low_priority)
        
        return ordered
    
    def _geographic_order(self) -> List[ProvinceInfo]:
        """Order by geographic regions: NORTH -> CENTRAL -> SOUTH"""
        ordered = []
        
        for region in [Region.NORTH, Region.CENTRAL, Region.SOUTH]:
            region_provinces = [p for p in self.provinces.values() if p.region == region]
            region_provinces.sort(key=lambda x: (x.priority.value, x.processing_order))
            ordered.extend(region_provinces)
            
        return ordered
    
    def _size_based_order(self) -> List[ProvinceInfo]:
        """Order by estimated data volume: high -> medium -> low"""
        volume_priority = {"high": 0, "large": 1, "medium": 2, "small": 3, "low": 4}
        
        ordered = list(self.provinces.values())
        ordered.sort(key=lambda x: (volume_priority.get(x.estimated_data_volume, 5), x.processing_order))
        
        return ordered
    
    def _success_rate_order(self) -> List[ProvinceInfo]:
        """Order by historical success rate (highest first)"""
        ordered = list(self.provinces.values())
        ordered.sort(key=lambda x: (-x.success_rate, x.processing_order))
        
        return ordered
    
    def _random_order(self) -> List[ProvinceInfo]:
        """Random order (for testing)"""
        ordered = list(self.provinces.values())
        random.shuffle(ordered)
        
        return ordered
    
    def get_province_batches(self, batch_size: int = 10, strategy: str = "priority_first") -> List[List[ProvinceInfo]]:
        """Get provinces organized in optimal batches"""
        ordered_provinces = self.get_processing_order(strategy)
        
        batches = []
        for i in range(0, len(ordered_provinces), batch_size):
            batch = ordered_provinces[i:i + batch_size]
            batches.append(batch)
            
        return batches
    
    def get_provinces_by_region(self, region: Region) -> List[ProvinceInfo]:
        """Get all provinces in a specific region"""
        return [p for p in self.provinces.values() if p.region == region]
    
    def get_provinces_by_priority(self, priority: ProcessingPriority) -> List[ProvinceInfo]:
        """Get all provinces with specific priority"""
        return [p for p in self.provinces.values() if p.priority == priority]
    
    def get_major_cities(self) -> List[ProvinceInfo]:
        """Get all major cities"""
        return [p for p in self.provinces.values() if p.is_major_city]
    
    def get_province(self, code: str) -> Optional[ProvinceInfo]:
        """Get specific province by code"""
        return self.provinces.get(code)
    
    def update_processing_stats(self, code: str, success: bool, processing_time: float = 0.0):
        """Update processing statistics for a province"""
        if code in self.provinces:
            province = self.provinces[code]
            
            # Update success rate (simple moving average)
            if success:
                province.success_rate = (province.success_rate * 0.8) + (1.0 * 0.2)
                self.processing_stats['successful'] += 1
            else:
                province.success_rate = (province.success_rate * 0.8) + (0.0 * 0.2)
                self.processing_stats['failed'] += 1
                
            province.last_processed = self._get_current_timestamp()
            self.processing_stats['processed'] += 1
            
            self.logger.info(f"Updated stats for {code}: success={success}, rate={province.success_rate:.2f}")
    
    def get_processing_statistics(self) -> Dict:
        """Get current processing statistics"""
        stats = self.processing_stats.copy()
        
        stats['completion_rate'] = (stats['processed'] / stats['total_provinces']) * 100
        stats['success_rate'] = (stats['successful'] / max(stats['processed'], 1)) * 100
        
        # Regional statistics
        stats['by_region'] = {}
        for region in Region:
            region_provinces = self.get_provinces_by_region(region)
            processed_in_region = sum(1 for p in region_provinces if p.last_processed)
            stats['by_region'][region.value] = {
                'total': len(region_provinces),
                'processed': processed_in_region,
                'completion_rate': (processed_in_region / len(region_provinces)) * 100
            }
        
        return stats
    
    def save_provinces_config(self, file_path: Optional[str] = None):
        """Save current province configuration"""
        save_path = Path(file_path) if file_path else self.config_path
        
        try:
            # Create directory if not exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to serializable format
            data = {}
            for code, province in self.provinces.items():
                data[code] = province.to_dict()
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Province configuration saved to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving province configuration: {e}")
            raise
    
    def iterator(self, strategy: str = "priority_first", batch_size: Optional[int] = None) -> Iterator[ProvinceInfo]:
        """Create iterator for provinces"""
        if batch_size:
            batches = self.get_province_batches(batch_size, strategy)
            for batch in batches:
                for province in batch:
                    yield province
        else:
            ordered_provinces = self.get_processing_order(strategy)
            for province in ordered_provinces:
                yield province
    
    def batch_iterator(self, batch_size: int = 10, strategy: str = "priority_first") -> Iterator[List[ProvinceInfo]]:
        """Create batch iterator for provinces"""
        batches = self.get_province_batches(batch_size, strategy)
        for batch in batches:
            yield batch
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_remaining_provinces(self) -> List[ProvinceInfo]:
        """Get provinces that haven't been processed yet"""
        return [p for p in self.provinces.values() if not p.last_processed]
    
    def get_failed_provinces(self) -> List[ProvinceInfo]:
        """Get provinces với success rate thấp"""
        return [p for p in self.provinces.values() if p.success_rate < 0.5 and p.last_processed]
    
    def reset_processing_stats(self):
        """Reset all processing statistics"""
        for province in self.provinces.values():
            province.last_processed = None
            province.success_rate = 0.0
            
        self.processing_stats = {
            'total_provinces': len(self.provinces),
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        
        self.logger.info("Processing statistics reset")


if __name__ == "__main__":
    # Example usage
    iterator = ProvinceIterator()
    
    print(f"Total provinces: {len(iterator.provinces)}")
    print(f"Major cities: {len(iterator.get_major_cities())}")
    
    # Test different ordering strategies
    for strategy in ["priority_first", "geographic", "size_based"]:
        print(f"\n{strategy.upper()} ordering:")
        provinces = iterator.get_processing_order(strategy)[:5]  # First 5
        for i, province in enumerate(provinces, 1):
            print(f"{i}. {province.code} - {province.name} ({province.priority.value})")
    
    # Test batch processing
    print("\nBatch processing (size=5):")
    for i, batch in enumerate(iterator.batch_iterator(batch_size=5), 1):
        print(f"Batch {i}: {[p.code for p in batch]}")
        if i >= 3:  # Show first 3 batches only
            break
