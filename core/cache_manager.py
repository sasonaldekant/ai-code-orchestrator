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
        self.tier_config = {
            "tier_1_rules": 3600,
            "tier_2_tokens": 3600,
            "tier_3_catalog": 1800,
            "default": 86400
        }
        self._load_config()
        self.load()

    def _load_config(self):
        """Load caching configuration from model_mapping_v2.yaml if exists."""
        try:
            import yaml
            config_path = Path("config/model_mapping_v2.yaml")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    if config and "caching" in config:
                        c_cfg = config["caching"]
                        self.tier_config["tier_1_rules"] = c_cfg.get("tier_1_rules", {}).get("ttl_seconds", 3600)
                        self.tier_config["tier_2_tokens"] = c_cfg.get("tier_2_tokens", {}).get("ttl_seconds", 3600)
                        self.tier_config["tier_3_catalog"] = c_cfg.get("tier_3_catalog", {}).get("ttl_seconds", 1800)
                        logger.info("Loaded tiered caching config from model_mapping_v2.yaml")
        except Exception as e:
            logger.warning(f"Could not load caching config: {e}")

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

    def _generate_key(self, prompt: str, model: str, temperature: float, tier: str = "default") -> str:
        """Create a unique hash for the request, including tier for isolation."""
        raw = f"{tier}:{model}:{temperature}:{prompt}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def get(self, prompt: str, model: str, temperature: float = 0.0, tier: str = "default") -> Optional[Any]:
        """Retrieve cached response if valid for the specific tier and TTL."""
        key = self._generate_key(prompt, model, temperature, tier)
        entry = self.cache.get(key)
        
        if not entry:
            return None
            
        # Check TTL specific to the tier
        ttl = self.tier_config.get(tier, self.tier_config["default"])
        if time.time() - entry["timestamp"] > ttl:
            del self.cache[key]
            return None
            
        return entry["content"]

    def set(self, prompt: str, model: str, content: Any, temperature: float = 0.0, tier: str = "default"):
        """Store response in cache with metadata."""
        key = self._generate_key(prompt, model, temperature, tier)
        self.cache[key] = {
            "content": content,
            "timestamp": time.time(),
            "tier": tier
        }
        self.save()

    def clear(self):
        self.cache = {}
        self.save()
