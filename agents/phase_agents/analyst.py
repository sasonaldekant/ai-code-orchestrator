"""
Analyst agent.

The analyst phase takes high‑level requirements and produces a structured
requirements specification. It uses a reasoning model for deep analysis.
"""

from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path
import logging
import json
import re

logger = logging.getLogger(__name__)


class AnalystAgent:
    """Analyst agent using the orchestrator's services."""

    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator
        self.prompt_path = Path("prompts/phase_prompts/analyst.txt")
        self.name = "Analyst"
        self.description = "Analyzes requirements and produces detailed specifications."
        self.tools = ["Requirement Analysis", "Pattern Recognition", "Risk Assessment"]
        self.role = "analyst"

    async def execute(self, context: Dict[str, Any], rag_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Build prompt
        prompt_content = self._build_prompt_content(context, rag_context)
        
        # Select model using v2 router (returns ModelConfig dataclass)
        cfg = self.orchestrator.model_router.get_model_for_phase("analyst")
        
        # Prepare messages
        messages = [
            {"role": "system", "content": "You are an expert systems analyst. Output strictly in JSON format."},
            {"role": "user", "content": prompt_content}
        ]
        
        # Call LLM
        # Use json_mode if provider is OpenAI-compatible for it
        json_mode = (cfg.provider == "openai")
        
        response = await self.orchestrator.llm_client.complete(
            messages=messages,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            json_mode=json_mode
        )
        
        # Parse output
        parsed_content = self._parse_to_json(response.content)
        
        result = {
            "phase": "analyst",
            "requirements": context.get("requirements", ""),
            "output": parsed_content,
            "raw_output": response.content,
            "tokens_in": response.tokens_used["prompt"],
            "tokens_out": response.tokens_used["completion"],
            "model": response.model,
            "provider": response.provider,
            "thinking": response.thinking
        }
        return result

    def _build_prompt_content(self, context: Dict[str, Any], rag_context: List[Dict[str, Any]]) -> str:
        # Load template or fallback
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                template = f.read()
        except FileNotFoundError:
            template = "Analyze the following requirements:\n{requirements}\n\nReturn a JSON object with 'summary', 'features', 'risks', and 'implementation_plan'."
            
        # Fill template
        prompt = template
        for k, v in context.items():
            prompt = prompt.replace(f"{{{k}}}", str(v))
            
        # Add RAG context
        if rag_context:
            rag_text = "\n\n--- Relevant Domain Knowledge ---\n"
            for doc in rag_context:
                content = doc.get("content", "")
                if not content and "metadata" in doc: # Handle specific structure
                    content = str(doc["metadata"])
                rag_text += f"\n- {content[:500]}...\n"
            prompt += rag_text
            
        return prompt

    def _parse_to_json(self, content: str) -> Dict[str, Any]:
        """Attempt to parse content as JSON, handling potential markdown blocks."""
        try:
            # Clean markdown code blocks if present
            cleaned = content.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON output from Analyst agent")
            return {"raw_text": content, "error": "json_parse_error"}
