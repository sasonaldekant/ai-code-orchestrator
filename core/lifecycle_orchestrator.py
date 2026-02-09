"""
Lifecycle Orchestrator for coordinating complex development workflows.

This module manages the breakdown of user requirements into milestones and tasks,
retrieves domain-specific knowledge, and orchestrates execution using the core V2 orchestrator.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.orchestrator_v2 import OrchestratorV2, PhaseStatus, PhaseResult
from rag.domain_aware_retriever import DomainAwareRetriever
from core.context_manager_v3 import ContextManagerV3

logger = logging.getLogger(__name__)

@dataclass
class Task:
    id: str
    description: str
    phase: str  # e.g., 'analyst', 'architect', 'implementation'
    dependencies: List[str] = field(default_factory=list)
    status: PhaseStatus = PhaseStatus.PENDING
    result: Optional[Dict[str, Any]] = None

@dataclass
class Milestone:
    id: str
    name: str
    tasks: List[Task] = field(default_factory=list)
    status: PhaseStatus = PhaseStatus.PENDING

class LifecycleOrchestrator:
    """
    Orchestrates the software development lifecycle (SDLC) for domain-specific projects.
    """

    def __init__(
        self, 
        orchestrator: Optional[OrchestratorV2] = None,
        domain_retriever: Optional[DomainAwareRetriever] = None
    ):
        self.domain_retriever = domain_retriever or DomainAwareRetriever()
        
        # Inject our domain retriever into the orchestrator context
        self.orchestrator = orchestrator or OrchestratorV2(
            retriever=self.domain_retriever
        )
        
        self.context_manager = ContextManagerV3(domain_retriever=self.domain_retriever)
        self.milestones: List[Milestone] = []

    async def execute_request(self, user_request: str) -> Dict[str, Any]:
        """
        Main entry point: break down request and execute tasks.
        """
        logger.info(f"Starting lifecycle execution for request: {user_request[:50]}...")
        
        # 1. Plan: Break down request into Milestones & Tasks
        # We use the 'analyst' phase of the underlying orchestrator for this
        planning_context = self.context_manager.build_context(
            phase="planning",
            user_requirement=user_request
        )
        
        # Execute planning phase
        # Note: In a real system, we'd have a specific 'planner' agent. 
        # Using 'analyst' as a proxy for now.
        plan_result = await self.orchestrator.run_phase_with_retry(
            phase="analyst",
            schema_name="implementation_plan", # Assuming this schema exists
            context={
                "role": "planner",
                "goal": "create_implementation_plan",
                "request": user_request,
                "domain_context": planning_context.to_prompt_string()
            },
            question=user_request
        )
        
        if plan_result.status != PhaseStatus.COMPLETED:
             return {"error": f"Planning failed: {plan_result.error}"}

        # Parse plan into Milestones/Tasks (mock parsing for now)
        # In reality, this would parse the structured output from the LLM
        milestones = self._parse_plan(plan_result.output, user_request)
        self.milestones = milestones
        
        # 2. Execute Milestones
        results = {}
        for milestone in self.milestones:
            results[milestone.id] = await self.execute_milestone(milestone)
            
        return {
            "status": "completed",
            "plan": plan_result.output,
            "results": results
        }

    async def execute_milestone(self, milestone: Milestone) -> Dict[str, Any]:
        """
        Execute all tasks in a milestone, respecting dependencies.
        """
        logger.info(f"Executing milestone: {milestone.name}")
        milestone.status = PhaseStatus.RUNNING
        
        results = {}
        # Simple sequential execution for now
        # TODO: Implement DAG topological sort for parallel execution
        for task in milestone.tasks:
            task_result = await self.execute_task(task)
            results[task.id] = task_result
            if task.status == PhaseStatus.FAILED:
                milestone.status = PhaseStatus.FAILED
                return {"error": f"Task {task.id} failed", "details": task_result}
                
        milestone.status = PhaseStatus.COMPLETED
        return results

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a single task with domain context.
        """
        logger.info(f"Executing task: {task.description}")
        task.status = PhaseStatus.RUNNING
        
        # 1. Build Task Context
        context = self.context_manager.build_context(
            phase=task.phase,
            user_requirement=task.description,
            # Pass results from dependencies if needed
        )
        
        # 2. Execute via Core Orchestrator with Feedback Loop
        if task.phase in ["architect", "implementation"]: # Phases suitable for review
             phase_result = await self.orchestrator.run_phase_with_feedback(
                phase=task.phase,
                schema_name=f"{task.phase}_output",
                context={
                    "task_description": task.description,
                    "domain_context": context.to_prompt_string(),
                },
                question=task.description
            )
        else:
            # Simple execution for other phases
            phase_result = await self.orchestrator.run_phase_with_retry(
                phase=task.phase,
                schema_name=f"{task.phase}_output",
                context={
                    "task_description": task.description,
                    "domain_context": context.to_prompt_string(),
                },
                question=task.description
            )
        
        if phase_result.status == PhaseStatus.COMPLETED:
            task.status = PhaseStatus.COMPLETED
            task.result = phase_result.output
            return phase_result.output # type: ignore
        else:
            task.status = PhaseStatus.FAILED
            return {"error": phase_result.error}

    def _parse_plan(self, plan_output: Any, original_request: str) -> List[Milestone]:
        """
        Mock parser to turn LLM output into internal Milestone/Task objects.
        In production, this would parse the JSON schema returned by the planner.
        """
        # Fallback/Mock implementation
        # Assuming the plan output might be unstructured or simple for now
        
        # Create a single default milestone with tasks inferred from request
        # This is a PLACEHOLDER until the Analyst agent returns strict JSON matching our schema
        
        task_list = []
        # If the output is a list of steps, use them
        if isinstance(plan_output, list):
             for i, step in enumerate(plan_output):
                 task_list.append(Task(
                     id=f"task_{i}",
                     description=str(step),
                     phase="implementation" # Default phase
                 ))
        elif isinstance(plan_output, dict) and "steps" in plan_output:
             for i, step in enumerate(plan_output["steps"]):
                 task_list.append(Task(
                     id=f"task_{i}",
                     description=step.get("description", str(step)),
                     phase=step.get("phase", "implementation")
                 ))
        else:
             # Default single task
             task_list.append(Task(
                 id="task_0",
                 description=f"Implement: {original_request}",
                 phase="implementation"
             ))

        return [Milestone(id="m1", name="Implementation", tasks=task_list)]
