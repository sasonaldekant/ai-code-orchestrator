"""
Error Tracker Module for AI Code Orchestrator v3.0

This module handles:
1. Logging detailed error context when tasks fail
2. Persisting error history for analysis
3. detecting frequent error patterns (via PatternDetector)
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ErrorLog:
    """Represents a single error event."""
    id: str
    timestamp: float
    phase: str
    error_type: str
    message: str
    context_summary: str  # Brief description of what was being done
    stack_trace: Optional[str] = None
    related_files: List[str] = field(default_factory=list)
    resolution: Optional[str] = None  # How it was fixed (if known)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ErrorTracker:
    """
    Tracks and persists errors to enable learning from mistakes.
    """
    
    def __init__(self, storage_dir: str = "outputs/error_tracking"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = self.storage_dir / "error_history.jsonl"
        self.session_errors: List[ErrorLog] = []
        
    def log_error(
        self, 
        phase: str, 
        error: Exception | str, 
        context: Dict[str, Any] = None
    ) -> str:
        """
        Log an error with context.
        
        Args:
            phase: The phase/agent where error occurred
            error: The exception or error message
            context: Context dictionary (task desc, file path, etc.)
            
        Returns:
            Error ID
        """
        if isinstance(error, Exception):
            error_type = type(error).__name__
            # Format message to look like a standard traceback line for easier regex matching
            # e.g. "NameError: name 'foo' is not defined"
            if not str(error).startswith(error_type):
                error_msg = f"{error_type}: {error}"
            else:
                error_msg = str(error)
        else:
            error_type = "RuntimeError"
            error_msg =str(error)
        timestamp = time.time()
        error_id = f"err_{int(timestamp)}_{hash(error_msg) % 10000}"
        
        context_summary = str(context.get("task_description", context.get("summary", "No context"))) if context else "No context"
        
        log_entry = ErrorLog(
            id=error_id,
            timestamp=timestamp,
            phase=phase,
            error_type=error_type,
            message=error_msg,
            context_summary=context_summary,
            related_files=context.get("files", []) if context else []
        )
        
        self.session_errors.append(log_entry)
        self._persist_log(log_entry)
        
        logger.error(f"Error logged [{error_id}]: {error_msg}")
        return error_id

    def _persist_log(self, log: ErrorLog):
        """Append log entry to JSONL file."""
        try:
            with open(self.current_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log.to_dict()) + "\n")
        except Exception as e:
            logger.error(f"Failed to persist error log: {e}")

    def get_recent_errors(self, limit: int = 10) -> List[ErrorLog]:
        """Retrieve recent errors."""
        return sorted(self.session_errors, key=lambda x: x.timestamp, reverse=True)[:limit]

    def analyze_patterns(self) -> List[Dict[str, Any]]:
        """
        Analyze accumulated errors to find patterns.
        (Placeholder for PatternDetector integration)
        """
        # Group by error type
        stats = {}
        for err in self.session_errors:
            key = f"{err.phase}:{err.error_type}"
            if key not in stats:
                stats[key] = {"count": 0, "examples": []}
            stats[key]["count"] += 1
            stats[key]["examples"].append(err.message)
            
        patterns = []
        for key, data in stats.items():
            if data["count"] >= 3:
                patterns.append({
                    "pattern": key,
                    "frequency": data["count"],
                    "suggestion": "Investigate common cause"
                })
        return patterns
