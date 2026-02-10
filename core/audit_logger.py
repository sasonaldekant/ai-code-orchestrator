import json
import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class AuditLogger:
    """
    Tracks and persists all AI decisions, costs, and system changes using SQLite.
    """
    
    def __init__(self, db_path: str = "outputs/audit_logs/audit_system.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite schema if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    agent TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    cost REAL DEFAULT 0.0
                )
            """)
            conn.commit()

    def log_action(self, agent: str, action: str, details: Dict[str, Any], cost: float = 0.0):
        """Logs a single system action to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO audit_logs (agent, action, details, cost) VALUES (?, ?, ?, ?)",
                    (agent, action, json.dumps(details), cost)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to write audit DB: {e}")

    def get_logs(self, limit: int = 100, agent: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves recent logs with optional filtering."""
        query = "SELECT * FROM audit_logs"
        params = []
        if agent:
            query += " WHERE agent = ?"
            params.append(agent)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch logs: {e}")
            return []

    def generate_report(self) -> str:
        """Generates a summary report of system activity from the DB."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Summary stats
                stats = conn.execute("""
                    SELECT 
                        COUNT(*) as total_count,
                        SUM(cost) as total_cost,
                        SUM(CASE WHEN action = 'completion' THEN 1 ELSE 0 END) as success_count,
                        SUM(CASE WHEN action LIKE '%error%' THEN 1 ELSE 0 END) as fail_count
                    FROM audit_logs
                """).fetchone()
                
                # Agent breakdown
                agent_counts = conn.execute("""
                    SELECT agent, COUNT(*) as count FROM audit_logs GROUP BY agent
                """).fetchall()

            total_cost = stats['total_cost'] or 0.0
            total_actions = stats['total_count'] or 0
            success = stats['success_count'] or 0
            fail = stats['fail_count'] or 0
            
            report = f"""# Enterprise Audit Report (Database-Backed)
Generated: {datetime.now().isoformat()}

## Summary
- **Total Actions Logged:** {total_actions}
- **Total Estimated Cost:** ${total_cost:.4f}
- **Success Rate:** {(success / (success + fail) * 100) if (success + fail) > 0 else 100:.1f}%

## Activity Breakdown by Agent
"""
            for row in agent_counts:
                report += f"- **{row['agent']}:** {row['count']} actions\n"
                
            return report
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return "Error generating audit report."
