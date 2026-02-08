"""
Implementation agent.

Generates backend and frontend code in parallel using appropriate models.
This simplified implementation produces placeholder outputs and demonstrates
parallel LLM calls.
"""

from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path
import asyncio
import logging

logger = logging.getLogger(__name__)


class ImplementationAgent:
    """Implement the designed architecture."""

    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator
        # prompt templates for backend and frontend
        self.backend_prompt = Path("prompts/phase_prompts/implementation_backend.txt")
        self.frontend_prompt = Path("prompts/phase_prompts/implementation_frontend.txt")

    async def execute(self, context: Dict[str, Any], rag_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Build prompts
        backend_prompt = self._fill_prompt(self._load_prompt(self.backend_prompt), context, rag_context)
        frontend_prompt = self._fill_prompt(self._load_prompt(self.frontend_prompt), context, rag_context)
        # Get model configs
        backend_cfg = self.orchestrator.model_router.get_model_config("implementation")
        frontend_cfg = backend_cfg  # for simplicity use same model; could vary by speciality
        # Run LLM calls concurrently
        async def call_backend():
            return await self.orchestrator.llm_client.generate(backend_prompt, backend_cfg)
        async def call_frontend():
            return await self.orchestrator.llm_client.generate(frontend_prompt, frontend_cfg)
        backend_resp, frontend_resp = await asyncio.gather(call_backend(), call_frontend())
        result = {
            "phase": "implementation",
            "backend": backend_resp["content"],
            "frontend": frontend_resp["content"],
            "tokens_in": backend_resp["tokens_in"] + frontend_resp["tokens_in"],
            "tokens_out": backend_resp["tokens_out"] + frontend_resp["tokens_out"],
            "model": backend_cfg["model"],
            "provider": backend_cfg.get("provider", "openai"),
        }
        return result

    def _load_prompt(self, path: Path) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "You are an implementation agent. Architecture: {architecture}"

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
