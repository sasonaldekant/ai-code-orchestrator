"""
Cascade Metrics
---------------
Tracks usage stats for the Model Cascading System.
Persists metrics to JSON for dashboard visualization.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

STATUS_FILE = Path("outputs/cascade_metrics.json")

class CascadeMetrics:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CascadeMetrics, cls).__new__(cls)
            cls._instance._init_data()
        return cls._instance

    def _init_data(self):
        self.data = {
            "tier_usage": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
            "model_usage": {},
            "total_requests": 0,
            "saved_cost_estimated": 0.0,
            "last_updated": datetime.utcnow().isoformat()
        }
        self.load()

    def load(self):
        if STATUS_FILE.exists():
            try:
                with open(STATUS_FILE, "r") as f:
                    saved = json.load(f)
                    # Merge or overwrite
                    self.data.update(saved)
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")

    def save(self):
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.data["last_updated"] = datetime.utcnow().isoformat()
        try:
            with open(STATUS_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def record_selection(self, tier: int, model: str, provider: str):
        """Record a model selection event."""
        # Update Tier
        self.data["tier_usage"][str(tier)] = self.data["tier_usage"].get(str(tier), 0) + 1
        
        # Update Model
        key = f"{provider}/{model}"
        self.data["model_usage"][key] = self.data["model_usage"].get(key, 0) + 1
        
        self.data["total_requests"] += 1
        
        # Auto-save every few requests or rely on explicit save
        if self.data["total_requests"] % 5 == 0:
            self.save()

    def record_outcome(self, tier: int, success: bool):
        """Record the outcome of a tier execution."""
        if "tier_outcomes" not in self.data:
            self.data["tier_outcomes"] = {}
        
        key = str(tier)
        if key not in self.data["tier_outcomes"]:
            self.data["tier_outcomes"][key] = {"success": 0, "failure": 0}
            
        if success:
            self.data["tier_outcomes"][key]["success"] += 1
        else:
            self.data["tier_outcomes"][key]["failure"] += 1
            
        self.save()

    def get_stats(self) -> Dict[str, Any]:
        return self.data
