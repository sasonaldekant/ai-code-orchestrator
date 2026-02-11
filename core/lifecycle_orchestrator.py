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
from core.agents.specialist_agents.repair_agent import RepairAgent
from api.event_bus import bus, Event, EventType
from core.memory.experience_db import ExperienceDB
from core.vision_manager import VisionManager

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
        domain_retriever: Optional[DomainAwareRetriever] = None,
        simulation_mode: bool = False
    ):
        self.state = {}
        self.original_request = ""
        self.domain_retriever = domain_retriever or DomainAwareRetriever()
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
            
        self.repair_agent = RepairAgent(self.orchestrator.llm_client)
        self.experience_db = ExperienceDB()
            
        self.verification_loop = VerificationLoop(self.code_executor, max_retries=3)
        self.file_writer = FileWriter(project_root=".", auto_approve=False)
        self.code_evaluator = CodeEvaluator()
        self.error_tracker = ErrorTracker()
        self.guardrails = GuardrailMonitor()
        self.vision_manager = VisionManager(self.orchestrator.llm_client)

    async def execute_request(
        self, 
        user_request: str,
        mode: str = "standard",
        deep_search: bool = False,
        retrieval_strategy: str = "local",
        auto_fix: bool = False,
        budget_limit: Optional[float] = None,
        consensus_mode: bool = False,
        review_strategy: str = "basic",
        image: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Main entry point: break down request and execute tasks.
        """
        logger.info(f"Starting lifecycle execution for request: {user_request[:50]}... Mode: {mode}")
        await bus.publish(Event(type=EventType.LOG, agent="Orchestrator", content=f"Initializing request in {mode.upper()} mode"))
        # Reset state for new request
        self.state = {}
        self.original_request = user_request
        
        # 1. Plan: Break down request into Milestones & Tasks
        # We use the 'analyst' phase of the underlying orchestrator for this
        await bus.publish(Event(type=EventType.THOUGHT, agent="Analyst", content="Analyzing requirements and domain context..."))
        
        planning_context = self.context_manager.build_context(
            phase="planning",
            user_requirement=user_request
        )
        
        # Build context for Analyst
        analyst_context = {
            "role": "planner",
            "goal": "create_implementation_plan",
            "request": user_request,
            "requirements": user_request,
            "domain_context": planning_context.to_prompt_string()
        }

        # 1.1 Process Vision if image provided
        if image:
            await bus.publish(Event(type=EventType.LOG, agent="Orchestrator", content="Analyzing attached image for visual context..."))
            vision_result = await self.vision_manager.analyze_image(
                image, 
                "Identify all UI elements, layout, fields, and labels in this image. Be as specific as possible so we can replicate this structure using our components."
            )
            if vision_result["success"]:
                # Inject vision data into requirements for the analyst
                analyst_context["requirements"] = f"USER REQUEST: {user_request}\n\nVISUAL CONTEXT FROM IMAGE:\n{vision_result['analysis']}"
                await bus.publish(Event(type=EventType.LOG, agent="VisionManager", content="Visual analysis completed and injected into context."))

        if mode == "question":
            analyst_context["instruction_override"] = "### CRITICAL: DIRECT QUESTION MODE\nThe user is asking a question. DO NOT generate an implementation plan. Provide a detailed answer in the 'answer' field of the JSON output and keep 'implementation_plan' as an empty list []."

        # Execute planning phase
        # Note: In a real system, we'd have a specific 'planner' agent. 
        # Using 'analyst' as a proxy for now.
        plan_result = await self.orchestrator.run_phase_with_retry(
            phase="analyst",
            schema_name="implementation_plan", # Assuming this schema exists
            context=analyst_context,
            question=user_request,
            deep_search=deep_search,
            retrieval_strategy=retrieval_strategy,
            budget_limit=budget_limit,
            consensus_mode=consensus_mode,
            review_strategy=review_strategy,
        )
        
        if plan_result.status != PhaseStatus.COMPLETED:
             err_msg = f"Planning failed: {plan_result.error}"
             await bus.publish(Event(type=EventType.ERROR, agent="Analyst", content=err_msg))
             return {"error": err_msg}

        # [NEW] Publish model thinking if present (useful for reasoning models like Claude 3.7)
        if isinstance(plan_result.output, dict) and plan_result.output.get("thinking"):
             await bus.publish(Event(
                 type=EventType.THOUGHT, 
                 agent="Analyst", 
                 content=plan_result.output["thinking"]
             ))

        # [Phase 17/18] Check for direct answer (Q&A mode)
        output_data = plan_result.output
        answer = None
        
        if isinstance(output_data, dict):
            # Check nested and flat structures
            answer = output_data.get("answer") or output_data.get("output", {}).get("answer")
            
            # If implementation_plan is explicitly empty, it's a strong signal of Q&A
            impl_plan = output_data.get("implementation_plan") or output_data.get("output", {}).get("implementation_plan", {})
            if isinstance(impl_plan, dict) and impl_plan and not impl_plan.get("milestones"):
                if not answer:
                    logger.warning("Agent returned empty plan but no answer field. Checking for answer in output root.")
                    for k, v in output_data.items():
                        if k in ["answer", "response", "result"] and v:
                            answer = v
                            break

        if answer:
            logger.info(f"Direct answer detected: {answer}")
            await bus.publish(Event(
                type=EventType.INFO,
                agent="Analyst",
                content=f"### 📝 ANSWER\n\n{answer}"
            ))
            return {"status": "completed", "answer": answer, "results": {}}

        # 2. Extract plan and tasks
        # If we reached here, we expect a plan.
        milestones = self._parse_plan(plan_result.output, user_request)
        self.milestones = milestones
        
        # Broadcast initial plan
        plan_data = {"milestones": [m.to_dict() for m in self.milestones]}
        await bus.publish(Event(type=EventType.PLAN, agent="Orchestrator", content=plan_data))
        
        # 2. Execute Milestones
        results = {}
        for milestone in self.milestones:
            await bus.publish(Event(type=EventType.MILESTONE, agent="Orchestrator", content=f"Starting Milestone: {milestone.id}"))
            results[milestone.id] = await self.execute_milestone(
                milestone, 
                auto_fix=auto_fix,
                budget_limit=budget_limit,
                consensus_mode=consensus_mode,
                review_strategy=review_strategy
            )
            
            # Update plan status broadcast
            plan_data = {"milestones": [m.to_dict() for m in self.milestones]}
            await bus.publish(Event(type=EventType.PLAN, agent="Orchestrator", content=plan_data))
            
        return {
            "status": "completed",
            "plan": plan_data,
            "results": results
        }

    async def execute_milestone(
        self, 
        milestone: Milestone, 
        auto_fix: bool = False,
        budget_limit: Optional[float] = None,
        consensus_mode: bool = False,
        review_strategy: str = "basic"
    ) -> Dict[str, Any]:
        """
        Execute all tasks in a milestone, respecting dependencies.
        """
        logger.info(f"Executing milestone: {milestone.name}")
        milestone.status = "running"
        
        results = {}
        # Simple sequential execution for now
        # TODO: Implement DAG topological sort for parallel execution
        for task in milestone.tasks:
            task_result = await self.execute_task(
                task, 
                milestone,
                auto_fix=auto_fix,
                budget_limit=budget_limit,
                consensus_mode=consensus_mode,
                review_strategy=review_strategy
            )
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

    async def execute_task(
        self, 
        task: Task, 
        milestone: Milestone,
        auto_fix: bool = False,
        budget_limit: Optional[float] = None,
        consensus_mode: bool = False,
        review_strategy: str = "basic"
    ) -> Dict[str, Any]:
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
        
        # Schema mapping
        schema_map = {
            "analyst": "requirements",
            "architect": "architecture",
            "implementation": "implementation_output",
        }
        schema_name = schema_map.get(task.phase, f"{task.phase}_output")
        # Prepare enhanced context with previous phase results
        task_context = {
            "requirements": task.description, 
            "original_request": self.original_request,
            "milestone": milestone.name,
            "task_description": task.description, 
            "domain_context": context.to_prompt_string(),
        }
        
        # Inject previous phase results into context
        for phase, phase_res in self.state.items():
            task_context[phase] = phase_res

        if task.phase in ["architect", "implementation"]: # Phases suitable for review
            phase_result = await self.orchestrator.run_phase_with_feedback(
                phase=task.phase, # type: ignore
                schema_name=schema_name,
                context=task_context,
                question=task.description,
                budget_limit=budget_limit,
                consensus_mode=consensus_mode,
                review_strategy=review_strategy
            )
        else:
            # Simple execution for other phases
            phase_result = await self.orchestrator.run_phase_with_retry(
                phase=task.phase, # type: ignore
                schema_name=schema_name,
                context=task_context,
                question=task.description,
                budget_limit=budget_limit,
                consensus_mode=consensus_mode,
                review_strategy=review_strategy
            )
        
        if phase_result.status == PhaseStatus.COMPLETED:
            # Update state with successful result for downstream tasks
            self.state[task.phase] = phase_result.output
            task.result = phase_result.output
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
                    
                    # [Phase 16] Auto-Fix Logic
                    if auto_fix:
                        await bus.publish(Event(type=EventType.THOUGHT, agent="RepairAgent", content="Auto-Fix triggered. Analyzing failure..."))
                        
                        # Extract error details
                        exec_result = verification_result.get("result") # ExecutionResult obj
                        error_log = verification_result.get("feedback", "")
                        if exec_result:
                            error_log += f"\nStderr: {exec_result.stderr}\nStdout: {exec_result.stdout}"
                            
                        # Attempt fix
                        fix_result = await self.repair_agent.auto_fix(
                            error_log=error_log, 
                            test_command="Verification Test Suite" 
                        )
                        
                        if fix_result["success"]:
                            await bus.publish(Event(type=EventType.ACTION, agent="RepairAgent", content=f"Fix applied: {fix_result['summary']}"))
                            
                            # Verify again!
                            # We need to re-read the code from the file because RepairAgent overwrote it? 
                            # Or did RepairAgent return the new content?
                            # RepairAgent overwrote the file on disk, but phase_result.output still has old code.
                            # We should update phase_result.output with the new code from disk.
                            
                            # Extract filename to re-read
                            _, filename = self._extract_code_from_output(phase_result.output)
                            if filename and Path(filename).exists():
                                new_code = Path(filename).read_text(encoding="utf-8")
                                # Update phase result for next steps (like file writing - though RepairAgent already wrote it)
                                # But let's keep consistency
                                if isinstance(phase_result.output.get("output"), dict) and phase_result.output["output"].get("backend_files"):
                                    phase_result.output["output"]["backend_files"][0]["content"] = new_code
                                else:
                                    phase_result.output["code"] = new_code
                                
                                # Re-verify
                                verification_result = await self._verify_code(phase_result.output, task)
                                if verification_result.get("verified"):
                                    await bus.publish(Event(type=EventType.LOG, agent="RepairAgent", content="Fix verified! Tests passed."))
                                    
                                    # [Phase 17] Record Experience
                                    self.experience_db.record_fix(
                                        error_pattern=error_log,
                                        fix_strategy=fix_result['summary'],
                                        context=task.description
                                    )
                                else:
                                    await bus.publish(Event(type=EventType.WARNING, agent="RepairAgent", content="Fix failed validation."))
                        else:
                             await bus.publish(Event(type=EventType.ERROR, agent="RepairAgent", content=f"Auto-Fix failed: {fix_result['summary']}"))

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
            
            # [NEW] Publish model thinking if present
            if isinstance(phase_result.output, dict) and phase_result.output.get("thinking"):
                 await bus.publish(Event(
                     type=EventType.THOUGHT, 
                     agent=task.phase.capitalize(), 
                     content=phase_result.output["thinking"]
                 ))

            # Check if this task result contains a direct answer we should highlight
            answer = None
            if isinstance(phase_result.output, dict):
                answer = phase_result.output.get("answer") or phase_result.output.get("output", {}).get("answer")
            
            if answer:
                logger.info(f"Task produced a direct answer: {answer}")
                await bus.publish(Event(
                    type=EventType.INFO,
                    agent=task.phase.capitalize(),
                    content=f"### 📝 ANSWER\n\n{answer}"
                ))

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
        Parse LLM output into internal Milestone/Task objects.
        Supports both flat 'steps' and structured 'milestones'.
        """
        milestones_list = []
        
        # 1. Check for 'milestones' structure (New Analyst Format)
        impl_plan = None
        if isinstance(plan_output, dict):
            impl_plan = plan_output.get("implementation_plan")
            if not impl_plan and "output" in plan_output and isinstance(plan_output["output"], dict):
                impl_plan = plan_output["output"].get("implementation_plan")
        
        if isinstance(impl_plan, dict) and "milestones" in impl_plan and isinstance(impl_plan["milestones"], list):
            for m_data in impl_plan["milestones"]:
                if not isinstance(m_data, dict): continue
                
                m_id = str(m_data.get("id", f"m{len(milestones_list)+1}"))
                m_name = str(m_data.get("name", "Unnamed Milestone"))
                tasks_data = m_data.get("tasks", [])
                
                tasks = []
                if isinstance(tasks_data, list):
                    for t_data in tasks_data:
                        if isinstance(t_data, dict):
                            t_id = str(t_data.get("id", f"t{len(tasks)+1}"))
                            t_desc = str(t_data.get("description", ""))
                            # Phase detection
                            t_phase = str(t_data.get("phase", "implementation")).lower()
                            
                            # Heuristics if phase is generic or missing
                            desc_lower = t_desc.lower()
                            analyst_keywords = ["analyze", "check", "count", "list", "search", "find", "read", "how many", "koliko", "sta", "šta", "ima", "nabroj", "koji"]
                            architect_keywords = ["design", "plan", "architecture", "structure", "arhitektura", "planiraj", "dizajn"]
                            testing_keywords = ["test", "verify", "validate", "proveri", "potvrdi", "testiraj"]
                            
                            if t_phase not in ["analyst", "architect", "implementation", "testing"]:
                                if any(k in desc_lower for k in analyst_keywords): t_phase = "analyst"
                                elif any(k in desc_lower for k in architect_keywords): t_phase = "architect"
                                elif any(k in desc_lower for k in testing_keywords): t_phase = "testing"
                                else: t_phase = "implementation"
                                
                            tasks.append(Task(id=t_id, description=t_desc, phase=t_phase))
                
                if tasks:
                    milestones_list.append(Milestone(id=m_id, name=m_name, tasks=tasks))

        # 2. Fallback to flat 'steps' structure (Legacy)
        if not milestones_list:
            task_list = []
            steps = []
            if isinstance(plan_output, list):
                steps = plan_output
            elif isinstance(plan_output, dict):
                steps = plan_output.get("steps", plan_output.get("plan", []))
                if not steps and "output" in plan_output and isinstance(plan_output["output"], dict):
                    nested = plan_output["output"]
                    steps = nested.get("steps", nested.get("plan", []))
            
            if isinstance(steps, list):
                for i, step in enumerate(steps):
                    desc = step.get("description", str(step)) if isinstance(step, dict) else str(step)
                    phase = "implementation"
                    desc_lower = desc.lower()
                    if any(k in desc_lower for k in ["analyze", "check", "count", "list", "search", "find", "read", "how many", "koliko", "sta", "šta"]):
                        phase = "analyst"
                    elif any(k in desc_lower for k in ["design", "plan", "architecture", "arhitektura", "planiraj"]):
                        phase = "architect"
                    
                    task_list.append(Task(id=f"task_{i}", description=desc, phase=phase))
            
            if task_list:
                milestones_list.append(Milestone(id="m1", name="Implementation Plan", tasks=task_list))

        # 3. Final Fallback if still empty
        if not milestones_list:
            req_lower = original_request.lower()
            is_question = "?" in original_request or any(k in req_lower for k in ["how", "what", "how many", "list", "koliko", "sta", "šta", "koji", "ima"])
            phase = "analyst" if is_question else "implementation"
            
            milestones_list.append(Milestone(
                id="m1", 
                name="Quick Response", 
                tasks=[Task(id="task_0", description=f"Execute: {original_request}", phase=phase)]
            ))

        return milestones_list

    def _extract_code_from_output(self, output: Dict[str, Any]) -> Tuple[str, str]:
        """Helper to extract code and filename from various agent output formats."""
        # 1. Try flat structure (legacy/simple agents)
        code = output.get("code", output.get("implementation", ""))
        if not isinstance(code, str):
            code = ""
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
