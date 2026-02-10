
"""
Database Content Ingester.
Supports:
1. Direct SQL Connection (via pyodbc/sqlalchemy)
2. JSON File Import (fallback)
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

from rag.vector_store import Document

logger = logging.getLogger(__name__)

class DatabaseContentIngester:
    def __init__(self):
        self.chunk_size = 500 # Characters per "row document"

    def ingest_from_json(self, file_path: str, table_name: str = None) -> List[Document]:
        """
        Ingest database content from a JSON file.
        Expected format: List of Dicts (rows).
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            content = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(content, list):
                # Maybe it is wrapped? type check
                if isinstance(content, dict) and "rows" in content:
                    content = content["rows"]
                else:
                    raise ValueError("JSON must be a list of records or have a 'rows' key")
            
            # Determine table name from filename if not provided
            if not table_name:
                table_name = path.stem

            return self._process_rows(content, table_name, source=f"json_file:{path.name}")
        except Exception as e:
            logger.error(f"Failed to ingest JSON: {e}")
            raise

    def ingest_from_sql(self, connection_string: str, query: str, table_name: str) -> List[Document]:
        """
        Ingest database content via direct SQL connection.
        Requires pyodbc.
        """
        try:
            import pyodbc
            import pandas as pd # Optional, but makes life easier. Let's try raw cursor to minimize deps.
        except ImportError:
            logger.error("pyodbc not installed. Cannot use SQL ingestion.")
            raise ImportError("pyodbc is required for SQL ingestion.")

        documents = []
        try:
            logger.info(f"Connecting to DB...")
            # Establish connection
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            
            logger.info(f"Executing query: {query}")
            cursor.execute(query)
            
            # Fetch columns
            columns = [column[0] for column in cursor.description]
            
            # Fetch rows
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))
            
            conn.close()
            
            return self._process_rows(data, table_name, source="sql_query")

        except Exception as e:
            logger.error(f"SQL Ingestion failed: {e}")
            raise

    def _process_rows(self, rows: List[Dict[str, Any]], table_name: str, source: str) -> List[Document]:
        """
        Convert list of dicts (rows) into RAG Documents.
        """
        documents = []
        for i, row in enumerate(rows):
            # 1. Create text representation
            # "Product (ID: 1): Laptop, Price: 999"
            text_parts = [f"Table: {table_name}"]
            
            # Identify ID if possible
            row_id = row.get("id") or row.get("Id") or row.get("ID") or f"row_{i}"
            
            for k, v in row.items():
                if v is not None:
                     text_parts.append(f"{k}: {v}")
            
            text_content = ", ".join(text_parts)
            
            # 2. Hash for ID
            content_hash = hashlib.md5(text_content.encode()).hexdigest()
            
            # 3. Create Document
            doc = Document(
                id=f"db_{table_name}_{content_hash}",
                text=text_content,
                metadata={
                    "type": "database_row",
                    "table": table_name,
                    "source": source,
                    "row_id": str(row_id),
                    "original_json": json.dumps(row, default=str) # Store raw data for retrieval
                }
            )
            documents.append(doc)
            
        logger.info(f"Processed {len(documents)} rows from {table_name}")
        return documents
