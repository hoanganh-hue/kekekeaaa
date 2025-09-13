import sqlite3
import json
import csv
import gzip
import shutil
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import threading
import hashlib


@dataclass
class StorageMetadata:
    """Storage metadata structure"""
    file_path: str
    format: str
    created_at: str
    updated_at: str
    size_bytes: int
    checksum: str
    compression: bool
    backup_count: int
    province_code: Optional[str] = None
    data_type: Optional[str] = None
    

class StorageInterface(ABC):
    """Abstract interface for storage implementations"""
    
    @abstractmethod
    def save(self, data: Any, identifier: str, metadata: Dict[str, Any]) -> bool:
        """Save data với identifier"""
        pass
    
    @abstractmethod
    def load(self, identifier: str) -> Optional[Any]:
        """Load data by identifier"""
        pass
    
    @abstractmethod
    def exists(self, identifier: str) -> bool:
        """Check if data exists"""
        pass
    
    @abstractmethod
    def delete(self, identifier: str) -> bool:
        """Delete data by identifier"""
        pass
    
    @abstractmethod
    def list_items(self) -> List[str]:
        """List all stored items"""
        pass


class JSONStorage(StorageInterface):
    """JSON file storage implementation"""
    
    def __init__(self, base_path: Path, compression: bool = True):
        self.base_path = Path(base_path)
        self.compression = compression
        self.logger = logging.getLogger(__name__)
        
        # Create directory if not exists
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, data: Any, identifier: str, metadata: Dict[str, Any] = None) -> bool:
        """Save data as JSON file"""
        try:
            file_path = self.base_path / f"{identifier}.json"
            
            # Add metadata to data
            save_data = {
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            if self.compression:
                with gzip.open(f"{file_path}.gz", 'wt', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                file_path = Path(f"{file_path}.gz")
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved JSON data to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving JSON data {identifier}: {e}")
            return False
    
    def load(self, identifier: str) -> Optional[Any]:
        """Load data from JSON file"""
        try:
            # Try compressed file first
            compressed_path = self.base_path / f"{identifier}.json.gz"
            regular_path = self.base_path / f"{identifier}.json"
            
            if compressed_path.exists():
                with gzip.open(compressed_path, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
            elif regular_path.exists():
                with open(regular_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                return None
            
            return data.get('data') if isinstance(data, dict) else data
            
        except Exception as e:
            self.logger.error(f"Error loading JSON data {identifier}: {e}")
            return None
    
    def exists(self, identifier: str) -> bool:
        """Check if JSON file exists"""
        compressed_path = self.base_path / f"{identifier}.json.gz"
        regular_path = self.base_path / f"{identifier}.json"
        return compressed_path.exists() or regular_path.exists()
    
    def delete(self, identifier: str) -> bool:
        """Delete JSON file"""
        try:
            compressed_path = self.base_path / f"{identifier}.json.gz"
            regular_path = self.base_path / f"{identifier}.json"
            
            deleted = False
            if compressed_path.exists():
                compressed_path.unlink()
                deleted = True
            if regular_path.exists():
                regular_path.unlink()
                deleted = True
                
            return deleted
            
        except Exception as e:
            self.logger.error(f"Error deleting JSON data {identifier}: {e}")
            return False
    
    def list_items(self) -> List[str]:
        """List all JSON files"""
        items = []
        for file_path in self.base_path.glob("*.json*"):
            identifier = file_path.stem
            if file_path.suffix == '.gz':
                identifier = identifier.replace('.json', '')
            items.append(identifier)
        return list(set(items))


class CSVStorage(StorageInterface):
    """CSV file storage implementation"""
    
    def __init__(self, base_path: Path, compression: bool = True):
        self.base_path = Path(base_path)
        self.compression = compression
        self.logger = logging.getLogger(__name__)
        
        # Create directory if not exists
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, data: Any, identifier: str, metadata: Dict[str, Any] = None) -> bool:
        """Save data as CSV file"""
        try:
            file_path = self.base_path / f"{identifier}.csv"
            
            # Convert data to list of dictionaries if needed
            if not isinstance(data, list):
                if isinstance(data, dict):
                    data = [data]
                else:
                    return False
            
            if not data:
                return False
            
            # Get fieldnames from first item
            fieldnames = list(data[0].keys())
            
            if self.compression:
                with gzip.open(f"{file_path}.gz", 'wt', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                file_path = Path(f"{file_path}.gz")
            else:
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            
            self.logger.debug(f"Saved CSV data to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving CSV data {identifier}: {e}")
            return False
    
    def load(self, identifier: str) -> Optional[List[Dict]]:
        """Load data from CSV file"""
        try:
            compressed_path = self.base_path / f"{identifier}.csv.gz"
            regular_path = self.base_path / f"{identifier}.csv"
            
            if compressed_path.exists():
                with gzip.open(compressed_path, 'rt', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    return list(reader)
            elif regular_path.exists():
                with open(regular_path, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    return list(reader)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading CSV data {identifier}: {e}")
            return None
    
    def exists(self, identifier: str) -> bool:
        """Check if CSV file exists"""
        compressed_path = self.base_path / f"{identifier}.csv.gz"
        regular_path = self.base_path / f"{identifier}.csv"
        return compressed_path.exists() or regular_path.exists()
    
    def delete(self, identifier: str) -> bool:
        """Delete CSV file"""
        try:
            compressed_path = self.base_path / f"{identifier}.csv.gz"
            regular_path = self.base_path / f"{identifier}.csv"
            
            deleted = False
            if compressed_path.exists():
                compressed_path.unlink()
                deleted = True
            if regular_path.exists():
                regular_path.unlink()
                deleted = True
                
            return deleted
            
        except Exception as e:
            self.logger.error(f"Error deleting CSV data {identifier}: {e}")
            return False
    
    def list_items(self) -> List[str]:
        """List all CSV files"""
        items = []
        for file_path in self.base_path.glob("*.csv*"):
            identifier = file_path.stem
            if file_path.suffix == '.gz':
                identifier = identifier.replace('.csv', '')
            items.append(identifier)
        return list(set(items))


class SQLiteStorage(StorageInterface):
    """SQLite database storage implementation"""
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Create directory if not exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database với required tables"""
        with self.lock:
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # Create main data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vss_data (
                        identifier TEXT PRIMARY KEY,
                        data_type TEXT,
                        province_code TEXT,
                        data_json TEXT,
                        metadata_json TEXT,
                        created_at TEXT,
                        updated_at TEXT,
                        checksum TEXT
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_province_code ON vss_data(province_code)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_type ON vss_data(data_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON vss_data(created_at)")
                
                conn.commit()
                conn.close()
                
                self.logger.debug(f"SQLite database initialized at {self.db_path}")
                
            except Exception as e:
                self.logger.error(f"Error initializing SQLite database: {e}")
                raise
    
    def save(self, data: Any, identifier: str, metadata: Dict[str, Any] = None) -> bool:
        """Save data to SQLite database"""
        with self.lock:
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # Serialize data
                data_json = json.dumps(data, ensure_ascii=False)
                metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
                
                # Calculate checksum
                checksum = hashlib.sha256(data_json.encode('utf-8')).hexdigest()
                
                # Extract metadata fields
                province_code = metadata.get('province_code') if metadata else None
                data_type = metadata.get('data_type') if metadata else None
                
                # Insert or update
                cursor.execute("""
                    INSERT OR REPLACE INTO vss_data 
                    (identifier, data_type, province_code, data_json, metadata_json, 
                     created_at, updated_at, checksum)
                    VALUES (?, ?, ?, ?, ?, 
                           COALESCE((SELECT created_at FROM vss_data WHERE identifier = ?), ?),
                           ?, ?)
                """, (
                    identifier, data_type, province_code, data_json, metadata_json,
                    identifier, datetime.now().isoformat(),
                    datetime.now().isoformat(), checksum
                ))
                
                conn.commit()
                conn.close()
                
                self.logger.debug(f"Saved data to SQLite: {identifier}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error saving SQLite data {identifier}: {e}")
                return False
    
    def load(self, identifier: str) -> Optional[Any]:
        """Load data from SQLite database"""
        with self.lock:
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT data_json FROM vss_data WHERE identifier = ?", (identifier,))
                result = cursor.fetchone()
                
                conn.close()
                
                if result:
                    return json.loads(result[0])
                else:
                    return None
                    
            except Exception as e:
                self.logger.error(f"Error loading SQLite data {identifier}: {e}")
                return None
    
    def exists(self, identifier: str) -> bool:
        """Check if data exists in SQLite database"""
        with self.lock:
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT 1 FROM vss_data WHERE identifier = ?", (identifier,))
                result = cursor.fetchone()
                
                conn.close()
                
                return result is not None
                
            except Exception as e:
                self.logger.error(f"Error checking SQLite data existence {identifier}: {e}")
                return False
    
    def delete(self, identifier: str) -> bool:
        """Delete data from SQLite database"""
        with self.lock:
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM vss_data WHERE identifier = ?", (identifier,))
                deleted = cursor.rowcount > 0
                
                conn.commit()
                conn.close()
                
                return deleted
                
            except Exception as e:
                self.logger.error(f"Error deleting SQLite data {identifier}: {e}")
                return False
    
    def list_items(self) -> List[str]:
        """List all items in SQLite database"""
        with self.lock:
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT identifier FROM vss_data ORDER BY created_at")
                results = cursor.fetchall()
                
                conn.close()
                
                return [result[0] for result in results]
                
            except Exception as e:
                self.logger.error(f"Error listing SQLite data: {e}")
                return []
    
    def query_by_province(self, province_code: str) -> List[Dict[str, Any]]:
        """Query data by province code"""
        with self.lock:
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT identifier, data_type, data_json, metadata_json, created_at, updated_at
                    FROM vss_data 
                    WHERE province_code = ?
                    ORDER BY created_at DESC
                """, (province_code,))
                results = cursor.fetchall()
                
                conn.close()
                
                return [
                    {
                        "identifier": row[0],
                        "data_type": row[1],
                        "data": json.loads(row[2]),
                        "metadata": json.loads(row[3]),
                        "created_at": row[4],
                        "updated_at": row[5]
                    } for row in results
                ]
                
            except Exception as e:
                self.logger.error(f"Error querying SQLite data by province {province_code}: {e}")
                return []


class VSSDataStorage:
    """Comprehensive data storage manager cho VSS system"""
    
    def __init__(self, base_directory: str = "data/collected", 
                 formats: List[str] = None, compression: bool = True,
                 backup_enabled: bool = True, backup_interval: int = 3600):
        """Initialize data storage manager"""
        self.base_directory = Path(base_directory)
        self.formats = formats or ["json", "csv", "sqlite"]
        self.compression = compression
        self.backup_enabled = backup_enabled
        self.backup_interval = backup_interval
        self.logger = logging.getLogger(__name__)
        
        # Create base directory if not exists
        self.base_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage instances
        self.json_storage = JSONStorage(self.base_directory / "json", compression)
        self.csv_storage = CSVStorage(self.base_directory / "csv", compression)
        self.sqlite_storage = SQLiteStorage(self.base_directory / "vss_data.db")
        
        # Backup thread
        self._backup_thread = None
        self._stop_backup_event = threading.Event()
        
        if self.backup_enabled:
            self._start_backup_thread()
            
    def _start_backup_thread(self):
        """Start background backup thread"""
        if self._backup_thread is None or not self._backup_thread.is_alive():
            self._stop_backup_event.clear()
            self._backup_thread = threading.Thread(target=self._backup_worker)
            self._backup_thread.daemon = True
            self._backup_thread.start()
            self.logger.info("Started data backup thread")
            
    def _backup_worker(self):
        """Background worker for data backups"""
        while not self._stop_backup_event.is_set():
            self.logger.info("Performing scheduled data backup...")
            self.perform_backup()
            self._stop_backup_event.wait(self.backup_interval)
            
        self.logger.info("Data backup thread stopped")
            
    def stop_backup_thread(self):
        """Stop background backup thread"""
        if self._backup_thread and self._backup_thread.is_alive():
            self._stop_backup_event.set()
            self._backup_thread.join()
            self.logger.info("Stopped data backup thread")
            
    def perform_backup(self):
        """Perform a full backup of collected data"""
        backup_dir = self.base_directory.parent / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Backup JSON files
            shutil.copytree(self.base_directory / "json", backup_dir / "json", dirs_exist_ok=True)
            
            # Backup CSV files
            shutil.copytree(self.base_directory / "csv", backup_dir / "csv", dirs_exist_ok=True)
            
            # Backup SQLite database
            shutil.copy2(self.sqlite_storage.db_path, backup_dir / self.sqlite_storage.db_path.name)
            
            self.logger.info(f"Data backup completed to {backup_dir}")
            
        except Exception as e:
            self.logger.error(f"Error during data backup: {e}")
            
    def save_province_data(self, province_code: str, data_type: str, data: Any, metadata: Dict[str, Any] = None) -> bool:
        """Save data for a specific province and data type"""
        success = True
        identifier = f"{province_code}_{data_type}"
        full_metadata = metadata or {}
        full_metadata["province_code"] = province_code
        full_metadata["data_type"] = data_type
        
        if "json" in self.formats:
            if not self.json_storage.save(data, identifier, full_metadata):
                success = False
        
        if "csv" in self.formats and isinstance(data, list) and all(isinstance(item, dict) for item in data):
            if not self.csv_storage.save(data, identifier, full_metadata):
                success = False
        
        if "sqlite" in self.formats:
            if not self.sqlite_storage.save(data, identifier, full_metadata):
                success = False
                
        return success
    
    def load_province_data(self, province_code: str, data_type: str, format: str = "json") -> Optional[Any]:
        """Load data for a specific province and data type"""
        identifier = f"{province_code}_{data_type}"
        
        if format == "json":
            return self.json_storage.load(identifier)
        elif format == "csv":
            return self.csv_storage.load(identifier)
        elif format == "sqlite":
            return self.sqlite_storage.load(identifier)
        else:
            self.logger.warning(f"Unsupported format for loading: {format}")
            return None
            
    def get_province_data_identifiers(self, province_code: str) -> List[str]:
        """Get all data identifiers for a given province"""
        return self.sqlite_storage.query_by_province(province_code)
    
    def get_all_data_identifiers(self) -> List[str]:
        """Get all data identifiers across all storage types"""
        json_ids = self.json_storage.list_items()
        csv_ids = self.csv_storage.list_items()
        sqlite_ids = self.sqlite_storage.list_items()
        return list(set(json_ids + csv_ids + sqlite_ids))
    
    def delete_province_data(self, province_code: str, data_type: str) -> bool:
        """Delete data for a specific province and data type from all formats"""
        success = True
        identifier = f"{province_code}_{data_type}"
        
        if not self.json_storage.delete(identifier):
            success = False
        if not self.csv_storage.delete(identifier):
            success = False
        if not self.sqlite_storage.delete(identifier):
            success = False
            
        return success
    
    def close(self):
        """Close storage connections and stop backup thread"""
        self.stop_backup_thread()
        # No explicit close needed for JSON/CSV, but SQLite might need it
        # self.sqlite_storage.close() # Assuming SQLiteStorage handles its own connection closing per operation


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Example usage
    storage = VSSDataStorage(base_directory="test_data_storage", formats=["json", "csv", "sqlite"], compression=True)
    
    # Create some dummy data
    province_data = {"ma": "001", "ten": "Hà Nội", "ma_tra_cuu": "HN"}
    district_data = [
        {"ma": "001001", "ten": "Ba Đình", "ma_tinh": "001"},
        {"ma": "001002", "ten": "Hoàn Kiếm", "ma_tinh": "001"}
    ]
    hospital_data = {"ma": "HN001", "ten": "Bệnh viện A", "dia_chi": "123 Đường ABC", "ma_tinh": "001"}
    
    # Save data
    print("Saving data...")
    storage.save_province_data("001", "province", province_data)
    storage.save_province_data("001", "districts", district_data)
    storage.save_province_data("001", "hospital", hospital_data)
    
    # Load data
    print("\nLoading data...")
    loaded_province = storage.load_province_data("001", "province", "json")
    print(f"Loaded Province (JSON): {loaded_province}")
    
    loaded_districts_csv = storage.load_province_data("001", "districts", "csv")
    print(f"Loaded Districts (CSV): {loaded_districts_csv}")
    
    loaded_hospital_sqlite = storage.load_province_data("001", "hospital", "sqlite")
    print(f"Loaded Hospital (SQLite): {loaded_hospital_sqlite}")
    
    # Check existence
    print("\nChecking existence...")
    print(f"Province 001_province exists: {storage.json_storage.exists('001_province')}")
    print(f"District 001_districts exists (CSV): {storage.csv_storage.exists('001_districts')}")
    print(f"Hospital 001_hospital exists (SQLite): {storage.sqlite_storage.exists('001_hospital')}")
    
    # List items
    print("\nListing items...")
    print(f"All JSON items: {storage.json_storage.list_items()}")
    print(f"All CSV items: {storage.csv_storage.list_items()}")
    print(f"All SQLite items: {storage.sqlite_storage.list_items()}")
    
    # Query by province (SQLite)
    print("\nQuerying SQLite by province...")
    province_001_data = storage.sqlite_storage.query_by_province("001")
    for item in province_001_data:
        print(f"  - {item['identifier']} ({item['data_type']})")
        
    # Perform backup
    print("\nPerforming backup...")
    storage.perform_backup()
    
    # Delete data
    print("\nDeleting data...")
    storage.delete_province_data("001", "province")
    print(f"Province 001_province exists after delete: {storage.json_storage.exists('001_province')}")
    
    # Clean up test data
    print("\nCleaning up test data...")
    shutil.rmtree("test_data_storage", ignore_errors=True)
    shutil.rmtree(storage.base_directory.parent / "backups", ignore_errors=True)
    
    # Stop backup thread
    storage.close()
    print("Done.")

