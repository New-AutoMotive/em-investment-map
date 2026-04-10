"""
CSV parsing and conversion utilities
"""

import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class CSVParser:
    """Handle CSV file operations for database management"""
    
    @staticmethod
    def read_csv(file_path: str) -> List[Dict[str, Any]]:
        """
        Read CSV file and convert to list of dictionaries
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of dictionaries with row data
        """
        try:
            df = pd.read_csv(file_path)
            
            # Convert to list of dicts
            records = df.to_dict('records')
            
            # Clean up NaN values
            cleaned_records = []
            for record in records:
                cleaned = {}
                for key, value in record.items():
                    # Skip NaN values
                    if pd.isna(value):
                        cleaned[key] = None
                    else:
                        cleaned[key] = value
                cleaned_records.append(cleaned)
            
            logger.info(f"Read {len(cleaned_records)} records from {file_path}")
            return cleaned_records
            
        except Exception as e:
            logger.error(f"Error reading CSV file '{file_path}': {e}")
            raise
    
    @staticmethod
    def read_sites_csv(file_path: str) -> List[Dict[str, Any]]:
        """
        Read sites CSV and convert to proper format with nested location
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of site dictionaries with proper structure
        """
        try:
            records = CSVParser.read_csv(file_path)
            
            # Convert flat CSV structure to nested structure
            sites = []
            for record in records:
                site = {
                    'id': record.get('id'),
                    'name': record.get('name'),
                    'countryId': record.get('countryId'),
                    'type': record.get('type'),
                    'manufacturer': record.get('manufacturer'),
                    'location': {
                        'lat': float(record.get('location.lat', record.get('lat', 0))),
                        'lng': float(record.get('location.lng', record.get('lng', 0)))
                    }
                }
                
                # Add optional fields if present
                optional_fields = [
                    'produces', 'brands', 'city', 'description',
                    'evConversionPlans', 'investmentAmount', 
                    'source', 'sourceUrl'
                ]
                for field in optional_fields:
                    if record.get(field):
                        site[field] = record[field]
                
                sites.append(site)
            
            logger.info(f"Converted {len(sites)} sites from CSV")
            return sites
            
        except Exception as e:
            logger.error(f"Error reading sites CSV '{file_path}': {e}")
            raise
    
    @staticmethod
    def write_csv(data: List[Dict[str, Any]], file_path: str, flatten: bool = True):
        """
        Write data to CSV file
        
        Args:
            data: List of dictionaries to write
            file_path: Output file path
            flatten: Whether to flatten nested structures
        """
        try:
            if not data:
                logger.warning("No data to write to CSV")
                return
            
            # Flatten nested structures if requested
            if flatten:
                flattened_data = []
                for record in data:
                    flattened = CSVParser._flatten_dict(record)
                    flattened_data.append(flattened)
                data = flattened_data
            
            # Convert to DataFrame and write
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            
            logger.info(f"Wrote {len(data)} records to {file_path}")
            
        except Exception as e:
            logger.error(f"Error writing CSV file '{file_path}': {e}")
            raise
    
    @staticmethod
    def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """
        Flatten nested dictionary
        
        Args:
            d: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for flattened keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(CSVParser._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def read_json(file_path: str) -> List[Dict[str, Any]]:
        """
        Read JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of dictionaries (or single dict wrapped in list)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Wrap in list if single object
            if isinstance(data, dict):
                data = [data]
            
            logger.info(f"Read {len(data)} records from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error reading JSON file '{file_path}': {e}")
            raise
    
    @staticmethod
    def write_json(data: List[Dict[str, Any]], file_path: str, indent: int = 2):
        """
        Write data to JSON file
        
        Args:
            data: List of dictionaries to write
            file_path: Output file path
            indent: JSON indentation
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            logger.info(f"Wrote {len(data)} records to {file_path}")
            
        except Exception as e:
            logger.error(f"Error writing JSON file '{file_path}': {e}")
            raise
    
    @staticmethod
    def auto_read(file_path: str) -> List[Dict[str, Any]]:
        """
        Auto-detect file format and read
        
        Args:
            file_path: Path to file
            
        Returns:
            List of dictionaries
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == '.csv':
            # Check if it's a sites CSV (has location columns)
            df = pd.read_csv(file_path, nrows=1)
            if 'location.lat' in df.columns or 'lat' in df.columns:
                return CSVParser.read_sites_csv(file_path)
            else:
                return CSVParser.read_csv(file_path)
        elif suffix == '.json':
            return CSVParser.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
