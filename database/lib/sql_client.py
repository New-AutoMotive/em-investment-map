"""
Google Cloud SQL (MySQL) client for battery tracker data
Uses the Cloud SQL Python Connector for secure IAM-authenticated connections.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CloudSQLClient:
    """Client for reading from Google Cloud SQL MySQL instance"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Cloud SQL client.

        Args:
            config_path: Path to sql-config.json. Defaults to config/sql-config.json
                         relative to the database/ directory.
        """
        self.config = self._load_config(config_path)
        self._connector = None
        self._connection = None

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load SQL connection config from JSON file."""
        if config_path:
            path = Path(config_path)
        else:
            # Default: look relative to the database/ root
            path = Path(__file__).parent.parent / "config" / "sql-config.json"

        if not path.exists():
            raise FileNotFoundError(
                f"SQL config not found at: {path}\n"
                "Please create database/config/sql-config.json with:\n"
                '  instance_connection_name, database, user, password, service_account_path'
            )

        with open(path, "r") as f:
            config = json.load(f)

        required = ["instance_connection_name", "database", "user", "password"]
        missing = [k for k in required if k not in config]
        if missing:
            raise ValueError(f"sql-config.json is missing required keys: {missing}")

        # Resolve service_account_path relative to database/ root
        sa_path_str = config.get("service_account_path")
        if sa_path_str:
            sa_path = Path(__file__).parent.parent / sa_path_str
            if not sa_path.exists():
                raise FileNotFoundError(
                    f"Service account file not found at: {sa_path}\n"
                    "Please follow the setup instructions to create a service account key\n"
                    "and save it as database/config/sql-credentials.json"
                )
            config["_resolved_sa_path"] = str(sa_path)

        logger.info(f"Loaded SQL config for instance: {config['instance_connection_name']}")
        return config

    def _get_credentials(self):
        """Load Google service account credentials."""
        from google.oauth2 import service_account

        sa_path = self.config.get("_resolved_sa_path")
        if not sa_path:
            # Fall back to application default credentials
            logger.warning("No service account path configured, using application default credentials")
            import google.auth
            credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            return credentials

        logger.info(f"Using service account credentials from: {sa_path}")
        return service_account.Credentials.from_service_account_file(
            sa_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

    def connect(self):
        """Establish connection to Cloud SQL MySQL instance."""
        try:
            from google.cloud.sql.connector import Connector

            credentials = self._get_credentials()
            self._connector = Connector(credentials=credentials)

            self._connection = self._connector.connect(
                self.config["instance_connection_name"],
                "pymysql",
                user=self.config["user"],
                password=self.config["password"],
                db=self.config["database"],
                charset="utf8mb4",
            )

            logger.info(
                f"Connected to Cloud SQL: {self.config['instance_connection_name']} "
                f"/ {self.config['database']}"
            )
            return self

        except ImportError:
            raise ImportError(
                "Cloud SQL connector not installed. Run:\n"
                "  pip install cloud-sql-python-connector[pymysql] pymysql google-auth"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Cloud SQL: {e}")
            raise

    def query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as a list of dicts.

        Args:
            sql: SQL query string
            params: Optional tuple of query parameters

        Returns:
            List of row dicts with column names as keys
        """
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            import pymysql.cursors
            with self._connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params)
                results = cursor.fetchall()
                logger.debug(f"Query returned {len(results)} rows")
                return results
        except Exception as e:
            logger.error(f"Query failed: {e}\nSQL: {sql[:200]}")
            raise

    def close(self):
        """Close connection and connector."""
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
            self._connection = None

        if self._connector:
            try:
                self._connector.close()
            except Exception:
                pass
            self._connector = None

        logger.info("Cloud SQL connection closed")

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
