"""
Cache Manager
-------------
Simple file-based caching for LLM responses to reduce costs and latency.
"""

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

CACHE_DIR = Path("outputs/cache")
CACHE_FILE = CACHE_DIR / "llm_response_cache.json"

class CacheManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance._init_cache()
        return cls._instance

    def _init_cache(self):
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 86400  # Default 24 hours
        self.load()

    def load(self):
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load cache: {e}")

    def save(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _generate_key(self, prompt: str, model: str, temperature: float) -> str:
        """Create a unique hash for the request."""
        raw = f"{model}:{temperature}:{prompt}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def get(self, prompt: str, model: str, temperature: float = 0.0) -> Optional[Any]:
        """Retrieve cached response if valid."""
        key = self._generate_key(prompt, model, temperature)
        entry = self.cache.get(key)
        
        if not entry:
            return None
            
        # Check TTL
        if time.time() - entry["timestamp"] > self.cache_ttl:
            del self.cache[key]
            return None
            
        return entry["content"]

    def set(self, prompt: str, model: str, content: Any, temperature: float = 0.0):
        """Store response in cache."""
        key = self._generate_key(prompt, model, temperature)
        self.cache[key] = {
            "content": content,
            "timestamp": time.time()
        }
        # Auto-save occasionally or on every write for safety
        self.save()

    def clear(self):
        self.cache = {}
        self.save()
