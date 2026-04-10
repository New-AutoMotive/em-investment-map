"""
Database operations (CRUD, merge, sync, etc.)
"""

import logging
from typing import List, Dict, Any, Optional, Literal
from tqdm import tqdm

from .firestore_client import FirestoreClient
from .csv_parser import CSVParser
from .validators import validate_batch_countries, validate_batch_sites

logger = logging.getLogger(__name__)

UpdateMode = Literal['merge', 'sync', 'add-new', 'replace']


class DatabaseOperations:
    """High-level database operations"""
    
    def __init__(self, client: FirestoreClient):
        """
        Initialize operations handler
        
        Args:
            client: Initialized Firestore client
        """
        self.client = client
    
    def seed_database(
        self,
        countries_file: Optional[str] = None,
        sites_file: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Seed entire database (replace all data)
        
        Args:
            countries_file: Path to countries data file (CSV or JSON)
            sites_file: Path to sites data file (CSV or JSON)
            dry_run: If True, only validate without writing
            
        Returns:
            Dictionary with operation counts
        """
        results = {'countries': 0, 'sites': 0, 'errors': 0}
        
        try:
            # Seed countries
            if countries_file:
                logger.info(f"Seeding countries from {countries_file}")
                data = CSVParser.auto_read(countries_file)
                valid, invalid = validate_batch_countries(data)
                
                if invalid:
                    logger.warning(f"Found {len(invalid)} invalid country records")
                    for err in invalid:
                        logger.error(f"Row {err['row']}: {err['error']}")
                    results['errors'] += len(invalid)
                
                if valid and not dry_run:
                    # Clear existing
                    self.client.clear_collection('countries')
                    # Write new data
                    validated_dicts = [c.model_dump() for c in valid]
                    results['countries'] = self.client.batch_set('countries', validated_dicts)
                else:
                    results['countries'] = len(valid)
                    if dry_run:
                        logger.info(f"[DRY RUN] Would write {len(valid)} countries")
            
            # Seed sites
            if sites_file:
                logger.info(f"Seeding sites from {sites_file}")
                data = CSVParser.auto_read(sites_file)
                valid, invalid = validate_batch_sites(data)
                
                if invalid:
                    logger.warning(f"Found {len(invalid)} invalid site records")
                    for err in invalid:
                        logger.error(f"Row {err['row']}: {err['error']}")
                    results['errors'] += len(invalid)
                
                if valid and not dry_run:
                    # Clear existing
                    self.client.clear_collection('sites')
                    # Write new data
                    validated_dicts = [s.model_dump() for s in valid]
                    results['sites'] = self.client.batch_set('sites', validated_dicts)
                else:
                    results['sites'] = len(valid)
                    if dry_run:
                        logger.info(f"[DRY RUN] Would write {len(valid)} sites")
            
            return results
            
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            raise
    
    def update_collection(
        self,
        collection: str,
        file_path: str,
        mode: UpdateMode = 'merge',
        dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Update a collection with different merge strategies
        
        Args:
            collection: Collection name ('countries' or 'sites')
            file_path: Path to data file
            mode: Update mode (merge, sync, add-new, replace)
            dry_run: If True, only validate without writing
            
        Returns:
            Dictionary with operation counts
        """
        results = {'added': 0, 'updated': 0, 'deleted': 0, 'errors': 0}
        
        try:
            # Read and validate new data
            logger.info(f"Reading {collection} from {file_path}")
            data = CSVParser.auto_read(file_path)
            
            if collection == 'countries':
                valid, invalid = validate_batch_countries(data)
            elif collection == 'sites':
                valid, invalid = validate_batch_sites(data)
            else:
                raise ValueError(f"Unknown collection: {collection}")
            
            if invalid:
                logger.warning(f"Found {len(invalid)} invalid records")
                for err in invalid:
                    logger.error(f"Row {err['row']}: {err['error']}")
                results['errors'] = len(invalid)
            
            if not valid:
                logger.warning("No valid records to process")
                return results
            
            # Get existing data
            existing = self.client.get_collection(collection)
            existing_ids = {doc['id'] for doc in existing}
            new_data = {v.id: v.model_dump() for v in valid}
            new_ids = set(new_data.keys())
            
            # Determine operations based on mode
            if mode == 'replace':
                # Delete all and add new
                if not dry_run:
                    results['deleted'] = self.client.clear_collection(collection)
                    results['added'] = self.client.batch_set(collection, list(new_data.values()))
                else:
                    results['deleted'] = len(existing_ids)
                    results['added'] = len(new_ids)
                    logger.info(f"[DRY RUN] Would delete {results['deleted']} and add {results['added']} records")
            
            elif mode == 'merge':
                # Update existing + add new
                to_add = new_ids - existing_ids
                to_update = new_ids & existing_ids
                
                if not dry_run:
                    docs_to_write = [new_data[id] for id in (to_add | to_update)]
                    written = self.client.batch_set(collection, docs_to_write)
                    results['added'] = len(to_add)
                    results['updated'] = len(to_update)
                else:
                    results['added'] = len(to_add)
                    results['updated'] = len(to_update)
                    logger.info(f"[DRY RUN] Would add {results['added']} and update {results['updated']} records")
            
            elif mode == 'sync':
                # Update, add new, delete missing
                to_add = new_ids - existing_ids
                to_update = new_ids & existing_ids
                to_delete = existing_ids - new_ids
                
                if not dry_run:
                    # Add/update
                    docs_to_write = [new_data[id] for id in (to_add | to_update)]
                    self.client.batch_set(collection, docs_to_write)
                    # Delete
                    for id_to_delete in tqdm(to_delete, desc="Deleting"):
                        self.client.delete_document(collection, id_to_delete)
                    
                    results['added'] = len(to_add)
                    results['updated'] = len(to_update)
                    results['deleted'] = len(to_delete)
                else:
                    results['added'] = len(to_add)
                    results['updated'] = len(to_update)
                    results['deleted'] = len(to_delete)
                    logger.info(f"[DRY RUN] Would add {results['added']}, update {results['updated']}, delete {results['deleted']} records")
            
            elif mode == 'add-new':
                # Only add new records
                to_add = new_ids - existing_ids
                
                if not dry_run:
                    docs_to_write = [new_data[id] for id in to_add]
                    results['added'] = self.client.batch_set(collection, docs_to_write)
                else:
                    results['added'] = len(to_add)
                    logger.info(f"[DRY RUN] Would add {results['added']} new records")
            
            return results
            
        except Exception as e:
            logger.error(f"Error updating collection: {e}")
            raise
    
    def export_collection(
        self,
        collection: str,
        output_path: str,
        format: Literal['csv', 'json'] = 'csv'
    ) -> int:
        """
        Export collection to file
        
        Args:
            collection: Collection name
            output_path: Output file path
            format: Output format (csv or json)
            
        Returns:
            Number of records exported
        """
        try:
            logger.info(f"Exporting {collection} to {output_path}")
            data = self.client.get_collection(collection)
            
            if not data:
                logger.warning(f"Collection '{collection}' is empty")
                return 0
            
            if format == 'csv':
                CSVParser.write_csv(data, output_path, flatten=True)
            elif format == 'json':
                CSVParser.write_json(data, output_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Exported {len(data)} records")
            return len(data)
            
        except Exception as e:
            logger.error(f"Error exporting collection: {e}")
            raise
    
    def clear_collection(self, collection: str, confirm: bool = False) -> int:
        """
        Clear all documents from a collection
        
        Args:
            collection: Collection name
            confirm: Must be True to proceed
            
        Returns:
            Number of documents deleted
        """
        if not confirm:
            raise ValueError("Must explicitly confirm collection clearing")
        
        try:
            count = self.client.clear_collection(collection)
            logger.info(f"Cleared {count} documents from '{collection}'")
            return count
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise
