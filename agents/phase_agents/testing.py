"""
Testing agent.

Generates test cases and reports for the implementation.  Uses a smaller,
cheaper model (e.g. GPT‑4o mini) for cost efficiency.
"""

from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TestingAgent:
    """Generate tests for the implemented solution."""

    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator
        self.prompt_path = Path("prompts/phase_prompts/testing.txt")

    async def execute(self, context: Dict[str, Any], rag_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt_template = self._load_prompt()
        prompt = self._fill_prompt(prompt_template, context, rag_context)
        cfg = self.orchestrator.model_router.get_model_config("testing")
        resp = await self.orchestrator.llm_client.generate(prompt, cfg)
        result = {
            "phase": "testing",
            "tests": resp["content"],
            "tokens_in": resp["tokens_in"],
            "tokens_out": resp["tokens_out"],
            "model": cfg["model"],
            "provider": cfg.get("provider", "openai"),
        }
        return result

    def _load_prompt(self) -> str:
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "You are a testing agent. Implementation details: {implementation}"

    def _fill_prompt(self, template: str, context: Dict[str, Any], rag_context: List[Dict[str, Any]]) -> str:
        prompt = template
        for k, v in context.items():
            prompt = prompt.replace(f"{{{k}}}", str(v))
        if rag_context:
            rag_text = "\n\n--- Retrieved Context ---\n"
            for doc in rag_context:
                rag_text += f"\n{doc.get('content', '')[:1000]}\n"
            prompt += rag_text
        return prompt
