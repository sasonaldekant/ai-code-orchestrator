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

        # 3. Combine into EnrichedContext
        return EnrichedContextV3(
            phase=phase,
            specialty=specialty,
            domain_context=domain_context,
            rules=rules,
            formatted_prompt_context=formatted_context
        )
