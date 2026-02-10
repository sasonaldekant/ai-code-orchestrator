"""
Experience Database ("Self-Correction Memory")
Stores successful error fixes to avoid repeating mistakes.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class ExperienceDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExperienceDB, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.db_path = Path("experience.db")
        self._init_db()

    def _init_db(self):
        """Initialize SQLite table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_pattern TEXT NOT NULL,
                    fix_strategy TEXT NOT NULL,
                    context_hash TEXT,
                    timestamp TEXT,
                    success_count INTEGER DEFAULT 1
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to init ExperienceDB: {e}")

    def record_fix(self, error_pattern: str, fix_strategy: str, context: str = ""):
        """Record a successful fix."""
        try:
            # Create a simple hash of context to avoid duplicates
            ctx_hash = hashlib.md5(context.encode()).hexdigest() if context else ""
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute(
                "SELECT id, success_count FROM experiences WHERE error_pattern = ? AND fix_strategy = ?", 
                (error_pattern, fix_strategy)
            )
            row = cursor.fetchone()
            
            if row:
                # Increment count
                new_count = row[1] + 1
                cursor.execute("UPDATE experiences SET success_count = ? WHERE id = ?", (new_count, row[0]))
                logger.info(f"Updated experience count for pattern: {error_pattern[:30]}...")
            else:
                # Insert new
                cursor.execute(
                    "INSERT INTO experiences (error_pattern, fix_strategy, context_hash, timestamp) VALUES (?, ?, ?, ?)",
                    (error_pattern, fix_strategy, ctx_hash, datetime.now().isoformat())
                )
                logger.info(f"Recorded new experience: {error_pattern[:30]}...")
                
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to record experience: {e}")

    def find_similar_error(self, error_pattern: str) -> List[Dict[str, Any]]:
        """
        Find potential fixes for a given error pattern.
        Uses simple text matching for now.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Simple keyword matching logic or Exact match
            # "Select * from exp where error_pattern LIKE %...%"
            # For robustness, we might want to search for substrings of the error.
            
            # For V1, let's try to match substantial parts or just exact.
            # Or retrieve all and filter in python (if small DB).
            
            cursor.execute("SELECT * FROM experiences ORDER BY success_count DESC LIMIT 5")
            rows = cursor.fetchall()
            conn.close()
            
            matching_experiences = []
            words = set(error_pattern.lower().split())
            
            for row in rows:
                db_pattern = row["error_pattern"].lower()
                # Jaccard similarity or overlap?
                db_words = set(db_pattern.split())
                overlap = len(words.intersection(db_words))
                
                # If significant overlap or substring match
                if overlap > 2 or db_pattern in error_pattern.lower() or error_pattern.lower() in db_pattern:
                    matching_experiences.append({
                        "error_pattern": row["error_pattern"],
                        "fix_strategy": row["fix_strategy"],
                        "success_count": row["success_count"]
                    })
            
            return matching_experiences
            
        except Exception as e:
            logger.error(f"Failed to search experiences: {e}")
            return []
