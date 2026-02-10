"""
User Preferences Memory
Stores explicit user rules and preferences to customize AI behavior.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PreferenceRule:
    rule: str
    category: str
    timestamp: str

class UserPreferences:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserPreferences, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.storage_path = Path("user_prefs.json")
        self.rules: List[PreferenceRule] = []
        self._load()

    def add_rule(self, rule: str, category: str = "general"):
        """Add a new user preference rule."""
        new_rule = PreferenceRule(
            rule=rule,
            category=category,
            timestamp=datetime.now().isoformat()
        )
        self.rules.append(new_rule)
        self._save()
        logger.info(f"Added user preference: {rule} ({category})")

    def get_rules(self, category: Optional[str] = None) -> List[str]:
        """Get list of rules, optionally filtered by category."""
        if category:
            return [r.rule for r in self.rules if r.category == category]
        return [r.rule for r in self.rules]

    def get_system_prompt_context(self) -> str:
        """Format rules for inclusion in System Prompt."""
        if not self.rules:
            return ""
            
        context = "USER PREFERENCES (Follow these strictly):\n"
        # Group by category
        categories = {}
        for r in self.rules:
            if r.category not in categories: categories[r.category] = []
            categories[r.category].append(r.rule)
            
        for cat, rules in categories.items():
            context += f"[{cat.upper()}]\n"
            for rule in rules:
                context += f"- {rule}\n"
        
        return context

    def _save(self):
        try:
            data = [asdict(r) for r in self.rules]
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user prefs: {e}")

    def _load(self):
        try:
            if self.storage_path.exists():
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.rules = [PreferenceRule(**item) for item in data]
        except Exception as e:
            logger.error(f"Failed to load user prefs: {e}")
            self.rules = []
