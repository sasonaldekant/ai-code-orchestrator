"""
Enhanced orchestrator with advanced features:
- Retry logic with exponential backoff
- Feedback loop system for iterative improvements
- Enhanced error handling and recovery
- Parallel execution with dependency management
- Dynamic strategy selection
- Real-time monitoring and metrics
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import time

from .model_cascade_router import ModelCascadeRouter, ModelConfig
from .llm_client_v2 import LLMClientV2
from .cost_manager import CostManager
from .validator import OutputValidator
from .tracer import TracingService
from rag.domain_aware_retriever import DomainAwareRetriever as RAGRetriever
from .self_healing_manager import SelfHealingManager
from .prompt_gate import PromptGate
from core.agents.specialist_agents.retrieval_agent import RetrievalAgent
from .external_integration import ExternalIntegration

logger = logging.getLogger(__name__)


class ExecutionStrategy(Enum):
    """Execution strategies for different task complexities."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    ADAPTIVE = "adaptive"


class PhaseStatus(Enum):
    """Status of a phase execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class PhaseResult:
    """Result of a phase execution."""
    phase: str
    status: PhaseStatus
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    attempts: int = 0
    execution_time: float = 0.0
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeedbackResult:
    """Feedback from quality assessment."""
    quality_score: float
    issues: List[str]
    suggestions: List[str]
    needs_iteration: bool


class OrchestratorV2:
    """
    Enhanced orchestrator with advanced orchestration capabilities.
    
    Features:
    - Automatic retry with exponential backoff
    - Feedback loop for iterative refinement
    - Parallel execution where possible
    - Dynamic strategy selection
    - Comprehensive monitoring and metrics
    """


    def __init__(
        self,
        config_path: str = "config/model_mapping_v2.yaml",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        max_feedback_iterations: int = 3,
        retriever: Optional[Any] = None,
        llm_client: Optional[Any] = None,
        local_task_budget: Optional[float] = None
    ) -> None:
        # Configuration
        import yaml
        self.limits_config = {}
        try:
            with open("config/limits.yaml", "r") as f:
                self.limits_config = yaml.safe_load(f) or {}
        except Exception:
            pass

        global_conf = self.limits_config.get("global", {})
        
        # Initialize CostManager with global limits from config
        self.cost_manager = CostManager(
            per_task_budget=global_conf.get("per_task_budget", 0.50),
            per_hour_budget=global_conf.get("per_hour_budget", 5.0),
            per_day_budget=global_conf.get("per_day_budget", 40.0),
            local_task_budget=local_task_budget
        )
        
        self.model_router = ModelCascadeRouter(config_path)
        self.llm_client = llm_client or LLMClientV2(self.cost_manager)
        self.validator = OutputValidator()
        self.tracer = TracingService()
        self.retriever = retriever or RAGRetriever()
        self.self_healer = SelfHealingManager(self.llm_client, self.model_router)
        self.prompt_gate = PromptGate(self.llm_client, self.model_router)
        
        # Initialize Producer-Reviewer Loop
        from core.producer_reviewer import ProducerReviewerLoop
        self.producer_reviewer = ProducerReviewerLoop(self.llm_client, self.cost_manager)

        self.max_retries = max_retries if max_retries != 3 else global_conf.get("max_retries", 3)
        self.retry_delay = retry_delay
        self.max_feedback_iterations = max_feedback_iterations if max_feedback_iterations != 3 else global_conf.get("max_feedback_iterations", 3)
        self.deep_search_default = global_conf.get("deep_search", False)
        self.global_temperature = global_conf.get("temperature", 0.0)

        # Phase agents will be initialized lazily
        self._phase_agents: Optional[Dict[str, Any]] = None

        # Output directory
        self.outputs_dir = Path("outputs")
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        # Metrics
        self.metrics: Dict[str, Any] = {
            "total_phases_executed": 0,
            "total_retries": 0,
            "total_feedback_iterations": 0,
            "phase_execution_times": {},
            "error_counts": {},
        }

    @property
    def phase_agents(self) -> Dict[str, Any]:
        """Lazy initialization of phase agents."""
        if self._phase_agents is None:
            from agents.phase_agents.analyst import AnalystAgent
            from agents.phase_agents.architect import ArchitectAgent
            from agents.phase_agents.implementation import ImplementationAgent
            from agents.phase_agents.testing import TestingAgent

            self._phase_agents = {
                "analyst": AnalystAgent(self),
                "architect": ArchitectAgent(self),
                "implementation": ImplementationAgent(self),
                "testing": TestingAgent(self),
            }
        return self._phase_agents

    async def run_phase_with_retry(
        self,
        phase: str,
        schema_name: str,
        context: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
        top_k: int = 3,
        deep_search: bool = False,
        retrieval_strategy: str = "local",
        budget_limit: Optional[float] = None,
        consensus_mode: bool = False,
        review_strategy: str = "basic",
        model_override: Optional[str] = None,
    ) -> PhaseResult:
        """
        Run a phase with automatic retry on failure.
        
        Args:
            phase: Name of the phase
            schema_name: Schema for validation
            context: Context from previous phases
            question: RAG query
            top_k: Number of RAG results
            
        Returns:
            PhaseResult with execution details
        """
        result = PhaseResult(phase=phase, status=PhaseStatus.PENDING)
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                result.attempts = attempt + 1
                result.status = PhaseStatus.RUNNING if attempt == 0 else PhaseStatus.RETRYING
                
                msg = f"Executing phase '{phase}' (attempt {attempt + 1}/{self.max_retries})"
                logger.info(msg)
                print(f":::STEP:{{\"type\": \"analyzing\", \"text\": \"{msg}\"}}:::", flush=True)
                
                # Execute phase
                output = await self._execute_phase(
                    phase=phase,
                    schema_name=schema_name,
                    context=context,
                    question=question,
                    top_k=top_k,
                    deep_search=deep_search,
                    retrieval_strategy=retrieval_strategy,
                    budget_limit=budget_limit,
                    consensus_mode=consensus_mode,
                    review_strategy=review_strategy,
                    model_override=model_override,
                )
                
                result.output = output
                result.status = PhaseStatus.COMPLETED
                result.execution_time = time.time() - start_time
                
                logger.info(f"Phase '{phase}' completed successfully")
                print(f":::STEP:{{\"type\": \"done\", \"text\": \"Phase '{phase}' finished\"}}:::", flush=True)

                self.metrics["total_phases_executed"] += 1
                
                return result
                
            except Exception as e:
                error_msg = f"Error in phase '{phase}' (attempt {attempt + 1}): {str(e)}"
                logger.error(error_msg)
                
                result.error = error_msg
                self.metrics["total_retries"] += 1
                self.metrics["error_counts"][phase] = self.metrics["error_counts"].get(phase, 0) + 1
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    result.status = PhaseStatus.FAILED
                    result.execution_time = time.time() - start_time
                    logger.error(f"Phase '{phase}' failed after {self.max_retries} attempts")
                    
        return result

    async def _execute_phase(
        self,
        phase: str,
        schema_name: str,
        context: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
        top_k: int = 3,
        deep_search: bool = False,
        retrieval_strategy: str = "local",
        budget_limit: Optional[float] = None,
        consensus_mode: bool = False,
        review_strategy: str = "basic",
        model_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Internal method to execute a single phase.
        """
        # [Check Budget]
        if budget_limit is not None:
            current_cost = self.cost_manager.total_cost
            if current_cost >= budget_limit:
                raise ValueError(f"Budget limit exceeded (${current_cost:.2f} >= ${budget_limit:.2f})")

        self.tracer.log_event("phase_start", {
            "phase": phase,
            "schema": schema_name,
            "deep_search": deep_search,
            "timestamp": datetime.utcnow().isoformat(),
            "consensus_mode": consensus_mode
        })
        
        # RAG retrieval
        rag_context: list = []
        
        # [Phase 15] Agentic Retrieval / Deep Search
        if deep_search and question:
             msg = f"Running Deep Search (Investigator) for: {question[:50]}..."
             logger.info(msg)
             print(f":::STEP:{{\"type\": \"analyzing\", \"text\": \"{msg}\"}}:::", flush=True)
             
             # Preliminary RAG for planning
             rag_context = self.retriever.retrieve(question, top_k=top_k)
             
             initial_plan = None
        
             # Phase 2.5: Deep Research (Tier 3/4)
             msg = "Conducting Deep Research..."
             print(f":::STEP:{{\"type\": \"thinking\", \"text\": \"{msg}\"}}:::", flush=True)
            
             research_config = self.model_router.select_model("research", complexity="high")
            
             if "sonar" in research_config.model:
                  investigator = RetrievalAgent(self.llm_client)
                  investigator.config = research_config 
                  deep_findings = await investigator.run(question, initial_plan=initial_plan)
             else:
                  deep_findings = await self.llm_client.complete(
                      messages=[{"role": "user", "content": f"Analyze this large context regarding: {question}"}],
                      model=research_config.model,
                      max_tokens=8000
                  ).content
            
             rag_context.append({"source": "deep_research", "content": deep_findings})

        elif question:
             # [Task 3.2] Tier-Based Query Routing
             tier_id = context.get("rag_tier") if context else None
             if tier_id:
                  logger.info(f"Performing Tier-Based RAG retrieval for Tier {tier_id}")
                  if hasattr(self.retriever, "retrieve_tier"):
                      rag_context = self.retriever.retrieve_tier(tier_id, question, top_k=top_k)
                  else:
                      rag_context = self.retriever.retrieve(question, top_k=top_k)
             else:
                  rag_context = self.retriever.retrieve(question, top_k=top_k)
        
        # Estimate context size for routing
        # Rough calc: 1 token ~= 4 chars
        context_str = json.dumps(context or {}) + json.dumps(rag_context)
        context_tokens = len(context_str) // 4
        
        # Get optimal model via cascade for main task
        if model_override:
            logger.info(f"Using manual model override: {model_override}")
            model_config = ModelConfig(
                model=model_override,
                provider="manual", # Or detect provider if needed
                tier=2,
                temperature=0.0
            )
        else:
            complexity = "high" if deep_search or (question and len(question)>500) else "simple"
            model_config = self.model_router.select_model(
                phase, 
                complexity=complexity, 
                context_tokens=context_tokens
            )
        
        # Persist context for audit
        rag_path = self.outputs_dir / f"rag_context_{phase}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
        with open(rag_path, "w", encoding="utf-8") as f:
            json.dump(rag_context, f, indent=2)

        # Get agent and execute
        agent = self.phase_agents.get(phase)
        if not agent:
            raise ValueError(f"Unknown phase: {phase}")
            
        # Inject run-time configuration into context
        execution_context = context or {}
        execution_context.update({
            "consensus_mode": consensus_mode,
            "review_strategy": review_strategy
        })

        try:
            result = await agent.execute(context=execution_context, rag_context=rag_context)
        except Exception as e:
            # [Task 6.2] Record failure for Adaptive Tuning
            self.model_router.metrics_tracker.record_outcome(model_config.tier, success=False)
            raise e
        
        # Validate
        validation = self.validator.validate(result, schema_name)
        
        if not validation["valid"]:
            error_msg = f"Validation failed for phase {phase}: {validation['errors']}"
            self.tracer.log_event("validation_failed", {
                "phase": phase,
                "errors": validation["errors"],
            })
            
            # [Task 6.2] Record failure for Adaptive Tuning
            self.model_router.metrics_tracker.record_outcome(model_config.tier, success=False)
            
            raise ValueError(error_msg)
        
        # Save output
        out_path = self.outputs_dir / f"{phase}_{schema_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            
        self.tracer.log_event("phase_complete", {
            "phase": phase,
            "output_path": str(out_path),
        })
        
        # [Task 6.2] Record success for Adaptive Tuning
        self.model_router.metrics_tracker.record_outcome(model_config.tier, success=True)
        
        return result

    async def run_phase_with_feedback(
        self,
        phase: str,
        schema_name: str,
        context: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
        quality_threshold: float = 0.8,
        budget_limit: Optional[float] = None,
        consensus_mode: bool = False,
        review_strategy: str = "basic",
        model_override: Optional[str] = None,
    ) -> PhaseResult:
        """
        Run phase with iterative feedback loop for quality improvement.
        
        Args:
            phase: Name of the phase
            schema_name: Schema for validation
            context: Context from previous phases
            question: RAG query
            quality_threshold: Minimum acceptable quality score
            
        Returns:
            PhaseResult with final output
        """
        logger.info(f"Starting phase '{phase}' with iterative feedback")
        
        current_context = context or {}
        best_result: Optional[PhaseResult] = None
        best_score = 0.0

        for iteration in range(self.max_feedback_iterations):
            msg = f"Feedback iteration {iteration + 1}/{self.max_feedback_iterations}"
            logger.info(msg)
            print(f":::STEP:{{\"type\": \"thinking\", \"text\": \"{msg}\"}}:::", flush=True)
            
            # Execute phase
            result = await self.run_phase_with_retry(
                phase=phase,
                schema_name=schema_name,
                context=current_context,
                question=question,
                budget_limit=budget_limit,
                consensus_mode=consensus_mode,
                review_strategy=review_strategy,
                model_override=model_override,
            )
            
            if result.status != PhaseStatus.COMPLETED:
                logger.warning(f"Phase failed during iteration {iteration}")
                return result
            
            # Use the internal _assess_quality (which we will improve or keep)
            # Re-adding _assess_quality structure but improved
            feedback = await self._assess_quality(result.output, phase)
            
            logger.info(f"Quality score: {feedback.quality_score:.2f}")
            
            if feedback.quality_score >= quality_threshold:
                logger.info(f"Quality threshold met for phase '{phase}'")
                return result

            # Keep track of best result
            if feedback.quality_score > best_score:
                best_score = feedback.quality_score
                best_result = result
            
            if not feedback.needs_iteration or iteration >= self.max_feedback_iterations - 1:
                logger.warning(f"Max iterations reached for phase '{phase}'")
                return best_result or result
            
            # Update context for next pass
            current_context = current_context.copy()
            current_context["previous_output"] = result.output
            current_context["feedback"] = {
                "issues": feedback.issues,
                "suggestions": feedback.suggestions,
                "instruction": "Please refine the previous output based on the feedback."
            }
            
            self.metrics["total_feedback_iterations"] += 1
            logger.info(f"Refining output based on feedback...")
        
        return best_result or result

    async def _assess_quality(
        self,
        output: Dict[str, Any],
        phase: str,
    ) -> FeedbackResult:
        """
        Assess the quality of phase output using an LLM reviewer.
        
        Should match the logic of ProducerReviewerLoop._review but adapted for Phase outputs.
        """
        logger.info(f"Assessing quality for phase: {phase}")
        
        # Get reviewer configuration
        reviewer_cfg = self.model_router.get_model_for_phase("reviewer")
        
        # Construct review prompt
        prompt = (
            f"You are a Quality Assurance Reviewer for the '{phase}' phase.\n"
            f"Review the following output against the expected quality standards.\n"
            f"Output JSON with check result.\n\n"
            f"Output to Review:\n{json.dumps(output, indent=2)[:4000]}...\n\n" # Truncate if too long
            f"Return JSON format:\n"
            f"{{\n"
            f"  \"score\": <float 0.0-1.0>,\n"
            f"  \"issues\": [\"ticket 1\", ...],\n"
            f"  \"suggestions\": [\"suggestion 1\", ...],\n"
            f"  \"needs_iteration\": <bool>\n"
            f"}}"
        )
        
        try:
            # Call LLM for review
            response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": "You are a critical code reviewer. Output structured JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=reviewer_cfg.model,
                temperature=0.0,
                json_mode=True
            )
            
            # Parse result
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            review_data = json.loads(content)
            
            return FeedbackResult(
                quality_score=float(review_data.get("score", 0.0)),
                issues=review_data.get("issues", []),
                suggestions=review_data.get("suggestions", []),
                needs_iteration=bool(review_data.get("needs_iteration", False))
            )

        except Exception as e:
            logger.warning(f"Review failed, falling back to heuristic: {e}")
            # Fallback heuristic
            return FeedbackResult(
                quality_score=0.8,
                issues=["Review process failed"],
                suggestions=[],
                needs_iteration=False
            )

    async def run_parallel_phases(
        self,
        phases: List[Dict[str, Any]],
    ) -> List[PhaseResult]:
        """
        Execute multiple independent phases in parallel.
        
        Args:
            phases: List of phase configurations
            
        Returns:
            List of PhaseResults
        """
        logger.info(f"Executing {len(phases)} phases in parallel")
        
        tasks = [
            self.run_phase_with_retry(
                phase=p["phase"],
                schema_name=p["schema_name"],
                context=p.get("context"),
                question=p.get("question"),
            )
            for p in phases
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        phase_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                phase_results.append(PhaseResult(
                    phase=phases[i]["phase"],
                    status=PhaseStatus.FAILED,
                    error=str(result),
                ))
            else:
                phase_results.append(result)
        
        return phase_results

    async def run_pipeline_adaptive(
        self,
        initial_requirements: str,
        question: Optional[str] = None,
        strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL,
        use_feedback: bool = True,
        deep_search: bool = False,
    ) -> Dict[str, Any]:
        """
        Run pipeline with adaptive strategy selection.
        
        Args:
            initial_requirements: Feature requirements
            question: RAG query
            strategy: Execution strategy
            use_feedback: Whether to use feedback loops
            
        Returns:
            Dictionary with all phase outputs and metadata
        """
        logger.info(f"Starting adaptive pipeline with strategy: {strategy.value}")
        
        self.cost_manager.reset_task()
        pipeline_start = time.time()
        results: Dict[str, Any] = {
            "metadata": {
                "strategy": strategy.value,
                "use_feedback": use_feedback,
                "start_time": datetime.utcnow().isoformat(),
            },
            "phases": {},
        }
        
        try:
            # Step 0: Prompt Validation (Gateway)
            msg = "Validating prompt with Prompt Gate (Gemini Flash)..."
            print(f":::STEP:{{\"type\": \"thinking\", \"text\": \"{msg}\"}}:::", flush=True)
            
            gate_res = await self.prompt_gate.validate_and_classify(initial_requirements)
            if not gate_res.get("is_valid", True):
                msg = f"Prompt Gate rejected the request: {gate_res.get('refined_prompt', 'The prompt is unclear or nonsense.')}"
                logger.warning(msg)
                raise ValueError(f"I'm sorry, but I couldn't understand that request. Could you please provide more details or clarify what you'd like me to do? (Ref: {gate_res.get('refined_prompt')})")

            if gate_res["refined_prompt"] != initial_requirements:
                logger.info("Prompt refined by Gate.")
                initial_requirements = gate_res["refined_prompt"]
            
            # Store complexity for later decision making
            task_complexity = gate_res["complexity"]
            
            # Analyst phase
            msg = "Phase 1: Analyzing Requirements"
            print(f":::STEP:{{\"type\": \"thinking\", \"text\": \"{msg}\", \"tier\": \"T1: Rules\"}}:::", flush=True)
            
            analyst_result = await (
                self.run_phase_with_feedback(
                    phase="analyst",
                    schema_name="requirements",
                    context={"requirements": initial_requirements, "rag_tier": 3},
                    question=question,
                    deep_search=deep_search,
                )
                if use_feedback
                else self.run_phase_with_retry(
                    phase="analyst",
                    schema_name="requirements",
                    context={"requirements": initial_requirements, "rag_tier": 3},
                    question=question,
                    deep_search=deep_search,
                )
            )
            
            if analyst_result.status != PhaseStatus.COMPLETED:
                raise RuntimeError(f"Analyst phase failed: {analyst_result.error}")
            
            results["phases"]["analyst"] = {
                "output": analyst_result.output,
                "metadata": {
                    "attempts": analyst_result.attempts,
                    "execution_time": analyst_result.execution_time,
                },
            }
            
            # Architect phase
            msg = "Phase 2: Designing Architecture"
            print(f":::STEP:{{\"type\": \"thinking\", \"text\": \"{msg}\", \"tier\": \"T4: Schema\"}}:::", flush=True)

            architect_result = await (
                self.run_phase_with_feedback(
                    phase="architect",
                    schema_name="architecture",
                    context={**analyst_result.output, "rag_tier": 4},
                )
                if use_feedback
                else self.run_phase_with_retry(
                    phase="architect",
                    schema_name="architecture",
                    context={**analyst_result.output, "rag_tier": 4},
                )
            )
            
            if architect_result.status != PhaseStatus.COMPLETED:
                raise RuntimeError(f"Architect phase failed: {architect_result.error}")
            
            results["phases"]["architect"] = {
                "output": architect_result.output,
                "metadata": {
                    "attempts": architect_result.attempts,
                    "execution_time": architect_result.execution_time,
                },
            }
            
            # Implementation phase
            msg = "Phase 3: Generating Code"
            print(f":::STEP:{{\"type\": \"editing\", \"text\": \"{msg}\", \"tier\": \"T2: Tokens\"}}:::", flush=True)

            implementation_result = await self.run_phase_with_retry(
                phase="implementation",
                schema_name="implementation",
                context={**architect_result.output, "rag_tier": 2},
            )
            
            if implementation_result.status != PhaseStatus.COMPLETED:
                raise RuntimeError(f"Implementation phase failed: {implementation_result.error}")
            
            results["phases"]["implementation"] = {
                "output": implementation_result.output,
                "metadata": {
                    "attempts": implementation_result.attempts,
                    "execution_time": implementation_result.execution_time,
                },
            }

            # Phase 3.5: Self-Healing Build Check (Auto-Detected)
            msg = "Automatic Integrity Check & Self-Healing"
            print(f":::STEP:{{\"type\": \"analyzing\", \"text\": \"{msg}\"}}:::", flush=True)
            
            # Let self_healer detect commands (pass None)
            healing_res = await self.self_healer.run_self_healing_cycle(
                build_commands=None,
                context={"request": initial_requirements, "implementation": implementation_result.output}
            )
            results["self_healing"] = healing_res
            
            # Testing phase
            msg = "Phase 4: Testing Implementation"
            print(f":::STEP:{{\"type\": \"analyzing\", \"text\": \"{msg}\"}}:::", flush=True)

            testing_result = await self.run_phase_with_retry(
                phase="testing",
                schema_name="testing",
                context=implementation_result.output,
            )
            
            if testing_result.status != PhaseStatus.COMPLETED:
                raise RuntimeError(f"Testing phase failed: {testing_result.error}")
            
            results["phases"]["testing"] = {
                "output": testing_result.output,
                "metadata": {
                    "attempts": testing_result.attempts,
                    "execution_time": testing_result.execution_time,
                },
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            results["error"] = str(e)
            results["status"] = "failed"
        else:
            results["status"] = "completed"
        finally:
            # Add final metadata
            results["metadata"]["end_time"] = datetime.utcnow().isoformat()
            results["metadata"]["total_time"] = time.time() - pipeline_start
            results["metadata"]["total_cost"] = self.cost_manager.total_cost
            results["metadata"]["metrics"] = self.metrics
            
            # Save results
            pipeline_path = self.outputs_dir / f"pipeline_v2_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
            with open(pipeline_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            
            self.tracer.log_event("pipeline_complete", {
                "pipeline_path": str(pipeline_path),
                "status": results["status"],
                "total_cost": self.cost_manager.total_cost,
            })
            
            logger.info(f"Pipeline {results['status']}. Results saved to {pipeline_path}")
        
        return results

    def get_metrics(self) -> Dict[str, Any]:
        """Get current orchestrator metrics."""
        return {
            **self.metrics,
            "total_cost": self.cost_manager.total_cost,
            "cost_by_model": self.cost_manager.get_cost_breakdown(),
        }

    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self.metrics = {
            "total_phases_executed": 0,
            "total_retries": 0,
            "total_feedback_iterations": 0,
            "phase_execution_times": {},
            "error_counts": {},
        }
        self.cost_manager.reset_task()
