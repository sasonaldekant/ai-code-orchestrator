"""
Prompt Gate (Tier 0 Validation)
-------------------------------
Uses Gemini Flash to validate prompt clarity and classification before heavy lift.
Cost: ~$0.0001 per call.
"""

from __future__ import annotations
import json
import logging
from typing import Dict, Any, List, Optional
from .llm_client_v2 import LLMClientV2
from .model_cascade_router import ModelCascadeRouter

logger = logging.getLogger(__name__)

class PromptGate:
    def __init__(self, llm_client: LLMClientV2, router: ModelCascadeRouter):
        self.llm_client = llm_client
        self.router = router
        # Get gate config (Gemini Flash)
        self.config = self.router.base_router.get_model_for_phase("gate")

    async def validate_and_classify(self, prompt: str) -> Dict[str, Any]:
        """
        Validate clarity, extract complexity, and identify dependencies.
        Returns:
            {
                "is_valid": bool,
                "refined_prompt": str,
                "complexity": "simple" | "medium" | "high",
                "dependencies": ["fastapi", "react", ...]
            }
        """
        system_prompt = (
            "You are a Gatekeeper for an AI Coding Agent. Your job is to:\n"
            "1. Check if the prompt is clear and related to a software task. If not, set 'is_valid' to false.\n"
            "2. If valid but slightly unclear, refine it into a technical instruction.\n"
            "3. Classify complexity: 'simple' (one file fix), 'medium' (feature add), 'high' (architecture change).\n"
            "4. Extract key technical dependencies mentioned (e.g., React, Django).\n"
            "5. If the prompt is absolute nonsense (e.g. 'xzy', 'asdf'), set 'is_valid' to false.\n"
            "Output valid JSON only with fields: is_valid (bool), refined_prompt (str), complexity (str), dependencies (list)."
        )

        user_content = f"PROMPT: {prompt}"

        try:
            response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                model=self.config.model,
                temperature=0.0,
                json_mode=True
            )
            
            data = json.loads(response.content)
            is_valid = data.get("is_valid", True)
            
            return {
                "is_valid": is_valid,
                "refined_prompt": data.get("refined_prompt", prompt),
                "complexity": data.get("complexity", "medium"),
                "dependencies": data.get("dependencies", [])
            }

        except Exception as e:
            logger.warning(f"Prompt Gate failed (pass-through activated): {e}")
            # Fail-open: Assume valid, medium complexity
            return {
                "is_valid": True,
                "refined_prompt": prompt,
                "complexity": "medium",
                "dependencies": []
            }
