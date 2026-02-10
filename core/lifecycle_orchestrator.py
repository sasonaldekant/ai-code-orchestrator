"""
Lifecycle Orchestrator for coordinating complex development workflows.

This module manages the breakdown of user requirements into milestones and tasks,
retrieves domain-specific knowledge, and orchestrates execution using the core V2 orchestrator.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.orchestrator_v2 import OrchestratorV2, PhaseStatus, PhaseResult
from rag.domain_aware_retriever import DomainAwareRetriever
from core.context_manager_v3 import ContextManagerV3
from core.code_executor import CodeExecutor, VerificationLoop
from core.file_writer import FileWriter, WriteMode
from core.code_evaluator import CodeEvaluator
from core.error_tracker import ErrorTracker
from core.guardrails import GuardrailMonitor, Action
from agents.specialist_agents.test_generator import TestGeneratorAgent
from api.event_bus import bus, Event, EventType

logger = logging.getLogger(__name__)

@dataclass
class Task:
    id: str
    description: str
    phase: str  # e.g., 'analyst', 'architect', 'implementation'
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending" # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None

@dataclass
class Milestone:
    id: str
    name: str # e.g. "Milestone 1: Database Updates"
    tasks: List[Task] = field(default_factory=list)
    status: str = "pending"

    def to_dict(self):
        return asdict(self)

class LifecycleOrchestrator:
    """
    Orchestrates the software development lifecycle (SDLC) for domain-specific projects.
    """

    def __init__(
        self, 
        domain_retriever: DomainAwareRetriever,
        simulation_mode: bool = False
    ):
        self.domain_retriever = domain_retriever
        self.simulation_mode = simulation_mode
        
        # Initialize Core Orchestrator
        if self.simulation_mode:
            from core.simulation.mock_llm import MockLLMClient
            logger.info("Initializing LifecycleOrchestrator in SIMULATION MODE")
            self.mock_client = MockLLMClient()
            self.orchestrator = OrchestratorV2(
                retriever=self.domain_retriever, 
                llm_client=self.mock_client
            )
        else:
            self.orchestrator = OrchestratorV2(retriever=self.domain_retriever)
            
        self.context_manager = ContextManagerV3(self.domain_retriever)
        self.milestones: List[Milestone] = []
        
        # Quality Gates: Code verification components
        self.code_executor = CodeExecutor(timeout_seconds=30)
        
        if self.simulation_mode:
            self.test_generator = TestGeneratorAgent(llm_client=self.mock_client)
        else:
            self.test_generator = TestGeneratorAgent()
            
        self.verification_loop = VerificationLoop(self.code_executor, max_retries=3)
        self.file_writer = FileWriter(project_root=".", auto_approve=False)
        self.code_evaluator = CodeEvaluator()
        self.error_tracker = ErrorTracker()
        self.guardrails = GuardrailMonitor()

    async def execute_request(self, user_request: str) -> Dict[str, Any]:
        """
        Main entry point: break down request and execute tasks.
        """
        logger.info(f"Starting lifecycle execution for request: {user_request[:50]}...")
        await bus.publish(Event(type=EventType.LOG, agent="Orchestrator", content=f"Initializing request: {user_request}"))
        
        # 1. Plan: Break down request into Milestones & Tasks
        # We use the 'analyst' phase of the underlying orchestrator for this
        await bus.publish(Event(type=EventType.THOUGHT, agent="Analyst", content="Analyzing requirements and domain context..."))
        
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
             err_msg = f"Planning failed: {plan_result.error}"
             await bus.publish(Event(type=EventType.ERROR, agent="Analyst", content=err_msg))
             return {"error": err_msg}

        # Parse plan into Milestones/Tasks (mock parsing for now)
        # In reality, this would parse the structured output from the LLM
        milestones = self._parse_plan(plan_result.output, user_request)
        self.milestones = milestones
        
        # Broadcast initial plan
        plan_data = {"milestones": [m.to_dict() for m in self.milestones]}
        await bus.publish(Event(type=EventType.PLAN, agent="Orchestrator", content=plan_data))
        
        # 2. Execute Milestones
        results = {}
        for milestone in self.milestones:
            await bus.publish(Event(type=EventType.MILESTONE, agent="Orchestrator", content=f"Starting Milestone: {milestone.id}"))
            results[milestone.id] = await self.execute_milestone(milestone)
            
            # Update plan status broadcast
            plan_data = {"milestones": [m.to_dict() for m in self.milestones]}
            await bus.publish(Event(type=EventType.PLAN, agent="Orchestrator", content=plan_data))
            
        return {
            "status": "completed",
            "plan": plan_data,
            "results": results
        }

    async def execute_milestone(self, milestone: Milestone) -> Dict[str, Any]:
        """
        Execute all tasks in a milestone, respecting dependencies.
        """
        logger.info(f"Executing milestone: {milestone.name}")
        milestone.status = "running"
        
        results = {}
        # Simple sequential execution for now
        # TODO: Implement DAG topological sort for parallel execution
        for task in milestone.tasks:
            task_result = await self.execute_task(task)
            results[task.id] = task_result
            if task.status == "failed":
                milestone.status = "failed"
                error_msg = f"Task {task.id} failed"
                self.error_tracker.log_error(
                    phase="execution",
                    error=error_msg,
                    context={"task_id": task.id, "milestone_id": milestone.id}
                )
                await bus.publish(Event(type=EventType.ERROR, agent="Orchestrator", content=f"Milestone {milestone.id} failed at task {task.id}"))
                return {"error": error_msg, "details": task_result}
                
        milestone.status = "completed"
        return results

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a single task with domain context.
        """
        logger.info(f"Executing task: {task.description}")
        task.status = "running"
        await bus.publish(Event(type=EventType.TASK, agent="Orchestrator", content=f"Starting Task: {task.description}"))
        
        # 1. Build Task Context
        await bus.publish(Event(type=EventType.THOUGHT, agent="ContextManager", content="Building task-specific context..."))
        context = self.context_manager.build_context(
            phase=task.phase,
            user_requirement=task.description,
            # Pass results from dependencies if needed
        )
        
        # 2. Execute via Core Orchestrator with Feedback Loop
        await bus.publish(Event(type=EventType.THOUGHT, agent=task.phase.capitalize(), content=f"Executing specialized agent workflow..."))
        
        if task.phase in ["architect", "implementation"]: # Phases suitable for review
             phase_result = await self.orchestrator.run_phase_with_feedback(
                phase=task.phase, # type: ignore
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
                phase=task.phase, # type: ignore
                schema_name=f"{task.phase}_output",
                context={
                    "task_description": task.description,
                    "domain_context": context.to_prompt_string(),
                },
                question=task.description
            )
        
        if phase_result.status == PhaseStatus.COMPLETED:
            # 3. Guardrail Check (Hallucinations)
            if task.phase == "implementation" and phase_result.output:
                code_check, _ = self._extract_code_from_output(phase_result.output)
                if code_check:
                    violations = self.guardrails.validate_code(code_check)
                    if violations:
                        for v in violations:
                            await bus.publish(Event(
                                type=EventType.WARNING,
                                agent="Guardrails",
                                content=f"Safety Violation: {v.message}"
                            ))
                        # If critical violations exist, fail the task or request retry
                        if any(v.severity == "critical" for v in violations):
                             msg = "Critical guardrail violation(s) detected. Aborting task."
                             await bus.publish(Event(type=EventType.ERROR, agent="Guardrails", content=msg))
                             task.status = "failed"
                             return {"error": msg, "violations": [asdict(v) for v in violations]}

            # 4. Verification Step for Implementation Phase
            if task.phase == "implementation" and phase_result.output:
                verification_result = await self._verify_code(phase_result.output, task)
                if not verification_result.get("verified", False):
                    await bus.publish(Event(
                        type=EventType.WARNING, 
                        agent="Verifier", 
                        content=f"Code verification failed: {verification_result.get('feedback', 'Unknown error')}"
                    ))
                # Store verification result but don't fail the task
                phase_result.output["verification"] = verification_result
            
            # 5. Evaluation Step (Quality/Security)
            if task.phase == "implementation" and phase_result.output:
                code_to_eval, _ = self._extract_code_from_output(phase_result.output)
                if code_to_eval:
                    eval_result = self.code_evaluator.evaluate(code_to_eval, "python") # Default to python for now
                    phase_result.output["evaluation"] = eval_result
                    await bus.publish(Event(
                        type=EventType.LOG, 
                        agent="Evaluator", 
                        content=f"Code Quality Score: {eval_result.get('overall_score', 0):.2f}/1.0"
                    ))

            # 6. File Writing Step
            if task.phase == "implementation" and phase_result.output:
                # Only write if verification passed or wasn't required
                verified = phase_result.output.get("verification", {}).get("verified", True)
                if verified:
                    write_result = await self._write_code(phase_result.output)
                    phase_result.output["file_write"] = write_result

            task.status = "completed"
            task.result = phase_result.output
            await bus.publish(Event(type=EventType.LOG, agent=task.phase.capitalize(), content=f"Task completed successfully."))
            return phase_result.output # type: ignore
        else:
            task.status = "failed"
            error_id = self.error_tracker.log_error(
                phase=task.phase,
                error=phase_result.error or "Unknown error",
                context={"task": task.description}
            )
            await bus.publish(Event(type=EventType.ERROR, agent=task.phase.capitalize(), content=f"Task failed: {phase_result.error} (ErrID: {error_id})"))
            return {"error": phase_result.error}

    def _parse_plan(self, plan_output: Any, original_request: str) -> List[Milestone]:
        """
        Mock parser to turn LLM output into internal Milestone/Task objects.
        In production, this would parse the JSON schema returned by the planner.
        """
        # Fallback/Mock implementation
        # Assuming the plan output might be unstructured or simple for now
        
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

    def _extract_code_from_output(self, output: Dict[str, Any]) -> Tuple[str, str]:
        """Helper to extract code and filename from various agent output formats."""
        # 1. Try flat structure (legacy/simple agents)
        code = output.get("code", output.get("implementation", ""))
        filename = output.get("filename", output.get("filepath", ""))
        
        # 2. Try nested 'output' structure (ImplementationAgent)
        if not code and "output" in output and isinstance(output["output"], dict):
            nested = output["output"]
            # Try backend files
            if "backend_files" in nested and nested["backend_files"]:
                file_obj = nested["backend_files"][0] # Take first file
                code = file_obj.get("content", "")
                filename = file_obj.get("path", "")
            # Try frontend files if backend empty
            elif "frontend_files" in nested and nested["frontend_files"]:
                file_obj = nested["frontend_files"][0]
                code = file_obj.get("content", "")
                filename = file_obj.get("path", "")
                
        return code, filename

    async def _verify_code(self, output: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """
        Verify generated code by generating and running tests.
        """
        await bus.publish(Event(
            type=EventType.THOUGHT, 
            agent="Verifier", 
            content="Starting code verification..."
        ))
        
        # Extract code from output
        code, _ = self._extract_code_from_output(output)
        
        if not code:
            return {"verified": True, "skipped": True, "reason": "No code to verify"}
        
        # Detect language
        language = self.test_generator.detect_language(code)
        if language == "unknown":
            return {"verified": True, "skipped": True, "reason": "Unknown language"}
        
        await bus.publish(Event(
            type=EventType.THOUGHT, 
            agent="TestGenerator", 
            content=f"Generating {language} tests..."
        ))
        
        # Generate tests
        try:
            test_suite = await self.test_generator.generate_unit_tests(code)
            test_code = test_suite.to_code()
        except Exception as e:
            logger.warning(f"Test generation failed: {e}")
            return {"verified": True, "skipped": True, "reason": f"Test generation failed: {e}"}
        
        await bus.publish(Event(
            type=EventType.THOUGHT, 
            agent="Verifier", 
            content=f"Running {len(test_suite.test_cases)} tests..."
        ))
        
        # Run verification loop
        result = await self.verification_loop.verify(
            code=code,
            test_code=test_code,
            language=language
        )
        
        if result.get("verified"):
            await bus.publish(Event(
                type=EventType.LOG, 
                agent="Verifier", 
                content=f"✓ All tests passed in {result.get('retries', 0)} retries"
            ))
        else:
            await bus.publish(Event(
                type=EventType.WARNING, 
                agent="Verifier", 
                content=f"✗ Tests failed after {result.get('retries', 0)} retries"
            ))
        
        return result

    async def _write_code(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write generated code to project files using FileWriter.
        """
        code, filename = self._extract_code_from_output(output)
        
        if not code or not filename:
            logger.warning("Missing code or filename for file write.")
            return {"status": "skipped", "reason": "Missing code or filename"}
            
        await bus.publish(Event(
            type=EventType.THOUGHT, 
            agent="FileWriter", 
            content=f"Writing code to {filename}..."
        ))
        
        # Determine write mode (default to overwrite for now, could be dynamic)
        result = self.file_writer.write(
            file_path=filename,
            content=code,
            mode=WriteMode.OVERWRITE,
            create_backup=True
        )
        
        if result.success:
            await bus.publish(Event(
                type=EventType.LOG, 
                agent="FileWriter", 
                content=f"Successfully wrote {filename}"
            ))
            return {
                "status": "success", 
                "path": result.file_path,
                "backup": result.backup_path
            }
        else:
            await bus.publish(Event(
                type=EventType.ERROR, 
                agent="FileWriter", 
                content=f"Failed to write {filename}: {result.error}"
            ))
            return {"status": "failed", "error": result.error}
