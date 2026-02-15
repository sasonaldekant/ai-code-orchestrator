"""
Architect agent.

This phase designs the system architecture from the requirements. It supports
consensus mode where multiple models propose designs, and a synthesis model
merges them into a final architecture specification.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
import json
import asyncio

logger = logging.getLogger(__name__)


class ArchitectAgent:
    """Generate architecture design with optional consensus."""

    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator
        self.prompt_path = Path("prompts/phase_prompts/architect.txt")
        self.name = "Architect"
        self.description = "Designs system architecture and data models."
        self.tools = ["System Design", "Consensus Synthesis", "Data Modeling"]
        self.role = "architect"

    async def execute(self, context: Dict[str, Any], rag_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate an architecture specification.
        Uses ModelRouter V2 to determine if consensus mode is active.
        """
        phase_config = self.orchestrator.model_router.get_model_for_phase("architect")
        
        # Build prompt
        prompt_content = self._build_prompt_content(context, rag_context)

        if phase_config.consensus_mode:
            return await self._execute_consensus(phase_config, prompt_content)
        
        # Single model execution
        return await self._execute_single(phase_config, prompt_content)

    async def _execute_single(self, config, prompt):
        messages = [
            {"role": "system", "content": "You are a software architect. Output structured JSON."},
            {"role": "user", "content": prompt}
        ]
        
        # Use json_mode if provider is OpenAI-compatible
        json_mode = (config.provider == "openai")
        
        response = await self.orchestrator.llm_client.complete(
            messages=messages,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            json_mode=json_mode,
            tier="tier_1_rules"
        )
        
        parsed_output = self._parse_json(response.content)
        
        return {
            "phase": "architect",
            "architecture": parsed_output,
            "raw_output": response.content,
            "tokens_in": response.tokens_used["prompt"],
            "tokens_out": response.tokens_used["completion"],
            "model": response.model,
            "provider": response.provider,
            "thinking": response.thinking
        }

    async def _execute_consensus(self, config, prompt):
        """Execute multiple models and synthesize results."""
        consensus_cfg = self.orchestrator.model_router.get_consensus_models("architect")
        primary = consensus_cfg.primary
        secondary = consensus_cfg.secondary
        tertiary = consensus_cfg.tertiary
        
        logger.info(f"Executing consensus architecture with {primary.model}, {secondary.model}...")

        # Run models in parallel
        tasks = [
            self._call_model(primary, prompt),
            self._call_model(secondary, prompt)
        ]
        if tertiary:
            tasks.append(self._call_model(tertiary, prompt))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful proposals
        proposals = []
        tokens_in = 0
        tokens_out = 0
        
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                logger.error(f"Consensus model {i} failed: {res}")
                continue
            proposals.append(f"Proposal {i+1}:\n{res.content}")
            tokens_in += res.tokens_used["prompt"]
            tokens_out += res.tokens_used["completion"]
            
        if not proposals:
            raise RuntimeError("All consensus models failed.")
            
        # Synthesis step
        synthesis_prompt = (
            "You are a Lead Architect. Review the following architecture proposals "
            "from two different specialist models. Identify any conflicts or "
            "differences in their approach.\n\n"
            "Synthesize the best aspects into a single, cohesive JSON specification.\n\n"
            "PROPOSALS:\n"
            + "\n\n".join(proposals) +
            "\n\nReturn JSON format:\n"
            "{\n"
            "  \"architecture\": { ... },\n"
            "  \"consensus_report\": {\n"
            "    \"agreement_score\": <0.0-1.0>,\n"
            "    \"conflicts\": [\"conflict 1\", ...],\n"
            "    \"confidence\": <0.0-1.0>\n"
            "  }\n"
            "}"
        )
        
        synthesis_model = consensus_cfg.synthesis_model
        synthesis_response = await self.orchestrator.llm_client.complete(
            messages=[{"role": "user", "content": synthesis_prompt}],
            model=synthesis_model,
            temperature=0.0,
            json_mode=True,
            tier="tier_1_rules"
        )
        
        parsed_output = self._parse_json(synthesis_response.content)
        
        return {
            "phase": "architect",
            "architecture": parsed_output.get("architecture"),
            "consensus_report": parsed_output.get("consensus_report"),
            "proposals": proposals,
            "tokens_in": tokens_in + synthesis_response.tokens_used["prompt"],
            "tokens_out": tokens_out + synthesis_response.tokens_used["completion"],
            "model": "consensus_synthesis",
            "provider": "multi",
        }

    async def _call_model(self, config, prompt):
        return await self.orchestrator.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            tier="tier_1_rules"
        )

    def _build_prompt_content(self, context: Dict[str, Any], rag_context: List[Dict[str, Any]]) -> str:
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                template = f.read()
        except FileNotFoundError:
            template = (
                "Design a software architecture based on: {requirements}\n"
                "Consider domain knowledge:\n{domain_context}\n"
                "Output JSON with 'components', 'data_models', 'api_definitions'."
            )
            
        # Load Golden Rules
        golden_rules = self._load_golden_rules()
        
        # Start with template
        prompt = template
        
        # Replace context variables
        for k, v in context.items():
            if isinstance(v, (dict, list)):
                v = json.dumps(v, indent=2)
            prompt = prompt.replace(f"{{{k}}}", str(v))
            
        # Inject Golden Rules if placeholder exists, otherwise append
        if "{golden_rules}" in prompt:
            prompt = prompt.replace("{golden_rules}", golden_rules)
        elif golden_rules:
            prompt += f"\n\n[GOLDEN RULES & STANDARDS]:\n{golden_rules}\n"
            
        # Add RAG context if not already handled by placement in template
        if rag_context and "{domain_context}" not in prompt:
             rag_text = "\n\n--- Retrieved Context ---\n"
             for doc in rag_context:
                 content = doc.get("content", "")
                 if not content and "metadata" in doc:
                     content = str(doc["metadata"])
                 rag_text += f"\n- {content[:500]}...\n"
             prompt += rag_text
             
        return prompt

    def _load_golden_rules(self) -> str:
        """Load the AI_CONTEXT.md file."""
        try:
            # rag/AI_CONTEXT.md relative to project root
            context_path = Path(__file__).parent.parent.parent / "rag" / "AI_CONTEXT.md"
            if context_path.exists():
                return context_path.read_text(encoding="utf-8")
            return ""
        except Exception as e:
            logger.warning(f"Failed to load AI_CONTEXT.md: {e}")
            return ""

    def _parse_json(self, content: str) -> Dict[str, Any]:
        try:
            cleaned = content.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback to returning raw string in a dict wrapper
            return {"raw_architecture": content, "error": "json_parse_error"}
