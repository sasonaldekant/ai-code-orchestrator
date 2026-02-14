from __future__ import annotations
import logging
import json
from typing import Dict, Any, Optional
from core.llm_client_v2 import LLMClientV2
from core.cost_manager import CostManager

logger = logging.getLogger(__name__)

class DomainValidator:
    """
    Validates if a prompt is within the project's technical scope.
    Scope: React, TypeScript, C#, .NET Core, EF Core, DynUI Components.
    """
    
    def __init__(self, llm_client: Optional[LLMClientV2] = None):
        self.llm_client = llm_client or LLMClientV2(CostManager())
        self.scope_description = """
        The project technical scope is strictly limited to:
        - Frontend: React, TypeScript, Vite.
        - UI Components: DynUI (custom library with components like DynAvatar, DynPopup, DynAccordion, DynInput, etc.).
        - Backend: C#, .NET Core 8+, Entity Framework Core (EF Core).
        - Data Format: JSON.
        - Environment: VS Code extension integration.
        - General: Software architecture, unit testing, and API design within these technologies.
        
        Out of scope:
        - Python web frameworks (Django, Flask).
        - Java, PHP, Go, Rust (unless for small utilities).
        - Mobile development (Swift, Kotlin).
        - Generic questions unrelated to coding or this stack (e.g., recipes, travel).
        """

    async def validate(self, prompt: str) -> Dict[str, Any]:
        """
        Validate if the prompt is within scope using an LLM check.
        """
        system_prompt = (
            "You are a Project Scope Guard. Your job is to determine if a user instruction "
            "falls within the technical scope of the current project.\n\n"
            f"PROJECT SCOPE:\n{self.scope_description}\n\n"
            "Return a JSON object with the following fields:\n"
            "- in_scope: boolean\n"
            "- reason: string (brief explanation)\n"
            "- confidence: float (0.0 to 1.0)\n"
            "- suggested_action: string (e.g., 'proceed', 'ask_clarification', 'reject')\n"
        )
        
        user_prompt = f"User Instruction: \"{prompt}\"\n\nIs this in scope?"
        
        try:
            # Use gpt-4o-mini for cost-effective validation
            response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="gpt-4o-mini",
                temperature=0.0,
                json_mode=True
            )
            
            result = json.loads(response.content)
            logger.info(f"Domain Validation Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Domain validation failed: {e}")
            # Fallback to proceed if validation itself fails
            return {
                "in_scope": True, 
                "reason": "Validation error, proceeding by default.", 
                "confidence": 0.5,
                "suggested_action": "proceed"
            }
