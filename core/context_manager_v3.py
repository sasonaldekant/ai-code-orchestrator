"""
Context Manager v3 for Domain-Agnostic AI Code Orchestrator.
Uses DomainAwareRetriever to inject structured domain knowledge into prompts.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import yaml

from rag.domain_aware_retriever import DomainAwareRetriever, DomainContext

logger = logging.getLogger(__name__)

@dataclass
class EnrichedContextV3:
    """Context enriched with structured domain knowledge."""
    phase: str
    specialty: str | None
    domain_context: DomainContext
    rules: Dict[str, Any]
    formatted_prompt_context: str
    
    def to_prompt_string(self) -> str:
        """Return the pre-formatted prompt context string."""
        return self.formatted_prompt_context


class ContextManagerV3:
    """
    Manages context construction using DomainAwareRetriever.
    """

    def __init__(
        self,
        domain_retriever: DomainAwareRetriever | None = None,
        enable_rag: bool = True,
    ) -> None:
        self.enable_rag = enable_rag
        if enable_rag:
            self.retriever = domain_retriever or DomainAwareRetriever()
        else:
            self.retriever = None

    def build_context(
        self,
        phase: str,
        user_requirement: str,
        specialty: str | None = None,
        project_config: Dict[str, Any] | None = None,
    ) -> EnrichedContextV3:
        """
        Build enriched context for a given phase and requirement.
        """
        # 1. Static Configuration (Rules)
        rules = project_config.get("rules", {}) if project_config else {}

        # 2. Dynamic Domain Knowledge
        domain_context = DomainContext() # Empty by default
        formatted_context = ""
        
        if self.enable_rag and self.retriever and user_requirement:
            try:
                # Retrieve structured context
                domain_context = self.retriever.retrieve_domain_context(
                    user_requirement=user_requirement
                )
                
                # Format for prompt (using optimization/compression)
                formatted_context = self.retriever.format_context_for_prompt(domain_context)
                
            except Exception as e:
                logger.error(f"Failed to retrieve/format domain context: {e}")
                formatted_context = "Error retrieving domain context."

        # 3. Project Structure Injection (for architectural awareness)
        project_structure = self._get_project_structure()
        formatted_context += f"\n\n[Project Structure]:\n{project_structure}\n"
        
        # 4. Golden Rules Injection (AI_CONTEXT.md)
        golden_rules = self._get_golden_rules()
        if golden_rules:
            formatted_context += f"\n\n[GOLDEN RULES & STANDARDS]:\n{golden_rules}\n"

        # 5. Combine into EnrichedContext
        return EnrichedContextV3(
            phase=phase,
            specialty=specialty,
            domain_context=domain_context,
            rules=rules,
            formatted_prompt_context=formatted_context
        )

    def _get_project_structure(self) -> str:
        """Scan key directories to provide structural context."""
        try:
            structure = []
            exclude = {'.git', '.venv', '__pycache__', 'node_modules', 'dist', 'coverage'}
            
            root = Path(".")
            # Limit to depth 2 to save tokens, focus on src/components/api
            for path in root.rglob("*"):
                if any(part in exclude for part in path.parts):
                    continue
                if path.is_file():
                    # Only include relevant code files
                    if path.suffix in {'.py', '.tsx', '.ts', '.cs', '.js', '.yaml', '.json'}:
                        structure.append(str(path))
                        
                if len(structure) > 200: # Limit to 200 files to avoid context overflow
                    break
                    
            return "\n".join(structure[:200])
        except Exception as e:
            logger.error(f"Failed to scan project structure: {e}")
            return "Error scanning project structure."

    def _get_golden_rules(self) -> str:
        """Load the AI_CONTEXT.md file."""
        try:
            # Assumes rag/AI_CONTEXT.md is relative to project root
            # core/context_manager_v3.py -> ../rag/AI_CONTEXT.md
            context_path = Path(__file__).parent.parent / "rag" / "AI_CONTEXT.md"
            if context_path.exists():
                return context_path.read_text(encoding="utf-8")
            return ""
        except Exception as e:
            logger.warning(f"Failed to load AI_CONTEXT.md: {e}")
            return ""
