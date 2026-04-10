"""
Firestore client wrapper for database operations
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client

logger = logging.getLogger(__name__)


class FirestoreClient:
    """Wrapper for Firebase Firestore operations"""
    
    def __init__(self, credentials_path: Optional[str] = None, database_id: Optional[str] = None):
        """
        Initialize Firestore client
        
        Args:
            credentials_path: Path to service account JSON file
            database_id: Firestore database ID (optional, defaults to project's default database)
        """
        self.credentials_path = credentials_path or self._find_credentials()
        self.database_id = database_id or self._get_database_id()
        self.db: Optional[Client] = None
        self._initialize()
    
    def _find_credentials(self) -> str:
        """Find Firebase credentials file"""
        possible_paths = [
            Path(__file__).parent.parent / 'config' / 'firebase-credentials.json',
            Path.cwd() / 'config' / 'firebase-credentials.json',
            Path.cwd() / 'firebase-credentials.json',
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found credentials at: {path}")
                return str(path)
        
        raise FileNotFoundError(
            "Firebase credentials not found. Please place firebase-credentials.json in database/config/ directory.\n"
            "Get it from: Firebase Console → Project Settings → Service Accounts → Generate New Private Key"
        )
    
    def _get_database_id(self) -> Optional[str]:
        """Get database ID from firebase-applet-config.json if available"""
        try:
            config_path = Path(__file__).parent.parent.parent / 'firebase-applet-config.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    db_id = config.get('firestoreDatabaseId')
                    if db_id:
                        logger.info(f"Using Firestore database: {db_id}")
                        return db_id
        except Exception as e:
            logger.warning(f"Could not read firebase-applet-config.json: {e}")
        
        return None
    
    def _initialize(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            try:
                firebase_admin.get_app()
                logger.info("Firebase app already initialized")
            except ValueError:
                # Initialize new app
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase app initialized successfully")
            
            # Get Firestore client
            if self.database_id:
                self.db = firestore.client(database_id=self.database_id)
            else:
                self.db = firestore.client()
            
            logger.info("Firestore client connected")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            raise
    
    def get_collection(self, collection_name: str) -> List[Dict[str, Any]]:
        """
        Get all documents from a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            List of documents as dictionaries
        """
        try:
            docs = self.db.collection(collection_name).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.error(f"Error getting collection '{collection_name}': {e}")
            raise
    
    def set_document(self, collection_name: str, doc_id: str, data: Dict[str, Any]):
        """
        Set a document in a collection
        
        Args:
            collection_name: Name of the collection
            doc_id: Document ID
            data: Document data
        """
        try:
            self.db.collection(collection_name).document(doc_id).set(data)
        except Exception as e:
            logger.error(f"Error setting document '{doc_id}' in '{collection_name}': {e}")
            raise
    
    def delete_document(self, collection_name: str, doc_id: str):
        """
        Delete a document from a collection
        
        Args:
            collection_name: Name of the collection
            doc_id: Document ID
        """
        try:
            self.db.collection(collection_name).document(doc_id).delete()
        except Exception as e:
            logger.error(f"Error deleting document '{doc_id}' from '{collection_name}': {e}")
            raise
    
    def clear_collection(self, collection_name: str, batch_size: int = 500) -> int:
        """
        Delete all documents in a collection
        
        Args:
            collection_name: Name of the collection
            batch_size: Number of documents to delete per batch
            
        Returns:
            Number of documents deleted
        """
        try:
            deleted = 0
            docs = self.db.collection(collection_name).limit(batch_size).stream()
            
            while True:
                batch_docs = list(docs)
                if not batch_docs:
                    break
                
                batch = self.db.batch()
                for doc in batch_docs:
                    batch.delete(doc.reference)
                    deleted += 1
                
                batch.commit()
                docs = self.db.collection(collection_name).limit(batch_size).stream()
            
            logger.info(f"Cleared {deleted} documents from '{collection_name}'")
            return deleted
            
        except Exception as e:
            logger.error(f"Error clearing collection '{collection_name}': {e}")
            raise
    
    def batch_set(self, collection_name: str, documents: List[Dict[str, Any]], batch_size: int = 500) -> int:
        """
        Batch write documents to a collection
        
        Args:
            collection_name: Name of the collection
            documents: List of documents (must have 'id' field)
            batch_size: Number of documents per batch
            
        Returns:
            Number of documents written
        """
        try:
            written = 0
            
            for i in range(0, len(documents), batch_size):
                batch = self.db.batch()
                batch_docs = documents[i:i + batch_size]
                
                for doc_data in batch_docs:
                    if 'id' not in doc_data:
                        logger.warning(f"Skipping document without 'id' field")
                        continue
                    
                    doc_id = doc_data['id']
                    doc_ref = self.db.collection(collection_name).document(doc_id)
                    batch.set(doc_ref, doc_data)
                    written += 1
                
                batch.commit()
                logger.debug(f"Wrote batch {i // batch_size + 1}: {len(batch_docs)} documents")
            
            logger.info(f"Wrote {written} documents to '{collection_name}'")
            return written
            
        except Exception as e:
            logger.error(f"Error batch writing to '{collection_name}': {e}")
            raise
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection has any documents"""
        try:
            docs = self.db.collection(collection_name).limit(1).stream()
            return len(list(docs)) > 0
        except Exception as e:
            logger.error(f"Error checking collection '{collection_name}': {e}")
            return False
    
    def get_document_count(self, collection_name: str) -> int:
        """Get the number of documents in a collection"""
        try:
            docs = self.db.collection(collection_name).stream()
            return len(list(docs))
        except Exception as e:
            logger.error(f"Error counting documents in '{collection_name}': {e}")
            return 0
