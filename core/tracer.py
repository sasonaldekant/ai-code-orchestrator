"""
Tracing service for logging orchestrator events and debugging.

The tracer writes each event to a JSONL file.  Events include timestamps,
event types and arbitrary data payloads.  Tracing can be disabled via
environment variables.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TracingService:
    """Simple JSONL tracer."""

    def __init__(self, enabled: bool = True, trace_file: str | None = None) -> None:
        # honour environment variables
        env_enabled = os.getenv("TRACE_JSONL", "1") == "1"
        self.enabled = enabled and env_enabled
        self.trace_file = trace_file or os.getenv("TRACE_FILE", "trace.jsonl")

    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Write an event to the trace file.

        Each record includes a UTC timestamp, the event type and a data
        dictionary.  If tracing is disabled the call is a no‑op.
        """
        if not self.enabled:
            return
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data,
        }
        try:
            with open(self.trace_file, "a", encoding="utf-8") as f:
                json.dump(record, f)
                f.write("\n")
        except Exception as exc:
            logger.warning(f"Failed to write trace: {exc}")
