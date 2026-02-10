"""
Implementation agent.

Generates backend and frontend code in parallel using appropriate models.
Supports specialized models for different tech stacks (e.g., GPT-4o for C#, Claude for React).
"""

from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


class ImplementationAgent:
    """Implement the designed architecture."""

    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator
        self.backend_prompt_path = Path("prompts/phase_prompts/implementation_backend.txt")
        self.frontend_prompt_path = Path("prompts/phase_prompts/implementation_frontend.txt")
        self.name = "Implementer"
        self.description = "Generates backend and frontend code based on architecture."
        self.tools = ["Code Generation", "Polyglot Implementation (C#/.NET, React)", "Tech Stack Adaptation"]
        self.role = "implementation"

    async def execute(self, context: Dict[str, Any], rag_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute implementation phase.
        
        Detailed flow:
        1. Retrieve specialized model configs for backend (e.g. dotnet) and frontend (e.g. react).
        2. Construct context-aware prompts.
        3. Execute LLM calls in parallel.
        4. Return structured code artifacts.
        """
        
        # 1. Get Specialized Models
        # Assuming we are building a .NET + React app as per domain config
        backend_cfg = self.orchestrator.model_router.get_model_for_specialty("backend", "efcore")
        frontend_cfg = self.orchestrator.model_router.get_model_for_specialty("frontend", "react")
        
        # 2. Build Prompts
        backend_prompt = self._build_prompt(
            self.backend_prompt_path, 
            context, 
            rag_context, 
            "Implement the backend logic based on the architecture."
        )
        
        frontend_prompt = self._build_prompt(
            self.frontend_prompt_path, 
            context, 
            rag_context, 
            "Implement the frontend components based on the architecture."
        )

        # 3. Parallel Execution
        backend_task = self.orchestrator.llm_client.complete(
            messages=[
                {"role": "system", "content": "You are an expert C#/.NET Developer. Output JSON with 'files' list (filename, content)."},
                {"role": "user", "content": backend_prompt}
            ],
            model=backend_cfg.model,
            temperature=backend_cfg.temperature,
            json_mode=True # Assuming supported provider
        )

        frontend_task = self.orchestrator.llm_client.complete(
            messages=[
                {"role": "system", "content": "You are an expert React/TypeScript Developer. Output JSON with 'files' list (filename, content)."},
                {"role": "user", "content": frontend_prompt}
            ],
            model=frontend_cfg.model,
            temperature=frontend_cfg.temperature,
            json_mode=True
        )

        results = await asyncio.gather(backend_task, frontend_task, return_exceptions=True)
        
        backend_resp = results[0]
        frontend_resp = results[1]
        
        # Handle errors gracefully
        output = {"backend_files": [], "frontend_files": [], "errors": []}
        tokens_in = 0
        tokens_out = 0

        if isinstance(backend_resp, Exception):
            output["errors"].append(f"Backend generation failed: {backend_resp}")
        else:
            output["backend_files"] = self._parse_files(backend_resp.content)
            tokens_in += backend_resp.tokens_used["prompt"]
            tokens_out += backend_resp.tokens_used["completion"]

        if isinstance(frontend_resp, Exception):
            output["errors"].append(f"Frontend generation failed: {frontend_resp}")
        else:
            output["frontend_files"] = self._parse_files(frontend_resp.content)
            tokens_in += frontend_resp.tokens_used["prompt"]
            tokens_out += frontend_resp.tokens_used["completion"]

        return {
            "phase": "implementation",
            "output": output,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "models": f"{backend_cfg.model}, {frontend_cfg.model}"
        }

    def _build_prompt(self, path: Path, context: Dict[str, Any], rag_context: List[Dict[str, Any]], fallback: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                template = f.read()
        except FileNotFoundError:
            template = fallback + "\nArchitecture: {architecture}\nDomain Context: {domain_context}"
            
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

    def _parse_files(self, content: str) -> List[Dict[str, str]]:
        """Parse JSON output containing file list."""
        try:
            cleaned = content.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            data = json.loads(cleaned)
            # Expecting {"files": [{"path": "...", "content": "..."}]}
            if "files" in data:
                return data["files"]
            return []
        except json.JSONDecodeError:
            return [{"path": "raw_output.txt", "content": content}]
