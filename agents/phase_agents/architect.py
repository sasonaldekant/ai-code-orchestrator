"""
Architect agent.

This phase designs the system architecture from the requirements.  In the
enhanced system, multiple proposals could be generated and merged via
consensus; for now a single model generates the architecture description.
"""

from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ArchitectAgent:
    """Generate architecture design."""

    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator
        self.prompt_path = Path("prompts/phase_prompts/architect.txt")

    async def execute(self, context: Dict[str, Any], rag_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate an architecture specification.

        If the model mapping specifies `consensus_mode`, multiple proposals
        will be generated using the listed `consensus_models`.  The proposals
        are concatenated and returned as the architecture description.  In a
        production system a synthesis step could merge or vote on proposals.
        """
        prompt_template = self._load_prompt()
        prompt = self._fill_prompt(prompt_template, context, rag_context)
        cfg = self.orchestrator.model_router.get_model_config("architect")
        # check for consensus mode
        proposals: List[str] = []
        total_tokens_in = 0
        total_tokens_out = 0
        if cfg.get("consensus_mode") and cfg.get("consensus_models"):
            for model_name in cfg.get("consensus_models", []):
                # create a per‑model config by copying the base config
                model_cfg = cfg.copy()
                model_cfg["model"] = model_name
                # heuristically set provider based on model name
                if "claude" in model_name:
                    model_cfg["provider"] = "anthropic"
                elif "gemini" in model_name:
                    model_cfg["provider"] = "google"
                elif "gpt" in model_name:
                    model_cfg["provider"] = "openai"
                resp = await self.orchestrator.llm_client.generate(prompt, model_cfg)
                proposals.append(resp.get("content", ""))
                total_tokens_in += resp.get("tokens_in", 0)
                total_tokens_out += resp.get("tokens_out", 0)
            # concatenate proposals; in future this could be a smarter merge
            architecture = "\n\n---\n\n".join(proposals)
            result = {
                "phase": "architect",
                "architecture": architecture,
                "tokens_in": total_tokens_in,
                "tokens_out": total_tokens_out,
                "model": ",".join(cfg.get("consensus_models", [])),
                "provider": "multi",
            }
            return result
        # single‑model case
        resp = await self.orchestrator.llm_client.generate(prompt, cfg)
        result = {
            "phase": "architect",
            "architecture": resp["content"],
            "tokens_in": resp.get("tokens_in", 0),
            "tokens_out": resp.get("tokens_out", 0),
            "model": cfg.get("model", "unknown"),
            "provider": cfg.get("provider", "openai"),
        }
        return result

    def _load_prompt(self) -> str:
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "You are an architect agent. Requirements: {requirements}"

    def _fill_prompt(self, template: str, context: Dict[str, Any], rag_context: List[Dict[str, Any]]) -> str:
        prompt = template
        # Flatten previous outputs into context for prompt
        for k, v in context.items():
            prompt = prompt.replace(f"{{{k}}}", str(v))
        if rag_context:
            rag_text = "\n\n--- Retrieved Context ---\n"
            for doc in rag_context:
                rag_text += f"\n{doc.get('content', '')[:1000]}\n"
            prompt += rag_text
        return prompt
