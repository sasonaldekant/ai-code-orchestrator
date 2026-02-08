"""
Main orchestrator for coordinating phase agents and cost management.

This class exposes methods to run individual phases or an entire pipeline.
It handles RAG retrieval, model selection, cost management, validation
and tracing.  Agents are executed asynchronously.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .model_router import ModelRouter
from .llm_client import LLMClient
from .cost_manager import CostManager
from .validator import OutputValidator
from .tracer import TracingService
from .retriever import RAGRetriever

import json

from ..agents.phase_agents.analyst import AnalystAgent
from ..agents.phase_agents.architect import ArchitectAgent
from ..agents.phase_agents.implementation import ImplementationAgent
from ..agents.phase_agents.testing import TestingAgent

logger = logging.getLogger(__name__)


class Orchestrator:
    """Coordinates the multi‑phase AI code generation workflow."""

    def __init__(self, config_path: str = "config/model_mapping.yaml") -> None:
        self.cost_manager = CostManager()
        self.model_router = ModelRouter(config_path)
        self.llm_client = LLMClient(self.cost_manager)
        self.validator = OutputValidator()
        self.tracer = TracingService()
        self.retriever = RAGRetriever()

        # instantiate phase agents
        self.phase_agents: Dict[str, Any] = {
            "analyst": AnalystAgent(self),
            "architect": ArchitectAgent(self),
            "implementation": ImplementationAgent(self),
            "testing": TestingAgent(self),
        }

        # output directory
        self.outputs_dir = Path("outputs")
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

    async def run_phase(
        self,
        phase: str,
        schema_name: str,
        context: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        Run a single phase agent with optional RAG enrichment and schema validation.

        Parameters
        ----------
        phase : str
            Name of the phase ("analyst", "architect", "implementation", "testing").
        schema_name : str
            Name of the JSON schema used for validation.
        context : dict, optional
            Previous phase outputs to be passed into the next phase.
        question : str, optional
            RAG query to enrich the prompt.
        top_k : int
            Number of RAG results to retrieve.
        Returns
        -------
        dict
            The validated output of the phase.
        """
        self.tracer.log_event("phase_start", {
            "phase": phase,
            "schema": schema_name,
            "timestamp": datetime.utcnow().isoformat(),
        })
        # RAG context
        # retrieve context from the RAG subsystem.  In the enhanced architecture
        # the retriever may perform vector search; here retrieval is synchronous.
        rag_context: list = []
        if question:
            # call the retriever (may be async in future) and persist context for audit
            rag_context = self.retriever.retrieve(question, top_k=top_k)
            rag_path = self.outputs_dir / f"rag_context_{phase}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
            with open(rag_path, "w", encoding="utf-8") as f:
                json.dump(rag_context, f, indent=2)

        agent = self.phase_agents.get(phase)
        if not agent:
            raise ValueError(f"Unknown phase: {phase}")
        result = await agent.execute(context=context or {}, rag_context=rag_context)
        # validate
        # Build schema path relative to phase_schemas.  Validator will resolve relative
        # paths from its configured base directory.
        schema_path = f"phase_schemas/{schema_name}.json"
        validation = self.validator.validate(result, schema_path)
        if not validation["valid"]:
            self.tracer.log_event("validation_failed", {
                "phase": phase,
                "errors": validation["errors"],
            })
            raise ValueError(f"Validation failed for phase {phase}: {validation['errors']}")
        # save output
        out_path = self.outputs_dir / f"{phase}_{schema_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        self.tracer.log_event("phase_complete", {
            "phase": phase,
            "output_path": str(out_path),
        })
        return result

    async def run_pipeline(
        self,
        initial_requirements: str,
        question: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run the full pipeline: analyst → architect → implementation → testing.

        Parameters
        ----------
        initial_requirements : str
            Natural language description of the feature to implement.
        question : str, optional
            Additional question for the RAG retriever during the analyst phase.
        Returns
        -------
        dict
            The outputs of all phases.
        """
        # reset task budget before pipeline
        self.cost_manager.reset_task()
        results: Dict[str, Any] = {}
        # analyst
        analyst_output = await self.run_phase(
            phase="analyst",
            schema_name="requirements",
            context={"requirements": initial_requirements},
            question=question,
        )
        results["analyst"] = analyst_output
        # architect
        architect_output = await self.run_phase(
            phase="architect",
            schema_name="architecture",
            context=analyst_output,
        )
        results["architect"] = architect_output
        # implementation – this phase can run backend & frontend concurrently
        implementation_output = await self.run_phase(
            phase="implementation",
            schema_name="implementation",
            context=architect_output,
        )
        results["implementation"] = implementation_output
        # testing
        testing_output = await self.run_phase(
            phase="testing",
            schema_name="testing",
            context=implementation_output,
        )
        results["testing"] = testing_output
        # save full pipeline
        pipeline_path = self.outputs_dir / f"pipeline_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
        with open(pipeline_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        self.tracer.log_event("pipeline_complete", {
            "pipeline_path": str(pipeline_path),
            "total_cost": self.cost_manager.total_cost,
        })
        return results
