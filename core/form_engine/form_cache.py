import os
import json
import logging
import hashlib
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

CACHE_DIR = "outputs/form-cache"

class FormProjectCache:
    """
    Implements a two-layer cache for Form Studio.
    Layer 1: JSON Schema Fingerprinting
    Layer 2: Multiple UI variants for a given JSON.
    """
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def compute_fingerprint(self, template: Dict[str, Any]) -> str:
        """
        Computes a deterministic SHA-256 fingerprint of the form's structural fields.
        Ignores metadata, focuses purely on the functional shape of the form.
        Supports both flat (form.fields) and sectioned (sections) formats.
        """
        sections = template.get("sections") or []
        form_fields = (template.get("form") or {}).get("fields") or []
        
        # Flatten structure
        all_fields = list(form_fields)
        for s in sections:
            all_fields.extend(s.get("fields", []))
            
        # We extract field IDs and their core types to identify "structural" equivalence
        structure = [{"id": f.get("id"), "type": f.get("type")} for f in all_fields]
        
        fingerprint_data = json.dumps(structure, sort_keys=True)
        return hashlib.sha256(fingerprint_data.encode("utf-8")).hexdigest()

    def get_cached_variant(self, fingerprint: str, layout: str) -> Optional[Dict[str, str]]:
        """
        Looks up a cached UI variant for a given fingerprint.
        Returns a dict with paths or code content if found.
        """
        variant_file = os.path.join(self.cache_dir, f"{fingerprint}_{layout}.json")
        if os.path.exists(variant_file):
            logger.info(f"Cache HIT for fingerprint {fingerprint[:8]} with layout {layout}")
            with open(variant_file, "r", encoding="utf-8") as f:
                return json.load(f)
        
        logger.info(f"Cache MISS for fingerprint {fingerprint[:8]} with layout {layout}")
        return None

    def store_cached_variant(self, fingerprint: str, layout: str, component_code: str, api_code: str, calc_code: str, schema_code: str):
        """
        Stores the generated files for a specific structural fingerprint + layout variation.
        """
        variant_file = os.path.join(self.cache_dir, f"{fingerprint}_{layout}.json")
        
        data = {
            "component_code": component_code,
            "api_code": api_code,
            "calc_code": calc_code,
            "schema_code": schema_code
        }
        
        with open(variant_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Stored variant {layout} for fingerprint {fingerprint[:8]} into cache.")
