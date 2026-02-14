"""
Fact Checker (Perplexity Sonar)
-------------------------------
Uses Perplexity Sonar ($1/1M) to verify external dependencies and API versions in real-time.
Prevents hallucinations about non-existent libraries or deprecated API methods.
"""

from __future__ import annotations
import logging
import json
from typing import List, Dict, Any, Optional
from .llm_client_v2 import LLMClientV2
from .model_cascade_router import ModelCascadeRouter

logger = logging.getLogger(__name__)

class FactChecker:
    def __init__(self, llm_client: LLMClientV2, router: ModelCascadeRouter):
        self.llm_client = llm_client
        self.router = router
        # Get checker config (Perplexity Sonar)
        self.config = self.router.base_router.get_model_for_phase("fact_checker")
        # Simple in-memory cache for this session
        self.cache: Dict[str, str] = {}

    async def verify_dependencies(self, dependencies: List[str]) -> Dict[str, str]:
        """
        Verify if the listed dependencies exist and are compatible.
        Returns a dict of {dependency: status/version_info}.
        """
        if not dependencies:
            return {}

        # Check cache first
        results = {}
        to_check = []
        
        for dep in dependencies:
            if dep in self.cache:
                results[dep] = self.cache[dep]
            else:
                to_check.append(dep)
        
        if not to_check:
            return results

        prompt = (
            f"Verify the following software libraries/dependencies: {', '.join(to_check)}.\n"
            "For each, confirm it exists and state the latest stable major version.\n"
            "If a library is deprecated or hallucinated, clearly state 'INVALID'.\n\n"
            "Output JSON:\n"
            "{\n"
            "  \"library_name\": \"status/version\",\n"
            "  ...\n"
            "}"
        )

        try:
            response = await self.llm_client.complete(
                messages=[{"role": "user", "content": prompt}],
                model=self.config.model,
                temperature=0.0,
                json_mode=True
            )
            
            fresh_data = json.loads(response.content)
            
            # Update cache and results
            for k, v in fresh_data.items():
                self.cache[k] = v
                results[k] = v
                
        except Exception as e:
            logger.warning(f"Fact check failed: {e}")
            for dep in to_check:
                results[dep] = "verification_failed"

        return results

    async def check_api_version(self, library: str, method: str) -> str:
        """
        Check if a specific method exists in a library version.
        Useful for avoiding deprecated API calls.
        """
        key = f"{library}::{method}"
        if key in self.cache:
            return self.cache[key]

        prompt = (
            f"Does the library '{library}' have a method or class named '{method}'?\n"
            "Is it deprecated in the latest version?\n"
            "Return a concise 'YES/NO' and brief explanation."
        )

        try:
            response = await self.llm_client.complete(
                messages=[{"role": "user", "content": prompt}],
                model=self.config.model,
                temperature=0.0
            )
            result = response.content.strip()
            self.cache[key] = result
            return result
        except Exception as e:
            logger.error(f"API check failed: {e}")
            return "CHECK_FAILED"
