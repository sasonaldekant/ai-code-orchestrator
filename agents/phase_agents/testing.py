"""
Testing agent.

Generates test cases and test plans for the implementation.
"""

from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)


class TestingAgent:
    """Generate tests for the implemented solution."""

    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator
        self.prompt_path = Path("prompts/phase_prompts/testing.txt")

    async def execute(self, context: Dict[str, Any], rag_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute testing phase.
        Generates test cases based on implementation output.
        """
        prompt_content = self._build_prompt_content(context, rag_context)
        
        cfg = self.orchestrator.model_router.get_model_for_phase("testing")
        
        # Use simple boolean for json_mode compatibility
        json_mode = (cfg.provider == "openai")
        
        response = await self.orchestrator.llm_client.complete(
            messages=[
                {"role": "system", "content": "You are a QA Engineer. Output JSON with 'test_cases'."},
                {"role": "user", "content": prompt_content}
            ],
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            json_mode=json_mode
        )
        
        parsed_tests = self._parse_json(response.content)
        
        return {
            "phase": "testing",
            "output": parsed_tests,
            "tokens_in": response.tokens_used["prompt"],
            "tokens_out": response.tokens_used["completion"],
            "model": response.model,
            "provider": response.provider,
        }

    def _build_prompt_content(self, context: Dict[str, Any], rag_context: List[Dict[str, Any]]) -> str:
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                template = f.read()
        except FileNotFoundError:
            template = "Generate comprehensive test cases for the following implementation:\n{implementation}"
        
        prompt = template
        for k, v in context.items():
            val = json.dumps(v, indent=2) if isinstance(v, (dict, list)) else str(v)
            prompt = prompt.replace(f"{{{k}}}", val)
            
        if rag_context and "{domain_context}" not in prompt:
             rag_text = "\n\n--- Retrieved Context ---\n"
             for doc in rag_context:
                 content = doc.get("content", "")
                 if not content and "metadata" in doc:
                     content = str(doc["metadata"])
                 rag_text += f"\n- {content[:500]}...\n"
             prompt += rag_text
             
        return prompt

    def _parse_json(self, content: str) -> Dict[str, Any]:
        try:
            cleaned = content.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"raw_output": content, "error": "json_parse_error"}
